from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path


PROXIES = [
    ("valid_positive_ll", "higher"),
    ("labeled_positive_ll", "higher"),
    ("valid_contrastive_gap", "higher"),
    ("labeled_contrastive_gap", "higher"),
    ("valid_negative_rejection", "higher"),
    ("labeled_negative_rejection", "higher"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--original-scores",
        type=Path,
        default=Path("results/robomimic_can_mg_branch_proxy_final20k_original/checkpoint_scores.csv"),
    )
    parser.add_argument(
        "--shuffle-scores",
        type=Path,
        default=Path("results/robomimic_can_mg_branch_proxy_final20k_shuffle42/checkpoint_scores.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/robomimic_can_mg_branch_proxy_summary"),
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def method_name(run: str) -> str:
    if run.startswith("soft_weighted"):
        return "soft_weighted"
    if run.startswith("hard_posmin"):
        return "hard_posmin"
    return run.rsplit("_seed", 1)[0]


def seed_name(run: str) -> str:
    if "_seed" not in run:
        return ""
    return run.rsplit("_seed", 1)[1]


def fmean(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(statistics.fmean(values))


def fmt(value: float, digits: int = 3) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def aggregate_split(split_name: str, rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    per_run: dict[str, dict[str, float | str]] = {}
    for row in rows:
        run = row["run"]
        entry = per_run.setdefault(
            run,
            {
                "split": split_name,
                "run": run,
                "method": method_name(run),
                "seed": seed_name(run),
                "rollout_success_20k": float(row["rollout_success"]),
            },
        )
        entry[f"{row['filter_name']}_ll"] = float(row["log_likelihood"])

    run_rows: list[dict[str, str]] = []
    for entry in per_run.values():
        valid_positive = float(entry["valid_positive_ll"])
        valid_negative = float(entry["valid_negative_ll"])
        labeled_positive = float(entry["labeled_positive_ll"])
        labeled_negative = float(entry["labeled_negative_ll"])
        derived = {
            **entry,
            "valid_contrastive_gap": valid_positive - valid_negative,
            "labeled_contrastive_gap": labeled_positive - labeled_negative,
            # Larger is stronger rejection because negative log-likelihood is more negative.
            "valid_negative_rejection": -valid_negative,
            "labeled_negative_rejection": -labeled_negative,
        }
        run_rows.append(
            {
                key: fmt(value) if isinstance(value, float) else str(value)
                for key, value in derived.items()
            }
        )

    method_rows = []
    methods = sorted({row["method"] for row in run_rows})
    for method in methods:
        selected = [row for row in run_rows if row["method"] == method]
        method_rows.append(
            {
                "split": split_name,
                "method": method,
                "num_runs": str(len(selected)),
                "rollout_success_20k": fmt(fmean([float(row["rollout_success_20k"]) for row in selected])),
                "valid_positive_ll": fmt(fmean([float(row["valid_positive_ll"]) for row in selected])),
                "labeled_positive_ll": fmt(fmean([float(row["labeled_positive_ll"]) for row in selected])),
                "valid_contrastive_gap": fmt(fmean([float(row["valid_contrastive_gap"]) for row in selected])),
                "labeled_contrastive_gap": fmt(fmean([float(row["labeled_contrastive_gap"]) for row in selected])),
                "valid_negative_rejection": fmt(fmean([float(row["valid_negative_rejection"]) for row in selected])),
                "labeled_negative_rejection": fmt(fmean([float(row["labeled_negative_rejection"]) for row in selected])),
            }
        )
    return run_rows, method_rows


def proxy_winners(method_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    winners = []
    for split in sorted({row["split"] for row in method_rows}):
        split_rows = [row for row in method_rows if row["split"] == split]
        rollout_best = max(split_rows, key=lambda row: float(row["rollout_success_20k"]))
        rollout_best_success = float(rollout_best["rollout_success_20k"])
        for proxy, direction in PROXIES:
            if direction != "higher":
                raise ValueError(direction)
            best = max(split_rows, key=lambda row: float(row[proxy]))
            best_success = float(best["rollout_success_20k"])
            winners.append(
                {
                    "split": split,
                    "proxy": proxy,
                    "proxy_winner": best["method"],
                    "proxy_winner_rollout_20k": best["rollout_success_20k"],
                    "rollout_best_method": rollout_best["method"],
                    "rollout_best_20k": rollout_best["rollout_success_20k"],
                    "proxy_matches_rollout_best_method": str(best["method"] == rollout_best["method"]).lower(),
                    "proxy_matches_best_success": str(abs(best_success - rollout_best_success) < 1.0e-9).lower(),
                }
            )
    return winners


def table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[col] for col in columns) + " |")
    return lines


def write_report(out_dir: Path, method_rows: list[dict[str, str]], winners: list[dict[str, str]]) -> None:
    report = [
        "# Robomimic Can MG Branch-Proxy Summary",
        "",
        "This report tests whether hidden-label-free BC likelihood scores can replace router-v2 abstention on Can MG.",
        "It reuses existing final-20k official Robomimic BC-RNN-GMM checkpoints; no new policy training is included.",
        "",
        "The tested proxies score each trained policy on labeled and held-out positive/negative masks.",
        "Higher positive log-likelihood, higher positive-minus-negative likelihood gap, or stronger negative rejection are treated as candidate branch-quality signals.",
        "",
        "## Method Means",
        "",
        *table(
            method_rows,
            [
                "split",
                "method",
                "num_runs",
                "rollout_success_20k",
                "valid_positive_ll",
                "valid_contrastive_gap",
                "valid_negative_rejection",
            ],
        ),
        "",
        "## Proxy Winners",
        "",
        *table(
            winners,
            [
                "split",
                "proxy",
                "proxy_winner",
                "proxy_winner_rollout_20k",
                "rollout_best_method",
                "rollout_best_20k",
                "proxy_matches_best_success",
            ],
        ),
        "",
        "## Interpretation",
        "",
        "- On original Can MG, the rollout-best final-20k method is `weighted`, but the likelihood proxies prefer `allpositive` because it fits positives tightly and rejects negatives strongly.",
        "- Those hard-support policies lose coverage and underperform the broad weighted sampler at fixed 20k, so simple positive/negative likelihood is not a valid replacement for abstention.",
        "- On shuffled Can MG, final-20k hard and soft branches tie at `0.100`; the proxies can select a branch but cannot detect that both branches are weak.",
        "- Router v2 should keep abstaining on Can MG until we have a proxy that predicts rollout-quality coverage, not just positive imitation or negative rejection.",
    ]
    (out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    run_rows = []
    method_rows = []
    for split_name, path in [
        ("can_mg_original", args.original_scores),
        ("can_mg_shuffle42", args.shuffle_scores),
    ]:
        split_run_rows, split_method_rows = aggregate_split(split_name, read_rows(path))
        run_rows.extend(split_run_rows)
        method_rows.extend(split_method_rows)

    winners = proxy_winners(method_rows)
    write_csv(args.out_dir / "per_run_proxy_scores.csv", run_rows)
    write_csv(args.out_dir / "method_proxy_scores.csv", method_rows)
    write_csv(args.out_dir / "proxy_winners.csv", winners)
    write_report(args.out_dir, method_rows, winners)
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
