from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(".")
BASE_SPLIT = ROOT / "results" / "robomimic_inspection" / "can_paired_low_dim" / "split_indices.json"
OUT_DIR = ROOT / "results" / "final_paper" / "ablations"
SPLIT_DIR = OUT_DIR / "hard_negative_can_action_conflict_splits"

CONSTRUCTION_OUT = OUT_DIR / "hard_negative_can_action_conflict_construction.csv"
PER_SPLIT_OUT = OUT_DIR / "hard_negative_can_action_conflict_support_per_split.csv"
SUMMARY_OUT = OUT_DIR / "hard_negative_can_action_conflict_summary.csv"
REPORT_OUT = OUT_DIR / "hard_negative_can_action_conflict_REPORT.md"

SPLIT_SEEDS = (101, 202, 303)
LABEL_BUDGET = 10
UNLABELED_POSITIVE_COUNT = 40
UNLABELED_NEGATIVE_COUNT = 80
VALID_COUNT_PER_CLASS = 10


@dataclass(frozen=True)
class Batch:
    observations: np.ndarray
    actions: np.ndarray
    demo_ids: np.ndarray


@dataclass(frozen=True)
class DemoFeatures:
    state: dict[str, np.ndarray]
    action: dict[str, np.ndarray]
    state_action: dict[str, np.ndarray]


@dataclass(frozen=True)
class ConstructedSplit:
    split: dict[str, object]
    split_path: Path
    construction_stats: dict[str, object]
    hard_scores: dict[str, float]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


def sorted_demos(demo_ids: list[str]) -> list[str]:
    return sorted(demo_ids, key=demo_sort_key)


def dataset_obs_keys(hdf5_path: str) -> list[str]:
    with h5py.File(hdf5_path, "r") as f:
        first_demo = sorted(f["data"].keys(), key=demo_sort_key)[0]
        return sorted(f["data"][first_demo]["obs"].keys())


def obs_vector_from_demo(group, obs_keys: list[str]) -> np.ndarray:
    obs_group = group["obs"]
    parts = [
        np.asarray(obs_group[key], dtype=np.float32).reshape((obs_group[key].shape[0], -1))
        for key in obs_keys
    ]
    return np.concatenate(parts, axis=1)


def demo_summary(observations: np.ndarray, actions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    state = np.concatenate(
        [
            observations[0],
            observations[-1],
            observations.mean(axis=0),
            observations.std(axis=0),
        ]
    )
    action = np.concatenate(
        [
            actions[0],
            actions[-1],
            actions.mean(axis=0),
            actions.std(axis=0),
        ]
    )
    return state.astype(np.float32), action.astype(np.float32)


def normalize_matrix(matrix: np.ndarray) -> np.ndarray:
    mean = matrix.mean(axis=0, keepdims=True)
    std = matrix.std(axis=0, keepdims=True) + 1.0e-6
    return ((matrix - mean) / std).astype(np.float32, copy=False)


def load_demo_features(hdf5_path: str, demo_ids: list[str], obs_keys: list[str]) -> DemoFeatures:
    state_rows: list[np.ndarray] = []
    action_rows: list[np.ndarray] = []
    ordered = sorted_demos(demo_ids)
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in ordered:
            group = f["data"][demo_id]
            observations = obs_vector_from_demo(group, obs_keys)
            actions = np.asarray(group["actions"], dtype=np.float32)
            state, action = demo_summary(observations, actions)
            state_rows.append(state)
            action_rows.append(action)

    state_matrix = normalize_matrix(np.stack(state_rows))
    action_matrix = normalize_matrix(np.stack(action_rows))
    state = {demo_id: state_matrix[i] for i, demo_id in enumerate(ordered)}
    action = {demo_id: action_matrix[i] for i, demo_id in enumerate(ordered)}
    state_action = {
        demo_id: np.concatenate([state[demo_id], action[demo_id]]).astype(np.float32, copy=False)
        for demo_id in ordered
    }
    return DemoFeatures(state=state, action=action, state_action=state_action)


def load_batch(hdf5_path: str, demo_ids: list[str], obs_keys: list[str]) -> Batch:
    obs_chunks = []
    action_chunks = []
    demo_chunks = []
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted_demos(demo_ids):
            group = f["data"][demo_id]
            actions = np.asarray(group["actions"], dtype=np.float32)
            obs_chunks.append(obs_vector_from_demo(group, obs_keys))
            action_chunks.append(actions)
            demo_chunks.append(np.full((actions.shape[0],), demo_sort_key(demo_id), dtype=np.int32))
    return Batch(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        demo_ids=np.concatenate(demo_chunks, axis=0),
    )


def pairwise_l2(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    squared = np.sum(a * a, axis=1)[:, None] + np.sum(b * b, axis=1)[None, :] - 2.0 * (a @ b.T)
    return np.sqrt(np.maximum(squared, 0.0))


def min_l2_to(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    distances = pairwise_l2(a, b)
    argmin = distances.argmin(axis=1)
    return distances[np.arange(distances.shape[0]), argmin], argmin


def stack_features(features: dict[str, np.ndarray], demo_ids: list[str]) -> np.ndarray:
    return np.stack([features[demo_id] for demo_id in demo_ids]).astype(np.float32, copy=False)


def zscore(values: np.ndarray) -> np.ndarray:
    return (values - values.mean()) / (values.std() + 1.0e-6)


def take_ids(ids: list[str], indices: np.ndarray) -> list[str]:
    return [ids[int(index)] for index in indices]


def construct_split(base_split: dict, features: DemoFeatures, split_seed: int) -> ConstructedSplit:
    rng = np.random.default_rng(split_seed)
    all_positive = sorted_demos(base_split["all_positive_ids"])
    all_negative = sorted_demos(base_split["all_negative_ids"])

    anchor = str(rng.choice(all_positive))
    positive_state = stack_features(features.state, all_positive)
    anchor_state = stack_features(features.state, [anchor])
    positive_anchor_dist = pairwise_l2(positive_state, anchor_state).reshape(-1)
    labeled_positive = take_ids(all_positive, np.argsort(positive_anchor_dist)[:LABEL_BUDGET])

    remaining_positive = [demo_id for demo_id in all_positive if demo_id not in set(labeled_positive)]
    remaining_positive_state = stack_features(features.state, remaining_positive)
    labeled_positive_state = stack_features(features.state, labeled_positive)
    positive_gap, _ = min_l2_to(remaining_positive_state, labeled_positive_state)
    hidden_positive = take_ids(
        remaining_positive,
        np.argsort(-positive_gap)[:UNLABELED_POSITIVE_COUNT],
    )
    leftover_positive = [demo_id for demo_id in remaining_positive if demo_id not in set(hidden_positive)]
    valid_positive = sorted_demos(list(rng.choice(leftover_positive, size=VALID_COUNT_PER_CLASS, replace=False)))

    negative_state = stack_features(features.state, all_negative)
    negative_action = stack_features(features.action, all_negative)
    labeled_positive_action = stack_features(features.action, labeled_positive)
    negative_state_dist, nearest_positive = min_l2_to(negative_state, labeled_positive_state)
    nearest_positive_action = labeled_positive_action[nearest_positive]
    negative_action_conflict = np.sqrt(np.maximum(np.sum((negative_action - nearest_positive_action) ** 2, axis=1), 0.0))
    hard_score_array = zscore(-negative_state_dist) + 0.5 * zscore(negative_action_conflict)
    hard_order = np.argsort(-hard_score_array)

    labeled_negative = take_ids(all_negative, hard_order[:LABEL_BUDGET])
    unlabeled_negative = take_ids(
        all_negative,
        hard_order[LABEL_BUDGET : LABEL_BUDGET + UNLABELED_NEGATIVE_COUNT],
    )
    valid_negative = take_ids(
        all_negative,
        hard_order[LABEL_BUDGET + UNLABELED_NEGATIVE_COUNT : LABEL_BUDGET + UNLABELED_NEGATIVE_COUNT + VALID_COUNT_PER_CLASS],
    )

    unlabeled_ids = sorted_demos([*hidden_positive, *unlabeled_negative])
    valid_ids = sorted_demos([*valid_positive, *valid_negative])
    train_ids = sorted_demos([demo_id for demo_id in [*all_positive, *all_negative] if demo_id not in set(valid_ids)])
    hard_scores = {demo_id: float(score) for demo_id, score in zip(all_negative, hard_score_array)}
    state_distances = {demo_id: float(dist) for demo_id, dist in zip(all_negative, negative_state_dist)}
    action_conflicts = {demo_id: float(dist) for demo_id, dist in zip(all_negative, negative_action_conflict)}

    split = {
        "hdf5_path": base_split["hdf5_path"],
        "all_positive_ids": all_positive,
        "all_negative_ids": all_negative,
        "label_budget": LABEL_BUDGET,
        "labeled_positive_ids": sorted_demos(labeled_positive),
        "labeled_negative_ids": sorted_demos(labeled_negative),
        "unlabeled_ids": unlabeled_ids,
        "train_ids": train_ids,
        "valid_ids": valid_ids,
        "valid_positive_ids": valid_positive,
        "valid_negative_ids": sorted_demos(valid_negative),
        "unlabeled_positive_count": UNLABELED_POSITIVE_COUNT,
        "unlabeled_negative_count": UNLABELED_NEGATIVE_COUNT,
        "split_seed": split_seed,
        "used_fallback_split": False,
        "diagnostic_split_type": "hard_negative_can_action_conflict",
        "construction_note": (
            "Labeled positives are a compact successful cluster; hidden positives are far from that cluster; "
            "labeled and unlabeled bad demos are ranked by near-positive state distance plus action conflict."
        ),
    }

    hidden_positive_gap = [
        float(positive_gap[remaining_positive.index(demo_id)]) for demo_id in hidden_positive
    ]
    construction_stats = {
        "split_seed": split_seed,
        "split_path": str(SPLIT_DIR / f"split{split_seed}" / "split_indices.json"),
        "positive_anchor_demo": anchor,
        "labeled_positive_count": len(labeled_positive),
        "labeled_negative_count": len(labeled_negative),
        "unlabeled_positive_count": len(hidden_positive),
        "unlabeled_negative_count": len(unlabeled_negative),
        "valid_positive_count": len(valid_positive),
        "valid_negative_count": len(valid_negative),
        "hidden_positive_state_gap_mean": f"{float(np.mean(hidden_positive_gap)):.3f}",
        "hidden_positive_state_gap_min": f"{float(np.min(hidden_positive_gap)):.3f}",
        "unlabeled_bad_state_distance_mean": f"{float(np.mean([state_distances[x] for x in unlabeled_negative])):.3f}",
        "valid_bad_state_distance_mean": f"{float(np.mean([state_distances[x] for x in valid_negative])):.3f}",
        "unlabeled_bad_action_conflict_mean": f"{float(np.mean([action_conflicts[x] for x in unlabeled_negative])):.3f}",
        "valid_bad_action_conflict_mean": f"{float(np.mean([action_conflicts[x] for x in valid_negative])):.3f}",
        "unlabeled_bad_hard_score_mean": f"{float(np.mean([hard_scores[x] for x in unlabeled_negative])):.3f}",
        "valid_bad_hard_score_mean": f"{float(np.mean([hard_scores[x] for x in valid_negative])):.3f}",
    }

    split_path = SPLIT_DIR / f"split{split_seed}" / "split_indices.json"
    split_path.parent.mkdir(parents=True, exist_ok=True)
    split_path.write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")
    return ConstructedSplit(
        split=split,
        split_path=split_path,
        construction_stats=construction_stats,
        hard_scores=hard_scores,
    )


def normalize_observations(train_obs: np.ndarray, *arrays: np.ndarray) -> list[np.ndarray]:
    mean = train_obs.mean(axis=0, keepdims=True)
    std = train_obs.std(axis=0, keepdims=True) + 1.0e-6
    return [(array - mean) / std for array in arrays]


def frame_positive_nn_ranking(split: dict, obs_keys: list[str], *, use_actions: bool) -> tuple[list[str], dict[str, float]]:
    hdf5_path = split["hdf5_path"]
    pos_raw = load_batch(hdf5_path, split["labeled_positive_ids"], obs_keys)
    neg_raw = load_batch(hdf5_path, split["labeled_negative_ids"], obs_keys)
    unl_raw = load_batch(hdf5_path, split["unlabeled_ids"], obs_keys)
    train_obs = np.concatenate([pos_raw.observations, neg_raw.observations, unl_raw.observations], axis=0)
    pos_obs, _neg_obs, unl_obs = normalize_observations(train_obs, pos_raw.observations, neg_raw.observations, unl_raw.observations)

    if use_actions:
        pos_x = np.concatenate([pos_obs, pos_raw.actions], axis=1)
        unl_x = np.concatenate([unl_obs, unl_raw.actions], axis=1)
    else:
        pos_x = pos_obs
        unl_x = unl_obs
    feature_mean = np.mean(np.concatenate([pos_x, unl_x], axis=0), axis=0, keepdims=True)
    feature_std = np.std(np.concatenate([pos_x, unl_x], axis=0), axis=0, keepdims=True) + 1.0e-6
    pos_x = ((pos_x - feature_mean) / feature_std).astype(np.float32, copy=False)
    unl_x = ((unl_x - feature_mean) / feature_std).astype(np.float32, copy=False)

    pos_norm = np.sum(pos_x * pos_x, axis=1)[None, :]
    min_dist = np.full((unl_x.shape[0],), np.inf, dtype=np.float32)
    chunk = 4096
    for start in range(0, unl_x.shape[0], chunk):
        part = unl_x[start : start + chunk]
        distances = np.sum(part * part, axis=1)[:, None] + pos_norm - 2.0 * (part @ pos_x.T)
        min_dist[start : start + chunk] = np.maximum(distances.min(axis=1), 0.0)

    scores: list[tuple[str, float]] = []
    for demo_index in np.unique(unl_raw.demo_ids):
        mask = unl_raw.demo_ids == demo_index
        scores.append((f"demo_{int(demo_index)}", -float(min_dist[mask].mean())))
    scores.sort(key=lambda item: item[1], reverse=True)
    return [demo_id for demo_id, _score in scores], dict(scores)


def bad_aware_proxy_ranking(split: dict, features: DemoFeatures) -> tuple[list[str], dict[str, float]]:
    labeled_positive = list(split["labeled_positive_ids"])
    labeled_negative = list(split["labeled_negative_ids"])
    unlabeled = list(split["unlabeled_ids"])
    pos_x = stack_features(features.state_action, labeled_positive)
    neg_x = stack_features(features.state_action, labeled_negative)
    unl_x = stack_features(features.state_action, unlabeled)
    pos_dist, _ = min_l2_to(unl_x, pos_x)
    neg_dist, _ = min_l2_to(unl_x, neg_x)
    scores = {
        demo_id: float(neg_distance - pos_distance)
        for demo_id, pos_distance, neg_distance in zip(unlabeled, pos_dist, neg_dist)
    }
    ranked = sorted(unlabeled, key=lambda demo_id: (scores[demo_id], -demo_sort_key(demo_id)), reverse=True)
    return ranked, scores


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def rank_fusion(
    first_ranked: list[str],
    second_ranked: list[str],
    *,
    count: int,
    second_weight: float,
) -> list[str]:
    first_rank = {demo_id: rank for rank, demo_id in enumerate(first_ranked, start=1)}
    second_rank = {demo_id: rank for rank, demo_id in enumerate(second_ranked, start=1)}
    candidates = set(first_rank) & set(second_rank)
    n_first = max(1, len(first_ranked) - 1)
    n_second = max(1, len(second_ranked) - 1)

    def score(demo_id: str) -> tuple[float, int]:
        first_score = 1.0 - (first_rank[demo_id] - 1) / n_first
        second_score = 1.0 - (second_rank[demo_id] - 1) / n_second
        fused = (1.0 - second_weight) * first_score + second_weight * second_score
        return fused, -second_rank[demo_id]

    return sorted(candidates, key=score, reverse=True)[:count]


def candidate_sets(split: dict, obs_keys: list[str], features: DemoFeatures) -> tuple[dict[str, list[str]], dict[str, dict[str, float]]]:
    state_ranked, state_scores = frame_positive_nn_ranking(split, obs_keys, use_actions=False)
    state_action_ranked, state_action_scores = frame_positive_nn_ranking(split, obs_keys, use_actions=True)
    bad_ranked, bad_scores = bad_aware_proxy_ranking(split, features)

    candidates: dict[str, list[str]] = {}
    for topk in (20, 40, 60, 80):
        candidates[f"state_positive_nn_top{topk}"] = state_ranked[:topk]
        candidates[f"state_action_positive_nn_top{topk}"] = state_action_ranked[:topk]
        candidates[f"bad_aware_proxy_top{topk}"] = bad_ranked[:topk]

    pos40 = state_action_ranked[:40]
    bad40 = bad_ranked[:40]
    bad80 = set(bad_ranked[:80])
    candidates["hybrid_intersection_pos40_badaware40"] = [demo_id for demo_id in pos40 if demo_id in set(bad40)]
    filtered = [demo_id for demo_id in pos40 if demo_id in bad80]
    candidates["hybrid_pos40_filter_badaware80"] = filtered
    refill = list(filtered)
    for demo_id in bad_ranked:
        if len(refill) >= 40:
            break
        if demo_id not in refill:
            refill.append(demo_id)
    candidates["hybrid_pos40_filter_badaware80_refill40"] = refill
    candidates["hybrid_rank_fusion_equal_top40"] = rank_fusion(
        state_action_ranked,
        bad_ranked,
        count=40,
        second_weight=0.5,
    )
    candidates["hybrid_rank_fusion_badaware_heavy_top40"] = rank_fusion(
        state_action_ranked,
        bad_ranked,
        count=40,
        second_weight=0.65,
    )
    candidates["all_unlabeled_soft_reference"] = list(split["unlabeled_ids"])
    return candidates, {
        "state_positive": state_scores,
        "state_action_positive": state_action_scores,
        "bad_aware": bad_scores,
    }


def candidate_family(candidate_id: str) -> str:
    if candidate_id.startswith("state_"):
        return "positive-only"
    if candidate_id.startswith("bad_aware"):
        return "bad-aware proxy"
    if candidate_id.startswith("hybrid"):
        return "hybrid"
    return "soft-reference"


def summarize_candidate(
    *,
    split_seed: int,
    split_path: Path,
    candidate_id: str,
    demo_ids: list[str],
    labels: dict[str, str],
    hard_scores: dict[str, float],
) -> dict[str, object]:
    demo_ids = ordered_unique(demo_ids)
    selected = len(demo_ids)
    hidden_positive = sum(1 for demo_id in demo_ids if labels[demo_id] == "positive")
    hidden_bad = selected - hidden_positive
    total_positive = sum(1 for label in labels.values() if label == "positive")
    total_bad = sum(1 for label in labels.values() if label == "bad")
    selected_hard_scores = [hard_scores[demo_id] for demo_id in demo_ids if demo_id in hard_scores]
    return {
        "setting_id": "can_hard_negative_action_conflict",
        "setting_label": "Can hard-negative/action-conflict",
        "row_role": "support_diagnostic",
        "split_seed": split_seed,
        "candidate_id": candidate_id,
        "candidate_family": candidate_family(candidate_id),
        "selected_unlabeled": selected,
        "hidden_positive_selected": hidden_positive,
        "hidden_bad_selected": hidden_bad,
        "total_hidden_positive": total_positive,
        "total_hidden_bad": total_bad,
        "support_purity": f"{hidden_positive / selected:.3f}" if selected else "",
        "hidden_positive_recall": f"{hidden_positive / total_positive:.3f}" if total_positive else "",
        "hidden_bad_admission": f"{hidden_bad / total_bad:.3f}" if total_bad else "",
        "selected_contamination": f"{hidden_bad / selected:.3f}" if selected else "",
        "selected_bad_hard_score_mean": f"{float(np.mean(selected_hard_scores)):.3f}" if selected_hard_scores else "",
        "selected_demo_ids": ";".join(demo_ids),
        "source": str(split_path),
    }


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["candidate_id"]), []).append(row)
    summary = []
    for candidate_id, group in grouped.items():
        first = group[0]
        selected = sum(int(row["selected_unlabeled"]) for row in group)
        hidden_positive = sum(int(row["hidden_positive_selected"]) for row in group)
        hidden_bad = sum(int(row["hidden_bad_selected"]) for row in group)
        total_positive = sum(int(row["total_hidden_positive"]) for row in group)
        total_bad = sum(int(row["total_hidden_bad"]) for row in group)
        summary.append(
            {
                "setting_id": first["setting_id"],
                "setting_label": first["setting_label"],
                "row_role": first["row_role"],
                "candidate_id": candidate_id,
                "candidate_family": first["candidate_family"],
                "split_count": len(group),
                "selected_unlabeled": selected,
                "hidden_positive_selected": hidden_positive,
                "hidden_bad_selected": hidden_bad,
                "total_hidden_positive": total_positive,
                "total_hidden_bad": total_bad,
                "support_purity": f"{hidden_positive / selected:.3f}" if selected else "",
                "hidden_positive_recall": f"{hidden_positive / total_positive:.3f}" if total_positive else "",
                "hidden_bad_admission": f"{hidden_bad / total_bad:.3f}" if total_bad else "",
                "selected_contamination": f"{hidden_bad / selected:.3f}" if selected else "",
            }
        )
    family_order = {"positive-only": 0, "bad-aware proxy": 1, "hybrid": 2, "soft-reference": 3}
    summary.sort(key=lambda row: (family_order.get(str(row["candidate_family"]), 9), str(row["candidate_id"])))
    return summary


def row_by_id(summary_rows: list[dict[str, object]], candidate_id: str) -> dict[str, object]:
    for row in summary_rows:
        if row["candidate_id"] == candidate_id:
            return row
    raise KeyError(candidate_id)


def format_row(row: dict[str, object]) -> str:
    return (
        f"| {row['candidate_id']} | {row['candidate_family']} | {row['selected_unlabeled']} | "
        f"{row['hidden_positive_recall']} | {row['hidden_bad_admission']} | {row['support_purity']} |"
    )


def support_gate(summary_rows: list[dict[str, object]]) -> str:
    baseline = row_by_id(summary_rows, "state_action_positive_nn_top40")
    base_recall = float(baseline["hidden_positive_recall"])
    base_bad = float(baseline["hidden_bad_admission"])
    cleared = []
    for row in summary_rows:
        if row["candidate_id"] == baseline["candidate_id"]:
            continue
        recall = float(row["hidden_positive_recall"] or 0.0)
        bad = float(row["hidden_bad_admission"] or 0.0)
        if recall >= base_recall and bad < base_bad:
            cleared.append(str(row["candidate_id"]))
    if cleared:
        return (
            "The support gate is cleared by "
            + ", ".join(cleared)
            + ": it matches or exceeds state-action positive-NN recall while reducing hidden-bad admission."
        )
    return (
        "No tested hidden-label-free support rule clears the support gate against state-action positive-NN top40; "
        "treat this as a diagnostic benchmark construction, not an endpoint-training trigger yet."
    )


def report(construction_rows: list[dict[str, object]], summary_rows: list[dict[str, object]]) -> str:
    selected_ids = [
        "state_action_positive_nn_top40",
        "state_positive_nn_top40",
        "bad_aware_proxy_top40",
        "hybrid_pos40_filter_badaware80_refill40",
        "hybrid_rank_fusion_equal_top40",
        "all_unlabeled_soft_reference",
    ]
    lines = [
        "# Hard-Negative Can Action-Conflict Support Audit",
        "",
        "Generated from the paired low-dimensional Can dataset without policy training.",
        "The diagnostic constructs compact-positive splits, places hidden positives far from the labeled-positive cluster, and ranks bad demos by near-positive state distance plus action conflict.",
        "Hidden labels are used only for audit summaries.",
        "",
        "## Construction Check",
        "",
            "| split seed | hidden-positive state gap mean | unlabeled-bad state distance mean | valid-bad state distance mean | unlabeled-bad action conflict mean | valid-bad action conflict mean | unlabeled-bad hard score mean | valid-bad hard score mean |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in construction_rows:
        lines.append(
            f"| {row['split_seed']} | {row['hidden_positive_state_gap_mean']} | "
            f"{row['unlabeled_bad_state_distance_mean']} | {row['valid_bad_state_distance_mean']} | "
            f"{row['unlabeled_bad_action_conflict_mean']} | {row['valid_bad_action_conflict_mean']} | "
            f"{row['unlabeled_bad_hard_score_mean']} | {row['valid_bad_hard_score_mean']} |"
        )
    lines.extend(
        [
            "",
            "## Support Gate",
            "",
            "Rows aggregate over the three generated split seeds.",
            "",
            "| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for candidate_id in selected_ids:
        lines.append(format_row(row_by_id(summary_rows, candidate_id)))
    lines.extend(
        [
            "",
            "## Decision",
            "",
            support_gate(summary_rows),
            "",
            "Use this audit as Experiment Group C1 support evidence. A cleared support rule is a candidate for endpoint BC on these generated split files, not a rollout-performance claim.",
            "",
            "## Outputs",
            "",
            f"- `{CONSTRUCTION_OUT}`",
            f"- `{PER_SPLIT_OUT}`",
            f"- `{SUMMARY_OUT}`",
            f"- `{REPORT_OUT}`",
            f"- `{SPLIT_DIR}`",
            "",
            f"Summary rows: `{len(summary_rows)}`. Per-split rows: `{sum(1 for _ in open(PER_SPLIT_OUT, encoding='utf-8')) - 1 if PER_SPLIT_OUT.exists() else 0}`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    base_split = read_json(BASE_SPLIT)
    hdf5_path = base_split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    all_demo_ids = sorted_demos([*base_split["all_positive_ids"], *base_split["all_negative_ids"]])
    features = load_demo_features(hdf5_path, all_demo_ids, obs_keys)

    construction_rows: list[dict[str, object]] = []
    per_split_rows: list[dict[str, object]] = []
    for split_seed in SPLIT_SEEDS:
        constructed = construct_split(base_split, features, split_seed)
        split = constructed.split
        labels = {
            demo_id: "positive" if demo_id in set(split["all_positive_ids"]) else "bad"
            for demo_id in split["unlabeled_ids"]
        }
        candidates, _scores = candidate_sets(split, obs_keys, features)
        construction_rows.append(constructed.construction_stats)
        for candidate_id, demo_ids in candidates.items():
            per_split_rows.append(
                summarize_candidate(
                    split_seed=split_seed,
                    split_path=constructed.split_path,
                    candidate_id=candidate_id,
                    demo_ids=demo_ids,
                    labels=labels,
                    hard_scores=constructed.hard_scores,
                )
            )

    per_split_rows.sort(key=lambda row: (int(row["split_seed"]), str(row["candidate_id"])))
    summary_rows = aggregate(per_split_rows)

    construction_fields = [
        "split_seed",
        "split_path",
        "positive_anchor_demo",
        "labeled_positive_count",
        "labeled_negative_count",
        "unlabeled_positive_count",
        "unlabeled_negative_count",
        "valid_positive_count",
        "valid_negative_count",
        "hidden_positive_state_gap_mean",
        "hidden_positive_state_gap_min",
        "unlabeled_bad_state_distance_mean",
        "valid_bad_state_distance_mean",
        "unlabeled_bad_action_conflict_mean",
        "valid_bad_action_conflict_mean",
        "unlabeled_bad_hard_score_mean",
        "valid_bad_hard_score_mean",
    ]
    per_split_fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "split_seed",
        "candidate_id",
        "candidate_family",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "selected_bad_hard_score_mean",
        "selected_demo_ids",
        "source",
    ]
    summary_fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "candidate_id",
        "candidate_family",
        "split_count",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
    ]

    write_csv(CONSTRUCTION_OUT, construction_rows, construction_fields)
    write_csv(PER_SPLIT_OUT, per_split_rows, per_split_fields)
    write_csv(SUMMARY_OUT, summary_rows, summary_fields)
    REPORT_OUT.write_text(report(construction_rows, summary_rows), encoding="utf-8")

    print(f"wrote {CONSTRUCTION_OUT}")
    print(f"wrote {PER_SPLIT_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
