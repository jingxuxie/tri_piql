from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_ROOT = Path("results/final_paper_v02")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=None)
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


def task_rows(root: Path) -> list[tuple[str, Path]]:
    return [
        ("Can 40p/80b", root / "tables" / "v02_fresh_can_endpoint_summary.csv"),
        ("Lift MG", root / "tables" / "v02_fresh_lift_endpoint_summary.csv"),
    ]


def summarize_task(setting_label: str, rows: list[dict[str, str]]) -> tuple[dict[str, object], list[dict[str, object]]]:
    selected_rows = [row for row in rows if row["method_role"] == "v02_selected"]
    split_ids = sorted({int(row["split_seed"]) for row in selected_rows})

    selected_success = sum(int(row["success_count"]) for row in selected_rows)
    selected_episodes = sum(int(row["eval_episodes"]) for row in selected_rows)
    selected_method = "+".join(sorted({row["method_id"] for row in selected_rows}))

    best_success = 0
    best_episodes = 0
    per_split_rows: list[dict[str, object]] = []
    losing_splits = 0
    tied_splits = 0
    winning_splits = 0
    best_methods: list[str] = []

    for split_seed in split_ids:
        split_rows = [row for row in rows if int(row["split_seed"]) == split_seed]
        selected = next(row for row in split_rows if row["method_role"] == "v02_selected")
        baselines = [
            row
            for row in split_rows
            if row["method_role"] != "v02_selected" and row["method_role"] != "oracle_control"
        ]
        best = max(baselines, key=lambda row: float(row["endpoint_success"]))
        best_methods.append(best["method_id"])
        best_success += int(best["success_count"])
        best_episodes += int(best["eval_episodes"])

        selected_rate = int(selected["success_count"]) / int(selected["eval_episodes"])
        best_rate = int(best["success_count"]) / int(best["eval_episodes"])
        margin = selected_rate - best_rate
        if margin > 0:
            winning_splits += 1
        elif margin < 0:
            losing_splits += 1
        else:
            tied_splits += 1

        per_split_rows.append(
            {
                "setting_label": setting_label,
                "split_seed": split_seed,
                "selected_method": selected["method_id"],
                "selected_success": selected["success_count"],
                "selected_episodes": selected["eval_episodes"],
                "best_baseline_method": best["method_id"],
                "best_baseline_success": best["success_count"],
                "best_baseline_episodes": best["eval_episodes"],
                "margin": f"{margin:+.3f}",
            }
        )

    selected_rate = selected_success / selected_episodes if selected_episodes else 0.0
    best_rate = best_success / best_episodes if best_episodes else 0.0
    summary = {
        "setting_label": setting_label,
        "selected_method": selected_method,
        "selected_success": selected_success,
        "selected_episodes": selected_episodes,
        "selected_rate": f"{selected_rate:.3f}",
        "best_baseline_success": best_success,
        "best_baseline_episodes": best_episodes,
        "best_baseline_rate": f"{best_rate:.3f}",
        "margin": f"{selected_rate - best_rate:+.3f}",
        "winning_splits": winning_splits,
        "tied_splits": tied_splits,
        "losing_splits": losing_splits,
        "best_baseline_methods": ",".join(best_methods),
    }
    return summary, per_split_rows


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    out = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return out


def build_report(summary_rows: list[dict[str, object]], per_split_rows: list[dict[str, object]]) -> str:
    lines = [
        "# v0.2 Fresh Can+Lift Endpoint Gate",
        "",
        "Combined endpoint read for the frozen `METHOD_FREEZE_V02.md` fresh-split gate.",
        "Rows use official Robomimic BC-RNN-GMM, epoch-200 checkpoints, and 50 valid-positive-start rollouts per split.",
        "",
        "## Aggregate Read",
        "",
    ]
    summary_columns = [
        "setting_label",
        "selected_method",
        "selected_success",
        "selected_episodes",
        "selected_rate",
        "best_baseline_success",
        "best_baseline_episodes",
        "best_baseline_rate",
        "margin",
        "winning_splits",
        "losing_splits",
    ]
    lines.extend(markdown_table(summary_rows, summary_columns))

    total_selected_success = sum(int(row["selected_success"]) for row in summary_rows)
    total_selected_episodes = sum(int(row["selected_episodes"]) for row in summary_rows)
    total_best_success = sum(int(row["best_baseline_success"]) for row in summary_rows)
    total_best_episodes = sum(int(row["best_baseline_episodes"]) for row in summary_rows)
    total_margin = total_selected_success / total_selected_episodes - total_best_success / total_best_episodes
    lines.extend(
        [
            "",
            f"- Combined selected rows: {total_selected_success}/{total_selected_episodes}.",
            f"- Combined best per-split non-oracle baselines: {total_best_success}/{total_best_episodes} (margin {total_margin:+.3f}).",
            "",
            "## Per-Split Read",
            "",
        ]
    )
    per_split_columns = [
        "setting_label",
        "split_seed",
        "selected_method",
        "selected_success",
        "selected_episodes",
        "best_baseline_method",
        "best_baseline_success",
        "best_baseline_episodes",
        "margin",
    ]
    lines.extend(markdown_table(per_split_rows, per_split_columns))
    lines.extend(["", "## Interpretation", ""])
    for row in summary_rows:
        winning_splits = int(row["winning_splits"])
        tied_splits = int(row["tied_splits"])
        losing_splits = int(row["losing_splits"])
        total_splits = winning_splits + tied_splits + losing_splits
        tie_word = "tie" if tied_splits == 1 else "ties"
        loss_word = "loss" if losing_splits == 1 else "losses"
        lines.append(
            "- "
            f"{row['setting_label']}: selected branch margin {row['margin']} "
            f"over the best per-split non-oracle baseline, with "
            f"{winning_splits}/{total_splits} winning splits, "
            f"{tied_splits} {tie_word}, and {losing_splits} {loss_word}."
        )
    lines.extend(
        [
            "- Treat the completed fresh gate as evidence for hidden-label-free branch selection, not as a claim that hard bad-aware support dominates weighted BC.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir or args.root / "tables"

    summary_rows: list[dict[str, object]] = []
    per_split_rows: list[dict[str, object]] = []
    for setting_label, path in task_rows(args.root):
        rows = read_csv(path)
        summary, splits = summarize_task(setting_label, rows)
        summary_rows.append(summary)
        per_split_rows.extend(splits)

    write_csv(
        out_dir / "v02_fresh_gate_summary.csv",
        summary_rows,
        [
            "setting_label",
            "selected_method",
            "selected_success",
            "selected_episodes",
            "selected_rate",
            "best_baseline_success",
            "best_baseline_episodes",
            "best_baseline_rate",
            "margin",
            "winning_splits",
            "tied_splits",
            "losing_splits",
            "best_baseline_methods",
        ],
    )
    write_csv(
        out_dir / "v02_fresh_gate_per_split.csv",
        per_split_rows,
        [
            "setting_label",
            "split_seed",
            "selected_method",
            "selected_success",
            "selected_episodes",
            "best_baseline_method",
            "best_baseline_success",
            "best_baseline_episodes",
            "margin",
        ],
    )
    report_path = out_dir / "v02_fresh_gate_REPORT.md"
    report_path.write_text(build_report(summary_rows, per_split_rows), encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
