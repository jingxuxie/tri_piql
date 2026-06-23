from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np


STEP_SUFFIX_RE = re.compile(r"_step\d+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_can_gmm_summary"))
    return parser.parse_args()


def load_run(run_dir: Path) -> list[dict]:
    metrics_path = run_dir / "metrics.csv"
    diagnostics_path = run_dir / "diagnostics.json"
    if not metrics_path.exists() or not diagnostics_path.exists():
        raise FileNotFoundError(f"missing metrics or diagnostics in {run_dir}")
    diagnostics = json.loads(diagnostics_path.read_text(encoding="utf-8"))
    validation_enabled = bool((diagnostics.get("gmm_validation") or {}).get("enabled", False))
    rows = []
    with metrics_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            raw_method = row["method"]
            rows.append(
                {
                    "run_dir": str(run_dir),
                    "method": STEP_SUFFIX_RE.sub("", raw_method),
                    "raw_method": raw_method,
                    "success_rate": float(row["success_rate"]),
                    "avg_return": float(row["avg_return"]),
                    "avg_len": float(row["avg_len"]),
                    "source": diagnostics.get("source", ""),
                    "split_path": diagnostics.get("split_path", ""),
                    "seed": diagnostics.get("seed"),
                    "steps": diagnostics.get("steps"),
                    "checkpoint_step": int(row.get("checkpoint_step") or diagnostics.get("steps") or 0),
                    "source_transition_count": diagnostics.get("source_transition_count"),
                    "top_unlabeled_demos": diagnostics.get("top_unlabeled_demos"),
                    "selection_rule": (diagnostics.get("selection_diagnostics") or {}).get("selection_rule", ""),
                    "checkpoint_selection_metric": (
                        diagnostics.get("gmm_checkpoint_selection_metric", "") if validation_enabled else ""
                    ),
                    "selected_unlabeled_demo_count": len(diagnostics.get("selected_unlabeled_demos") or []),
                    "selected_hidden_positive_demos": diagnostics.get("selected_hidden_positive_demos", 0),
                    "selected_unlabeled_transitions": diagnostics.get("selected_unlabeled_transitions", 0),
                    "feature_mode": diagnostics.get("feature_mode", "obs"),
                    "eval_episodes": diagnostics.get("eval_episodes"),
                    "eval_horizon": diagnostics.get("eval_horizon"),
                }
            )
    return rows


def summarize(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        key = (
            row["source"],
            row["method"],
            row["split_path"],
            row["checkpoint_step"],
            row["top_unlabeled_demos"],
            row["selection_rule"],
            row["checkpoint_selection_metric"],
            row["feature_mode"],
            row["eval_episodes"],
            row["eval_horizon"],
        )
        groups[key].append(row)

    summary = []
    def sort_key(item):
        (
            source,
            method,
            split_path,
            checkpoint_step,
            top_k,
            selection_rule,
            checkpoint_selection_metric,
            feature_mode,
            eval_episodes,
            eval_horizon,
        ) = item[0]
        return (
            str(source),
            str(method),
            str(split_path),
            -1 if checkpoint_step is None else int(checkpoint_step),
            -1 if top_k is None else int(top_k),
            str(selection_rule),
            str(checkpoint_selection_metric),
            str(feature_mode),
            -1 if eval_episodes is None else int(eval_episodes),
            -1 if eval_horizon is None else int(eval_horizon),
        )

    for (
        source,
        method,
        split_path,
        checkpoint_step,
        top_k,
        selection_rule,
        checkpoint_selection_metric,
        feature_mode,
        eval_episodes,
        eval_horizon,
    ), group in sorted(groups.items(), key=sort_key):
        success = np.asarray([row["success_rate"] for row in group], dtype=np.float64)
        returns = np.asarray([row["avg_return"] for row in group], dtype=np.float64)
        lengths = np.asarray([row["avg_len"] for row in group], dtype=np.float64)
        hidden_pos = np.asarray([row["selected_hidden_positive_demos"] for row in group], dtype=np.float64)
        selected_demo_count = np.asarray([row["selected_unlabeled_demo_count"] for row in group], dtype=np.float64)
        selected_transitions = np.asarray([row["selected_unlabeled_transitions"] for row in group], dtype=np.float64)
        max_steps = np.asarray([row["steps"] for row in group if row["steps"] is not None], dtype=np.int64)
        source_transitions = np.asarray(
            [row["source_transition_count"] for row in group if row["source_transition_count"] is not None],
            dtype=np.float64,
        )
        summary.append(
            {
                "source": source,
                "method": method,
                "split_path": split_path,
                "max_steps_max": int(max_steps.max()) if max_steps.size else None,
                "max_steps_values": ",".join(str(int(value)) for value in max_steps) if max_steps.size else "",
                "checkpoint_step": checkpoint_step,
                "source_transition_count_mean": float(source_transitions.mean()) if source_transitions.size else 0.0,
                "source_transition_count_values": ",".join(f"{value:.0f}" for value in source_transitions),
                "top_unlabeled_demos": top_k,
                "selection_rule": selection_rule,
                "checkpoint_selection_metric": checkpoint_selection_metric,
                "feature_mode": feature_mode,
                "eval_episodes": eval_episodes,
                "eval_horizon": eval_horizon,
                "n_runs": len(group),
                "seeds": ",".join(str(row["seed"]) for row in group),
                "success_mean": float(success.mean()),
                "success_values": ",".join(f"{value:.3f}" for value in success),
                "return_mean": float(returns.mean()),
                "length_mean": float(lengths.mean()),
                "selected_unlabeled_demo_count_mean": float(selected_demo_count.mean()),
                "selected_hidden_positive_mean": float(hidden_pos.mean()),
                "selected_unlabeled_transitions_mean": float(selected_transitions.mean()),
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict]) -> str:
    lines = [
        "| source | method | selector | ckpt metric | features | max steps | ckpt | train transitions | selected demos | eval eps | runs | seeds | success mean | success values | hidden-positive demos |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|",
    ]
    for row in rows:
        selector = row["selection_rule"] or ("fixed_top" if row["selected_unlabeled_demo_count_mean"] else "")
        lines.append(
            f"| {row['source']} | {row['method']} | {selector} | {row['checkpoint_selection_metric']} | "
            f"{row['feature_mode']} | {row['max_steps_max']} | "
            f"{row['checkpoint_step']} | {row['source_transition_count_mean']:.0f} | {row['selected_unlabeled_demo_count_mean']:.1f} | "
            f"{row['eval_episodes']} | {row['n_runs']} | {row['seeds']} | "
            f"{row['success_mean']:.3f} | {row['success_values']} | "
            f"{row['selected_hidden_positive_mean']:.1f} |"
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for run_dir in args.run_dirs:
        rows.extend(load_run(run_dir))
    summary = summarize(rows)
    write_csv(args.out_dir / "all_metrics.csv", rows)
    write_csv(args.out_dir / "summary.csv", summary)

    report = [
        "# Robomimic GMM Run Summary",
        "",
        f"Run directories: `{len(args.run_dirs)}`.",
        "",
        "## Aggregate",
        "",
        markdown_table(summary),
        "",
        "## Interpretation",
        "",
        "- This summary aggregates completed smoke runs only; it does not rerun experiments.",
        "- Treat low-episode or single-seed rows as triage evidence rather than final benchmark numbers.",
    ]
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
