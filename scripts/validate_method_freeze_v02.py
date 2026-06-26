from __future__ import annotations

import ast
import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "METHOD_FREEZE_V02.md"
ROUTER_SCRIPT = ROOT / "scripts" / "summarize_v02_fresh_router_support_audit.py"
SUPPORT_PER_SPLIT = ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_router_support_per_split.csv"
SUPPORT_SUMMARY = ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_router_support_summary.csv"
CAN_ENDPOINT = ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_can_endpoint_summary.csv"
LIFT_ENDPOINT = ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_lift_endpoint_summary.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def expect_contains(text: str, path: Path, needles: list[str], failures: list[str]) -> None:
    for needle in needles:
        if needle not in text:
            fail(f"{path.relative_to(ROOT)} missing expected text: {needle!r}", failures)


def function_source(path: Path, function_name: str, failures: list[str]) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            segment = ast.get_source_segment(text, node)
            if segment is None:
                fail(f"could not extract source for {function_name} in {path.relative_to(ROOT)}", failures)
                return ""
            return segment
    fail(f"{path.relative_to(ROOT)} missing function {function_name}", failures)
    return ""


def find_row(rows: list[dict[str, str]], failures: list[str], **where: str) -> dict[str, str]:
    matches = [
        row
        for row in rows
        if all(row.get(key) == value for key, value in where.items())
    ]
    if len(matches) != 1:
        fail(f"expected one row for {where}, found {len(matches)}", failures)
        return {}
    return matches[0]


def validate_freeze_text(failures: list[str]) -> None:
    text = FREEZE.read_text(encoding="utf-8")
    expect_contains(
        text,
        FREEZE,
        [
            "TRIAGE-BC v0.2 is a hidden-label-free portfolio router over three branches",
            "estimated_positive_mass = sum_tau p_u(tau)",
            "count_ge_pos_min = count_tau(g(tau) >= min_{tau+ in D+} g(tau+))",
            "If `estimated_positive_mass >= 800` and `count_ge_pos_min >= 400`, use",
            "`stress_abstain`",
            "Else if `estimated_positive_mass >= 200` and `count_ge_pos_min >= 80`, use",
            "`soft_weighted`",
            "Else use `hard_risk_union`",
            "Hidden labels are audit-only",
            "results/final_paper_v02/A1_FIVE_SPLIT_EXTENSION_PREFLIGHT.md",
        ],
        failures,
    )


def validate_router_source(failures: list[str]) -> None:
    router = function_source(ROUTER_SCRIPT, "router_decision", failures)
    expect_contains(
        router,
        ROUTER_SCRIPT,
        [
            "mass >= 800.0 and count_ge_pos_min >= 400",
            'branch = "stress_abstain"',
            "mass >= 200.0 and count_ge_pos_min >= 80",
            'branch = "soft_weighted"',
            'branch = "hard_risk_union"',
        ],
        failures,
    )
    if "labeled_positive_p10 >= 0.85" in router:
        fail(
            "v0.2 router_decision should not use the v0.1 labeled_positive_p10 branch rule",
            failures,
        )


def validate_support_artifacts(failures: list[str]) -> None:
    per_split = read_csv(SUPPORT_PER_SPLIT)
    summary = read_csv(SUPPORT_SUMMARY)

    expected_branches = {
        ("can40", "101"): "hard_risk_union",
        ("can40", "202"): "hard_risk_union",
        ("can40", "303"): "hard_risk_union",
        ("can40", "404"): "hard_risk_union",
        ("can40", "505"): "hard_risk_union",
        ("lift_mg", "101"): "soft_weighted",
        ("lift_mg", "202"): "soft_weighted",
        ("lift_mg", "303"): "soft_weighted",
        ("lift_mg", "404"): "soft_weighted",
        ("lift_mg", "505"): "soft_weighted",
    }
    for (setting_id, split_seed), expected_branch in expected_branches.items():
        rows = [
            row
            for row in per_split
            if row["setting_id"] == setting_id and row["split_seed"] == split_seed
        ]
        branches = {row["router_branch"] for row in rows}
        if branches != {expected_branch}:
            fail(
                f"{setting_id} split {split_seed}: expected router branch "
                f"{expected_branch!r}, got {sorted(branches)}",
                failures,
            )

    expected_summary = {
        ("can40", "positive_nn_risk_union_top40"): {
            "candidate_branch": "hard_risk_union",
            "split_count": "5",
            "selected_unlabeled": "226",
            "hidden_positive_selected": "198",
            "hidden_bad_selected": "28",
        },
        ("lift_mg", "weighted_bc"): {
            "candidate_branch": "soft_weighted",
            "split_count": "5",
            "selected_unlabeled": "7100",
            "hidden_positive_selected": "1380",
            "hidden_bad_selected": "5720",
        },
    }
    for (setting_id, candidate_id), expected_fields in expected_summary.items():
        row = find_row(summary, failures, setting_id=setting_id, candidate_id=candidate_id)
        if not row:
            continue
        for key, expected_value in expected_fields.items():
            if row.get(key) != expected_value:
                fail(
                    f"{setting_id} / {candidate_id}: expected {key}={expected_value!r}, "
                    f"got {row.get(key)!r}",
                    failures,
                )


def validate_endpoint_role_alignment(failures: list[str]) -> None:
    can = read_csv(CAN_ENDPOINT)
    lift = read_csv(LIFT_ENDPOINT)
    can_selected = [row for row in can if row["method_role"] == "v02_selected"]
    lift_selected = [row for row in lift if row["method_role"] == "v02_selected"]
    if len(can_selected) != 5:
        fail(f"expected 5 v0.2 selected Can endpoint rows, got {len(can_selected)}", failures)
    if len(lift_selected) != 5:
        fail(f"expected 5 v0.2 selected Lift endpoint rows, got {len(lift_selected)}", failures)
    for row in can_selected:
        if row["method_id"] != "positive_nn_risk_union_top40":
            fail(
                f"Can split {row['split_seed']} v0.2 selected row should be "
                f"positive_nn_risk_union_top40, got {row['method_id']}",
                failures,
            )
    for row in lift_selected:
        if row["method_id"] != "weighted_bc":
            fail(
                f"Lift split {row['split_seed']} v0.2 selected row should be "
                f"weighted_bc, got {row['method_id']}",
                failures,
            )


def main() -> None:
    failures: list[str] = []
    validate_freeze_text(failures)
    validate_router_source(failures)
    validate_support_artifacts(failures)
    validate_endpoint_role_alignment(failures)

    if failures:
        print("v0.2 method-freeze validation failed:")
        for failure in failures:
            print(f"- {failure}")
        sys.exit(1)

    print("validated METHOD_FREEZE_V02 against v0.2 router code and staged artifacts")


if __name__ == "__main__":
    main()
