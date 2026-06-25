from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(".")
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from summarize_hard_negative_can_action_conflict_audit import (  # noqa: E402
    DemoFeatures,
    bad_aware_proxy_ranking,
    candidate_family,
    candidate_sets,
    dataset_obs_keys,
    demo_sort_key,
    frame_positive_nn_ranking,
    load_demo_features,
    min_l2_to,
    ordered_unique,
    pairwise_l2,
    rank_fusion,
    read_json,
    sorted_demos,
    stack_features,
    take_ids,
)


BASE_SPLIT = ROOT / "results" / "robomimic_inspection" / "can_paired_low_dim" / "split_indices.json"
OUT_DIR = ROOT / "results" / "final_paper" / "ablations"
SPLIT_DIR = OUT_DIR / "can_coverage_shift_splits"

CONSTRUCTION_OUT = OUT_DIR / "can_coverage_shift_construction.csv"
PER_SPLIT_OUT = OUT_DIR / "can_coverage_shift_support_per_split.csv"
SUMMARY_OUT = OUT_DIR / "can_coverage_shift_summary.csv"
REPORT_OUT = OUT_DIR / "can_coverage_shift_REPORT.md"

SPLIT_SEEDS = (101, 202, 303)
LABEL_BUDGET = 10
UNLABELED_POSITIVE_COUNT = 40
UNLABELED_NEGATIVE_COUNT = 80
VALID_COUNT_PER_CLASS = 10
POSE_CLUSTERS = 4


@dataclass(frozen=True)
class PoseClusters:
    positive_labels: dict[str, int]
    negative_labels: dict[str, int]
    positive_features: dict[str, np.ndarray]
    negative_features: dict[str, np.ndarray]
    centroids: np.ndarray


@dataclass(frozen=True)
class ConstructedSplit:
    split: dict[str, object]
    split_path: Path
    construction_stats: dict[str, object]
    pose_shift_scores: dict[str, float]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_matrix(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = matrix.mean(axis=0, keepdims=True)
    std = matrix.std(axis=0, keepdims=True) + 1.0e-6
    return ((matrix - mean) / std).astype(np.float32, copy=False), mean, std


def initial_pose_features(hdf5_path: str, demo_ids: list[str]) -> dict[str, np.ndarray]:
    features: dict[str, np.ndarray] = {}
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted_demos(demo_ids):
            obs = f["data"][demo_id]["obs"]
            object_pose = np.asarray(obs["object"][0, :7], dtype=np.float32)
            eef_pos = np.asarray(obs["robot0_eef_pos"][0], dtype=np.float32)
            features[demo_id] = np.concatenate([object_pose, eef_pos]).astype(np.float32, copy=False)
    return features


def farthest_point_centroids(matrix: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    first = int(rng.integers(matrix.shape[0]))
    chosen = [first]
    while len(chosen) < k:
        distances = pairwise_l2(matrix, matrix[chosen])
        nearest = distances.min(axis=1)
        for index in np.argsort(-nearest):
            if int(index) not in chosen:
                chosen.append(int(index))
                break
    return matrix[chosen].copy()


def kmeans(matrix: np.ndarray, k: int, seed: int, iterations: int = 50) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    centroids = farthest_point_centroids(matrix, k, rng)
    labels = np.zeros((matrix.shape[0],), dtype=np.int32)
    for _ in range(iterations):
        distances = pairwise_l2(matrix, centroids)
        new_labels = distances.argmin(axis=1).astype(np.int32)
        new_centroids = centroids.copy()
        for cluster in range(k):
            mask = new_labels == cluster
            if np.any(mask):
                new_centroids[cluster] = matrix[mask].mean(axis=0)
            else:
                nearest = distances.min(axis=1)
                new_centroids[cluster] = matrix[int(np.argmax(nearest))]
        if np.array_equal(new_labels, labels) and np.allclose(new_centroids, centroids):
            break
        labels = new_labels
        centroids = new_centroids
    return labels, centroids


def make_pose_clusters(hdf5_path: str, positive_ids: list[str], negative_ids: list[str], seed: int) -> PoseClusters:
    positive_raw = initial_pose_features(hdf5_path, positive_ids)
    negative_raw = initial_pose_features(hdf5_path, negative_ids)
    positive_matrix = np.stack([positive_raw[demo_id] for demo_id in positive_ids])
    positive_norm, mean, std = normalize_matrix(positive_matrix)
    labels_array, centroids = kmeans(positive_norm, POSE_CLUSTERS, seed)

    positive_norm_features = {
        demo_id: positive_norm[index]
        for index, demo_id in enumerate(positive_ids)
    }
    negative_norm_features = {
        demo_id: ((negative_raw[demo_id][None, :] - mean) / std).reshape(-1).astype(np.float32, copy=False)
        for demo_id in negative_ids
    }
    negative_matrix = np.stack([negative_norm_features[demo_id] for demo_id in negative_ids])
    negative_labels_array = pairwise_l2(negative_matrix, centroids).argmin(axis=1).astype(np.int32)
    return PoseClusters(
        positive_labels={demo_id: int(labels_array[index]) for index, demo_id in enumerate(positive_ids)},
        negative_labels={demo_id: int(negative_labels_array[index]) for index, demo_id in enumerate(negative_ids)},
        positive_features=positive_norm_features,
        negative_features=negative_norm_features,
        centroids=centroids,
    )


def ids_by_cluster(ids: list[str], labels: dict[str, int]) -> dict[int, list[str]]:
    grouped = {cluster: [] for cluster in range(POSE_CLUSTERS)}
    for demo_id in ids:
        grouped[labels[demo_id]].append(demo_id)
    for cluster in grouped:
        grouped[cluster] = sorted_demos(grouped[cluster])
    return grouped


def cluster_counts(grouped: dict[int, list[str]]) -> str:
    return ";".join(f"{cluster}:{len(grouped[cluster])}" for cluster in range(POSE_CLUSTERS))


def round_robin_take(
    grouped: dict[int, list[str]],
    *,
    count: int,
    cluster_order: list[int],
) -> list[str]:
    selected: list[str] = []
    offsets = {cluster: 0 for cluster in grouped}
    while len(selected) < count:
        progressed = False
        for cluster in cluster_order:
            bucket = grouped.get(cluster, [])
            offset = offsets.get(cluster, 0)
            if offset >= len(bucket):
                continue
            selected.append(bucket[offset])
            offsets[cluster] = offset + 1
            progressed = True
            if len(selected) >= count:
                break
        if not progressed:
            break
    return selected


def cluster_ids_sorted_by_distance(
    ids: list[str],
    labels: dict[str, int],
    features: dict[str, np.ndarray],
    reference: np.ndarray,
    *,
    descending: bool,
) -> dict[int, list[str]]:
    grouped = ids_by_cluster(ids, labels)
    for cluster, bucket in grouped.items():
        grouped[cluster] = sorted(
            bucket,
            key=lambda demo_id: (float(np.linalg.norm(features[demo_id] - reference)), -demo_sort_key(demo_id)),
            reverse=descending,
        )
    return grouped


def choose_label_cluster(grouped_positive: dict[int, list[str]], rng: np.random.Generator) -> int:
    eligible = [cluster for cluster, bucket in grouped_positive.items() if len(bucket) >= LABEL_BUDGET]
    if not eligible:
        raise ValueError("no positive initial-pose cluster can satisfy the label budget")
    return int(rng.choice(eligible))


def construct_split(base_split: dict, pose: PoseClusters, split_seed: int) -> ConstructedSplit:
    rng = np.random.default_rng(split_seed)
    all_positive = sorted_demos(base_split["all_positive_ids"])
    all_negative = sorted_demos(base_split["all_negative_ids"])
    positive_by_cluster = ids_by_cluster(all_positive, pose.positive_labels)
    negative_by_cluster = ids_by_cluster(all_negative, pose.negative_labels)
    label_cluster = choose_label_cluster(positive_by_cluster, rng)
    label_centroid = pose.centroids[label_cluster]

    positive_label_bucket = sorted(
        positive_by_cluster[label_cluster],
        key=lambda demo_id: (
            float(np.linalg.norm(pose.positive_features[demo_id] - label_centroid)),
            demo_sort_key(demo_id),
        ),
    )
    labeled_positive = positive_label_bucket[:LABEL_BUDGET]

    non_label_positive = [
        demo_id for demo_id in all_positive if pose.positive_labels[demo_id] != label_cluster
    ]
    hidden_grouped = cluster_ids_sorted_by_distance(
        non_label_positive,
        pose.positive_labels,
        pose.positive_features,
        label_centroid,
        descending=True,
    )
    hidden_cluster_order = sorted(
        [cluster for cluster in range(POSE_CLUSTERS) if cluster != label_cluster],
        key=lambda cluster: float(np.linalg.norm(pose.centroids[cluster] - label_centroid)),
        reverse=True,
    )
    hidden_positive = round_robin_take(
        hidden_grouped,
        count=UNLABELED_POSITIVE_COUNT,
        cluster_order=hidden_cluster_order,
    )
    used_positive = set(labeled_positive) | set(hidden_positive)
    remaining_shift_positive = [
        demo_id for demo_id in non_label_positive if demo_id not in used_positive
    ]
    valid_positive_grouped = cluster_ids_sorted_by_distance(
        remaining_shift_positive,
        pose.positive_labels,
        pose.positive_features,
        label_centroid,
        descending=True,
    )
    valid_positive = round_robin_take(
        valid_positive_grouped,
        count=VALID_COUNT_PER_CLASS,
        cluster_order=hidden_cluster_order,
    )
    if len(valid_positive) < VALID_COUNT_PER_CLASS:
        fallback = [
            demo_id for demo_id in all_positive
            if demo_id not in used_positive and demo_id not in set(valid_positive)
        ]
        valid_positive.extend(fallback[: VALID_COUNT_PER_CLASS - len(valid_positive)])

    negative_label_grouped = cluster_ids_sorted_by_distance(
        all_negative,
        pose.negative_labels,
        pose.negative_features,
        label_centroid,
        descending=False,
    )
    negative_cluster_order = list(range(POSE_CLUSTERS))
    rng.shuffle(negative_cluster_order)
    labeled_negative = round_robin_take(
        negative_label_grouped,
        count=LABEL_BUDGET,
        cluster_order=negative_cluster_order,
    )
    remaining_negative = [demo_id for demo_id in all_negative if demo_id not in set(labeled_negative)]
    valid_negative_grouped = cluster_ids_sorted_by_distance(
        remaining_negative,
        pose.negative_labels,
        pose.negative_features,
        label_centroid,
        descending=True,
    )
    valid_negative = round_robin_take(
        valid_negative_grouped,
        count=VALID_COUNT_PER_CLASS,
        cluster_order=negative_cluster_order,
    )
    held_out_negative = set(labeled_negative) | set(valid_negative)
    unlabeled_negative = [demo_id for demo_id in all_negative if demo_id not in held_out_negative]
    if len(unlabeled_negative) != UNLABELED_NEGATIVE_COUNT:
        raise ValueError(f"expected {UNLABELED_NEGATIVE_COUNT} unlabeled negatives, got {len(unlabeled_negative)}")

    unlabeled_ids = sorted_demos([*hidden_positive, *unlabeled_negative])
    valid_ids = sorted_demos([*valid_positive, *valid_negative])
    train_ids = sorted_demos([demo_id for demo_id in [*all_positive, *all_negative] if demo_id not in set(valid_ids)])
    pose_shift_scores = {
        demo_id: float(np.linalg.norm(features[demo_id] - label_centroid))
        for features in (pose.positive_features, pose.negative_features)
        for demo_id in features
    }

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
        "valid_positive_ids": sorted_demos(valid_positive),
        "valid_negative_ids": sorted_demos(valid_negative),
        "unlabeled_positive_count": UNLABELED_POSITIVE_COUNT,
        "unlabeled_negative_count": UNLABELED_NEGATIVE_COUNT,
        "split_seed": split_seed,
        "used_fallback_split": False,
        "diagnostic_split_type": "can_coverage_shift",
        "coverage_shift_label_cluster": label_cluster,
        "coverage_shift_pose_clusters": POSE_CLUSTERS,
        "construction_note": (
            "Labeled positives come from one compact initial-object-pose cluster; hidden positives come from other "
            "successful clusters; labeled and unlabeled bad demos are spread across all pose clusters."
        ),
    }

    def shift_mean(ids: list[str]) -> float:
        return float(np.mean([pose_shift_scores[demo_id] for demo_id in ids])) if ids else 0.0

    construction_stats = {
        "split_seed": split_seed,
        "split_path": str(SPLIT_DIR / f"split{split_seed}" / "split_indices.json"),
        "label_cluster": label_cluster,
        "positive_cluster_counts": cluster_counts(positive_by_cluster),
        "negative_cluster_counts": cluster_counts(negative_by_cluster),
        "labeled_positive_count": len(labeled_positive),
        "labeled_negative_count": len(labeled_negative),
        "unlabeled_positive_count": len(hidden_positive),
        "unlabeled_negative_count": len(unlabeled_negative),
        "valid_positive_count": len(valid_positive),
        "valid_negative_count": len(valid_negative),
        "labeled_negative_cluster_count": len({pose.negative_labels[demo_id] for demo_id in labeled_negative}),
        "hidden_positive_cluster_count": len({pose.positive_labels[demo_id] for demo_id in hidden_positive}),
        "unlabeled_negative_cluster_count": len({pose.negative_labels[demo_id] for demo_id in unlabeled_negative}),
        "labeled_positive_shift_mean": f"{shift_mean(labeled_positive):.3f}",
        "hidden_positive_shift_mean": f"{shift_mean(hidden_positive):.3f}",
        "valid_positive_shift_mean": f"{shift_mean(valid_positive):.3f}",
        "labeled_negative_shift_mean": f"{shift_mean(labeled_negative):.3f}",
        "unlabeled_negative_shift_mean": f"{shift_mean(unlabeled_negative):.3f}",
        "valid_negative_shift_mean": f"{shift_mean(valid_negative):.3f}",
    }

    split_path = SPLIT_DIR / f"split{split_seed}" / "split_indices.json"
    split_path.parent.mkdir(parents=True, exist_ok=True)
    split_path.write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")
    return ConstructedSplit(
        split=split,
        split_path=split_path,
        construction_stats=construction_stats,
        pose_shift_scores=pose_shift_scores,
    )


def coverage_candidate_sets(
    split: dict,
    obs_keys: list[str],
    features: DemoFeatures,
) -> tuple[dict[str, list[str]], dict[str, dict[str, float]]]:
    candidates, scores = candidate_sets(split, obs_keys, features)
    state_action_ranked, _state_action_scores = frame_positive_nn_ranking(split, obs_keys, use_actions=True)
    bad_ranked, _bad_scores = bad_aware_proxy_ranking(split, features)
    pos20 = state_action_ranked[:20]
    bad80 = set(bad_ranked[:80])
    filtered = [demo_id for demo_id in pos20 if demo_id in bad80]
    refill = list(filtered)
    for demo_id in bad_ranked:
        if len(refill) >= 40:
            break
        if demo_id not in refill:
            refill.append(demo_id)
    candidates["hybrid_pos20_filter_badaware80_refill40"] = refill
    candidates["hybrid_rank_fusion_badaware_heavy_top40"] = rank_fusion(
        state_action_ranked,
        bad_ranked,
        count=40,
        second_weight=0.65,
    )
    return candidates, scores


def summarize_candidate(
    *,
    split_seed: int,
    split_path: Path,
    candidate_id: str,
    demo_ids: list[str],
    labels: dict[str, str],
    pose_shift_scores: dict[str, float],
) -> dict[str, object]:
    demo_ids = ordered_unique(demo_ids)
    selected = len(demo_ids)
    hidden_positive = sum(1 for demo_id in demo_ids if labels[demo_id] == "positive")
    hidden_bad = selected - hidden_positive
    total_positive = sum(1 for label in labels.values() if label == "positive")
    total_bad = sum(1 for label in labels.values() if label == "bad")
    selected_shift = [pose_shift_scores[demo_id] for demo_id in demo_ids]
    return {
        "setting_id": "can_coverage_shift",
        "setting_label": "Can scarce-positive coverage shift",
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
        "selected_pose_shift_mean": f"{float(np.mean(selected_shift)):.3f}" if selected_shift else "",
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
        if (recall > base_recall and bad <= base_bad) or (recall >= base_recall and bad < base_bad):
            cleared.append(str(row["candidate_id"]))
    if cleared:
        return (
            "The support gate is cleared by "
            + ", ".join(cleared)
            + ": it improves the state-action positive-NN top40 recall/bad-admission tradeoff under coverage shift."
        )
    return (
        "No tested hidden-label-free support rule clears the coverage-shift support gate against state-action "
        "positive-NN top40; this split is useful as a failure-mode diagnostic, not an endpoint-training trigger yet."
    )


def report(construction_rows: list[dict[str, object]], summary_rows: list[dict[str, object]]) -> str:
    selected_ids = [
        "state_action_positive_nn_top40",
        "state_positive_nn_top40",
        "bad_aware_proxy_top40",
        "hybrid_pos20_filter_badaware80_refill40",
        "hybrid_pos40_filter_badaware80_refill40",
        "hybrid_rank_fusion_badaware_heavy_top40",
        "hybrid_rank_fusion_equal_top40",
        "all_unlabeled_soft_reference",
    ]
    lines = [
        "# Can Scarce-Positive Coverage-Shift Support Audit",
        "",
        "Generated from the paired low-dimensional Can dataset without policy training.",
        "Each split labels successes from one compact initial-object-pose cluster, hides successes from other clusters, and spreads bad demos across all clusters.",
        "Hidden labels are used only for audit summaries.",
        "",
        "## Construction Check",
        "",
        "| split seed | label cluster | positive clusters | negative clusters | hidden-positive clusters | labeled-negative clusters | labeled-positive shift | hidden-positive shift | unlabeled-negative shift |",
        "|---:|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in construction_rows:
        lines.append(
            f"| {row['split_seed']} | {row['label_cluster']} | {row['positive_cluster_counts']} | "
            f"{row['negative_cluster_counts']} | {row['hidden_positive_cluster_count']} | "
            f"{row['labeled_negative_cluster_count']} | {row['labeled_positive_shift_mean']} | "
            f"{row['hidden_positive_shift_mean']} | {row['unlabeled_negative_shift_mean']} |"
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
            "Use this audit as Experiment Group C2 support evidence. A cleared support rule is a candidate for endpoint BC on these generated split files, not a rollout-performance claim.",
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
    all_positive = sorted_demos(base_split["all_positive_ids"])
    all_negative = sorted_demos(base_split["all_negative_ids"])
    all_demo_ids = sorted_demos([*all_positive, *all_negative])
    features = load_demo_features(hdf5_path, all_demo_ids, obs_keys)

    construction_rows: list[dict[str, object]] = []
    per_split_rows: list[dict[str, object]] = []
    for split_seed in SPLIT_SEEDS:
        pose = make_pose_clusters(hdf5_path, all_positive, all_negative, split_seed)
        constructed = construct_split(base_split, pose, split_seed)
        split = constructed.split
        labels = {
            demo_id: "positive" if demo_id in set(split["all_positive_ids"]) else "bad"
            for demo_id in split["unlabeled_ids"]
        }
        candidates, _scores = coverage_candidate_sets(split, obs_keys, features)
        construction_rows.append(constructed.construction_stats)
        for candidate_id, demo_ids in candidates.items():
            per_split_rows.append(
                summarize_candidate(
                    split_seed=split_seed,
                    split_path=constructed.split_path,
                    candidate_id=candidate_id,
                    demo_ids=demo_ids,
                    labels=labels,
                    pose_shift_scores=constructed.pose_shift_scores,
                )
            )

    per_split_rows.sort(key=lambda row: (int(row["split_seed"]), str(row["candidate_id"])))
    summary_rows = aggregate(per_split_rows)
    construction_rows.sort(key=lambda row: int(row["split_seed"]))

    construction_fields = [
        "split_seed",
        "split_path",
        "label_cluster",
        "positive_cluster_counts",
        "negative_cluster_counts",
        "labeled_positive_count",
        "labeled_negative_count",
        "unlabeled_positive_count",
        "unlabeled_negative_count",
        "valid_positive_count",
        "valid_negative_count",
        "labeled_negative_cluster_count",
        "hidden_positive_cluster_count",
        "unlabeled_negative_cluster_count",
        "labeled_positive_shift_mean",
        "hidden_positive_shift_mean",
        "valid_positive_shift_mean",
        "labeled_negative_shift_mean",
        "unlabeled_negative_shift_mean",
        "valid_negative_shift_mean",
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
        "selected_pose_shift_mean",
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
