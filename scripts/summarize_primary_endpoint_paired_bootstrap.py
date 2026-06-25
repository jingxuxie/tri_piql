from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path


OUT_DIR = Path("results/final_paper/tables")
PER_SEED = Path("results/final_paper/per_seed")
SPLIT_SEEDS = [11, 22, 33]
BOOTSTRAP_SAMPLES = 10_000
BOOTSTRAP_SEED = 20260624

TASKS = {
    "Can 40p/80b": {
        "prefix": "can_paired_pos40_bad80",
        "methods": {
            "all-demo BC": "bc_all_mixed",
            "weighted BC": "weighted_bc",
            "positive-only NN": "positive_only_nn",
            "TRIAGE-BC": "triage_bc",
            "all-positive oracle": "all_train_positive_oracle",
        },
    },
    "Lift MG": {
        "prefix": "lift_mg_mg_sparse",
        "methods": {
            "all-demo BC": "bc_all_mixed",
            "weighted BC": "weighted_bc",
            "positive-only NN": "positive_only_nn",
            "TRIAGE-BC": "triage_bc",
            "all-positive oracle": "all_train_positive_oracle",
        },
    },
}

COMPARISONS = [
    ("Can 40p/80b", "TRIAGE-BC", "weighted BC"),
    ("Can 40p/80b", "TRIAGE-BC", "all-demo BC"),
    ("Can 40p/80b", "TRIAGE-BC", "positive-only NN"),
    ("Lift MG", "weighted BC", "TRIAGE-BC"),
    ("Lift MG", "weighted BC", "positive-only NN"),
    ("Lift MG", "TRIAGE-BC", "all-demo BC"),
]


def read_episode_successes(path: Path) -> dict[str, list[float]]:
    if not path.exists():
        raise FileNotFoundError(path)
    grouped: dict[str, list[float]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            grouped[row["initial_demo_id"]].append(float(row["success"]))
    if not grouped:
        raise ValueError(f"empty episode metrics: {path}")
    return dict(grouped)


def method_episode_path(task: str, split_seed: int, method: str) -> Path:
    task_cfg = TASKS[task]
    method_slug = task_cfg["methods"][method]
    run_name = f"{task_cfg['prefix']}_split{split_seed}_{method_slug}_policy0"
    return PER_SEED / run_name / "eval" / "episode_metrics.csv"


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot average an empty list")
    return sum(values) / len(values)


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("cannot compute percentile of empty list")
    index = int(round((len(sorted_values) - 1) * q))
    return sorted_values[index]


def sign_test_p_two_sided(split_deltas: list[float]) -> str:
    signs = [1 if delta > 0 else -1 if delta < 0 else 0 for delta in split_deltas]
    nonzero = [sign for sign in signs if sign != 0]
    n = len(nonzero)
    if n == 0:
        return "1.000"
    wins = sum(1 for sign in nonzero if sign > 0)
    # Exact two-sided binomial sign test under p=0.5.
    probs = [comb(n, k) * (0.5**n) for k in range(n + 1)]
    lower = sum(probs[: wins + 1])
    upper = sum(probs[wins:])
    return f"{min(1.0, 2.0 * min(lower, upper)):.3f}"


def comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def paired_initial_deltas(
    task: str,
    split_seed: int,
    left_method: str,
    right_method: str,
) -> dict[str, float]:
    left = read_episode_successes(method_episode_path(task, split_seed, left_method))
    right = read_episode_successes(method_episode_path(task, split_seed, right_method))
    left_ids = set(left)
    right_ids = set(right)
    if left_ids != right_ids:
        missing_left = sorted(right_ids - left_ids)
        missing_right = sorted(left_ids - right_ids)
        raise ValueError(
            f"{task} split {split_seed} initial IDs do not match for "
            f"{left_method} vs {right_method}: missing_left={missing_left}, "
            f"missing_right={missing_right}"
        )
    return {
        initial_id: mean(left[initial_id]) - mean(right[initial_id])
        for initial_id in sorted(left_ids)
    }


def summarize_comparison(task: str, left_method: str, right_method: str) -> dict[str, str]:
    deltas_by_split = {
        split_seed: paired_initial_deltas(task, split_seed, left_method, right_method)
        for split_seed in SPLIT_SEEDS
    }
    split_deltas = [
        mean(list(deltas_by_split[split_seed].values())) for split_seed in SPLIT_SEEDS
    ]
    rng = random.Random(BOOTSTRAP_SEED)
    bootstrap_values: list[float] = []
    for _ in range(BOOTSTRAP_SAMPLES):
        sampled_split_means: list[float] = []
        for _ in SPLIT_SEEDS:
            split_seed = rng.choice(SPLIT_SEEDS)
            split_deltas_by_initial = deltas_by_split[split_seed]
            initial_ids = list(split_deltas_by_initial)
            sampled_initial_deltas = [
                split_deltas_by_initial[rng.choice(initial_ids)] for _ in initial_ids
            ]
            sampled_split_means.append(mean(sampled_initial_deltas))
        bootstrap_values.append(mean(sampled_split_means))
    bootstrap_values.sort()
    ci_low = percentile(bootstrap_values, 0.025)
    ci_high = percentile(bootstrap_values, 0.975)
    point = mean(split_deltas)
    signs = "".join("+" if delta > 0 else "-" if delta < 0 else "0" for delta in split_deltas)
    initial_counts = [len(deltas_by_split[split_seed]) for split_seed in SPLIT_SEEDS]
    return {
        "task": task,
        "comparison": f"{left_method} - {right_method}",
        "point_delta": f"{point:.3f}",
        "bootstrap95_low": f"{ci_low:.3f}",
        "bootstrap95_high": f"{ci_high:.3f}",
        "split11_delta": f"{split_deltas[0]:.3f}",
        "split22_delta": f"{split_deltas[1]:.3f}",
        "split33_delta": f"{split_deltas[2]:.3f}",
        "split_signs": signs,
        "split_sign_p_two_sided": sign_test_p_two_sided(split_deltas),
        "initial_states_per_split": "/".join(str(count) for count in initial_counts),
        "bootstrap_samples": str(BOOTSTRAP_SAMPLES),
        "note": "bootstrap resamples split seeds and paired initial states; repeated rollouts per initial state are averaged first",
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError("no rows to write")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    columns = [
        "task",
        "comparison",
        "point_delta",
        "bootstrap95_low",
        "bootstrap95_high",
        "split_signs",
        "split_sign_p_two_sided",
        "initial_states_per_split",
    ]
    lines = [
        "# Primary Endpoint Paired Bootstrap Audit",
        "",
        "This report summarizes paired endpoint success deltas using the staged per-episode metrics.",
        "For each split and method pair, episode successes are first averaged by held-out `initial_demo_id`; bootstrap samples then resample split seeds and paired initial states.",
        "This avoids treating repeated rollouts from the same validation-positive starts as fully independent.",
        "",
        *markdown_table(rows, columns),
        "",
        "## Interpretation",
        "",
        "- Can 40p/80b keeps a directionally consistent TRIAGE-BC over weighted-BC split signal, but the paired bootstrap interval still crosses zero.",
        "- Can 40p/80b does not support TRIAGE-BC over positive-only retrieval; the point estimate is negative and split signs are mixed.",
        "- Lift MG supports the coverage caveat: weighted BC has a positive pooled paired delta over TRIAGE-BC, but the split signs are mixed.",
        "- With only three split seeds, exact split-level sign tests are low power; the audit is a robustness and wording guardrail rather than a decisive significance claim.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [summarize_comparison(*comparison) for comparison in COMPARISONS]
    csv_path = OUT_DIR / "primary_endpoint_paired_bootstrap.csv"
    report_path = OUT_DIR / "primary_endpoint_paired_bootstrap_REPORT.md"
    write_csv(csv_path, rows)
    write_report(report_path, rows)
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
