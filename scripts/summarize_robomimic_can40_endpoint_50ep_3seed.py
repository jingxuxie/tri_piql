from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


RUNS = [
    (
        "adaptive masscap",
        0,
        0.800,
        Path("results/robomimic_can40_seed0_endpoint_50ep_masscap_eval"),
    ),
    (
        "weighted probability sampler",
        0,
        0.500,
        Path("results/robomimic_can40_seed0_endpoint_50ep_weighted_eval"),
    ),
    (
        "adaptive masscap",
        1,
        0.600,
        Path("results/robomimic_can40_seed1_endpoint_50ep_masscap_eval"),
    ),
    (
        "weighted probability sampler",
        1,
        0.600,
        Path("results/robomimic_can40_seed1_endpoint_50ep_weighted_eval"),
    ),
    (
        "adaptive masscap",
        2,
        0.800,
        Path("results/robomimic_can40_seed2_endpoint_50ep_masscap_eval"),
    ),
    (
        "weighted probability sampler",
        2,
        0.600,
        Path("results/robomimic_can40_seed2_endpoint_50ep_weighted_eval"),
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/robomimic_can40_endpoint_50ep_3seed_summary"),
    )
    return parser.parse_args()


def read_single_metric(run_dir: Path) -> dict[str, str]:
    with (run_dir / "metrics.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1:
        raise ValueError(f"expected one metric row in {run_dir}, got {len(rows)}")
    return rows[0]


def read_episode_rows(run_dir: Path) -> list[dict[str, str]]:
    with (run_dir / "episode_metrics.csv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fmt(value: float) -> str:
    return f"{value:.3f}"


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def pstdev(values: list[float]) -> float:
    mu = mean(values)
    return math.sqrt(sum((v - mu) ** 2 for v in values) / len(values))


def ci95(p: float, n: int) -> tuple[float, float, float]:
    se = math.sqrt(max(p * (1.0 - p), 0.0) / n)
    lo = max(0.0, p - 1.96 * se)
    hi = min(1.0, p + 1.96 * se)
    return se, lo, hi


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    endpoint_rows: list[dict[str, object]] = []
    per_initial_counts: dict[tuple[str, str], dict[str, object]] = {}
    per_initial_order: set[str] = set()

    for method, seed, original_10ep, run_dir in RUNS:
        metric = read_single_metric(run_dir)
        success = float(metric["success_rate"])
        episodes = int(metric["eval_episodes"])
        avg_len = float(metric["avg_len"])
        endpoint_rows.append(
            {
                "method": method,
                "seed": seed,
                "original_10ep_success": original_10ep,
                "success_50ep": success,
                "successes_50ep": int(round(success * episodes)),
                "episodes": episodes,
                "avg_len": avg_len,
                "run_dir": str(run_dir),
            }
        )
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in read_episode_rows(run_dir):
            grouped[row["initial_demo_id"]].append(float(row["success"]))
        for initial_id, values in grouped.items():
            per_initial_order.add(initial_id)
            key = (method, initial_id)
            counts = per_initial_counts.setdefault(
                key,
                {
                    "method": method,
                    "initial_demo_id": initial_id,
                },
            )
            counts[f"seed{seed}_successes"] = int(sum(values))
            counts[f"seed{seed}_episodes"] = len(values)

    methods = sorted({row["method"] for row in endpoint_rows})
    aggregate_rows: list[dict[str, object]] = []
    for method in methods:
        rows = [row for row in endpoint_rows if row["method"] == method]
        success_values = [float(row["success_50ep"]) for row in rows]
        original_values = [float(row["original_10ep_success"]) for row in rows]
        successes = sum(int(row["successes_50ep"]) for row in rows)
        episodes = sum(int(row["episodes"]) for row in rows)
        p = successes / episodes
        se, lo, hi = ci95(p, episodes)
        aggregate_rows.append(
            {
                "method": method,
                "original_10ep_mean": mean(original_values),
                "success_50ep_mean_by_seed": mean(success_values),
                "success_50ep_std_by_seed": pstdev(success_values),
                "pooled_success_50ep": p,
                "pooled_successes": successes,
                "pooled_episodes": episodes,
                "approx_se": se,
                "approx_ci95_low": lo,
                "approx_ci95_high": hi,
            }
        )

    masscap = next(row for row in aggregate_rows if row["method"] == "adaptive masscap")
    weighted = next(row for row in aggregate_rows if row["method"] == "weighted probability sampler")
    aggregate_gap = float(masscap["success_50ep_mean_by_seed"]) - float(weighted["success_50ep_mean_by_seed"])
    original_gap = float(masscap["original_10ep_mean"]) - float(weighted["original_10ep_mean"])

    paired_rows: list[dict[str, object]] = []
    for seed in [0, 1, 2]:
        masscap_row = next(row for row in endpoint_rows if row["method"] == "adaptive masscap" and row["seed"] == seed)
        weighted_row = next(
            row for row in endpoint_rows if row["method"] == "weighted probability sampler" and row["seed"] == seed
        )
        paired_rows.append(
            {
                "seed": seed,
                "masscap_10ep": masscap_row["original_10ep_success"],
                "weighted_10ep": weighted_row["original_10ep_success"],
                "gap_10ep": float(masscap_row["original_10ep_success"]) - float(weighted_row["original_10ep_success"]),
                "masscap_50ep": masscap_row["success_50ep"],
                "weighted_50ep": weighted_row["success_50ep"],
                "gap_50ep": float(masscap_row["success_50ep"]) - float(weighted_row["success_50ep"]),
            }
        )

    per_initial_rows: list[dict[str, object]] = []
    for initial_id in sorted(per_initial_order):
        row: dict[str, object] = {"initial_demo_id": initial_id}
        for method in methods:
            successes = 0
            episodes = 0
            for seed in [0, 1, 2]:
                counts = per_initial_counts.get((method, initial_id), {})
                successes += int(counts.get(f"seed{seed}_successes", 0))
                episodes += int(counts.get(f"seed{seed}_episodes", 0))
            prefix = "masscap" if method == "adaptive masscap" else "weighted"
            row[f"{prefix}_successes"] = successes
            row[f"{prefix}_episodes"] = episodes
            row[f"{prefix}_rate"] = successes / episodes if episodes else float("nan")
        row["difference"] = float(row["masscap_rate"]) - float(row["weighted_rate"])
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
            "run_dir",
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
        args.out_dir / "paired_seed_gaps.csv",
        paired_rows,
        ["seed", "masscap_10ep", "weighted_10ep", "gap_10ep", "masscap_50ep", "weighted_50ep", "gap_50ep"],
    )
    write_csv(
        args.out_dir / "per_initial_state.csv",
        per_initial_rows,
        [
            "initial_demo_id",
            "masscap_successes",
            "masscap_episodes",
            "masscap_rate",
            "weighted_successes",
            "weighted_episodes",
            "weighted_rate",
            "difference",
        ],
    )

    endpoint_table = [
        "| seed | masscap 10 ep | weighted 10 ep | gap 10 ep | masscap 50 ep | weighted 50 ep | gap 50 ep |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in paired_rows:
        endpoint_table.append(
            f"| {row['seed']} | {fmt(float(row['masscap_10ep']))} | {fmt(float(row['weighted_10ep']))} | "
            f"{fmt(float(row['gap_10ep']))} | {fmt(float(row['masscap_50ep']))} | "
            f"{fmt(float(row['weighted_50ep']))} | {fmt(float(row['gap_50ep']))} |"
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
        "| initial state | masscap | weighted | difference |",
        "|---|---:|---:|---:|",
    ]
    for row in per_initial_rows:
        initial_table.append(
            f"| {row['initial_demo_id']} | {row['masscap_successes']}/{row['masscap_episodes']} | "
            f"{row['weighted_successes']}/{row['weighted_episodes']} | {fmt(float(row['difference']))} |"
        )

    report = [
        "# Can 40p/80b Three-Seed Endpoint 50-Episode Check",
        "",
        "This diagnostic extends the seed-0 higher-episode endpoint check to all three seeds for the original "
        "Can 40 positive / 80 bad fixed-20k masscap-vs-weighted comparison.",
        "",
        "Protocol:",
        "",
        "- Task/split: Robomimic Can paired low-dim, 40 labeled positives / 80 labeled bads.",
        "- Checkpoints: original fixed-20k checkpoints from the three-seed table.",
        "- Evaluation: 50 held-out validation-positive initial-state rollouts per seed and method, horizon 400.",
        "- The 50 rollouts cycle over the same 10 validation-positive initial states five times.",
        "",
        "## Seed Results",
        "",
        "\n".join(endpoint_table),
        "",
        "## Aggregate Results",
        "",
        "\n".join(aggregate_table),
        "",
        f"The 10-episode mean gap was `{fmt(original_gap)}`. The 50-episode mean-by-seed gap is "
        f"`{fmt(aggregate_gap)}`.",
        "",
        "## Per-Initial-State Pattern",
        "",
        "\n".join(initial_table),
        "",
        "## Interpretation",
        "",
        "- The higher-episode direction favors masscap on every seed: gaps are `0.140`, `0.120`, and `0.060`.",
        "- The aggregate gap shrinks relative to the original 10-episode table, from `0.167` to `0.107` by seed mean.",
        "- The approximate pooled binomial intervals still overlap, so this is not a standalone statistical proof.",
        "- The result strengthens the main fixed-budget story because the masscap edge persists under a less noisy endpoint estimate, while also forcing the paper to describe the endpoint gap as modest.",
        "",
        "## Artifacts",
        "",
        "- `endpoint_summary.csv`",
        "- `aggregate_summary.csv`",
        "- `paired_seed_gaps.csv`",
        "- `per_initial_state.csv`",
        "- Seed-level evaluator reports: `results/robomimic_can40_seed{0,1,2}_endpoint_50ep_{masscap,weighted}_eval/REPORT.md`",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
