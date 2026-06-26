from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_ROOT = Path("results/final_paper_v02")
DEFAULT_SPLITS = ("101", "202", "303", "404", "505")


EXPECTED_ROWS = [
    {
        "setting_label": "Can 40p/80b",
        "summary_file": "v02_fresh_can_endpoint_summary.csv",
        "row_label": "v0.2 selected hard union",
        "method_id": "positive_nn_risk_union_top40",
        "requirement": "required_branch_selection",
        "role": "v02_selected",
    },
    {
        "setting_label": "Can 40p/80b",
        "summary_file": "v02_fresh_can_endpoint_summary.csv",
        "row_label": "positive-only NN",
        "method_id": "positive_only_nn",
        "requirement": "required_branch_selection",
        "role": "strong_baseline",
    },
    {
        "setting_label": "Can 40p/80b",
        "summary_file": "v02_fresh_can_endpoint_summary.csv",
        "row_label": "weighted BC",
        "method_id": "weighted_bc",
        "requirement": "required_branch_selection",
        "role": "strong_baseline",
    },
    {
        "setting_label": "Can 40p/80b",
        "summary_file": "v02_fresh_can_endpoint_summary.csv",
        "row_label": "v0.1 TRIAGE-BC",
        "method_id": "triage_bc",
        "requirement": "required_branch_selection",
        "role": "v01_fixed_branch",
    },
    {
        "setting_label": "Can 40p/80b",
        "summary_file": "v02_fresh_can_endpoint_summary.csv",
        "row_label": "all-demo BC",
        "method_id": "bc_all_mixed",
        "requirement": "optional_diagnostic",
        "role": "all_demo_control",
    },
    {
        "setting_label": "Can 40p/80b",
        "summary_file": "v02_fresh_can_endpoint_summary.csv",
        "row_label": "all-positive oracle",
        "method_id": "all_train_positive_oracle",
        "requirement": "optional_diagnostic",
        "role": "oracle_control",
    },
    {
        "setting_label": "Lift MG",
        "summary_file": "v02_fresh_lift_endpoint_summary.csv",
        "row_label": "v0.2 selected weighted BC",
        "method_id": "weighted_bc",
        "requirement": "required_branch_selection",
        "role": "v02_selected",
    },
    {
        "setting_label": "Lift MG",
        "summary_file": "v02_fresh_lift_endpoint_summary.csv",
        "row_label": "positive-only NN",
        "method_id": "positive_only_nn",
        "requirement": "required_branch_selection",
        "role": "strong_baseline",
    },
    {
        "setting_label": "Lift MG",
        "summary_file": "v02_fresh_lift_endpoint_summary.csv",
        "row_label": "v0.1 TRIAGE-BC",
        "method_id": "triage_bc",
        "requirement": "required_branch_selection",
        "role": "v01_fixed_branch",
    },
    {
        "setting_label": "Lift MG",
        "summary_file": "v02_fresh_lift_endpoint_summary.csv",
        "row_label": "all-demo BC",
        "method_id": "bc_all_mixed",
        "requirement": "optional_diagnostic",
        "role": "all_demo_control",
    },
    {
        "setting_label": "Lift MG",
        "summary_file": "v02_fresh_lift_endpoint_summary.csv",
        "row_label": "all-positive oracle",
        "method_id": "all_train_positive_oracle",
        "requirement": "optional_diagnostic",
        "role": "oracle_control",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--split-seeds", nargs="+", default=list(DEFAULT_SPLITS))
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    out = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return out


def summarize_rows(root: Path, split_seeds: list[str]) -> list[dict[str, object]]:
    cached_tables: dict[str, list[dict[str, str]]] = {}
    expected_splits = set(split_seeds)
    out: list[dict[str, object]] = []

    for expected in EXPECTED_ROWS:
        summary_file = expected["summary_file"]
        if summary_file not in cached_tables:
            cached_tables[summary_file] = read_csv(root / "tables" / summary_file)
        rows = [
            row
            for row in cached_tables[summary_file]
            if row["method_id"] == expected["method_id"]
        ]
        completed_splits = sorted({row["split_seed"] for row in rows}, key=int)
        missing_splits = [split for split in split_seeds if split not in completed_splits]
        successes = sum(int(row["success_count"]) for row in rows)
        episodes = sum(int(row["eval_episodes"]) for row in rows)
        status = "complete" if not missing_splits and rows else "missing"
        if expected["requirement"] == "optional_diagnostic" and status == "missing":
            status = "optional_not_run"
        if rows and missing_splits:
            status = "partial"

        out.append(
            {
                "setting_label": expected["setting_label"],
                "row_label": expected["row_label"],
                "method_id": expected["method_id"],
                "role": expected["role"],
                "requirement": expected["requirement"],
                "status": status,
                "completed_splits": "/".join(completed_splits),
                "missing_splits": "/".join(missing_splits),
                "successes": "" if episodes == 0 else successes,
                "episodes": "" if episodes == 0 else episodes,
                "success_rate": "" if episodes == 0 else f"{successes / episodes:.3f}",
            }
        )
    return out


def build_report(rows: list[dict[str, object]]) -> str:
    required = [row for row in rows if row["requirement"] == "required_branch_selection"]
    optional = [row for row in rows if row["requirement"] == "optional_diagnostic"]
    required_complete = sum(row["status"] == "complete" for row in required)
    optional_run = sum(row["status"] != "optional_not_run" for row in optional)

    lines = [
        "# v0.2 Fresh Baseline Coverage Audit",
        "",
        "This audit separates rows required for the frozen v0.2 branch-selection claim from optional diagnostic controls.",
        "It is evidence accounting only; it does not introduce new endpoint data.",
        "",
        "## Summary",
        "",
        f"- Required branch-selection rows complete: `{required_complete}/{len(required)}`.",
        f"- Optional diagnostic rows run in the fresh five-split gate: `{optional_run}/{len(optional)}`.",
        "- The current v0.2 fresh-gate claim is a branch-selection comparison over selected, positive-only, weighted, and v0.1 fixed branches.",
        "- Fresh all-demo and all-positive rows would be useful diagnostic controls, but they are not required for the current validated branch-selection claim and should not be implied as completed fresh-gate evidence.",
        "",
        "## Row Coverage",
        "",
    ]
    columns = [
        "setting_label",
        "row_label",
        "requirement",
        "status",
        "completed_splits",
        "missing_splits",
        "successes",
        "episodes",
        "success_rate",
    ]
    lines.extend(markdown_table(rows, columns))
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A3 now closes the required v0.1 fixed-branch objection for the fresh five-split Can/Lift gate.",
            "- The paper should describe the fresh gate as a complete selected-vs-strong-baseline/v0.1 audit, not as a full SOTA leaderboard with all possible diagnostic controls.",
            "- If more GPU budget is spent, the highest-value optional fresh rows are all-demo and all-positive oracle controls, clearly labeled as diagnostics.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir or args.root / "tables"
    rows = summarize_rows(args.root, [str(seed) for seed in args.split_seeds])
    write_csv(
        out_dir / "v02_fresh_baseline_coverage.csv",
        rows,
        [
            "setting_label",
            "row_label",
            "method_id",
            "role",
            "requirement",
            "status",
            "completed_splits",
            "missing_splits",
            "successes",
            "episodes",
            "success_rate",
        ],
    )
    report_path = out_dir / "v02_fresh_baseline_coverage_REPORT.md"
    report_path.write_text(build_report(rows), encoding="utf-8")
    print(f"wrote {out_dir / 'v02_fresh_baseline_coverage.csv'}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
