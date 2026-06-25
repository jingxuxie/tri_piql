from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-tri-piql")

import matplotlib.pyplot as plt


TABLE_DIR = Path("results/final_paper/tables")
FIG_DIR = Path("results/final_paper/figures")
PER_SEED = Path("results/final_paper/per_seed")
SPLIT_SEEDS = [11, 22, 33]

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

SPLIT_COLORS = {
    11: "#2563eb",
    22: "#f59e0b",
    33: "#16a34a",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table-dir", type=Path, default=TABLE_DIR)
    parser.add_argument("--fig-dir", type=Path, default=FIG_DIR)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot average an empty list")
    return sum(values) / len(values)


def method_episode_path(task: str, split_seed: int, method: str) -> Path:
    task_cfg = TASKS[task]
    method_slug = task_cfg["methods"][method]
    run_name = f"{task_cfg['prefix']}_split{split_seed}_{method_slug}_policy0"
    return PER_SEED / run_name / "eval" / "episode_metrics.csv"


def read_episode_successes(path: Path) -> dict[str, list[float]]:
    if not path.exists():
        raise FileNotFoundError(path)
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in read_rows(path):
        grouped[row["initial_demo_id"]].append(float(row["success"]))
    if not grouped:
        raise ValueError(f"empty episode metrics: {path}")
    return dict(grouped)


def paired_delta_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for task, left_method, right_method in COMPARISONS:
        for split_seed in SPLIT_SEEDS:
            left = read_episode_successes(method_episode_path(task, split_seed, left_method))
            right = read_episode_successes(method_episode_path(task, split_seed, right_method))
            if set(left) != set(right):
                raise ValueError(
                    f"initial IDs do not match for {task} split {split_seed}: "
                    f"{left_method} vs {right_method}"
                )
            for initial_demo_id in sorted(left):
                left_mean = mean(left[initial_demo_id])
                right_mean = mean(right[initial_demo_id])
                rows.append(
                    {
                        "task": task,
                        "comparison": f"{left_method} - {right_method}",
                        "left_method": left_method,
                        "right_method": right_method,
                        "split_seed": str(split_seed),
                        "initial_demo_id": initial_demo_id,
                        "left_success_mean": f"{left_mean:.3f}",
                        "right_success_mean": f"{right_mean:.3f}",
                        "paired_delta": f"{left_mean - right_mean:.3f}",
                        "left_rollouts": str(len(left[initial_demo_id])),
                        "right_rollouts": str(len(right[initial_demo_id])),
                    }
                )
    return rows


def read_bootstrap_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows = read_rows(path)
    return {(row["task"], row["comparison"]): row for row in rows}


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return lines


def write_report(
    path: Path,
    bootstrap_rows: dict[tuple[str, str], dict[str, str]],
    delta_rows: list[dict[str, str]],
) -> None:
    summary_rows = []
    for task, left_method, right_method in COMPARISONS:
        comparison = f"{left_method} - {right_method}"
        row = bootstrap_rows[(task, comparison)]
        num_initial_rows = sum(
            1
            for delta_row in delta_rows
            if delta_row["task"] == task and delta_row["comparison"] == comparison
        )
        summary_rows.append(
            {
                "task": task,
                "comparison": comparison,
                "point_delta": row["point_delta"],
                "bootstrap95_low": row["bootstrap95_low"],
                "bootstrap95_high": row["bootstrap95_high"],
                "split_signs": row["split_signs"],
                "paired_initial_rows": str(num_initial_rows),
            }
        )
    columns = [
        "task",
        "comparison",
        "point_delta",
        "bootstrap95_low",
        "bootstrap95_high",
        "split_signs",
        "paired_initial_rows",
    ]
    lines = [
        "# Primary Endpoint Paired Initial-State Delta Figure",
        "",
        "This report stages the final-evaluation uncertainty figure requested by the paper plan.",
        "Each plotted point is a per-initial-state paired endpoint-success delta after averaging repeated rollouts from the same validation-positive start.",
        "Black intervals are the existing bootstrap intervals that resample split seeds and paired initial states.",
        "",
        *markdown_table(summary_rows, columns),
        "",
        "## Artifacts",
        "",
        "- CSV: `results/final_paper/tables/primary_endpoint_paired_initial_deltas.csv`",
        "- PNG: `results/final_paper/figures/primary_endpoint_paired_deltas.png`",
        "- PDF: `results/final_paper/figures/primary_endpoint_paired_deltas.pdf`",
        "",
        "## Interpretation Guardrail",
        "",
        "The figure is a descriptive uncertainty visualization, not a formal independent significance test.",
        "It makes the repeated-start structure visible and reinforces the paper wording that primary endpoint gaps are directional and split-sensitive.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(
    path: Path,
    delta_rows: list[dict[str, str]],
    bootstrap_rows: dict[tuple[str, str], dict[str, str]],
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), sharex=True)
    task_to_axis = {"Can 40p/80b": axes[0], "Lift MG": axes[1]}

    for task, ax in task_to_axis.items():
        task_comparisons = [comparison for comparison in COMPARISONS if comparison[0] == task]
        labels = [f"{left}\nminus {right}" for _, left, right in task_comparisons]
        y_positions = list(range(len(task_comparisons)))[::-1]

        for y_pos, (_, left_method, right_method) in zip(y_positions, task_comparisons):
            comparison = f"{left_method} - {right_method}"
            rows = [
                row
                for row in delta_rows
                if row["task"] == task and row["comparison"] == comparison
            ]
            for split_index, split_seed in enumerate(SPLIT_SEEDS):
                split_rows = [row for row in rows if row["split_seed"] == str(split_seed)]
                split_rows = sorted(split_rows, key=lambda row: row["initial_demo_id"])
                count = max(1, len(split_rows) - 1)
                for initial_index, row in enumerate(split_rows):
                    jitter = ((initial_index / count) - 0.5) * 0.22
                    split_offset = (split_index - 1) * 0.08
                    ax.scatter(
                        float(row["paired_delta"]),
                        y_pos + split_offset + jitter,
                        s=18,
                        color=SPLIT_COLORS[split_seed],
                        alpha=0.58,
                        edgecolors="none",
                    )

            boot = bootstrap_rows[(task, comparison)]
            point = float(boot["point_delta"])
            low = float(boot["bootstrap95_low"])
            high = float(boot["bootstrap95_high"])
            ax.plot([low, high], [y_pos, y_pos], color="#111827", linewidth=2.0, zorder=4)
            ax.scatter(
                [point],
                [y_pos],
                marker="D",
                s=44,
                color="#111827",
                edgecolors="white",
                linewidths=0.5,
                zorder=5,
            )

        ax.axvline(0.0, color="#6b7280", linewidth=1.0, linestyle="--")
        ax.set_title(task, fontsize=12)
        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels, fontsize=8.5)
        ax.set_xlim(-1.05, 1.05)
        ax.set_xlabel("Paired endpoint success delta")
        ax.grid(axis="x", color="#e5e7eb", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    handles = [
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=SPLIT_COLORS[seed], markersize=6, label=f"split {seed}")
        for seed in SPLIT_SEEDS
    ]
    handles.append(
        plt.Line2D([0], [0], marker="D", color="#111827", markerfacecolor="#111827", markersize=5, label="bootstrap point/interval")
    )
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=8.5)
    fig.suptitle("Primary Endpoint Paired Initial-State Deltas", fontsize=13)
    fig.text(
        0.5,
        0.045,
        "Points are validation-start means; black intervals resample split seeds and paired initial states.",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.09, 1, 0.95))
    for suffix in ["png", "pdf"]:
        fig.savefig(path.with_suffix(f".{suffix}"), dpi=220)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    args.table_dir.mkdir(parents=True, exist_ok=True)
    args.fig_dir.mkdir(parents=True, exist_ok=True)

    delta_rows = paired_delta_rows()
    delta_csv = args.table_dir / "primary_endpoint_paired_initial_deltas.csv"
    write_csv(delta_csv, delta_rows)

    bootstrap_csv = args.table_dir / "primary_endpoint_paired_bootstrap.csv"
    bootstrap_rows = read_bootstrap_rows(bootstrap_csv)
    report_path = args.table_dir / "primary_endpoint_paired_deltas_REPORT.md"
    write_report(report_path, bootstrap_rows, delta_rows)

    figure_path = args.fig_dir / "primary_endpoint_paired_deltas"
    plot(figure_path, delta_rows, bootstrap_rows)

    print(f"wrote {delta_csv}")
    print(f"wrote {report_path}")
    print(f"wrote {figure_path.with_suffix('.png')}")
    print(f"wrote {figure_path.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
