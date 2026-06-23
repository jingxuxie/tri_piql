from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Callable

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--title", default="Robomimic Checkpoint Selection Rule Summary")
    parser.add_argument("--notes", action="append", default=[])
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str | int | float]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def method_name(run: str) -> str:
    return run.rsplit("_seed", 1)[0]


def mean(values: list[float]) -> float:
    return float(np.mean(values)) if values else float("nan")


def fmt(value: float, digits: int = 3) -> str:
    if np.isnan(value):
        return "nan"
    return f"{value:.{digits}f}"


def markdown_table(rows: list[dict[str, str | int | float]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        rendered = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                rendered.append(fmt(value))
            else:
                rendered.append(str(value))
        lines.append("| " + " | ".join(rendered) + " |")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    score_rows = read_csv(args.analysis_dir / "checkpoint_scores.csv")

    by_run_epoch: dict[tuple[str, int], dict[str, dict[str, str]]] = defaultdict(dict)
    rollout_by_run_epoch: dict[tuple[str, int], float] = {}
    for row in score_rows:
        run = row["run"]
        epoch = int(row["checkpoint_epoch"])
        by_run_epoch[(run, epoch)][row["filter_name"]] = row
        rollout_by_run_epoch[(run, epoch)] = float(row["rollout_success"])

    def ll(filter_name: str) -> Callable[[dict[str, dict[str, str]]], float]:
        return lambda filters: float(filters[filter_name]["log_likelihood"])

    rules: dict[str, Callable[[dict[str, dict[str, str]]], float]] = {
        "train_support_ll": ll("train_support"),
        "valid_positive_ll": ll("valid_positive"),
        "valid_negative_ll": ll("valid_negative"),
        "labeled_positive_ll": ll("labeled_positive"),
        "labeled_negative_ll": ll("labeled_negative"),
        "valid_pos_minus_neg_ll": lambda filters: float(filters["valid_positive"]["log_likelihood"])
        - float(filters["valid_negative"]["log_likelihood"]),
        "labeled_pos_minus_neg_ll": lambda filters: float(filters["labeled_positive"]["log_likelihood"])
        - float(filters["labeled_negative"]["log_likelihood"]),
        "valid_joint_pos_neg_ll": lambda filters: float(filters["valid_positive"]["log_likelihood"])
        + float(filters["valid_negative"]["log_likelihood"]),
        "labeled_joint_pos_neg_ll": lambda filters: float(filters["labeled_positive"]["log_likelihood"])
        + float(filters["labeled_negative"]["log_likelihood"]),
    }

    required_filters = {
        "train_support_ll": ["train_support"],
        "valid_positive_ll": ["valid_positive"],
        "valid_negative_ll": ["valid_negative"],
        "labeled_positive_ll": ["labeled_positive"],
        "labeled_negative_ll": ["labeled_negative"],
        "valid_pos_minus_neg_ll": ["valid_positive", "valid_negative"],
        "labeled_pos_minus_neg_ll": ["labeled_positive", "labeled_negative"],
        "valid_joint_pos_neg_ll": ["valid_positive", "valid_negative"],
        "labeled_joint_pos_neg_ll": ["labeled_positive", "labeled_negative"],
    }

    selection_rows: list[dict[str, str | int | float]] = []
    runs = sorted({run for run, _epoch in by_run_epoch})
    for run in runs:
        run_candidates = [(epoch, filters) for (candidate_run, epoch), filters in by_run_epoch.items() if candidate_run == run]
        rollout_best_epoch, rollout_best_success = max(
            ((epoch, rollout_by_run_epoch[(run, epoch)]) for epoch, _filters in run_candidates),
            key=lambda item: item[1],
        )
        for rule_name, rule_fn in rules.items():
            needed = required_filters[rule_name]
            candidates = [
                (epoch, rule_fn(filters), rollout_by_run_epoch[(run, epoch)])
                for epoch, filters in run_candidates
                if all(name in filters for name in needed)
            ]
            if not candidates:
                continue
            selected_epoch, selected_score, selected_success = max(candidates, key=lambda item: item[1])
            selection_rows.append(
                {
                    "run": run,
                    "method": method_name(run),
                    "rule": rule_name,
                    "selected_epoch": selected_epoch,
                    "selected_score": selected_score,
                    "selected_rollout_success": selected_success,
                    "rollout_best_epoch": rollout_best_epoch,
                    "rollout_best_success": rollout_best_success,
                }
            )
    write_csv(args.analysis_dir / "selection_rule_summary.csv", selection_rows)

    aggregate_rows: list[dict[str, str | int | float]] = []
    for rule_name in rules:
        for method in sorted({str(row["method"]) for row in selection_rows}):
            rows = [row for row in selection_rows if row["rule"] == rule_name and row["method"] == method]
            if rows:
                aggregate_rows.append(
                    {
                        "rule": rule_name,
                        "method": method,
                        "mean_selected_success": mean([float(row["selected_rollout_success"]) for row in rows]),
                        "mean_rollout_best_success": mean([float(row["rollout_best_success"]) for row in rows]),
                    }
                )
    write_csv(args.analysis_dir / "selection_rule_aggregate.csv", aggregate_rows)

    fixed_rows: list[dict[str, str | int | float]] = []
    for method in sorted({method_name(run) for run in runs}):
        method_runs = [run for run in runs if method_name(run) == method]
        epochs = sorted({epoch for run in method_runs for candidate_run, epoch in by_run_epoch if candidate_run == run})
        for epoch in epochs:
            successes = [
                rollout_by_run_epoch[(run, epoch)]
                for run in method_runs
                if (run, epoch) in rollout_by_run_epoch and not np.isnan(rollout_by_run_epoch[(run, epoch)])
            ]
            if successes:
                fixed_rows.append({"method": method, "epoch": epoch, "mean_success": mean(successes)})
        best_successes = []
        for run in method_runs:
            run_successes = [
                rollout_by_run_epoch[(candidate_run, epoch)]
                for candidate_run, epoch in rollout_by_run_epoch
                if candidate_run == run
            ]
            best_successes.append(max(run_successes))
        fixed_rows.append({"method": method, "epoch": "oracle_best", "mean_success": mean(best_successes)})
    write_csv(args.analysis_dir / "fixed_epoch_summary.csv", fixed_rows)

    report = [
        f"# {args.title}",
        "",
    ]
    if args.notes:
        report.extend(["## Notes", ""])
        report.extend([f"- {note}" for note in args.notes])
        report.append("")
    report.extend(
        [
            "## Fixed Epochs",
            "",
            markdown_table(fixed_rows, ["method", "epoch", "mean_success"]),
            "",
            "## Rule Aggregate",
            "",
            markdown_table(aggregate_rows, ["rule", "method", "mean_selected_success", "mean_rollout_best_success"]),
            "",
            "## Per-Run Selections",
            "",
            markdown_table(
                selection_rows,
                [
                    "run",
                    "rule",
                    "selected_epoch",
                    "selected_rollout_success",
                    "rollout_best_epoch",
                    "rollout_best_success",
                ],
            ),
            "",
            "## Files",
            "",
            "- `selection_rule_summary.csv`: selected checkpoint per run and rule.",
            "- `selection_rule_aggregate.csv`: mean selected rollout success by method and rule.",
            "- `fixed_epoch_summary.csv`: fixed-epoch and oracle-best rollout means.",
        ]
    )
    (args.analysis_dir / "RULE_SUMMARY.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.analysis_dir / 'RULE_SUMMARY.md'}")


if __name__ == "__main__":
    main()
