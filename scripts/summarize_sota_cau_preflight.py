from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(".")
DEFAULT_SPLIT_PATH = ROOT / "results" / "final_paper_v02" / "splits" / "can_paired_pos40_bad80_split404" / "split_indices.json"
DEFAULT_BASE_WEIGHTS = (
    ROOT
    / "results"
    / "candidate_breakthrough"
    / "candidate_c_sequence_mask_preflight"
    / "candidate_c_sequence_mask_weights.hdf5"
)
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate" / "cau_action_conflict_can404_preflight"
STANDARD_LOW_DIM_OBS = [
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "object",
]
RETRIEVAL_MODES = ["nearest_state", "nearest_state_action", "action_conflict"]


@dataclass(frozen=True)
class DemoArrays:
    observations: np.ndarray
    actions: np.ndarray
    state_action: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a CAU-BC negative-action preflight from an existing sequence-mask "
            "loss-weight HDF5. The selected output can be consumed by "
            "train_robomimic_official_transition_weighted.py."
        )
    )
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--base-weights", type=Path, default=DEFAULT_BASE_WEIGHTS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--obs-keys", choices=["standard", "all"], default="standard")
    parser.add_argument("--chunk-size", type=int, default=2048)
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--selected-retrieval", choices=RETRIEVAL_MODES, default="action_conflict")
    parser.add_argument(
        "--negative-loss-scope",
        choices=["selected", "extra_selected"],
        default="selected",
        help="selected applies CAU on all masked timesteps; extra_selected excludes full-weight anchor demos.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def sorted_demos(demo_ids: list[str] | set[str]) -> list[str]:
    return sorted(demo_ids, key=demo_sort_key)


def dataset_obs_keys(hdf5_path: str) -> list[str]:
    with h5py.File(hdf5_path, "r") as f:
        first_demo = sorted(f["data"].keys(), key=demo_sort_key)[0]
        return sorted(f["data"][first_demo]["obs"].keys())


def obs_vector(group, obs_keys: list[str]) -> np.ndarray:
    obs_group = group["obs"]
    parts = [
        np.asarray(obs_group[key], dtype=np.float32).reshape((obs_group[key].shape[0], -1))
        for key in obs_keys
    ]
    return np.concatenate(parts, axis=1).astype(np.float32, copy=False)


def load_arrays(hdf5_path: str, demo_ids: list[str], obs_keys: list[str]) -> dict[str, DemoArrays]:
    arrays: dict[str, DemoArrays] = {}
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted_demos(demo_ids):
            group = f["data"][demo_id]
            observations = obs_vector(group, obs_keys)
            actions = np.asarray(group["actions"], dtype=np.float32)
            if observations.shape[0] != actions.shape[0]:
                raise ValueError(f"{demo_id}: obs/action length mismatch")
            arrays[demo_id] = DemoArrays(
                observations=observations,
                actions=actions,
                state_action=np.concatenate([observations, actions], axis=1).astype(np.float32, copy=False),
            )
    return arrays


def load_base_weights(path: Path) -> tuple[dict[str, dict[str, np.ndarray]], dict[str, object]]:
    weights: dict[str, dict[str, np.ndarray]] = {}
    metadata: dict[str, object] = {}
    with h5py.File(path, "r") as f:
        if "metadata_json" in f.attrs:
            metadata = json.loads(f.attrs["metadata_json"])
        for demo_id in f["data"]:
            group = f["data"][demo_id]
            weights[demo_id] = {
                key: np.asarray(group[key], dtype=np.float32)
                for key in group
            }
    if not weights:
        raise ValueError(f"no base weights in {path}")
    return weights, metadata


def standardize_fit(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = matrix.mean(axis=0, keepdims=True)
    std = matrix.std(axis=0, keepdims=True) + 1.0e-6
    return mean.astype(np.float32), std.astype(np.float32)


def standardize_apply(matrix: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((matrix - mean) / std).astype(np.float32, copy=False)


def nearest_index_and_dist(query: np.ndarray, reference: np.ndarray, *, chunk_size: int) -> tuple[np.ndarray, np.ndarray]:
    indices = np.empty((query.shape[0],), dtype=np.int64)
    dists = np.empty((query.shape[0],), dtype=np.float32)
    ref_t = reference.T
    ref_norm = np.sum(reference * reference, axis=1, keepdims=True).T
    for start in range(0, query.shape[0], chunk_size):
        end = min(start + chunk_size, query.shape[0])
        block = query[start:end]
        dist2 = np.sum(block * block, axis=1, keepdims=True) + ref_norm - 2.0 * block @ ref_t
        best = np.argmin(dist2, axis=1)
        indices[start:end] = best
        dists[start:end] = np.sqrt(np.maximum(dist2[np.arange(end - start), best], 0.0)).astype(np.float32)
    return indices, dists


def action_conflict_indices(
    query_obs: np.ndarray,
    query_actions: np.ndarray,
    negative_obs: np.ndarray,
    negative_actions: np.ndarray,
    *,
    top_k: int,
    chunk_size: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    k = min(top_k, negative_obs.shape[0])
    indices = np.empty((query_obs.shape[0],), dtype=np.int64)
    obs_dists = np.empty((query_obs.shape[0],), dtype=np.float32)
    action_dists = np.empty((query_obs.shape[0],), dtype=np.float32)
    ref_t = negative_obs.T
    ref_norm = np.sum(negative_obs * negative_obs, axis=1, keepdims=True).T
    for start in range(0, query_obs.shape[0], chunk_size):
        end = min(start + chunk_size, query_obs.shape[0])
        block = query_obs[start:end]
        dist2 = np.sum(block * block, axis=1, keepdims=True) + ref_norm - 2.0 * block @ ref_t
        dist2 = np.maximum(dist2, 0.0)
        nearest = np.argpartition(dist2, kth=k - 1, axis=1)[:, :k]
        cand_actions = negative_actions[nearest]
        action_delta = cand_actions - query_actions[start:end, None, :]
        cand_action_dist = np.sqrt(np.maximum(np.sum(action_delta * action_delta, axis=2), 0.0))
        local_choice = np.argmax(cand_action_dist, axis=1)
        chosen = nearest[np.arange(end - start), local_choice]
        indices[start:end] = chosen
        obs_dists[start:end] = np.sqrt(dist2[np.arange(end - start), chosen]).astype(np.float32)
        action_dists[start:end] = cand_action_dist[np.arange(end - start), local_choice].astype(np.float32)
    return indices, obs_dists, action_dists


def fmt(value: float | int) -> str:
    if isinstance(value, int):
        return str(value)
    return f"{float(value):.6f}"


def write_weight_hdf5(path: Path, weights: dict[str, dict[str, np.ndarray]], metadata: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        f.attrs["metadata_json"] = json.dumps(metadata, sort_keys=True)
        data_group = f.create_group("data")
        for demo_id in sorted_demos(set(weights)):
            demo_group = data_group.create_group(demo_id)
            for key, value in weights[demo_id].items():
                demo_group.create_dataset(key, data=value.astype(np.float32), compression="gzip")


def selected_mask_for_demo(base: dict[str, np.ndarray], *, is_anchor: bool, scope: str) -> np.ndarray:
    loss_weight = np.asarray(base["loss_weight"], dtype=np.float32)
    if scope == "extra_selected" and is_anchor:
        return np.zeros_like(loss_weight)
    return (loss_weight > 0.0).astype(np.float32)


def main() -> None:
    args = parse_args()
    split = read_json(args.split_path)
    hdf5_path = split["hdf5_path"]
    obs_keys = STANDARD_LOW_DIM_OBS if args.obs_keys == "standard" else dataset_obs_keys(hdf5_path)
    base_weights, base_metadata = load_base_weights(args.base_weights)
    train_ids = sorted_demos(set(base_weights))
    labeled_negative = sorted_demos(split["labeled_negative_ids"])
    labeled_positive = set(split["labeled_positive_ids"])
    all_positive = set(split["all_positive_ids"])
    arrays = load_arrays(hdf5_path, sorted_demos(set(train_ids) | set(labeled_negative)), obs_keys)

    fit_obs = np.concatenate([arrays[demo_id].observations for demo_id in sorted_demos(set(train_ids) | set(labeled_negative))], axis=0)
    fit_actions = np.concatenate([arrays[demo_id].actions for demo_id in sorted_demos(set(train_ids) | set(labeled_negative))], axis=0)
    fit_state_action = np.concatenate([arrays[demo_id].state_action for demo_id in sorted_demos(set(train_ids) | set(labeled_negative))], axis=0)
    obs_mean, obs_std = standardize_fit(fit_obs)
    action_mean, action_std = standardize_fit(fit_actions)
    state_action_mean, state_action_std = standardize_fit(fit_state_action)

    neg_obs = np.concatenate([arrays[demo_id].observations for demo_id in labeled_negative], axis=0)
    neg_actions = np.concatenate([arrays[demo_id].actions for demo_id in labeled_negative], axis=0)
    neg_state_action = np.concatenate([arrays[demo_id].state_action for demo_id in labeled_negative], axis=0)
    neg_obs_norm = standardize_apply(neg_obs, obs_mean, obs_std)
    neg_actions_norm = standardize_apply(neg_actions, action_mean, action_std)
    neg_state_action_norm = standardize_apply(neg_state_action, state_action_mean, state_action_std)

    mode_outputs: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    mode_summaries: list[dict[str, object]] = []
    selected_rows: list[dict[str, object]] = []

    for mode in RETRIEVAL_MODES:
        out: dict[str, dict[str, np.ndarray]] = {}
        selected_action_dists: list[np.ndarray] = []
        selected_obs_dists: list[np.ndarray] = []
        selected_sa_dists: list[np.ndarray] = []
        hidden_positive_mass = 0
        hidden_bad_mass = 0
        negative_loss_mass = 0
        for demo_id in train_ids:
            demo = arrays[demo_id]
            base = base_weights[demo_id]
            is_anchor = demo_id in labeled_positive or np.all(base["loss_weight"] > 0.0)
            negative_loss_weight = selected_mask_for_demo(
                base,
                is_anchor=is_anchor,
                scope=args.negative_loss_scope,
            )
            query_obs = standardize_apply(demo.observations, obs_mean, obs_std)
            query_actions_norm = standardize_apply(demo.actions, action_mean, action_std)
            query_sa = standardize_apply(demo.state_action, state_action_mean, state_action_std)
            if mode == "nearest_state":
                neg_idx, obs_dist = nearest_index_and_dist(query_obs, neg_obs_norm, chunk_size=args.chunk_size)
                action_dist = np.sqrt(
                    np.maximum(np.sum((neg_actions_norm[neg_idx] - query_actions_norm) ** 2, axis=1), 0.0)
                ).astype(np.float32)
                sa_dist = np.sqrt(
                    np.maximum(np.sum((neg_state_action_norm[neg_idx] - query_sa) ** 2, axis=1), 0.0)
                ).astype(np.float32)
            elif mode == "nearest_state_action":
                neg_idx, sa_dist = nearest_index_and_dist(
                    query_sa,
                    neg_state_action_norm,
                    chunk_size=args.chunk_size,
                )
                obs_dist = np.sqrt(
                    np.maximum(np.sum((neg_obs_norm[neg_idx] - query_obs) ** 2, axis=1), 0.0)
                ).astype(np.float32)
                action_dist = np.sqrt(
                    np.maximum(np.sum((neg_actions_norm[neg_idx] - query_actions_norm) ** 2, axis=1), 0.0)
                ).astype(np.float32)
            else:
                neg_idx, obs_dist, action_dist = action_conflict_indices(
                    query_obs,
                    query_actions_norm,
                    neg_obs_norm,
                    neg_actions_norm,
                    top_k=args.top_k,
                    chunk_size=args.chunk_size,
                )
                sa_dist = np.sqrt(
                    np.maximum(np.sum((neg_state_action_norm[neg_idx] - query_sa) ** 2, axis=1), 0.0)
                ).astype(np.float32)

            selected = negative_loss_weight > 0.0
            if np.any(selected):
                selected_action_dists.append(action_dist[selected])
                selected_obs_dists.append(obs_dist[selected])
                selected_sa_dists.append(sa_dist[selected])
                mass = int(np.sum(selected))
                negative_loss_mass += mass
                if demo_id in all_positive:
                    hidden_positive_mass += mass
                elif demo_id not in labeled_positive:
                    hidden_bad_mass += mass
            out[demo_id] = {
                "loss_weight": np.asarray(base["loss_weight"], dtype=np.float32),
                "negative_action": neg_actions[neg_idx].astype(np.float32),
                "negative_loss_weight": negative_loss_weight.astype(np.float32),
                "negative_obs_distance": obs_dist.astype(np.float32),
                "negative_state_action_distance": sa_dist.astype(np.float32),
                "negative_action_distance": action_dist.astype(np.float32),
            }
            if mode == args.selected_retrieval:
                selected_rows.append(
                    {
                        "demo_id": demo_id,
                        "role": "anchor" if is_anchor else "extra_masked",
                        "hidden_label": "labeled_or_anchor" if is_anchor else ("positive" if demo_id in all_positive else "bad"),
                        "transition_count": int(demo.actions.shape[0]),
                        "bc_selected_mass": int(np.sum(np.asarray(base["loss_weight"]) > 0.0)),
                        "negative_loss_mass": int(np.sum(selected)),
                        "selected_negative_obs_distance_mean": ""
                        if not np.any(selected)
                        else fmt(float(np.mean(obs_dist[selected]))),
                        "selected_negative_action_distance_mean": ""
                        if not np.any(selected)
                        else fmt(float(np.mean(action_dist[selected]))),
                        "selected_negative_state_action_distance_mean": ""
                        if not np.any(selected)
                        else fmt(float(np.mean(sa_dist[selected]))),
                    }
                )
        action_flat = np.concatenate(selected_action_dists) if selected_action_dists else np.asarray([], dtype=np.float32)
        obs_flat = np.concatenate(selected_obs_dists) if selected_obs_dists else np.asarray([], dtype=np.float32)
        sa_flat = np.concatenate(selected_sa_dists) if selected_sa_dists else np.asarray([], dtype=np.float32)
        mode_outputs[mode] = out
        mode_summaries.append(
            {
                "retrieval_mode": mode,
                "negative_loss_scope": args.negative_loss_scope,
                "negative_loss_mass": negative_loss_mass,
                "hidden_positive_negative_loss_mass": hidden_positive_mass,
                "hidden_bad_negative_loss_mass": hidden_bad_mass,
                "selected_negative_obs_distance_mean": fmt(float(np.mean(obs_flat))) if obs_flat.size else "",
                "selected_negative_action_distance_mean": fmt(float(np.mean(action_flat))) if action_flat.size else "",
                "selected_negative_action_distance_p25": fmt(float(np.quantile(action_flat, 0.25))) if action_flat.size else "",
                "selected_negative_action_distance_p50": fmt(float(np.quantile(action_flat, 0.50))) if action_flat.size else "",
                "selected_negative_action_distance_p75": fmt(float(np.quantile(action_flat, 0.75))) if action_flat.size else "",
                "selected_negative_state_action_distance_mean": fmt(float(np.mean(sa_flat))) if sa_flat.size else "",
            }
        )

    selected_summary = next(row for row in mode_summaries if row["retrieval_mode"] == args.selected_retrieval)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    weights_hdf5 = args.out_dir / "cau_negative_action_weights.hdf5"
    summary_csv = args.out_dir / "cau_retrieval_summary.csv"
    selected_csv = args.out_dir / "cau_selected_demo_summary.csv"
    recipe_json = args.out_dir / "cau_recipe.json"
    report_path = args.out_dir / "cau_preflight_REPORT.md"
    metadata = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "base_weights": str(args.base_weights),
        "base_metadata": base_metadata,
        "obs_keys": obs_keys,
        "top_k": args.top_k,
        "selected_retrieval": args.selected_retrieval,
        "negative_loss_scope": args.negative_loss_scope,
        "selected_summary": selected_summary,
    }
    write_weight_hdf5(weights_hdf5, mode_outputs[args.selected_retrieval], metadata)
    write_csv(
        summary_csv,
        mode_summaries,
        [
            "retrieval_mode",
            "negative_loss_scope",
            "negative_loss_mass",
            "hidden_positive_negative_loss_mass",
            "hidden_bad_negative_loss_mass",
            "selected_negative_obs_distance_mean",
            "selected_negative_action_distance_mean",
            "selected_negative_action_distance_p25",
            "selected_negative_action_distance_p50",
            "selected_negative_action_distance_p75",
            "selected_negative_state_action_distance_mean",
        ],
    )
    write_csv(
        selected_csv,
        selected_rows,
        [
            "demo_id",
            "role",
            "hidden_label",
            "transition_count",
            "bc_selected_mass",
            "negative_loss_mass",
            "selected_negative_obs_distance_mean",
            "selected_negative_action_distance_mean",
            "selected_negative_state_action_distance_mean",
        ],
    )
    recipe_json.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# CAU-BC Negative-Action Preflight",
        "",
        "This preflight reuses the Candidate C sequence mask but changes the counterfactual bad-action target.",
        "The goal is to avoid repeating the rejected nearest-state Candidate D/X hinge unchanged.",
        "",
        "## Retrieval Summary",
        "",
        "| retrieval | neg mass | hidden-pos mass | hidden-bad mass | obs dist | action dist | state-action dist |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in mode_summaries:
        lines.append(
            "| {retrieval_mode} | {negative_loss_mass} | {hidden_positive_negative_loss_mass} | {hidden_bad_negative_loss_mass} | {selected_negative_obs_distance_mean} | {selected_negative_action_distance_mean} | {selected_negative_state_action_distance_mean} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Selected Recipe",
            "",
            f"- Retrieval mode: `{args.selected_retrieval}`.",
            f"- Negative-loss scope: `{args.negative_loss_scope}`.",
            f"- Top-k local negative states for action-conflict retrieval: `{args.top_k}`.",
            f"- Negative-loss mass: `{selected_summary['negative_loss_mass']}`.",
            f"- Mean selected negative-action distance: `{selected_summary['selected_negative_action_distance_mean']}`.",
            "",
            "## Read",
            "",
            "- `action_conflict` chooses among local negative states but picks the negative action most different from the demonstrated action.",
            "- This is a different bad-action target from Candidate D/X's nearest-observation negative action. It still needs a bounded endpoint screen before any claim.",
            "",
            "## Outputs",
            "",
            f"- Weight HDF5: `{weights_hdf5}`.",
            f"- Retrieval summary CSV: `{summary_csv}`.",
            f"- Selected per-demo CSV: `{selected_csv}`.",
            f"- Recipe JSON: `{recipe_json}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"out_dir": str(args.out_dir), **selected_summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
