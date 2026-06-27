from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(".")
DEFAULT_SPLIT_PATH = ROOT / "results" / "final_paper_v02" / "splits" / "can_paired_pos40_bad80_split404" / "split_indices.json"
DEFAULT_WEIGHTED_DIAGNOSTICS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
    / "setup"
    / "diagnostics.json"
)
DEFAULT_SCORE_RANKINGS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "score_diagnostics"
    / "can_paired_pos40_bad80_split404_policy0"
    / "demo_rankings.csv"
)
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate" / "sm_rwbc_can404_preflight"

STANDARD_LOW_DIM_OBS = [
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "object",
]
RISK_FEATURES = ["bad_neighbor_action", "bad_neighbor_state_action", "combined"]


@dataclass(frozen=True)
class DemoArrays:
    observations: np.ndarray
    actions: np.ndarray


@dataclass(frozen=True)
class TransitionBatch:
    observations: np.ndarray
    actions: np.ndarray
    demo_ids: np.ndarray
    timesteps: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a broad-pool Sequence-Masked Risk-Weighted BC preflight. "
            "The output HDF5 can be consumed by train_robomimic_official_transition_weighted.py."
        )
    )
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--weighted-diagnostics", type=Path, default=DEFAULT_WEIGHTED_DIAGNOSTICS)
    parser.add_argument("--score-rankings", type=Path, default=DEFAULT_SCORE_RANKINGS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--obs-keys", choices=["standard", "all"], default="standard")
    parser.add_argument("--chunk-size", type=int, default=2048)
    parser.add_argument("--m-min-grid", type=float, nargs="+", default=[0.03, 0.05, 0.10])
    parser.add_argument("--lambda-grid", type=float, nargs="+", default=[1.0, 2.0, 4.0])
    parser.add_argument("--risk-feature-grid", nargs="+", default=RISK_FEATURES, choices=RISK_FEATURES)
    parser.add_argument("--selected-m-min", type=float, default=0.05)
    parser.add_argument("--selected-lambda", type=float, default=2.0)
    parser.add_argument("--selected-risk-feature", choices=RISK_FEATURES, default="combined")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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


def ordered_unique(demo_ids: list[str]) -> list[str]:
    return list(dict.fromkeys(demo_ids))


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


def load_demo_arrays(hdf5_path: str, demo_ids: list[str], obs_keys: list[str]) -> dict[str, DemoArrays]:
    arrays: dict[str, DemoArrays] = {}
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted_demos(demo_ids):
            group = f["data"][demo_id]
            observations = obs_vector(group, obs_keys)
            actions = np.asarray(group["actions"], dtype=np.float32)
            if observations.shape[0] != actions.shape[0]:
                raise ValueError(f"{demo_id}: obs/action length mismatch")
            arrays[demo_id] = DemoArrays(observations=observations, actions=actions)
    return arrays


def stack_transitions(arrays: dict[str, DemoArrays], demo_ids: list[str]) -> TransitionBatch:
    obs_chunks: list[np.ndarray] = []
    action_chunks: list[np.ndarray] = []
    demo_chunks: list[np.ndarray] = []
    timestep_chunks: list[np.ndarray] = []
    for demo_id in sorted_demos(demo_ids):
        demo = arrays[demo_id]
        length = demo.actions.shape[0]
        obs_chunks.append(demo.observations)
        action_chunks.append(demo.actions)
        demo_chunks.append(np.full((length,), demo_id, dtype=object))
        timestep_chunks.append(np.arange(length, dtype=np.int32))
    return TransitionBatch(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        demo_ids=np.concatenate(demo_chunks, axis=0),
        timesteps=np.concatenate(timestep_chunks, axis=0),
    )


def standardize_fit(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = matrix.mean(axis=0, keepdims=True)
    std = matrix.std(axis=0, keepdims=True) + 1.0e-6
    return mean.astype(np.float32), std.astype(np.float32)


def standardize_apply(matrix: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((matrix - mean) / std).astype(np.float32, copy=False)


def nearest_l2(query: np.ndarray, reference: np.ndarray, *, chunk_size: int) -> tuple[np.ndarray, np.ndarray]:
    if reference.shape[0] == 0:
        raise ValueError("empty reference matrix")
    distances = np.empty((query.shape[0],), dtype=np.float32)
    indices = np.empty((query.shape[0],), dtype=np.int64)
    ref_norm = np.sum(reference * reference, axis=1)[None, :]
    ref_t = reference.T
    for start in range(0, query.shape[0], chunk_size):
        end = min(start + chunk_size, query.shape[0])
        chunk = query[start:end]
        dist2 = np.sum(chunk * chunk, axis=1)[:, None] + ref_norm - 2.0 * (chunk @ ref_t)
        dist2 = np.maximum(dist2, 0.0)
        local_indices = np.argmin(dist2, axis=1)
        distances[start:end] = np.sqrt(dist2[np.arange(end - start), local_indices]).astype(np.float32)
        indices[start:end] = local_indices
    return distances, indices


def minmax(values: np.ndarray) -> np.ndarray:
    lo = float(np.min(values))
    hi = float(np.max(values))
    if hi <= lo:
        return np.zeros_like(values, dtype=np.float32)
    return ((values - lo) / (hi - lo)).astype(np.float32, copy=False)


def score_by_demo(path: Path) -> dict[str, float]:
    return {row["demo_id"]: float(row["score"]) for row in read_csv(path)}


def fmt(value: float | int) -> str:
    if isinstance(value, int):
        return str(value)
    if math.isnan(float(value)):
        return ""
    return f"{float(value):.6f}"


def effective_sample_size(weights: np.ndarray) -> float:
    denom = float(np.sum(weights * weights))
    if denom <= 0.0:
        return 0.0
    total = float(np.sum(weights))
    return (total * total) / denom


def risk_arrays_for_pool(
    *,
    split: dict,
    arrays: dict[str, DemoArrays],
    train_ids: list[str],
    unlabeled_train_ids: list[str],
    chunk_size: int,
) -> tuple[dict[tuple[str, int], dict[str, float]], dict[str, float]]:
    labeled_positive = sorted_demos(split["labeled_positive_ids"])
    labeled_negative = sorted_demos(split["labeled_negative_ids"])
    fit_ids = sorted_demos(ordered_unique([*train_ids, *labeled_negative]))
    fit_batch = stack_transitions(arrays, fit_ids)
    pos_batch = stack_transitions(arrays, labeled_positive)
    neg_batch = stack_transitions(arrays, labeled_negative)
    unl_batch = stack_transitions(arrays, unlabeled_train_ids)

    obs_mean, obs_std = standardize_fit(fit_batch.observations)
    act_mean, act_std = standardize_fit(fit_batch.actions)

    pos_obs = standardize_apply(pos_batch.observations, obs_mean, obs_std)
    neg_obs = standardize_apply(neg_batch.observations, obs_mean, obs_std)
    unl_obs = standardize_apply(unl_batch.observations, obs_mean, obs_std)
    pos_act = standardize_apply(pos_batch.actions, act_mean, act_std)
    neg_act = standardize_apply(neg_batch.actions, act_mean, act_std)
    unl_act = standardize_apply(unl_batch.actions, act_mean, act_std)

    pos_sa = np.concatenate([pos_obs, pos_act], axis=1)
    neg_sa = np.concatenate([neg_obs, neg_act], axis=1)
    unl_sa = np.concatenate([unl_obs, unl_act], axis=1)

    pos_state_dist, nearest_pos_state = nearest_l2(unl_obs, pos_obs, chunk_size=chunk_size)
    nearest_pos_action = pos_act[nearest_pos_state]
    action_conflict = np.sqrt(np.sum((unl_act - nearest_pos_action) ** 2, axis=1)).astype(np.float32)
    pos_sa_dist, _ = nearest_l2(unl_sa, pos_sa, chunk_size=chunk_size)
    neg_sa_dist, _ = nearest_l2(unl_sa, neg_sa, chunk_size=chunk_size)
    bad_neighbor_raw = (pos_sa_dist - neg_sa_dist).astype(np.float32)

    action_risk = minmax(action_conflict)
    bad_neighbor_risk = minmax(bad_neighbor_raw)
    combined = (0.5 * action_risk + 0.5 * bad_neighbor_risk).astype(np.float32)

    by_key: dict[tuple[str, int], dict[str, float]] = {}
    for idx, (demo_id, timestep) in enumerate(zip(unl_batch.demo_ids, unl_batch.timesteps)):
        by_key[(str(demo_id), int(timestep))] = {
            "bad_neighbor_action": float(action_risk[idx]),
            "bad_neighbor_state_action": float(bad_neighbor_risk[idx]),
            "combined": float(combined[idx]),
            "action_conflict_distance": float(action_conflict[idx]),
            "pos_state_action_distance": float(pos_sa_dist[idx]),
            "neg_state_action_distance": float(neg_sa_dist[idx]),
            "bad_neighbor_raw": float(bad_neighbor_raw[idx]),
        }

    return by_key, {
        "obs_dim": int(pos_batch.observations.shape[1]),
        "action_dim": int(pos_batch.actions.shape[1]),
        "positive_reference_transitions": int(pos_batch.actions.shape[0]),
        "negative_reference_transitions": int(neg_batch.actions.shape[0]),
        "unlabeled_train_transitions": int(unl_batch.actions.shape[0]),
    }


def make_weights_for_recipe(
    *,
    split: dict,
    arrays: dict[str, DemoArrays],
    train_ids: list[str],
    labeled_positive_set: set[str],
    all_positive_set: set[str],
    scores: dict[str, float],
    risk_by_key: dict[tuple[str, int], dict[str, float]],
    m_min: float,
    lambda_risk: float,
    risk_feature: str,
) -> tuple[dict[str, dict[str, np.ndarray]], list[dict[str, object]], dict[str, float]]:
    weights_by_demo: dict[str, dict[str, np.ndarray]] = {}
    rows: list[dict[str, object]] = []
    all_weights: list[np.ndarray] = []
    hidden_positive_weights: list[np.ndarray] = []
    hidden_bad_weights: list[np.ndarray] = []
    hidden_positive_transitions = 0
    hidden_bad_transitions = 0
    hidden_positive_demos = 0
    hidden_bad_demos = 0
    labeled_positive_mass = 0.0
    hidden_positive_mass = 0.0
    hidden_bad_mass = 0.0

    for demo_id in sorted_demos(train_ids):
        demo = arrays[demo_id]
        length = demo.actions.shape[0]
        classifier_score = float(scores.get(demo_id, 1.0 if demo_id in labeled_positive_set else 0.0))
        loss_weight = np.ones((length,), dtype=np.float32)
        risk_values = np.zeros((length,), dtype=np.float32)
        action_risk = np.zeros((length,), dtype=np.float32)
        state_action_risk = np.zeros((length,), dtype=np.float32)
        combined_risk = np.zeros((length,), dtype=np.float32)
        action_conflict_distance = np.full((length,), np.nan, dtype=np.float32)
        pos_sa_dist = np.full((length,), np.nan, dtype=np.float32)
        neg_sa_dist = np.full((length,), np.nan, dtype=np.float32)
        role = "labeled_positive"

        if demo_id in labeled_positive_set:
            labeled_positive_mass += float(np.sum(loss_weight))
        else:
            role = "unlabeled_weighted"
            base = float(np.clip(classifier_score, m_min, 1.0))
            for timestep in range(length):
                stats = risk_by_key[(demo_id, timestep)]
                risk_values[timestep] = stats[risk_feature]
                action_risk[timestep] = stats["bad_neighbor_action"]
                state_action_risk[timestep] = stats["bad_neighbor_state_action"]
                combined_risk[timestep] = stats["combined"]
                action_conflict_distance[timestep] = stats["action_conflict_distance"]
                pos_sa_dist[timestep] = stats["pos_state_action_distance"]
                neg_sa_dist[timestep] = stats["neg_state_action_distance"]
            loss_weight = (base * np.exp(-float(lambda_risk) * risk_values)).astype(np.float32)
            loss_weight = np.clip(loss_weight, 1.0e-6, 1.0).astype(np.float32, copy=False)
            if demo_id in all_positive_set:
                hidden_positive_demos += 1
                hidden_positive_transitions += length
                hidden_positive_mass += float(np.sum(loss_weight))
                hidden_positive_weights.append(loss_weight)
            else:
                hidden_bad_demos += 1
                hidden_bad_transitions += length
                hidden_bad_mass += float(np.sum(loss_weight))
                hidden_bad_weights.append(loss_weight)

        all_weights.append(loss_weight)
        weights_by_demo[demo_id] = {
            "loss_weight": loss_weight,
            "risk_feature": risk_values,
            "bad_neighbor_action_risk": action_risk,
            "bad_neighbor_state_action_risk": state_action_risk,
            "combined_risk": combined_risk,
            "action_conflict_distance": action_conflict_distance,
            "pos_state_action_distance": pos_sa_dist,
            "neg_state_action_distance": neg_sa_dist,
            "classifier_score": np.full((length,), classifier_score, dtype=np.float32),
        }

        rows.append(
            {
                "demo_id": demo_id,
                "role": role,
                "hidden_label": "labeled_positive" if role == "labeled_positive" else ("positive" if demo_id in all_positive_set else "bad"),
                "transition_count": length,
                "classifier_score": fmt(classifier_score),
                "weight_mean": fmt(float(np.mean(loss_weight))),
                "weight_min": fmt(float(np.min(loss_weight))),
                "weight_max": fmt(float(np.max(loss_weight))),
                "weight_mass": fmt(float(np.sum(loss_weight))),
                "risk_mean": "" if role == "labeled_positive" else fmt(float(np.mean(risk_values))),
                "risk_p90": "" if role == "labeled_positive" else fmt(float(np.quantile(risk_values, 0.90))),
                "action_risk_mean": "" if role == "labeled_positive" else fmt(float(np.mean(action_risk))),
                "state_action_risk_mean": "" if role == "labeled_positive" else fmt(float(np.mean(state_action_risk))),
                "combined_risk_mean": "" if role == "labeled_positive" else fmt(float(np.mean(combined_risk))),
            }
        )

    flat_weights = np.concatenate(all_weights)
    hidden_positive_flat = (
        np.concatenate(hidden_positive_weights) if hidden_positive_weights else np.asarray([], dtype=np.float32)
    )
    hidden_bad_flat = np.concatenate(hidden_bad_weights) if hidden_bad_weights else np.asarray([], dtype=np.float32)
    hidden_unlabeled_mass = hidden_positive_mass + hidden_bad_mass
    hidden_unlabeled_transitions = hidden_positive_transitions + hidden_bad_transitions
    summary = {
        "m_min": float(m_min),
        "lambda_risk": float(lambda_risk),
        "risk_feature": risk_feature,
        "train_demo_count": float(len(train_ids)),
        "labeled_positive_count": float(len(labeled_positive_set)),
        "hidden_positive_demo_count": float(hidden_positive_demos),
        "hidden_bad_demo_count": float(hidden_bad_demos),
        "hidden_positive_transition_count": float(hidden_positive_transitions),
        "hidden_bad_transition_count": float(hidden_bad_transitions),
        "labeled_positive_mass": float(labeled_positive_mass),
        "hidden_positive_mass": float(hidden_positive_mass),
        "hidden_bad_mass": float(hidden_bad_mass),
        "hidden_bad_unweighted_transition_fraction": float(
            hidden_bad_transitions / max(1, hidden_unlabeled_transitions)
        ),
        "hidden_bad_weighted_mass_fraction": float(hidden_bad_mass / max(1.0, hidden_unlabeled_mass)),
        "hidden_positive_mean_weight": float(np.mean(hidden_positive_flat)) if hidden_positive_flat.size else 0.0,
        "hidden_bad_mean_weight": float(np.mean(hidden_bad_flat)) if hidden_bad_flat.size else 0.0,
        "all_transition_weight_mean": float(np.mean(flat_weights)),
        "all_transition_weight_min": float(np.min(flat_weights)),
        "all_transition_weight_max": float(np.max(flat_weights)),
        "transition_effective_sample_size": float(effective_sample_size(flat_weights)),
    }
    return weights_by_demo, rows, summary


def write_weight_hdf5(path: Path, weights_by_demo: dict[str, dict[str, np.ndarray]], metadata: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        f.attrs["metadata_json"] = json.dumps(metadata, sort_keys=True)
        data_group = f.create_group("data")
        for demo_id in sorted_demos(set(weights_by_demo)):
            demo_group = data_group.create_group(demo_id)
            for key, value in weights_by_demo[demo_id].items():
                demo_group.create_dataset(key, data=value.astype(np.float32), compression="gzip")


def write_report(
    path: Path,
    *,
    selected_summary: dict[str, float],
    grid_rows: list[dict[str, object]],
    output_paths: dict[str, Path],
) -> None:
    sorted_grid = sorted(
        grid_rows,
        key=lambda row: (
            float(row["hidden_bad_weighted_mass_fraction"]),
            -float(row["hidden_positive_mass"]),
        ),
    )
    lines = [
        "# SOTA Candidate 1 SM-RWBC Preflight",
        "",
        "This preflight builds broad-pool per-timestep weights for Sequence-Masked Risk-Weighted BC.",
        "It uses the weighted-BC train pool, keeps labeled positives at full weight, and downweights",
        "unlabeled timesteps by classifier score and local bad-action risk.",
        "",
        "## Selected Recipe",
        "",
        f"- `m_min`: `{selected_summary['m_min']:.3f}`.",
        f"- `lambda_risk`: `{selected_summary['lambda_risk']:.3f}`.",
        f"- Risk feature: `{selected_summary['risk_feature']}`.",
        f"- Train demos: `{int(selected_summary['train_demo_count'])}`.",
        f"- Hidden-positive / hidden-bad demos in broad pool: `{int(selected_summary['hidden_positive_demo_count'])}` / `{int(selected_summary['hidden_bad_demo_count'])}`.",
        f"- Hidden-bad unweighted transition fraction: `{selected_summary['hidden_bad_unweighted_transition_fraction']:.3f}`.",
        f"- Hidden-bad weighted mass fraction: `{selected_summary['hidden_bad_weighted_mass_fraction']:.3f}`.",
        f"- Hidden-positive mass: `{selected_summary['hidden_positive_mass']:.1f}`.",
        f"- Hidden-bad mass: `{selected_summary['hidden_bad_mass']:.1f}`.",
        f"- Transition ESS: `{selected_summary['transition_effective_sample_size']:.1f}`.",
        "",
        "## Lowest Hidden-Bad Mass Grid Rows",
        "",
        "| m_min | lambda | risk | hidden-positive mass | hidden-bad mass | bad mass frac | ESS |",
        "| ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted_grid[:8]:
        lines.append(
            "| {m_min} | {lambda_risk} | {risk_feature} | {hidden_positive_mass} | {hidden_bad_mass} | {hidden_bad_weighted_mass_fraction} | {transition_effective_sample_size} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- This is not a policy result. It only checks whether the SOTA Candidate 1 recipe creates a trainable broad-coverage distribution with less hidden-bad transition mass than unweighted broad cloning.",
            "- The next gate is a bounded Can404 train/eval with the existing transition-weighted trainer, because previous union-only and hard-mask variants did not beat positive-only.",
            "",
            "## Outputs",
            "",
            f"- Selected weights HDF5: `{output_paths['weights_hdf5']}`.",
            f"- Selected per-demo CSV: `{output_paths['selected_summary_csv']}`.",
            f"- Grid CSV: `{output_paths['grid_csv']}`.",
            f"- Recipe JSON: `{output_paths['recipe_json']}`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def grid_fieldnames() -> list[str]:
    return [
        "m_min",
        "lambda_risk",
        "risk_feature",
        "train_demo_count",
        "labeled_positive_count",
        "hidden_positive_demo_count",
        "hidden_bad_demo_count",
        "hidden_positive_transition_count",
        "hidden_bad_transition_count",
        "labeled_positive_mass",
        "hidden_positive_mass",
        "hidden_bad_mass",
        "hidden_bad_unweighted_transition_fraction",
        "hidden_bad_weighted_mass_fraction",
        "hidden_positive_mean_weight",
        "hidden_bad_mean_weight",
        "all_transition_weight_mean",
        "all_transition_weight_min",
        "all_transition_weight_max",
        "transition_effective_sample_size",
    ]


def main() -> None:
    args = parse_args()
    split = read_json(args.split_path)
    weighted = read_json(args.weighted_diagnostics)
    hdf5_path = split["hdf5_path"]
    obs_keys = STANDARD_LOW_DIM_OBS if args.obs_keys == "standard" else dataset_obs_keys(hdf5_path)
    scores = score_by_demo(args.score_rankings)
    train_ids = sorted_demos(weighted["train_demo_ids"])
    labeled_positive_set = set(split["labeled_positive_ids"])
    unlabeled_train_ids = [demo_id for demo_id in train_ids if demo_id not in labeled_positive_set]
    all_needed = sorted_demos(set(train_ids) | set(split["labeled_negative_ids"]))
    arrays = load_demo_arrays(hdf5_path, all_needed, obs_keys)
    risk_by_key, reference_summary = risk_arrays_for_pool(
        split=split,
        arrays=arrays,
        train_ids=train_ids,
        unlabeled_train_ids=unlabeled_train_ids,
        chunk_size=args.chunk_size,
    )
    all_positive_set = set(split["all_positive_ids"])

    grid_rows: list[dict[str, object]] = []
    selected_weights: dict[str, dict[str, np.ndarray]] | None = None
    selected_rows: list[dict[str, object]] | None = None
    selected_summary: dict[str, float] | None = None
    for m_min in args.m_min_grid:
        for lambda_risk in args.lambda_grid:
            for risk_feature in args.risk_feature_grid:
                weights, rows, summary = make_weights_for_recipe(
                    split=split,
                    arrays=arrays,
                    train_ids=train_ids,
                    labeled_positive_set=labeled_positive_set,
                    all_positive_set=all_positive_set,
                    scores=scores,
                    risk_by_key=risk_by_key,
                    m_min=float(m_min),
                    lambda_risk=float(lambda_risk),
                    risk_feature=risk_feature,
                )
                grid_rows.append({key: fmt(value) if isinstance(value, float) else value for key, value in summary.items()})
                if (
                    abs(float(m_min) - args.selected_m_min) < 1.0e-9
                    and abs(float(lambda_risk) - args.selected_lambda) < 1.0e-9
                    and risk_feature == args.selected_risk_feature
                ):
                    selected_weights = weights
                    selected_rows = rows
                    selected_summary = summary

    if selected_weights is None or selected_rows is None or selected_summary is None:
        raise ValueError("selected recipe is not present in the requested grid")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    weights_hdf5 = args.out_dir / "sm_rwbc_loss_weights.hdf5"
    selected_summary_csv = args.out_dir / "sm_rwbc_selected_demo_summary.csv"
    grid_csv = args.out_dir / "sm_rwbc_grid_summary.csv"
    recipe_json = args.out_dir / "sm_rwbc_recipe.json"
    report_path = args.out_dir / "sm_rwbc_preflight_REPORT.md"
    metadata = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "weighted_diagnostics": str(args.weighted_diagnostics),
        "score_rankings": str(args.score_rankings),
        "obs_keys": obs_keys,
        "selected_recipe": {
            "m_min": args.selected_m_min,
            "lambda_risk": args.selected_lambda,
            "risk_feature": args.selected_risk_feature,
        },
        "selected_summary": selected_summary,
        "reference_summary": reference_summary,
    }
    write_weight_hdf5(weights_hdf5, selected_weights, metadata)
    write_csv(
        selected_summary_csv,
        selected_rows,
        [
            "demo_id",
            "role",
            "hidden_label",
            "transition_count",
            "classifier_score",
            "weight_mean",
            "weight_min",
            "weight_max",
            "weight_mass",
            "risk_mean",
            "risk_p90",
            "action_risk_mean",
            "state_action_risk_mean",
            "combined_risk_mean",
        ],
    )
    write_csv(grid_csv, grid_rows, grid_fieldnames())
    recipe_json.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    write_report(
        report_path,
        selected_summary=selected_summary,
        grid_rows=grid_rows,
        output_paths={
            "weights_hdf5": weights_hdf5,
            "selected_summary_csv": selected_summary_csv,
            "grid_csv": grid_csv,
            "recipe_json": recipe_json,
        },
    )
    print(
        json.dumps(
            {
                "out_dir": str(args.out_dir),
                **reference_summary,
                **selected_summary,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
