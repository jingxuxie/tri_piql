from __future__ import annotations

import argparse
import csv
import math
import random
from collections import defaultdict
from pathlib import Path


DEFAULT_ROOT = Path("results/final_paper_v02")
BOOTSTRAP_SAMPLES = 10_000
BOOTSTRAP_SEED = 20260625


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--bootstrap-samples", type=int, default=BOOTSTRAP_SAMPLES)
    parser.add_argument("--bootstrap-seed", type=int, default=BOOTSTRAP_SEED)
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


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot average empty values")
    return sum(values) / len(values)


def sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return float("nan")
    avg = mean(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))


def fmt(value: float | int | str, digits: int = 3) -> str:
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("cannot compute percentile of empty values")
    index = int(round((len(sorted_values) - 1) * q))
    return sorted_values[index]


def wilson_interval(successes: int, episodes: int, z: float = 1.96) -> tuple[float, float]:
    if episodes <= 0:
        raise ValueError("episodes must be positive")
    p_hat = successes / episodes
    denom = 1.0 + z**2 / episodes
    center = (p_hat + z**2 / (2.0 * episodes)) / denom
    radius = z * math.sqrt((p_hat * (1.0 - p_hat) + z**2 / (4.0 * episodes)) / episodes) / denom
    return max(0.0, center - radius), min(1.0, center + radius)


def comb(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(1, k + 1):
        result = result * (n - k + i) // i
    return result


def sign_test_p_two_sided(split_deltas: list[float]) -> str:
    signs = [1 if delta > 0 else -1 if delta < 0 else 0 for delta in split_deltas]
    nonzero = [sign for sign in signs if sign != 0]
    n = len(nonzero)
    if n == 0:
        return "1.000"
    wins = sum(1 for sign in nonzero if sign > 0)
    probs = [comb(n, k) * (0.5**n) for k in range(n + 1)]
    lower = sum(probs[: wins + 1])
    upper = sum(probs[wins:])
    return f"{min(1.0, 2.0 * min(lower, upper)):.3f}"


def episode_metrics_path(metrics_path: str) -> Path:
    path = Path(metrics_path)
    if path.name != "metrics.csv":
        raise ValueError(f"expected metrics.csv path, got {path}")
    return path.with_name("episode_metrics.csv")


def read_initial_successes(path: Path) -> dict[str, list[float]]:
    if not path.exists():
        raise FileNotFoundError(path)
    grouped: dict[str, list[float]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            grouped[row["initial_demo_id"]].append(float(row["success"]))
    if not grouped:
        raise ValueError(f"empty episode metrics: {path}")
    return dict(grouped)


def rows_by_task(root: Path) -> dict[str, list[dict[str, str]]]:
    return {
        "Can 40p/80b": read_csv(root / "tables" / "v02_fresh_can_endpoint_summary.csv"),
        "Lift MG": read_csv(root / "tables" / "v02_fresh_lift_endpoint_summary.csv"),
    }


def row_for_method(rows: list[dict[str, str]], split_seed: int, method_id: str) -> dict[str, str]:
    matches = [
        row for row in rows if int(row["split_seed"]) == split_seed and row["method_id"] == method_id
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one row for split {split_seed} method {method_id}, found {len(matches)}")
    return matches[0]


def split_delta_rows(
    root: Path,
    setting_label: str,
    split_seed: int,
    selected_method: str,
    best_baseline_method: str,
    task_endpoint_rows: dict[str, list[dict[str, str]]],
) -> tuple[list[dict[str, object]], float]:
    task_rows = task_endpoint_rows[setting_label]
    selected_row = row_for_method(task_rows, split_seed, selected_method)
    baseline_row = row_for_method(task_rows, split_seed, best_baseline_method)
    selected = read_initial_successes(episode_metrics_path(selected_row["metrics_path"]))
    baseline = read_initial_successes(episode_metrics_path(baseline_row["metrics_path"]))
    if set(selected) != set(baseline):
        raise ValueError(
            f"{setting_label} split {split_seed} initial IDs mismatch for "
            f"{selected_method} vs {best_baseline_method}"
        )

    rows: list[dict[str, object]] = []
    for initial_id in sorted(selected):
        selected_mean = mean(selected[initial_id])
        baseline_mean = mean(baseline[initial_id])
        rows.append(
            {
                "setting_label": setting_label,
                "split_seed": split_seed,
                "selected_method": selected_method,
                "best_baseline_method": best_baseline_method,
                "initial_demo_id": initial_id,
                "selected_success_rate": f"{selected_mean:.3f}",
                "best_baseline_success_rate": f"{baseline_mean:.3f}",
                "delta": f"{selected_mean - baseline_mean:+.3f}",
            }
        )
    split_delta = mean([float(row["delta"]) for row in rows])
    return rows, split_delta


def bootstrap_scope(
    units: list[tuple[str, int, dict[str, float]]],
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> tuple[float, float, float]:
    rng = random.Random(bootstrap_seed)
    bootstrap_values: list[float] = []
    for _ in range(bootstrap_samples):
        sampled_split_means: list[float] = []
        for _ in units:
            _setting_label, _split_seed, deltas_by_initial = rng.choice(units)
            initial_ids = list(deltas_by_initial)
            sampled = [deltas_by_initial[rng.choice(initial_ids)] for _ in initial_ids]
            sampled_split_means.append(mean(sampled))
        bootstrap_values.append(mean(sampled_split_means))
    bootstrap_values.sort()
    return (
        mean([mean(list(unit[2].values())) for unit in units]),
        percentile(bootstrap_values, 0.025),
        percentile(bootstrap_values, 0.975),
    )


def scope_summary(
    scope: str,
    scope_rows: list[dict[str, object]],
    paired_rows: list[dict[str, object]],
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, object]:
    selected_success = sum(int(row["selected_success"]) for row in scope_rows)
    selected_episodes = sum(int(row["selected_episodes"]) for row in scope_rows)
    best_success = sum(int(row["best_baseline_success"]) for row in scope_rows)
    best_episodes = sum(int(row["best_baseline_episodes"]) for row in scope_rows)
    selected_low, selected_high = wilson_interval(selected_success, selected_episodes)
    best_low, best_high = wilson_interval(best_success, best_episodes)

    deltas_by_unit: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    for row in paired_rows:
        if row["setting_label"] in {scope, "Can 40p/80b", "Lift MG"}:
            key = (str(row["setting_label"]), int(row["split_seed"]))
            deltas_by_unit[key][str(row["initial_demo_id"])] = float(row["delta"])

    if scope in {"Can 40p/80b", "Lift MG"}:
        units = [
            (setting, split_seed, deltas)
            for (setting, split_seed), deltas in sorted(deltas_by_unit.items())
            if setting == scope
        ]
    elif scope == "Combined Can+Lift":
        units = [
            (setting, split_seed, deltas)
            for (setting, split_seed), deltas in sorted(deltas_by_unit.items())
        ]
    else:
        raise ValueError(f"unknown scope {scope}")

    point, low, high = bootstrap_scope(units, bootstrap_samples, bootstrap_seed)
    split_deltas = [mean(list(unit[2].values())) for unit in units]
    signs = "".join("+" if delta > 0 else "-" if delta < 0 else "0" for delta in split_deltas)
    initial_counts = "/".join(str(len(unit[2])) for unit in units)

    return {
        "scope": scope,
        "selected_success": selected_success,
        "selected_episodes": selected_episodes,
        "selected_rate": fmt(selected_success / selected_episodes),
        "selected_wilson95_low": fmt(selected_low),
        "selected_wilson95_high": fmt(selected_high),
        "best_baseline_success": best_success,
        "best_baseline_episodes": best_episodes,
        "best_baseline_rate": fmt(best_success / best_episodes),
        "best_baseline_wilson95_low": fmt(best_low),
        "best_baseline_wilson95_high": fmt(best_high),
        "pooled_delta": fmt(selected_success / selected_episodes - best_success / best_episodes),
        "paired_bootstrap_delta": fmt(point),
        "paired_bootstrap95_low": fmt(low),
        "paired_bootstrap95_high": fmt(high),
        "split_mean_delta": fmt(mean(split_deltas)),
        "split_std_delta": fmt(sample_std(split_deltas)),
        "split_signs": signs,
        "split_sign_p_two_sided": sign_test_p_two_sided(split_deltas),
        "split_units": len(units),
        "initial_states_per_split": initial_counts,
        "bootstrap_samples": bootstrap_samples,
        "note": "paired bootstrap resamples split units and paired validation initial states; repeated rollouts per initial state are averaged first",
    }


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    out = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return out


def build_report(summary_rows: list[dict[str, object]], per_split_rows: list[dict[str, object]]) -> str:
    columns = [
        "scope",
        "selected_success",
        "selected_episodes",
        "selected_rate",
        "best_baseline_success",
        "best_baseline_episodes",
        "best_baseline_rate",
        "pooled_delta",
        "paired_bootstrap95_low",
        "paired_bootstrap95_high",
        "split_signs",
        "split_sign_p_two_sided",
    ]
    split_columns = [
        "setting_label",
        "split_seed",
        "selected_method",
        "selected_success",
        "best_baseline_method",
        "best_baseline_success",
        "margin",
    ]
    lines = [
        "# v0.2 Fresh Gate Uncertainty Audit",
        "",
        "This report adds descriptive uncertainty checks to the frozen `METHOD_FREEZE_V02.md` fresh Can+Lift gate.",
        "Rows compare the router-selected branch against the best completed non-oracle baseline within each split.",
        "Wilson intervals describe pooled endpoint rates; paired bootstrap intervals average repeated rollouts by `initial_demo_id`, then resample split units and paired validation initial states.",
        "The intervals are wording guardrails rather than formal independent tests because there are only three split seeds per setting.",
        "",
        "## Aggregate And Paired-Bootstrap Read",
        "",
        *markdown_table(summary_rows, columns),
        "",
        "## Split Margins",
        "",
        *markdown_table(per_split_rows, split_columns),
        "",
        "## Interpretation",
        "",
        "- Can 40p/80b remains the clean v0.2 result: the selected hard-union branch wins all three fresh splits.",
        "- Lift MG remains modest: the selected weighted branch wins two splits, loses one, and has a paired-bootstrap interval that crosses zero.",
        "- The combined Can+Lift gate is positive, but it should still be framed as branch-selection evidence because the Lift gain is small and uses the weighted branch.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    out_dir = args.out_dir or args.root / "tables"
    task_endpoint_rows = rows_by_task(args.root)
    gate_per_split = read_csv(args.root / "tables" / "v02_fresh_gate_per_split.csv")

    paired_rows: list[dict[str, object]] = []
    split_delta_by_key: dict[tuple[str, int], float] = {}
    for row in gate_per_split:
        rows, split_delta = split_delta_rows(
            args.root,
            row["setting_label"],
            int(row["split_seed"]),
            row["selected_method"],
            row["best_baseline_method"],
            task_endpoint_rows,
        )
        paired_rows.extend(rows)
        split_delta_by_key[(row["setting_label"], int(row["split_seed"]))] = split_delta

    per_split_rows: list[dict[str, object]] = []
    for row in gate_per_split:
        per_split_rows.append(
            {
                **row,
                "paired_initial_delta": f"{split_delta_by_key[(row['setting_label'], int(row['split_seed']))]:+.3f}",
            }
        )

    scopes = [
        ("Can 40p/80b", [row for row in gate_per_split if row["setting_label"] == "Can 40p/80b"]),
        ("Lift MG", [row for row in gate_per_split if row["setting_label"] == "Lift MG"]),
        ("Combined Can+Lift", gate_per_split),
    ]
    summary_rows = [
        scope_summary(scope, rows, paired_rows, args.bootstrap_samples, args.bootstrap_seed)
        for scope, rows in scopes
    ]

    write_csv(
        out_dir / "v02_fresh_gate_uncertainty.csv",
        summary_rows,
        [
            "scope",
            "selected_success",
            "selected_episodes",
            "selected_rate",
            "selected_wilson95_low",
            "selected_wilson95_high",
            "best_baseline_success",
            "best_baseline_episodes",
            "best_baseline_rate",
            "best_baseline_wilson95_low",
            "best_baseline_wilson95_high",
            "pooled_delta",
            "paired_bootstrap_delta",
            "paired_bootstrap95_low",
            "paired_bootstrap95_high",
            "split_mean_delta",
            "split_std_delta",
            "split_signs",
            "split_sign_p_two_sided",
            "split_units",
            "initial_states_per_split",
            "bootstrap_samples",
            "note",
        ],
    )
    write_csv(
        out_dir / "v02_fresh_gate_paired_initial_deltas.csv",
        paired_rows,
        [
            "setting_label",
            "split_seed",
            "selected_method",
            "best_baseline_method",
            "initial_demo_id",
            "selected_success_rate",
            "best_baseline_success_rate",
            "delta",
        ],
    )
    write_csv(
        out_dir / "v02_fresh_gate_uncertainty_per_split.csv",
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
            "paired_initial_delta",
        ],
    )
    report_path = out_dir / "v02_fresh_gate_uncertainty_REPORT.md"
    report_path.write_text(build_report(summary_rows, per_split_rows), encoding="utf-8")
    print(f"wrote {out_dir / 'v02_fresh_gate_uncertainty.csv'}")
    print(f"wrote {out_dir / 'v02_fresh_gate_paired_initial_deltas.csv'}")
    print(f"wrote {out_dir / 'v02_fresh_gate_uncertainty_per_split.csv'}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
