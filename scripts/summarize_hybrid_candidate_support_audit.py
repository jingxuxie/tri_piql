from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(".")
SPLIT_DIR = ROOT / "results" / "final_paper" / "splits"
SCORE_DIR = ROOT / "results" / "final_paper" / "score_diagnostics"
PER_SEED = ROOT / "results" / "final_paper" / "per_seed"
OUT_DIR = ROOT / "results" / "final_paper" / "tables"

PER_SPLIT_OUT = OUT_DIR / "hybrid_candidate_support_per_split.csv"
SUMMARY_OUT = OUT_DIR / "hybrid_candidate_support_summary.csv"
REPORT_OUT = OUT_DIR / "hybrid_candidate_support_REPORT.md"


@dataclass(frozen=True)
class Setting:
    setting_id: str
    setting_label: str
    split_key: str
    run_key: str
    split_seeds: tuple[int, ...]
    base_k: int
    topk_values: tuple[int, ...]
    row_role: str


SETTINGS = [
    Setting(
        setting_id="can40",
        setting_label="Can 40p/80b",
        split_key="can_paired_pos40_bad80",
        run_key="can_paired_pos40_bad80",
        split_seeds=(11, 22, 33),
        base_k=40,
        topk_values=(20, 40, 60, 80),
        row_role="primary",
    ),
    Setting(
        setting_id="can20",
        setting_label="Can 20p/80b",
        split_key="can_paired_pos20_bad80",
        run_key="can_paired_pos20_bad80",
        split_seeds=(11, 22, 33),
        base_k=20,
        topk_values=(10, 20, 40),
        row_role="diagnostic",
    ),
    Setting(
        setting_id="can80",
        setting_label="Can 80p/80b",
        split_key="can_paired_balanced_80p80b",
        run_key="can_paired_balanced_80p80b",
        split_seeds=(11, 22, 33),
        base_k=80,
        topk_values=(40, 80, 120, 160),
        row_role="diagnostic",
    ),
    Setting(
        setting_id="lift_mg",
        setting_label="Lift MG",
        split_key="lift_mg_mg_sparse",
        run_key="lift_mg_mg_sparse",
        split_seeds=(11, 22, 33),
        base_k=160,
        topk_values=(80, 160, 320, 480),
        row_role="primary",
    ),
]

SETTING_ORDER = {setting.setting_id: idx for idx, setting in enumerate(SETTINGS)}


@dataclass(frozen=True)
class Batch:
    observations: np.ndarray
    actions: np.ndarray
    demo_ids: np.ndarray


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


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


def load_batch(hdf5_path: str, demo_ids: list[str], obs_keys: list[str]) -> Batch:
    obs_chunks = []
    action_chunks = []
    demo_chunks = []
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted(demo_ids, key=demo_sort_key):
            group = f["data"][demo_id]
            actions = np.asarray(group["actions"], dtype=np.float32)
            obs_chunks.append(obs_vector_from_demo(group, obs_keys))
            action_chunks.append(actions)
            demo_chunks.append(np.full((actions.shape[0],), demo_sort_key(demo_id), dtype=np.int32))
    if not obs_chunks:
        raise ValueError("no demos loaded")
    return Batch(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        demo_ids=np.concatenate(demo_chunks, axis=0),
    )


def state_action_features(observations: np.ndarray, actions: np.ndarray) -> np.ndarray:
    return np.concatenate([observations, actions], axis=1).astype(np.float32, copy=False)


def normalize(train_obs: np.ndarray, *arrays: np.ndarray) -> list[np.ndarray]:
    mean = train_obs.mean(axis=0, keepdims=True)
    std = train_obs.std(axis=0, keepdims=True) + 1.0e-6
    return [(array - mean) / std for array in arrays]


def positive_nn_demo_ranking(split: dict) -> list[dict[str, object]]:
    hdf5_path = split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    pos_raw = load_batch(hdf5_path, split["labeled_positive_ids"], obs_keys)
    neg_raw = load_batch(hdf5_path, split["labeled_negative_ids"], obs_keys)
    unl_raw = load_batch(hdf5_path, split["unlabeled_ids"], obs_keys)
    train_obs = np.concatenate([pos_raw.observations, neg_raw.observations, unl_raw.observations], axis=0)
    pos_obs, _neg_obs, unl_obs = normalize(train_obs, pos_raw.observations, neg_raw.observations, unl_raw.observations)

    pos_x = state_action_features(pos_obs, pos_raw.actions)
    unl_x = state_action_features(unl_obs, unl_raw.actions)
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

    demo_scores: list[tuple[int, float]] = []
    for demo_index in np.unique(unl_raw.demo_ids):
        mask = unl_raw.demo_ids == demo_index
        demo_scores.append((int(demo_index), -float(min_dist[mask].mean())))
    demo_scores.sort(key=lambda item: item[1], reverse=True)
    hidden_positive = set(split["all_positive_ids"])
    return [
        {
            "demo_id": f"demo_{demo_index}",
            "positive_nn_rank": rank,
            "positive_nn_score": score,
            "hidden_label": "positive" if f"demo_{demo_index}" in hidden_positive else "bad",
        }
        for rank, (demo_index, score) in enumerate(demo_scores, start=1)
    ]


def classifier_ranking(setting: Setting, split_seed: int) -> tuple[list[str], dict[str, float], dict[str, str], dict[str, float]]:
    score_path = SCORE_DIR / f"{setting.split_key}_split{split_seed}_policy0" / "demo_rankings.csv"
    rows = read_csv(score_path)
    ranked = [row["demo_id"] for row in rows]
    scores = {row["demo_id"]: float(row["score"]) for row in rows}
    labels = {row["demo_id"]: row["hidden_label"] for row in rows}
    thresholds = {
        row["threshold_name"]: float(row["threshold"])
        for row in read_csv(score_path.parent / "selection_rules.csv")
        if row.get("threshold")
    }
    return ranked, scores, labels, thresholds


def diagnostics_selected(setting: Setting, split_seed: int, method: str) -> list[str]:
    path = PER_SEED / f"{setting.run_key}_split{split_seed}_{method}_policy0" / "setup" / "diagnostics.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data["selected_unlabeled_demos"])


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def rank_fusion(
    pos_ranked: list[str],
    clf_ranked: list[str],
    *,
    count: int,
    classifier_weight: float,
) -> list[str]:
    pos_rank = {demo_id: rank for rank, demo_id in enumerate(pos_ranked, start=1)}
    clf_rank = {demo_id: rank for rank, demo_id in enumerate(clf_ranked, start=1)}
    n_pos = max(1, len(pos_ranked))
    n_clf = max(1, len(clf_ranked))
    candidates = set(pos_ranked) | set(clf_ranked)

    def score(demo_id: str) -> tuple[float, int]:
        pos_score = 1.0 - (pos_rank[demo_id] - 1) / max(1, n_pos - 1)
        clf_score = 1.0 - (clf_rank[demo_id] - 1) / max(1, n_clf - 1)
        return ((1.0 - classifier_weight) * pos_score + classifier_weight * clf_score, -clf_rank[demo_id])

    return sorted(candidates, key=score, reverse=True)[:count]


def pareto_nondominated(
    pos_ranked: list[str],
    clf_ranked: list[str],
    *,
    max_count: int,
) -> list[str]:
    pos_rank = {demo_id: rank for rank, demo_id in enumerate(pos_ranked, start=1)}
    clf_rank = {demo_id: rank for rank, demo_id in enumerate(clf_ranked, start=1)}
    candidates = list(pos_rank)
    nondominated = []
    for demo_id in candidates:
        dominated = False
        for other in candidates:
            if other == demo_id:
                continue
            if (
                pos_rank[other] <= pos_rank[demo_id]
                and clf_rank[other] <= clf_rank[demo_id]
                and (pos_rank[other] < pos_rank[demo_id] or clf_rank[other] < clf_rank[demo_id])
            ):
                dominated = True
                break
        if not dominated:
            nondominated.append(demo_id)
    nondominated.sort(key=lambda demo_id: (pos_rank[demo_id] + clf_rank[demo_id], pos_rank[demo_id]))
    if len(nondominated) >= max_count:
        return nondominated[:max_count]
    fill = rank_fusion(pos_ranked, clf_ranked, count=max_count, classifier_weight=0.5)
    return ordered_unique([*nondominated, *fill])[:max_count]


def split_candidates(setting: Setting, split_seed: int) -> tuple[dict[str, list[str]], dict[str, str], dict[str, float], dict[str, object]]:
    split_path = SPLIT_DIR / f"{setting.split_key}_split{split_seed}" / "split_indices.json"
    split = json.loads(split_path.read_text(encoding="utf-8"))
    pos_nn_rows = positive_nn_demo_ranking(split)
    pos_ranked = [row["demo_id"] for row in pos_nn_rows]
    clf_ranked, clf_scores, labels, thresholds = classifier_ranking(setting, split_seed)
    triage = diagnostics_selected(setting, split_seed, "triage_bc")

    k = setting.base_k
    half_k = max(1, k // 2)
    two_k = min(2 * k, len(clf_ranked))
    candidates: dict[str, list[str]] = {}

    for topk in setting.topk_values:
        topk = min(topk, len(pos_ranked))
        candidates[f"positive_nn_top{topk}"] = pos_ranked[:topk]
        candidates[f"classifier_top{topk}"] = clf_ranked[:topk]

    pos_base = pos_ranked[:k]
    clf_base = clf_ranked[:k]
    clf_two = clf_ranked[:two_k]
    candidates[f"hybrid_intersection_pos{k}_classifier{k}"] = [demo_id for demo_id in pos_base if demo_id in set(clf_base)]
    candidates[f"hybrid_intersection_pos{k}_classifier{two_k}"] = [demo_id for demo_id in pos_base if demo_id in set(clf_two)]
    for threshold_name in ("mid_mean", "mid_minpos_maxneg", "pos_min", "pos_p10"):
        if threshold_name not in thresholds:
            continue
        threshold = thresholds[threshold_name]
        filtered = [demo_id for demo_id in pos_base if clf_scores[demo_id] >= threshold]
        candidates[f"hybrid_filter_{threshold_name}_pos{k}"] = filtered
        filled = list(filtered)
        for demo_id in clf_ranked:
            if len(filled) >= k:
                break
            if demo_id not in filled:
                filled.append(demo_id)
        candidates[f"hybrid_filter_{threshold_name}_fill_classifier_to{k}"] = filled

    candidates[f"hybrid_union_pos{k}_classifier{half_k}"] = ordered_unique([*pos_base, *clf_ranked[:half_k]])
    candidates[f"hybrid_union_pos{k}_triage"] = ordered_unique([*pos_base, *triage])
    candidates[f"hybrid_rank_fusion_equal_top{k}"] = rank_fusion(pos_ranked, clf_ranked, count=k, classifier_weight=0.5)
    candidates[f"hybrid_rank_fusion_classifier_heavy_top{k}"] = rank_fusion(
        pos_ranked, clf_ranked, count=k, classifier_weight=0.65
    )
    candidates[f"hybrid_pareto_top{k}"] = pareto_nondominated(pos_ranked, clf_ranked, max_count=k)
    candidates["triage_existing"] = triage

    metadata = {
        "split_path": str(split_path),
        "total_hidden_positive": sum(1 for label in labels.values() if label == "positive"),
        "total_hidden_bad": sum(1 for label in labels.values() if label != "positive"),
        "positive_nn_rows": len(pos_nn_rows),
        "classifier_rows": len(clf_ranked),
    }
    return candidates, labels, clf_scores, metadata


def family(candidate_id: str) -> str:
    if candidate_id.startswith("positive_nn"):
        return "positive-only"
    if candidate_id.startswith("classifier") or candidate_id == "triage_existing":
        return "bad-aware hard"
    return "hybrid"


def summarize_candidate(
    *,
    setting: Setting,
    split_seed: int,
    candidate_id: str,
    demo_ids: list[str],
    labels: dict[str, str],
    clf_scores: dict[str, float],
    metadata: dict[str, object],
) -> dict[str, object]:
    selected = len(demo_ids)
    hidden_positive = sum(1 for demo_id in demo_ids if labels[demo_id] == "positive")
    hidden_bad = selected - hidden_positive
    scores = [clf_scores[demo_id] for demo_id in demo_ids if demo_id in clf_scores]
    return {
        "setting_id": setting.setting_id,
        "setting_label": setting.setting_label,
        "row_role": setting.row_role,
        "split_seed": split_seed,
        "candidate_id": candidate_id,
        "candidate_family": family(candidate_id),
        "selected_unlabeled": selected,
        "hidden_positive_selected": hidden_positive,
        "hidden_bad_selected": hidden_bad,
        "total_hidden_positive": metadata["total_hidden_positive"],
        "total_hidden_bad": metadata["total_hidden_bad"],
        "support_purity": f"{hidden_positive / selected:.3f}" if selected else "",
        "hidden_positive_recall": f"{hidden_positive / int(metadata['total_hidden_positive']):.3f}",
        "hidden_bad_admission": f"{hidden_bad / int(metadata['total_hidden_bad']):.3f}",
        "selected_contamination": f"{hidden_bad / selected:.3f}" if selected else "",
        "classifier_score_mean": f"{float(np.mean(scores)):.3f}" if scores else "",
        "selected_demo_ids": ";".join(demo_ids),
        "source": metadata["split_path"],
    }


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault((str(row["setting_id"]), str(row["candidate_id"])), []).append(row)
    summary = []
    for (_setting_id, _candidate_id), group in grouped.items():
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
                "candidate_id": first["candidate_id"],
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
    summary.sort(
        key=lambda row: (
            SETTING_ORDER[str(row["setting_id"])],
            {"positive-only": 0, "bad-aware hard": 1, "hybrid": 2}.get(str(row["candidate_family"]), 9),
            str(row["candidate_id"]),
        )
    )
    return summary


def frontier_rows(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = []
    by_setting: dict[str, list[dict[str, object]]] = {}
    for row in summary_rows:
        by_setting.setdefault(str(row["setting_id"]), []).append(row)
    for setting_id, rows in by_setting.items():
        for row in rows:
            recall = float(row["hidden_positive_recall"] or 0.0)
            bad = float(row["hidden_bad_admission"] or 0.0)
            dominated = False
            for other in rows:
                if other is row:
                    continue
                other_recall = float(other["hidden_positive_recall"] or 0.0)
                other_bad = float(other["hidden_bad_admission"] or 0.0)
                if other_recall >= recall and other_bad <= bad and (other_recall > recall or other_bad < bad):
                    dominated = True
                    break
            if not dominated:
                out.append(row)
    return out


def best_by_setting(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for setting in SETTINGS:
        setting_rows = [row for row in summary_rows if row["setting_id"] == setting.setting_id]
        pos_base = next(row for row in setting_rows if row["candidate_id"] == f"positive_nn_top{setting.base_k}")
        frontier = frontier_rows(setting_rows)
        hybrid_frontier = [row for row in frontier if row["candidate_family"] == "hybrid"]
        clean_hybrid = min(
            [row for row in setting_rows if row["candidate_family"] == "hybrid"],
            key=lambda row: (-float(row["support_purity"] or 0.0), -float(row["hidden_positive_recall"] or 0.0)),
        )
        coverage_hybrid = max(
            [row for row in setting_rows if row["candidate_family"] == "hybrid"],
            key=lambda row: (float(row["hidden_positive_recall"] or 0.0), -float(row["hidden_bad_admission"] or 0.0)),
        )
        rows.append(
            {
                "setting_id": setting.setting_id,
                "setting_label": setting.setting_label,
                "positive_baseline": pos_base["candidate_id"],
                "positive_baseline_recall": pos_base["hidden_positive_recall"],
                "positive_baseline_bad_admission": pos_base["hidden_bad_admission"],
                "positive_baseline_purity": pos_base["support_purity"],
                "hybrid_frontier_count": len(hybrid_frontier),
                "cleanest_hybrid": clean_hybrid["candidate_id"],
                "cleanest_hybrid_recall": clean_hybrid["hidden_positive_recall"],
                "cleanest_hybrid_bad_admission": clean_hybrid["hidden_bad_admission"],
                "cleanest_hybrid_purity": clean_hybrid["support_purity"],
                "coverage_hybrid": coverage_hybrid["candidate_id"],
                "coverage_hybrid_recall": coverage_hybrid["hidden_positive_recall"],
                "coverage_hybrid_bad_admission": coverage_hybrid["hidden_bad_admission"],
                "coverage_hybrid_purity": coverage_hybrid["support_purity"],
            }
        )
    return rows


def report(summary_rows: list[dict[str, object]]) -> str:
    lines = [
        "# Hybrid Candidate Support Audit",
        "",
        "Generated from staged final-paper split files, classifier score diagnostics, and full positive-NN support rankings.",
        "This is a support-only audit: hidden labels are used only to decide which candidates are worth endpoint training.",
        "",
        "## Setting-Level Takeaways",
        "",
        "| setting | positive baseline | cleanest hybrid | coverage hybrid | hybrid frontier rows |",
        "|---|---|---|---|---:|",
    ]
    for row in best_by_setting(summary_rows):
        lines.append(
            f"| {row['setting_label']} | {row['positive_baseline']} "
            f"recall {row['positive_baseline_recall']}, bad {row['positive_baseline_bad_admission']}, purity {row['positive_baseline_purity']} | "
            f"{row['cleanest_hybrid']} recall {row['cleanest_hybrid_recall']}, bad {row['cleanest_hybrid_bad_admission']}, purity {row['cleanest_hybrid_purity']} | "
            f"{row['coverage_hybrid']} recall {row['coverage_hybrid_recall']}, bad {row['coverage_hybrid_bad_admission']}, purity {row['coverage_hybrid_purity']} | "
            f"{row['hybrid_frontier_count']} |"
        )
    lines.extend(
        [
            "",
            "## Primary Hybrid Rows",
            "",
            "| setting | candidate | family | selected | recall | bad admission | purity |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
    )
    selected_ids = {
        "positive_nn_top40",
        "positive_nn_top160",
        "classifier_top40",
        "classifier_top160",
        "triage_existing",
        "hybrid_intersection_pos40_classifier80",
        "hybrid_filter_mid_mean_pos40",
        "hybrid_filter_mid_mean_fill_classifier_to40",
        "hybrid_rank_fusion_equal_top40",
        "hybrid_union_pos40_classifier20",
        "hybrid_intersection_pos160_classifier320",
        "hybrid_filter_mid_mean_fill_classifier_to160",
        "hybrid_rank_fusion_equal_top160",
        "hybrid_union_pos160_classifier80",
    }
    for row in summary_rows:
        if row["setting_id"] not in {"can40", "lift_mg"} or row["candidate_id"] not in selected_ids:
            continue
        lines.append(
            f"| {row['setting_label']} | {row['candidate_id']} | {row['candidate_family']} | "
            f"{row['selected_unlabeled']} | {row['hidden_positive_recall']} | "
            f"{row['hidden_bad_admission']} | {row['support_purity']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- On Can 40p/80b, strict bad-filtered positive-NN candidates are much cleaner than positive-only top40 but lose hidden-positive coverage; refill and union variants do not improve the positive-only support frontier.",
            "- On Lift MG, classifier-heavy hybrids become very pure but remain far below weighted BC's broad coverage regime; this supports treating Lift as a soft/coverage branch rather than another hard-filter endpoint run.",
            "- The current hybrid support screen does not justify immediate endpoint training for the tested rules. The next useful method work is a stronger proxy or a genuinely new candidate that improves recall without increasing bad admission on Can.",
            "",
            "## Outputs",
            "",
            f"- `{PER_SPLIT_OUT}`",
            f"- `{SUMMARY_OUT}`",
            f"- `{REPORT_OUT}`",
            "",
            f"Summary rows: `{len(summary_rows)}`.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    per_split_rows: list[dict[str, object]] = []
    for setting in SETTINGS:
        for split_seed in setting.split_seeds:
            candidates, labels, clf_scores, metadata = split_candidates(setting, split_seed)
            for candidate_id, demo_ids in candidates.items():
                per_split_rows.append(
                    summarize_candidate(
                        setting=setting,
                        split_seed=split_seed,
                        candidate_id=candidate_id,
                        demo_ids=demo_ids,
                        labels=labels,
                        clf_scores=clf_scores,
                        metadata=metadata,
                    )
                )
    per_split_rows.sort(key=lambda row: (SETTING_ORDER[str(row["setting_id"])], int(row["split_seed"]), str(row["candidate_id"])))
    summary_rows = aggregate(per_split_rows)

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
        "classifier_score_mean",
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
    write_csv(PER_SPLIT_OUT, per_split_rows, per_split_fields)
    write_csv(SUMMARY_OUT, summary_rows, summary_fields)
    REPORT_OUT.write_text(report(summary_rows), encoding="utf-8")
    print(f"wrote {PER_SPLIT_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
