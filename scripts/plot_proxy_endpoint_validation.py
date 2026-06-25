from __future__ import annotations

import argparse
import csv
import math
import os
from collections import defaultdict
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-tri-piql")

import matplotlib.pyplot as plt


DEFAULT_AUDIT = Path("results/final_paper/tables/candidate_family_audit.csv")
DEFAULT_TABLE_DIR = Path("results/final_paper/tables")
DEFAULT_FIG_DIR = Path("results/final_paper/figures")

FAMILY_MARKERS = {
    "bad_aware_hard": "o",
    "positive_only": "^",
    "soft_weighted": "s",
    "union_hybrid": "D",
}

SETTING_COLORS = {
    "can40": "#2563eb",
    "lift_mg": "#16a34a",
    "can20": "#f59e0b",
    "can80": "#dc2626",
}

SETTING_ORDER = {
    "can40": 0,
    "lift_mg": 1,
    "can20": 2,
    "can80": 3,
}

SHORT_LABELS = {
    "TRIAGE-BC adaptive masscap": "TRIAGE",
    "TRIAGE-BC": "TRIAGE",
    "positive-only NN top40": "posNN",
    "positive-only NN top20": "posNN",
    "positive-only NN top80": "posNN",
    "positive-only NN": "posNN",
    "weighted BC full pool": "weighted",
    "weighted BC": "weighted",
    "classifier top-k": "cls-k",
    "positive-NN/risk union top40": "union",
}

LABEL_OFFSETS = {
    ("can40", "weighted"): (8, -10),
    ("can40", "union"): (8, 9),
    ("lift_mg", "weighted"): (8, 6),
    ("can20", "weighted"): (8, -8),
    ("can40", "posNN"): (8, 8),
    ("lift_mg", "posNN"): (8, -2),
    ("can20", "posNN"): (8, 9),
    ("can80", "posNN"): (8, 8),
    ("can40", "TRIAGE"): (8, 3),
    ("lift_mg", "TRIAGE"): (8, 7),
    ("can20", "TRIAGE"): (8, -6),
    ("can80", "TRIAGE"): (8, 5),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--table-dir", type=Path, default=DEFAULT_TABLE_DIR)
    parser.add_argument("--fig-dir", type=Path, default=DEFAULT_FIG_DIR)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def maybe_float(value: str) -> float | None:
    if value == "":
        return None
    return float(value)


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def rankdata(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    x_var = sum((x - x_mean) ** 2 for x in xs)
    y_var = sum((y - y_mean) ** 2 for y in ys)
    if x_var == 0.0 or y_var == 0.0:
        return None
    cov = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    return cov / math.sqrt(x_var * y_var)


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    return pearson(rankdata(xs), rankdata(ys))


def filtered_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        if row["candidate_family"] in {"diagnostic_oracle", "mixed_baseline"}:
            continue
        if not row["endpoint_success_rate"] or not row["coverage_proxy_score"]:
            continue
        out.append(row)
    return sorted(
        out,
        key=lambda row: (
            SETTING_ORDER.get(row["setting_id"], 99),
            row["candidate_family"],
            row["candidate_label"],
        ),
    )


def analysis_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        endpoint = maybe_float(row["endpoint_success_rate"])
        coverage = maybe_float(row["coverage_proxy_score"])
        audit = maybe_float(row["audit_oracle_score"])
        if endpoint is None or coverage is None:
            continue
        out.append(
            {
                "setting_id": row["setting_id"],
                "setting_label": row["setting_label"],
                "row_role": row["row_role"],
                "candidate_id": row["candidate_id"],
                "candidate_label": row["candidate_label"],
                "candidate_family": row["candidate_family"],
                "endpoint_status": row["endpoint_status"],
                "coverage_proxy_score": fmt(coverage),
                "audit_oracle_score": fmt(audit),
                "endpoint_success_rate": fmt(endpoint),
                "endpoint_successes": row["endpoint_successes"],
                "endpoint_episodes": row["endpoint_episodes"],
            }
        )
    return out


def correlation_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    groups: list[tuple[str, list[dict[str, str]]]] = [
        ("all endpoint-evaluated support rows", rows),
        (
            "primary complete rows",
            [
                row
                for row in rows
                if row["row_role"] == "primary"
                and row["endpoint_status"] == "complete_3split_endpoint"
            ],
        ),
    ]
    by_setting: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_setting[row["setting_id"]].append(row)
    for setting_id, setting_rows in sorted(
        by_setting.items(), key=lambda item: SETTING_ORDER.get(item[0], 99)
    ):
        groups.append((f"{setting_rows[0]['setting_label']} rows", setting_rows))

    out = []
    for name, group_rows in groups:
        endpoints = [float(row["endpoint_success_rate"]) for row in group_rows]
        coverage = [float(row["coverage_proxy_score"]) for row in group_rows]
        audit_pairs = [
            (float(row["audit_oracle_score"]), float(row["endpoint_success_rate"]))
            for row in group_rows
            if row["audit_oracle_score"] != ""
        ]
        audit_x = [item[0] for item in audit_pairs]
        audit_y = [item[1] for item in audit_pairs]
        out.append(
            {
                "analysis_set": name,
                "num_rows": str(len(group_rows)),
                "coverage_proxy_pearson": fmt(pearson(coverage, endpoints)),
                "coverage_proxy_spearman": fmt(spearman(coverage, endpoints)),
                "audit_score_pearson": fmt(pearson(audit_x, audit_y)),
                "audit_score_spearman": fmt(spearman(audit_x, audit_y)),
            }
        )
    return out


def winner_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_setting: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_setting[row["setting_id"]].append(row)
    out = []
    for _, setting_rows in sorted(
        by_setting.items(), key=lambda item: SETTING_ORDER.get(item[0], 99)
    ):
        endpoint_winner = max(setting_rows, key=lambda row: float(row["endpoint_success_rate"]))
        coverage_winner = max(setting_rows, key=lambda row: float(row["coverage_proxy_score"]))
        audit_candidates = [row for row in setting_rows if row["audit_oracle_score"]]
        audit_winner = (
            max(audit_candidates, key=lambda row: float(row["audit_oracle_score"]))
            if audit_candidates
            else None
        )
        out.append(
            {
                "setting_id": setting_rows[0]["setting_id"],
                "setting_label": setting_rows[0]["setting_label"],
                "endpoint_winner": endpoint_winner["candidate_label"],
                "endpoint_winner_success": (
                    f"{endpoint_winner['endpoint_successes']}/"
                    f"{endpoint_winner['endpoint_episodes']}"
                ),
                "coverage_proxy_winner": coverage_winner["candidate_label"],
                "coverage_proxy_winner_success": (
                    f"{coverage_winner['endpoint_successes']}/"
                    f"{coverage_winner['endpoint_episodes']}"
                ),
                "coverage_proxy_matches_endpoint": str(
                    coverage_winner["candidate_id"] == endpoint_winner["candidate_id"]
                ).lower(),
                "audit_score_winner": audit_winner["candidate_label"] if audit_winner else "",
                "audit_score_winner_success": (
                    f"{audit_winner['endpoint_successes']}/{audit_winner['endpoint_episodes']}"
                    if audit_winner
                    else ""
                ),
                "audit_score_matches_endpoint": (
                    str(audit_winner["candidate_id"] == endpoint_winner["candidate_id"]).lower()
                    if audit_winner
                    else ""
                ),
            }
        )
    return out


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return lines


def plot(rows: list[dict[str, str]], fig_dir: Path) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.7), sharey=True)

    panels = [
        (axes[0], "coverage_proxy_score", "Coverage-only proxy", "hidden-label-free"),
        (axes[1], "audit_oracle_score", "Audit precision-risk score", "hidden labels, audit only"),
    ]

    for ax, x_key, title, subtitle in panels:
        for row in rows:
            if row[x_key] == "":
                continue
            x = float(row[x_key])
            y = float(row["endpoint_success_rate"])
            marker = FAMILY_MARKERS.get(row["candidate_family"], "o")
            color = SETTING_COLORS.get(row["setting_id"], "#6b7280")
            ax.scatter(
                [x],
                [y],
                s=88,
                marker=marker,
                color=color,
                edgecolors="#111827",
                linewidths=0.55,
                alpha=0.88,
                zorder=3,
            )
            label = SHORT_LABELS.get(row["candidate_label"], row["candidate_label"])
            offset = LABEL_OFFSETS.get((row["setting_id"], label), (5, 5))
            ax.annotate(
                label,
                (x, y),
                xytext=offset,
                textcoords="offset points",
                fontsize=7.5,
                color="#111827",
            )
        ax.set_title(title, fontsize=11)
        ax.text(
            0.02,
            0.96,
            subtitle,
            transform=ax.transAxes,
            fontsize=8,
            color="#4b5563",
            va="top",
        )
        ax.set_xlabel("Proxy score")
        ax.set_xlim(-0.04, 1.04)
        ax.set_ylim(0.30, 1.02)
        ax.grid(True, color="#e5e7eb", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[0].set_ylabel("Endpoint success rate")

    setting_handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="white",
            markerfacecolor=color,
            markeredgecolor="#111827",
            markersize=7,
            label=label,
        )
        for label, color in [
            ("Can 40p/80b", SETTING_COLORS["can40"]),
            ("Lift MG", SETTING_COLORS["lift_mg"]),
            ("Can 20p/80b", SETTING_COLORS["can20"]),
            ("Can 80p/80b", SETTING_COLORS["can80"]),
        ]
    ]
    family_handles = [
        plt.Line2D(
            [0],
            [0],
            marker=marker,
            color="#111827",
            markerfacecolor="white",
            markeredgecolor="#111827",
            linestyle="None",
            markersize=7,
            label=label,
        )
        for label, marker in [
            ("bad-aware hard", FAMILY_MARKERS["bad_aware_hard"]),
            ("union hybrid", FAMILY_MARKERS["union_hybrid"]),
            ("positive-only", FAMILY_MARKERS["positive_only"]),
            ("soft weighted", FAMILY_MARKERS["soft_weighted"]),
        ]
    ]
    fig.legend(
        handles=setting_handles + family_handles,
        loc="lower center",
        ncol=7,
        frameon=False,
        fontsize=8,
        bbox_to_anchor=(0.5, -0.02),
    )
    fig.suptitle("Proxy Score vs Endpoint Success", fontsize=13, y=0.995)
    fig.tight_layout(rect=(0, 0.08, 1, 0.96))
    for suffix in ["png", "pdf"]:
        fig.savefig(fig_dir / f"proxy_endpoint_validation.{suffix}", dpi=220)
    plt.close(fig)


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    correlations: list[dict[str, str]],
    winners: list[dict[str, str]],
) -> None:
    coverage_matches = sum(row["coverage_proxy_matches_endpoint"] == "true" for row in winners)
    primary_winners = [row for row in winners if row["setting_id"] in {"can40", "lift_mg"}]
    primary_matches = sum(row["coverage_proxy_matches_endpoint"] == "true" for row in primary_winners)
    lines = [
        "# Proxy Endpoint Validation",
        "",
        "This is Experiment D2 from the high-impact completion plan.",
        "It checks whether the current hidden-label-free coverage proxy predicts endpoint success well enough to justify a v0.2 branch selector.",
        "",
        "## Correlation Summary",
        "",
        *markdown_table(
            correlations,
            [
                "analysis_set",
                "num_rows",
                "coverage_proxy_pearson",
                "coverage_proxy_spearman",
                "audit_score_pearson",
                "audit_score_spearman",
            ],
        ),
        "",
        "## Winner Check",
        "",
        *markdown_table(
            winners,
            [
                "setting_label",
                "endpoint_winner",
                "endpoint_winner_success",
                "coverage_proxy_winner",
                "coverage_proxy_winner_success",
                "coverage_proxy_matches_endpoint",
                "audit_score_winner",
                "audit_score_winner_success",
                "audit_score_matches_endpoint",
            ],
        ),
        "",
        "## Interpretation",
        "",
        f"- Coverage-only proxy matches the endpoint winner in `{coverage_matches}/{len(winners)}` evaluated settings and `{primary_matches}/{len(primary_winners)}` primary settings.",
        "- It correctly favors broad weighted support on Lift MG, but it incorrectly favors broad weighted support on the Can 40p/80b and Can 20p/80b contamination settings.",
        "- The audit-only precision-risk score is not deployable and also fails on Lift MG, where high-purity hard support under-covers the policy learner relative to weighted BC.",
        "- This is negative evidence for freezing a v0.2 method around the current coverage-only proxy. A publishable v0.2 needs additional hidden-label-free bad-risk and action-conflict features before spending fresh endpoint GPU budget.",
        "",
        "## Outputs",
        "",
        "- `results/final_paper/tables/proxy_endpoint_validation.csv`",
        "- `results/final_paper/tables/proxy_endpoint_validation_correlations.csv`",
        "- `results/final_paper/tables/proxy_endpoint_validation_winners.csv`",
        "- `results/final_paper/figures/proxy_endpoint_validation.png`",
        "- `results/final_paper/figures/proxy_endpoint_validation.pdf`",
        "",
        "Rows included:",
        "",
        *markdown_table(
            rows,
            [
                "setting_label",
                "candidate_label",
                "candidate_family",
                "endpoint_status",
                "coverage_proxy_score",
                "audit_oracle_score",
                "endpoint_success_rate",
            ],
        ),
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = filtered_rows(read_rows(args.audit))
    analysis = analysis_rows(rows)
    correlations = correlation_rows(analysis)
    winners = winner_rows(analysis)

    table_dir = args.table_dir
    table_dir.mkdir(parents=True, exist_ok=True)
    write_csv(table_dir / "proxy_endpoint_validation.csv", analysis)
    write_csv(table_dir / "proxy_endpoint_validation_correlations.csv", correlations)
    write_csv(table_dir / "proxy_endpoint_validation_winners.csv", winners)
    write_report(table_dir / "proxy_endpoint_validation_REPORT.md", analysis, correlations, winners)
    plot(analysis, args.fig_dir)

    print(f"wrote {table_dir / 'proxy_endpoint_validation.csv'}")
    print(f"wrote {table_dir / 'proxy_endpoint_validation_correlations.csv'}")
    print(f"wrote {table_dir / 'proxy_endpoint_validation_winners.csv'}")
    print(f"wrote {table_dir / 'proxy_endpoint_validation_REPORT.md'}")
    print(f"wrote {args.fig_dir / 'proxy_endpoint_validation.png'}")
    print(f"wrote {args.fig_dir / 'proxy_endpoint_validation.pdf'}")


if __name__ == "__main__":
    main()
