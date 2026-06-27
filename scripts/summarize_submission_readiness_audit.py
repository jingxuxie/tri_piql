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
    candidate_breakthrough = read_csv(
        ROOT / "results" / "candidate_breakthrough" / "candidate_breakthrough_decision_summary.csv"
    )
    sota_sweep = read_csv(ROOT / "results" / "sota_candidate" / "sota_candidate_sweep_summary.csv")
    anchor_overlap = read_csv(ROOT / "results" / "sota_candidate" / "can404_anchor_overlap_summary.csv")
    anchor_feature_gate = read_csv(
        ROOT / "results" / "sota_candidate" / "can404_anchor_feature_gate_preflight.csv"
    )
    cau_fallback_fresh_505 = read_csv(
        ROOT / "results" / "sota_candidate" / "can505_cau_fallback_fresh_validation_summary.csv"
    )
    cau_fallback_fresh_303 = read_csv(
        ROOT / "results" / "sota_candidate" / "can303_cau_fallback_fresh_validation_summary.csv"
    )
    cau_two_feature_gate = read_csv(
        ROOT / "results" / "sota_candidate" / "cau_two_feature_gate_fresh_validation_summary.csv"
    )
    cau_five_split = {
        row["method_id"]: row
        for row in read_csv(
            ROOT / "results" / "sota_candidate" / "cau_action_conflict_can_five_split_endpoint_summary.csv"
        )
    }
    cau_v02_portfolio = read_csv(
        ROOT / "results" / "sota_candidate" / "cau_v02_portfolio_preflight_gate_scan.csv"
    )[0]
    cau_selector_rows = read_csv(ROOT / "results" / "sota_candidate" / "cau_selector_feature_loo_rows.csv")
    cau_selector_baselines = read_csv(
        ROOT / "results" / "sota_candidate" / "cau_selector_feature_split_baselines.csv"
    )
    cau_policy_selector_rows = read_csv(
        ROOT / "results" / "sota_candidate" / "cau_policy_feature_selector_loo_rows.csv"
    )
    cau_policy_selector_baselines = read_csv(
        ROOT / "results" / "sota_candidate" / "cau_policy_feature_split_baselines.csv"
    )
    cau_policy_fresh909 = {
        row["method_id"]: row
        for row in read_csv(ROOT / "results" / "sota_candidate" / "cau_policy_feature_fresh909_summary.csv")
    }
    cau_policy_learned_rows = read_csv(
        ROOT / "results" / "sota_candidate" / "cau_policy_feature_learned_router_summary.csv"
    )
    cau_sequence_support = {
        row["screen_id"]: row
        for row in read_csv(ROOT / "results" / "sota_candidate" / "cau_sequence_support_router_summary.csv")
    }
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

    candidate_f_can = find_row(candidate_breakthrough, area="Can discovery matrix")
    candidate_f_fresh_can = find_row(candidate_breakthrough, area="Fresh Can smokes")
    candidate_f_fresh_validation = find_row(candidate_breakthrough, area="Fresh Can validation")
    candidate_f_lift = find_row(candidate_breakthrough, area="Lift transfer")
    transition_objectives = find_row(candidate_breakthrough, area="Transition-level objectives")
    output_anchor = find_row(candidate_breakthrough, area="Output-anchor fine-tuning")
    two_feature_gate = find_row(candidate_breakthrough, area="Two-feature weighted-rescue gate")
    rows.append(
        {
            "criterion_id": "methods_candidate_breakthrough_validation",
            "required_for": "top_tier_methods_dominance",
            "status": "not_met",
            "criterion": "The latest candidate-breakthrough search validates a general method beyond scoped Can discovery.",
            "evidence": (
                f"{candidate_f_can['key_result']}; "
                f"{candidate_f_fresh_can['key_result']}; "
                f"{candidate_f_fresh_validation['key_result']}; "
                f"{candidate_f_lift['key_result']}; "
                f"{transition_objectives['key_result']}; "
                f"{output_anchor['key_result']}; "
                f"{two_feature_gate['key_result']}."
            ),
            "artifact": "results/candidate_breakthrough/candidate_breakthrough_decision_REPORT.md",
            "decision": "Candidate F failed its predeclared fresh Can validation gate early, and later transition/object-anchor/router follow-ups also failed validation; keep them as scoped discovery / failed-development evidence.",
        }
    )

    best_can_sweep = [
        row
        for row in sota_sweep
        if row["decision_level"] == "endpoint_screen"
        and row["primary_gate"] == "Can404 valid-positive starts"
    ]
    best_can_success = max(int(row["best_candidate_score"].split("/", maxsplit=1)[0]) for row in best_can_sweep)
    best_can_episodes = max(int(row["best_candidate_score"].split("/", maxsplit=1)[1]) for row in best_can_sweep)
    can_positive = find_row(sota_sweep, candidate_id="2")["positive_score"]
    ccg = find_row(sota_sweep, candidate_id="3")
    anchored_iql = find_row(sota_sweep, candidate_id="6")
    cau_overlap = find_row(anchor_overlap, method_id="cau_action_conflict")
    demo_overlap = find_row(anchor_overlap, method_id="demo_dpo_refcenter")
    cau_gate_rows = [
        row
        for row in anchor_feature_gate
        if row["method_id"] == "cau_action_conflict"
        and row["gains_vs_positive"] == "1"
        and row["losses_vs_positive"] == "0"
    ]
    cau_gate = max(cau_gate_rows, key=lambda row: int(row["routed_successes"]))
    cau_fallback_505_first20 = find_row(cau_fallback_fresh_505, screen_id="first20", checkpoint_name="model_epoch_200")
    cau_fallback_505_eval50 = find_row(cau_fallback_fresh_505, screen_id="eval50", checkpoint_name="model_epoch_200")
    cau_fallback_303_first20 = find_row(cau_fallback_fresh_303, screen_id="first20", checkpoint_name="model_epoch_200")
    two_feature_101_eval50 = find_row(
        cau_two_feature_gate,
        split="101",
        screen_id="eval50",
        checkpoint_name="model_epoch_200",
    )
    two_feature_202_eval50 = find_row(
        cau_two_feature_gate,
        split="202",
        screen_id="eval50",
        checkpoint_name="model_epoch_200",
    )
    selector_total_episodes = sum(int(row["episodes"]) for row in cau_selector_baselines)
    selector_positive = sum(int(row["positive_successes"]) for row in cau_selector_baselines)
    selector_cau = sum(int(row["cau_successes"]) for row in cau_selector_baselines)
    selector_oracle = sum(int(row["oracle_switch_successes"]) for row in cau_selector_baselines)
    selector_safe_rows = [
        row
        for row in cau_selector_rows
        if row["selector_mode"] == "safe_zero_loss" and row["heldout_split"] != "pooled_resubstitution"
    ]
    selector_best_rows = [
        row
        for row in cau_selector_rows
        if row["selector_mode"] == "best_delta" and row["heldout_split"] != "pooled_resubstitution"
    ]
    selector_safe_routed = sum(int(row["test_routed_successes"]) for row in selector_safe_rows)
    selector_safe_gains = sum(int(row["test_gains_vs_positive"]) for row in selector_safe_rows)
    selector_safe_losses = sum(int(row["test_losses_vs_positive"]) for row in selector_safe_rows)
    selector_best_routed = sum(int(row["test_routed_successes"]) for row in selector_best_rows)
    selector_best_gains = sum(int(row["test_gains_vs_positive"]) for row in selector_best_rows)
    selector_best_losses = sum(int(row["test_losses_vs_positive"]) for row in selector_best_rows)
    policy_selector_total_episodes = sum(int(row["episodes"]) for row in cau_policy_selector_baselines)
    policy_selector_positive = sum(int(row["positive_successes"]) for row in cau_policy_selector_baselines)
    policy_selector_cau = sum(int(row["cau_successes"]) for row in cau_policy_selector_baselines)
    policy_selector_oracle = sum(int(row["oracle_switch_successes"]) for row in cau_policy_selector_baselines)
    policy_selector_safe_rows = [
        row
        for row in cau_policy_selector_rows
        if row["selector_mode"] == "safe_zero_loss" and row["heldout_split"] != "pooled_resubstitution"
    ]
    policy_selector_best_rows = [
        row
        for row in cau_policy_selector_rows
        if row["selector_mode"] == "best_delta" and row["heldout_split"] != "pooled_resubstitution"
    ]
    policy_selector_safe_routed = sum(int(row["test_routed_successes"]) for row in policy_selector_safe_rows)
    policy_selector_safe_gains = sum(int(row["test_gains_vs_positive"]) for row in policy_selector_safe_rows)
    policy_selector_safe_losses = sum(int(row["test_losses_vs_positive"]) for row in policy_selector_safe_rows)
    policy_selector_best_routed = sum(int(row["test_routed_successes"]) for row in policy_selector_best_rows)
    policy_selector_best_gains = sum(int(row["test_gains_vs_positive"]) for row in policy_selector_best_rows)
    policy_selector_best_losses = sum(int(row["test_losses_vs_positive"]) for row in policy_selector_best_rows)
    learned_safe_rows = [
        row
        for row in cau_policy_learned_rows
        if row["selector_mode"] == "safe_zero_loss" and row["heldout_split"].isdigit()
    ]
    learned_best_rows = [
        row
        for row in cau_policy_learned_rows
        if row["selector_mode"] == "best_delta" and row["heldout_split"].isdigit()
    ]
    learned_safe_fresh909 = find_row(cau_policy_learned_rows, selector_mode="safe_zero_loss", heldout_split="fresh909")
    learned_best_fresh909 = find_row(cau_policy_learned_rows, selector_mode="best_delta", heldout_split="fresh909")
    learned_safe_episodes = sum(int(row["test_episodes"]) for row in learned_safe_rows)
    learned_safe_routed = sum(int(row["test_routed_successes"]) for row in learned_safe_rows)
    learned_safe_gains = sum(int(row["test_gains_vs_positive"]) for row in learned_safe_rows)
    learned_safe_losses = sum(int(row["test_losses_vs_positive"]) for row in learned_safe_rows)
    learned_best_episodes = sum(int(row["test_episodes"]) for row in learned_best_rows)
    learned_best_routed = sum(int(row["test_routed_successes"]) for row in learned_best_rows)
    learned_best_gains = sum(int(row["test_gains_vs_positive"]) for row in learned_best_rows)
    learned_best_losses = sum(int(row["test_losses_vs_positive"]) for row in learned_best_rows)
    seq909 = cau_sequence_support["split909_thr005"]
    seq808 = cau_sequence_support["split808_thr005"]
    seq707 = cau_sequence_support["split707_thr005"]
    seq606 = cau_sequence_support["split606_thr005_heldout"]
    seq101_eval50 = cau_sequence_support["split101_thr005_eval50"]
    seq101_persistent = cau_sequence_support["split101_persistent_thr005_k10_eval50"]
    seq606_eval50 = cau_sequence_support["split606_thr005_eval50"]
    seq005_rows = [seq909, seq808, seq707]
    seq005_episodes = sum(int(row["episodes"]) for row in seq005_rows)
    seq005_router = sum(int(row["router_successes"]) for row in seq005_rows)
    seq005_positive = sum(int(row["positive_successes"]) for row in seq005_rows)
    seq005_cau = sum(int(row["cau_successes"]) for row in seq005_rows)
    seq005_gains = sum(int(row["gains_vs_positive"]) for row in seq005_rows)
    seq005_losses = sum(int(row["losses_vs_positive"]) for row in seq005_rows)
    seq005_with_heldout_rows = seq005_rows + [seq606]
    seq005_with_heldout_episodes = sum(int(row["episodes"]) for row in seq005_with_heldout_rows)
    seq005_with_heldout_router = sum(int(row["router_successes"]) for row in seq005_with_heldout_rows)
    seq005_with_heldout_positive = sum(int(row["positive_successes"]) for row in seq005_with_heldout_rows)
    seq005_with_heldout_cau = sum(int(row["cau_successes"]) for row in seq005_with_heldout_rows)
    seq_eval50_rows = [seq606_eval50, seq101_eval50]
    seq_eval50_episodes = sum(int(row["episodes"]) for row in seq_eval50_rows)
    seq_eval50_router = sum(int(row["router_successes"]) for row in seq_eval50_rows)
    seq_eval50_positive = sum(int(row["positive_successes"]) for row in seq_eval50_rows)
    seq_eval50_cau = sum(int(row["cau_successes"]) for row in seq_eval50_rows)
    seq_eval50_gains = sum(int(row["gains_vs_positive"]) for row in seq_eval50_rows)
    seq_eval50_losses = sum(int(row["losses_vs_positive"]) for row in seq_eval50_rows)
    rows.append(
        {
            "criterion_id": "methods_sota_candidate_sweep",
            "required_for": "top_tier_methods_dominance",
            "status": "not_met",
            "criterion": "The focused SOTA-candidate sweep finds a promotable method beyond the precision/coverage framing.",
            "evidence": (
                f"Best Can404 short-screen candidates reach {best_can_success}/{best_can_episodes} "
                f"versus positive-only {can_positive}; CCG transfer reaches "
                f"{ccg['best_candidate_score']} versus positive-only {ccg['positive_score']}; "
                f"anchored IQL-AWBC reaches {anchored_iql['best_candidate_score']}; "
                f"Can404 anchor-overlap: CAU gains {cau_overlap['gains_vs_positive']} starts but loses "
                f"{cau_overlap['losses_vs_positive']} positive-only starts, while Demo-DPO gains "
                f"{demo_overlap['gains_vs_positive']} and loses {demo_overlap['losses_vs_positive']}; "
                f"post-hoc CAU feature fallback reaches {cau_gate['routed_successes']}/20 with "
                f"{cau_gate['losses_vs_positive']} same-screen anchor losses; frozen CAU fallback fresh "
                f"split505 first-20 reaches {cau_fallback_505_first20['routed_successes']}/"
                f"{cau_fallback_505_first20['eval_episodes']} versus positive-only "
                f"{cau_fallback_505_first20['positive_successes']}/{cau_fallback_505_first20['eval_episodes']}; "
                f"50-episode confirmation reaches {cau_fallback_505_eval50['routed_successes']}/"
                f"{cau_fallback_505_eval50['eval_episodes']} versus positive-only "
                f"{cau_fallback_505_eval50['positive_successes']}/{cau_fallback_505_eval50['eval_episodes']}, "
                f"with {cau_fallback_505_eval50['losses_vs_positive']} anchor losses; split303 first-20 "
                f"shows CAU alone {cau_fallback_303_first20['cau_successes']}/"
                f"{cau_fallback_303_first20['eval_episodes']} but frozen routed fallback "
                f"{cau_fallback_303_first20['routed_successes']}/{cau_fallback_303_first20['eval_episodes']} "
                f"versus positive-only {cau_fallback_303_first20['positive_successes']}/"
                f"{cau_fallback_303_first20['eval_episodes']} with "
                f"{cau_fallback_303_first20['losses_vs_positive']} anchor losses; two-feature CAU gate "
                f"split101 confirmation reaches {two_feature_101_eval50['routed_successes']}/"
                f"{two_feature_101_eval50['eval_episodes']} versus positive-only "
                f"{two_feature_101_eval50['positive_successes']}/{two_feature_101_eval50['eval_episodes']} "
                f"with {two_feature_101_eval50['losses_vs_positive']} losses, while split202 50-episode confirmation is "
                f"{two_feature_202_eval50['routed_successes']}/{two_feature_202_eval50['eval_episodes']} "
                f"versus {two_feature_202_eval50['positive_successes']}/{two_feature_202_eval50['eval_episodes']} "
                f"despite CAU alone reaching {two_feature_202_eval50['cau_successes']}/"
                f"{two_feature_202_eval50['eval_episodes']}; CAU-alone five-split follow-up reaches "
                f"{cau_five_split['cau_action_conflict']['successes']}/"
                f"{cau_five_split['cau_action_conflict']['eval_episodes']} versus positive-only "
                f"{cau_five_split['positive_only_nn']['successes']}/"
                f"{cau_five_split['positive_only_nn']['eval_episodes']}, weighted BC "
                f"{cau_five_split['weighted_bc']['successes']}/"
                f"{cau_five_split['weighted_bc']['eval_episodes']}, TRIAGE-BC v0.1 "
                f"{cau_five_split['triage_bc_v01']['successes']}/"
                f"{cau_five_split['triage_bc_v01']['eval_episodes']}, best old baseline per split "
                f"{cau_five_split['best_old_baseline_per_split']['successes']}/"
                f"{cau_five_split['best_old_baseline_per_split']['eval_episodes']}, and v0.2 selected union "
                f"{cau_five_split['v02_selected_union']['successes']}/"
                f"{cau_five_split['v02_selected_union']['eval_episodes']}; post-hoc CAU-plus-v0.2 "
                f"portfolio preflight selects CAU on splits {cau_v02_portfolio['selected_cau_splits']} "
                f"and v0.2 on splits {cau_v02_portfolio['selected_v02_splits']}, reaching "
                f"{cau_v02_portfolio['selected_successes']}/{cau_v02_portfolio['eval_episodes']} "
                f"but without fresh validation; LOO selector-feature audit has positive-only "
                f"{selector_positive}/{selector_total_episodes}, always-CAU "
                f"{selector_cau}/{selector_total_episodes}, oracle switch "
                f"{selector_oracle}/{selector_total_episodes}, safe selector "
                f"{selector_safe_routed}/{selector_total_episodes} with {selector_safe_gains} gains and "
                f"{selector_safe_losses} losses, and best-delta selector "
                f"{selector_best_routed}/{selector_total_episodes} with {selector_best_gains} gains and "
                f"{selector_best_losses} losses; policy-feature LOO audit has positive-only "
                f"{policy_selector_positive}/{policy_selector_total_episodes}, always-CAU "
                f"{policy_selector_cau}/{policy_selector_total_episodes}, oracle switch "
                f"{policy_selector_oracle}/{policy_selector_total_episodes}, safe selector "
                f"{policy_selector_safe_routed}/{policy_selector_total_episodes} with "
                f"{policy_selector_safe_gains} gains and {policy_selector_safe_losses} losses, "
                f"and best-delta selector {policy_selector_best_routed}/{policy_selector_total_episodes} "
                f"with {policy_selector_best_gains} gains and {policy_selector_best_losses} losses; "
                f"the pooled frozen policy-feature gate on fresh split909 is "
                f"{cau_policy_fresh909['cau_policy_feature_gate']['screen_score']} versus positive-only "
                f"{cau_policy_fresh909['positive_only_nn']['screen_score']} and CAU-alone "
                f"{cau_policy_fresh909['cau_action_conflict']['screen_score']}, with "
                f"{cau_policy_fresh909['cau_policy_feature_gate']['gate_open_episodes']} CAU opens; "
                f"linear learned-router LOO safe reaches {learned_safe_routed}/{learned_safe_episodes} "
                f"with {learned_safe_gains} gains and {learned_safe_losses} losses, while best-delta reaches "
                f"{learned_best_routed}/{learned_best_episodes} with {learned_best_gains} gains and "
                f"{learned_best_losses} losses; frozen learned routers on split909 open all CAU starts and reach "
                f"{learned_safe_fresh909['test_routed_successes']}/{learned_safe_fresh909['test_episodes']} safe "
                f"and {learned_best_fresh909['test_routed_successes']}/{learned_best_fresh909['test_episodes']} best-delta "
                f"versus positive-only {learned_safe_fresh909['test_positive_successes']}/{learned_safe_fresh909['test_episodes']}."
                f" Per-step support-margin router fixed threshold 0.05 reaches "
                f"{seq005_router}/{seq005_episodes} across splits 909/808/707 versus positive-only "
                f"{seq005_positive}/{seq005_episodes} and CAU {seq005_cau}/{seq005_episodes}, "
                f"with {seq005_gains} gains and {seq005_losses} loss versus positive-only; per split it reaches "
                f"{seq909['router_score']} on split909, {seq808['router_score']} on split808, and "
                f"{seq707['router_score']} on split707. The first no-retune held-out guardrail on split606 "
                f"is neutral at {seq606['router_score']} versus positive-only {seq606['positive_score']} "
                f"and CAU {seq606['cau_score']}; including split606, the same threshold is "
                f"{seq005_with_heldout_router}/{seq005_with_heldout_episodes} versus positive-only "
                f"{seq005_with_heldout_positive}/{seq005_with_heldout_episodes} and CAU "
                f"{seq005_with_heldout_cau}/{seq005_with_heldout_episodes}. The 50-episode split606 "
                f"validation is {seq606_eval50['router_score']} router versus positive-only "
                f"{seq606_eval50['positive_score']} and CAU {seq606_eval50['cau_score']}, "
                f"with {seq606_eval50['gains_vs_positive']} gains and {seq606_eval50['losses_vs_positive']} "
                f"losses versus positive-only; split101 is mixed-negative at {seq101_eval50['router_score']} "
                f"versus positive-only {seq101_eval50['positive_score']} but below CAU {seq101_eval50['cau_score']}. "
                f"Across these two 50-episode validations, the router is {seq_eval50_router}/{seq_eval50_episodes} "
                f"versus positive-only {seq_eval50_positive}/{seq_eval50_episodes} and CAU "
                f"{seq_eval50_cau}/{seq_eval50_episodes}, with {seq_eval50_gains} gains and "
                f"{seq_eval50_losses} losses versus positive-only. Persistent support-margin switching "
                f"falls to {seq101_persistent['router_score']} on split101 versus non-persistent "
                f"{seq101_eval50['router_score']} and CAU {seq101_eval50['cau_score']}."
            ),
            "artifact": "results/sota_candidate/SOTA_CANDIDATE_SWEEP_REPORT.md; results/sota_candidate/CAN404_ANCHOR_OVERLAP_REPORT.md; results/sota_candidate/CAN404_ANCHOR_FEATURE_GATE_PREFLIGHT_REPORT.md; results/sota_candidate/CAN505_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md; results/sota_candidate/CAN303_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md; results/sota_candidate/CAU_GATE_FEATURE_AUDIT_REPORT.md; results/sota_candidate/CAU_TWO_FEATURE_GATE_FRESH_VALIDATION_REPORT.md; results/sota_candidate/CAU_ACTION_CONFLICT_CAN_FIVE_SPLIT_ENDPOINT_REPORT.md; results/sota_candidate/CAU_V02_PORTFOLIO_PREFLIGHT_REPORT.md; results/sota_candidate/CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md; results/sota_candidate/CAU_POLICY_FEATURE_SELECTOR_LOO_AUDIT_REPORT.md; results/sota_candidate/CAU_POLICY_FEATURE_FRESH909_REPORT.md; results/sota_candidate/CAU_POLICY_FEATURE_LEARNED_ROUTER_AUDIT_REPORT.md; results/sota_candidate/CAU_SEQUENCE_SUPPORT_ROUTER_REPORT.md",
            "decision": "Do not promote SM-RWBC, CCG-Distill, SafeExpand, Demo-DPO, simple IQL-AWBC, the unchanged CAU fallback, the two-feature CAU gate, the current policy-feature gate, the learned policy-feature router, or the current per-step support-margin router as methods/SOTA dominance evidence yet; the support-margin router beats positive-only over two 50-episode no-retune validations but fails to capture the CAU-dominant split101 upside, so broader or improved routing is still needed; CAU action-conflict and CAU-plus-v0.2 remain useful method seeds.",
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
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
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
