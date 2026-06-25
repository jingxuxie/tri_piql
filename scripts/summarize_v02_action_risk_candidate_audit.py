from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from summarize_hybrid_candidate_support_audit import (
    SETTINGS,
    SPLIT_DIR,
    SETTING_ORDER,
    classifier_ranking,
    diagnostics_selected,
    positive_nn_demo_ranking,
)
from summarize_v02_action_risk_feature_screen import split_risk_scores


ROOT = Path(".")
TABLE_DIR = ROOT / "results" / "final_paper" / "tables"

PER_SPLIT_OUT = TABLE_DIR / "v02_action_risk_candidate_support_per_split.csv"
SUMMARY_OUT = TABLE_DIR / "v02_action_risk_candidate_support_summary.csv"
DECISION_OUT = TABLE_DIR / "v02_action_risk_candidate_support_decision.csv"
REPORT_OUT = TABLE_DIR / "v02_action_risk_candidate_support_REPORT.md"

BASELINES = {
    "can20": "positive_nn_top20",
    "can40": "positive_nn_top40",
    "can80": "positive_nn_top80",
    "lift_mg": "positive_nn_top160",
}


@dataclass(frozen=True)
class SplitContext:
    setting_id: str
    setting_label: str
    row_role: str
    split_seed: int
    split_path: Path
    unlabeled_ids: list[str]
    labels: dict[str, str]
    classifier_scores: dict[str, float]
    risk_scores: dict[str, dict[str, float]]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def fmt(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.3f}"


def as_int(value: object) -> int:
    return int(round(float(value)))


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
    first_den = max(1, len(first_ranked) - 1)
    second_den = max(1, len(second_ranked) - 1)

    def score(demo_id: str) -> tuple[float, int]:
        first_score = 1.0 - (first_rank[demo_id] - 1) / first_den
        second_score = 1.0 - (second_rank[demo_id] - 1) / second_den
        fused = (1.0 - second_weight) * first_score + second_weight * second_score
        return fused, -second_rank[demo_id]

    return sorted(candidates, key=score, reverse=True)[:count]


def candidate_family(candidate_id: str) -> str:
    if candidate_id.startswith(("action_safe", "bad_neighbor_safe", "combined_risk_safe", "safe_margin")):
        return "risk-only"
    if "risk" in candidate_id or candidate_id.startswith("triple_fusion"):
        return "risk-hybrid"
    if candidate_id.startswith("positive_nn"):
        return "positive-only"
    if candidate_id.startswith("classifier") or candidate_id == "triage_existing":
        return "bad-aware hard"
    return "risk-hybrid"


def risk_value(risk_scores: dict[str, dict[str, float]], demo_id: str) -> float:
    scores = risk_scores[demo_id]
    return float(scores["action_conflict_risk"]) + float(scores["bad_neighbor_risk"])


def build_context(setting, split_seed: int) -> tuple[SplitContext, list[str], list[str]]:
    split_path = SPLIT_DIR / f"{setting.split_key}_split{split_seed}" / "split_indices.json"
    split = json.loads(split_path.read_text(encoding="utf-8"))
    pos_ranked = [row["demo_id"] for row in positive_nn_demo_ranking(split)]
    classifier_ranked, classifier_scores, labels, _thresholds = classifier_ranking(setting, split_seed)
    risk_scores = split_risk_scores(split_path)
    context = SplitContext(
        setting_id=setting.setting_id,
        setting_label=setting.setting_label,
        row_role=setting.row_role,
        split_seed=split_seed,
        split_path=split_path,
        unlabeled_ids=list(split["unlabeled_ids"]),
        labels=labels,
        classifier_scores=classifier_scores,
        risk_scores=risk_scores,
    )
    return context, pos_ranked, classifier_ranked


def risk_rankings(context: SplitContext) -> dict[str, list[str]]:
    risk_scores = context.risk_scores
    unlabeled = list(context.unlabeled_ids)
    action_safe = sorted(
        unlabeled,
        key=lambda demo_id: (
            risk_scores[demo_id]["action_conflict_risk"],
            risk_scores[demo_id]["bad_neighbor_risk"],
            demo_sort_key(demo_id),
        ),
    )
    bad_neighbor_safe = sorted(
        unlabeled,
        key=lambda demo_id: (
            risk_scores[demo_id]["bad_neighbor_risk"],
            risk_scores[demo_id]["action_conflict_risk"],
            demo_sort_key(demo_id),
        ),
    )
    combined_safe = sorted(
        unlabeled,
        key=lambda demo_id: (
            risk_value(risk_scores, demo_id),
            risk_scores[demo_id]["positive_distance_risk"],
            demo_sort_key(demo_id),
        ),
    )
    safe_margin = sorted(
        unlabeled,
        key=lambda demo_id: (
            risk_scores[demo_id]["safe_margin_score"],
            -risk_value(risk_scores, demo_id),
            -demo_sort_key(demo_id),
        ),
        reverse=True,
    )
    return {
        "action": action_safe,
        "bad_neighbor": bad_neighbor_safe,
        "combined": combined_safe,
        "safe_margin": safe_margin,
    }


def risk_refine(pool: list[str], context: SplitContext, count: int) -> list[str]:
    return sorted(
        ordered_unique(pool),
        key=lambda demo_id: (
            risk_value(context.risk_scores, demo_id),
            context.risk_scores[demo_id]["bad_neighbor_risk"],
            demo_sort_key(demo_id),
        ),
    )[:count]


def candidate_sets(
    setting,
    context: SplitContext,
    pos_ranked: list[str],
    classifier_ranked: list[str],
) -> dict[str, list[str]]:
    rankings = risk_rankings(context)
    triage = diagnostics_selected(setting, context.split_seed, "triage_bc")
    candidates: dict[str, list[str]] = {
        "triage_existing": triage,
    }
    for topk in setting.topk_values:
        topk = min(topk, len(context.unlabeled_ids))
        pool_count = min(2 * topk, len(context.unlabeled_ids))
        candidates[f"positive_nn_top{topk}"] = pos_ranked[:topk]
        candidates[f"classifier_top{topk}"] = classifier_ranked[:topk]
        candidates[f"action_safe_top{topk}"] = rankings["action"][:topk]
        candidates[f"bad_neighbor_safe_top{topk}"] = rankings["bad_neighbor"][:topk]
        candidates[f"combined_risk_safe_top{topk}"] = rankings["combined"][:topk]
        candidates[f"safe_margin_top{topk}"] = rankings["safe_margin"][:topk]
        candidates[f"positive_nn_top{pool_count}_risk_refine_top{topk}"] = risk_refine(
            pos_ranked[:pool_count],
            context,
            topk,
        )
        candidates[f"classifier_top{pool_count}_risk_refine_top{topk}"] = risk_refine(
            classifier_ranked[:pool_count],
            context,
            topk,
        )
        candidates[f"positive_nn_risk_fusion_top{topk}"] = rank_fusion(
            pos_ranked,
            rankings["combined"],
            count=topk,
            second_weight=0.5,
        )
        candidates[f"classifier_risk_fusion_top{topk}"] = rank_fusion(
            classifier_ranked,
            rankings["combined"],
            count=topk,
            second_weight=0.5,
        )
        candidates[f"triple_fusion_top{topk}"] = rank_fusion(
            rank_fusion(pos_ranked, classifier_ranked, count=len(pos_ranked), second_weight=0.5),
            rankings["combined"],
            count=topk,
            second_weight=0.5,
        )
    return candidates


def summarize_candidate(
    context: SplitContext,
    candidate_id: str,
    demo_ids: list[str],
) -> dict[str, object]:
    demo_ids = ordered_unique(demo_ids)
    selected = len(demo_ids)
    hidden_positive = sum(1 for demo_id in demo_ids if context.labels[demo_id] == "positive")
    hidden_bad = selected - hidden_positive
    total_positive = sum(1 for label in context.labels.values() if label == "positive")
    total_bad = sum(1 for label in context.labels.values() if label != "positive")
    classifier_scores = [context.classifier_scores[demo_id] for demo_id in demo_ids]
    action_risks = [context.risk_scores[demo_id]["action_conflict_risk"] for demo_id in demo_ids]
    bad_neighbor_risks = [context.risk_scores[demo_id]["bad_neighbor_risk"] for demo_id in demo_ids]
    combined_risks = [risk_value(context.risk_scores, demo_id) for demo_id in demo_ids]
    safe_margins = [context.risk_scores[demo_id]["safe_margin_score"] for demo_id in demo_ids]
    return {
        "setting_id": context.setting_id,
        "setting_label": context.setting_label,
        "row_role": context.row_role,
        "split_seed": context.split_seed,
        "candidate_id": candidate_id,
        "candidate_family": candidate_family(candidate_id),
        "selected_unlabeled": selected,
        "hidden_positive_selected": hidden_positive,
        "hidden_bad_selected": hidden_bad,
        "total_hidden_positive": total_positive,
        "total_hidden_bad": total_bad,
        "support_purity": hidden_positive / selected if selected else 0.0,
        "hidden_positive_recall": hidden_positive / total_positive if total_positive else 0.0,
        "hidden_bad_admission": hidden_bad / total_bad if total_bad else 0.0,
        "selected_contamination": hidden_bad / selected if selected else 0.0,
        "classifier_score_mean": float(np.mean(classifier_scores)) if classifier_scores else float("nan"),
        "action_conflict_risk_mean": float(np.mean(action_risks)) if action_risks else float("nan"),
        "bad_neighbor_risk_mean": float(np.mean(bad_neighbor_risks)) if bad_neighbor_risks else float("nan"),
        "combined_risk_mean": float(np.mean(combined_risks)) if combined_risks else float("nan"),
        "safe_margin_score_mean": float(np.mean(safe_margins)) if safe_margins else float("nan"),
        "selected_demo_ids": ";".join(demo_ids),
        "source": str(context.split_path),
    }


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["setting_id"]), str(row["candidate_id"]))].append(row)

    out = []
    for (_setting_id, _candidate_id), group in grouped.items():
        first = group[0]
        selected = sum(as_int(row["selected_unlabeled"]) for row in group)
        hidden_positive = sum(as_int(row["hidden_positive_selected"]) for row in group)
        hidden_bad = sum(as_int(row["hidden_bad_selected"]) for row in group)
        total_positive = sum(as_int(row["total_hidden_positive"]) for row in group)
        total_bad = sum(as_int(row["total_hidden_bad"]) for row in group)

        def weighted(field: str) -> float:
            valid = [
                (float(row[field]), as_int(row["selected_unlabeled"]))
                for row in group
                if not math.isnan(float(row[field])) and as_int(row["selected_unlabeled"]) > 0
            ]
            if not valid:
                return float("nan")
            weight_sum = sum(weight for _value, weight in valid)
            return sum(value * weight for value, weight in valid) / weight_sum

        recall = hidden_positive / total_positive if total_positive else 0.0
        bad_admission = hidden_bad / total_bad if total_bad else 0.0
        out.append(
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
                "support_purity": hidden_positive / selected if selected else 0.0,
                "hidden_positive_recall": recall,
                "hidden_bad_admission": bad_admission,
                "selected_contamination": hidden_bad / selected if selected else 0.0,
                "classifier_score_mean": weighted("classifier_score_mean"),
                "action_conflict_risk_mean": weighted("action_conflict_risk_mean"),
                "bad_neighbor_risk_mean": weighted("bad_neighbor_risk_mean"),
                "combined_risk_mean": weighted("combined_risk_mean"),
                "safe_margin_score_mean": weighted("safe_margin_score_mean"),
                "audit_oracle_score": recall - bad_admission,
            }
        )

    family_order = {
        "positive-only": 0,
        "bad-aware hard": 1,
        "risk-only": 2,
        "risk-hybrid": 3,
    }
    return sorted(
        out,
        key=lambda row: (
            SETTING_ORDER.get(str(row["setting_id"]), 99),
            family_order.get(str(row["candidate_family"]), 9),
            str(row["candidate_id"]),
        ),
    )


def format_rows(rows: list[dict[str, object]], *, include_split_fields: bool) -> list[dict[str, str]]:
    shared = [
        "setting_id",
        "setting_label",
        "row_role",
        "candidate_id",
        "candidate_family",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
    ]
    if include_split_fields:
        shared.insert(3, "split_seed")
    else:
        shared.insert(3, "split_count")
    numeric = [
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "classifier_score_mean",
        "action_conflict_risk_mean",
        "bad_neighbor_risk_mean",
        "combined_risk_mean",
        "safe_margin_score_mean",
    ]
    if not include_split_fields:
        numeric.append("audit_oracle_score")
    out = []
    for row in rows:
        formatted = {field: str(row[field]) for field in shared}
        for field in numeric:
            formatted[field] = fmt(float(row[field]))
        if include_split_fields:
            formatted["selected_demo_ids"] = str(row["selected_demo_ids"])
            formatted["source"] = str(row["source"])
        out.append(formatted)
    return out


def decision_rows(summary_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    out = []
    by_setting: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in summary_rows:
        by_setting[str(row["setting_id"])].append(row)
    for setting_id, rows in sorted(
        by_setting.items(), key=lambda item: SETTING_ORDER.get(item[0], 99)
    ):
        baseline_id = BASELINES[setting_id]
        baseline = next(row for row in rows if row["candidate_id"] == baseline_id)
        best = max(
            rows,
            key=lambda row: (
                float(row["audit_oracle_score"]),
                float(row["hidden_positive_recall"]),
                -float(row["hidden_bad_admission"]),
                float(row["support_purity"]),
            ),
        )
        dominated = [
            row
            for row in rows
            if float(row["hidden_positive_recall"]) >= float(baseline["hidden_positive_recall"])
            and float(row["hidden_bad_admission"]) <= float(baseline["hidden_bad_admission"])
            and (
                float(row["hidden_positive_recall"]) > float(baseline["hidden_positive_recall"])
                or float(row["hidden_bad_admission"]) < float(baseline["hidden_bad_admission"])
            )
        ]
        risk_dominated = [row for row in dominated if str(row["candidate_family"]) in {"risk-only", "risk-hybrid"}]
        best_risk = max(
            [row for row in rows if str(row["candidate_family"]) in {"risk-only", "risk-hybrid"}],
            key=lambda row: (
                float(row["audit_oracle_score"]),
                float(row["hidden_positive_recall"]),
                -float(row["hidden_bad_admission"]),
            ),
        )
        out.append(
            {
                "setting_id": setting_id,
                "setting_label": str(rows[0]["setting_label"]),
                "baseline_id": baseline_id,
                "baseline_recall": fmt(float(baseline["hidden_positive_recall"])),
                "baseline_bad_admission": fmt(float(baseline["hidden_bad_admission"])),
                "best_id": str(best["candidate_id"]),
                "best_family": str(best["candidate_family"]),
                "best_recall": fmt(float(best["hidden_positive_recall"])),
                "best_bad_admission": fmt(float(best["hidden_bad_admission"])),
                "best_audit_score": fmt(float(best["audit_oracle_score"])),
                "best_risk_id": str(best_risk["candidate_id"]),
                "best_risk_family": str(best_risk["candidate_family"]),
                "best_risk_recall": fmt(float(best_risk["hidden_positive_recall"])),
                "best_risk_bad_admission": fmt(float(best_risk["hidden_bad_admission"])),
                "best_risk_audit_score": fmt(float(best_risk["audit_oracle_score"])),
                "risk_candidates_dominate_baseline": str(len(risk_dominated) > 0).lower(),
                "risk_dominating_candidate_count": str(len(risk_dominated)),
            }
        )
    return out


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return lines


def report(summary_rows: list[dict[str, object]], decisions: list[dict[str, str]]) -> str:
    primary_candidates = [
        row
        for row in format_rows(summary_rows, include_split_fields=False)
        if row["setting_id"] in {"can40", "lift_mg"}
        and row["candidate_id"]
        in {
            "positive_nn_top40",
            "positive_nn_top160",
            "combined_risk_safe_top40",
            "combined_risk_safe_top160",
            "positive_nn_risk_fusion_top40",
            "positive_nn_risk_fusion_top160",
            "positive_nn_top80_risk_refine_top40",
            "positive_nn_top320_risk_refine_top160",
            "classifier_risk_fusion_top40",
            "classifier_risk_fusion_top160",
            "triple_fusion_top40",
            "triple_fusion_top160",
        }
    ]
    risk_dominate = sum(row["risk_candidates_dominate_baseline"] == "true" for row in decisions)
    lines = [
        "# v0.2 Action-Risk Candidate Support Audit",
        "",
        "Generated from final-paper split files without policy training.",
        "Unlike the feature screen, this audit directly constructs candidate supports from action-conflict and bad-neighbor risk rankings, then uses hidden labels only for support audit.",
        "",
        "## Decision Rows",
        "",
        *markdown_table(
            decisions,
            [
                "setting_label",
                "baseline_id",
                "baseline_recall",
                "baseline_bad_admission",
                "best_id",
                "best_family",
                "best_recall",
                "best_bad_admission",
                "best_risk_id",
                "best_risk_family",
                "best_risk_recall",
                "best_risk_bad_admission",
                "risk_candidates_dominate_baseline",
                "risk_dominating_candidate_count",
            ],
        ),
        "",
        "## Primary Candidate Rows",
        "",
        *markdown_table(
            primary_candidates,
            [
                "setting_label",
                "candidate_id",
                "candidate_family",
                "selected_unlabeled",
                "hidden_positive_recall",
                "hidden_bad_admission",
                "support_purity",
                "audit_oracle_score",
                "combined_risk_mean",
            ],
        ),
        "",
        "## Interpretation",
        "",
        f"- Risk-generated candidates strictly dominate the setting-specific positive-NN baseline in `{risk_dominate}/4` settings.",
        "- Use this only as a support gate. A candidate that clears support still needs endpoint training before it becomes a policy claim.",
        "- Endpoint results supersede this support audit: a support-clearing candidate can still fail if it shifts the policy-learning distribution.",
        "",
        "## Outputs",
        "",
        f"- `{PER_SPLIT_OUT}`",
        f"- `{SUMMARY_OUT}`",
        f"- `{DECISION_OUT}`",
        f"- `{REPORT_OUT}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    per_split_rows: list[dict[str, object]] = []
    for setting in SETTINGS:
        for split_seed in setting.split_seeds:
            context, pos_ranked, classifier_ranked = build_context(setting, split_seed)
            candidates = candidate_sets(setting, context, pos_ranked, classifier_ranked)
            for candidate_id, demo_ids in candidates.items():
                per_split_rows.append(summarize_candidate(context, candidate_id, demo_ids))

    per_split_rows.sort(
        key=lambda row: (
            SETTING_ORDER.get(str(row["setting_id"]), 99),
            int(row["split_seed"]),
            str(row["candidate_family"]),
            str(row["candidate_id"]),
        )
    )
    summary_rows = aggregate(per_split_rows)
    decisions = decision_rows(summary_rows)

    per_split = format_rows(per_split_rows, include_split_fields=True)
    summary = format_rows(summary_rows, include_split_fields=False)

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
        "action_conflict_risk_mean",
        "bad_neighbor_risk_mean",
        "combined_risk_mean",
        "safe_margin_score_mean",
        "selected_demo_ids",
        "source",
    ]
    summary_fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "split_count",
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
        "action_conflict_risk_mean",
        "bad_neighbor_risk_mean",
        "combined_risk_mean",
        "safe_margin_score_mean",
        "audit_oracle_score",
    ]
    decision_fields = [
        "setting_id",
        "setting_label",
        "baseline_id",
        "baseline_recall",
        "baseline_bad_admission",
        "best_id",
        "best_family",
        "best_recall",
        "best_bad_admission",
        "best_audit_score",
        "best_risk_id",
        "best_risk_family",
        "best_risk_recall",
        "best_risk_bad_admission",
        "best_risk_audit_score",
        "risk_candidates_dominate_baseline",
        "risk_dominating_candidate_count",
    ]

    write_csv(PER_SPLIT_OUT, per_split, per_split_fields)
    write_csv(SUMMARY_OUT, summary, summary_fields)
    write_csv(DECISION_OUT, decisions, decision_fields)
    REPORT_OUT.write_text(report(summary_rows, decisions), encoding="utf-8")
    print(f"wrote {PER_SPLIT_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {DECISION_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
