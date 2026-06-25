from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from summarize_hard_negative_can_action_conflict_audit import (
    dataset_obs_keys,
    load_demo_features,
    min_l2_to,
    stack_features,
    zscore,
)


ROOT = Path(".")
TABLE_DIR = ROOT / "results" / "final_paper" / "tables"
PER_SPLIT = TABLE_DIR / "hybrid_candidate_support_per_split.csv"

PER_SPLIT_OUT = TABLE_DIR / "v02_action_risk_feature_screen_per_split.csv"
SUMMARY_OUT = TABLE_DIR / "v02_action_risk_feature_screen.csv"
WINNERS_OUT = TABLE_DIR / "v02_action_risk_feature_screen_winners.csv"
REPORT_OUT = TABLE_DIR / "v02_action_risk_feature_screen_REPORT.md"

BASELINES = {
    "can20": "positive_nn_top20",
    "can40": "positive_nn_top40",
    "can80": "positive_nn_top80",
    "lift_mg": "positive_nn_top160",
}

SETTING_ORDER = {
    "can40": 0,
    "lift_mg": 1,
    "can20": 2,
    "can80": 3,
}

PROXY_COLUMNS = [
    ("audit_oracle_score", "audit oracle"),
    ("coverage_fraction", "coverage only"),
    ("classifier_score_norm", "classifier score only"),
    ("coverage_x_classifier", "coverage x classifier"),
    ("coverage_minus_action_risk", "coverage - action risk"),
    ("coverage_minus_bad_neighbor_risk", "coverage - bad-neighbor risk"),
    ("coverage_classifier_minus_action_risk", "coverage + classifier - action risk"),
    ("coverage_classifier_minus_bad_neighbor_risk", "coverage + classifier - bad-neighbor risk"),
    ("coverage_classifier_minus_both_risks", "coverage + classifier - both risks"),
]

DEPLOYABLE_PROXY_KEYS = [key for key, _label in PROXY_COLUMNS if key != "audit_oracle_score"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sorted_demos(demo_ids: list[str]) -> list[str]:
    return sorted(demo_ids, key=lambda demo_id: int(demo_id.split("_")[-1]))


def ordered_unique(demo_ids: list[str]) -> list[str]:
    return list(dict.fromkeys(demo_ids))


def parse_demo_ids(value: str) -> list[str]:
    if not value:
        return []
    return [item for item in value.split(";") if item]


def as_int(value: str) -> int:
    return int(round(float(value)))


def fmt(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.3f}"


def mean(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(np.mean(np.asarray(values, dtype=np.float64)))


def weighted_mean(values: list[tuple[float, int]]) -> float:
    valid = [(value, weight) for value, weight in values if not math.isnan(value) and weight > 0]
    if not valid:
        return float("nan")
    total_weight = sum(weight for _value, weight in valid)
    return sum(value * weight for value, weight in valid) / total_weight


def minmax(values: list[float], *, higher_is_risk: bool) -> list[float]:
    valid = [value for value in values if not math.isnan(value)]
    if not valid:
        return [1.0 if higher_is_risk else 0.0 for _value in values]
    filler = max(valid) if higher_is_risk else min(valid)
    filled = [value if not math.isnan(value) else filler for value in values]
    lo = min(filled)
    hi = max(filled)
    if hi <= lo:
        return [0.0 for _value in filled]
    return [(value - lo) / (hi - lo) for value in filled]


def split_risk_scores(split_path: Path) -> dict[str, dict[str, float]]:
    split = json.loads(split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    support_ids = sorted_demos(
        ordered_unique(
            [
                *split["labeled_positive_ids"],
                *split["labeled_negative_ids"],
                *split["unlabeled_ids"],
            ]
        )
    )
    features = load_demo_features(hdf5_path, support_ids, obs_keys)

    unlabeled = list(split["unlabeled_ids"])
    labeled_positive = list(split["labeled_positive_ids"])
    labeled_negative = list(split["labeled_negative_ids"])

    unl_state = stack_features(features.state, unlabeled)
    unl_action = stack_features(features.action, unlabeled)
    unl_state_action = stack_features(features.state_action, unlabeled)
    pos_state = stack_features(features.state, labeled_positive)
    pos_action = stack_features(features.action, labeled_positive)
    pos_state_action = stack_features(features.state_action, labeled_positive)
    neg_state_action = stack_features(features.state_action, labeled_negative)

    pos_state_dist, nearest_positive = min_l2_to(unl_state, pos_state)
    nearest_positive_action = pos_action[nearest_positive]
    action_conflict = np.sqrt(np.sum((unl_action - nearest_positive_action) ** 2, axis=1))
    pos_state_action_dist, _ = min_l2_to(unl_state_action, pos_state_action)
    neg_state_action_dist, _ = min_l2_to(unl_state_action, neg_state_action)

    action_conflict_risk = zscore(-pos_state_dist) + zscore(action_conflict)
    bad_neighbor_risk = zscore(pos_state_action_dist - neg_state_action_dist)
    positive_distance_risk = zscore(pos_state_action_dist)
    negative_neighbor_risk = zscore(-neg_state_action_dist)
    safe_margin_score = zscore(neg_state_action_dist - pos_state_action_dist)

    out: dict[str, dict[str, float]] = {}
    for idx, demo_id in enumerate(unlabeled):
        out[demo_id] = {
            "pos_state_distance": float(pos_state_dist[idx]),
            "action_conflict_distance": float(action_conflict[idx]),
            "pos_state_action_distance": float(pos_state_action_dist[idx]),
            "neg_state_action_distance": float(neg_state_action_dist[idx]),
            "action_conflict_risk": float(action_conflict_risk[idx]),
            "bad_neighbor_risk": float(bad_neighbor_risk[idx]),
            "positive_distance_risk": float(positive_distance_risk[idx]),
            "negative_neighbor_risk": float(negative_neighbor_risk[idx]),
            "safe_margin_score": float(safe_margin_score[idx]),
        }
    return out


def add_candidate_features(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    cache: dict[str, dict[str, dict[str, float]]] = {}
    out: list[dict[str, object]] = []
    feature_keys = [
        "pos_state_distance",
        "action_conflict_distance",
        "pos_state_action_distance",
        "neg_state_action_distance",
        "action_conflict_risk",
        "bad_neighbor_risk",
        "positive_distance_risk",
        "negative_neighbor_risk",
        "safe_margin_score",
    ]
    for row in rows:
        source = row["source"]
        if source not in cache:
            cache[source] = split_risk_scores(Path(source))
        selected_demo_ids = parse_demo_ids(row["selected_demo_ids"])
        selected_scores = [cache[source][demo_id] for demo_id in selected_demo_ids if demo_id in cache[source]]
        enriched: dict[str, object] = dict(row)
        for key in feature_keys:
            enriched[key] = mean([scores[key] for scores in selected_scores])
        out.append(enriched)
    return out


def aggregate_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[
            (
                str(row["setting_id"]),
                str(row["setting_label"]),
                str(row["candidate_id"]),
                str(row["candidate_family"]),
            )
        ].append(row)

    feature_keys = [
        "pos_state_distance",
        "action_conflict_distance",
        "pos_state_action_distance",
        "neg_state_action_distance",
        "action_conflict_risk",
        "bad_neighbor_risk",
        "positive_distance_risk",
        "negative_neighbor_risk",
        "safe_margin_score",
    ]

    out: list[dict[str, object]] = []
    for (setting_id, setting_label, candidate_id, candidate_family), split_rows in grouped.items():
        selected = sum(as_int(str(row["selected_unlabeled"])) for row in split_rows)
        hidden_positive = sum(as_int(str(row["hidden_positive_selected"])) for row in split_rows)
        hidden_bad = sum(as_int(str(row["hidden_bad_selected"])) for row in split_rows)
        total_positive = sum(as_int(str(row["total_hidden_positive"])) for row in split_rows)
        total_bad = sum(as_int(str(row["total_hidden_bad"])) for row in split_rows)
        classifier_scores = [
            float(row["classifier_score_mean"])
            for row in split_rows
            if str(row["classifier_score_mean"]) != ""
        ]
        hidden_positive_recall = hidden_positive / total_positive if total_positive else 0.0
        hidden_bad_admission = hidden_bad / total_bad if total_bad else 0.0
        support_purity = hidden_positive / selected if selected else 0.0
        selected_contamination = hidden_bad / selected if selected else 0.0
        coverage_fraction = selected / (total_positive + total_bad) if total_positive + total_bad else 0.0

        aggregate: dict[str, object] = {
            "setting_id": setting_id,
            "setting_label": setting_label,
            "candidate_id": candidate_id,
            "candidate_family": candidate_family,
            "split_count": len(split_rows),
            "selected_unlabeled": selected,
            "hidden_positive_selected": hidden_positive,
            "hidden_bad_selected": hidden_bad,
            "total_hidden_positive": total_positive,
            "total_hidden_bad": total_bad,
            "support_purity": support_purity,
            "hidden_positive_recall": hidden_positive_recall,
            "hidden_bad_admission": hidden_bad_admission,
            "selected_contamination": selected_contamination,
            "coverage_fraction": coverage_fraction,
            "classifier_score_mean": mean(classifier_scores),
            "audit_oracle_score": hidden_positive_recall - hidden_bad_admission,
        }
        for key in feature_keys:
            aggregate[key] = weighted_mean(
                [
                    (
                        float(row[key]),
                        as_int(str(row["selected_unlabeled"])),
                    )
                    for row in split_rows
                ]
            )
        out.append(aggregate)

    return sorted(
        out,
        key=lambda row: (
            SETTING_ORDER.get(str(row["setting_id"]), 99),
            str(row["candidate_family"]),
            str(row["candidate_id"]),
        ),
    )


def add_proxy_scores(rows: list[dict[str, object]]) -> None:
    by_setting: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_setting[str(row["setting_id"])].append(row)

    for setting_rows in by_setting.values():
        classifier_norm = minmax(
            [float(row["classifier_score_mean"]) for row in setting_rows],
            higher_is_risk=False,
        )
        action_risk_norm = minmax(
            [float(row["action_conflict_risk"]) for row in setting_rows],
            higher_is_risk=True,
        )
        bad_neighbor_risk_norm = minmax(
            [float(row["bad_neighbor_risk"]) for row in setting_rows],
            higher_is_risk=True,
        )
        positive_distance_risk_norm = minmax(
            [float(row["positive_distance_risk"]) for row in setting_rows],
            higher_is_risk=True,
        )
        safe_margin_norm = minmax(
            [float(row["safe_margin_score"]) for row in setting_rows],
            higher_is_risk=False,
        )

        for idx, row in enumerate(setting_rows):
            coverage = float(row["coverage_fraction"])
            classifier = classifier_norm[idx]
            action_risk = action_risk_norm[idx]
            bad_risk = bad_neighbor_risk_norm[idx]
            pos_dist_risk = positive_distance_risk_norm[idx]
            safe_margin = safe_margin_norm[idx]
            combined_risk = 0.5 * (action_risk + bad_risk)

            row["classifier_score_norm"] = classifier
            row["action_conflict_risk_norm"] = action_risk
            row["bad_neighbor_risk_norm"] = bad_risk
            row["positive_distance_risk_norm"] = pos_dist_risk
            row["safe_margin_score_norm"] = safe_margin
            row["coverage_x_classifier"] = coverage * classifier
            row["coverage_minus_action_risk"] = coverage - action_risk
            row["coverage_minus_bad_neighbor_risk"] = coverage - bad_risk
            row["coverage_classifier_minus_action_risk"] = coverage + classifier - action_risk
            row["coverage_classifier_minus_bad_neighbor_risk"] = coverage + classifier - bad_risk
            row["coverage_classifier_minus_both_risks"] = coverage + classifier - combined_risk


def display_candidate(candidate_id: object) -> str:
    text = str(candidate_id)
    labels = {
        "positive_nn_top20": "positive-NN top20",
        "positive_nn_top40": "positive-NN top40",
        "positive_nn_top80": "positive-NN top80",
        "positive_nn_top160": "positive-NN top160",
        "triage_existing": "TRIAGE-BC current",
        "classifier_top20": "classifier top20",
        "classifier_top40": "classifier top40",
        "classifier_top80": "classifier top80",
        "classifier_top160": "classifier top160",
        "classifier_top320": "classifier top320",
        "classifier_top480": "classifier top480",
    }
    return labels.get(text, text.replace("_", " "))


def format_per_split_rows(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    fields = [
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
        "source",
    ]
    feature_fields = [
        "pos_state_distance",
        "action_conflict_distance",
        "pos_state_action_distance",
        "neg_state_action_distance",
        "action_conflict_risk",
        "bad_neighbor_risk",
        "positive_distance_risk",
        "negative_neighbor_risk",
        "safe_margin_score",
    ]
    out = []
    for row in rows:
        formatted = {field: str(row[field]) for field in fields}
        for field in feature_fields:
            formatted[field] = fmt(float(row[field]))
        out.append(formatted)
    return out


def format_summary_rows(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    numeric_fields = [
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "coverage_fraction",
        "classifier_score_mean",
        "pos_state_distance",
        "action_conflict_distance",
        "pos_state_action_distance",
        "neg_state_action_distance",
        "action_conflict_risk",
        "bad_neighbor_risk",
        "positive_distance_risk",
        "negative_neighbor_risk",
        "safe_margin_score",
        "classifier_score_norm",
        "action_conflict_risk_norm",
        "bad_neighbor_risk_norm",
        "positive_distance_risk_norm",
        "safe_margin_score_norm",
        "coverage_x_classifier",
        "coverage_minus_action_risk",
        "coverage_minus_bad_neighbor_risk",
        "coverage_classifier_minus_action_risk",
        "coverage_classifier_minus_bad_neighbor_risk",
        "coverage_classifier_minus_both_risks",
        "audit_oracle_score",
    ]
    out = []
    for row in rows:
        formatted = {
            "setting_id": str(row["setting_id"]),
            "setting_label": str(row["setting_label"]),
            "candidate_id": str(row["candidate_id"]),
            "candidate_label": display_candidate(row["candidate_id"]),
            "candidate_family": str(row["candidate_family"]),
            "split_count": str(row["split_count"]),
            "selected_unlabeled": str(row["selected_unlabeled"]),
            "hidden_positive_selected": str(row["hidden_positive_selected"]),
            "hidden_bad_selected": str(row["hidden_bad_selected"]),
        }
        for field in numeric_fields:
            formatted[field] = fmt(float(row[field]))
        out.append(formatted)
    return out


def best_audit_row(rows: list[dict[str, object]]) -> dict[str, object]:
    return max(
        rows,
        key=lambda row: (
            float(row["audit_oracle_score"]),
            float(row["hidden_positive_recall"]),
            -float(row["hidden_bad_admission"]),
            float(row["support_purity"]),
            -int(row["selected_unlabeled"]),
            str(row["candidate_id"]),
        ),
    )


def proxy_winner(rows: list[dict[str, object]], proxy_key: str) -> dict[str, object]:
    return max(
        rows,
        key=lambda row: (
            float(row[proxy_key]),
            float(row["audit_oracle_score"]),
            float(row["hidden_positive_recall"]),
            -float(row["hidden_bad_admission"]),
            str(row["candidate_id"]),
        ),
    )


def winner_rows(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    by_setting: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_setting[str(row["setting_id"])].append(row)

    out: list[dict[str, str]] = []
    for setting_id, setting_rows in sorted(
        by_setting.items(), key=lambda item: SETTING_ORDER.get(item[0], 99)
    ):
        baseline_id = BASELINES.get(setting_id)
        baseline = next((row for row in setting_rows if row["candidate_id"] == baseline_id), None)
        audit_winner = best_audit_row(setting_rows)
        best_audit_score = float(audit_winner["audit_oracle_score"])
        for proxy_key, proxy_label in PROXY_COLUMNS:
            winner = proxy_winner(setting_rows, proxy_key)
            matches_audit = abs(float(winner["audit_oracle_score"]) - best_audit_score) < 0.0005
            dominates_baseline = ""
            if baseline is not None:
                dominates_baseline = str(
                    float(winner["hidden_positive_recall"]) >= float(baseline["hidden_positive_recall"])
                    and float(winner["hidden_bad_admission"]) <= float(baseline["hidden_bad_admission"])
                    and (
                        float(winner["hidden_positive_recall"]) > float(baseline["hidden_positive_recall"])
                        or float(winner["hidden_bad_admission"]) < float(baseline["hidden_bad_admission"])
                    )
                ).lower()
            out.append(
                {
                    "setting_id": setting_id,
                    "setting_label": str(setting_rows[0]["setting_label"]),
                    "proxy": proxy_key,
                    "proxy_label": proxy_label,
                    "winner_id": str(winner["candidate_id"]),
                    "winner_label": display_candidate(winner["candidate_id"]),
                    "winner_selected": str(winner["selected_unlabeled"]),
                    "winner_recall": fmt(float(winner["hidden_positive_recall"])),
                    "winner_bad_admission": fmt(float(winner["hidden_bad_admission"])),
                    "winner_audit_score": fmt(float(winner["audit_oracle_score"])),
                    "winner_action_risk": fmt(float(winner["action_conflict_risk_norm"])),
                    "winner_bad_neighbor_risk": fmt(float(winner["bad_neighbor_risk_norm"])),
                    "audit_winner_id": str(audit_winner["candidate_id"]),
                    "audit_winner_label": display_candidate(audit_winner["candidate_id"]),
                    "matches_audit_winner": str(matches_audit).lower(),
                    "baseline_id": baseline_id or "",
                    "dominates_positive_nn_baseline": dominates_baseline,
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


def write_report(summary: list[dict[str, str]], winners: list[dict[str, str]]) -> None:
    deployable_winners = [row for row in winners if row["proxy"] in DEPLOYABLE_PROXY_KEYS]
    matches = sum(row["matches_audit_winner"] == "true" for row in deployable_winners)
    dominates = sum(row["dominates_positive_nn_baseline"] == "true" for row in deployable_winners)
    setting_count = len({row["setting_id"] for row in winners})
    proxy_count = len(DEPLOYABLE_PROXY_KEYS)

    compact_proxy_names = {
        "audit_oracle_score",
        "coverage_fraction",
        "classifier_score_norm",
        "coverage_minus_action_risk",
        "coverage_minus_bad_neighbor_risk",
        "coverage_classifier_minus_both_risks",
    }
    compact_winners = [row for row in winners if row["proxy"] in compact_proxy_names]
    baseline_rows = [
        row
        for row in summary
        if BASELINES.get(row["setting_id"]) == row["candidate_id"]
    ]
    action_risk_probe = [
        row
        for row in summary
        if row["candidate_id"]
        in {
            "positive_nn_top40",
            "positive_nn_top160",
            "classifier_top40",
            "classifier_top160",
            "classifier_top320",
            "triage_existing",
        }
        and row["setting_id"] in {"can40", "lift_mg"}
    ]

    lines = [
        "# v0.2 Action-Risk Feature Screen",
        "",
        "This is a support-side screen over the existing hybrid candidate audit.",
        "It uses labeled-positive and labeled-negative demos to compute hidden-label-free action-conflict and bad-neighbor risk features for each unlabeled demo.",
        "Hidden labels are used only for audit columns and winner checks.",
        "",
        "## Baseline Positive-NN Rows",
        "",
        *markdown_table(
            baseline_rows,
            [
                "setting_label",
                "candidate_label",
                "selected_unlabeled",
                "hidden_positive_recall",
                "hidden_bad_admission",
                "audit_oracle_score",
                "action_conflict_risk_norm",
                "bad_neighbor_risk_norm",
            ],
        ),
        "",
        "## Proxy Winners",
        "",
        *markdown_table(
            compact_winners,
            [
                "setting_label",
                "proxy_label",
                "winner_label",
                "winner_selected",
                "winner_recall",
                "winner_bad_admission",
                "winner_audit_score",
                "matches_audit_winner",
                "dominates_positive_nn_baseline",
            ],
        ),
        "",
        "## Primary Risk Probe Rows",
        "",
        *markdown_table(
            action_risk_probe,
            [
                "setting_label",
                "candidate_label",
                "selected_unlabeled",
                "hidden_positive_recall",
                "hidden_bad_admission",
                "action_conflict_risk_norm",
                "bad_neighbor_risk_norm",
                "audit_oracle_score",
            ],
        ),
        "",
        "## Interpretation",
        "",
        f"- Across `{setting_count}` settings and `{proxy_count}` deployable action-risk proxy formulas, proxy winners match the audit-support winner in `{matches}/{setting_count * proxy_count}` setting-proxy cases.",
        f"- Proxy winners strictly dominate the positive-NN baseline on hidden support metrics in `{dominates}/{setting_count * proxy_count}` setting-proxy cases.",
        "- The action-conflict and bad-neighbor features are useful diagnostics, but they still do not produce a reliable hidden-label-free selector over the current candidate family.",
        "- Treat this as another no-go for endpoint training a new v0.2 branch from the existing support candidates. The next useful step is to create candidates that optimize these risks directly, or freeze an abstention/router story instead of proxy-selecting among stale candidates.",
        "",
        "## Outputs",
        "",
        f"- `{PER_SPLIT_OUT}`",
        f"- `{SUMMARY_OUT}`",
        f"- `{WINNERS_OUT}`",
        f"- `{REPORT_OUT}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    raw_rows = read_csv(PER_SPLIT)
    per_split_rows = add_candidate_features(raw_rows)
    summary_rows = aggregate_rows(per_split_rows)
    add_proxy_scores(summary_rows)

    per_split = format_per_split_rows(per_split_rows)
    summary = format_summary_rows(summary_rows)
    winners = winner_rows(summary_rows)

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
        "pos_state_distance",
        "action_conflict_distance",
        "pos_state_action_distance",
        "neg_state_action_distance",
        "action_conflict_risk",
        "bad_neighbor_risk",
        "positive_distance_risk",
        "negative_neighbor_risk",
        "safe_margin_score",
        "source",
    ]
    summary_fields = [
        "setting_id",
        "setting_label",
        "candidate_id",
        "candidate_label",
        "candidate_family",
        "split_count",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "coverage_fraction",
        "classifier_score_mean",
        "pos_state_distance",
        "action_conflict_distance",
        "pos_state_action_distance",
        "neg_state_action_distance",
        "action_conflict_risk",
        "bad_neighbor_risk",
        "positive_distance_risk",
        "negative_neighbor_risk",
        "safe_margin_score",
        "classifier_score_norm",
        "action_conflict_risk_norm",
        "bad_neighbor_risk_norm",
        "positive_distance_risk_norm",
        "safe_margin_score_norm",
        "coverage_x_classifier",
        "coverage_minus_action_risk",
        "coverage_minus_bad_neighbor_risk",
        "coverage_classifier_minus_action_risk",
        "coverage_classifier_minus_bad_neighbor_risk",
        "coverage_classifier_minus_both_risks",
        "audit_oracle_score",
    ]
    winner_fields = [
        "setting_id",
        "setting_label",
        "proxy",
        "proxy_label",
        "winner_id",
        "winner_label",
        "winner_selected",
        "winner_recall",
        "winner_bad_admission",
        "winner_audit_score",
        "winner_action_risk",
        "winner_bad_neighbor_risk",
        "audit_winner_id",
        "audit_winner_label",
        "matches_audit_winner",
        "baseline_id",
        "dominates_positive_nn_baseline",
    ]

    write_csv(PER_SPLIT_OUT, per_split, per_split_fields)
    write_csv(SUMMARY_OUT, summary, summary_fields)
    write_csv(WINNERS_OUT, winners, winner_fields)
    write_report(summary, winners)
    print(f"wrote {PER_SPLIT_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {WINNERS_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
