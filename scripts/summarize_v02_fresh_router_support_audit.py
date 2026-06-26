from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from summarize_hybrid_candidate_support_audit import positive_nn_demo_ranking
from summarize_v02_action_risk_feature_screen import split_risk_scores


DEFAULT_ROOT = Path("results/final_paper_v02")
DEFAULT_OUT_DIR = DEFAULT_ROOT / "tables"

TASKS = {
    "can40": {
        "setting_label": "Can 40p/80b",
        "split_key": "can_paired_pos40_bad80",
        "row_role": "primary",
        "top_k": 40,
    },
    "lift_mg": {
        "setting_label": "Lift MG",
        "split_key": "lift_mg_mg_sparse",
        "row_role": "primary",
        "top_k": 160,
    },
}


@dataclass(frozen=True)
class RouterDecision:
    branch: str
    reason: str
    estimated_positive_mass: float
    count_ge_pos_min: int
    labeled_positive_min: float
    labeled_positive_p10: float
    labeled_positive_mean: float
    labeled_negative_mean: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--tasks", nargs="+", default=["can40", "lift_mg"], choices=sorted(TASKS))
    parser.add_argument("--split-seeds", nargs="+", type=int, default=[101, 202, 303])
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.3f}"


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def split_path(root: Path, task: str, split_seed: int) -> Path:
    split_key = TASKS[task]["split_key"]
    return root / "splits" / f"{split_key}_split{split_seed}" / "split_indices.json"


def score_dir(root: Path, task: str, split_seed: int) -> Path:
    split_key = TASKS[task]["split_key"]
    return root / "score_diagnostics" / f"{split_key}_split{split_seed}_policy0"


def router_decision(score_path: Path) -> RouterDecision:
    summary_rows = read_csv(score_path / "score_summary.csv")
    ranking_rows = read_csv(score_path / "demo_rankings.csv")
    if len(summary_rows) != 1:
        raise ValueError(f"expected one score summary row in {score_path}")
    row = summary_rows[0]
    pos_mean = float(row["labeled_positive_mean"])
    neg_mean = float(row["labeled_negative_mean"])
    denom = max(1.0e-8, pos_mean - neg_mean)
    mass = sum(
        min(1.0, max(0.0, (float(rank_row["score"]) - neg_mean) / denom))
        for rank_row in ranking_rows
    )
    labeled_positive_min = float(row["labeled_positive_min"])
    count_ge_pos_min = sum(float(rank_row["score"]) >= labeled_positive_min for rank_row in ranking_rows)
    if mass >= 800.0 and count_ge_pos_min >= 400:
        branch = "stress_abstain"
        reason = "large estimated positive mass and large pos-min pool"
    elif mass >= 200.0 and count_ge_pos_min >= 80:
        branch = "soft_weighted"
        reason = "moderate broad positive mass / pos-min pool"
    else:
        branch = "hard_risk_union"
        reason = "low-mass Can-like contamination"
    return RouterDecision(
        branch=branch,
        reason=reason,
        estimated_positive_mass=mass,
        count_ge_pos_min=int(count_ge_pos_min),
        labeled_positive_min=labeled_positive_min,
        labeled_positive_p10=float(row["labeled_positive_p10"]),
        labeled_positive_mean=pos_mean,
        labeled_negative_mean=neg_mean,
    )


def rank_fusion(first_ranked: list[str], second_ranked: list[str], *, count: int, second_weight: float = 0.5) -> list[str]:
    first_rank = {demo_id: rank for rank, demo_id in enumerate(first_ranked, start=1)}
    second_rank = {demo_id: rank for rank, demo_id in enumerate(second_ranked, start=1)}
    candidates = set(first_rank) & set(second_rank)
    first_den = max(1, len(first_ranked) - 1)
    second_den = max(1, len(second_ranked) - 1)

    def score(demo_id: str) -> tuple[float, int]:
        first_score = 1.0 - (first_rank[demo_id] - 1) / first_den
        second_score = 1.0 - (second_rank[demo_id] - 1) / second_den
        fused = (1.0 - second_weight) * first_score + second_weight * second_score
        return fused, -second_rank[demo_id]

    return sorted(candidates, key=score, reverse=True)[:count]


def risk_ranked(split: dict, path: Path) -> list[str]:
    risks = split_risk_scores(path)
    return sorted(
        split["unlabeled_ids"],
        key=lambda demo_id: (
            risks[demo_id]["action_conflict_risk"] + risks[demo_id]["bad_neighbor_risk"],
            risks[demo_id]["positive_distance_risk"],
            demo_sort_key(demo_id),
        ),
    )


def hard_union_ids(split: dict, path: Path, top_k: int) -> tuple[list[str], list[str], list[str]]:
    positive_ranked = [row["demo_id"] for row in positive_nn_demo_ranking(split)]
    risk_safe_ranked = risk_ranked(split, path)
    positive_top = positive_ranked[:top_k]
    fusion_top = rank_fusion(positive_ranked, risk_safe_ranked, count=top_k, second_weight=0.5)
    union = ordered_unique([*positive_top, *fusion_top])
    return positive_top, fusion_top, union


def score_mean(score_rows: list[dict[str, str]], demo_ids: list[str]) -> float:
    by_demo = {row["demo_id"]: float(row["score"]) for row in score_rows}
    values = [by_demo[demo_id] for demo_id in demo_ids if demo_id in by_demo]
    if not values:
        return float("nan")
    return float(np.mean(values))


def summarize_selection(
    *,
    task: str,
    split_seed: int,
    split: dict,
    source: Path,
    score_rows: list[dict[str, str]],
    decision: RouterDecision,
    candidate_id: str,
    branch: str,
    selected_ids: list[str],
) -> dict[str, object]:
    positives = set(split["all_positive_ids"])
    unlabeled = set(split["unlabeled_ids"])
    selected = len(selected_ids)
    hidden_positive = sum(demo_id in positives for demo_id in selected_ids)
    hidden_bad = selected - hidden_positive
    total_positive = sum(demo_id in positives for demo_id in unlabeled)
    total_bad = len(unlabeled) - total_positive
    return {
        "setting_id": task,
        "setting_label": TASKS[task]["setting_label"],
        "row_role": TASKS[task]["row_role"],
        "split_seed": split_seed,
        "router_branch": decision.branch,
        "router_reason": decision.reason,
        "estimated_positive_mass": decision.estimated_positive_mass,
        "count_ge_pos_min": decision.count_ge_pos_min,
        "labeled_positive_min": decision.labeled_positive_min,
        "labeled_positive_p10": decision.labeled_positive_p10,
        "labeled_positive_mean": decision.labeled_positive_mean,
        "labeled_negative_mean": decision.labeled_negative_mean,
        "candidate_id": candidate_id,
        "candidate_branch": branch,
        "selected_unlabeled": selected,
        "hidden_positive_selected": hidden_positive,
        "hidden_bad_selected": hidden_bad,
        "total_hidden_positive": total_positive,
        "total_hidden_bad": total_bad,
        "support_purity": hidden_positive / selected if selected else 0.0,
        "hidden_positive_recall": hidden_positive / total_positive if total_positive else 0.0,
        "hidden_bad_admission": hidden_bad / total_bad if total_bad else 0.0,
        "selected_contamination": hidden_bad / selected if selected else 0.0,
        "classifier_score_mean": score_mean(score_rows, selected_ids),
        "selected_demo_ids": ";".join(selected_ids),
        "source": str(source),
    }


def per_split_rows(root: Path, tasks: list[str], split_seeds: list[int]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for task in tasks:
        top_k = int(TASKS[task]["top_k"])
        for seed in split_seeds:
            path = split_path(root, task, seed)
            scores = score_dir(root, task, seed)
            if not path.exists() or not (scores / "demo_rankings.csv").exists():
                raise FileNotFoundError(
                    f"missing split or score diagnostics for {task} split {seed}: "
                    f"{path}, {scores}"
                )
            split = json.loads(path.read_text(encoding="utf-8"))
            score_rows = read_csv(scores / "demo_rankings.csv")
            decision = router_decision(scores)
            if decision.branch == "hard_risk_union":
                positive_top, fusion_top, union = hard_union_ids(split, path, top_k)
                rows.append(
                    summarize_selection(
                        task=task,
                        split_seed=seed,
                        split=split,
                        source=path,
                        score_rows=score_rows,
                        decision=decision,
                        candidate_id=f"positive_nn_top{top_k}",
                        branch="positive_only_component",
                        selected_ids=positive_top,
                    )
                )
                rows.append(
                    summarize_selection(
                        task=task,
                        split_seed=seed,
                        split=split,
                        source=path,
                        score_rows=score_rows,
                        decision=decision,
                        candidate_id=f"positive_nn_risk_fusion_top{top_k}",
                        branch="risk_fusion_component",
                        selected_ids=fusion_top,
                    )
                )
                rows.append(
                    summarize_selection(
                        task=task,
                        split_seed=seed,
                        split=split,
                        source=path,
                        score_rows=score_rows,
                        decision=decision,
                        candidate_id=f"positive_nn_risk_union_top{top_k}",
                        branch="hard_risk_union",
                        selected_ids=union,
                    )
                )
            elif decision.branch == "soft_weighted":
                rows.append(
                    summarize_selection(
                        task=task,
                        split_seed=seed,
                        split=split,
                        source=path,
                        score_rows=score_rows,
                        decision=decision,
                        candidate_id="weighted_bc",
                        branch="soft_weighted",
                        selected_ids=list(split["unlabeled_ids"]),
                    )
                )
            else:
                rows.append(
                    summarize_selection(
                        task=task,
                        split_seed=seed,
                        split=split,
                        source=path,
                        score_rows=score_rows,
                        decision=decision,
                        candidate_id="stress_abstain",
                        branch="stress_abstain",
                        selected_ids=[],
                    )
                )
    return rows


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["setting_id"]), str(row["candidate_id"]))].append(row)
    out = []
    for (_setting, _candidate), group in grouped.items():
        first = group[0]
        selected = sum(int(row["selected_unlabeled"]) for row in group)
        hidden_positive = sum(int(row["hidden_positive_selected"]) for row in group)
        hidden_bad = sum(int(row["hidden_bad_selected"]) for row in group)
        total_positive = sum(int(row["total_hidden_positive"]) for row in group)
        total_bad = sum(int(row["total_hidden_bad"]) for row in group)
        score_values = [
            (float(row["classifier_score_mean"]), int(row["selected_unlabeled"]))
            for row in group
            if not math.isnan(float(row["classifier_score_mean"])) and int(row["selected_unlabeled"]) > 0
        ]
        score_weight = sum(weight for _value, weight in score_values)
        out.append(
            {
                "setting_id": first["setting_id"],
                "setting_label": first["setting_label"],
                "row_role": first["row_role"],
                "candidate_id": first["candidate_id"],
                "candidate_branch": first["candidate_branch"],
                "split_count": len(group),
                "selected_unlabeled": selected,
                "hidden_positive_selected": hidden_positive,
                "hidden_bad_selected": hidden_bad,
                "total_hidden_positive": total_positive,
                "total_hidden_bad": total_bad,
                "support_purity": hidden_positive / selected if selected else 0.0,
                "hidden_positive_recall": hidden_positive / total_positive if total_positive else 0.0,
                "hidden_bad_admission": hidden_bad / total_bad if total_bad else 0.0,
                "selected_contamination": hidden_bad / selected if selected else 0.0,
                "classifier_score_mean": (
                    sum(value * weight for value, weight in score_values) / score_weight
                    if score_weight
                    else float("nan")
                ),
                "audit_oracle_score": (
                    (hidden_positive / total_positive if total_positive else 0.0)
                    - (hidden_bad / total_bad if total_bad else 0.0)
                ),
            }
        )
    return sorted(out, key=lambda row: (str(row["setting_id"]), str(row["candidate_id"])))


def format_rows(rows: list[dict[str, object]], *, split: bool) -> list[dict[str, str]]:
    fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "candidate_id",
        "candidate_branch",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
    ]
    if split:
        fields.insert(3, "split_seed")
        fields.insert(4, "router_branch")
        fields.insert(5, "router_reason")
        fields.insert(6, "estimated_positive_mass")
        fields.insert(7, "count_ge_pos_min")
        fields.insert(8, "labeled_positive_p10")
    else:
        fields.insert(3, "split_count")
    numeric = [
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "classifier_score_mean",
    ]
    if not split:
        numeric.append("audit_oracle_score")
    out = []
    for row in rows:
        formatted: dict[str, str] = {field: str(row[field]) for field in fields}
        for field in numeric:
            formatted[field] = fmt(float(row[field]))
        if split:
            formatted["labeled_positive_min"] = fmt(float(row["labeled_positive_min"]))
            formatted["labeled_positive_mean"] = fmt(float(row["labeled_positive_mean"]))
            formatted["labeled_negative_mean"] = fmt(float(row["labeled_negative_mean"]))
            formatted["selected_demo_ids"] = str(row["selected_demo_ids"])
            formatted["source"] = str(row["source"])
        out.append(formatted)
    return out


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return lines


def write_report(path: Path, split_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    decision_rows = []
    seen = set()
    for row in split_rows:
        key = (row["setting_id"], row["split_seed"])
        if key in seen:
            continue
        seen.add(key)
        decision_rows.append(row)
    lines = [
        "# v0.2 Fresh Router Support Audit",
        "",
        "This is a support/router preflight for `METHOD_FREEZE_V02.md`.",
        "It uses fresh split and score artifacts only; hidden labels are audit-only.",
        "",
        "## Router Decisions",
        "",
        *markdown_table(
            decision_rows,
            [
                "setting_label",
                "split_seed",
                "router_branch",
                "estimated_positive_mass",
                "count_ge_pos_min",
                "labeled_positive_p10",
            ],
        ),
        "",
        "## Support Summary",
        "",
        *markdown_table(
            summary_rows,
            [
                "setting_label",
                "candidate_id",
                "split_count",
                "selected_unlabeled",
                "hidden_positive_selected",
                "hidden_bad_selected",
                "support_purity",
                "hidden_positive_recall",
                "hidden_bad_admission",
                "audit_oracle_score",
            ],
        ),
        "",
        "## Read",
        "",
        "- If Can fresh splits choose `hard_risk_union`, the corresponding union rows are ready for endpoint setup.",
        "- If Lift fresh splits choose `soft_weighted`, the existing weighted trainer is the v0.2 selected branch for that split.",
        "- This report is not endpoint evidence; it is the cheap preflight before 200-epoch GPU jobs.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    split_rows_raw = per_split_rows(args.root, args.tasks, args.split_seeds)
    summary_rows_raw = aggregate(split_rows_raw)
    split_rows = format_rows(split_rows_raw, split=True)
    summary_rows = format_rows(summary_rows_raw, split=False)
    out_dir = args.out_dir
    write_csv(
        out_dir / "v02_fresh_router_support_per_split.csv",
        split_rows,
        list(split_rows[0]),
    )
    write_csv(
        out_dir / "v02_fresh_router_support_summary.csv",
        summary_rows,
        list(summary_rows[0]),
    )
    write_report(out_dir / "v02_fresh_router_support_REPORT.md", split_rows, summary_rows)
    print(f"wrote {out_dir / 'v02_fresh_router_support_per_split.csv'}")
    print(f"wrote {out_dir / 'v02_fresh_router_support_summary.csv'}")
    print(f"wrote {out_dir / 'v02_fresh_router_support_REPORT.md'}")


if __name__ == "__main__":
    main()
