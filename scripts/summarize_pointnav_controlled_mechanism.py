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

METHOD_NAMES = {
    "bc_all": "BC-all",
    "pos_unlabeled_bc": "pos+unlabeled BC",
    "local_weighted_bc": "local weighted BC",
    "triage_gap_demo_bc": "TRIAGE-BC gap support",
    "triage_gap_posterior_bc": "TRIAGE-BC gap posterior",
    "oracle_good_bc": "hidden-good oracle",
}

METHOD_COLORS = {
    "BC-all": "#8b5cf6",
    "pos+unlabeled BC": "#64748b",
    "local weighted BC": "#2563eb",
    "TRIAGE-BC gap support": "#dc2626",
    "TRIAGE-BC gap posterior": "#f97316",
    "hidden-good oracle": "#16a34a",
}

METHOD_STYLES = {
    "BC-all": {"linestyle": "-", "marker": "o", "linewidth": 2.0, "alpha": 1.0},
    "pos+unlabeled BC": {"linestyle": "-", "marker": "o", "linewidth": 2.0, "alpha": 1.0},
    "local weighted BC": {"linestyle": "-", "marker": "o", "linewidth": 2.0, "alpha": 1.0},
    "TRIAGE-BC gap support": {"linestyle": "-", "marker": "o", "linewidth": 2.6, "alpha": 1.0},
    "hidden-good oracle": {"linestyle": "--", "marker": "x", "linewidth": 1.8, "alpha": 0.75},
}


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


def add_method_rows(
    rows: list[dict[str, str]],
    *,
    source_path: Path,
    source_report: str,
    experiment: str,
    n_pos: int,
    n_neg: int,
    method_keys: list[str],
) -> None:
    for source_row in read_rows(source_path):
        for key in method_keys:
            if key not in source_row:
                continue
            row_n_neg = source_row.get("n_neg", str(n_neg)) if n_neg < 0 else str(n_neg)
            has_selected_support = key.startswith("triage_gap") or key == "oracle_good_bc"
            rows.append(
                {
                    "experiment": experiment,
                    "n_pos": str(n_pos),
                    "n_neg": row_n_neg,
                    "bad_frac": source_row["bad_frac"],
                    "method": METHOD_NAMES[key],
                    "success": fmt(float(source_row[key])),
                    "selected_frac": source_row.get("selected_frac", "") if has_selected_support else "",
                    "selected_demo_purity": source_row.get("selected_demo_purity", "") if has_selected_support else "",
                    "hidden_good_demos": source_row.get("hidden_good_demos", "") if has_selected_support else "",
                    "hidden_bad_demos": source_row.get("hidden_bad_demos", "") if has_selected_support else "",
                    "source": source_report,
                }
            )


def build_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    method_keys = [
        "bc_all",
        "pos_unlabeled_bc",
        "local_weighted_bc",
        "triage_gap_demo_bc",
        "oracle_good_bc",
    ]
    add_method_rows(
        rows,
        source_path=Path("results/final_paper/ablations/continuous_pointnav_label_budget2_gap_selection.csv"),
        source_report="results/final_paper/ablations/continuous_pointnav_label_budget2_gap_selection_REPORT.md",
        experiment="equal_label_budget",
        n_pos=2,
        n_neg=2,
        method_keys=[*method_keys, "triage_gap_posterior_bc"],
    )
    add_method_rows(
        rows,
        source_path=Path("results/final_paper/ablations/continuous_pointnav_label_budget5_gap_selection.csv"),
        source_report="results/final_paper/ablations/continuous_pointnav_label_budget5_gap_selection_REPORT.md",
        experiment="equal_label_budget",
        n_pos=5,
        n_neg=5,
        method_keys=method_keys,
    )
    add_method_rows(
        rows,
        source_path=Path("results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5.csv"),
        source_report="results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md",
        experiment="bad_label_count",
        n_pos=5,
        n_neg=-1,
        method_keys=[
            "bc_all",
            "local_weighted_bc",
            "triage_gap_demo_bc",
            "triage_gap_posterior_bc",
            "oracle_good_bc",
        ],
    )
    return rows


def rows_for(
    rows: list[dict[str, str]],
    *,
    experiment: str,
    n_pos: str | None = None,
    n_neg: str | None = None,
    method: str | None = None,
) -> list[dict[str, str]]:
    selected = [row for row in rows if row["experiment"] == experiment]
    if n_pos is not None:
        selected = [row for row in selected if row["n_pos"] == n_pos]
    if n_neg is not None:
        selected = [row for row in selected if row["n_neg"] == n_neg]
    if method is not None:
        selected = [row for row in selected if row["method"] == method]
    return selected


def table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[col] for col in columns) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    budget2 = rows_for(rows, experiment="equal_label_budget", n_pos="2", n_neg="2")
    budget2 = [
        row
        for row in budget2
        if row["method"]
        in {
            "BC-all",
            "pos+unlabeled BC",
            "local weighted BC",
            "TRIAGE-BC gap support",
            "hidden-good oracle",
        }
    ]
    budget2 = sorted(
        budget2,
        key=lambda row: (
            float(row["bad_frac"]),
            [
                "BC-all",
                "pos+unlabeled BC",
                "local weighted BC",
                "TRIAGE-BC gap support",
                "hidden-good oracle",
            ].index(row["method"]),
        ),
    )
    triage_bad_counts = sorted(
        rows_for(rows, experiment="bad_label_count", method="TRIAGE-BC gap support"),
        key=lambda row: (int(row["n_neg"]), float(row["bad_frac"])),
    )
    lines = [
        "# Controlled PointNav Mechanism Summary",
        "",
        "This report consolidates the current controlled PointNav evidence staged under `results/final_paper/ablations/`.",
        "The strongest paper-facing rows use route-prefix positives, explicit bad shortcut trajectories, and unlabeled logs with hidden safe routes plus hidden trap trajectories.",
        "",
        "## Equal Label Budget Stress: n+=n-=2",
        "",
        *table(
            budget2,
            [
                "bad_frac",
                "method",
                "success",
                "selected_demo_purity",
                "hidden_good_demos",
                "hidden_bad_demos",
            ],
        ),
        "",
        "## Bad-Label Count: n+=5",
        "",
        *table(
            triage_bad_counts,
            [
                "n_neg",
                "bad_frac",
                "method",
                "success",
                "selected_demo_purity",
                "hidden_good_demos",
                "hidden_bad_demos",
            ],
        ),
        "",
        "## Interpretation",
        "",
        "- With only two positive prefixes and two bad shortcut demos, TRIAGE gap support reaches `1.000` success at every tested contamination level, matching the hidden-good oracle.",
        "- BC-all, positive+unlabeled BC, and local weighted BC degrade sharply as the unlabeled bad fraction rises.",
        "- With five positives, even one explicit bad shortcut demo is enough for gap support to select pure hidden-good support and reach `1.000` success at all tested bad fractions.",
        "- This is the cleanest controlled mechanism evidence for the paper: explicit bad labels calibrate support recovery when positives are scarce and incomplete.",
        "",
        "## Figure",
        "",
        "- PNG: `results/final_paper/figures/pointnav_controlled_mechanism.png`",
        "- PDF: `results/final_paper/figures/pointnav_controlled_mechanism.pdf`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(rows: list[dict[str, str]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.4), sharey=True)

    budget2_methods = [
        "hidden-good oracle",
        "BC-all",
        "pos+unlabeled BC",
        "local weighted BC",
        "TRIAGE-BC gap support",
    ]
    for method in budget2_methods:
        style = METHOD_STYLES[method]
        selected = sorted(
            rows_for(
                rows,
                experiment="equal_label_budget",
                n_pos="2",
                n_neg="2",
                method=method,
            ),
            key=lambda row: float(row["bad_frac"]),
        )
        axes[0].plot(
            [float(row["bad_frac"]) for row in selected],
            [float(row["success"]) for row in selected],
            marker=style["marker"],
            linestyle=style["linestyle"],
            linewidth=style["linewidth"],
            alpha=style["alpha"],
            color=METHOD_COLORS[method],
            label=method,
        )

    axes[0].set_title("Equal scarce labels: n+=n-=2", fontsize=11)
    axes[0].set_xlabel("Bad fraction in unlabeled log")
    axes[0].set_ylabel("Closed-loop success")
    axes[0].set_ylim(-0.05, 1.05)
    axes[0].grid(True, color="#e5e7eb", linewidth=0.8)

    bad_count_styles = {
        "1": {"color": "#0f766e", "linestyle": "--", "marker": "s"},
        "2": {"color": "#dc2626", "linestyle": "-", "marker": "o"},
        "5": {"color": "#7c3aed", "linestyle": ":", "marker": "^"},
    }
    for n_neg, style in bad_count_styles.items():
        selected = sorted(
            rows_for(
                rows,
                experiment="bad_label_count",
                n_pos="5",
                n_neg=n_neg,
                method="TRIAGE-BC gap support",
            ),
            key=lambda row: float(row["bad_frac"]),
        )
        axes[1].plot(
            [float(row["bad_frac"]) for row in selected],
            [float(row["success"]) for row in selected],
            marker=style["marker"],
            linestyle=style["linestyle"],
            linewidth=2.0,
            color=style["color"],
            label=f"{n_neg} bad demo{'s' if n_neg != '1' else ''}",
        )

    axes[1].set_title("Bad-label count with n+=5", fontsize=11)
    axes[1].set_xlabel("Bad fraction in unlabeled log")
    axes[1].grid(True, color="#e5e7eb", linewidth=0.8)

    for ax in axes:
        ax.set_xticks([0.50, 0.75, 0.90, 0.95])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[0].legend(loc="lower left", fontsize=7.5, frameon=False)
    axes[1].legend(loc="lower left", fontsize=8, frameon=False)
    fig.suptitle("Controlled PointNav: Scarce Labels Recover Clean Support", fontsize=13)
    fig.text(
        0.08,
        0.01,
        "Positives are safe-route prefixes; bad labels are shortcut trajectories; unlabeled logs mix hidden safe routes and hidden traps.",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))

    for suffix in ["png", "pdf"]:
        fig.savefig(out_dir / f"pointnav_controlled_mechanism.{suffix}", dpi=220)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    csv_path = args.out_dir / "pointnav_controlled_mechanism.csv"
    report_path = args.out_dir / "pointnav_controlled_mechanism_REPORT.md"
    write_csv(csv_path, rows)
    write_report(report_path, rows)
    plot(rows, args.fig_dir)
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")
    print(f"wrote {args.fig_dir / 'pointnav_controlled_mechanism.png'}")
    print(f"wrote {args.fig_dir / 'pointnav_controlled_mechanism.pdf'}")


if __name__ == "__main__":
    main()
