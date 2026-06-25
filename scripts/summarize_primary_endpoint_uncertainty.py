from __future__ import annotations

import csv
import math
from pathlib import Path


OUT_DIR = Path("results/final_paper/tables")

CAN40_SOURCE = OUT_DIR / "can_paired_pos40_bad80_final_endpoint_summary.csv"
LIFT_SOURCE = OUT_DIR / "lift_mg_mg_sparse_final_endpoint_summary.csv"

METHOD_ORDER = [
    "all-demo BC",
    "weighted BC",
    "positive-only NN",
    "TRIAGE-BC",
    "all-positive oracle",
]

PAIRWISE_COMPARISONS = [
    ("Can 40p/80b", "TRIAGE-BC", "weighted BC"),
    ("Can 40p/80b", "TRIAGE-BC", "all-demo BC"),
    ("Can 40p/80b", "TRIAGE-BC", "positive-only NN"),
    ("Lift MG", "weighted BC", "TRIAGE-BC"),
    ("Lift MG", "weighted BC", "positive-only NN"),
    ("Lift MG", "TRIAGE-BC", "all-demo BC"),
]


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


def fmt(value: float | int | str, digits: int = 3) -> str:
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return value
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return float("nan")
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def wilson_interval(successes: int, episodes: int, z: float = 1.96) -> tuple[float, float]:
    if episodes <= 0:
        return float("nan"), float("nan")
    p_hat = successes / episodes
    denom = 1.0 + z**2 / episodes
    center = (p_hat + z**2 / (2.0 * episodes)) / denom
    radius = z * math.sqrt((p_hat * (1.0 - p_hat) + z**2 / (4.0 * episodes)) / episodes) / denom
    return max(0.0, center - radius), min(1.0, center + radius)


def load_can40() -> dict[tuple[str, str], dict[str, float | int]]:
    rows = read_rows(CAN40_SOURCE)
    split_rows = [row for row in rows if row["split_seed"] != "aggregate"]
    aggregate = next(row for row in rows if row["split_seed"] == "aggregate")
    methods = {
        "all-demo BC": ("all_demo_success_rate", "all_demo_successes"),
        "weighted BC": ("weighted_success_rate", "weighted_successes"),
        "positive-only NN": ("positive_only_nn_success_rate", "positive_only_nn_successes"),
        "TRIAGE-BC": ("triage_success_rate", "triage_successes"),
        "all-positive oracle": ("all_positive_oracle_success_rate", "all_positive_oracle_successes"),
    }
    records: dict[tuple[str, str], dict[str, float | int]] = {}
    for method, (rate_key, successes_key) in methods.items():
        split_rates = [float(row[rate_key]) for row in split_rows]
        split_successes = [int(row[successes_key]) for row in split_rows]
        successes = int(aggregate[successes_key])
        episodes = int(aggregate["eval_episodes"])
        lower, upper = wilson_interval(successes, episodes)
        records[("Can 40p/80b", method)] = {
            "successes": successes,
            "episodes": episodes,
            "pooled_success_rate": successes / episodes,
            "wilson95_low": lower,
            "wilson95_high": upper,
            "split_mean": sum(split_rates) / len(split_rates),
            "split_std": sample_std(split_rates),
            "split11": split_rates[0],
            "split22": split_rates[1],
            "split33": split_rates[2],
            "split11_successes": split_successes[0],
            "split22_successes": split_successes[1],
            "split33_successes": split_successes[2],
        }
    return records


def load_lift() -> dict[tuple[str, str], dict[str, float | int]]:
    rows = read_rows(LIFT_SOURCE)
    methods = {
        "all-demo BC": "all-demo BC",
        "weighted BC": "weighted BC",
        "positive-only NN": "positive-only NN top160",
        "TRIAGE-BC": "TRIAGE-BC / pos-min",
        "all-positive oracle": "all-positive oracle",
    }
    rows_by_source_method = {row["method"]: row for row in rows}
    records: dict[tuple[str, str], dict[str, float | int]] = {}
    for method, source_method in methods.items():
        row = rows_by_source_method[source_method]
        split_successes = [
            int(row["split11_successes"]),
            int(row["split22_successes"]),
            int(row["split33_successes"]),
        ]
        split_rates = [successes / 50 for successes in split_successes]
        successes = int(row["pooled_successes"])
        episodes = int(row["pooled_episodes"])
        lower, upper = wilson_interval(successes, episodes)
        records[("Lift MG", method)] = {
            "successes": successes,
            "episodes": episodes,
            "pooled_success_rate": successes / episodes,
            "wilson95_low": lower,
            "wilson95_high": upper,
            "split_mean": sum(split_rates) / len(split_rates),
            "split_std": sample_std(split_rates),
            "split11": split_rates[0],
            "split22": split_rates[1],
            "split33": split_rates[2],
            "split11_successes": split_successes[0],
            "split22_successes": split_successes[1],
            "split33_successes": split_successes[2],
        }
    return records


def endpoint_rows(records: dict[tuple[str, str], dict[str, float | int]]) -> list[dict[str, str]]:
    rows = []
    for task in ["Can 40p/80b", "Lift MG"]:
        for method in METHOD_ORDER:
            record = records[(task, method)]
            rows.append(
                {
                    "task": task,
                    "method": method,
                    "successes": fmt(record["successes"]),
                    "episodes": fmt(record["episodes"]),
                    "pooled_success_rate": fmt(record["pooled_success_rate"]),
                    "wilson95_low": fmt(record["wilson95_low"]),
                    "wilson95_high": fmt(record["wilson95_high"]),
                    "split_mean": fmt(record["split_mean"]),
                    "split_std": fmt(record["split_std"]),
                    "split11_success_rate": fmt(record["split11"]),
                    "split22_success_rate": fmt(record["split22"]),
                    "split33_success_rate": fmt(record["split33"]),
                    "split11_successes": fmt(record["split11_successes"]),
                    "split22_successes": fmt(record["split22_successes"]),
                    "split33_successes": fmt(record["split33_successes"]),
                }
            )
    return rows


def pairwise_rows(records: dict[tuple[str, str], dict[str, float | int]]) -> list[dict[str, str]]:
    rows = []
    for task, left_method, right_method in PAIRWISE_COMPARISONS:
        left = records[(task, left_method)]
        right = records[(task, right_method)]
        split_deltas = [
            float(left["split11"]) - float(right["split11"]),
            float(left["split22"]) - float(right["split22"]),
            float(left["split33"]) - float(right["split33"]),
        ]
        pooled_delta = float(left["pooled_success_rate"]) - float(right["pooled_success_rate"])
        rows.append(
            {
                "task": task,
                "comparison": f"{left_method} - {right_method}",
                "pooled_delta": fmt(pooled_delta),
                "split_mean_delta": fmt(sum(split_deltas) / len(split_deltas)),
                "split_std_delta": fmt(sample_std(split_deltas)),
                "split11_delta": fmt(split_deltas[0]),
                "split22_delta": fmt(split_deltas[1]),
                "split33_delta": fmt(split_deltas[2]),
                "direction_consistent": str(all(delta > 0 for delta in split_deltas) or all(delta < 0 for delta in split_deltas)).lower(),
            }
        )
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return lines


def write_report(path: Path, endpoint: list[dict[str, str]], pairwise: list[dict[str, str]]) -> None:
    endpoint_columns = [
        "task",
        "method",
        "successes",
        "episodes",
        "pooled_success_rate",
        "wilson95_low",
        "wilson95_high",
        "split_mean",
        "split_std",
    ]
    pairwise_columns = [
        "task",
        "comparison",
        "pooled_delta",
        "split_mean_delta",
        "split_std_delta",
        "direction_consistent",
    ]
    lines = [
        "# Primary Endpoint Uncertainty Summary",
        "",
        "This report adds descriptive uncertainty summaries to the primary frozen Robomimic endpoint matrix.",
        "Wilson intervals treat the pooled 150 rollouts as Bernoulli trials, while split means and standard deviations summarize variation across the three frozen split seeds.",
        "Because rollouts reuse validation-positive start pools within each split, these intervals should be read as descriptive error bars, not as fully independent statistical tests.",
        "",
        "## Pooled Rates And Split Variation",
        "",
        *markdown_table(endpoint, endpoint_columns),
        "",
        "## Paired Split Deltas",
        "",
        *markdown_table(pairwise, pairwise_columns),
        "",
        "## Interpretation",
        "",
        "- Can 40p/80b favors TRIAGE-BC over weighted BC on every split, but the pooled gap is small (`+0.060`) and the rollout-level Wilson intervals overlap.",
        "- Can 40p/80b does not support a TRIAGE-over-positive-only claim: positive-only NN is higher pooled and the split deltas change sign.",
        "- Lift MG favors weighted BC over TRIAGE-BC pooled (`+0.127`) and on two of three splits, while all-demo BC remains consistently weak.",
        "- These summaries support cautious wording: report counts, split context, and direction of paired split deltas rather than making strong significance claims.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = {}
    records.update(load_can40())
    records.update(load_lift())
    endpoint = endpoint_rows(records)
    pairwise = pairwise_rows(records)
    endpoint_path = OUT_DIR / "primary_endpoint_uncertainty.csv"
    pairwise_path = OUT_DIR / "primary_endpoint_pairwise_deltas.csv"
    report_path = OUT_DIR / "primary_endpoint_uncertainty_REPORT.md"
    write_csv(endpoint_path, endpoint)
    write_csv(pairwise_path, pairwise)
    write_report(report_path, endpoint, pairwise)
    print(f"wrote {endpoint_path}")
    print(f"wrote {pairwise_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
