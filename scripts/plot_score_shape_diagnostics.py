from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-tri-piql")

import matplotlib.pyplot as plt


OUT_DIR = Path("results/final_paper/tables")
FIG_DIR = Path("results/final_paper/figures")


ANALYSES = [
    {
        "analysis": "Can 40p/80b",
        "status": "primary_frozen_3split",
        "dirs": [
            Path("results/final_paper/score_diagnostics/can_paired_pos40_bad80_split11_policy0"),
            Path("results/final_paper/score_diagnostics/can_paired_pos40_bad80_split22_policy0"),
            Path("results/final_paper/score_diagnostics/can_paired_pos40_bad80_split33_policy0"),
        ],
        "rule_name": "adaptive_masscap",
        "threshold_field": "selected_score_min",
        "threshold_name": "adaptive_masscap selected-min",
        "message": "intermediate overlap; mass-capped hard support",
    },
    {
        "analysis": "Lift MG",
        "status": "primary_frozen_3split",
        "dirs": [
            Path("results/final_paper/score_diagnostics/lift_mg_mg_sparse_split11_policy0"),
            Path("results/final_paper/score_diagnostics/lift_mg_mg_sparse_split22_policy0"),
            Path("results/final_paper/score_diagnostics/lift_mg_mg_sparse_split33_policy0"),
        ],
        "rule_name": "pos_min",
        "threshold_field": "threshold",
        "threshold_name": "pos-min threshold",
        "message": "high-purity hard support but endpoint under-covers",
    },
    {
        "analysis": "Can MG",
        "status": "stress_diagnostic_original",
        "dirs": [Path("results/robomimic_selector_score_analysis_can_mg")],
        "rule_name": "pos_min",
        "threshold_field": "threshold",
        "threshold_name": "pos-min threshold",
        "message": "large ambiguous high-score plateau; router-v2 abstains",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--fig-dir", type=Path, default=FIG_DIR)
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


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    pos = (len(values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return values[lo]
    weight = pos - lo
    return values[lo] * (1.0 - weight) + values[hi] * weight


def fmt(value: float | int | str | None, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def load_demo_scores(dirs: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for directory in dirs:
        for row in read_rows(directory / "demo_rankings.csv"):
            enriched = dict(row)
            enriched["analysis_dir"] = str(directory)
            rows.append(enriched)
    return rows


def load_thresholds(dirs: list[Path], rule_name: str, threshold_field: str) -> list[float]:
    thresholds: list[float] = []
    for directory in dirs:
        for row in read_rows(directory / "selection_rules.csv"):
            if row["threshold_name"] != rule_name:
                continue
            raw = row.get(threshold_field, "")
            if raw:
                thresholds.append(float(raw))
    return thresholds


def summarize_analysis(config: dict[str, object]) -> tuple[dict[str, str], dict[str, list[float]], float]:
    rows = load_demo_scores(config["dirs"])  # type: ignore[arg-type]
    scores_by_label = {
        "positive": [float(row["score"]) for row in rows if row["hidden_label"] == "positive"],
        "bad": [float(row["score"]) for row in rows if row["hidden_label"] == "bad"],
    }
    thresholds = load_thresholds(
        config["dirs"],  # type: ignore[arg-type]
        str(config["rule_name"]),
        str(config["threshold_field"]),
    )
    threshold = sum(thresholds) / len(thresholds) if thresholds else float("nan")
    pos = scores_by_label["positive"]
    bad = scores_by_label["bad"]
    summary = {
        "analysis": str(config["analysis"]),
        "status": str(config["status"]),
        "num_scores": str(len(rows)),
        "positive_count": str(len(pos)),
        "bad_count": str(len(bad)),
        "positive_mean": fmt(sum(pos) / len(pos)),
        "bad_mean": fmt(sum(bad) / len(bad)),
        "positive_p10": fmt(percentile(pos, 0.10)),
        "bad_p90": fmt(percentile(bad, 0.90)),
        "positive_frac_ge_0p95": fmt(sum(score >= 0.95 for score in pos) / len(pos)),
        "bad_frac_ge_0p95": fmt(sum(score >= 0.95 for score in bad) / len(bad)),
        "plotted_threshold": fmt(threshold),
        "threshold_name": str(config["threshold_name"]),
        "message": str(config["message"]),
    }
    return summary, scores_by_label, threshold


def table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[col] for col in columns) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    columns = [
        "analysis",
        "status",
        "positive_count",
        "bad_count",
        "positive_mean",
        "bad_mean",
        "positive_frac_ge_0p95",
        "bad_frac_ge_0p95",
        "plotted_threshold",
        "message",
    ]
    lines = [
        "# Score-Shape Diagnostics",
        "",
        "This report consolidates score-distribution diagnostics for the current Figure 4 candidate.",
        "Can 40p/80b and Lift MG use frozen final split seeds 11/22/33; Can MG uses the original stress diagnostic and is not a final endpoint row.",
        "",
        *table(rows, columns),
        "",
        "## Interpretation",
        "",
        "- Can 40p/80b has overlap between hidden-positive and hidden-bad unlabeled demos, motivating a precision/coverage support converter.",
        "- Lift MG scores separate positives from most bad demos, but the endpoint result shows high-purity hard support can still under-cover policy learning.",
        "- Can MG has many positives and bad demos in the high-score plateau, explaining why router-v2 abstains and why simple likelihood proxies fail.",
        "",
        "## Figure",
        "",
        "- PNG: `results/final_paper/figures/score_shape_diagnostics.png`",
        "- PDF: `results/final_paper/figures/score_shape_diagnostics.pdf`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(
    summaries: list[dict[str, str]],
    score_maps: list[dict[str, list[float]]],
    thresholds: list[float],
    out_dir: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.2), sharey=False)
    bins = [i / 25 for i in range(26)]
    status_display = {
        "primary_frozen_3split": "frozen 3-split",
        "stress_diagnostic_original": "stress diagnostic",
    }

    for ax, summary, scores_by_label, threshold in zip(axes, summaries, score_maps, thresholds):
        pos = scores_by_label["positive"]
        bad = scores_by_label["bad"]
        ax.hist(
            bad,
            bins=bins,
            density=True,
            alpha=0.55,
            color="#64748b",
            label="hidden bad",
        )
        ax.hist(
            pos,
            bins=bins,
            density=True,
            alpha=0.55,
            color="#16a34a",
            label="hidden positive",
        )
        if not math.isnan(threshold):
            ax.axvline(
                threshold,
                color="#dc2626",
                linestyle="--",
                linewidth=1.6,
                label=summary["threshold_name"],
            )
        if summary["analysis"] == "Can MG":
            ax.axvspan(0.95, 1.0, color="#f59e0b", alpha=0.12, label=">=0.95 plateau")

        ax.set_title(
            f"{summary['analysis']}\n{status_display.get(summary['status'], summary['status'])}",
            fontsize=10,
        )
        ax.set_xlabel("Trajectory score")
        ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        text = (
            f"pos >= .95: {summary['positive_frac_ge_0p95']}\n"
            f"bad >= .95: {summary['bad_frac_ge_0p95']}"
        )
        ax.text(
            0.04,
            0.95,
            text,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=8,
            bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "none", "pad": 3},
        )

    axes[0].set_ylabel("Density")
    handles_by_label = {}
    for ax in axes:
        handles, labels = ax.get_legend_handles_labels()
        for handle, label in zip(handles, labels):
            handles_by_label.setdefault(label, handle)
    fig.legend(
        handles_by_label.values(),
        handles_by_label.keys(),
        loc="lower center",
        ncol=4,
        frameon=False,
        fontsize=8,
        bbox_to_anchor=(0.5, 0.055),
    )
    fig.suptitle("Score Shapes Explain Support Conversion and Abstention", fontsize=13)
    fig.text(
        0.06,
        0.01,
        "Histograms use hidden labels only for audit/visualization; method thresholds use labeled-score or score-shape rules.",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.16, 1, 0.92))

    for suffix in ["png", "pdf"]:
        fig.savefig(out_dir / f"score_shape_diagnostics.{suffix}", dpi=220)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, str]] = []
    score_maps: list[dict[str, list[float]]] = []
    thresholds: list[float] = []
    for config in ANALYSES:
        summary, scores_by_label, threshold = summarize_analysis(config)
        summaries.append(summary)
        score_maps.append(scores_by_label)
        thresholds.append(threshold)

    csv_path = args.out_dir / "score_shape_diagnostics.csv"
    report_path = args.out_dir / "score_shape_diagnostics_REPORT.md"
    write_csv(csv_path, summaries)
    write_report(report_path, summaries)
    plot(summaries, score_maps, thresholds, args.fig_dir)
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")
    print(f"wrote {args.fig_dir / 'score_shape_diagnostics.png'}")
    print(f"wrote {args.fig_dir / 'score_shape_diagnostics.pdf'}")


if __name__ == "__main__":
    main()
