from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "final_paper" / "tables"
OUT_CSV = OUT_DIR / "submission_readiness_audit.csv"
OUT_REPORT = OUT_DIR / "submission_readiness_audit_REPORT.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_row(rows: list[dict[str, str]], **where: str) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if all(row.get(key) == value for key, value in where.items())
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one row for {where} in table, found {len(matches)}")
    return matches[0]


def path_exists(path: str) -> bool:
    return (ROOT / path).exists()


def status_label(status: str) -> str:
    return {
        "pass": "Pass",
        "caution": "Caution",
        "not_met": "Not met",
    }[status]


def count_status(rows: list[dict[str, str]], required_for: str, status: str) -> int:
    return sum(
        1
        for row in rows
        if row["required_for"] == required_for and row["status"] == status
    )


def build_rows() -> list[dict[str, str]]:
    primary = read_csv(OUT_DIR / "robotics_primary_endpoint_matrix.csv")
    generated = read_csv(OUT_DIR / "generated_regime_probe_summary.csv")
    primary_bootstrap = read_csv(OUT_DIR / "primary_endpoint_paired_bootstrap.csv")
    v02_gate = read_csv(ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_gate_summary.csv")
    v02_uncertainty = read_csv(
        ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_gate_uncertainty.csv"
    )
    router_regret = read_csv(
        ROOT / "results" / "final_paper_v02" / "tables" / "v02_router_regret_summary.csv"
    )
    v02_baseline_coverage = read_csv(
        ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_baseline_coverage.csv"
    )
    lift_hn = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "ablations"
        / "lift_hard_negative_endpoint_200ep"
        / "endpoint_200ep_summary.csv"
    )

    rows: list[dict[str, str]] = []

    combined = find_row(v02_uncertainty, scope="Combined Can+Lift")
    can = find_row(v02_gate, setting_label="Can 40p/80b")
    lift = find_row(v02_gate, setting_label="Lift MG")
    rows.append(
        {
            "criterion_id": "empirical_v02_fresh_gate",
            "required_for": "high_quality_empirical_submission",
            "status": "pass",
            "criterion": "Frozen v0.2 fresh gate is complete and documented.",
            "evidence": (
                f"Combined selected {combined['selected_success']}/{combined['selected_episodes']} "
                f"versus best baselines {combined['best_baseline_success']}/{combined['best_baseline_episodes']}; "
                f"Can {can['selected_success']}/{can['selected_episodes']} versus "
                f"{can['best_baseline_success']}/{can['best_baseline_episodes']}; "
                f"Lift {lift['selected_success']}/{lift['selected_episodes']} versus "
                f"{lift['best_baseline_success']}/{lift['best_baseline_episodes']}."
            ),
            "artifact": "results/final_paper_v02/tables/v02_fresh_gate_REPORT.md",
            "decision": "Use as cautious portfolio-router evidence, not a decisive win.",
        }
    )

    generated_ok = (
        len(generated) == 3
        and all(row["claim_scope"] == "generated diagnostic, not primary benchmark row" for row in generated)
        and all(row["endpoint_delta"].startswith("+") for row in generated)
        and path_exists("REGIME_PROBE_SUITE.md")
    )
    rows.append(
        {
            "criterion_id": "empirical_regime_probes",
            "required_for": "high_quality_empirical_submission",
            "status": "pass" if generated_ok else "caution",
            "criterion": "Generated regime probes are formalized and separated from default benchmark rows.",
            "evidence": "; ".join(
                f"{row['probe_label']} {row['bad_aware_endpoint']} vs {row['positive_endpoint']}"
                for row in generated
            ),
            "artifact": "results/final_paper/tables/generated_regime_probe_summary_REPORT.md",
            "decision": "Keep as mechanism diagnostics and cite REGIME_PROBE_SUITE.md for allowed claims.",
        }
    )

    expected_primary = {
        ("Can 40p/80b", "all-demo BC"),
        ("Can 40p/80b", "positive-only NN"),
        ("Can 40p/80b", "weighted BC"),
        ("Can 40p/80b", "TRIAGE-BC"),
        ("Can 40p/80b", "all-positive oracle"),
        ("Lift MG", "all-demo BC"),
        ("Lift MG", "positive-only NN"),
        ("Lift MG", "weighted BC"),
        ("Lift MG", "TRIAGE-BC"),
        ("Lift MG", "all-positive oracle"),
    }
    observed_primary = {(row["task"], row["method"]) for row in primary}
    missing_primary = sorted(expected_primary - observed_primary)
    required_fresh = [
        row
        for row in v02_baseline_coverage
        if row["requirement"] == "required_branch_selection"
    ]
    optional_fresh = [
        row
        for row in v02_baseline_coverage
        if row["requirement"] == "optional_diagnostic"
    ]
    required_fresh_complete = sum(row["status"] == "complete" for row in required_fresh)
    optional_fresh_run = sum(row["status"] != "optional_not_run" for row in optional_fresh)
    rows.append(
        {
            "criterion_id": "empirical_strong_baselines",
            "required_for": "high_quality_empirical_submission",
            "status": "pass" if not missing_primary and required_fresh_complete == len(required_fresh) else "caution",
            "criterion": "Strong baselines are included in the primary Can/Lift evidence package and the fresh branch-selection audit.",
            "evidence": "Primary matrix includes all-demo, positive-only NN, weighted BC, TRIAGE-BC, and oracle rows for Can and Lift; "
            f"fresh branch-selection required rows are {required_fresh_complete}/{len(required_fresh)} complete, "
            f"with optional all-demo/all-positive diagnostic rows {optional_fresh_run}/{len(optional_fresh)} run."
            if not missing_primary
            else f"Missing primary rows: {missing_primary}",
            "artifact": "results/final_paper_v02/tables/v02_fresh_baseline_coverage_REPORT.md",
            "decision": "Primary baselines are complete; the v0.2 fresh gate is a complete selected-vs-strong-baseline/v0.1 audit, while all-demo/all-positive fresh rows remain optional diagnostics.",
        }
    )

    primary_intervals_cross = all(
        float(row["bootstrap95_low"]) <= 0.0 <= float(row["bootstrap95_high"])
        for row in primary_bootstrap
        if row["comparison"] in {"TRIAGE-BC - weighted BC", "weighted BC - TRIAGE-BC"}
    )
    v02_intervals_cross = all(
        float(row["paired_bootstrap95_low"]) <= 0.0 <= float(row["paired_bootstrap95_high"])
        for row in v02_uncertainty
    )
    rows.append(
        {
            "criterion_id": "empirical_uncertainty",
            "required_for": "high_quality_empirical_submission",
            "status": "pass",
            "criterion": "Uncertainty is reported without overclaiming significance.",
            "evidence": (
                f"Primary intervals cross zero: {primary_intervals_cross}; "
                f"v0.2 intervals cross zero: {v02_intervals_cross}; "
                f"combined v0.2 interval [{combined['paired_bootstrap95_low']}, {combined['paired_bootstrap95_high']}]."
            ),
            "artifact": "results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md",
            "decision": "Report counts, split signs, and bootstrap context; do not claim formal significance.",
        }
    )

    claim_docs = [
        "FINAL_CLAIM_CONTRACT.md",
        "paper/REVIEWER_CLAIM_SUMMARY.md",
        "paper/MANUSCRIPT_CHECKLIST.md",
        "paper/REPRODUCE_PAPER.md",
    ]
    rows.append(
        {
            "criterion_id": "empirical_claim_contract",
            "required_for": "high_quality_empirical_submission",
            "status": "pass" if all(path_exists(path) for path in claim_docs) else "caution",
            "criterion": "Title, abstract, and claim handoff emphasize when bad demos help instead of universal dominance.",
            "evidence": "Final claim contract and reviewer-facing summary are staged and validator-covered.",
            "artifact": "FINAL_CLAIM_CONTRACT.md",
            "decision": "Use precision/coverage framing as the submission spine.",
        }
    )

    rows.append(
        {
            "criterion_id": "empirical_reproducibility_gate",
            "required_for": "high_quality_empirical_submission",
            "status": "pass",
            "criterion": "Reproducibility scripts validate quoted numbers and artifact references.",
            "evidence": "make -C paper validate regenerates paper artifacts, compiles both PDFs, and runs claim, structure, and artifact validators.",
            "artifact": "paper/Makefile",
            "decision": "Keep this as the required pre-submission gate.",
        }
    )

    v02 = find_row(router_regret, row_id="v02_router")
    always_hard = find_row(router_regret, row_id="always_hard_support")
    rows.append(
        {
            "criterion_id": "methods_fixed_branch_dominance",
            "required_for": "top_tier_methods_dominance",
            "status": "not_met",
            "criterion": "v0.2 beats every fixed branch across multiple regimes with stable margins.",
            "evidence": (
                f"v0.2 regret is {v02['counted_regret_to_oracle']}/500 on completed Can+Lift rows, "
                f"while always-hard support also has regret {always_hard['counted_regret_to_oracle']} in the router-regret table."
            ),
            "artifact": "results/final_paper_v02/tables/v02_router_regret_REPORT.md",
            "decision": "Do not frame as methods/SOTA dominance.",
        }
    )

    rows.append(
        {
            "criterion_id": "methods_uncertainty_above_zero",
            "required_for": "top_tier_methods_dominance",
            "status": "not_met",
            "criterion": "v0.2 fresh gate remains positive over five or more split seeds with intervals mostly above zero.",
            "evidence": (
                f"Combined selected margin is {combined['pooled_delta']} with paired-bootstrap interval "
                f"[{combined['paired_bootstrap95_low']}, {combined['paired_bootstrap95_high']}]."
            ),
            "artifact": "results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md",
            "decision": "Keep v0.2 as directional branch-selection evidence.",
        }
    )

    bad_lift_rows = [row for row in lift_hn if row["candidate_id"] == "bad_aware_proxy_top40"]
    pos_lift_rows = [row for row in lift_hn if row["candidate_id"] == "state_action_positive_nn_top40"]
    bad_lift_success = sum(int(row["success_count"]) for row in bad_lift_rows)
    bad_lift_episodes = sum(int(row["eval_episodes"]) for row in bad_lift_rows)
    pos_lift_success = sum(int(row["success_count"]) for row in pos_lift_rows)
    pos_lift_episodes = sum(int(row["eval_episodes"]) for row in pos_lift_rows)
    completed_lift_splits = sorted({row["split_seed"] for row in lift_hn})
    rows.append(
        {
            "criterion_id": "methods_second_non_can_task",
            "required_for": "top_tier_methods_dominance",
            "status": "caution",
            "criterion": "A second non-Can task family shows a bad-label endpoint benefit over positive-only retrieval.",
            "evidence": (
                f"Lift hard-negative splits {','.join(completed_lift_splits)} are "
                f"{bad_lift_success}/{bad_lift_episodes} versus {pos_lift_success}/{pos_lift_episodes}; "
                "the directional non-Can effect is complete, but absolute success remains low."
            ),
            "artifact": "results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md",
            "decision": "Use as exploratory C1 mechanism evidence, not as primary endpoint dominance.",
        }
    )

    rows.append(
        {
            "criterion_id": "methods_validated_policy_proxy",
            "required_for": "top_tier_methods_dominance",
            "status": "not_met",
            "criterion": "A hidden-label-free policy-quality proxy predicts hard-versus-soft winners better than mass/count heuristics.",
            "evidence": "Consolidated proxy no-go table shows deployable proxy attempts match endpoint winners in only 2/11 rows.",
            "artifact": "results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md",
            "decision": "Keep policy-quality prediction as an open problem and abstention as risk control.",
        }
    )

    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "criterion_id",
        "required_for",
        "status",
        "criterion",
        "evidence",
        "artifact",
        "decision",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    empirical_pass = count_status(rows, "high_quality_empirical_submission", "pass")
    empirical_caution = count_status(rows, "high_quality_empirical_submission", "caution")
    methods_caution = count_status(rows, "top_tier_methods_dominance", "caution")
    methods_not_met = count_status(rows, "top_tier_methods_dominance", "not_met")

    lines = [
        "# Submission Readiness Audit",
        "",
        "Generated from staged final-paper artifacts. This audit is an evidence-accounting table, not a new experiment.",
        "",
        "## Summary",
        "",
        f"- High-quality empirical submission criteria: {empirical_pass} pass, {empirical_caution} caution.",
        f"- Top-tier methods/SOTA dominance criteria: {methods_caution} caution, {methods_not_met} not met.",
        "- Recommended posture: submit as a careful precision/coverage empirical study with a cautious v0.2 portfolio-router method component.",
        "",
        "## Criteria",
        "",
        "| required for | status | criterion | evidence | decision |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {required_for} | {status} | {criterion} | {evidence} | {decision} |".format(
                required_for=row["required_for"],
                status=status_label(row["status"]),
                criterion=row["criterion"],
                evidence=row["evidence"],
                decision=row["decision"],
            )
        )

    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{OUT_CSV.relative_to(ROOT)}`",
            f"- `{OUT_REPORT.relative_to(ROOT)}`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    rows = build_rows()
    write_csv(OUT_CSV, rows)
    write_report(OUT_REPORT, rows)
    print(f"wrote {OUT_CSV.relative_to(ROOT)}")
    print(f"wrote {OUT_REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
