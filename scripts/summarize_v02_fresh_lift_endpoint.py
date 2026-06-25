from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_ROOT = Path("results/final_paper_v02")
SELECTED_ID = "weighted_bc"
METHODS = [
    ("weighted_bc", "v02_selected"),
    ("positive_only_nn", "strong_baseline"),
    ("triage_bc", "v01_method"),
    ("bc_all_mixed", "mixed_log_baseline"),
    ("all_train_positive_oracle", "oracle_control"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--split-seeds", type=int, nargs="+", default=[101, 202, 303])
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def success_count(row: dict[str, str]) -> int:
    return int(round(float(row["success_rate"]) * int(float(row["eval_episodes"]))))


def train_counts(report_path: Path) -> tuple[str, str]:
    if not report_path.exists():
        return "", ""
    train_demo_count = ""
    selected_unlabeled = ""
    for line in report_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Train demos:"):
            train_demo_count = line.split("`", 2)[1]
        elif line.startswith("- Selected unlabeled demos:"):
            selected_unlabeled = line.split("`", 2)[1]
    return train_demo_count, selected_unlabeled


def collect_rows(root: Path, split_seeds: list[int]) -> list[dict[str, object]]:
    rows = []
    for split_seed in split_seeds:
        for method_id, method_role in METHODS:
            run_root = root / "per_seed" / f"lift_mg_mg_sparse_split{split_seed}_{method_id}_policy0"
            metrics_path = run_root / "eval" / "metrics.csv"
            if not metrics_path.exists():
                continue
            metrics = read_csv(metrics_path)[0]
            train_demo_count, selected_unlabeled = train_counts(run_root / "REPORT.md")
            rows.append(
                {
                    "split_seed": split_seed,
                    "method_id": method_id,
                    "method_role": method_role,
                    "endpoint_success": f"{float(metrics['success_rate']):.3f}",
                    "success_count": success_count(metrics),
                    "eval_episodes": int(float(metrics["eval_episodes"])),
                    "avg_len": f"{float(metrics['avg_len']):.1f}",
                    "train_demo_count": train_demo_count,
                    "selected_unlabeled": selected_unlabeled,
                    "checkpoint": metrics["checkpoint"],
                    "metrics_path": str(metrics_path),
                }
            )
    return rows


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def build_report(rows: list[dict[str, object]]) -> str:
    lines = [
        "# v0.2 Fresh Lift MG Endpoint Summary",
        "",
        "Fresh-split endpoint rows for the frozen `METHOD_FREEZE_V02.md` Lift branch.",
        "The frozen router selects weighted BC on Lift-like broad-coverage rows.",
        "",
    ]
    if not rows:
        lines.append("No endpoint metrics found.")
        return "\n".join(lines) + "\n"

    columns = [
        "split_seed",
        "method_id",
        "method_role",
        "success_count",
        "eval_episodes",
        "endpoint_success",
        "train_demo_count",
        "selected_unlabeled",
    ]
    lines.extend(markdown_table(rows, columns))

    lines.extend(["", "## Aggregate Read", ""])
    selected_rows = [row for row in rows if row["method_id"] == SELECTED_ID]
    if selected_rows:
        selected_successes = sum(int(row["success_count"]) for row in selected_rows)
        selected_episodes = sum(int(row["eval_episodes"]) for row in selected_rows)
        best_successes = 0
        best_episodes = 0
        for split_seed in sorted({int(row["split_seed"]) for row in selected_rows}):
            split_rows = [row for row in rows if int(row["split_seed"]) == split_seed]
            baselines = [
                row
                for row in split_rows
                if row["method_role"] != "oracle_control" and row["method_id"] != SELECTED_ID
            ]
            if not baselines:
                continue
            best = max(baselines, key=lambda row: float(row["endpoint_success"]))
            best_successes += int(best["success_count"])
            best_episodes += int(best["eval_episodes"])
        lines.append(f"- Completed v0.2 selected Lift rows: {selected_successes}/{selected_episodes}.")
        if best_episodes:
            margin = selected_successes / selected_episodes - best_successes / best_episodes
            lines.append(
                f"- Best completed non-oracle baseline per split: {best_successes}/{best_episodes} "
                f"(margin {margin:+.3f})."
            )

    lines.extend(["", "## Per-Split Read", ""])
    for split_seed in sorted({int(row["split_seed"]) for row in rows}):
        split_rows = [row for row in rows if int(row["split_seed"]) == split_seed]
        selected = next((row for row in split_rows if row["method_id"] == SELECTED_ID), None)
        baselines = [
            row
            for row in split_rows
            if row["method_role"] != "oracle_control" and row["method_id"] != SELECTED_ID
        ]
        if selected is None:
            lines.append(f"- Split {split_seed}: selected weighted row is missing.")
        elif not baselines:
            lines.append(f"- Split {split_seed}: selected weighted row exists, but no non-oracle baselines are complete.")
        else:
            best = max(baselines, key=lambda row: float(row["endpoint_success"]))
            margin = float(selected["endpoint_success"]) - float(best["endpoint_success"])
            lines.append(
                f"- Split {split_seed}: selected `{selected['method_id']}` is "
                f"{selected['success_count']}/{selected['eval_episodes']} versus best completed non-oracle baseline "
                f"`{best['method_id']}` at {best['success_count']}/{best['eval_episodes']} "
                f"(margin {margin:+.3f})."
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir or args.root / "tables"
    rows = collect_rows(args.root, args.split_seeds)
    fieldnames = [
        "split_seed",
        "method_id",
        "method_role",
        "endpoint_success",
        "success_count",
        "eval_episodes",
        "avg_len",
        "train_demo_count",
        "selected_unlabeled",
        "checkpoint",
        "metrics_path",
    ]
    write_csv(out_dir / "v02_fresh_lift_endpoint_summary.csv", rows, fieldnames)
    (out_dir / "v02_fresh_lift_endpoint_REPORT.md").write_text(build_report(rows), encoding="utf-8")
    print(f"wrote {out_dir / 'v02_fresh_lift_endpoint_REPORT.md'}")


if __name__ == "__main__":
    main()
