from __future__ import annotations

import csv
import sys
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "latex": ROOT / "paper" / "triage_bc_paper.tex",
    "iclr_latex": ROOT / "paper" / "iclr2026" / "main.tex",
    "markdown": ROOT / "paper" / "triage_bc_draft.md",
    "paper_makefile": ROOT / "paper" / "Makefile",
    "reproduce_paper": ROOT / "paper" / "REPRODUCE_PAPER.md",
    "checklist": ROOT / "paper" / "MANUSCRIPT_CHECKLIST.md",
    "outline": ROOT / "PAPER_DRAFT_OUTLINE.md",
    "top_tier_plan": ROOT / "triage_bc_top_tier_completion_plan.md",
    "claim_package": ROOT / "results" / "PAPER_CLAIM_PACKAGE.md",
    "reviewer_summary": ROOT / "paper" / "REVIEWER_CLAIM_SUMMARY.md",
    "final_claim_contract": ROOT / "FINAL_CLAIM_CONTRACT.md",
    "final_artifact_readme": ROOT / "results" / "final_paper" / "README.md",
    "v02_artifact_readme": ROOT / "results" / "final_paper_v02" / "README.md",
}

CLAIM_CONTRACT_DOCS = ["latex", "iclr_latex", "markdown", "reviewer_summary", "final_claim_contract"]
CURRENT_CLAIM_DOCS = [
    "latex",
    "iclr_latex",
    "markdown",
    "paper_makefile",
    "reproduce_paper",
    "checklist",
    "outline",
    "top_tier_plan",
    "claim_package",
    "reviewer_summary",
    "final_claim_contract",
    "final_artifact_readme",
    "v02_artifact_readme",
]

REQUIRED_CLAIM_CAVEATS = [
    "not a validated inverse-Q robotics method",
    "Positive-only NN is the strongest",
    "Weighted BC is strongest",
    "formal significance claim",
    "not fully independent",
    "score-to-support conversion problem",
    "broad weighted coverage",
]

FORBIDDEN_UNQUALIFIED_CLAIMS = [
    re.compile(r"bad labels are (?:strictly )?(?:necessary|required)", re.IGNORECASE),
    re.compile(r"hard (?:filtering|support) (?:always wins|is uniformly better)", re.IGNORECASE),
    re.compile(r"(?:TRIAGE-BC|\\method\{\}) uniformly beats", re.IGNORECASE),
    re.compile(r"weighted BC is weak", re.IGNORECASE),
    re.compile(r"full .*inverse[- ]Q.*validated", re.IGNORECASE),
    re.compile(r"best checkpoint proves", re.IGNORECASE),
]

QUALIFYING_WORDS = ("not", "do not", "does not", "unvalidated", "not supported")

STALE_OR_OVERCLAIMING_CURRENT_CLAIMS = [
    (
        re.compile(r"modestly improves fresh Lift MG", re.IGNORECASE),
        "fresh Lift is not improved versus the completed per-split baseline",
    ),
    (
        re.compile(r"Lift endpoint advantage is modest", re.IGNORECASE),
        "fresh Lift has a negative per-split-baseline margin",
    ),
    (
        re.compile(r"340/500`?\s+versus\s+`?317/500", re.IGNORECASE),
        "fresh Can+Lift best-baseline total is now 338/500",
    ),
    (
        re.compile(r"best completed per-split non-oracle baselines\s+`?125/250", re.IGNORECASE),
        "fresh Lift best-baseline total is now 146/250 after the v0.1 audit",
    ),
    (
        re.compile(r"portfolio router can improve a fresh Can\+Lift gate", re.IGNORECASE),
        "fresh Can+Lift should be qualified as barely positive",
    ),
    (
        re.compile(r"portfolio router that improves a fresh Can\+Lift gate", re.IGNORECASE),
        "fresh Can+Lift should be qualified as barely positive",
    ),
    (
        re.compile(r"Weakness 2: three split seeds give low statistical power", re.IGNORECASE),
        "the fresh v0.2 gate is now expanded to five split seeds",
    ),
    (
        re.compile(r"Reduce the .only three split seeds. weakness", re.IGNORECASE),
        "A1 is now complete; the remaining issue is weak five-split margins",
    ),
    (
        re.compile(r"Test whether Can improvement and Lift modest gain persist", re.IGNORECASE),
        "fresh Lift is negative versus the completed per-split baseline",
    ),
    (
        re.compile(r"Combined Can\+Lift v0\.2 remains positive over the best fixed branch", re.IGNORECASE),
        "v0.2 ties the completed always-hard-support branch on Can+Lift",
    ),
    (
        re.compile(r"fresh v0\.2 branch selection improves the combined Can\+Lift gate", re.IGNORECASE),
        "fresh Can+Lift should be qualified as barely positive and not fixed-branch dominance",
    ),
    (
        re.compile(r"remains exploratory until split seeds `?202/303`? are complete", re.IGNORECASE),
        "Lift hard-negative endpoint split seeds 202/303 are now complete",
    ),
    (
        re.compile(r"expand to split seeds `?202/303`?", re.IGNORECASE),
        "Lift hard-negative endpoint split seeds 202/303 are now complete",
    ),
    (
        re.compile(r"is not a policy endpoint result until Lift endpoint training is run", re.IGNORECASE),
        "Lift hard-negative endpoint training has now run for split seeds 101/202/303",
    ),
    (
        re.compile(r"until the multi-split check is run", re.IGNORECASE),
        "coverage-shift Can endpoint aggregation is now complete",
    ),
    (
        re.compile(r"Can 40p/80b favors hard selected support", re.IGNORECASE),
        "Can 40p/80b should be qualified because positive-only NN is the strongest non-oracle Can row",
    ),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def find_row(rows: list[dict[str, str]], failures: list[str], **where: str) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if all(row.get(key) == value for key, value in where.items())
    ]
    if len(matches) != 1:
        fail(f"expected exactly one row for {where}, found {len(matches)}", failures)
        return {}
    return matches[0]


def as_int(row: dict[str, str], key: str, failures: list[str], context: str) -> int:
    try:
        return int(float(row[key]))
    except Exception:
        fail(f"{context}: field {key!r} is not an int-like value: {row.get(key)!r}", failures)
        return -1


def as_float(row: dict[str, str], key: str, failures: list[str], context: str) -> float:
    try:
        return float(row[key])
    except Exception:
        fail(f"{context}: field {key!r} is not a float value: {row.get(key)!r}", failures)
        return float("nan")


def expect_count(
    row: dict[str, str],
    successes: int,
    episodes: int,
    failures: list[str],
    context: str,
) -> None:
    got_successes = as_int(row, "successes", failures, context)
    got_episodes = as_int(row, "episodes", failures, context)
    if (got_successes, got_episodes) != (successes, episodes):
        fail(
            f"{context}: expected {successes}/{episodes}, got {got_successes}/{got_episodes}",
            failures,
        )


def expect_row_count(
    rows: list[dict[str, str]],
    failures: list[str],
    task: str,
    method: str,
    successes: int,
    episodes: int,
) -> None:
    row = find_row(rows, failures, task=task, method=method)
    if row:
        expect_count(row, successes, episodes, failures, f"{task} / {method}")


def expect_doc_contains(
    docs: dict[str, str],
    doc_names: list[str],
    needle: str,
    failures: list[str],
) -> None:
    for name in doc_names:
        if needle not in docs[name]:
            fail(f"{DOCS[name].relative_to(ROOT)} missing quoted claim {needle!r}", failures)


def validate_claim_contract(docs: dict[str, str], failures: list[str]) -> None:
    for needle in REQUIRED_CLAIM_CAVEATS:
        expect_doc_contains(docs, CLAIM_CONTRACT_DOCS, needle, failures)

    for name in CLAIM_CONTRACT_DOCS:
        for lineno, line in enumerate(docs[name].splitlines(), start=1):
            normalized = line.lower()
            for pattern in FORBIDDEN_UNQUALIFIED_CLAIMS:
                if not pattern.search(line):
                    continue
                if any(word in normalized for word in QUALIFYING_WORDS):
                    continue
                fail(
                    f"{DOCS[name].relative_to(ROOT)}:{lineno} has unqualified "
                    f"claim matching {pattern.pattern!r}: {line.strip()}",
                    failures,
                )


def validate_no_stale_current_claims(docs: dict[str, str], failures: list[str]) -> None:
    for name in CURRENT_CLAIM_DOCS:
        for pattern, reason in STALE_OR_OVERCLAIMING_CURRENT_CLAIMS:
            match = pattern.search(docs[name])
            if match:
                fail(
                    f"{DOCS[name].relative_to(ROOT)} contains stale or overclaiming "
                    f"fresh-gate wording ({reason}): {match.group(0)!r}",
                    failures,
                )


def expect_all_bad_fracs_perfect(
    rows: list[dict[str, str]], failures: list[str], n_pos: str, n_neg: str
) -> None:
    for bad_frac in ["0.50", "0.75", "0.90", "0.95"]:
        row = find_row(
            rows,
            failures,
            experiment="equal_label_budget",
            n_pos=n_pos,
            n_neg=n_neg,
            bad_frac=bad_frac,
            method="TRIAGE-BC gap support",
        )
        if not row:
            continue
        success = as_float(
            row,
            "success",
            failures,
            f"PointNav n_pos={n_pos} n_neg={n_neg} bad_frac={bad_frac}",
        )
        if abs(success - 1.0) > 1e-9:
            fail(
                f"PointNav n_pos={n_pos} n_neg={n_neg} bad_frac={bad_frac}: "
                f"expected TRIAGE gap support success 1.000, got {success:.3f}",
                failures,
            )


def expect_float_field(
    row: dict[str, str],
    key: str,
    expected: float,
    failures: list[str],
    context: str,
    tol: float = 1e-9,
) -> None:
    value = as_float(row, key, failures, context)
    if abs(value - expected) > tol:
        fail(f"{context}: expected {key}={expected:.3f}, got {value:.3f}", failures)


def main() -> None:
    failures: list[str] = []
    docs = {name: path.read_text(encoding="utf-8") for name, path in DOCS.items()}

    primary = read_csv(ROOT / "results" / "final_paper" / "tables" / "robotics_primary_endpoint_matrix.csv")
    current = read_csv(ROOT / "results" / "final_paper" / "tables" / "robotics_current_endpoint_matrix.csv")
    pointnav = read_csv(ROOT / "results" / "final_paper" / "tables" / "pointnav_controlled_mechanism.csv")
    pointnav_bad_count = read_csv(ROOT / "results" / "final_paper" / "ablations" / "continuous_pointnav_bad_label_count_npos5.csv")
    paired_bootstrap = read_csv(ROOT / "results" / "final_paper" / "tables" / "primary_endpoint_paired_bootstrap.csv")
    can20 = read_csv(ROOT / "results" / "final_paper" / "ablations" / "can_paired_pos20_bad80_support_audit_3split.csv")
    can80 = read_csv(ROOT / "results" / "final_paper" / "ablations" / "can_paired_balanced_80p80b_support_and_split33_endpoint.csv")
    can_mg = read_csv(ROOT / "results" / "final_paper" / "ablations" / "can_mg_branch_proxy_summary" / "method_proxy_scores.csv")
    can_mg_proxies = read_csv(ROOT / "results" / "final_paper" / "ablations" / "can_mg_branch_proxy_summary" / "proxy_winners.csv")
    active_abstention = read_csv(ROOT / "results" / "final_paper" / "tables" / "active_abstention_evaluation.csv")
    active_abstention_summary = read_csv(ROOT / "results" / "final_paper" / "tables" / "active_abstention_assignment_summary.csv")
    lift_top160 = read_csv(ROOT / "results" / "final_paper" / "ablations" / "lift_mg_classifier_top160_endpoint_summary.csv")
    bad_label_summary = read_csv(ROOT / "results" / "final_paper" / "tables" / "bad_label_control_summary.csv")
    hard_negative = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "ablations"
        / "hard_negative_can_endpoint_200ep"
        / "endpoint_200ep_3split_summary.csv"
    )
    lift_hard_negative = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "ablations"
        / "lift_hard_negative_action_conflict_summary.csv"
    )
    lift_hard_negative_endpoint = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "ablations"
        / "lift_hard_negative_endpoint_200ep"
        / "endpoint_200ep_summary.csv"
    )
    coverage_shift = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "ablations"
        / "can_coverage_shift_endpoint_200ep"
        / "endpoint_200ep_3split_summary.csv"
    )
    prefix_positive = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "can_prefix_positive_diagnostic.csv"
    )
    generated_regime_probe_summary = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "generated_regime_probe_summary.csv"
    )
    prefix_length_robustness = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "can_prefix_length_robustness.csv"
    )
    v02_policy_coverage_split11 = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "v02_policy_coverage_diagnostic.csv"
    )
    v02_policy_coverage_split22 = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "v02_policy_coverage_diagnostic_split22.csv"
    )
    v02_action_risk_setup_split11 = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "ablations"
        / "v02_action_risk_endpoint_200ep_can40"
        / "split11"
        / "endpoint_setup_summary.csv"
    )
    v02_action_risk_setup_split22 = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "ablations"
        / "v02_action_risk_endpoint_200ep_can40"
        / "split22"
        / "endpoint_setup_summary.csv"
    )
    v02_fresh_gate = read_csv(
        ROOT
        / "results"
        / "final_paper_v02"
        / "tables"
        / "v02_fresh_gate_summary.csv"
    )
    v02_fresh_gate_per_split = read_csv(
        ROOT
        / "results"
        / "final_paper_v02"
        / "tables"
        / "v02_fresh_gate_per_split.csv"
    )
    v02_fresh_uncertainty = read_csv(
        ROOT
        / "results"
        / "final_paper_v02"
        / "tables"
        / "v02_fresh_gate_uncertainty.csv"
    )
    hard_union_component = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "hard_union_component_ablation.csv"
    )
    failure_mode_cases = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "failure_mode_initial_states_cases.csv"
    )
    failure_mode_rows = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "failure_mode_initial_states.csv"
    )
    submission_readiness = read_csv(
        ROOT
        / "results"
        / "final_paper"
        / "tables"
        / "submission_readiness_audit.csv"
    )

    main_counts = {
        ("Can 40p/80b", "all-positive oracle"): (147, 150),
        ("Can 40p/80b", "positive-only NN"): (108, 150),
        ("Can 40p/80b", "TRIAGE-BC"): (99, 150),
        ("Can 40p/80b", "weighted BC"): (90, 150),
        ("Can 40p/80b", "all-demo BC"): (81, 150),
        ("Lift MG", "all-positive oracle"): (105, 150),
        ("Lift MG", "weighted BC"): (93, 150),
        ("Lift MG", "positive-only NN"): (82, 150),
        ("Lift MG", "TRIAGE-BC"): (74, 150),
        ("Lift MG", "all-demo BC"): (31, 150),
    }
    for (task, method), (successes, episodes) in main_counts.items():
        expect_row_count(primary, failures, task, method, successes, episodes)
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], f"{successes}/{episodes}", failures)

    for needle in ["99/150", "90/150", "81/150", "108/150", "93/150", "74/150", "82/150"]:
        expect_doc_contains(docs, ["checklist"], needle, failures)

    # Can 40p/80b support-side precision/coverage numbers.
    can40_triage = find_row(current, failures, task="Can 40p/80b", method="TRIAGE-BC")
    can40_posonly = find_row(current, failures, task="Can 40p/80b", method="positive-only NN")
    if can40_triage:
        if (as_int(can40_triage, "support_positive", failures, "Can 40 TRIAGE support"), as_int(can40_triage, "support_bad", failures, "Can 40 TRIAGE support")) != (110, 80):
            fail("Can 40 TRIAGE support expected 110 hidden positives and 80 hidden bad", failures)
    if can40_posonly:
        if (as_int(can40_posonly, "support_positive", failures, "Can 40 positive-only support"), as_int(can40_posonly, "support_bad", failures, "Can 40 positive-only support")) != (106, 14):
            fail("Can 40 positive-only support expected 106 hidden positives and 14 hidden bad", failures)
    for needle in ["110/120", "80/240", "106/120", "14/240"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)

    hard_union_expected = {
        "positive_only_nn_top40": (106, 14, "108/150", "+0.000", "complete_3split_endpoint"),
        "positive_nn_risk_fusion_top40": (117, 3, "73/100", "-0.070", "partial_2split_endpoint"),
        "positive_nn_risk_union_top40": (119, 16, "116/150", "+0.053", "complete_3split_endpoint"),
        "classifier_top40": (85, 35, "", "", "support_only"),
        "weighted_full_pool": (120, 240, "90/150", "-0.120", "complete_3split_endpoint"),
        "triage_adaptive_masscap": (110, 80, "99/150", "-0.060", "complete_3split_endpoint"),
    }
    for method_id, (hidden_pos, hidden_bad, endpoint_count, delta, status) in hard_union_expected.items():
        row = find_row(hard_union_component, failures, method_id=method_id)
        if not row:
            continue
        context = f"hard-union component {method_id}"
        if as_int(row, "hidden_positive_selected", failures, context) != hidden_pos:
            fail(f"{context}: hidden-positive count mismatch", failures)
        if as_int(row, "hidden_bad_selected", failures, context) != hidden_bad:
            fail(f"{context}: hidden-bad count mismatch", failures)
        if row.get("endpoint_success_count") != endpoint_count:
            fail(f"{context}: expected endpoint {endpoint_count!r}, got {row.get('endpoint_success_count')!r}", failures)
        if row.get("endpoint_delta_vs_positive_same_splits") != delta:
            fail(f"{context}: expected delta {delta!r}, got {row.get('endpoint_delta_vs_positive_same_splits')!r}", failures)
        if row.get("endpoint_status") != status:
            fail(f"{context}: expected status {status!r}, got {row.get('endpoint_status')!r}", failures)
    for needle in ["116/150", "108/150", "73/100", "119/120", "16/240"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)

    failure_case_expected = {
        "union_rescue": ("33", "demo_105", "5/5", "0/5", "1/5", "0/5"),
        "positive_anchor_regression": ("11", "demo_39", "0/5", "5/5", "0/5", "5/5"),
        "soft_pool_rescue": ("33", "demo_99", "1/5", "0/5", "5/5", "3/5"),
    }
    for case_id, (
        split_seed,
        initial_demo_id,
        union_success,
        positive_success,
        weighted_success,
        all_demo_success,
    ) in failure_case_expected.items():
        row = find_row(failure_mode_cases, failures, case_id=case_id)
        if not row:
            continue
        context = f"failure-mode case {case_id}"
        if row.get("split_seed") != split_seed:
            fail(f"{context}: expected split {split_seed}, got {row.get('split_seed')}", failures)
        if row.get("initial_demo_id") != initial_demo_id:
            fail(f"{context}: expected initial {initial_demo_id}, got {row.get('initial_demo_id')}", failures)
        if row.get("union_success_count") != union_success:
            fail(f"{context}: expected union {union_success}, got {row.get('union_success_count')}", failures)
        if row.get("positive_only_success_count") != positive_success:
            fail(f"{context}: expected positive-only {positive_success}, got {row.get('positive_only_success_count')}", failures)
        if row.get("weighted_bc_success_count") != weighted_success:
            fail(f"{context}: expected weighted {weighted_success}, got {row.get('weighted_bc_success_count')}", failures)
        if row.get("all_demo_success_count") != all_demo_success:
            fail(f"{context}: expected all-demo {all_demo_success}, got {row.get('all_demo_success_count')}", failures)

    failure_row_expected = {
        ("union_rescue", "positive_nn_risk_union_top40"): (5, 5, "118.8", "no_failure_observed"),
        ("union_rescue", "positive_only_nn_top40"): (0, 5, "400.0", "timeout_or_miss_all_failures"),
        ("positive_anchor_regression", "positive_only_nn_top40"): (5, 5, "125.2", "no_failure_observed"),
        ("positive_anchor_regression", "positive_nn_risk_union_top40"): (0, 5, "400.0", "timeout_or_miss_all_failures"),
        ("soft_pool_rescue", "weighted_bc_full_pool"): (5, 5, "123.8", "no_failure_observed"),
        ("soft_pool_rescue", "positive_nn_risk_union_top40"): (1, 5, "344.2", "timeout_or_miss_all_failures"),
    }
    for (case_id, method_id), (successes, episodes, avg_length, loop_proxy) in failure_row_expected.items():
        row = find_row(failure_mode_rows, failures, case_id=case_id, method_id=method_id)
        if not row:
            continue
        context = f"failure-mode row {case_id} / {method_id}"
        if as_int(row, "success_count", failures, context) != successes:
            fail(f"{context}: success count mismatch", failures)
        if as_int(row, "eval_episodes", failures, context) != episodes:
            fail(f"{context}: episode count mismatch", failures)
        if row.get("avg_trajectory_length") != avg_length:
            fail(f"{context}: expected average length {avg_length}, got {row.get('avg_trajectory_length')}", failures)
        if row.get("loop_or_miss_proxy") != loop_proxy:
            fail(f"{context}: expected loop proxy {loop_proxy}, got {row.get('loop_or_miss_proxy')}", failures)
    if len(failure_mode_cases) != 3:
        fail(f"failure-mode case table expected 3 rows, got {len(failure_mode_cases)}", failures)
    if len(failure_mode_rows) != 12:
        fail(f"failure-mode method table expected 12 rows, got {len(failure_mode_rows)}", failures)
    for needle in ["union rescue", "positive-anchor regression", "soft-pool rescue"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)
    expect_doc_contains(
        docs,
        ["checklist", "outline"],
        "failure_mode_initial_states_REPORT.md",
        failures,
    )

    expect_all_bad_fracs_perfect(pointnav, failures, "2", "2")
    expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], "1.000", failures)

    for n_neg in ["1", "2", "5"]:
        for bad_frac in ["0.50", "0.75", "0.90", "0.95"]:
            row = find_row(pointnav_bad_count, failures, n_neg=n_neg, bad_frac=bad_frac)
            if not row:
                continue
            context = f"PointNav bad-label count n_neg={n_neg} bad_frac={bad_frac}"
            expect_float_field(row, "selected_demo_purity", 1.0, failures, context)
            expect_float_field(row, "selected_transition_purity", 1.0, failures, context)
            expect_float_field(row, "hidden_bad_demos", 0.0, failures, context)
            if n_neg in {"1", "5"}:
                expect_float_field(row, "triage_gap_demo_bc", 1.0, failures, context)
    for needle in ["1/2/5", "1 labeled bad shortcut", "0 hidden-bad"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)

    bootstrap_expected = {
        ("Can 40p/80b", "TRIAGE-BC - weighted BC"): (0.060, -0.113, 0.240),
        ("Lift MG", "weighted BC - TRIAGE-BC"): (0.122, -0.100, 0.317),
        ("Lift MG", "TRIAGE-BC - all-demo BC"): (0.306, 0.211, 0.400),
    }
    for (task, comparison), (point, low, high) in bootstrap_expected.items():
        row = find_row(paired_bootstrap, failures, task=task, comparison=comparison)
        if not row:
            continue
        context = f"{task} / {comparison} paired bootstrap"
        expect_float_field(row, "point_delta", point, failures, context)
        expect_float_field(row, "bootstrap95_low", low, failures, context)
        expect_float_field(row, "bootstrap95_high", high, failures, context)
    for needle in ["-0.113", "0.240", "+0.122", "-0.100", "0.317", "0.211", "0.400"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)

    can20_expected = {
        "triage_adaptive_masscap": (46, 100, 54, 69),
        "positive_only_nn_top20": (54, 100, 49, 11),
        "weighted_full_pool": (18, 50, 60, 240),
    }
    for support_rule, (successes, episodes, hidden_pos, hidden_bad) in can20_expected.items():
        row = find_row(can20, failures, support_rule=support_rule)
        if not row:
            continue
        if as_int(row, "endpoint_successes", failures, f"Can 20 {support_rule}") != successes:
            fail(f"Can 20 {support_rule}: endpoint successes mismatch", failures)
        if as_int(row, "endpoint_episodes", failures, f"Can 20 {support_rule}") != episodes:
            fail(f"Can 20 {support_rule}: endpoint episodes mismatch", failures)
        if as_int(row, "total_hidden_positive", failures, f"Can 20 {support_rule}") != hidden_pos:
            fail(f"Can 20 {support_rule}: hidden positives mismatch", failures)
        if as_int(row, "total_hidden_bad", failures, f"Can 20 {support_rule}") != hidden_bad:
            fail(f"Can 20 {support_rule}: hidden bad mismatch", failures)
    for needle in ["54/100", "46/100", "18/50", "54/60", "49/60", "69/240", "11/240"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)

    for method, successes in [("positive_only_nn_top80", 49), ("triage_bc_adaptive_masscap", 43)]:
        row = find_row(can80, failures, split="33", method=method)
        if row:
            got_successes = as_int(row, "endpoint_successes", failures, f"Can 80 {method}")
            got_episodes = as_int(row, "eval_episodes", failures, f"Can 80 {method}")
            if (got_successes, got_episodes) != (successes, 50):
                fail(f"Can 80 {method}: expected {successes}/50, got {got_successes}/{got_episodes}", failures)
    for needle in ["49/50", "43/50"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)

    original_mg = [row for row in can_mg if row["split"] == "can_mg_original"]
    if original_mg:
        best = max(original_mg, key=lambda row: float(row["rollout_success_20k"]))
        if best["method"] != "weighted" or abs(float(best["rollout_success_20k"]) - 0.333) > 1e-9:
            fail("Can MG original rollout-best method should be weighted at 0.333", failures)
    false_original_proxy_matches = [
        row for row in can_mg_proxies
        if row["split"] == "can_mg_original" and row["proxy_matches_best_success"] == "false"
    ]
    if len(false_original_proxy_matches) != 6:
        fail(f"expected all 6 original Can MG proxies to miss rollout best, got {len(false_original_proxy_matches)} misses", failures)
    for needle in ["0.333", "0.200"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)

    active_expected = {
        "can_mg_original": (
            "stress_abstain",
            "1947.9",
            "1025.7",
            "weighted",
            "0.333",
            "alltrain",
            "0.100",
            "0/6",
            "0/6",
            "yes_proxy_miss_and_low_ceiling",
        ),
        "can_mg_shuffle42": (
            "stress_abstain",
            "1466.3",
            "515.7",
            "hard_posmin=soft_weighted",
            "0.100",
            "hard_posmin=soft_weighted",
            "0.100",
            "5/6",
            "6/6",
            "yes_all_forced_branches_weak",
        ),
    }
    for split, (
        decision,
        mass,
        count_ge_pos_min,
        best_branch,
        best_success,
        worst_branch,
        worst_success,
        proxy_method_match,
        proxy_success_match,
        justification,
    ) in active_expected.items():
        row = find_row(active_abstention, failures, split=split)
        if not row:
            continue
        context = f"active abstention {split}"
        expected_fields = {
            "router_decision": decision,
            "estimated_positive_mass": mass,
            "count_ge_pos_min": count_ge_pos_min,
            "best_forced_branch": best_branch,
            "best_forced_success_20k": best_success,
            "worst_forced_branch": worst_branch,
            "worst_forced_success_20k": worst_success,
            "proxy_matches_rollout_best_method": proxy_method_match,
            "proxy_matches_best_success": proxy_success_match,
            "abstention_justified": justification,
        }
        for key, expected_value in expected_fields.items():
            if row.get(key) != expected_value:
                fail(f"{context}: expected {key}={expected_value!r}, got {row.get(key)!r}", failures)

    active_summary_expected = {
        "assigned": ("6", "0.700", "0.600", "0.900"),
        "abstained": ("2", "0.217", "0.100", "0.333"),
    }
    for status, (num_rows, mean_policy, min_policy, max_policy) in active_summary_expected.items():
        row = find_row(active_abstention_summary, failures, assignment_status=status)
        if not row:
            continue
        context = f"active abstention summary {status}"
        expected_fields = {
            "num_rows": num_rows,
            "mean_policy_20k": mean_policy,
            "min_policy_20k": min_policy,
            "max_policy_20k": max_policy,
        }
        for key, expected_value in expected_fields.items():
            if row.get(key) != expected_value:
                fail(f"{context}: expected {key}={expected_value!r}, got {row.get(key)!r}", failures)
    for needle in ["1947.9", "1025.7", "1466.3", "515.7", "0.700"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist", "outline"], needle, failures)
    for needle in ["0/6", "6/6", "active_abstention_evaluation_REPORT.md"]:
        expect_doc_contains(docs, ["markdown", "checklist", "outline"], needle, failures)
    for needle in [
        "Proposition 1",
        "coverage-contamination criterion",
        "marginal coverage gain exceeds",
        "marginal contamination cost",
    ]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "outline"], needle, failures)

    lift_row = find_row(lift_top160, failures, method="classifier-score top160")
    if lift_row:
        if (as_int(lift_row, "pooled_successes", failures, "Lift top160"), as_int(lift_row, "pooled_episodes", failures, "Lift top160")) != (68, 150):
            fail("Lift classifier top160 expected 68/150", failures)
    expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], "68/150", failures)

    hard_negative_expected = {
        ("101", "hybrid_rank_fusion_badaware_heavy_top40"): (33, 50, 36, 4),
        ("101", "state_action_positive_nn_top40"): (30, 50, 16, 24),
        ("202", "hybrid_rank_fusion_badaware_heavy_top40"): (35, 50, 38, 2),
        ("202", "state_action_positive_nn_top40"): (27, 50, 22, 18),
        ("303", "hybrid_rank_fusion_badaware_heavy_top40"): (36, 50, 39, 1),
        ("303", "state_action_positive_nn_top40"): (34, 50, 32, 8),
    }
    aggregate: dict[str, list[int]] = {}
    for (split_seed, candidate_id), (successes, episodes, hidden_pos, hidden_bad) in hard_negative_expected.items():
        row = find_row(hard_negative, failures, split_seed=split_seed, candidate_id=candidate_id)
        if not row:
            continue
        context = f"Hard-negative Can split {split_seed} {candidate_id}"
        if as_int(row, "success_count", failures, context) != successes:
            fail(f"{context}: endpoint successes mismatch", failures)
        if as_int(row, "eval_episodes", failures, context) != episodes:
            fail(f"{context}: endpoint episodes mismatch", failures)
        if as_int(row, "selected_hidden_positive", failures, context) != hidden_pos:
            fail(f"{context}: hidden positives mismatch", failures)
        if as_int(row, "selected_hidden_bad", failures, context) != hidden_bad:
            fail(f"{context}: hidden bad mismatch", failures)
        entry = aggregate.setdefault(candidate_id, [0, 0, 0, 0])
        entry[0] += successes
        entry[1] += episodes
        entry[2] += hidden_pos
        entry[3] += hidden_bad
    expected_aggregate = {
        "hybrid_rank_fusion_badaware_heavy_top40": [104, 150, 113, 7],
        "state_action_positive_nn_top40": [91, 150, 70, 50],
    }
    if aggregate != expected_aggregate:
        fail(f"Hard-negative Can aggregate expected {expected_aggregate}, got {aggregate}", failures)
    for needle in ["104/150", "91/150"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)
    for needle in ["113 hidden positives", "7 hidden bad", "70 hidden positives", "50 hidden bad"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)

    lift_hard_negative_expected = {
        "state_action_positive_nn_top40": (12, 108, "0.100", "0.450", "0.100"),
        "bad_aware_proxy_top40": (82, 38, "0.683", "0.158", "0.683"),
        "hybrid_pos40_filter_badaware80_refill40": (68, 52, "0.567", "0.217", "0.567"),
    }
    for candidate_id, (hidden_pos, hidden_bad, recall, bad_admission, purity) in lift_hard_negative_expected.items():
        row = find_row(lift_hard_negative, failures, candidate_id=candidate_id)
        if not row:
            continue
        context = f"Lift hard-negative support {candidate_id}"
        if as_int(row, "hidden_positive_selected", failures, context) != hidden_pos:
            fail(f"{context}: hidden positives mismatch", failures)
        if as_int(row, "hidden_bad_selected", failures, context) != hidden_bad:
            fail(f"{context}: hidden bad mismatch", failures)
        if row.get("hidden_positive_recall") != recall:
            fail(f"{context}: expected recall {recall}, got {row.get('hidden_positive_recall')}", failures)
        if row.get("hidden_bad_admission") != bad_admission:
            fail(f"{context}: expected bad admission {bad_admission}, got {row.get('hidden_bad_admission')}", failures)
        if row.get("support_purity") != purity:
            fail(f"{context}: expected purity {purity}, got {row.get('support_purity')}", failures)
    for needle in ["82/120", "38/240", "12/120", "108/240"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)
    expect_doc_contains(
        docs,
        ["checklist", "outline"],
        "lift_hard_negative_action_conflict_REPORT.md",
        failures,
    )

    lift_endpoint_expected = {
        ("101", "bad_aware_proxy_top40"): (7, 50, 21, 19),
        ("101", "state_action_positive_nn_top40"): (3, 50, 7, 33),
        ("202", "bad_aware_proxy_top40"): (6, 50, 38, 2),
        ("202", "state_action_positive_nn_top40"): (1, 50, 0, 40),
        ("303", "bad_aware_proxy_top40"): (2, 50, 23, 17),
        ("303", "state_action_positive_nn_top40"): (1, 50, 5, 35),
    }
    lift_endpoint_aggregate: dict[str, list[int]] = {}
    for (split_seed, candidate_id), (successes, episodes, hidden_pos, hidden_bad) in lift_endpoint_expected.items():
        row = find_row(
            lift_hard_negative_endpoint,
            failures,
            split_seed=split_seed,
            candidate_id=candidate_id,
        )
        if not row:
            continue
        context = f"Lift hard-negative endpoint split {split_seed} {candidate_id}"
        if as_int(row, "success_count", failures, context) != successes:
            fail(f"{context}: endpoint successes mismatch", failures)
        if as_int(row, "eval_episodes", failures, context) != episodes:
            fail(f"{context}: endpoint episodes mismatch", failures)
        if as_int(row, "selected_hidden_positive", failures, context) != hidden_pos:
            fail(f"{context}: hidden positives mismatch", failures)
        if as_int(row, "selected_hidden_bad", failures, context) != hidden_bad:
            fail(f"{context}: hidden bad mismatch", failures)
        entry = lift_endpoint_aggregate.setdefault(candidate_id, [0, 0, 0, 0])
        entry[0] += successes
        entry[1] += episodes
        entry[2] += hidden_pos
        entry[3] += hidden_bad
    expected_lift_endpoint_aggregate = {
        "bad_aware_proxy_top40": [15, 150, 82, 38],
        "state_action_positive_nn_top40": [5, 150, 12, 108],
    }
    if lift_endpoint_aggregate != expected_lift_endpoint_aggregate:
        fail(
            f"Lift hard-negative endpoint aggregate expected {expected_lift_endpoint_aggregate}, got {lift_endpoint_aggregate}",
            failures,
        )
    for needle in ["15/150", "5/150", "82 hidden positives", "38 hidden bad", "12 hidden positives", "108 hidden bad"]:
        expect_doc_contains(
            docs,
            ["latex", "iclr_latex", "markdown", "checklist", "outline", "reviewer_summary", "final_claim_contract"],
            needle,
            failures,
        )
    expect_doc_contains(
        docs,
        ["checklist", "outline"],
        "lift_hard_negative_endpoint_200ep/REPORT.md",
        failures,
    )

    coverage_shift_expected = {
        ("101", "hybrid_rank_fusion_badaware_heavy_top40"): (39, 50, 39, 1),
        ("101", "state_action_positive_nn_top40"): (35, 50, 34, 6),
        ("202", "hybrid_rank_fusion_badaware_heavy_top40"): (41, 50, 39, 1),
        ("202", "state_action_positive_nn_top40"): (29, 50, 34, 6),
        ("303", "hybrid_rank_fusion_badaware_heavy_top40"): (40, 50, 40, 0),
        ("303", "state_action_positive_nn_top40"): (39, 50, 37, 3),
    }
    aggregate = {}
    for (split_seed, candidate_id), (successes, episodes, hidden_pos, hidden_bad) in coverage_shift_expected.items():
        row = find_row(coverage_shift, failures, split_seed=split_seed, candidate_id=candidate_id)
        if not row:
            continue
        context = f"Coverage-shift Can split {split_seed} {candidate_id}"
        if as_int(row, "success_count", failures, context) != successes:
            fail(f"{context}: endpoint successes mismatch", failures)
        if as_int(row, "eval_episodes", failures, context) != episodes:
            fail(f"{context}: endpoint episodes mismatch", failures)
        if as_int(row, "selected_hidden_positive", failures, context) != hidden_pos:
            fail(f"{context}: hidden positives mismatch", failures)
        if as_int(row, "selected_hidden_bad", failures, context) != hidden_bad:
            fail(f"{context}: hidden bad mismatch", failures)
        entry = aggregate.setdefault(candidate_id, [0, 0, 0, 0])
        entry[0] += successes
        entry[1] += episodes
        entry[2] += hidden_pos
        entry[3] += hidden_bad
    expected_coverage_aggregate = {
        "hybrid_rank_fusion_badaware_heavy_top40": [120, 150, 118, 2],
        "state_action_positive_nn_top40": [103, 150, 105, 15],
    }
    if aggregate != expected_coverage_aggregate:
        fail(f"Coverage-shift Can aggregate expected {expected_coverage_aggregate}, got {aggregate}", failures)
    for needle in ["120/150", "103/150"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)
    for needle in ["118 hidden positives", "2 hidden bad", "105 hidden positives", "15 hidden bad"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)

    prefix_positive_expected = {
        "prefix_bad_aware_state_top80": (119, 150, 195, 45),
        "prefix_state_action_nn_top80": (6, 150, 37, 203),
    }
    for candidate_id, (successes, episodes, hidden_pos, hidden_bad) in prefix_positive_expected.items():
        row = find_row(prefix_positive, failures, candidate_id=candidate_id)
        if not row:
            continue
        context = f"Prefix-positive Can {candidate_id}"
        success_parts = row["success"].split("/")
        if len(success_parts) != 2:
            fail(f"{context}: malformed success field {row['success']!r}", failures)
            continue
        got_successes = int(success_parts[0])
        got_episodes = int(success_parts[1])
        if (got_successes, got_episodes) != (successes, episodes):
            fail(
                f"{context}: expected {successes}/{episodes}, got {got_successes}/{got_episodes}",
                failures,
            )
        if as_int(row, "hidden_positive_selected", failures, context) != hidden_pos:
            fail(f"{context}: hidden positives mismatch", failures)
        if as_int(row, "hidden_bad_selected", failures, context) != hidden_bad:
            fail(f"{context}: hidden bad mismatch", failures)
    for needle in ["119/150", "6/150"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)
    for needle in ["195 hidden positives", "45 hidden bad", "37 hidden positives", "203 hidden bad"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)

    generated_summary_expected = {
        "hard_negative_can": ("104/150", "91/150", "+13/150", "113", "7", "70", "50"),
        "coverage_shift_can": ("120/150", "103/150", "+17/150", "118", "2", "105", "15"),
        "prefix_positive_can": ("119/150", "6/150", "+113/150", "195", "45", "37", "203"),
    }
    for probe_id, (
        bad_endpoint,
        positive_endpoint,
        endpoint_delta,
        bad_hidden_pos,
        bad_hidden_bad,
        positive_hidden_pos,
        positive_hidden_bad,
    ) in generated_summary_expected.items():
        row = find_row(generated_regime_probe_summary, failures, probe_id=probe_id)
        if not row:
            continue
        context = f"generated regime-probe summary {probe_id}"
        expected_fields = {
            "bad_aware_endpoint": bad_endpoint,
            "positive_endpoint": positive_endpoint,
            "endpoint_delta": endpoint_delta,
            "bad_aware_hidden_positive": bad_hidden_pos,
            "bad_aware_hidden_bad": bad_hidden_bad,
            "positive_hidden_positive": positive_hidden_pos,
            "positive_hidden_bad": positive_hidden_bad,
            "claim_scope": "generated diagnostic, not primary benchmark row",
        }
        for key, expected_value in expected_fields.items():
            if row.get(key) != expected_value:
                fail(f"{context}: expected {key}={expected_value!r}, got {row.get(key)!r}", failures)
    for needle in ["+13/150", "+17/150", "+113/150", "113/7", "70/50", "118/2", "105/15", "195/45", "37/203"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)
    expect_doc_contains(
        docs,
        ["markdown", "checklist", "outline"],
        "generated_regime_probe_summary_REPORT.md",
        failures,
    )

    prefix_length_expected = {
        ("short_prefix", "prefix_state_action_nn_top80"): (61, 179, "0.254", "0.746", "0.000", "0.000"),
        ("short_prefix", "prefix_bad_aware_state_top80"): (157, 83, "0.654", "0.346", "0.400", "-0.400"),
        ("default_prefix", "prefix_state_action_nn_top80"): (37, 203, "0.154", "0.846", "0.000", "0.000"),
        ("default_prefix", "prefix_bad_aware_state_top80"): (195, 45, "0.812", "0.188", "0.658", "-0.658"),
        ("long_prefix", "prefix_state_action_nn_top80"): (22, 218, "0.092", "0.908", "0.000", "0.000"),
        ("long_prefix", "prefix_bad_aware_state_top80"): (199, 41, "0.829", "0.171", "0.737", "-0.737"),
    }
    for (config_id, candidate_id), (
        hidden_pos,
        hidden_bad,
        recall,
        bad_admission,
        recall_delta,
        bad_delta,
    ) in prefix_length_expected.items():
        row = find_row(prefix_length_robustness, failures, config_id=config_id, candidate_id=candidate_id)
        if not row:
            continue
        context = f"prefix-length robustness {config_id} / {candidate_id}"
        if as_int(row, "hidden_positive_selected", failures, context) != hidden_pos:
            fail(f"{context}: hidden positives mismatch", failures)
        if as_int(row, "hidden_bad_selected", failures, context) != hidden_bad:
            fail(f"{context}: hidden bad mismatch", failures)
        if row.get("hidden_positive_recall") != recall:
            fail(f"{context}: expected recall {recall}, got {row.get('hidden_positive_recall')}", failures)
        if row.get("hidden_bad_admission") != bad_admission:
            fail(f"{context}: expected bad admission {bad_admission}, got {row.get('hidden_bad_admission')}", failures)
        if row.get("delta_recall_vs_prefix_state_action_nn_top80") != recall_delta:
            fail(f"{context}: expected recall delta {recall_delta}, got {row.get('delta_recall_vs_prefix_state_action_nn_top80')}", failures)
        if row.get("delta_bad_admission_vs_prefix_state_action_nn_top80") != bad_delta:
            fail(f"{context}: expected bad-admission delta {bad_delta}, got {row.get('delta_bad_admission_vs_prefix_state_action_nn_top80')}", failures)
    if len(prefix_length_robustness) != 15:
        fail(f"prefix-length robustness key table expected 15 rows, got {len(prefix_length_robustness)}", failures)
    for needle in ["+0.400", "+0.658", "+0.737", "-0.400", "-0.658", "-0.737"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)
    expect_doc_contains(
        docs,
        ["checklist", "outline"],
        "can_prefix_length_robustness_REPORT.md",
        failures,
    )

    v02_endpoint_expected = [
        (v02_policy_coverage_split11, "positive_nn_risk_fusion_top40", 0.820, 49, 1, "split 11 risk fusion"),
        (v02_policy_coverage_split11, "positive_only_nn", 0.840, 46, 4, "split 11 positive-only"),
        (v02_policy_coverage_split22, "positive_nn_risk_fusion_top40", 0.640, 50, 0, "split 22 risk fusion"),
        (v02_policy_coverage_split22, "positive_only_nn", 0.760, 47, 3, "split 22 positive-only"),
    ]
    for rows, method_id, success, train_pos, train_bad, context in v02_endpoint_expected:
        row = find_row(rows, failures, method_id=method_id)
        if not row:
            continue
        expect_float_field(row, "endpoint_success", success, failures, f"v0.2 action-risk {context}", tol=1e-9)
        if as_int(row, "train_positive_count", failures, f"v0.2 action-risk {context}") != train_pos:
            fail(f"v0.2 action-risk {context}: train positive count mismatch", failures)
        if as_int(row, "train_bad_count", failures, f"v0.2 action-risk {context}") != train_bad:
            fail(f"v0.2 action-risk {context}: train bad count mismatch", failures)
    v02_setup_expected = [
        (v02_action_risk_setup_split11, "positive_nn_risk_fusion_top40", 39, 1, "split 11 risk fusion setup"),
        (v02_action_risk_setup_split22, "positive_nn_risk_fusion_top40", 40, 0, "split 22 risk fusion setup"),
    ]
    for rows, candidate_id, hidden_pos, hidden_bad, context in v02_setup_expected:
        row = find_row(rows, failures, candidate_id=candidate_id)
        if not row:
            continue
        if as_int(row, "selected_hidden_positive", failures, f"v0.2 action-risk {context}") != hidden_pos:
            fail(f"v0.2 action-risk {context}: selected hidden positives mismatch", failures)
        if as_int(row, "selected_hidden_bad", failures, f"v0.2 action-risk {context}") != hidden_bad:
            fail(f"v0.2 action-risk {context}: selected hidden bad mismatch", failures)
    for needle in ["0.820", "0.840", "0.640", "0.760"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)
    for needle in ["39 hidden positives", "1 hidden bad", "40 hidden positives", "0 hidden bad"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)

    v02_fresh_expected = {
        "Can 40p/80b": (197, 250, 192, 250, "+0.020", 4, 1),
        "Lift MG": (143, 250, 146, 250, "-0.012", 2, 3),
    }
    for setting_label, (
        selected_success,
        selected_episodes,
        baseline_success,
        baseline_episodes,
        margin,
        winning_splits,
        losing_splits,
    ) in v02_fresh_expected.items():
        row = find_row(v02_fresh_gate, failures, setting_label=setting_label)
        if not row:
            continue
        context = f"v0.2 fresh gate {setting_label}"
        if as_int(row, "selected_success", failures, context) != selected_success:
            fail(f"{context}: selected success mismatch", failures)
        if as_int(row, "selected_episodes", failures, context) != selected_episodes:
            fail(f"{context}: selected episodes mismatch", failures)
        if as_int(row, "best_baseline_success", failures, context) != baseline_success:
            fail(f"{context}: best baseline success mismatch", failures)
        if as_int(row, "best_baseline_episodes", failures, context) != baseline_episodes:
            fail(f"{context}: best baseline episodes mismatch", failures)
        if row.get("margin") != margin:
            fail(f"{context}: expected margin {margin}, got {row.get('margin')}", failures)
        if as_int(row, "winning_splits", failures, context) != winning_splits:
            fail(f"{context}: winning split count mismatch", failures)
        if as_int(row, "losing_splits", failures, context) != losing_splits:
            fail(f"{context}: losing split count mismatch", failures)

    combined_selected = sum(as_int(row, "selected_success", failures, "v0.2 fresh gate combined") for row in v02_fresh_gate)
    combined_selected_eps = sum(as_int(row, "selected_episodes", failures, "v0.2 fresh gate combined") for row in v02_fresh_gate)
    combined_baseline = sum(as_int(row, "best_baseline_success", failures, "v0.2 fresh gate combined") for row in v02_fresh_gate)
    combined_baseline_eps = sum(as_int(row, "best_baseline_episodes", failures, "v0.2 fresh gate combined") for row in v02_fresh_gate)
    if (combined_selected, combined_selected_eps, combined_baseline, combined_baseline_eps) != (340, 500, 338, 500):
        fail(
            "v0.2 fresh gate combined expected selected 340/500 and best baselines 338/500, "
            f"got {combined_selected}/{combined_selected_eps} and {combined_baseline}/{combined_baseline_eps}",
            failures,
        )
    for needle in ["340/500", "338/500", "197/250", "192/250", "143/250", "146/250"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)
    for needle in ["340/500", "338/500", "197/250", "192/250", "143/250", "146/250"]:
        expect_doc_contains(docs, ["v02_artifact_readme", "final_artifact_readme"], needle, failures)
    for needle in ["+8/50", "+5/50", "+3/50", "-12/50", "+1/50", "-5/50", "-4/50", "-2/50", "+7/50"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)
    for needle in ["-0.144", "0.168", "-0.083", "0.140", "-0.074", "0.120"]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], needle, failures)

    v02_uncertainty_expected = {
        "Can 40p/80b": (197, 250, 192, 250, 0.020, -0.144, 0.168, "+++-+", "0.375"),
        "Lift MG": (143, 250, 146, 250, -0.012, -0.083, 0.140, "+---+", "1.000"),
        "Combined Can+Lift": (340, 500, 338, 500, 0.004, -0.074, 0.120, "+++-++---+", "0.754"),
    }
    for scope, (
        selected_success,
        selected_episodes,
        baseline_success,
        baseline_episodes,
        pooled_delta,
        boot_low,
        boot_high,
        split_signs,
        sign_p,
    ) in v02_uncertainty_expected.items():
        row = find_row(v02_fresh_uncertainty, failures, scope=scope)
        if not row:
            continue
        context = f"v0.2 fresh uncertainty {scope}"
        if as_int(row, "selected_success", failures, context) != selected_success:
            fail(f"{context}: selected success mismatch", failures)
        if as_int(row, "selected_episodes", failures, context) != selected_episodes:
            fail(f"{context}: selected episodes mismatch", failures)
        if as_int(row, "best_baseline_success", failures, context) != baseline_success:
            fail(f"{context}: baseline success mismatch", failures)
        if as_int(row, "best_baseline_episodes", failures, context) != baseline_episodes:
            fail(f"{context}: baseline episodes mismatch", failures)
        expect_float_field(row, "pooled_delta", pooled_delta, failures, context)
        expect_float_field(row, "paired_bootstrap95_low", boot_low, failures, context)
        expect_float_field(row, "paired_bootstrap95_high", boot_high, failures, context)
        if row.get("split_signs") != split_signs:
            fail(f"{context}: expected split signs {split_signs}, got {row.get('split_signs')}", failures)
        if row.get("split_sign_p_two_sided") != sign_p:
            fail(f"{context}: expected sign p {sign_p}, got {row.get('split_sign_p_two_sided')}", failures)

    v02_split_expected = {
        ("Can 40p/80b", "101"): ("positive_nn_risk_union_top40", 45, "weighted_bc", 37),
        ("Can 40p/80b", "202"): ("positive_nn_risk_union_top40", 45, "positive_only_nn", 40),
        ("Can 40p/80b", "303"): ("positive_nn_risk_union_top40", 39, "positive_only_nn", 36),
        ("Can 40p/80b", "404"): ("positive_nn_risk_union_top40", 27, "positive_only_nn", 39),
        ("Can 40p/80b", "505"): ("positive_nn_risk_union_top40", 41, "positive_only_nn", 40),
        ("Lift MG", "101"): ("weighted_bc", 31, "triage_bc", 36),
        ("Lift MG", "202"): ("weighted_bc", 30, "triage_bc", 34),
        ("Lift MG", "303"): ("weighted_bc", 19, "positive_only_nn", 21),
        ("Lift MG", "404"): ("weighted_bc", 30, "triage_bc", 29),
        ("Lift MG", "505"): ("weighted_bc", 33, "positive_only_nn", 26),
    }
    for (setting_label, split_seed), (selected_method, selected_success, baseline_method, baseline_success) in v02_split_expected.items():
        row = find_row(v02_fresh_gate_per_split, failures, setting_label=setting_label, split_seed=split_seed)
        if not row:
            continue
        context = f"v0.2 fresh gate {setting_label} split {split_seed}"
        if row.get("selected_method") != selected_method:
            fail(f"{context}: selected method mismatch", failures)
        if as_int(row, "selected_success", failures, context) != selected_success:
            fail(f"{context}: selected successes mismatch", failures)
        if row.get("best_baseline_method") != baseline_method:
            fail(f"{context}: best baseline method mismatch", failures)
        if as_int(row, "best_baseline_success", failures, context) != baseline_success:
            fail(f"{context}: best baseline successes mismatch", failures)

    bad_label_expected = {
        "Controlled PointNav n+=5, n- in {1,2,5}": (
            "min 0.973, mean 0.997",
            "BC-all mean 0.292; local weighted mean 0.131",
            "min purity 1.000; max hidden-bad demos 0.0",
            "",
        ),
        "Can 40p/80b primary frozen 3-split": (
            "99/150",
            "108/150",
            "110 pos, 80 bad / 190 selected (purity 0.579)",
            "106 pos, 14 bad / 120 selected (purity 0.883)",
        ),
        "Can 20p/80b diagnostic support audit + two endpoints": (
            "46/100",
            "54/100",
            "54 pos, 69 bad / 123 selected (purity 0.439)",
            "49 pos, 11 bad / 60 selected (purity 0.817)",
        ),
        "Can 80p/80b balanced diagnostic": (
            "43/50",
            "49/50",
            "137 pos, 28 bad / 165 selected (purity 0.830)",
            "220 pos, 20 bad / 240 selected (purity 0.917)",
        ),
        "Lift MG primary frozen 3-split": (
            "74/150",
            "82/150",
            "421 pos, 20 bad / 441 selected (purity 0.955)",
            "342 pos, 138 bad / 480 selected (purity 0.713)",
        ),
    }
    for setting, expected_values in bad_label_expected.items():
        row = find_row(bad_label_summary, failures, setting=setting)
        if not row:
            continue
        got = (
            row["bad_aware_endpoint"],
            row["baseline_endpoint"],
            row["bad_aware_support"],
            row["baseline_support"],
        )
        if got != expected_values:
            fail(f"bad-label summary row {setting!r}: expected {expected_values}, got {got}", failures)

    for needle in [
        "Bad-label versus positive-only control summary",
        "0.973/0.997",
        "0.292",
        "0.131",
        "110 versus 106",
        "80 versus 14",
        "421",
        "342",
        "138",
    ]:
        expect_doc_contains(docs, ["latex", "iclr_latex", "markdown"], needle, failures)

    readiness_counts = {
        ("high_quality_empirical_submission", "pass"): 6,
        ("high_quality_empirical_submission", "caution"): 0,
        ("top_tier_methods_dominance", "caution"): 1,
        ("top_tier_methods_dominance", "not_met"): 3,
    }
    for (required_for, status), expected_count in readiness_counts.items():
        got = sum(
            1
            for row in submission_readiness
            if row.get("required_for") == required_for and row.get("status") == status
        )
        if got != expected_count:
            fail(
                f"submission-readiness audit expected {expected_count} rows for "
                f"{required_for}/{status}, got {got}",
                failures,
            )
    if len(submission_readiness) != 10:
        fail(f"submission-readiness audit expected 10 criteria rows, got {len(submission_readiness)}", failures)

    readiness_expected = {
        "empirical_v02_fresh_gate": ("pass", ["340/500", "338/500", "197/250", "192/250", "143/250", "146/250"]),
        "empirical_regime_probes": ("pass", ["104/150", "91/150", "120/150", "103/150", "119/150", "6/150"]),
        "methods_fixed_branch_dominance": ("not_met", ["23/500"]),
        "methods_uncertainty_above_zero": ("not_met", ["[-0.074, 0.120]"]),
        "methods_second_non_can_task": ("caution", ["15/150", "5/150"]),
        "methods_validated_policy_proxy": ("not_met", ["2/11"]),
    }
    for criterion_id, (expected_status, evidence_needles) in readiness_expected.items():
        row = find_row(submission_readiness, failures, criterion_id=criterion_id)
        if not row:
            continue
        if row.get("status") != expected_status:
            fail(
                f"submission-readiness {criterion_id}: expected status {expected_status}, got {row.get('status')}",
                failures,
            )
        for needle in evidence_needles:
            if needle not in row.get("evidence", ""):
                fail(f"submission-readiness {criterion_id}: evidence missing {needle!r}", failures)
    expect_doc_contains(
        docs,
        ["checklist", "final_claim_contract"],
        "submission_readiness_audit_REPORT.md",
        failures,
    )

    for needle in [
        "Do not claim TRIAGE-BC uniformly beats weighted BC",
        "Do not claim TRIAGE-BC uniformly beats positive-only retrieval",
        "Do not claim bad labels are necessary on Can",
        "not validated inverse-Q robotics",
    ]:
        expect_doc_contains(docs, ["checklist"], needle, failures)

    validate_claim_contract(docs, failures)
    validate_no_stale_current_claims(docs, failures)
    expect_doc_contains(
        docs,
        ["latex", "iclr_latex", "markdown"],
        "frozen portfolio router is barely positive on a fresh Can+Lift gate",
        failures,
    )
    expect_doc_contains(
        docs,
        ["latex", "iclr_latex", "markdown"],
        "generated split constructions are not intended to replace default benchmark rows",
        failures,
    )
    expect_doc_contains(
        docs,
        ["latex", "iclr_latex", "markdown"],
        "fresh all-demo/all-positive diagnostic rows remain unrun",
        failures,
    )
    expect_doc_contains(
        docs,
        ["reviewer_summary", "final_claim_contract"],
        "barely positive",
        failures,
    )
    expect_doc_contains(
        docs,
        ["reviewer_summary", "final_claim_contract"],
        "fresh all-demo/all-positive diagnostic",
        failures,
    )
    for needle in [
        "five split seeds still leave weak margins",
        "Combined Can+Lift selected branches reach `340/500` versus `338/500`",
        "ties the completed always-hard-support branch on Can+Lift",
        "Do not promote v0.2 as methods/SOTA dominance",
    ]:
        expect_doc_contains(docs, ["top_tier_plan"], needle, failures)
    for needle in [
        "Non-Can C1 full-budget endpoint update",
        "Bad-aware proxy top40 reaches `15/150` versus state-action positive-NN top40 `5/150`",
        "completed non-Can mechanism evidence",
        "barely positive selected-vs-baseline Can+Lift gate",
    ]:
        expect_doc_contains(docs, ["claim_package"], needle, failures)

    if failures:
        print("paper claim-number validation failed:")
        for item in failures:
            print(f"- {item}")
        sys.exit(1)

    print("validated paper claim numbers and claim contract against staged CSVs and manuscript text")


if __name__ == "__main__":
    main()
