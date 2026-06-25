from __future__ import annotations

import os
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-tri-piql")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


FIG_DIR = Path("results/final_paper/figures")


def add_box(
    ax,
    xy: tuple[float, float],
    width: float,
    height: float,
    title: str,
    body: str,
    *,
    facecolor: str,
    edgecolor: str = "#334155",
    title_color: str = "#0f172a",
) -> None:
    x, y = xy
    title_lines = title.count("\n") + 1
    body_offset = -0.16 if title_lines > 1 else -0.05
    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.018",
        linewidth=1.4,
        facecolor=facecolor,
        edgecolor=edgecolor,
    )
    ax.add_patch(box)
    ax.text(
        x + width / 2,
        y + height - 0.11,
        title,
        ha="center",
        va="top",
        fontsize=10.8,
        fontweight="bold",
        color=title_color,
    )
    ax.text(
        x + width / 2,
        y + height / 2 + body_offset,
        body,
        ha="center",
        va="center",
        fontsize=9,
        color="#1e293b",
        linespacing=1.25,
    )


def arrow(ax, start: tuple[float, float], end: tuple[float, float], *, color: str = "#475569") -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.6,
            color=color,
            shrinkA=5,
            shrinkB=5,
        )
    )


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12.2, 5.8), dpi=180)
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    colors = {
        "positive": "#dcfce7",
        "negative": "#fee2e2",
        "unlabeled": "#e0f2fe",
        "score": "#ede9fe",
        "router": "#fff7ed",
        "policy": "#f8fafc",
        "eval": "#fef9c3",
    }

    ax.text(
        0.25,
        5.46,
        "TRIAGE-BC: score-calibrated support selection for contaminated offline imitation",
        ha="left",
        va="top",
        fontsize=14,
        fontweight="bold",
        color="#0f172a",
    )
    ax.text(
        0.25,
        5.13,
        "Hidden labels in the mixed log are used only for audits and oracle diagnostics, never for routing.",
        ha="left",
        va="top",
        fontsize=9.5,
        color="#475569",
    )

    add_box(
        ax,
        (0.35, 3.75),
        1.85,
        0.88,
        "Trusted success",
        "D+\nscarce desirable demos",
        facecolor=colors["positive"],
    )
    add_box(
        ax,
        (0.35, 2.52),
        1.85,
        0.88,
        "Known failure",
        "D-\nscarce bad demos",
        facecolor=colors["negative"],
    )
    add_box(
        ax,
        (0.35, 1.29),
        1.85,
        0.88,
        "Mixed log",
        "Du\nlarge unlabeled demos",
        facecolor=colors["unlabeled"],
    )

    add_box(
        ax,
        (3.05, 3.05),
        2.0,
        1.25,
        "Tri-signal score",
        "Train classifier c(s,a)\nusing D+ vs D-\nscore Du without labels",
        facecolor=colors["score"],
    )
    add_box(
        ax,
        (5.85, 3.05),
        2.0,
        1.25,
        "Calibration",
        "Aggregate g(tau)\nestimate positive mass\nfrom D+/D- score means",
        facecolor=colors["score"],
    )
    add_box(
        ax,
        (8.65, 3.05),
        2.25,
        1.25,
        "Hidden-label-free\nrouter",
        "adaptive masscap\npos-min threshold\nsoft weighting or abstain",
        facecolor=colors["router"],
    )
    add_box(
        ax,
        (8.65, 1.22),
        2.25,
        1.12,
        "Policy learner",
        "BC-RNN-GMM on selected\nor weighted support\nfixed 20k endpoint",
        facecolor=colors["policy"],
    )
    add_box(
        ax,
        (5.85, 1.22),
        2.0,
        1.12,
        "Audits only",
        "purity / coverage\noracle support\nheld-out rollouts",
        facecolor=colors["eval"],
    )

    arrow(ax, (2.2, 4.19), (3.05, 3.86), color="#16a34a")
    arrow(ax, (2.2, 2.96), (3.05, 3.47), color="#dc2626")
    arrow(ax, (2.2, 1.73), (3.05, 3.18), color="#0284c7")
    arrow(ax, (5.05, 3.68), (5.85, 3.68))
    arrow(ax, (7.85, 3.68), (8.65, 3.68))
    arrow(ax, (9.78, 3.05), (9.78, 2.34))
    arrow(ax, (8.65, 1.78), (7.85, 1.78), color="#ca8a04")

    ax.text(
        3.98,
        2.66,
        "score model sees labels only in D+ and D-",
        ha="center",
        va="center",
        fontsize=8.5,
        color="#64748b",
    )
    ax.text(
        9.78,
        2.62,
        "selected / weighted\ntraining data",
        ha="center",
        va="center",
        fontsize=8.5,
        color="#64748b",
        linespacing=1.15,
    )

    ax.plot([0.18, 12.02], [0.72, 0.72], color="#cbd5e1", linewidth=1.0)
    ax.text(
        0.25,
        0.47,
        "Paper evidence: PointNav validates the mechanism; Can 40p/80b favors hard support over weighting; Lift MG and Can MG show coverage and abstention limits.",
        ha="left",
        va="center",
        fontsize=9,
        color="#334155",
    )

    out_png = FIG_DIR / "triage_bc_method_diagram.png"
    out_pdf = FIG_DIR / "triage_bc_method_diagram.pdf"
    fig.savefig(out_png, bbox_inches="tight", facecolor="white")
    fig.savefig(out_pdf, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out_png}")
    print(f"wrote {out_pdf}")


if __name__ == "__main__":
    main()
