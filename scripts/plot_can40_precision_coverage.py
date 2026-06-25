from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-tri-piql")

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize


DEFAULT_INPUT = Path("results/final_paper/ablations/can40_score_support_tradeoff.csv")
DEFAULT_OUT_DIR = Path("results/final_paper/figures")

DISPLAY_NAMES = {
    "classifier_top10": "top10",
    "classifier_top20": "top20",
    "classifier_top40": "top40",
    "classifier_top60": "top60",
    "classifier_top80": "top80",
    "triage_adaptive_masscap": "TRIAGE-BC",
    "weighted_full_pool": "weighted BC",
    "positive_only_nn_top40": "positive-only NN",
}

METHOD_MARKERS = {
    "triage_adaptive_masscap": "o",
    "weighted_full_pool": "s",
    "positive_only_nn_top40": "^",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value == "":
        return float("nan")
    return float(value)


def plot(rows: list[dict[str, str]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    classifier_rows = [
        row for row in rows if row["support_rule"].startswith("classifier_top")
    ]
    classifier_rows = sorted(classifier_rows, key=lambda row: as_float(row, "mean_selected"))
    method_rows = [
        row
        for row in rows
        if row["support_rule"]
        in {"triage_adaptive_masscap", "weighted_full_pool", "positive_only_nn_top40"}
    ]

    fig, ax = plt.subplots(figsize=(7.1, 4.6))

    frontier_x = [as_float(row, "hidden_positive_recall") for row in classifier_rows]
    frontier_y = [as_float(row, "hidden_bad_admission") for row in classifier_rows]
    ax.plot(
        frontier_x,
        frontier_y,
        color="#6b7280",
        linewidth=1.6,
        linestyle="--",
        marker="o",
        markersize=5,
        markerfacecolor="white",
        markeredgecolor="#374151",
        label="classifier top-k support",
        zorder=2,
    )

    for row in classifier_rows:
        x = as_float(row, "hidden_positive_recall")
        y = as_float(row, "hidden_bad_admission")
        ax.annotate(
            DISPLAY_NAMES[row["support_rule"]],
            (x, y),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
            color="#374151",
        )

    successes = [as_float(row, "endpoint_success") for row in method_rows]
    norm = Normalize(vmin=min(successes), vmax=max(successes))
    cmap = plt.get_cmap("viridis")

    for row in method_rows:
        rule = row["support_rule"]
        x = as_float(row, "hidden_positive_recall")
        y = as_float(row, "hidden_bad_admission")
        success = as_float(row, "endpoint_success")
        ax.scatter(
            [x],
            [y],
            s=120,
            marker=METHOD_MARKERS[rule],
            c=[success],
            cmap=cmap,
            norm=norm,
            edgecolors="#111827",
            linewidths=0.9,
            zorder=3,
        )
        label = f"{DISPLAY_NAMES[rule]} ({success:.2f})"
        if rule == "positive_only_nn_top40":
            label = f"{DISPLAY_NAMES[rule]}\n({success:.2f})"
        offset = {
            "triage_adaptive_masscap": (-70, 8),
            "weighted_full_pool": (-92, -2),
            "positive_only_nn_top40": (-115, -8),
        }[rule]
        ax.annotate(
            label,
            (x, y),
            xytext=offset,
            textcoords="offset points",
            fontsize=8.5,
            color="#111827",
            linespacing=0.95,
        )

    colorbar = fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=ax,
        pad=0.015,
    )
    colorbar.set_label("Endpoint success", fontsize=9)

    ax.set_title("Can 40p/80b Precision-Coverage Tradeoff", fontsize=12)
    ax.set_xlabel("Hidden-positive recall")
    ax.set_ylabel("Hidden-bad admission")
    ax.set_xlim(0.15, 1.04)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(True, color="#e5e7eb", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=8)

    note = "Top-k points are support-only; colored markers include 50-episode endpoint results."
    fig.text(0.12, 0.01, note, ha="left", va="bottom", fontsize=8, color="#4b5563")
    fig.tight_layout(rect=(0, 0.04, 1, 1))

    for suffix in ["png", "pdf"]:
        fig.savefig(out_dir / f"can40_precision_coverage.{suffix}", dpi=220)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    plot(read_rows(args.input), args.out_dir)
    print(f"wrote {args.out_dir / 'can40_precision_coverage.png'}")
    print(f"wrote {args.out_dir / 'can40_precision_coverage.pdf'}")


if __name__ == "__main__":
    main()
