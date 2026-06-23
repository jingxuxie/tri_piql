from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/robomimic_lift_mg_posonly_nn_top160_3seed_summary"),
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str | int | float]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = mean(values)
    return (sum((value - avg) ** 2 for value in values) / (len(values) - 1)) ** 0.5


def epoch_from_name(name: str) -> int:
    match = re.search(r"model_epoch_(\d+)", name)
    if not match:
        raise ValueError(name)
    return int(match.group(1))


def load_setup(path: Path) -> dict:
    return json.loads((path / "diagnostics.json").read_text(encoding="utf-8"))


def setup_row(method: str, setup_dir: Path, seed: int | None = None) -> dict[str, str | int | float]:
    diagnostics = load_setup(setup_dir)
    selection = diagnostics.get("selection_diagnostics", {})
    selected = int(selection.get("selected_demo_count", 0))
    hidden_positive = int(selection.get("selected_hidden_positive_demos", 0))
    hidden_bad = int(selection.get("selected_hidden_bad_demos", 0))
    purity = float(selection.get("selected_hidden_positive_purity", 1.0 if selected == 0 else 0.0))
    row: dict[str, str | int | float] = {
        "method": method,
        "train_demos": int(diagnostics["train_demo_count"]),
        "selected_unlabeled": selected,
        "hidden_positive": hidden_positive,
        "hidden_bad": hidden_bad,
        "purity": purity,
    }
    if seed is not None:
        row = {"method": method, "seed": seed, **row}
    return row


def policy_rows(method: str, eval_dir: Path, seed: int | None = None) -> list[dict[str, str | int | float]]:
    rows = []
    for row in read_csv(eval_dir / "metrics.csv"):
        item: dict[str, str | int | float] = {
            "method": method,
            "epoch": epoch_from_name(row["checkpoint_name"]),
            "success": float(row["success_rate"]),
            "avg_return": float(row["avg_return"]),
            "avg_len": float(row["avg_len"]),
            "eval_episodes": int(row["eval_episodes"]),
        }
        if seed is not None:
            item = {"method": method, "seed": seed, **item}
        rows.append(item)
    return rows


def aggregate_policy(policy: list[dict[str, str | int | float]]) -> list[dict[str, str | int | float]]:
    grouped: dict[tuple[str, int], list[dict[str, str | int | float]]] = defaultdict(list)
    for row in policy:
        grouped[(str(row["method"]), int(row["epoch"]))].append(row)

    rows = []
    for (method, epoch), items in sorted(grouped.items()):
        successes = [float(item["success"]) for item in items]
        returns = [float(item["avg_return"]) for item in items]
        lens = [float(item["avg_len"]) for item in items]
        rows.append(
            {
                "method": method,
                "epoch": epoch,
                "n_seeds": len(items),
                "mean_success": mean(successes),
                "std_success": std(successes),
                "min_success": min(successes),
                "max_success": max(successes),
                "mean_return": mean(returns),
                "mean_len": mean(lens),
            }
        )
    return rows


def aggregate_best(policy: list[dict[str, str | int | float]]) -> list[dict[str, str | int | float]]:
    grouped: dict[tuple[str, int], list[dict[str, str | int | float]]] = defaultdict(list)
    for row in policy:
        grouped[(str(row["method"]), int(row["seed"]))].append(row)

    best_by_seed = []
    for (method, seed), items in sorted(grouped.items()):
        best = max(float(item["success"]) for item in items)
        best_by_seed.append({"method": method, "seed": seed, "best_success": best})

    by_method: dict[str, list[float]] = defaultdict(list)
    for row in best_by_seed:
        by_method[str(row["method"])].append(float(row["best_success"]))

    return [
        {
            "method": method,
            "n_seeds": len(values),
            "mean_oracle_best_success": mean(values),
            "std_oracle_best_success": std(values),
            "min_oracle_best_success": min(values),
            "max_oracle_best_success": max(values),
        }
        for method, values in sorted(by_method.items())
    ]


def table_values(
    aggregate: list[dict[str, str | int | float]],
    best_rows: list[dict[str, str | int | float]],
    method: str,
) -> dict[str, float]:
    by_epoch = {int(row["epoch"]): row for row in aggregate if row["method"] == method}
    best = {str(row["method"]): row for row in best_rows}[method]
    return {
        "e50": float(by_epoch[50]["mean_success"]),
        "e100": float(by_epoch[100]["mean_success"]),
        "e150": float(by_epoch[150]["mean_success"]),
        "e200": float(by_epoch[200]["mean_success"]),
        "oracle": float(best["mean_oracle_best_success"]),
    }


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    support_sweep_specs = [
        ("posonly_nn_top80", Path("results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top80_seed0_setup")),
        ("posonly_nn_top160", Path("results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed0_setup")),
        ("posonly_nn_top240", Path("results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top240_seed0_setup")),
        ("posonly_nn_top320", Path("results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top320_seed0_setup")),
        ("bad_aware_pos_min", Path("results/robomimic_lift_mg_official_bc_rnn_posmin_seed0_setup")),
    ]
    support_sweep_rows = [setup_row(method, path, seed=0) for method, path in support_sweep_specs]
    write_csv(args.out_dir / "support_sweep_seed0.csv", support_sweep_rows)

    compare_specs = [
        (
            "posonly_nn_top160",
            seed,
            Path(f"results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed{seed}_setup"),
            Path(f"results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed{seed}_eval"),
        )
        for seed in range(3)
    ] + [
        (
            "bad_aware_pos_min",
            seed,
            Path(f"results/robomimic_lift_mg_official_bc_rnn_posmin_seed{seed}_setup"),
            Path(f"results/robomimic_lift_mg_official_bc_rnn_posmin_seed{seed}_eval"),
        )
        for seed in range(3)
    ]
    support_rows = [setup_row(method, setup_dir, seed=seed) for method, seed, setup_dir, _ in compare_specs]
    write_csv(args.out_dir / "support_by_seed.csv", support_rows)

    policy = [
        row
        for method, seed, _, eval_dir in compare_specs
        for row in policy_rows(method, eval_dir, seed=seed)
    ]
    write_csv(args.out_dir / "policy_by_seed.csv", policy)

    aggregate = aggregate_policy(policy)
    write_csv(args.out_dir / "policy_aggregate.csv", aggregate)

    best_rows = aggregate_best(policy)
    write_csv(args.out_dir / "oracle_best_by_method.csv", best_rows)

    report = [
        "# Robomimic Lift Positive-Only NN Control",
        "",
        "This diagnostic tests a no-bad-label nearest-neighbor support selector on the Lift MG sparse split.",
        "It uses the same official Robomimic BC-RNN-GMM backbone and the same three policy seeds as the bad-aware Lift control.",
        "",
        "## Seed-0 Support Sweep",
        "",
        "| method | train demos | selected unlabeled | hidden positive | hidden bad | purity |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in support_sweep_rows:
        report.append(
            f"| {row['method']} | {row['train_demos']} | {row['selected_unlabeled']} | "
            f"{row['hidden_positive']} | {row['hidden_bad']} | {fmt(float(row['purity']))} |"
        )

    report.extend(
        [
            "",
            "## Three-Seed Policy Results",
            "",
            "| method | 5k mean | 10k mean | 15k mean | 20k mean | oracle-by-seed mean |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for method in ["posonly_nn_top160", "bad_aware_pos_min"]:
        values = table_values(aggregate, best_rows, method)
        report.append(
            f"| {method} | {fmt(values['e50'])} | {fmt(values['e100'])} | "
            f"{fmt(values['e150'])} | {fmt(values['e200'])} | {fmt(values['oracle'])} |"
        )

    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Positive-only NN has a sharp precision/coverage tradeoff on Lift MG: top80 is high purity (`0.975`) but recovers only 78 hidden-positive demos; top160 recovers 126 hidden positives but already admits 34 hidden-bad demos.",
            "- Broad positive-only NN support degrades quickly: top240 has purity `0.596` and top320 has purity `0.512`.",
            "- Across three policy seeds, bad-aware `pos_min` is stronger at the fixed 15k and 20k budgets and under oracle-by-seed checkpoint selection.",
            "- The no-bad-label top160 policy is not collapsed, but it does not remove the need for explicit bad-demo calibration on Lift MG.",
        ]
    )
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
