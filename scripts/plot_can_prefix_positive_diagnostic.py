from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-tri-piql")

import matplotlib.pyplot as plt


DEFAULT_ROOT = Path("results/final_paper/ablations/can_prefix_positive_endpoint_200ep")
DEFAULT_TABLE_DIR = Path("results/final_paper/tables")
DEFAULT_FIG_DIR = Path("results/final_paper/figures")

DISPLAY_NAMES = {
    "prefix_bad_aware_state_top80": "bad-aware\nstate top80",
    "prefix_state_action_nn_top80": "positive-NN\nstate-action top80",
}

BAR_COLORS = {
    "prefix_bad_aware_state_top80": "#2563eb",
    "prefix_state_action_nn_top80": "#dc2626",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
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


def fmt_rate(value: str | float) -> str:
    return f"{float(value):.3f}"


def as_int(row: dict[str, str], key: str) -> int:
    return int(float(row[key]))


def sorted_summary_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    order = {
        "prefix_bad_aware_state_top80": 0,
        "prefix_state_action_nn_top80": 1,
    }
    return sorted(rows, key=lambda row: order.get(row["candidate_id"], 99))


def normalized_summary_rows(root: Path) -> list[dict[str, str]]:
    rows = sorted_summary_rows(read_rows(root / "endpoint_200ep_aggregate_summary.csv"))
    out: list[dict[str, str]] = []
    for row in rows:
        successes = as_int(row, "success_count")
        episodes = as_int(row, "eval_episodes")
        out.append(
            {
                "candidate_id": row["candidate_id"],
                "candidate_label": DISPLAY_NAMES.get(row["candidate_id"], row["candidate_id"]).replace("\n", " "),
                "success": f"{successes}/{episodes}",
                "success_rate": fmt_rate(row["success_rate"]),
                "support_purity": fmt_rate(row["mean_support_purity"]),
                "hidden_positive_selected": str(as_int(row, "selected_hidden_positive")),
                "hidden_bad_selected": str(as_int(row, "selected_hidden_bad")),
                "avg_len": f"{float(row['avg_len']):.1f}",
            }
        )
    return out


def per_split_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(root.glob("split*/endpoint_200ep_summary.csv")):
        rows.extend(read_rows(path))
    return sorted_summary_rows(rows)


def write_report(
    table_dir: Path,
    summary: list[dict[str, str]],
    split_rows: list[dict[str, str]],
) -> None:
    best = max(summary, key=lambda row: float(row["success_rate"]))
    baseline = next(
        row for row in summary if row["candidate_id"] == "prefix_state_action_nn_top80"
    )
    delta = int(best["success"].split("/")[0]) - int(baseline["success"].split("/")[0])
    lines = [
        "# Can Prefix-Positive Diagnostic Figure",
        "",
        "This is a controlled Robomimic diagnostic, not a primary benchmark row. "
        "Trusted positive labels are early successful-demo prefixes, failures are explicit negatives, "
        "and the unlabeled pool contains full successful and failed demonstrations.",
        "",
        "## Aggregate",
        "",
        "| candidate | support purity | hidden pos | hidden bad | endpoint | avg len |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['candidate_id']} | {row['support_purity']} | "
            f"{row['hidden_positive_selected']} | {row['hidden_bad_selected']} | "
            f"{row['success']} ({row['success_rate']}) | {row['avg_len']} |"
        )
    lines.extend(
        [
            "",
            "## Per-Split Endpoint Counts",
            "",
            "| split | bad-aware top80 | positive-NN top80 |",
            "|---:|---:|---:|",
        ]
    )
    by_split: dict[str, dict[str, dict[str, str]]] = {}
    for row in split_rows:
        by_split.setdefault(row["split_seed"], {})[row["candidate_id"]] = row
    for split in sorted(by_split, key=int):
        bad = by_split[split]["prefix_bad_aware_state_top80"]
        pos = by_split[split]["prefix_state_action_nn_top80"]
        lines.append(
            f"| {split} | {bad['success_count']}/{bad['eval_episodes']} | "
            f"{pos['success_count']}/{pos['eval_episodes']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Bad-aware prefix support leads positive-only prefix retrieval by `{delta}` successes over `150` endpoint rollouts.",
            "- This mirrors the controlled PointNav prefix-positive mechanism in Robomimic Can.",
            "- Keep the result as generated diagnostic evidence because the split construction changes the default benchmark setting.",
            "",
            "## Outputs",
            "",
            "- `results/final_paper/tables/can_prefix_positive_diagnostic.csv`",
            "- `results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md`",
            "- `results/final_paper/figures/can_prefix_positive_diagnostic.png`",
            "- `results/final_paper/figures/can_prefix_positive_diagnostic.pdf`",
        ]
    )
    (table_dir / "can_prefix_positive_diagnostic_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def plot(summary: list[dict[str, str]], fig_dir: Path) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)

    x = list(range(len(summary)))
    labels = [DISPLAY_NAMES[row["candidate_id"]] for row in summary]
    colors = [BAR_COLORS[row["candidate_id"]] for row in summary]

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6), gridspec_kw={"width_ratios": [1.0, 1.2]})

    success_rates = [float(row["success_rate"]) for row in summary]
    axes[0].bar(x, success_rates, color=colors, edgecolor="#111827", linewidth=0.8)
    for idx, row in enumerate(summary):
        axes[0].text(
            idx,
            success_rates[idx] + 0.03,
            row["success"],
            ha="center",
            va="bottom",
            fontsize=8.5,
        )
    axes[0].set_xticks(x, labels)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("Endpoint success rate")
    axes[0].set_title("Policy endpoint")
    axes[0].grid(axis="y", color="#e5e7eb", linewidth=0.8)

    hidden_pos = [int(row["hidden_positive_selected"]) for row in summary]
    hidden_bad = [int(row["hidden_bad_selected"]) for row in summary]
    axes[1].bar(
        x,
        hidden_pos,
        color="#16a34a",
        edgecolor="#111827",
        linewidth=0.8,
        label="hidden positive",
    )
    axes[1].bar(
        x,
        hidden_bad,
        bottom=hidden_pos,
        color="#f97316",
        edgecolor="#111827",
        linewidth=0.8,
        label="hidden bad",
    )
    for idx, row in enumerate(summary):
        axes[1].text(
            idx,
            hidden_pos[idx] + hidden_bad[idx] + 6,
            f"purity {float(row['support_purity']):.2f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
        )
    axes[1].set_xticks(x, labels)
    axes[1].set_ylim(0, max(hp + hb for hp, hb in zip(hidden_pos, hidden_bad)) * 1.18)
    axes[1].set_ylabel("Selected hidden demos")
    axes[1].set_title("Support composition")
    axes[1].grid(axis="y", color="#e5e7eb", linewidth=0.8)
    axes[1].legend(frameon=False, fontsize=8, loc="upper left", bbox_to_anchor=(1.02, 1.0))

    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=8.5)

    fig.suptitle("Can Prefix-Positive Diagnostic", fontsize=12)
    fig.text(
        0.5,
        0.01,
        "Generated diagnostic over split seeds 101/202/303; official BC-RNN-GMM, epoch 200, 50 rollouts per split.",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))

    for suffix in ["png", "pdf"]:
        fig.savefig(fig_dir / f"can_prefix_positive_diagnostic.{suffix}", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    summary = normalized_summary_rows(args.root)
    split_rows = per_split_rows(args.root)

    write_csv(args.table_dir / "can_prefix_positive_diagnostic.csv", summary)
    write_report(args.table_dir, summary, split_rows)
    plot(summary, args.fig_dir)

    print(f"wrote {args.table_dir / 'can_prefix_positive_diagnostic.csv'}")
    print(f"wrote {args.table_dir / 'can_prefix_positive_diagnostic_REPORT.md'}")
    print(f"wrote {args.fig_dir / 'can_prefix_positive_diagnostic.png'}")
    print(f"wrote {args.fig_dir / 'can_prefix_positive_diagnostic.pdf'}")


if __name__ == "__main__":
    main()
