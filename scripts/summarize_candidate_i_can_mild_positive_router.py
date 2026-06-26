#!/usr/bin/env python3
"""Summarize Candidate I and its fresh endpoint validation."""

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


def sum_int_column(path: Path, column: str) -> tuple[int, int]:
    rows = read_csv(path)
    return sum(int(float(row[column])) for row in rows), len(rows)


def candidate_i_choice(task: str, below_count: int, below_fraction: float) -> str:
    if task == "can_paired":
        if below_count == 0:
            return "candidate_e_gate"
        if below_fraction < MILD_TAIL_FRACTION_MAX:
            return "positive_only_nn"
        return "weighted_bc"
    if task == "lift_mg":
        if below_count == 0:
            return "positive_only_nn"
        if below_fraction < MILD_TAIL_FRACTION_MAX:
            return "triage_bc"
        return "weighted_bc"
    raise ValueError(task)


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


def fresh_rows() -> list[dict[str, object]]:
    rows = []
    for row in read_csv(PREFLIGHT / "candidate_g_fresh_preflight_summary.csv"):
        below_count = int(row["below_count"])
        below_fraction = float(row["below_fraction"])
        i_choice = candidate_i_choice(row["task"], below_count, below_fraction)
        rows.append(
            {
                "task": row["task"],
                "split_seed": int(row["split_seed"]),
                "below_count": below_count,
                "below_fraction": below_fraction,
                "candidate_g_choice": row["candidate_g_choice"],
                "candidate_h_choice": (
                    "weighted_bc"
                    if row["task"] == "can_paired" and below_fraction >= MILD_TAIL_FRACTION_MAX
                    else (
                        "candidate_e_gate"
                        if row["task"] == "can_paired"
                        else candidate_i_choice(row["task"], below_count, below_fraction)
                    )
                ),
                "candidate_i_choice": i_choice,
                "note": "I differs from H" if i_choice == "positive_only_nn" and row["task"] == "can_paired" else "",
            }
        )
    return rows


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def fresh_table(rows: list[dict[str, object]]) -> list[str]:
    lines = [
        "| task | split | #<thr | frac<thr | Candidate G | Candidate H | Candidate I | note |",
        "| --- | ---: | ---: | ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {task} | {split} | {below} | {frac} | {g} | {h} | {i} | {note} |".format(
                task=row["task"],
                split=row["split_seed"],
                below=row["below_count"],
                frac=fmt(row["below_fraction"]),
                g=row["candidate_g_choice"],
                h=row["candidate_h_choice"],
                i=row["candidate_i_choice"],
                note=row["note"],
            )
        )
    return lines


def endpoint_validation_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    def add(
        task: str,
        split_seed: int,
        method: str,
        selected_by_candidate_i: bool,
        report_dir: str,
        protocol: str,
    ) -> None:
        successes, episodes, avg_len = metric_success(PREFLIGHT / report_dir / "metrics.csv")
        rows.append(
            {
                "task": task,
                "split_seed": split_seed,
                "method": method,
                "selected_by_candidate_i": selected_by_candidate_i,
                "successes": successes,
                "episodes": episodes,
                "success_rate": successes / episodes,
                "avg_len": avg_len,
                "protocol": protocol,
                "report": f"results/candidate_g_fresh_preflight/{report_dir}/REPORT.md",
            }
        )

    add(
        "can_paired",
        707,
        "candidate_g_triage",
        False,
        "can707_triage_epoch200_eval20",
        "20 valid-positive starts",
    )
    add(
        "can_paired",
        707,
        "candidate_h_candidate_e_gate",
        False,
        "can707_candidate_e_gate_eval20",
        "20 valid-positive starts",
    )
    add(
        "can_paired",
        707,
        "positive_only_nn",
        True,
        "can707_positive_epoch200_eval20",
        "20 valid-positive starts",
    )
    add(
        "lift_mg",
        606,
        "triage_bc",
        True,
        "lift606_triage_epoch200_eval50",
        "50 valid-positive starts",
    )
    add(
        "lift_mg",
        606,
        "positive_only_nn",
        False,
        "lift606_positive_epoch200_eval50",
        "50 valid-positive starts",
    )
    add(
        "lift_mg",
        606,
        "weighted_bc",
        False,
        "lift606_weighted_epoch200_eval50",
        "50 valid-positive starts",
    )
    return rows


def endpoint_table(rows: list[dict[str, object]], task: str, split_seed: int) -> list[str]:
    lines = [
        "| method | Candidate I selected? | successes | avg len | protocol |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        if row["task"] != task or row["split_seed"] != split_seed:
            continue
        selected = "yes" if row["selected_by_candidate_i"] else "no"
        lines.append(
            "| {method} | {selected} | {successes}/{episodes} | {avg_len:.1f} | {protocol} |".format(
                method=row["method"],
                selected=selected,
                successes=row["successes"],
                episodes=row["episodes"],
                avg_len=row["avg_len"],
                protocol=row["protocol"],
            )
        )
    return lines


def main() -> None:
    totals = completed_totals()
    fresh = fresh_rows()
    endpoint_rows = endpoint_validation_rows()
    gate_open, gate_episodes = sum_int_column(
        PREFLIGHT / "can707_candidate_e_gate_eval20" / "episode_metrics.csv",
        "initial_gate_open",
    )

    csv_path = PREFLIGHT / "candidate_i_can_mild_positive_fresh_preflight.csv"
    write_csv(
        csv_path,
        fresh,
        [
            "task",
            "split_seed",
            "below_count",
            "below_fraction",
            "candidate_g_choice",
            "candidate_h_choice",
            "candidate_i_choice",
            "note",
        ],
    )

    endpoint_csv_path = PREFLIGHT / "candidate_i_fresh_endpoint_validation.csv"
    write_csv(
        endpoint_csv_path,
        endpoint_rows,
        [
            "task",
            "split_seed",
            "method",
            "selected_by_candidate_i",
            "successes",
            "episodes",
            "success_rate",
            "avg_len",
            "protocol",
            "report",
        ],
    )

    report_path = PREFLIGHT / "candidate_i_can_mild_positive_REPORT.md"
    lines = [
        "# Candidate I Can-Mild-Positive Tail Router",
        "",
        "**Status: rejected as a development candidate after fresh Lift 606",
        "validation.** Candidate I was a task-aware refinement after Can 707",
        "showed that both task-agnostic mild-tail triage and Can mild-tail",
        "Candidate E can lose to the positive-only anchor. Its retained Lift",
        "mild-tail triage branch then lost to positive-only on held-out Lift 606.",
        "",
        "Frozen candidate rule under test:",
        "",
        "- Can 40p/80b no tail: Candidate E initial-distance gate;",
        "- Can 40p/80b mild tail: positive-only NN;",
        "- Can 40p/80b severe tail (`below_fraction >= 0.03`): weighted BC;",
        "- Lift MG no tail: positive-only NN;",
        "- Lift MG mild tail: triage/hard support;",
        "- Lift MG severe tail: weighted BC.",
        "",
        "## Completed-Row Assembly",
        "",
        f"- Can: `{totals['can_candidate']}/250` versus completed oracle `{totals['can_best']}/250`.",
        f"- Lift: `{totals['lift_candidate']}/250` versus completed oracle `{totals['lift_best']}/250`.",
        f"- Combined: `{totals['combined_candidate']}/500` versus completed oracle `{totals['combined_best']}/500`.",
        "",
        "Candidate I is identical to Candidate G/H on the completed Can+Lift rows:",
        "completed Can has either no tail or severe tail, not a mild-tail case.",
        "This completed-row assembly is no longer enough for a method claim",
        "because fresh Lift mild-tail validation failed.",
        "",
        "## Fresh Preflight Choices",
        "",
        *fresh_table(fresh),
        "",
        "## Can 707 Endpoint Smoke",
        "",
        *endpoint_table(endpoint_rows, "can_paired", 707),
        "",
        f"- Candidate E opened its weighted fallback on `{gate_open}/{gate_episodes}` episodes. It rescued",
        "  some starts but lost more than it gained on this fresh mild-tail split.",
        "- Candidate I fixed this Can mild-tail failure by selecting positive-only.",
        "",
        "## Lift 606 Endpoint Validation",
        "",
        *endpoint_table(endpoint_rows, "lift_mg", 606),
        "",
        "- Candidate I selected triage on this retained Lift mild-tail case, but",
        "  positive-only was stronger by `5/50` successes and weighted was worse.",
        "- The smaller 20-episode smoke showed the same ordering between positive",
        "  and triage (`14/20` versus `13/20`), and the 50-episode endpoint widened",
        "  the gap.",
        "",
        "## Read",
        "",
        "- Candidate I should not be promoted or scaled as-is.",
        "- The failure is informative: old completed Lift mild-tail rows favored",
        "  triage, while fresh Lift 606 favors positive-only. A global task/tail",
        "  rule is unstable for Lift mild tails.",
        "- The next candidate should use a deployable episode-level gate or a new",
        "  score diagnostic for Lift mild-tail cases, rather than only changing the",
        "  global mild-tail branch.",
        "",
        "## Artifacts",
        "",
        f"- Fresh preflight CSV: `{csv_path.relative_to(ROOT)}`.",
        f"- Fresh endpoint validation CSV: `{endpoint_csv_path.relative_to(ROOT)}`.",
        "- Candidate E eval: `results/candidate_g_fresh_preflight/can707_candidate_e_gate_eval20/REPORT.md`.",
        "- Positive-only eval: `results/candidate_g_fresh_preflight/can707_positive_epoch200_eval20/REPORT.md`.",
        "- Triage eval: `results/candidate_g_fresh_preflight/can707_triage_epoch200_eval20/REPORT.md`.",
        "- Lift 606 triage eval: `results/candidate_g_fresh_preflight/lift606_triage_epoch200_eval50/REPORT.md`.",
        "- Lift 606 positive-only eval: `results/candidate_g_fresh_preflight/lift606_positive_epoch200_eval50/REPORT.md`.",
        "- Lift 606 weighted eval: `results/candidate_g_fresh_preflight/lift606_weighted_epoch200_eval50/REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
