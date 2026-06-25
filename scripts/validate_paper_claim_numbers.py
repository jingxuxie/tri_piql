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
    "checklist": ROOT / "paper" / "MANUSCRIPT_CHECKLIST.md",
    "outline": ROOT / "PAPER_DRAFT_OUTLINE.md",
}

CLAIM_CONTRACT_DOCS = ["latex", "iclr_latex", "markdown"]

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
    lift_top160 = read_csv(ROOT / "results" / "final_paper" / "ablations" / "lift_mg_classifier_top160_endpoint_summary.csv")
    bad_label_summary = read_csv(ROOT / "results" / "final_paper" / "tables" / "bad_label_control_summary.csv")

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

    lift_row = find_row(lift_top160, failures, method="classifier-score top160")
    if lift_row:
        if (as_int(lift_row, "pooled_successes", failures, "Lift top160"), as_int(lift_row, "pooled_episodes", failures, "Lift top160")) != (68, 150):
            fail("Lift classifier top160 expected 68/150", failures)
    expect_doc_contains(docs, ["latex", "iclr_latex", "markdown", "checklist"], "68/150", failures)

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

    for needle in [
        "Do not claim TRIAGE-BC uniformly beats weighted BC",
        "Do not claim TRIAGE-BC uniformly beats positive-only retrieval",
        "Do not claim bad labels are necessary on Can",
        "not validated inverse-Q robotics",
    ]:
        expect_doc_contains(docs, ["checklist"], needle, failures)

    validate_claim_contract(docs, failures)

    if failures:
        print("paper claim-number validation failed:")
        for item in failures:
            print(f"- {item}")
        sys.exit(1)

    print("validated paper claim numbers and claim contract against staged CSVs and manuscript text")


if __name__ == "__main__":
    main()
