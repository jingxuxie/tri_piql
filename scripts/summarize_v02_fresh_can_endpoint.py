from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_ROOT = Path("results/final_paper_v02")
UNION_TAG = "positive_nn_risk_union_top40"
BASELINES = [
    ("positive_only_nn", "strong_baseline"),
    ("weighted_bc", "strong_baseline"),
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
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def success_count(row: dict[str, str]) -> int:
    return int(round(float(row["success_rate"]) * int(float(row["eval_episodes"]))))


def select_endpoint_metric(rows: list[dict[str, str]]) -> dict[str, str]:
    for row in rows:
        checkpoint_name = row.get("checkpoint_name", "")
        checkpoint = row.get("checkpoint", "")
        if checkpoint_name == "model_epoch_200" or Path(checkpoint).name == "model_epoch_200.pth":
            return row
    return rows[-1]


def metric_row(
    *,
    split_seed: int,
    method_id: str,
    method_role: str,
    metrics_path: Path,
    setup_row: dict[str, str] | None = None,
) -> dict[str, object] | None:
    if not metrics_path.exists():
        return None
    metrics = select_endpoint_metric(read_csv(metrics_path))
    out: dict[str, object] = {
        "split_seed": split_seed,
        "method_id": method_id,
        "method_role": method_role,
        "endpoint_success": f"{float(metrics['success_rate']):.3f}",
        "success_count": success_count(metrics),
        "eval_episodes": int(float(metrics["eval_episodes"])),
        "avg_len": f"{float(metrics['avg_len']):.1f}",
        "checkpoint": metrics["checkpoint"],
        "metrics_path": str(metrics_path),
        "train_demo_count": "",
        "selected_unlabeled": "",
        "selected_hidden_positive": "",
        "selected_hidden_bad": "",
        "support_purity": "",
        "hidden_positive_recall": "",
        "hidden_bad_admission": "",
    }
    if setup_row is not None:
        for key in [
            "train_demo_count",
            "selected_unlabeled",
            "selected_hidden_positive",
            "selected_hidden_bad",
            "support_purity",
            "hidden_positive_recall",
            "hidden_bad_admission",
        ]:
            out[key] = setup_row.get(key, "")
    return out


def union_row(root: Path, split_seed: int) -> dict[str, object] | None:
    split_root = root / "ablations" / "v02_fresh_endpoint_200ep_can40" / f"split{split_seed}"
    setup_path = split_root / "endpoint_setup_summary.csv"
    if not setup_path.exists():
        return None
    setup_rows = {row["candidate_id"]: row for row in read_csv(setup_path)}
    metrics_path = split_root / UNION_TAG / "eval_50ep" / "metrics.csv"
    return metric_row(
        split_seed=split_seed,
        method_id=UNION_TAG,
        method_role="v02_selected",
        metrics_path=metrics_path,
        setup_row=setup_rows.get(UNION_TAG),
    )


def baseline_row(root: Path, split_seed: int, method_id: str, method_role: str) -> dict[str, object] | None:
    result_root = root / "per_seed" / f"can_paired_pos40_bad80_split{split_seed}_{method_id}_policy0"
    metrics_path = result_root / "eval" / "metrics.csv"
    row = metric_row(split_seed=split_seed, method_id=method_id, method_role=method_role, metrics_path=metrics_path)
    if row is None:
        return None

    report_path = result_root / "REPORT.md"
    if report_path.exists():
        for line in report_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("- Train demos:"):
                row["train_demo_count"] = line.split("`", 2)[1]
            elif line.startswith("- Selected unlabeled demos:"):
                row["selected_unlabeled"] = line.split("`", 2)[1]
    return row


def collect_rows(root: Path, split_seeds: list[int]) -> list[dict[str, object]]:
    rows = []
    for split_seed in split_seeds:
        row = union_row(root, split_seed)
        if row is not None:
            rows.append(row)
        for method_id, method_role in BASELINES:
            row = baseline_row(root, split_seed, method_id, method_role)
            if row is not None:
                rows.append(row)
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
        "# v0.2 Fresh Can 40 Endpoint Summary",
        "",
        "Fresh-split endpoint rows for the frozen `METHOD_FREEZE_V02.md` Can branch.",
        "This report covers the Can branch; see the v0.2 README and Lift report for the cross-task gate.",
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
    selected_rows = [row for row in rows if row["method_id"] == UNION_TAG]
    if selected_rows:
        selected_successes = sum(int(row["success_count"]) for row in selected_rows)
        selected_episodes = sum(int(row["eval_episodes"]) for row in selected_rows)
        completed_split_ids = {int(row["split_seed"]) for row in selected_rows}
        best_successes = 0
        best_episodes = 0
        comparable_selected_successes = 0
        comparable_selected_episodes = 0
        comparable_splits = 0
        for split_seed in sorted(completed_split_ids):
            split_rows = [row for row in rows if int(row["split_seed"]) == split_seed]
            selected = next((row for row in split_rows if row["method_id"] == UNION_TAG), None)
            baselines = [
                row
                for row in split_rows
                if row["method_role"] != "oracle_control" and row["method_id"] != UNION_TAG
            ]
            if not baselines:
                continue
            best = max(baselines, key=lambda row: float(row["endpoint_success"]))
            comparable_splits += 1
            if selected is not None:
                comparable_selected_successes += int(selected["success_count"])
                comparable_selected_episodes += int(selected["eval_episodes"])
            best_successes += int(best["success_count"])
            best_episodes += int(best["eval_episodes"])
        lines.append(
            f"- Completed v0.2 selected Can rows: {selected_successes}/{selected_episodes}."
        )
        if best_episodes:
            margin = (
                comparable_selected_successes / comparable_selected_episodes
                - best_successes / best_episodes
            )
            lines.append(
                f"- Comparable splits with completed non-oracle baselines: {comparable_splits}."
            )
            lines.append(
                f"- On comparable splits, v0.2 selected Can rows: "
                f"{comparable_selected_successes}/{comparable_selected_episodes}."
            )
            lines.append(
                f"- On comparable splits, best completed non-oracle baseline per split: {best_successes}/{best_episodes} "
                f"(margin {margin:+.3f})."
            )
        else:
            lines.append("- No completed non-oracle baseline rows are available for the selected splits.")

    lines.extend(["", "## Per-Split Read", ""])
    for split_seed in sorted({int(row["split_seed"]) for row in rows}):
        split_rows = [row for row in rows if int(row["split_seed"]) == split_seed]
        selected = next((row for row in split_rows if row["method_id"] == UNION_TAG), None)
        baselines = [
            row
            for row in split_rows
            if row["method_role"] != "oracle_control" and row["method_id"] != UNION_TAG
        ]
        if selected is None:
            lines.append(f"- Split {split_seed}: v0.2 selected row is missing.")
            continue
        if not baselines:
            lines.append(f"- Split {split_seed}: v0.2 selected row exists, but no non-oracle baselines are complete.")
            continue
        best = max(baselines, key=lambda row: float(row["endpoint_success"]))
        margin = float(selected["endpoint_success"]) - float(best["endpoint_success"])
        lines.append(
            f"- Split {split_seed}: v0.2 selected `{selected['method_id']}` is "
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
        "selected_hidden_positive",
        "selected_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "checkpoint",
        "metrics_path",
    ]
    write_csv(out_dir / "v02_fresh_can_endpoint_summary.csv", rows, fieldnames)
    (out_dir / "v02_fresh_can_endpoint_REPORT.md").write_text(build_report(rows), encoding="utf-8")
    print(f"wrote {out_dir / 'v02_fresh_can_endpoint_REPORT.md'}")


if __name__ == "__main__":
    main()
