from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(".")
TABLE_DIR = ROOT / "results" / "final_paper" / "tables"
PER_SPLIT = TABLE_DIR / "hybrid_candidate_support_per_split.csv"

SUMMARY_OUT = TABLE_DIR / "v02_proxy_feature_screen.csv"
WINNERS_OUT = TABLE_DIR / "v02_proxy_feature_screen_winners.csv"
REPORT_OUT = TABLE_DIR / "v02_proxy_feature_screen_REPORT.md"

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
    ("coverage_classifier_hmean", "coverage/classifier harmonic"),
    ("coverage_minus_half_risk", "coverage - 0.5 risk"),
    ("coverage_minus_one_risk", "coverage - 1.0 risk"),
    ("coverage_minus_two_risk", "coverage - 2.0 risk"),
]


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


def as_int(value: str) -> int:
    return int(round(float(value)))


def fmt(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.3f}"


def aggregate_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row["setting_id"],
            row["setting_label"],
            row["candidate_id"],
            row["candidate_family"],
        )
        grouped[key].append(row)

    out: list[dict[str, object]] = []
    for (setting_id, setting_label, candidate_id, candidate_family), split_rows in grouped.items():
        selected = sum(as_int(row["selected_unlabeled"]) for row in split_rows)
        hidden_positive = sum(as_int(row["hidden_positive_selected"]) for row in split_rows)
        hidden_bad = sum(as_int(row["hidden_bad_selected"]) for row in split_rows)
        total_positive = sum(as_int(row["total_hidden_positive"]) for row in split_rows)
        total_bad = sum(as_int(row["total_hidden_bad"]) for row in split_rows)
        classifier_scores = [
            float(row["classifier_score_mean"])
            for row in split_rows
            if row["classifier_score_mean"] != ""
        ]
        classifier_score_mean = (
            sum(classifier_scores) / len(classifier_scores) if classifier_scores else float("nan")
        )
        hidden_positive_recall = hidden_positive / total_positive if total_positive else 0.0
        hidden_bad_admission = hidden_bad / total_bad if total_bad else 0.0
        support_purity = hidden_positive / selected if selected else 0.0
        selected_contamination = hidden_bad / selected if selected else 0.0
        coverage_fraction = selected / (total_positive + total_bad) if total_positive + total_bad else 0.0
        audit_oracle_score = hidden_positive_recall - hidden_bad_admission
        out.append(
            {
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
                "classifier_score_mean": classifier_score_mean,
                "audit_oracle_score": audit_oracle_score,
            }
        )
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
        scores = [float(row["classifier_score_mean"]) for row in setting_rows]
        lo = min(scores)
        hi = max(scores)
        for row in setting_rows:
            if hi > lo:
                score_norm = (float(row["classifier_score_mean"]) - lo) / (hi - lo)
            else:
                score_norm = 0.0
            coverage = float(row["coverage_fraction"])
            row["classifier_score_norm"] = score_norm
            row["coverage_x_classifier"] = coverage * score_norm
            row["coverage_classifier_hmean"] = (
                2.0 * coverage * score_norm / (coverage + score_norm)
                if coverage + score_norm > 0.0
                else 0.0
            )
            row["coverage_minus_half_risk"] = coverage - 0.5 * (1.0 - score_norm)
            row["coverage_minus_one_risk"] = coverage - 1.0 * (1.0 - score_norm)
            row["coverage_minus_two_risk"] = coverage - 2.0 * (1.0 - score_norm)


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


def format_summary_rows(rows: list[dict[str, object]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        out.append(
            {
                "setting_id": str(row["setting_id"]),
                "setting_label": str(row["setting_label"]),
                "candidate_id": str(row["candidate_id"]),
                "candidate_label": display_candidate(row["candidate_id"]),
                "candidate_family": str(row["candidate_family"]),
                "split_count": str(row["split_count"]),
                "selected_unlabeled": str(row["selected_unlabeled"]),
                "hidden_positive_selected": str(row["hidden_positive_selected"]),
                "hidden_bad_selected": str(row["hidden_bad_selected"]),
                "support_purity": fmt(float(row["support_purity"])),
                "hidden_positive_recall": fmt(float(row["hidden_positive_recall"])),
                "hidden_bad_admission": fmt(float(row["hidden_bad_admission"])),
                "selected_contamination": fmt(float(row["selected_contamination"])),
                "coverage_fraction": fmt(float(row["coverage_fraction"])),
                "classifier_score_mean": fmt(float(row["classifier_score_mean"])),
                "classifier_score_norm": fmt(float(row["classifier_score_norm"])),
                "coverage_x_classifier": fmt(float(row["coverage_x_classifier"])),
                "coverage_classifier_hmean": fmt(float(row["coverage_classifier_hmean"])),
                "coverage_minus_half_risk": fmt(float(row["coverage_minus_half_risk"])),
                "coverage_minus_one_risk": fmt(float(row["coverage_minus_one_risk"])),
                "coverage_minus_two_risk": fmt(float(row["coverage_minus_two_risk"])),
                "audit_oracle_score": fmt(float(row["audit_oracle_score"])),
            }
        )
    return out


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
        for proxy_key, proxy_label in PROXY_COLUMNS:
            winner = max(setting_rows, key=lambda row: float(row[proxy_key]))
            audit_winner = max(setting_rows, key=lambda row: float(row["audit_oracle_score"]))
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
                    "audit_winner_id": str(audit_winner["candidate_id"]),
                    "audit_winner_label": display_candidate(audit_winner["candidate_id"]),
                    "matches_audit_winner": str(winner["candidate_id"] == audit_winner["candidate_id"]).lower(),
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
    compact_winners = [
        row
        for row in winners
        if row["proxy"]
        in {
            "audit_oracle_score",
            "coverage_fraction",
            "classifier_score_norm",
            "coverage_x_classifier",
            "coverage_classifier_hmean",
        }
    ]
    risk_proxy_rows = [row for row in winners if row["proxy"] != "audit_oracle_score"]
    matches = sum(row["matches_audit_winner"] == "true" for row in risk_proxy_rows)
    dominates = sum(row["dominates_positive_nn_baseline"] == "true" for row in risk_proxy_rows)
    setting_count = len({row["setting_id"] for row in winners})
    proxy_count = len({row["proxy"] for row in risk_proxy_rows})

    baseline_rows = [
        row
        for row in summary
        if row["candidate_id"] in set(BASELINES.values())
    ]
    lines = [
        "# v0.2 Proxy Feature Screen",
        "",
        "This is a support-side screen over the existing hybrid candidate audit.",
        "It uses hidden labels only for audit columns; candidate selection scores use selected support size and classifier-score means.",
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
                "classifier_score_mean",
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
        "## Interpretation",
        "",
        f"- Across `{setting_count}` settings and `{proxy_count}` deployable proxy formulas, proxy winners match the audit-support winner in `{matches}/{setting_count * proxy_count}` setting-proxy cases.",
        f"- Proxy winners strictly dominate the positive-NN baseline on hidden support metrics in `{dominates}/{setting_count * proxy_count}` setting-proxy cases.",
        "- Coverage-only proxies over-select broad supports; classifier-only proxies under-cover. Simple coverage/classifier combinations do not reliably recover the audit frontier.",
        "- The best support-audit rows are setting-specific: positive-NN top40 on Can 40p/80b, a small fill hybrid on Can 20p/80b, an intersection hybrid on Can 80p/80b, and classifier top320 on Lift MG.",
        "- This does not justify endpoint training a new branch yet. The next v0.2 feature should explicitly estimate action-conflict or bad-neighbor risk, not just mean classifier score.",
        "",
        "## Outputs",
        "",
        f"- `{SUMMARY_OUT}`",
        f"- `{WINNERS_OUT}`",
        f"- `{REPORT_OUT}`",
    ]
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    raw_rows = read_csv(PER_SPLIT)
    rows = aggregate_rows(raw_rows)
    add_proxy_scores(rows)
    summary = format_summary_rows(rows)
    winners = winner_rows(rows)

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
        "classifier_score_norm",
        "coverage_x_classifier",
        "coverage_classifier_hmean",
        "coverage_minus_half_risk",
        "coverage_minus_one_risk",
        "coverage_minus_two_risk",
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
        "audit_winner_id",
        "audit_winner_label",
        "matches_audit_winner",
        "baseline_id",
        "dominates_positive_nn_baseline",
    ]
    write_csv(SUMMARY_OUT, summary, summary_fields)
    write_csv(WINNERS_OUT, winners, winner_fields)
    write_report(summary, winners)
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {WINNERS_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
