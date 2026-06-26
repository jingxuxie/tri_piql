#!/usr/bin/env python3
"""Summarize Candidate F fresh Can first-20 smoke checks."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"

RUNS = [
    {
        "split": "606",
        "candidate_f_choice": "candidate_e_gate",
        "methods": {
            "positive_only_nn": OUT / "can606_positive_epoch200_eval20",
            "weighted_bc": OUT / "can606_weighted_epoch200_eval20",
            "candidate_e_gate": OUT / "can606_candidate_e_gate_eval20",
        },
    },
    {
        "split": "707",
        "candidate_f_choice": "weighted_bc",
        "methods": {
            "positive_only_nn": OUT / "can707_positive_epoch200_eval20",
            "weighted_bc": OUT / "can707_weighted_epoch200_eval20",
            "triage_bc": OUT / "can707_triage_epoch200_eval20",
            "candidate_e_gate": OUT / "can707_candidate_e_gate_eval20",
        },
    },
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize_metrics(path: Path) -> dict[str, object]:
    row = read_csv(path / "metrics.csv")[0]
    episodes = int(row["eval_episodes"])
    return {
        "successes": int(round(float(row["success_rate"]) * episodes)),
        "episodes": episodes,
        "avg_len": round(float(row["avg_len"]), 3),
    }


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def main() -> None:
    rows = []
    totals: dict[str, int] = {}
    total_episodes: dict[str, int] = {}
    for split_spec in RUNS:
        split = split_spec["split"]
        candidate_f_choice = split_spec["candidate_f_choice"]
        for method, run_dir in split_spec["methods"].items():
            metrics = summarize_metrics(run_dir)
            selected = method == candidate_f_choice
            row = {
                "split": split,
                "method": method,
                "candidate_f_selected": int(selected),
                "successes": metrics["successes"],
                "episodes": metrics["episodes"],
                "avg_len": metrics["avg_len"],
                "artifact": str(run_dir.relative_to(ROOT)),
            }
            rows.append(row)
            if selected:
                totals["candidate_f"] = totals.get("candidate_f", 0) + int(metrics["successes"])
                total_episodes["candidate_f"] = total_episodes.get("candidate_f", 0) + int(metrics["episodes"])
            totals[method] = totals.get(method, 0) + int(metrics["successes"])
            total_episodes[method] = total_episodes.get(method, 0) + int(metrics["episodes"])

    summary_rows = [
        {
            "method": method,
            "successes": successes,
            "episodes": total_episodes[method],
        }
        for method, successes in sorted(totals.items())
    ]
    summary_rows.sort(key=lambda row: (-int(row["successes"]), row["method"]))

    row_csv = OUT / "candidate_f_fresh_can_smokes_rows.csv"
    summary_csv = OUT / "candidate_f_fresh_can_smokes_summary.csv"
    report_path = OUT / "candidate_f_fresh_can_smokes_REPORT.md"
    write_csv(
        row_csv,
        rows,
        ["split", "method", "candidate_f_selected", "successes", "episodes", "avg_len", "artifact"],
    )
    write_csv(summary_csv, summary_rows, ["method", "successes", "episodes"])

    display_rows = [
        {
            **row,
            "successes": f"{row['successes']}/{row['episodes']}",
        }
        for row in rows
    ]
    display_summary = [
        {
            **row,
            "successes": f"{row['successes']}/{row['episodes']}",
        }
        for row in summary_rows
    ]
    lines = [
        "# Candidate F Fresh Can Smoke Checks",
        "",
        "**Status: neutral.** These first-20 held-out Can checks are useful for",
        "stress-testing the Can-only Candidate F story, but they do not yet",
        "strengthen it into a fresh validation claim.",
        "",
        "Candidate F choices under the frozen Can rule:",
        "",
        "- Can606 no-tail: Candidate E gate.",
        "- Can707 mild-tail: weighted BC.",
        "",
        "## Per-Split Rows",
        "",
        *table(display_rows, ["split", "method", "candidate_f_selected", "successes", "avg_len", "artifact"]),
        "",
        "## Two-Split First-20 Aggregate",
        "",
        *table(display_summary, ["method", "successes"]),
        "",
        "## Read",
        "",
        "- Candidate F ties positive-only over the two fresh Can first-20 smokes:",
        "  both are `31/40`.",
        "- The Can606 no-tail branch is neutral: Candidate E gate and positive-only",
        "  both reach `16/20`.",
        "- The Can707 mild-tail branch is also neutral: weighted BC and",
        "  positive-only both reach `15/20`; Candidate E is worse at `13/20` and",
        "  triage is worse at `10/20`.",
        "- This weakens the case for spending broad endpoint budget on Candidate F",
        "  as a high-impact fresh Can method. If continued, it should be a",
        "  predeclared Can-only validation matrix, not another ad hoc split.",
        "",
        "## Artifacts",
        "",
        f"- Row CSV: `{row_csv.relative_to(ROOT)}`.",
        f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
        "- Can606 report: `results/candidate_g_fresh_preflight/candidate_f_can606_fresh_smoke_REPORT.md`.",
        "- Can707 weighted eval: `results/candidate_g_fresh_preflight/can707_weighted_epoch200_eval20/REPORT.md`.",
        "- Can707 branch comparison: `results/candidate_g_fresh_preflight/candidate_i_can_mild_positive_REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
