#!/usr/bin/env python3
"""Summarize Candidate H after the Candidate G fresh-Can mild-tail failure."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BREAKTHROUGH = ROOT / "results" / "candidate_breakthrough"
PREFLIGHT = ROOT / "results" / "candidate_g_fresh_preflight"
MILD_TAIL_FRACTION_MAX = 0.03


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def metric_success(path: Path) -> tuple[int, int, float]:
    rows = read_csv(path)
    if len(rows) != 1:
        raise ValueError(f"{path}: expected one metric row")
    episodes = int(rows[0]["eval_episodes"])
    rate = float(rows[0]["success_rate"])
    return int(round(rate * episodes)), episodes, float(rows[0]["avg_len"])


def candidate_h_choice(task: str, below_count: int, below_fraction: float) -> str:
    if task == "can_paired":
        if below_fraction >= MILD_TAIL_FRACTION_MAX:
            return "weighted_bc"
        return "candidate_e_gate"
    if task == "lift_mg":
        if below_count == 0:
            return "positive_only_nn"
        if below_fraction < MILD_TAIL_FRACTION_MAX:
            return "triage_bc"
        return "weighted_bc"
    raise ValueError(task)


def fresh_rows() -> list[dict[str, object]]:
    rows = []
    for row in read_csv(PREFLIGHT / "candidate_g_fresh_preflight_summary.csv"):
        below_count = int(row["below_count"])
        below_fraction = float(row["below_fraction"])
        h_choice = candidate_h_choice(row["task"], below_count, below_fraction)
        rows.append(
            {
                "task": row["task"],
                "split_seed": int(row["split_seed"]),
                "below_count": below_count,
                "below_fraction": below_fraction,
                "candidate_g_choice": row["candidate_g_choice"],
                "candidate_h_choice": h_choice,
                "support_method_for_h": "positive_only_nn" if h_choice == "candidate_e_gate" else h_choice,
                "g_support_hp": int(row["branch_hidden_positive"]),
                "g_support_bad": int(row["branch_hidden_bad"]),
                "note": "H differs from G" if h_choice != row["candidate_g_choice"] else "",
            }
        )
    return rows


def completed_totals() -> dict[str, int]:
    g_rows = read_csv(BREAKTHROUGH / "candidate_g_tail_severity_router_summary.csv")
    combined = next(row for row in g_rows if row["task"] == "combined" and row["split"] == "total")
    can = next(row for row in g_rows if row["task"] == "can40" and row["split"] == "total")
    lift = next(row for row in g_rows if row["task"] == "lift_mg" and row["split"] == "total")
    return {
        "can_candidate": int(can["candidate_success"]),
        "can_best": int(can["best_baseline"]),
        "lift_candidate": int(lift["candidate_success"]),
        "lift_best": int(lift["best_baseline"]),
        "combined_candidate": int(combined["candidate_success"]),
        "combined_best": int(combined["best_baseline"]),
    }


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def fresh_table(rows: list[dict[str, object]]) -> list[str]:
    lines = [
        "| task | split | #<thr | frac<thr | Candidate G | Candidate H | note |",
        "| --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {task} | {split} | {below} | {frac} | {g} | {h} | {note} |".format(
                task=row["task"],
                split=row["split_seed"],
                below=row["below_count"],
                frac=fmt(row["below_fraction"]),
                g=row["candidate_g_choice"],
                h=row["candidate_h_choice"],
                note=row["note"],
            )
        )
    return lines


def main() -> None:
    rows = fresh_rows()
    totals = completed_totals()
    triage_success, triage_episodes, triage_len = metric_success(
        PREFLIGHT / "can707_triage_epoch200_eval20" / "metrics.csv"
    )
    positive_success, positive_episodes, positive_len = metric_success(
        PREFLIGHT / "can707_positive_epoch200_eval20" / "metrics.csv"
    )

    csv_path = PREFLIGHT / "candidate_h_task_aware_tail_fresh_preflight.csv"
    write_csv(
        csv_path,
        rows,
        [
            "task",
            "split_seed",
            "below_count",
            "below_fraction",
            "candidate_g_choice",
            "candidate_h_choice",
            "support_method_for_h",
            "g_support_hp",
            "g_support_bad",
            "note",
        ],
    )

    report_path = PREFLIGHT / "candidate_h_task_aware_tail_REPORT.md"
    lines = [
        "# Candidate H Task-Aware Tail Router",
        "",
        "Candidate H is a response to the first fresh Candidate G endpoint smoke.",
        "It keeps Candidate G's Lift interpretation but changes Can mild-tail",
        "handling:",
        "",
        "- Can 40p/80b: no or mild low tail uses Candidate E's clean anchor;",
        "- Can 40p/80b: severe low tail (`below_fraction >= 0.03`) uses weighted BC;",
        "- Lift MG: no tail uses positive-only, mild tail uses triage, severe tail",
        "  uses weighted BC.",
        "",
        "This is a discovery candidate, not a paper claim, because it was proposed",
        "after seeing the fresh Can 707 smoke.",
        "",
        "## Completed-Row Assembly",
        "",
        f"- Can: `{totals['can_candidate']}/250` versus completed oracle `{totals['can_best']}/250`.",
        f"- Lift: `{totals['lift_candidate']}/250` versus completed oracle `{totals['lift_best']}/250`.",
        f"- Combined: `{totals['combined_candidate']}/500` versus completed oracle `{totals['combined_best']}/500`.",
        "",
        "Candidate H is identical to Candidate G on the completed Can+Lift rows,",
        "because the completed Can rows had no mild-tail case.",
        "",
        "## Fresh Support Preflight",
        "",
        *fresh_table(rows),
        "",
        "## Can 707 Endpoint Smoke",
        "",
        f"- Candidate G selected triage: `{triage_success}/{triage_episodes}`",
        f"  success, avg length `{triage_len:.1f}`.",
        f"- Clean positive anchor lower bound, positive-only: `{positive_success}/{positive_episodes}`",
        f"  success, avg length `{positive_len:.1f}`.",
        "- This single fresh split argues against task-agnostic mild-tail triage on",
        "  Can; the next validation should freeze Candidate H before any broader",
        "  endpoint matrix.",
        "",
        "## Artifacts",
        "",
        f"- Fresh preflight CSV: `{csv_path.relative_to(ROOT)}`.",
        "- Candidate G triage eval: `results/candidate_g_fresh_preflight/can707_triage_epoch200_eval20/REPORT.md`.",
        "- Positive-only eval: `results/candidate_g_fresh_preflight/can707_positive_epoch200_eval20/REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
