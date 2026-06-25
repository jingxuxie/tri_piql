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

METHOD_ORDER = [
    "all-demo BC",
    "weighted BC",
    "positive-only NN",
    "TRIAGE-BC",
    "all-positive oracle",
]

METHOD_COLORS = {
    "all-demo BC": "#8b5cf6",
    "weighted BC": "#2563eb",
    "positive-only NN": "#16a34a",
    "TRIAGE-BC": "#dc2626",
    "all-positive oracle": "#f59e0b",
}

TASK_ORDER = [
    "Can 80p/80b",
    "Can 40p/80b",
    "Can 20p/80b",
    "Lift MG",
]

TASK_LABELS = {
    "Can 80p/80b": "Can 80p/80b\nsplit33 diag",
    "Can 40p/80b": "Can 40p/80b\n3-split primary",
    "Can 20p/80b": "Can 20p/80b\nsplit11 diag",
    "Lift MG": "Lift MG\n3-split primary",
}

PRIMARY_TASK_ORDER = [
    "Can 40p/80b",
    "Lift MG",
]

PRIMARY_TASK_LABELS = {
    "Can 40p/80b": "Can 40p/80b\n3-split primary",
    "Lift MG": "Lift MG\n3-split primary",
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


def safe_float(value: str) -> float:
    if value == "":
        return float("nan")
    return float(value)


def support_from_audits(paths: list[Path]) -> tuple[int, int, int, float]:
    total = 0
    positive = 0
    bad = 0
    for path in paths:
        for row in read_rows(path):
            total += 1
            label = row.get("hidden_label", "")
            if label == "positive":
                positive += 1
            elif label == "bad":
                bad += 1
    purity = positive / total if total else float("nan")
    return total, positive, bad, purity


def row(
    *,
    task: str,
    evidence_status: str,
    split_scope: str,
    method: str,
    success: float,
    successes: int,
    episodes: int,
    train_or_support_count: int | None,
    support_positive: int | None,
    support_bad: int | None,
    support_purity: float | None,
    source: str,
    note: str,
) -> dict[str, str]:
    return {
        "task": task,
        "evidence_status": evidence_status,
        "split_scope": split_scope,
        "method": method,
        "success_rate": fmt(success),
        "successes": str(successes),
        "episodes": str(episodes),
        "train_or_support_count": fmt(train_or_support_count),
        "support_positive": fmt(support_positive),
        "support_bad": fmt(support_bad),
        "support_purity": fmt(support_purity),
        "source": source,
        "note": note,
    }


def can40_rows() -> list[dict[str, str]]:
    path = Path("results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv")
    aggregate = next(row for row in read_rows(path) if row["split_seed"] == "aggregate")
    source = "results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md"
    return [
        row(
            task="Can 40p/80b",
            evidence_status="primary_frozen_3split",
            split_scope="split seeds 11/22/33, pooled",
            method="all-demo BC",
            success=safe_float(aggregate["all_demo_success_rate"]),
            successes=int(aggregate["all_demo_successes"]),
            episodes=int(aggregate["eval_episodes"]),
            train_or_support_count=None,
            support_positive=None,
            support_bad=None,
            support_purity=None,
            source=source,
            note="pooled all-demo cloning control",
        ),
        row(
            task="Can 40p/80b",
            evidence_status="primary_frozen_3split",
            split_scope="split seeds 11/22/33, pooled",
            method="weighted BC",
            success=safe_float(aggregate["weighted_success_rate"]),
            successes=int(aggregate["weighted_successes"]),
            episodes=int(aggregate["eval_episodes"]),
            train_or_support_count=int(aggregate["weighted_selected_unlabeled"]),
            support_positive=int(aggregate["weighted_hidden_positive"]),
            support_bad=int(aggregate["weighted_hidden_bad"]),
            support_purity=safe_float(aggregate["weighted_purity"]),
            source=source,
            note="full unlabeled pool with classifier-probability sampling",
        ),
        row(
            task="Can 40p/80b",
            evidence_status="primary_frozen_3split",
            split_scope="split seeds 11/22/33, pooled",
            method="positive-only NN",
            success=safe_float(aggregate["positive_only_nn_success_rate"]),
            successes=int(aggregate["positive_only_nn_successes"]),
            episodes=int(aggregate["eval_episodes"]),
            train_or_support_count=int(aggregate["positive_only_nn_selected_unlabeled"]),
            support_positive=int(aggregate["positive_only_nn_hidden_positive"]),
            support_bad=int(aggregate["positive_only_nn_hidden_bad"]),
            support_purity=safe_float(aggregate["positive_only_nn_purity"]),
            source=source,
            note="strong no-bad-label baseline",
        ),
        row(
            task="Can 40p/80b",
            evidence_status="primary_frozen_3split",
            split_scope="split seeds 11/22/33, pooled",
            method="TRIAGE-BC",
            success=safe_float(aggregate["triage_success_rate"]),
            successes=int(aggregate["triage_successes"]),
            episodes=int(aggregate["eval_episodes"]),
            train_or_support_count=int(aggregate["triage_selected_unlabeled"]),
            support_positive=int(aggregate["triage_hidden_positive"]),
            support_bad=int(aggregate["triage_hidden_bad"]),
            support_purity=safe_float(aggregate["triage_purity"]),
            source=source,
            note="router-v2 adaptive masscap",
        ),
        row(
            task="Can 40p/80b",
            evidence_status="primary_frozen_3split_diagnostic_oracle",
            split_scope="split seeds 11/22/33, pooled",
            method="all-positive oracle",
            success=safe_float(aggregate["all_positive_oracle_success_rate"]),
            successes=int(aggregate["all_positive_oracle_successes"]),
            episodes=int(aggregate["eval_episodes"]),
            train_or_support_count=int(aggregate["all_positive_oracle_train_demos"]),
            support_positive=None,
            support_bad=None,
            support_purity=1.0,
            source=source,
            note="diagnostic upper bound; uses hidden labels",
        ),
    ]


def can20_rows() -> list[dict[str, str]]:
    path = Path("results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic.csv")
    source = "results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic_REPORT.md"
    method_map = {
        "weighted_bc_sampler": "weighted BC",
        "positive_only_nn_top20": "positive-only NN",
        "triage_bc_adaptive_masscap": "TRIAGE-BC",
    }
    rows = []
    for source_row in read_rows(path):
        method = method_map.get(source_row["method"])
        if method is None:
            continue
        rows.append(
            row(
                task="Can 20p/80b",
                evidence_status="diagnostic_single_split",
                split_scope="split seed 11 only",
                method=method,
                success=safe_float(source_row["success"]),
                successes=int(source_row["successes"]),
                episodes=int(source_row["eval_episodes"]),
                train_or_support_count=int(source_row["selected_unlabeled"]),
                support_positive=int(source_row["hidden_positive"]),
                support_bad=int(source_row["hidden_bad"]),
                support_purity=safe_float(source_row["purity"]),
                source=source,
                note="heavier-contamination diagnostic; not a 3-split final table",
            )
        )
    return rows


def can80_rows() -> list[dict[str, str]]:
    path = Path("results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint.csv")
    source = "results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md"
    method_map = {
        "positive_only_nn_top80": "positive-only NN",
        "triage_bc_adaptive_masscap": "TRIAGE-BC",
    }
    rows = []
    for source_row in read_rows(path):
        if source_row["status"] != "endpoint":
            continue
        method = method_map.get(source_row["method"])
        if method is None:
            continue
        rows.append(
            row(
                task="Can 80p/80b",
                evidence_status="diagnostic_single_split",
                split_scope="split seed 33 endpoint; split seeds 11/22 support-only",
                method=method,
                success=safe_float(source_row["endpoint_success"]),
                successes=int(source_row["endpoint_successes"]),
                episodes=int(source_row["eval_episodes"]),
                train_or_support_count=int(source_row["selected_unlabeled"]),
                support_positive=int(source_row["hidden_positive"]),
                support_bad=int(source_row["hidden_bad"]),
                support_purity=safe_float(source_row["purity"]),
                source=source,
                note="balanced Can diagnostic; not a complete 3-split endpoint table",
            )
        )
    return rows


def lift_rows() -> list[dict[str, str]]:
    path = Path("results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary.csv")
    source = "results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md"
    method_map = {
        "all-demo BC": ("all-demo BC", "bc_all_mixed", "pooled all-demo cloning control"),
        "weighted BC": ("weighted BC", "weighted_bc", "full MG pool with classifier-probability sampling"),
        "positive-only NN top160": ("positive-only NN", "positive_only_nn", "strong no-bad-label baseline"),
        "TRIAGE-BC / pos-min": ("TRIAGE-BC", "triage_bc", "router-v2 pos-min branch"),
        "all-positive oracle": ("all-positive oracle", "all_train_positive_oracle", "diagnostic upper bound; uses hidden labels"),
    }
    rows = []
    for source_row in read_rows(path):
        label, dir_method, note = method_map[source_row["method"]]
        audit_paths = [
            Path(f"results/final_paper/per_seed/lift_mg_mg_sparse_split{seed}_{dir_method}_policy0/support_audit.csv")
            for seed in ["11", "22", "33"]
        ]
        support_count, support_positive, support_bad, support_purity = support_from_audits(audit_paths)
        if support_count == 0:
            support_count = None
            support_positive = None
            support_bad = None
            support_purity = None
        rows.append(
            row(
                task="Lift MG",
                evidence_status=(
                    "primary_frozen_3split_diagnostic_oracle"
                    if label == "all-positive oracle"
                    else "primary_frozen_3split"
                ),
                split_scope="split seeds 11/22/33, pooled",
                method=label,
                success=safe_float(source_row["pooled_success_rate"]),
                successes=int(source_row["pooled_successes"]),
                episodes=int(source_row["pooled_episodes"]),
                train_or_support_count=support_count,
                support_positive=support_positive,
                support_bad=support_bad,
                support_purity=support_purity,
                source=source,
                note=note,
            )
        )
    return rows


def table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[col] for col in columns) + " |")
    return lines


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    *,
    title: str,
    description: list[str],
    interpretation: list[str],
    figure_stem: str,
) -> None:
    columns = [
        "task",
        "evidence_status",
        "method",
        "success_rate",
        "successes",
        "episodes",
        "train_or_support_count",
        "support_purity",
    ]
    lines = [
        f"# {title}",
        "",
        *description,
        "",
        *table(rows, columns),
        "",
        "## Interpretation",
        "",
        *interpretation,
        "",
        "## Figure",
        "",
        f"- PNG: `results/final_paper/figures/{figure_stem}.png`",
        f"- PDF: `results/final_paper/figures/{figure_stem}.pdf`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(
    rows: list[dict[str, str]],
    out_dir: Path,
    *,
    task_order: list[str],
    task_labels: dict[str, str],
    out_stem: str,
    title: str,
    note: str,
    shade_diagnostics: bool,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_width = 8.2 if len(task_order) > 2 else 6.2
    fig, ax = plt.subplots(figsize=(fig_width, 4.4))

    width = 0.14
    x_positions = list(range(len(task_order)))
    offsets = {
        method: (index - (len(METHOD_ORDER) - 1) / 2) * width
        for index, method in enumerate(METHOD_ORDER)
    }

    row_by_task_method = {
        (row["task"], row["method"]): row
        for row in rows
    }
    for method in METHOD_ORDER:
        xs = []
        heights = []
        for task_index, task in enumerate(task_order):
            current = row_by_task_method.get((task, method))
            if current is None:
                continue
            xs.append(x_positions[task_index] + offsets[method])
            heights.append(float(current["success_rate"]))
        if xs:
            ax.bar(
                xs,
                heights,
                width=width,
                color=METHOD_COLORS[method],
                edgecolor="#111827",
                linewidth=0.5,
                label=method,
            )

    ax.set_title(title, fontsize=12)
    ax.set_ylabel("Endpoint success")
    ax.set_xticks(x_positions)
    ax.set_xticklabels([task_labels[task] for task in task_order], fontsize=8.5)
    ax.set_ylim(0.0, 1.05)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=8)

    for task_index, task in enumerate(task_order):
        if shade_diagnostics and "diag" in task_labels[task]:
            ax.axvspan(task_index - 0.47, task_index + 0.47, color="#f3f4f6", zorder=-1)

    note_bottom = 0.11 if "\n" in note else 0.06
    fig.text(0.09, 0.01, note, ha="left", va="bottom", fontsize=8, color="#4b5563")
    fig.tight_layout(rect=(0, note_bottom, 0.84, 1))

    for suffix in ["png", "pdf"]:
        fig.savefig(out_dir / f"{out_stem}.{suffix}", dpi=220)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = can80_rows() + can40_rows() + can20_rows() + lift_rows()
    rows = sorted(
        rows,
        key=lambda row: (
            TASK_ORDER.index(row["task"]),
            METHOD_ORDER.index(row["method"]),
        ),
    )
    csv_path = args.out_dir / "robotics_current_endpoint_matrix.csv"
    report_path = args.out_dir / "robotics_current_endpoint_matrix_REPORT.md"
    write_csv(csv_path, rows)
    write_report(
        report_path,
        rows,
        title="Current Robomimic Endpoint Matrix",
        description=[
            "This table consolidates the current endpoint evidence staged under `results/final_paper/`.",
            "It intentionally separates primary frozen three-split rows from diagnostic single-split rows.",
        ],
        interpretation=[
            "- Can 40p/80b and Lift MG are the current primary frozen three-split endpoint tables.",
            "- Can 20p/80b and Can 80p/80b are useful diagnostics but are not complete three-split endpoint tables.",
            "- Positive-only NN is the strongest non-oracle Can row in all staged Can endpoint checks so far.",
            "- Lift MG is the strongest counterexample to a hard-support-only story: weighted BC is the best non-oracle row on the frozen endpoint aggregate.",
        ],
        figure_stem="robotics_current_endpoint_matrix",
    )
    plot(
        rows,
        args.fig_dir,
        task_order=TASK_ORDER,
        task_labels=TASK_LABELS,
        out_stem="robotics_current_endpoint_matrix",
        title="Current Robomimic Endpoint Matrix",
        note="Gray task bands are diagnostic single-split endpoints; Can 40p/80b and Lift MG are frozen three-split aggregates.",
        shade_diagnostics=True,
    )

    primary_rows = [
        row
        for row in rows
        if row["task"] in PRIMARY_TASK_ORDER
        and row["evidence_status"].startswith("primary_frozen_3split")
    ]
    primary_rows = sorted(
        primary_rows,
        key=lambda row: (
            PRIMARY_TASK_ORDER.index(row["task"]),
            METHOD_ORDER.index(row["method"]),
        ),
    )
    primary_csv_path = args.out_dir / "robotics_primary_endpoint_matrix.csv"
    primary_report_path = args.out_dir / "robotics_primary_endpoint_matrix_REPORT.md"
    write_csv(primary_csv_path, primary_rows)
    write_report(
        primary_report_path,
        primary_rows,
        title="Primary Robomimic Endpoint Matrix",
        description=[
            "This table contains only the current primary frozen three-split endpoint evidence.",
            "Diagnostic Can 20p/80b and Can 80p/80b rows remain in `robotics_current_endpoint_matrix.csv` and the corresponding report.",
        ],
        interpretation=[
            "- Can 40p/80b supports the claim that TRIAGE-BC can beat weighted BC and all-demo cloning under action-conflicting contamination.",
            "- Can 40p/80b does not support a bad-label necessity claim because positive-only NN is the strongest non-oracle row.",
            "- Lift MG supports the coverage caveat: weighted BC is the best non-oracle row despite lower support purity.",
            "- The all-positive oracle rows are diagnostic upper bounds that use hidden labels and are not deployable methods.",
        ],
        figure_stem="robotics_primary_endpoint_matrix",
    )
    plot(
        primary_rows,
        args.fig_dir,
        task_order=PRIMARY_TASK_ORDER,
        task_labels=PRIMARY_TASK_LABELS,
        out_stem="robotics_primary_endpoint_matrix",
        title="Primary Robomimic Endpoint Matrix",
        note="Primary figure: frozen three-split rows only;\nCan 20/80 and Can 80/80 diagnostics are appendix-only.",
        shade_diagnostics=False,
    )
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")
    print(f"wrote {args.fig_dir / 'robotics_current_endpoint_matrix.png'}")
    print(f"wrote {args.fig_dir / 'robotics_current_endpoint_matrix.pdf'}")
    print(f"wrote {primary_csv_path}")
    print(f"wrote {primary_report_path}")
    print(f"wrote {args.fig_dir / 'robotics_primary_endpoint_matrix.png'}")
    print(f"wrote {args.fig_dir / 'robotics_primary_endpoint_matrix.pdf'}")


if __name__ == "__main__":
    main()
