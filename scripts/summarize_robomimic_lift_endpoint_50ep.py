from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


RUNS = [
    (
        "bad-aware pos-min",
        0,
        Path("results/robomimic_lift_mg_official_bc_rnn_posmin_seed0_eval"),
        Path("results/robomimic_lift_mg_seed0_endpoint_50ep_posmin_eval"),
    ),
    (
        "bad-aware pos-min",
        1,
        Path("results/robomimic_lift_mg_official_bc_rnn_posmin_seed1_eval"),
        Path("results/robomimic_lift_mg_seed1_endpoint_50ep_posmin_eval"),
    ),
    (
        "bad-aware pos-min",
        2,
        Path("results/robomimic_lift_mg_official_bc_rnn_posmin_seed2_eval"),
        Path("results/robomimic_lift_mg_seed2_endpoint_50ep_posmin_eval"),
    ),
    (
        "weighted probability sampler",
        0,
        Path("results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed0_eval"),
        Path("results/robomimic_lift_mg_seed0_endpoint_50ep_weighted_eval"),
    ),
    (
        "weighted probability sampler",
        1,
        Path("results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed1_eval"),
        Path("results/robomimic_lift_mg_seed1_endpoint_50ep_weighted_eval"),
    ),
    (
        "weighted probability sampler",
        2,
        Path("results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed2_eval"),
        Path("results/robomimic_lift_mg_seed2_endpoint_50ep_weighted_eval"),
    ),
    (
        "positive-only NN top160",
        0,
        Path("results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed0_eval"),
        Path("results/robomimic_lift_mg_seed0_endpoint_50ep_posonly_top160_eval"),
    ),
    (
        "positive-only NN top160",
        1,
        Path("results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed1_eval"),
        Path("results/robomimic_lift_mg_seed1_endpoint_50ep_posonly_top160_eval"),
    ),
    (
        "positive-only NN top160",
        2,
        Path("results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed2_eval"),
        Path("results/robomimic_lift_mg_seed2_endpoint_50ep_posonly_top160_eval"),
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/robomimic_lift_mg_endpoint_50ep_summary"),
    )
    return parser.parse_args()


def read_metrics(path: Path) -> list[dict[str, str]]:
    with (path / "metrics.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def endpoint_metric(path: Path) -> dict[str, str]:
    rows = read_metrics(path)
    if len(rows) != 1:
        raise ValueError(f"expected one endpoint row in {path}, got {len(rows)}")
    return rows[0]


def original_20k_success(path: Path) -> float:
    rows = read_metrics(path)
    matches = [row for row in rows if row["checkpoint_name"] == "model_epoch_200"]
    if len(matches) != 1:
        raise ValueError(f"expected one model_epoch_200 row in {path}, got {len(matches)}")
    return float(matches[0]["success_rate"])


def read_episode_rows(path: Path) -> list[dict[str, str]]:
    with (path / "episode_metrics.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def pstdev(values: list[float]) -> float:
    mu = mean(values)
    return math.sqrt(sum((value - mu) ** 2 for value in values) / len(values))


def ci95(p: float, n: int) -> tuple[float, float, float]:
    se = math.sqrt(max(p * (1.0 - p), 0.0) / n)
    return se, max(0.0, p - 1.96 * se), min(1.0, p + 1.96 * se)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    endpoint_rows: list[dict[str, object]] = []
    per_initial_counts: dict[tuple[str, str], dict[str, int | str]] = {}
    initials: set[str] = set()

    for method, seed, original_dir, endpoint_dir in RUNS:
        original = original_20k_success(original_dir)
        endpoint = endpoint_metric(endpoint_dir)
        success = float(endpoint["success_rate"])
        episodes = int(endpoint["eval_episodes"])
        endpoint_rows.append(
            {
                "method": method,
                "seed": seed,
                "original_10ep_success": original,
                "success_50ep": success,
                "successes_50ep": int(round(success * episodes)),
                "episodes": episodes,
                "avg_len": float(endpoint["avg_len"]),
                "original_eval_dir": str(original_dir),
                "endpoint_eval_dir": str(endpoint_dir),
            }
        )

        grouped: dict[str, list[float]] = defaultdict(list)
        for row in read_episode_rows(endpoint_dir):
            grouped[row["initial_demo_id"]].append(float(row["success"]))
        for initial_id, values in grouped.items():
            initials.add(initial_id)
            counts = per_initial_counts.setdefault((method, initial_id), {"method": method, "initial_demo_id": initial_id})
            counts[f"seed{seed}_successes"] = int(sum(values))
            counts[f"seed{seed}_episodes"] = len(values)

    method_order = ["bad-aware pos-min", "weighted probability sampler", "positive-only NN top160"]
    aggregate_rows: list[dict[str, object]] = []
    for method in method_order:
        rows = [row for row in endpoint_rows if row["method"] == method]
        original_values = [float(row["original_10ep_success"]) for row in rows]
        success_values = [float(row["success_50ep"]) for row in rows]
        successes = sum(int(row["successes_50ep"]) for row in rows)
        episodes = sum(int(row["episodes"]) for row in rows)
        pooled = successes / episodes
        se, lo, hi = ci95(pooled, episodes)
        aggregate_rows.append(
            {
                "method": method,
                "original_10ep_mean": mean(original_values),
                "success_50ep_mean_by_seed": mean(success_values),
                "success_50ep_std_by_seed": pstdev(success_values),
                "pooled_success_50ep": pooled,
                "pooled_successes": successes,
                "pooled_episodes": episodes,
                "approx_se": se,
                "approx_ci95_low": lo,
                "approx_ci95_high": hi,
            }
        )

    per_initial_rows: list[dict[str, object]] = []
    for initial_id in sorted(initials):
        row: dict[str, object] = {"initial_demo_id": initial_id}
        for method in method_order:
            prefix = {
                "bad-aware pos-min": "posmin",
                "weighted probability sampler": "weighted",
                "positive-only NN top160": "posonly",
            }[method]
            successes = 0
            episodes = 0
            counts = per_initial_counts.get((method, initial_id), {})
            for seed in [0, 1, 2]:
                successes += int(counts.get(f"seed{seed}_successes", 0))
                episodes += int(counts.get(f"seed{seed}_episodes", 0))
            row[f"{prefix}_successes"] = successes
            row[f"{prefix}_episodes"] = episodes
            row[f"{prefix}_rate"] = successes / episodes if episodes else float("nan")
        row["posmin_minus_weighted"] = float(row["posmin_rate"]) - float(row["weighted_rate"])
        row["posmin_minus_posonly"] = float(row["posmin_rate"]) - float(row["posonly_rate"])
        per_initial_rows.append(row)

    write_csv(
        args.out_dir / "endpoint_summary.csv",
        endpoint_rows,
        [
            "method",
            "seed",
            "original_10ep_success",
            "success_50ep",
            "successes_50ep",
            "episodes",
            "avg_len",
            "original_eval_dir",
            "endpoint_eval_dir",
        ],
    )
    write_csv(
        args.out_dir / "aggregate_summary.csv",
        aggregate_rows,
        [
            "method",
            "original_10ep_mean",
            "success_50ep_mean_by_seed",
            "success_50ep_std_by_seed",
            "pooled_success_50ep",
            "pooled_successes",
            "pooled_episodes",
            "approx_se",
            "approx_ci95_low",
            "approx_ci95_high",
        ],
    )
    write_csv(
        args.out_dir / "per_initial_state.csv",
        per_initial_rows,
        [
            "initial_demo_id",
            "posmin_successes",
            "posmin_episodes",
            "posmin_rate",
            "weighted_successes",
            "weighted_episodes",
            "weighted_rate",
            "posonly_successes",
            "posonly_episodes",
            "posonly_rate",
            "posmin_minus_weighted",
            "posmin_minus_posonly",
        ],
    )

    seed_table = [
        "| method | seed | 10 ep 20k | 50 ep 20k |",
        "|---|---:|---:|---:|",
    ]
    for row in endpoint_rows:
        seed_table.append(
            f"| {row['method']} | {row['seed']} | {fmt(float(row['original_10ep_success']))} | "
            f"{fmt(float(row['success_50ep']))} |"
        )

    aggregate_table = [
        "| method | 10 ep mean | 50 ep seed mean | 50 ep pooled | approx 95% CI |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in aggregate_rows:
        aggregate_table.append(
            f"| {row['method']} | {fmt(float(row['original_10ep_mean']))} | "
            f"{fmt(float(row['success_50ep_mean_by_seed']))} +/- "
            f"{fmt(float(row['success_50ep_std_by_seed']))} | "
            f"{fmt(float(row['pooled_success_50ep']))} ({row['pooled_successes']}/{row['pooled_episodes']}) | "
            f"[{fmt(float(row['approx_ci95_low']))}, {fmt(float(row['approx_ci95_high']))}] |"
        )

    initial_table = [
        "| initial state | pos-min | weighted | pos-only | pos-min - weighted | pos-min - pos-only |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in per_initial_rows:
        initial_table.append(
            f"| {row['initial_demo_id']} | {row['posmin_successes']}/{row['posmin_episodes']} | "
            f"{row['weighted_successes']}/{row['weighted_episodes']} | "
            f"{row['posonly_successes']}/{row['posonly_episodes']} | "
            f"{fmt(float(row['posmin_minus_weighted']))} | {fmt(float(row['posmin_minus_posonly']))} |"
        )

    posmin = next(row for row in aggregate_rows if row["method"] == "bad-aware pos-min")
    weighted = next(row for row in aggregate_rows if row["method"] == "weighted probability sampler")
    posonly = next(row for row in aggregate_rows if row["method"] == "positive-only NN top160")
    report = [
        "# Lift MG Endpoint 50-Episode Check",
        "",
        "This diagnostic re-evaluates the fixed-20k Lift MG endpoint for the core bad-aware, soft-weighted, and no-bad-label controls.",
        "",
        "Protocol:",
        "",
        "- Task/split: Robomimic Lift MG sparse low-dim, original split.",
        "- Checkpoints: original fixed-20k checkpoints from the three-seed table.",
        "- Evaluation: 50 held-out validation-positive initial-state rollouts per seed and method, horizon 150.",
        "- The split has 30 validation-positive initial states; 50 rollouts cycle through that ordered set, so the first 20 starts are visited twice per seed and the remaining 10 once per seed.",
        "",
        "## Seed Results",
        "",
        "\n".join(seed_table),
        "",
        "## Aggregate Results",
        "",
        "\n".join(aggregate_table),
        "",
        "## Per-Initial-State Pattern",
        "",
        "\n".join(initial_table),
        "",
        "## Interpretation",
        "",
        f"- Bad-aware pos-min remains ahead of weighted BC at the fixed 20k endpoint: "
        f"`{fmt(float(posmin['success_50ep_mean_by_seed']))}` versus "
        f"`{fmt(float(weighted['success_50ep_mean_by_seed']))}`.",
        f"- The bad-aware edge over positive-only NN top160 is much smaller: "
        f"`{fmt(float(posmin['success_50ep_mean_by_seed']))}` versus "
        f"`{fmt(float(posonly['success_50ep_mean_by_seed']))}`.",
        "- The 50-episode check weakens any strong bad-label-necessity claim on Lift; the better claim is calibrated bad labels improve the fixed-budget coverage-quality tradeoff, while positive-only retrieval remains a strong baseline.",
        "- Approximate pooled binomial intervals overlap, so this is a robustness/caveat check rather than a standalone statistical proof.",
        "",
        "## Artifacts",
        "",
        "- `endpoint_summary.csv`",
        "- `aggregate_summary.csv`",
        "- `per_initial_state.csv`",
        "- Seed-level evaluator reports: `results/robomimic_lift_mg_seed{0,1,2}_endpoint_50ep_{posmin,weighted,posonly_top160}_eval/REPORT.md`",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
