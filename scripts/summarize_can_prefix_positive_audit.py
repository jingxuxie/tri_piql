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
BASE_SPLIT = ROOT / "results" / "robomimic_inspection" / "can_paired_low_dim" / "split_indices.json"
OUT_DIR = ROOT / "results" / "final_paper" / "ablations"
SPLIT_DIR = OUT_DIR / "can_prefix_positive_splits"

CONSTRUCTION_OUT = OUT_DIR / "can_prefix_positive_construction.csv"
PER_SPLIT_OUT = OUT_DIR / "can_prefix_positive_support_per_split.csv"
SUMMARY_OUT = OUT_DIR / "can_prefix_positive_summary.csv"
REPORT_OUT = OUT_DIR / "can_prefix_positive_REPORT.md"

SPLIT_SEEDS = (101, 202, 303)
LABEL_BUDGET = 10
VALID_COUNT_PER_CLASS = 10
PREFIX_FRACTION = 0.20
PREFIX_MAX_STEPS = 30
PREFIX_MIN_STEPS = 8


@dataclass(frozen=True)
class Batch:
    observations: np.ndarray
    actions: np.ndarray
    demo_ids: np.ndarray


@dataclass(frozen=True)
class PrefixSplit:
    split: dict[str, object]
    split_path: Path
    construction_stats: dict[str, object]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-split", type=Path, default=BASE_SPLIT)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--prefix-fraction", type=float, default=PREFIX_FRACTION)
    parser.add_argument("--prefix-max-steps", type=int, default=PREFIX_MAX_STEPS)
    parser.add_argument("--prefix-min-steps", type=int, default=PREFIX_MIN_STEPS)
    parser.add_argument("--label-budget", type=int, default=LABEL_BUDGET)
    parser.add_argument("--valid-count-per-class", type=int, default=VALID_COUNT_PER_CLASS)
    return parser.parse_args()


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


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


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


def prefix_length(num_steps: int, *, fraction: float, min_steps: int, max_steps: int) -> int:
    count = int(math.ceil(num_steps * fraction))
    count = max(min_steps, count)
    count = min(max_steps, count)
    return max(1, min(num_steps, count))


def load_batch(
    hdf5_path: str,
    demo_ids: list[str],
    obs_keys: list[str],
    *,
    prefix_only: bool,
    prefix_fraction: float,
    prefix_min_steps: int,
    prefix_max_steps: int,
) -> Batch:
    obs_chunks = []
    action_chunks = []
    demo_chunks = []
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted_demos(demo_ids):
            group = f["data"][demo_id]
            observations = obs_vector_from_demo(group, obs_keys)
            actions = np.asarray(group["actions"], dtype=np.float32)
            if prefix_only:
                keep = prefix_length(
                    actions.shape[0],
                    fraction=prefix_fraction,
                    min_steps=prefix_min_steps,
                    max_steps=prefix_max_steps,
                )
                observations = observations[:keep]
                actions = actions[:keep]
            obs_chunks.append(observations)
            action_chunks.append(actions)
            demo_chunks.append(np.full((actions.shape[0],), demo_sort_key(demo_id), dtype=np.int32))
    return Batch(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        demo_ids=np.concatenate(demo_chunks, axis=0),
    )


def construct_split(base_split: dict, split_seed: int, args: argparse.Namespace) -> PrefixSplit:
    rng = np.random.default_rng(split_seed)
    all_positive = sorted_demos(base_split["all_positive_ids"])
    all_negative = sorted_demos(base_split["all_negative_ids"])

    positive_order = list(rng.permutation(all_positive))
    negative_order = list(rng.permutation(all_negative))
    valid_positive = sorted_demos(positive_order[: args.valid_count_per_class])
    valid_negative = sorted_demos(negative_order[: args.valid_count_per_class])
    labeled_positive = sorted_demos(
        positive_order[args.valid_count_per_class : args.valid_count_per_class + args.label_budget]
    )
    labeled_negative = sorted_demos(
        negative_order[args.valid_count_per_class : args.valid_count_per_class + args.label_budget]
    )
    unlabeled_positive = sorted_demos(
        [
            demo_id
            for demo_id in all_positive
            if demo_id not in set(valid_positive) and demo_id not in set(labeled_positive)
        ]
    )
    unlabeled_negative = sorted_demos(
        [
            demo_id
            for demo_id in all_negative
            if demo_id not in set(valid_negative) and demo_id not in set(labeled_negative)
        ]
    )
    unlabeled_ids = sorted_demos([*unlabeled_positive, *unlabeled_negative])
    valid_ids = sorted_demos([*valid_positive, *valid_negative])
    train_ids = sorted_demos([demo_id for demo_id in [*all_positive, *all_negative] if demo_id not in set(valid_ids)])

    split_path = SPLIT_DIR / f"split{split_seed}" / "split_indices.json"
    split = {
        "hdf5_path": base_split["hdf5_path"],
        "all_positive_ids": all_positive,
        "all_negative_ids": all_negative,
        "label_budget": args.label_budget,
        "labeled_positive_ids": labeled_positive,
        "labeled_negative_ids": labeled_negative,
        "labeled_positive_prefix_fraction": args.prefix_fraction,
        "labeled_positive_prefix_min_steps": args.prefix_min_steps,
        "labeled_positive_prefix_max_steps": args.prefix_max_steps,
        "unlabeled_ids": unlabeled_ids,
        "unlabeled_positive_count": len(unlabeled_positive),
        "unlabeled_negative_count": len(unlabeled_negative),
        "train_ids": train_ids,
        "valid_ids": valid_ids,
        "valid_positive_ids": valid_positive,
        "valid_negative_ids": valid_negative,
        "split_seed": split_seed,
        "used_fallback_split": False,
        "diagnostic_split_type": "can_prefix_positive",
        "construction_note": (
            "Only early prefixes of labeled successful demos are used for scoring. "
            "Full positive and bad trajectories are hidden in the unlabeled pool."
        ),
    }
    split_path.parent.mkdir(parents=True, exist_ok=True)
    split_path.write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")

    construction_stats = {
        "split_seed": split_seed,
        "split_path": str(split_path),
        "labeled_positive_count": len(labeled_positive),
        "labeled_negative_count": len(labeled_negative),
        "unlabeled_positive_count": len(unlabeled_positive),
        "unlabeled_negative_count": len(unlabeled_negative),
        "valid_positive_count": len(valid_positive),
        "valid_negative_count": len(valid_negative),
        "prefix_fraction": f"{args.prefix_fraction:.3f}",
        "prefix_min_steps": args.prefix_min_steps,
        "prefix_max_steps": args.prefix_max_steps,
        "labeled_positive_ids": ";".join(labeled_positive),
        "labeled_negative_ids": ";".join(labeled_negative),
    }
    return PrefixSplit(split=split, split_path=split_path, construction_stats=construction_stats)


def normalize(train_obs: np.ndarray, *arrays: np.ndarray) -> list[np.ndarray]:
    mean = train_obs.mean(axis=0, keepdims=True)
    std = train_obs.std(axis=0, keepdims=True) + 1.0e-6
    return [((array - mean) / std).astype(np.float32, copy=False) for array in arrays]


def state_action_features(observations: np.ndarray, actions: np.ndarray) -> np.ndarray:
    return np.concatenate([observations, actions], axis=1).astype(np.float32, copy=False)


def min_squared_distances(query: np.ndarray, support: np.ndarray, chunk_size: int = 4096) -> np.ndarray:
    support_norm = np.sum(support * support, axis=1)[None, :]
    out = np.full((query.shape[0],), np.inf, dtype=np.float32)
    for start in range(0, query.shape[0], chunk_size):
        part = query[start : start + chunk_size]
        distances = np.sum(part * part, axis=1)[:, None] + support_norm - 2.0 * (part @ support.T)
        out[start : start + chunk_size] = np.maximum(distances.min(axis=1), 0.0)
    return out


def demo_mean_scores(batch: Batch, scores: np.ndarray) -> dict[str, float]:
    out = {}
    for demo_index in np.unique(batch.demo_ids):
        mask = batch.demo_ids == demo_index
        out[f"demo_{int(demo_index)}"] = float(scores[mask].mean())
    return out


def transition_rankings(split: dict, obs_keys: list[str], args: argparse.Namespace) -> tuple[dict[str, list[str]], dict[str, dict[str, float]]]:
    hdf5_path = split["hdf5_path"]
    pos_raw = load_batch(
        hdf5_path,
        split["labeled_positive_ids"],
        obs_keys,
        prefix_only=True,
        prefix_fraction=args.prefix_fraction,
        prefix_min_steps=args.prefix_min_steps,
        prefix_max_steps=args.prefix_max_steps,
    )
    neg_raw = load_batch(
        hdf5_path,
        split["labeled_negative_ids"],
        obs_keys,
        prefix_only=False,
        prefix_fraction=args.prefix_fraction,
        prefix_min_steps=args.prefix_min_steps,
        prefix_max_steps=args.prefix_max_steps,
    )
    unl_raw = load_batch(
        hdf5_path,
        split["unlabeled_ids"],
        obs_keys,
        prefix_only=False,
        prefix_fraction=args.prefix_fraction,
        prefix_min_steps=args.prefix_min_steps,
        prefix_max_steps=args.prefix_max_steps,
    )
    train_obs = np.concatenate([pos_raw.observations, neg_raw.observations, unl_raw.observations], axis=0)
    pos_obs, neg_obs, unl_obs = normalize(train_obs, pos_raw.observations, neg_raw.observations, unl_raw.observations)

    pos_state = pos_obs
    neg_state = neg_obs
    unl_state = unl_obs
    pos_state_action = state_action_features(pos_obs, pos_raw.actions)
    neg_state_action = state_action_features(neg_obs, neg_raw.actions)
    unl_state_action = state_action_features(unl_obs, unl_raw.actions)

    state_pos_dist = min_squared_distances(unl_state, pos_state)
    sa_pos_dist = min_squared_distances(unl_state_action, pos_state_action)
    state_neg_dist = min_squared_distances(unl_state, neg_state)
    sa_neg_dist = min_squared_distances(unl_state_action, neg_state_action)

    state_pos_scores = {demo_id: -score for demo_id, score in demo_mean_scores(unl_raw, state_pos_dist).items()}
    sa_pos_scores = {demo_id: -score for demo_id, score in demo_mean_scores(unl_raw, sa_pos_dist).items()}
    state_bad_scores = {
        demo_id: demo_mean_scores(unl_raw, state_neg_dist)[demo_id] - demo_mean_scores(unl_raw, state_pos_dist)[demo_id]
        for demo_id in split["unlabeled_ids"]
    }
    sa_bad_scores = {
        demo_id: demo_mean_scores(unl_raw, sa_neg_dist)[demo_id] - demo_mean_scores(unl_raw, sa_pos_dist)[demo_id]
        for demo_id in split["unlabeled_ids"]
    }

    def ranked(scores: dict[str, float]) -> list[str]:
        return sorted(split["unlabeled_ids"], key=lambda demo_id: (scores[demo_id], -demo_sort_key(demo_id)), reverse=True)

    state_ranked = ranked(state_pos_scores)
    sa_ranked = ranked(sa_pos_scores)
    state_bad_ranked = ranked(state_bad_scores)
    sa_bad_ranked = ranked(sa_bad_scores)
    candidates: dict[str, list[str]] = {}
    for topk in (20, 40, 80, 120):
        candidates[f"prefix_state_nn_top{topk}"] = state_ranked[:topk]
        candidates[f"prefix_state_action_nn_top{topk}"] = sa_ranked[:topk]
        candidates[f"prefix_bad_aware_state_top{topk}"] = state_bad_ranked[:topk]
        candidates[f"prefix_bad_aware_state_action_top{topk}"] = sa_bad_ranked[:topk]
    for topk in (40, 80):
        candidates[f"prefix_rank_fusion_equal_top{topk}"] = rank_fusion(sa_ranked, sa_bad_ranked, count=topk, second_weight=0.5)
        candidates[f"prefix_rank_fusion_badaware_heavy_top{topk}"] = rank_fusion(
            sa_ranked,
            sa_bad_ranked,
            count=topk,
            second_weight=0.65,
        )
    candidates["all_unlabeled_soft_reference"] = list(split["unlabeled_ids"])
    return candidates, {
        "state_positive": state_pos_scores,
        "state_action_positive": sa_pos_scores,
        "state_bad_aware": state_bad_scores,
        "state_action_bad_aware": sa_bad_scores,
    }


def rank_fusion(first_ranked: list[str], second_ranked: list[str], *, count: int, second_weight: float) -> list[str]:
    first_rank = {demo_id: rank for rank, demo_id in enumerate(first_ranked, start=1)}
    second_rank = {demo_id: rank for rank, demo_id in enumerate(second_ranked, start=1)}
    n_first = max(1, len(first_ranked) - 1)
    n_second = max(1, len(second_ranked) - 1)

    def score(demo_id: str) -> tuple[float, int]:
        first_score = 1.0 - (first_rank[demo_id] - 1) / n_first
        second_score = 1.0 - (second_rank[demo_id] - 1) / n_second
        fused = (1.0 - second_weight) * first_score + second_weight * second_score
        return fused, -second_rank[demo_id]

    return sorted(first_rank, key=score, reverse=True)[:count]


def candidate_family(candidate_id: str) -> str:
    if "bad_aware" in candidate_id:
        return "bad-aware"
    if "rank_fusion" in candidate_id:
        return "hybrid"
    if "nn" in candidate_id:
        return "positive-only"
    return "soft-reference"


def summarize_candidate(split: dict, split_path: Path, candidate_id: str, demo_ids: list[str]) -> dict[str, object]:
    selected_ids = ordered_unique(demo_ids)
    hidden_positive_ids = set(split["all_positive_ids"]) & set(split["unlabeled_ids"])
    hidden_bad_ids = set(split["all_negative_ids"]) & set(split["unlabeled_ids"])
    selected = len(selected_ids)
    hidden_positive = sum(1 for demo_id in selected_ids if demo_id in hidden_positive_ids)
    hidden_bad = sum(1 for demo_id in selected_ids if demo_id in hidden_bad_ids)
    total_positive = len(hidden_positive_ids)
    total_bad = len(hidden_bad_ids)
    return {
        "setting_id": "can_prefix_positive",
        "setting_label": "Can prefix-positive",
        "row_role": "support_diagnostic",
        "split_seed": split["split_seed"],
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
        "selected_demo_ids": ";".join(selected_ids),
        "source": str(split_path),
    }


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(str(row["candidate_id"]), []).append(row)
    out = []
    for candidate_id, group in grouped.items():
        selected = sum(int(row["selected_unlabeled"]) for row in group)
        hidden_positive = sum(int(row["hidden_positive_selected"]) for row in group)
        hidden_bad = sum(int(row["hidden_bad_selected"]) for row in group)
        total_positive = sum(int(row["total_hidden_positive"]) for row in group)
        total_bad = sum(int(row["total_hidden_bad"]) for row in group)
        first = group[0]
        out.append(
            {
                "candidate_id": candidate_id,
                "candidate_family": first["candidate_family"],
                "splits": len(group),
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
    family_order = {"positive-only": 0, "bad-aware": 1, "hybrid": 2, "soft-reference": 3}
    return sorted(out, key=lambda row: (family_order.get(str(row["candidate_family"]), 9), str(row["candidate_id"])))


def row_by_id(rows: list[dict[str, object]], candidate_id: str) -> dict[str, object]:
    for row in rows:
        if row["candidate_id"] == candidate_id:
            return row
    raise KeyError(candidate_id)


def format_row(row: dict[str, object]) -> str:
    return (
        f"| {row['candidate_id']} | {row['candidate_family']} | {row['selected_unlabeled']} | "
        f"{row['hidden_positive_recall']} | {row['hidden_bad_admission']} | {row['support_purity']} |"
    )


def best_support_rows(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    def key(row: dict[str, object]) -> tuple[float, float, float]:
        recall = float(row["hidden_positive_recall"])
        bad_admission = float(row["hidden_bad_admission"])
        purity = float(row["support_purity"])
        return recall, -bad_admission, purity

    return sorted(summary_rows, key=key, reverse=True)[:8]


def report(summary_rows: list[dict[str, object]]) -> str:
    baseline40 = row_by_id(summary_rows, "prefix_state_action_nn_top40")
    baseline80 = row_by_id(summary_rows, "prefix_state_action_nn_top80")
    top_rows = best_support_rows(summary_rows)

    clears40 = [
        row["candidate_id"]
        for row in summary_rows
        if row["candidate_id"] != baseline40["candidate_id"]
        and float(row["hidden_positive_recall"]) >= float(baseline40["hidden_positive_recall"])
        and float(row["hidden_bad_admission"]) < float(baseline40["hidden_bad_admission"])
    ]
    clears80 = [
        row["candidate_id"]
        for row in summary_rows
        if row["candidate_id"] != baseline80["candidate_id"]
        and float(row["hidden_positive_recall"]) >= float(baseline80["hidden_positive_recall"])
        and float(row["hidden_bad_admission"]) < float(baseline80["hidden_bad_admission"])
    ]
    gate = (
        "The support gate is cleared by "
        f"{len(set(clears40 + clears80))} candidate(s): `{', '.join(sorted(set(clears40 + clears80)))}`."
        if clears40 or clears80
        else "No bad-aware or hybrid candidate strictly dominates the prefix positive-NN support baselines."
    )

    lines = [
        "# Can Prefix-Positive Support Diagnostic",
        "",
        "This controlled Robomimic diagnostic uses only early prefixes of successful Can demos",
        "as positive labels for scoring. Full successful and failed trajectories are hidden in",
        "the unlabeled pool, and failed demos provide explicit bad labels.",
        "",
        "Artifacts:",
        "",
        f"- Construction CSV: `{CONSTRUCTION_OUT}`",
        f"- Per-split support CSV: `{PER_SPLIT_OUT}`",
        f"- Summary CSV: `{SUMMARY_OUT}`",
        f"- Split files: `{SPLIT_DIR}/split*/split_indices.json`",
        "",
        "## Support Gate",
        "",
        gate,
        "",
        "## Baselines",
        "",
        "| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |",
        "|---|---|---:|---:|---:|---:|",
        format_row(baseline40),
        format_row(baseline80),
        "",
        "## Best Support Rows",
        "",
        "| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |",
        "|---|---|---:|---:|---:|---:|",
    ]
    lines.extend(format_row(row) for row in top_rows)
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- This is support-only evidence. Endpoint training is justified only if a hidden-label-free",
            "  bad-aware or hybrid rule strictly improves over prefix positive-NN at comparable selected count.",
            "- If the gate clears, train the best top80 candidate against prefix state-action positive-NN top80",
            "  on one split before expanding.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    base_split = read_json(args.base_split)
    obs_keys = dataset_obs_keys(base_split["hdf5_path"])

    construction_rows = []
    per_split_rows = []
    for split_seed in SPLIT_SEEDS:
        constructed = construct_split(base_split, split_seed, args)
        construction_rows.append(constructed.construction_stats)
        candidates, _scores = transition_rankings(constructed.split, obs_keys, args)
        for candidate_id, demo_ids in candidates.items():
            per_split_rows.append(
                summarize_candidate(
                    constructed.split,
                    constructed.split_path,
                    candidate_id,
                    demo_ids,
                )
            )

    summary_rows = aggregate(per_split_rows)
    write_csv(
        CONSTRUCTION_OUT,
        construction_rows,
        fieldnames=[
            "split_seed",
            "split_path",
            "labeled_positive_count",
            "labeled_negative_count",
            "unlabeled_positive_count",
            "unlabeled_negative_count",
            "valid_positive_count",
            "valid_negative_count",
            "prefix_fraction",
            "prefix_min_steps",
            "prefix_max_steps",
            "labeled_positive_ids",
            "labeled_negative_ids",
        ],
    )
    write_csv(
        PER_SPLIT_OUT,
        per_split_rows,
        fieldnames=[
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
            "selected_demo_ids",
            "source",
        ],
    )
    write_csv(
        SUMMARY_OUT,
        summary_rows,
        fieldnames=[
            "candidate_id",
            "candidate_family",
            "splits",
            "selected_unlabeled",
            "hidden_positive_selected",
            "hidden_bad_selected",
            "total_hidden_positive",
            "total_hidden_bad",
            "support_purity",
            "hidden_positive_recall",
            "hidden_bad_admission",
            "selected_contamination",
        ],
    )
    REPORT_OUT.write_text(report(summary_rows), encoding="utf-8")
    print(f"wrote {CONSTRUCTION_OUT}")
    print(f"wrote {PER_SPLIT_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
