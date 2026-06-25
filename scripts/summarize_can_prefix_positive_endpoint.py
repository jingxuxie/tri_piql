from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = ROOT / "results" / "final_paper" / "ablations" / "can_prefix_positive_endpoint_200ep"
BASELINE_ID = "prefix_state_action_nn_top80"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--eval-subdir", default="eval_50ep")
    parser.add_argument("--split-summary-name", default="endpoint_200ep_summary.csv")
    parser.add_argument("--aggregate-summary-name", default="endpoint_200ep_aggregate_summary.csv")
    parser.add_argument("--report-name", default="REPORT.md")
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


def split_sort_key(path: Path) -> tuple[int, str]:
    if path.name.startswith("split") and path.name.removeprefix("split").isdigit():
        return (int(path.name.removeprefix("split")), path.name)
    return (10**9, path.name)


def load_metrics(path: Path) -> dict[str, str]:
    rows = read_csv(path)
    if len(rows) != 1:
        raise ValueError(f"expected exactly one metric row in {path}, found {len(rows)}")
    return rows[0]


def summarize_split(split_root: Path, eval_subdir: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for setup in read_csv(split_root / "endpoint_setup_summary.csv"):
        tag = setup["candidate_tag"]
        metric_path = split_root / tag / eval_subdir / "metrics.csv"
        if not metric_path.exists():
            continue
        metric = load_metrics(metric_path)
        diagnostics = json.loads((split_root / tag / "setup" / "diagnostics.json").read_text(encoding="utf-8"))
        eval_episodes = int(metric["eval_episodes"])
        success_rate = float(metric["success_rate"])
        rows.append(
            {
                "split_seed": int(setup["split_seed"]),
                "candidate_id": setup["candidate_id"],
                "candidate_tag": tag,
                "train_epochs": int(diagnostics["num_epochs"]),
                "epoch_steps": int(diagnostics["epoch_steps"]),
                "train_demo_count": int(setup["train_demo_count"]),
                "selected_unlabeled": int(setup["selected_unlabeled"]),
                "selected_hidden_positive": int(setup["selected_hidden_positive"]),
                "selected_hidden_bad": int(setup["selected_hidden_bad"]),
                "support_purity": float(setup["support_purity"]),
                "hidden_positive_recall": float(setup["hidden_positive_recall"]),
                "hidden_bad_admission": float(setup["hidden_bad_admission"]),
                "success_count": int(round(success_rate * eval_episodes)),
                "eval_episodes": eval_episodes,
                "success_rate": success_rate,
                "avg_return": float(metric["avg_return"]),
                "avg_len": float(metric["avg_len"]),
                "checkpoint": metric["checkpoint"],
            }
        )
    rows.sort(key=lambda row: float(row["success_rate"]), reverse=True)
    return rows


def aggregate_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_candidate: dict[str, dict[str, object]] = {}
    for row in rows:
        candidate_id = str(row["candidate_id"])
        entry = by_candidate.setdefault(
            candidate_id,
            {
                "candidate_id": candidate_id,
                "success_count": 0,
                "eval_episodes": 0,
                "selected_hidden_positive": 0,
                "selected_hidden_bad": 0,
                "support_purity_sum": 0.0,
                "hidden_positive_recall_sum": 0.0,
                "hidden_bad_admission_sum": 0.0,
                "avg_len_weighted_sum": 0.0,
                "num_splits": 0,
            },
        )
        eval_episodes = int(row["eval_episodes"])
        entry["success_count"] = int(entry["success_count"]) + int(row["success_count"])
        entry["eval_episodes"] = int(entry["eval_episodes"]) + eval_episodes
        entry["selected_hidden_positive"] = int(entry["selected_hidden_positive"]) + int(
            row["selected_hidden_positive"]
        )
        entry["selected_hidden_bad"] = int(entry["selected_hidden_bad"]) + int(row["selected_hidden_bad"])
        entry["support_purity_sum"] = float(entry["support_purity_sum"]) + float(row["support_purity"])
        entry["hidden_positive_recall_sum"] = float(entry["hidden_positive_recall_sum"]) + float(
            row["hidden_positive_recall"]
        )
        entry["hidden_bad_admission_sum"] = float(entry["hidden_bad_admission_sum"]) + float(
            row["hidden_bad_admission"]
        )
        entry["avg_len_weighted_sum"] = float(entry["avg_len_weighted_sum"]) + float(row["avg_len"]) * eval_episodes
        entry["num_splits"] = int(entry["num_splits"]) + 1

    aggregate = []
    for entry in by_candidate.values():
        num_splits = int(entry["num_splits"])
        eval_episodes = int(entry["eval_episodes"])
        success_count = int(entry["success_count"])
        aggregate.append(
            {
                "candidate_id": entry["candidate_id"],
                "num_splits": num_splits,
                "success_count": success_count,
                "eval_episodes": eval_episodes,
                "success_rate": success_count / eval_episodes,
                "mean_support_purity": float(entry["support_purity_sum"]) / num_splits,
                "mean_hidden_positive_recall": float(entry["hidden_positive_recall_sum"]) / num_splits,
                "mean_hidden_bad_admission": float(entry["hidden_bad_admission_sum"]) / num_splits,
                "selected_hidden_positive": int(entry["selected_hidden_positive"]),
                "selected_hidden_bad": int(entry["selected_hidden_bad"]),
                "avg_len": float(entry["avg_len_weighted_sum"]) / eval_episodes,
            }
        )
    aggregate.sort(key=lambda row: (float(row["success_rate"]), int(row["success_count"])), reverse=True)
    return aggregate


def format_rate(value: object) -> str:
    return f"{float(value):.3f}"


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def write_split_report(split_root: Path, rows: list[dict[str, object]], report_name: str) -> None:
    best = rows[0]
    baseline = next((row for row in rows if row["candidate_id"] == BASELINE_ID), None)
    delta_line = ""
    if baseline is not None and best["candidate_id"] != BASELINE_ID:
        delta = int(best["success_count"]) - int(baseline["success_count"])
        delta_line = (
            f"- Best candidate leads the prefix-NN baseline by `{delta}` successes over "
            f"`{best['eval_episodes']}` matched rollouts."
        )
    lines = [
        "# Can Prefix-Positive Endpoint Check",
        "",
        "This controlled Robomimic diagnostic labels only early prefixes of successful Can demos as positives, "
        "uses failed demos as explicit negatives, and trains official BC-RNN-GMM policies on selected full trajectories.",
        "",
        "## Result",
        "",
        "| candidate | support purity | hidden-positive selected | hidden-bad selected | success | avg len |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['candidate_id']} | {format_rate(row['support_purity'])} | "
            f"{row['selected_hidden_positive']} | {row['selected_hidden_bad']} | "
            f"{row['success_count']}/{row['eval_episodes']} ({format_rate(row['success_rate'])}) | "
            f"{float(row['avg_len']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Best row: `{best['candidate_id']}` with `{best['success_count']}/{best['eval_episodes']}` successes.",
        ]
    )
    if delta_line:
        lines.append(delta_line)
    lines.extend(
        [
            "- This split-level report is one slice of the prefix-positive endpoint diagnostic.",
            "- Use the aggregate report, not any one split, for paper-facing claims.",
        ]
    )
    (split_root / report_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_aggregate_report(root: Path, rows: list[dict[str, object]], aggregate: list[dict[str, object]], report_name: str) -> None:
    split_seeds = sorted({int(row["split_seed"]) for row in rows})
    best = aggregate[0]
    baseline = next((row for row in aggregate if row["candidate_id"] == BASELINE_ID), None)
    split_phrase = ", ".join(str(seed) for seed in split_seeds)
    scope = "single-split" if len(split_seeds) == 1 else f"{len(split_seeds)}-split"
    lines = [
        f"# Can Prefix-Positive {scope.title()} Endpoint Check",
        "",
        "This is a controlled Robomimic diagnostic, not a primary benchmark row. It tests whether explicit bad labels "
        "help when trusted successes provide only early trajectory prefixes and the useful full trajectories are hidden "
        "inside the unlabeled pool.",
        "",
        f"Completed split seeds: `{split_phrase}`.",
        "All completed rows use official Robomimic BC-RNN-GMM, 200 epochs, 100 gradient steps per epoch, "
        "and 50 valid-positive evaluation starts per split.",
        "",
        "## Aggregate Result",
        "",
        "| candidate | splits | success | success rate | mean support purity | hidden-positive selected | hidden-bad selected | avg len |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in aggregate:
        lines.append(
            f"| {row['candidate_id']} | {row['num_splits']} | {row['success_count']}/{row['eval_episodes']} | "
            f"{format_rate(row['success_rate'])} | {format_rate(row['mean_support_purity'])} | "
            f"{row['selected_hidden_positive']} | {row['selected_hidden_bad']} | {float(row['avg_len']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Per-Split Result",
            "",
            "| split | candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    candidate_order = {str(row["candidate_id"]): index for index, row in enumerate(aggregate)}
    for row in sorted(rows, key=lambda item: (int(item["split_seed"]), candidate_order[str(item["candidate_id"])])):
        lines.append(
            f"| {row['split_seed']} | {row['candidate_id']} | {format_rate(row['support_purity'])} | "
            f"{format_rate(row['hidden_positive_recall'])} | {format_rate(row['hidden_bad_admission'])} | "
            f"{row['success_count']}/{row['eval_episodes']} | {float(row['avg_len']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Best aggregate row: `{best['candidate_id']}` with `{best['success_count']}/{best['eval_episodes']}` successes.",
        ]
    )
    if baseline is not None and best["candidate_id"] != BASELINE_ID:
        delta = int(best["success_count"]) - int(baseline["success_count"])
        lines.append(
            f"- Best row leads the prefix state-action NN top80 baseline by `{delta}` successes over "
            f"`{best['eval_episodes']}` matched rollouts."
        )
    lines.extend(
        [
            "- This is the first Robomimic result that directly mirrors the PointNav prefix-positive mechanism.",
            "- This is strong controlled robotics evidence for the prefix-positive mechanism, but it is not a primary benchmark row because the split construction changes the default Robomimic setting.",
            "",
            "## Outputs",
            "",
            f"- `{display_path(root / 'endpoint_200ep_aggregate_summary.csv')}`",
            f"- `{display_path(root / report_name)}`",
        ]
    )
    (root / report_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = args.root
    split_roots = [
        path
        for path in root.glob("split*")
        if path.is_dir() and (path / "endpoint_setup_summary.csv").exists()
    ]
    if not split_roots:
        raise FileNotFoundError(f"no split endpoint setup summaries found under {root}")

    all_rows: list[dict[str, object]] = []
    fieldnames = [
        "split_seed",
        "candidate_id",
        "candidate_tag",
        "train_epochs",
        "epoch_steps",
        "train_demo_count",
        "selected_unlabeled",
        "selected_hidden_positive",
        "selected_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "success_count",
        "eval_episodes",
        "success_rate",
        "avg_return",
        "avg_len",
        "checkpoint",
    ]
    for split_root in sorted(split_roots, key=split_sort_key):
        rows = summarize_split(split_root, args.eval_subdir)
        if not rows:
            continue
        write_csv(split_root / args.split_summary_name, rows, fieldnames)
        write_split_report(split_root, rows, args.report_name)
        all_rows.extend(rows)

    if not all_rows:
        raise FileNotFoundError(f"no completed {args.eval_subdir}/metrics.csv files found under {root}")

    aggregate = aggregate_rows(all_rows)
    write_csv(root / args.aggregate_summary_name, aggregate, list(aggregate[0].keys()))
    write_aggregate_report(root, all_rows, aggregate, args.report_name)
    print(f"wrote {root / args.aggregate_summary_name}")
    print(f"wrote {root / args.report_name}")


if __name__ == "__main__":
    main()
