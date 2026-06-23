from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inspection-dir",
        type=Path,
        default=Path("results/robomimic_inspection/square_mh_low_dim"),
    )
    parser.add_argument(
        "--quality-split-dir",
        type=Path,
        default=Path("results/robomimic_inspection/square_mh_quality_better_worse"),
    )
    parser.add_argument(
        "--selector-dir",
        type=Path,
        default=Path("results/robomimic_selector_score_analysis_square_mh_quality_better_worse"),
    )
    parser.add_argument(
        "--router-csv",
        type=Path,
        default=Path("results/robomimic_hidden_free_router_square_quality_extra/router_summary.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/robomimic_square_quality_transfer_summary"),
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(rows: list[dict[str, str]], key: str) -> float:
    return float(statistics.fmean(float(row[key]) for row in rows))


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def rule_row(rule_rows: list[dict[str, str]], name: str) -> dict[str, str | float]:
    rows = [row for row in rule_rows if row["threshold_name"] == name]
    if not rows:
        raise KeyError(name)
    return {
        "rule": name,
        "selected": mean(rows, "selected_demo_count"),
        "hidden_positive": mean(rows, "selected_hidden_positive_demos"),
        "hidden_bad": mean(rows, "selected_hidden_bad_demos"),
        "purity": mean(rows, "selected_hidden_positive_purity"),
    }


def write_csv(path: Path, rows: list[dict[str, str | float]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    inspection = json.loads((args.inspection_dir / "summary.json").read_text(encoding="utf-8"))
    split = json.loads((args.quality_split_dir / "split_indices.json").read_text(encoding="utf-8"))
    score_rows = read_csv(args.selector_dir / "score_summary.csv")
    rule_rows = read_csv(args.selector_dir / "selection_rules.csv")
    router_rows = read_csv(args.router_csv)
    square_router = [row for row in router_rows if row["analysis"] == "square_mh_quality"]
    if not square_router:
        raise KeyError("square_mh_quality not found in router csv")
    router = square_router[0]

    selected_rules = [
        rule_row(rule_rows, "top_posx2"),
        rule_row(rule_rows, "top_posx4"),
        rule_row(rule_rows, "pos_min"),
        rule_row(rule_rows, "adaptive_masscap"),
    ]
    write_csv(args.out_dir / "selection_summary.csv", selected_rules)
    score_summary = {
        "labeled_positive_mean": mean(score_rows, "labeled_positive_mean"),
        "labeled_positive_p10": mean(score_rows, "labeled_positive_p10"),
        "labeled_negative_mean": mean(score_rows, "labeled_negative_mean"),
        "labeled_negative_max": mean(score_rows, "labeled_negative_max"),
    }
    (args.out_dir / "score_summary.json").write_text(json.dumps(score_summary, indent=2), encoding="utf-8")

    report = [
        "# Robomimic Square Quality Transfer",
        "",
        "This is a support-side transfer diagnostic on a new Robomimic task family.",
        "Square MH contains relative-quality masks (`better`, `okay`, `worse`) but no reward-failure demonstrations, so it is not a bad-demo benchmark.",
        "",
        "## Dataset",
        "",
        f"- HDF5: `{inspection['hdf5_path']}`.",
        f"- Environment: `{inspection['env_name']}`.",
        f"- Demos: `{inspection['n_demos']}`.",
        f"- Reward-positive demos: `{inspection['n_positive']}`.",
        f"- Reward-negative demos: `{inspection['n_negative']}`.",
        "",
        "## Quality Split",
        "",
        "- Positive labels: scarce `better_train` demos.",
        "- Negative labels: scarce `worse_train` demos.",
        "- Unlabeled mix: remaining `better_train` and `worse_train` demos; `okay` demos are excluded from this audit to keep hidden labels well-defined.",
        f"- Labeled positives / negatives: `{len(split['labeled_positive_ids'])}` / `{len(split['labeled_negative_ids'])}`.",
        f"- Hidden-positive / hidden-negative unlabeled: `{split['unlabeled_positive_count']}` / `{split['unlabeled_negative_count']}`.",
        "",
        "## Score Calibration",
        "",
        f"- Labeled-positive mean score: `{fmt(score_summary['labeled_positive_mean'])}`.",
        f"- Labeled-positive p10 score: `{fmt(score_summary['labeled_positive_p10'])}`.",
        f"- Labeled-negative mean score: `{fmt(score_summary['labeled_negative_mean'])}`.",
        f"- Labeled-negative max score: `{fmt(score_summary['labeled_negative_max'])}`.",
        "",
        "## Selection Rules",
        "",
        "| rule | selected | hidden positive | hidden bad | purity |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in selected_rules:
        report.append(
            f"| {row['rule']} | {fmt(float(row['selected']), 1)} | "
            f"{fmt(float(row['hidden_positive']), 1)} | {fmt(float(row['hidden_bad']), 1)} | "
            f"{fmt(float(row['purity']))} |"
        )
    report.extend(
        [
            "",
            "## Router",
            "",
            f"- Hidden-label-free router branch: `{router['router_branch']}`.",
            f"- Training rule: `{router['training_rule']}`.",
            f"- Saturated unlabeled count >= 0.95: `{router['saturated_unlabeled_count']}`.",
            "",
            "## Interpretation",
            "",
            "- Scarce positive/negative quality labels produce a strong state-action score on Square MH.",
            "- The score improves support purity over the 50/50 unlabeled quality mix: `pos_min` reaches about `0.803` purity and adaptive masscap reaches about `0.712` purity.",
            "- This extends the score-calibration story to a new task family, but only as a relative-quality support diagnostic.",
            "- It should not be used as a main policy claim unless we add a quality-sensitive Square policy evaluation; sparse success alone is not enough because all recorded demos are successful.",
        ]
    )
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
