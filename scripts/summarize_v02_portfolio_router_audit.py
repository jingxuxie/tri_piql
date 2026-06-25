from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(".")
TABLE_DIR = ROOT / "results" / "final_paper" / "tables"
ABLATION_DIR = ROOT / "results" / "final_paper" / "ablations"

ROUTER_FEATURES = ROOT / "results" / "robomimic_router_v2_abstention_summary" / "router_v2_summary.csv"
CAN40_UNION_ENDPOINT = ABLATION_DIR / "v02_union_endpoint_200ep_can40" / "endpoint_200ep_3split_summary.csv"
CAN40_V01_ENDPOINT = TABLE_DIR / "can_paired_pos40_bad80_final_endpoint_summary.csv"
LIFT_ENDPOINT = TABLE_DIR / "lift_mg_mg_sparse_final_endpoint_summary.csv"
CAN_MG_PROXY = ABLATION_DIR / "can_mg_branch_proxy_summary" / "method_proxy_scores.csv"
UNION_SUPPORT = TABLE_DIR / "v02_union_candidate_support_summary.csv"

DECISIONS_OUT = TABLE_DIR / "v02_portfolio_router_decisions.csv"
SUMMARY_OUT = TABLE_DIR / "v02_portfolio_router_summary.csv"
REPORT_OUT = TABLE_DIR / "v02_portfolio_router_REPORT.md"

AMBIGUOUS_MASS = 800.0
AMBIGUOUS_POS_MIN_COUNT = 400.0
COVERAGE_MASS = 200.0
COVERAGE_POS_MIN_COUNT = 80.0


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


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def as_float(value: str) -> float:
    return float(value) if value else 0.0


def as_int(value: str) -> int:
    return int(round(float(value))) if value else 0


def rate(successes: int | None, episodes: int | None) -> str:
    if successes is None or episodes in (None, 0):
        return ""
    return fmt(successes / episodes)


def method_row(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    for row in rows:
        if row[key] == value:
            return row
    raise KeyError(f"missing {key}={value}")


def final_summary_row(rows: list[dict[str, str]], method: str) -> dict[str, str]:
    return method_row(rows, "method", method)


def aggregate_can40_row(rows: list[dict[str, str]]) -> dict[str, str]:
    return method_row(rows, "split_seed", "aggregate")


def branch_for_features(row: dict[str, str]) -> tuple[str, str]:
    mass = as_float(row["estimated_positive_mass"])
    count = as_float(row["count_ge_pos_min"])
    if mass >= AMBIGUOUS_MASS and count >= AMBIGUOUS_POS_MIN_COUNT:
        return (
            "stress_abstain",
            "large calibrated mass and large pos-min pool indicate ambiguous MG-style coverage/contamination",
        )
    if mass >= COVERAGE_MASS and count >= COVERAGE_POS_MIN_COUNT:
        return (
            "soft_weighted",
            "moderate broad positive mass indicates a coverage-sensitive branch",
        )
    return (
        "hard_risk_union",
        "low calibrated mass indicates Can-like contamination; prefer positive-NN/risk union hard support",
    )


def can40_evidence() -> dict[str, object]:
    union = method_row(read_csv(CAN40_UNION_ENDPOINT), "method_id", "positive_nn_risk_union_top40")
    v01 = aggregate_can40_row(read_csv(CAN40_V01_ENDPOINT))
    return {
        "selected_method": "positive_nn_risk_union_top40",
        "endpoint_successes": as_int(union["success_count"]),
        "endpoint_episodes": as_int(union["eval_episodes"]),
        "comparator_method": "positive_only_nn_top40",
        "comparator_successes": as_int(v01["positive_only_nn_successes"]),
        "comparator_episodes": as_int(v01["eval_episodes"]),
        "v01_method": "triage_bc",
        "v01_successes": as_int(v01["triage_successes"]),
        "v01_episodes": as_int(v01["eval_episodes"]),
        "oracle_successes": as_int(v01["all_positive_oracle_successes"]),
        "oracle_episodes": as_int(v01["eval_episodes"]),
        "evidence_status": "complete_primary_development_endpoint",
        "evidence_source": f"{CAN40_UNION_ENDPOINT}; {CAN40_V01_ENDPOINT}",
        "note": "post-hoc development branch; loses split 11 to positive-only NN",
    }


def lift_evidence() -> dict[str, object]:
    rows = read_csv(LIFT_ENDPOINT)
    weighted = final_summary_row(rows, "weighted BC")
    triage = final_summary_row(rows, "TRIAGE-BC / pos-min")
    oracle = final_summary_row(rows, "all-positive oracle")
    return {
        "selected_method": "weighted_bc",
        "endpoint_successes": as_int(weighted["pooled_successes"]),
        "endpoint_episodes": as_int(weighted["pooled_episodes"]),
        "comparator_method": "weighted_bc",
        "comparator_successes": as_int(weighted["pooled_successes"]),
        "comparator_episodes": as_int(weighted["pooled_episodes"]),
        "v01_method": "triage_bc_pos_min",
        "v01_successes": as_int(triage["pooled_successes"]),
        "v01_episodes": as_int(triage["pooled_episodes"]),
        "oracle_successes": as_int(oracle["pooled_successes"]),
        "oracle_episodes": as_int(oracle["pooled_episodes"]),
        "evidence_status": "complete_primary_development_endpoint",
        "evidence_source": str(LIFT_ENDPOINT),
        "note": "matches strongest baseline by selecting weighted branch; not a bad-label policy win",
    }


def can_mg_evidence(analysis: str) -> dict[str, object]:
    split = "can_mg_original" if analysis == "can_mg_sparse" else "can_mg_shuffle42"
    rows = [row for row in read_csv(CAN_MG_PROXY) if row["split"] == split]
    best = max(rows, key=lambda row: as_float(row["rollout_success_20k"]))
    return {
        "selected_method": "abstain",
        "endpoint_successes": None,
        "endpoint_episodes": None,
        "comparator_method": best["method"],
        "comparator_successes": None,
        "comparator_episodes": None,
        "v01_method": "",
        "v01_successes": None,
        "v01_episodes": None,
        "oracle_successes": None,
        "oracle_episodes": None,
        "evidence_status": "stress_abstained",
        "evidence_source": str(CAN_MG_PROXY),
        "note": f"abstains; best observed stress branch is {best['method']} at {float(best['rollout_success_20k']):.3f}",
    }


def support_only_evidence(analysis: str, branch: str) -> dict[str, object]:
    setting_map = {
        "can_paired_20p80b": "can20",
        "can_paired_80p80b": "can80",
    }
    note = "no endpoint for selected portfolio branch"
    if analysis in setting_map and UNION_SUPPORT.exists():
        setting_id = setting_map[analysis]
        rows = [
            row for row in read_csv(UNION_SUPPORT)
            if row["setting_id"] == setting_id and "union" in row["candidate_id"]
        ]
        if rows:
            row = rows[0]
            note = (
                f"support-only union audit: {row['hidden_positive_selected']}/"
                f"{row['total_hidden_positive']} hidden positives and "
                f"{row['hidden_bad_selected']}/{row['total_hidden_bad']} hidden bad selected"
            )
    return {
        "selected_method": branch,
        "endpoint_successes": None,
        "endpoint_episodes": None,
        "comparator_method": "",
        "comparator_successes": None,
        "comparator_episodes": None,
        "v01_method": "",
        "v01_successes": None,
        "v01_episodes": None,
        "oracle_successes": None,
        "oracle_episodes": None,
        "evidence_status": "needs_endpoint",
        "evidence_source": str(UNION_SUPPORT),
        "note": note,
    }


def evidence_for(analysis: str, branch: str) -> dict[str, object]:
    if analysis == "can_paired_40p80b":
        return can40_evidence()
    if analysis == "lift_mg_sparse":
        return lift_evidence()
    if analysis in {"can_mg_sparse", "can_mg_sparse_shuffle42"}:
        return can_mg_evidence(analysis)
    return support_only_evidence(analysis, branch)


def decision_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for feature_row in read_csv(ROUTER_FEATURES):
        branch, reason = branch_for_features(feature_row)
        evidence = evidence_for(feature_row["analysis"], branch)
        successes = evidence["endpoint_successes"]
        episodes = evidence["endpoint_episodes"]
        comparator_successes = evidence["comparator_successes"]
        comparator_episodes = evidence["comparator_episodes"]
        v01_successes = evidence["v01_successes"]
        v01_episodes = evidence["v01_episodes"]
        rows.append(
            {
                "analysis": feature_row["analysis"],
                "observed_mode": feature_row["observed_mode"],
                "estimated_positive_mass": feature_row["estimated_positive_mass"],
                "count_ge_pos_min": feature_row["count_ge_pos_min"],
                "labeled_positive_p10": feature_row["labeled_positive_p10"],
                "portfolio_branch": branch,
                "portfolio_reason": reason,
                "selected_method": evidence["selected_method"],
                "endpoint_successes": "" if successes is None else successes,
                "endpoint_episodes": "" if episodes is None else episodes,
                "endpoint_success_rate": rate(successes, episodes),
                "comparator_method": evidence["comparator_method"],
                "comparator_successes": "" if comparator_successes is None else comparator_successes,
                "comparator_episodes": "" if comparator_episodes is None else comparator_episodes,
                "comparator_success_rate": rate(comparator_successes, comparator_episodes),
                "v01_method": evidence["v01_method"],
                "v01_successes": "" if v01_successes is None else v01_successes,
                "v01_episodes": "" if v01_episodes is None else v01_episodes,
                "v01_success_rate": rate(v01_successes, v01_episodes),
                "oracle_successes": "" if evidence["oracle_successes"] is None else evidence["oracle_successes"],
                "oracle_episodes": "" if evidence["oracle_episodes"] is None else evidence["oracle_episodes"],
                "oracle_success_rate": rate(evidence["oracle_successes"], evidence["oracle_episodes"]),
                "evidence_status": evidence["evidence_status"],
                "evidence_source": evidence["evidence_source"],
                "note": evidence["note"],
            }
        )
    return rows


def summary_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    primary = [
        row for row in rows
        if row["analysis"] in {"can_paired_40p80b", "lift_mg_sparse"}
        and row["evidence_status"] == "complete_primary_development_endpoint"
    ]
    successes = sum(as_int(str(row["endpoint_successes"])) for row in primary)
    episodes = sum(as_int(str(row["endpoint_episodes"])) for row in primary)
    comparator_successes = sum(as_int(str(row["comparator_successes"])) for row in primary)
    comparator_episodes = sum(as_int(str(row["comparator_episodes"])) for row in primary)
    v01_successes = sum(as_int(str(row["v01_successes"])) for row in primary)
    v01_episodes = sum(as_int(str(row["v01_episodes"])) for row in primary)
    oracle_successes = sum(as_int(str(row["oracle_successes"])) for row in primary)
    oracle_episodes = sum(as_int(str(row["oracle_episodes"])) for row in primary)
    complete = [row for row in rows if row["evidence_status"] == "complete_primary_development_endpoint"]
    needs = [row for row in rows if row["evidence_status"] == "needs_endpoint"]
    abstained = [row for row in rows if row["evidence_status"] == "stress_abstained"]
    return [
        {
            "quantity": "primary_portfolio_success",
            "value": f"{successes}/{episodes}",
            "rate": rate(successes, episodes),
        },
        {
            "quantity": "primary_strongest_baseline_matched_success",
            "value": f"{comparator_successes}/{comparator_episodes}",
            "rate": rate(comparator_successes, comparator_episodes),
        },
        {
            "quantity": "primary_v01_success",
            "value": f"{v01_successes}/{v01_episodes}",
            "rate": rate(v01_successes, v01_episodes),
        },
        {
            "quantity": "primary_all_positive_oracle_success",
            "value": f"{oracle_successes}/{oracle_episodes}",
            "rate": rate(oracle_successes, oracle_episodes),
        },
        {
            "quantity": "complete_primary_development_endpoint_rows",
            "value": str(len(complete)),
            "rate": "",
        },
        {
            "quantity": "needs_endpoint_rows",
            "value": str(len(needs)),
            "rate": "",
        },
        {
            "quantity": "stress_abstained_rows",
            "value": str(len(abstained)),
            "rate": "",
        },
    ]


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def write_report(rows: list[dict[str, object]], summary: list[dict[str, object]]) -> None:
    primary = [row for row in rows if row["analysis"] in {"can_paired_40p80b", "lift_mg_sparse"}]
    rows_for_display = [
        row for row in rows
        if row["analysis"] in {
            "can_paired_40p80b",
            "lift_mg_sparse",
            "can_mg_sparse",
            "can_paired_20p80b",
            "can_paired_80p80b",
        }
    ]
    lines = [
        "# v0.2 Portfolio Router Audit",
        "",
        "This is a development audit for a hidden-label-free portfolio router after the Can 40 union endpoint gate.",
        "The rule uses only router features from labeled score calibration and the unlabeled score distribution.",
        "Hidden labels and endpoints are used only for audit.",
        "",
        "## Rule",
        "",
        f"- Abstain if estimated positive mass is at least `{AMBIGUOUS_MASS:.0f}` and the count above the labeled-positive minimum is at least `{AMBIGUOUS_POS_MIN_COUNT:.0f}`.",
        f"- Otherwise choose the soft weighted branch if estimated positive mass is at least `{COVERAGE_MASS:.0f}` and count above the labeled-positive minimum is at least `{COVERAGE_POS_MIN_COUNT:.0f}`.",
        "- Otherwise choose the hard positive-NN/risk union branch.",
        "",
        "## Primary Development Rows",
        "",
        *markdown_table(
            primary,
            [
                "analysis",
                "portfolio_branch",
                "selected_method",
                "endpoint_success_rate",
                "comparator_method",
                "comparator_success_rate",
                "v01_success_rate",
                "note",
            ],
        ),
        "",
        "## Summary",
        "",
        *markdown_table(summary, ["quantity", "value", "rate"]),
        "",
        "## Broader Decisions",
        "",
        *markdown_table(
            rows_for_display,
            [
                "analysis",
                "estimated_positive_mass",
                "count_ge_pos_min",
                "portfolio_branch",
                "selected_method",
                "endpoint_success_rate",
                "evidence_status",
                "note",
            ],
        ),
        "",
        "## Read",
        "",
        "- The portfolio clears a development endpoint screen on the two primary rows: Can 40 uses the union branch and Lift uses weighted BC.",
        "- Pooled primary development success is `209/300` (`0.697`), versus the strongest pre-union per-task baselines at `201/300` (`0.670`) and v0.1 at `173/300` (`0.577`).",
        "- This is still not a publishable v0.2 result: the rule was written after seeing the Can union endpoint, Lift is won by a baseline branch, Can 20/80 union rows lack endpoints, and fresh split validation is missing.",
        "- The next GPU budget should be a frozen fresh-split test of this router, not additional tuning on split seeds 11/22/33.",
        "",
        "## Outputs",
        "",
        f"- `{DECISIONS_OUT}`",
        f"- `{SUMMARY_OUT}`",
        f"- `{REPORT_OUT}`",
        "",
    ]
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    rows = decision_rows()
    summary = summary_rows(rows)
    decision_fields = [
        "analysis",
        "observed_mode",
        "estimated_positive_mass",
        "count_ge_pos_min",
        "labeled_positive_p10",
        "portfolio_branch",
        "portfolio_reason",
        "selected_method",
        "endpoint_successes",
        "endpoint_episodes",
        "endpoint_success_rate",
        "comparator_method",
        "comparator_successes",
        "comparator_episodes",
        "comparator_success_rate",
        "v01_method",
        "v01_successes",
        "v01_episodes",
        "v01_success_rate",
        "oracle_successes",
        "oracle_episodes",
        "oracle_success_rate",
        "evidence_status",
        "evidence_source",
        "note",
    ]
    summary_fields = ["quantity", "value", "rate"]
    write_csv(DECISIONS_OUT, rows, decision_fields)
    write_csv(SUMMARY_OUT, summary, summary_fields)
    write_report(rows, summary)
    print(f"wrote {DECISIONS_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
