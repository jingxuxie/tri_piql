#!/usr/bin/env python3
"""Assemble the next tail-severity router candidate from completed rows."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
N_EPISODES = 50
MILD_TAIL_FRACTION_MAX = 0.03
SENSITIVITY_CUTOFFS = [0.0, 0.02, 0.025, 0.026, 0.03, 0.04, 0.05, 0.051, 0.06]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_int(value: str) -> int:
    return int(float(value))


def fmt(value: object) -> str:
    if value == "":
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def choose_tail_severity(
    below_count: int,
    below_fraction: float,
    *,
    no_tail_choice: str,
    mild_cutoff: float = MILD_TAIL_FRACTION_MAX,
) -> str:
    if below_count == 0:
        return no_tail_choice
    if below_fraction < mild_cutoff:
        return "triage"
    return "weighted"


def can_rows(mild_cutoff: float = MILD_TAIL_FRACTION_MAX) -> list[dict[str, object]]:
    rows = []
    for row in read_csv(OUT / "candidate_f_anchor_calibration_first20_summary.csv"):
        if row["split"] == "total":
            continue
        split = int(row["split"])
        selected_count = to_int(row["selected_count"])
        below_count = to_int(row["selected_prob_below_calibrated_threshold"])
        below_fraction = below_count / selected_count
        candidate_e_50 = to_int(row["candidate_e_50"]) if row["candidate_e_50"] else to_int(row["positive_50"])
        values = {
            "candidate_e_gate": candidate_e_50,
            "weighted": to_int(row["weighted_50"]),
            "triage": to_int(row["triage_50"]),
        }
        choice = choose_tail_severity(
            below_count,
            below_fraction,
            no_tail_choice="candidate_e_gate",
            mild_cutoff=mild_cutoff,
        )
        rows.append(
            {
                "task": "can40",
                "split": split,
                "selected_count": selected_count,
                "below_count": below_count,
                "below_fraction": below_fraction,
                "tail_severity_choice": choice,
                "candidate_success": values[choice],
                "positive": to_int(row["positive_50"]),
                "weighted": to_int(row["weighted_50"]),
                "triage": to_int(row["triage_50"]),
                "best_baseline": to_int(row["best_baseline_50"]),
                "delta_vs_best": values[choice] - to_int(row["best_baseline_50"]),
                "branch_note": "no-tail uses Candidate E initial-distance gate",
            }
        )
    return rows


def lift_rows(mild_cutoff: float = MILD_TAIL_FRACTION_MAX) -> list[dict[str, object]]:
    rows = []
    for row in read_csv(OUT / "candidate_f_lift_transfer_audit.csv"):
        if row["split"] == "total":
            continue
        split = int(row["split"])
        below_count = to_int(row["below_calibrated_threshold"])
        below_fraction = float(row["below_calibrated_fraction"])
        values = {
            "positive": to_int(row["positive"]),
            "weighted": to_int(row["weighted"]),
            "triage": to_int(row["triage"]),
        }
        choice = choose_tail_severity(
            below_count,
            below_fraction,
            no_tail_choice="positive",
            mild_cutoff=mild_cutoff,
        )
        rows.append(
            {
                "task": "lift_mg",
                "split": split,
                "selected_count": to_int(row["selected_count"]),
                "below_count": below_count,
                "below_fraction": below_fraction,
                "tail_severity_choice": choice,
                "candidate_success": values[choice],
                "positive": values["positive"],
                "weighted": values["weighted"],
                "triage": values["triage"],
                "best_baseline": to_int(row["best_baseline"]),
                "delta_vs_best": values[choice] - to_int(row["best_baseline"]),
                "branch_note": "no-tail uses positive-only anchor",
            }
        )
    return rows


def add_totals(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    out = list(rows)
    for task in ["can40", "lift_mg"]:
        task_rows = [row for row in rows if row["task"] == task]
        out.append(total_row(task, task_rows, N_EPISODES * len(task_rows)))
    out.append(total_row("combined", rows, N_EPISODES * len(rows)))
    return out


def total_row(task: str, rows: list[dict[str, object]], denom: int) -> dict[str, object]:
    return {
        "task": task,
        "split": "total",
        "selected_count": "",
        "below_count": sum(int(row["below_count"]) for row in rows),
        "below_fraction": "",
        "tail_severity_choice": "",
        "candidate_success": sum(int(row["candidate_success"]) for row in rows),
        "positive": sum(int(row["positive"]) for row in rows),
        "weighted": sum(int(row["weighted"]) for row in rows),
        "triage": sum(int(row["triage"]) for row in rows),
        "best_baseline": sum(int(row["best_baseline"]) for row in rows),
        "delta_vs_best": sum(int(row["candidate_success"]) for row in rows)
        - sum(int(row["best_baseline"]) for row in rows),
        "branch_note": f"denom={denom}",
    }


def candidate_rows(mild_cutoff: float = MILD_TAIL_FRACTION_MAX) -> list[dict[str, object]]:
    return [*can_rows(mild_cutoff), *lift_rows(mild_cutoff)]


def sensitivity_rows() -> list[dict[str, object]]:
    rows = []
    for cutoff in SENSITIVITY_CUTOFFS:
        eval_rows = candidate_rows(cutoff)
        can_total = sum(int(row["candidate_success"]) for row in eval_rows if row["task"] == "can40")
        lift_total = sum(int(row["candidate_success"]) for row in eval_rows if row["task"] == "lift_mg")
        best_total = sum(int(row["best_baseline"]) for row in eval_rows)
        rows.append(
            {
                "mild_tail_fraction_max": cutoff,
                "can40_candidate": can_total,
                "lift_candidate": lift_total,
                "combined_candidate": can_total + lift_total,
                "combined_best_baseline": best_total,
                "delta_vs_combined_best": can_total + lift_total - best_total,
            }
        )
    return rows


def markdown_table(rows: list[dict[str, object]]) -> list[str]:
    lines = [
        "| task | split | #<thr | frac<thr | choice | candidate | best | delta |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        denom = 500 if row["task"] == "combined" else (250 if row["split"] == "total" else 50)
        lines.append(
            "| {task} | {split} | {below} | {frac} | {choice} | {cand}/{denom} | "
            "{best}/{denom} | {delta:+d} |".format(
                task=row["task"],
                split=row["split"],
                below=row["below_count"],
                frac=fmt(row["below_fraction"]),
                choice=row["tail_severity_choice"],
                cand=row["candidate_success"],
                best=row["best_baseline"],
                delta=int(row["delta_vs_best"]),
                denom=denom,
            )
        )
    return lines


def sensitivity_table(rows: list[dict[str, object]]) -> list[str]:
    lines = [
        "| mild cutoff | Can | Lift | combined | best | delta |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {cutoff:.3f} | {can}/250 | {lift}/250 | {combined}/500 | "
            "{best}/500 | {delta:+d} |".format(
                cutoff=float(row["mild_tail_fraction_max"]),
                can=row["can40_candidate"],
                lift=row["lift_candidate"],
                combined=row["combined_candidate"],
                best=row["combined_best_baseline"],
                delta=int(row["delta_vs_combined_best"]),
            )
        )
    return lines


def main() -> None:
    rows = candidate_rows()
    rows_with_totals = add_totals(rows)
    sensitivity = sensitivity_rows()

    summary_csv = OUT / "candidate_g_tail_severity_router_summary.csv"
    sensitivity_csv = OUT / "candidate_g_tail_severity_router_sensitivity.csv"
    fieldnames = [
        "task",
        "split",
        "selected_count",
        "below_count",
        "below_fraction",
        "tail_severity_choice",
        "candidate_success",
        "positive",
        "weighted",
        "triage",
        "best_baseline",
        "delta_vs_best",
        "branch_note",
    ]
    write_csv(summary_csv, rows_with_totals, fieldnames)
    write_csv(
        sensitivity_csv,
        sensitivity,
        [
            "mild_tail_fraction_max",
            "can40_candidate",
            "lift_candidate",
            "combined_candidate",
            "combined_best_baseline",
            "delta_vs_combined_best",
        ],
    )

    combined = next(row for row in rows_with_totals if row["task"] == "combined")
    can = next(row for row in rows_with_totals if row["task"] == "can40" and row["split"] == "total")
    lift = next(row for row in rows_with_totals if row["task"] == "lift_mg" and row["split"] == "total")

    report_path = OUT / "candidate_g_tail_severity_router_REPORT.md"
    lines = [
        "# Candidate G Tail-Severity Router",
        "",
        "This is a next-candidate assembly from completed endpoint rows only.",
        "It uses the same low-tail threshold as Candidate F:",
        "`0.5 * unlabeled_prob_mean`.",
        "",
        "Router rule:",
        "",
        "- no low-probability tail: use the clean positive anchor;",
        "- mild low tail (`below_fraction < 0.03`): use triage/hard support;",
        "- severe low tail: use weighted BC.",
        "",
        "For Can, the clean positive anchor is Candidate E's initial-distance gate.",
        "For Lift, the clean positive anchor is the positive-only policy.",
        "",
        *markdown_table(rows_with_totals),
        "",
        "## Read",
        "",
        f"- Candidate G reaches `{combined['candidate_success']}/500`, versus the",
        f"  completed per-split baseline oracle `{combined['best_baseline']}/500`.",
        f"- On Can 40p/80b it is identical to frozen Candidate F: `{can['candidate_success']}/250`",
        f"  versus baseline oracle `{can['best_baseline']}/250`.",
        f"- On Lift MG it matches the completed per-split baseline oracle:",
        f"  `{lift['candidate_success']}/250`.",
        "- This is not yet a paper claim. The `0.03` mild-tail cutoff is a new",
        "  hyperparameter discovered after inspecting completed Lift rows, so the",
        "  correct next step is a pre-registered/frozen endpoint check.",
        "",
        "## Mild-Cutoff Sensitivity",
        "",
        *sensitivity_table(sensitivity),
        "",
        "The best combined row is stable only for a narrow mild-cutoff band around",
        "`0.026` to `0.050` under the strict `< cutoff` rule. That is promising,",
        "but it is not enough to claim robust transfer without a fresh freeze.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
        f"- Sensitivity CSV: `{sensitivity_csv.relative_to(ROOT)}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
