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
DEFAULT_SCORE_RANKINGS = (
    ROOT / "results" / "final_paper_v02" / "score_diagnostics" / "can_paired_pos40_bad80_split404_policy0" / "demo_rankings.csv"
)
DEFAULT_POSITIVE_ONLY_DIAGNOSTICS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
    / "setup"
    / "diagnostics.json"
)
DEFAULT_UNION_DIAGNOSTICS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "ablations"
    / "v02_fresh_endpoint_200ep_can40"
    / "split404"
    / "positive_nn_risk_union_top40"
    / "setup"
    / "diagnostics.json"
)
DEFAULT_OUT_DIR = ROOT / "results" / "candidate_breakthrough" / "candidate_a_transition_weight_preflight"

STANDARD_LOW_DIM_OBS = [
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "object",
]


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


@dataclass(frozen=True)
class WeightRecipe:
    anchor_base_floor: float
    coverage_base_floor: float
    anchor_risk_floor: float
    coverage_risk_floor: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a transition-level Candidate A loss-weight preflight for the Can split-404 "
            "positive-NN/risk union failure case."
        )
    )
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--score-rankings", type=Path, default=DEFAULT_SCORE_RANKINGS)
    parser.add_argument("--positive-only-diagnostics", type=Path, default=DEFAULT_POSITIVE_ONLY_DIAGNOSTICS)
    parser.add_argument("--union-diagnostics", type=Path, default=DEFAULT_UNION_DIAGNOSTICS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--obs-keys", choices=["standard", "all"], default="standard")
    parser.add_argument("--chunk-size", type=int, default=2048)
    parser.add_argument(
        "--anchor-base-floor",
        type=float,
        default=0.40,
        help="Minimum demo-level base weight for positive-only anchor unlabeled demos.",
    )
    parser.add_argument(
        "--coverage-base-floor",
        type=float,
        default=0.15,
        help="Minimum demo-level base weight for union-only coverage demos.",
    )
    parser.add_argument(
        "--anchor-risk-floor",
        type=float,
        default=0.10,
        help="Minimum local risk multiplier for positive-only anchor unlabeled demos.",
    )
    parser.add_argument(
        "--coverage-risk-floor",
        type=float,
        default=0.05,
        help="Minimum local risk multiplier for union-only coverage demos.",
    )
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def sorted_demos(demo_ids: list[str]) -> list[str]:
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
                raise ValueError(f"{demo_id}: obs/action length mismatch {observations.shape[0]} vs {actions.shape[0]}")
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
    for start in range(0, query.shape[0], chunk_size):
        end = min(start + chunk_size, query.shape[0])
        chunk = query[start:end]
        dist2 = np.sum(chunk * chunk, axis=1)[:, None] + ref_norm - 2.0 * (chunk @ reference.T)
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


def demo_classifier_scores(path: Path) -> dict[str, float]:
    out: dict[str, float] = {}
    for row in read_csv(path):
        out[row["demo_id"]] = float(row["score"])
    return out


def hidden_label(split: dict, demo_id: str) -> str:
    if demo_id in set(split["all_positive_ids"]):
        return "positive"
    if demo_id in set(split["all_negative_ids"]):
        return "bad"
    return "unknown"


def fmt_float(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.6f}"


def fmt_nanmean(values: np.ndarray) -> str:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return ""
    return fmt_float(float(np.mean(finite)))


def summarize_values(values: np.ndarray) -> dict[str, float]:
    return {
        "mean": float(np.mean(values)),
        "min": float(np.min(values)),
        "max": float(np.max(values)),
    }


def build_transition_weights(
    *,
    split: dict,
    hdf5_path: str,
    obs_keys: list[str],
    score_by_demo: dict[str, float],
    positive_anchor_ids: list[str],
    union_selected_ids: list[str],
    recipe: WeightRecipe,
    chunk_size: int,
) -> tuple[dict[str, dict[str, np.ndarray]], list[dict[str, object]], dict[str, object]]:
    labeled_positive = sorted_demos(list(split["labeled_positive_ids"]))
    labeled_negative = sorted_demos(list(split["labeled_negative_ids"]))
    candidate_unlabeled = sorted_demos(union_selected_ids)
    train_demo_ids = sorted_demos(ordered_unique([*labeled_positive, *candidate_unlabeled]))
    all_needed = sorted_demos(ordered_unique([*train_demo_ids, *labeled_negative]))

    arrays = load_demo_arrays(hdf5_path, all_needed, obs_keys)
    pos_batch = stack_transitions(arrays, labeled_positive)
    neg_batch = stack_transitions(arrays, labeled_negative)
    unl_batch = stack_transitions(arrays, candidate_unlabeled)
    fit_batch = stack_transitions(arrays, sorted_demos(ordered_unique([*train_demo_ids, *labeled_negative])))

    obs_mean, obs_std = standardize_fit(fit_batch.observations)
    act_mean, act_std = standardize_fit(fit_batch.actions)

    pos_obs = standardize_apply(pos_batch.observations, obs_mean, obs_std)
    neg_obs = standardize_apply(neg_batch.observations, obs_mean, obs_std)
    unl_obs = standardize_apply(unl_batch.observations, obs_mean, obs_std)
    fit_obs = standardize_apply(fit_batch.observations, obs_mean, obs_std)
    del neg_obs, fit_obs

    pos_act = standardize_apply(pos_batch.actions, act_mean, act_std)
    neg_act = standardize_apply(neg_batch.actions, act_mean, act_std)
    unl_act = standardize_apply(unl_batch.actions, act_mean, act_std)
    fit_act = standardize_apply(fit_batch.actions, act_mean, act_std)
    del fit_act

    pos_sa = np.concatenate([pos_obs, pos_act], axis=1)
    neg_sa = np.concatenate([standardize_apply(neg_batch.observations, obs_mean, obs_std), neg_act], axis=1)
    unl_sa = np.concatenate([unl_obs, unl_act], axis=1)

    pos_state_dist, nearest_pos_state = nearest_l2(unl_obs, pos_obs, chunk_size=chunk_size)
    nearest_pos_action = pos_act[nearest_pos_state]
    action_conflict = np.sqrt(np.sum((unl_act - nearest_pos_action) ** 2, axis=1)).astype(np.float32)
    pos_sa_dist, _ = nearest_l2(unl_sa, pos_sa, chunk_size=chunk_size)
    neg_sa_dist, _ = nearest_l2(unl_sa, neg_sa, chunk_size=chunk_size)

    action_conflict_norm = minmax(action_conflict)
    bad_neighbor_risk = (pos_sa_dist - neg_sa_dist).astype(np.float32)
    bad_neighbor_risk_norm = minmax(bad_neighbor_risk)
    positive_distance_norm = minmax(pos_sa_dist)
    combined_risk = (0.5 * action_conflict_norm + 0.5 * bad_neighbor_risk_norm).astype(np.float32)
    safe_factor = np.clip(1.0 - combined_risk, 0.0, 1.0).astype(np.float32)

    transition_by_key: dict[tuple[str, int], dict[str, float]] = {}
    for idx, (demo_id, timestep) in enumerate(zip(unl_batch.demo_ids, unl_batch.timesteps)):
        transition_by_key[(str(demo_id), int(timestep))] = {
            "pos_state_distance": float(pos_state_dist[idx]),
            "action_conflict_distance": float(action_conflict[idx]),
            "pos_state_action_distance": float(pos_sa_dist[idx]),
            "neg_state_action_distance": float(neg_sa_dist[idx]),
            "bad_neighbor_risk": float(bad_neighbor_risk[idx]),
            "action_conflict_risk_norm": float(action_conflict_norm[idx]),
            "bad_neighbor_risk_norm": float(bad_neighbor_risk_norm[idx]),
            "positive_distance_risk_norm": float(positive_distance_norm[idx]),
            "combined_risk": float(combined_risk[idx]),
            "safe_factor": float(safe_factor[idx]),
        }

    positive_anchor_set = set(positive_anchor_ids)
    union_set = set(union_selected_ids)
    labeled_positive_set = set(labeled_positive)
    all_positive_set = set(split["all_positive_ids"])

    weights_by_demo: dict[str, dict[str, np.ndarray]] = {}
    rows: list[dict[str, object]] = []
    for demo_id in train_demo_ids:
        demo = arrays[demo_id]
        length = demo.actions.shape[0]
        weights = np.ones((length,), dtype=np.float32)
        base_weights = np.ones((length,), dtype=np.float32)
        safe = np.ones((length,), dtype=np.float32)
        combined = np.zeros((length,), dtype=np.float32)
        action_conflict_values = np.full((length,), np.nan, dtype=np.float32)
        bad_neighbor_values = np.full((length,), np.nan, dtype=np.float32)
        pos_sa_values = np.full((length,), np.nan, dtype=np.float32)
        neg_sa_values = np.full((length,), np.nan, dtype=np.float32)

        if demo_id in labeled_positive_set:
            role = "labeled_positive"
            classifier_score = 1.0
        else:
            role = "positive_nn_anchor" if demo_id in positive_anchor_set else "union_only"
            classifier_score = float(score_by_demo.get(demo_id, recipe.coverage_base_floor))
            if role == "positive_nn_anchor":
                base = max(recipe.anchor_base_floor, classifier_score)
                risk_floor = recipe.anchor_risk_floor
            else:
                base = max(recipe.coverage_base_floor, classifier_score)
                risk_floor = recipe.coverage_risk_floor
            base_weights.fill(base)
            for timestep in range(length):
                stats = transition_by_key[(demo_id, timestep)]
                safe[timestep] = stats["safe_factor"]
                combined[timestep] = stats["combined_risk"]
                action_conflict_values[timestep] = stats["action_conflict_distance"]
                bad_neighbor_values[timestep] = stats["bad_neighbor_risk"]
                pos_sa_values[timestep] = stats["pos_state_action_distance"]
                neg_sa_values[timestep] = stats["neg_state_action_distance"]
            weights = (base_weights * (risk_floor + (1.0 - risk_floor) * safe)).astype(np.float32)
            weights = np.clip(weights, 0.0, 1.0).astype(np.float32, copy=False)

        weights_by_demo[demo_id] = {
            "loss_weight": weights,
            "base_weight": base_weights,
            "safe_factor": safe,
            "combined_risk": combined,
            "action_conflict_distance": action_conflict_values,
            "bad_neighbor_risk": bad_neighbor_values,
            "pos_state_action_distance": pos_sa_values,
            "neg_state_action_distance": neg_sa_values,
        }

        weight_stats = summarize_values(weights)
        safe_stats = summarize_values(safe)
        combined_stats = summarize_values(combined)
        rows.append(
            {
                "demo_id": demo_id,
                "role": role,
                "hidden_label": "labeled_positive" if demo_id in labeled_positive_set else ("positive" if demo_id in all_positive_set else "bad"),
                "positive_only_anchor": int(demo_id in positive_anchor_set),
                "union_selected": int(demo_id in union_set),
                "transition_count": int(length),
                "classifier_score": fmt_float(classifier_score),
                "weight_mean": fmt_float(weight_stats["mean"]),
                "weight_min": fmt_float(weight_stats["min"]),
                "weight_max": fmt_float(weight_stats["max"]),
                "weight_mass": fmt_float(float(np.sum(weights))),
                "safe_factor_mean": fmt_float(safe_stats["mean"]),
                "combined_risk_mean": fmt_float(combined_stats["mean"]),
                "action_conflict_distance_mean": fmt_nanmean(action_conflict_values),
                "bad_neighbor_risk_mean": fmt_nanmean(bad_neighbor_values),
                "pos_state_action_distance_mean": fmt_nanmean(pos_sa_values),
                "neg_state_action_distance_mean": fmt_nanmean(neg_sa_values),
            }
        )

    hidden_positive_mass = sum(
        float(np.sum(weights_by_demo[demo_id]["loss_weight"]))
        for demo_id in candidate_unlabeled
        if demo_id in all_positive_set
    )
    hidden_bad_mass = sum(
        float(np.sum(weights_by_demo[demo_id]["loss_weight"]))
        for demo_id in candidate_unlabeled
        if demo_id not in all_positive_set
    )
    labeled_positive_mass = sum(float(np.sum(weights_by_demo[demo_id]["loss_weight"])) for demo_id in labeled_positive)
    hidden_positive_transitions = sum(arrays[demo_id].actions.shape[0] for demo_id in candidate_unlabeled if demo_id in all_positive_set)
    hidden_bad_transitions = sum(arrays[demo_id].actions.shape[0] for demo_id in candidate_unlabeled if demo_id not in all_positive_set)
    summary = {
        "train_demo_count": len(train_demo_ids),
        "labeled_positive_count": len(labeled_positive),
        "selected_unlabeled_count": len(candidate_unlabeled),
        "positive_anchor_unlabeled_count": sum(1 for demo_id in candidate_unlabeled if demo_id in positive_anchor_set),
        "union_only_unlabeled_count": sum(1 for demo_id in candidate_unlabeled if demo_id not in positive_anchor_set),
        "hidden_positive_selected": sum(1 for demo_id in candidate_unlabeled if demo_id in all_positive_set),
        "hidden_bad_selected": sum(1 for demo_id in candidate_unlabeled if demo_id not in all_positive_set),
        "hidden_positive_transition_count": int(hidden_positive_transitions),
        "hidden_bad_transition_count": int(hidden_bad_transitions),
        "labeled_positive_weight_mass": labeled_positive_mass,
        "hidden_positive_weight_mass": hidden_positive_mass,
        "hidden_bad_weight_mass": hidden_bad_mass,
        "hidden_bad_unweighted_transition_fraction": hidden_bad_transitions
        / max(1, hidden_positive_transitions + hidden_bad_transitions),
        "hidden_bad_weighted_mass_fraction": hidden_bad_mass / max(1.0, hidden_positive_mass + hidden_bad_mass),
        "obs_dim": int(pos_batch.observations.shape[1]),
        "action_dim": int(pos_batch.actions.shape[1]),
        "positive_reference_transitions": int(pos_batch.actions.shape[0]),
        "negative_reference_transitions": int(neg_batch.actions.shape[0]),
    }
    return weights_by_demo, rows, summary


def write_weight_hdf5(path: Path, weights_by_demo: dict[str, dict[str, np.ndarray]], metadata: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        f.attrs["metadata_json"] = json.dumps(metadata, sort_keys=True)
        data_group = f.create_group("data")
        for demo_id in sorted_demos(list(weights_by_demo)):
            demo_group = data_group.create_group(demo_id)
            for key, value in weights_by_demo[demo_id].items():
                demo_group.create_dataset(key, data=value.astype(np.float32), compression="gzip")


def write_report(path: Path, summary: dict[str, object], rows: list[dict[str, object]], output_paths: dict[str, Path]) -> None:
    bad_rows = [row for row in rows if row["hidden_label"] == "bad"]
    bad_rows = sorted(bad_rows, key=lambda row: float(row["weight_mean"]))
    union_only_rows = [row for row in rows if row["role"] == "union_only"]
    union_only_pos = sum(1 for row in union_only_rows if row["hidden_label"] == "positive")
    union_only_bad = sum(1 for row in union_only_rows if row["hidden_label"] == "bad")

    lines = [
        "# Candidate A Transition-Weight Preflight",
        "",
        "This preflight builds transition-level loss weights for the Can split-404 failure case.",
        "It does not train a policy; it creates the artifact needed for a weighted BC-RNN-GMM loss hook.",
        "",
        "## Pool",
        "",
        f"- Train demos: `{summary['train_demo_count']}`.",
        f"- Labeled positive anchors: `{summary['labeled_positive_count']}`.",
        (
            f"- Selected unlabeled demos: `{summary['selected_unlabeled_count']}` "
            f"(`{summary['hidden_positive_selected']}` hidden positive, `{summary['hidden_bad_selected']}` hidden bad)."
        ),
        (
            f"- Positive-only anchor demos inside selected pool: `{summary['positive_anchor_unlabeled_count']}`; "
            f"union-only additions: `{summary['union_only_unlabeled_count']}` "
            f"(`{union_only_pos}` hidden positive, `{union_only_bad}` hidden bad)."
        ),
        "",
        "## Weight Mass",
        "",
        f"- Hidden-bad unweighted transition fraction: `{summary['hidden_bad_unweighted_transition_fraction']:.3f}`.",
        f"- Hidden-bad weighted mass fraction: `{summary['hidden_bad_weighted_mass_fraction']:.3f}`.",
        f"- Labeled-positive mass: `{summary['labeled_positive_weight_mass']:.1f}`.",
        f"- Hidden-positive selected mass: `{summary['hidden_positive_weight_mass']:.1f}`.",
        f"- Hidden-bad selected mass: `{summary['hidden_bad_weight_mass']:.1f}`.",
        "",
        "## Lowest-Weight Selected Bad Demos",
        "",
        "| demo | mean weight | safe factor | action conflict | bad-neighbor risk |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in bad_rows[:8]:
        lines.append(
            "| {demo_id} | {weight_mean} | {safe_factor_mean} | {action_conflict_distance_mean} | {bad_neighbor_risk_mean} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- Loss weights HDF5: `{output_paths['weights_hdf5']}`.",
            f"- Per-demo summary CSV: `{output_paths['summary_csv']}`.",
            f"- Recipe JSON: `{output_paths['recipe_json']}`.",
            "",
            "Next trainer hook: load `data/<demo_id>/loss_weight` and multiply the BC-RNN-GMM per-timestep NLL as",
            "`-(log_probs * loss_weight).sum() / loss_weight.sum()` after sequence padding is handled.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    split = read_json(args.split_path)
    positive_only = read_json(args.positive_only_diagnostics)
    union = read_json(args.union_diagnostics)
    hdf5_path = split["hdf5_path"]
    obs_keys = STANDARD_LOW_DIM_OBS if args.obs_keys == "standard" else dataset_obs_keys(hdf5_path)

    score_by_demo = demo_classifier_scores(args.score_rankings)
    positive_anchor_ids = list(positive_only["selected_unlabeled_demos"])
    union_selected_ids = list(union["selected_unlabeled_demos"])
    recipe = WeightRecipe(
        anchor_base_floor=args.anchor_base_floor,
        coverage_base_floor=args.coverage_base_floor,
        anchor_risk_floor=args.anchor_risk_floor,
        coverage_risk_floor=args.coverage_risk_floor,
    )

    weights_by_demo, rows, summary = build_transition_weights(
        split=split,
        hdf5_path=hdf5_path,
        obs_keys=obs_keys,
        score_by_demo=score_by_demo,
        positive_anchor_ids=positive_anchor_ids,
        union_selected_ids=union_selected_ids,
        recipe=recipe,
        chunk_size=args.chunk_size,
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    weights_hdf5 = args.out_dir / "candidate_a_loss_weights.hdf5"
    summary_csv = args.out_dir / "candidate_a_transition_weight_summary.csv"
    recipe_json = args.out_dir / "candidate_a_transition_weight_recipe.json"
    report_path = args.out_dir / "candidate_a_transition_weight_preflight_REPORT.md"

    metadata = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "score_rankings": str(args.score_rankings),
        "positive_only_diagnostics": str(args.positive_only_diagnostics),
        "union_diagnostics": str(args.union_diagnostics),
        "obs_keys": obs_keys,
        "recipe": recipe.__dict__,
        "summary": summary,
    }
    write_weight_hdf5(weights_hdf5, weights_by_demo, metadata)

    fieldnames = [
        "demo_id",
        "role",
        "hidden_label",
        "positive_only_anchor",
        "union_selected",
        "transition_count",
        "classifier_score",
        "weight_mean",
        "weight_min",
        "weight_max",
        "weight_mass",
        "safe_factor_mean",
        "combined_risk_mean",
        "action_conflict_distance_mean",
        "bad_neighbor_risk_mean",
        "pos_state_action_distance_mean",
        "neg_state_action_distance_mean",
    ]
    write_csv(summary_csv, rows, fieldnames)

    recipe_json.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    write_report(
        report_path,
        summary,
        rows,
        {
            "weights_hdf5": weights_hdf5,
            "summary_csv": summary_csv,
            "recipe_json": recipe_json,
        },
    )
    print(json.dumps({"out_dir": str(args.out_dir), **summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
