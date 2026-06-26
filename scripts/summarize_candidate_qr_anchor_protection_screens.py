#!/usr/bin/env python3
"""Summarize Candidate Q/R Lift anchor-protection screens."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"
CANDIDATE_Q_DIR = OUT / "candidate_q_lift606_short_anchor_union"
CANDIDATE_R_DIR = OUT / "candidate_r_lift606_checkpoint_interpolation"

BASELINES = [
    ("positive_only_nn", OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv"),
    ("triage_bc", OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv"),
    ("weighted_bc", OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv"),
    ("initial_confidence_q25", OUT / "lift606_router_confidence_labeledpos_q25_eval20" / "episode_metrics.csv"),
    (
        "candidate_p_epoch20_posinit_finetune",
        OUT / "candidate_p_lift606_posinit_anchor_union" / "eval20_epoch20" / "episode_metrics.csv",
    ),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def summarize_episode_csv(group: str, name: str, path: Path, limit: int = 20) -> dict[str, object]:
    rows = read_csv(path)[:limit]
    successes = sum(int(float(row["success"])) for row in rows)
    avg_len = sum(float(row["length"]) for row in rows) / len(rows)
    return {
        "group": group,
        "method": name,
        "successes": successes,
        "episodes": len(rows),
        "avg_len": round(avg_len, 3),
    }


def summarize_metrics_csv(group: str, path: Path) -> list[dict[str, object]]:
    rows = []
    for row in read_csv(path):
        rows.append(
            {
                "group": group,
                "method": row["checkpoint_name"],
                "successes": int(round(float(row["success_rate"]) * int(row["eval_episodes"]))),
                "episodes": int(row["eval_episodes"]),
                "avg_len": round(float(row["avg_len"]), 3),
            }
        )
    return rows


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def main() -> None:
    baseline_rows = [summarize_episode_csv("baseline", name, path) for name, path in BASELINES]
    q_rows = summarize_metrics_csv("candidate_q_short_finetune", CANDIDATE_Q_DIR / "eval20_epochs1to5" / "metrics.csv")
    r_rows = summarize_metrics_csv("candidate_r_interpolation", CANDIDATE_R_DIR / "eval20_p20_alphas" / "metrics.csv")
    all_rows = baseline_rows + q_rows + r_rows

    summary_csv = OUT / "candidate_qr_anchor_protection_screen_summary.csv"
    report_path = OUT / "candidate_qr_anchor_protection_screen_REPORT.md"
    write_csv(summary_csv, all_rows, ["group", "method", "successes", "episodes", "avg_len"])

    display_rows = [
        {
            **row,
            "successes": f"{row['successes']}/{row['episodes']}",
        }
        for row in all_rows
    ]
    lines = [
        "# Candidate Q/R Anchor-Protection Screens",
        "",
        "**Status: rejected at the Lift606 development gate.** These screens",
        "test whether the failed positive-anchor union can be rescued by either",
        "very short fine-tuning or post-hoc interpolation back toward the",
        "positive-only anchor.",
        "",
        "## Lift606 First-20 Results",
        "",
        *table(display_rows, ["group", "method", "successes", "avg_len"]),
        "",
        "## Read",
        "",
        "- Candidate Q finds no early fine-tuning sweet spot. Epochs `1` through",
        "  `5` reach `10/20`, `10/20`, `9/20`, `11/20`, and `10/20`.",
        "- Candidate R finds no useful small parameter move from the positive-only",
        "  checkpoint toward the 20-epoch anchor-union fine-tune. Alphas `0.05`,",
        "  `0.10`, `0.20`, and `0.35` reach `11/20`, `10/20`, `10/20`, and",
        "  `10/20`.",
        "- The anchor-union line should stop. Positive initialization, shorter",
        "  fine-tuning, and checkpoint interpolation all fail to beat the",
        "  positive-only NN baseline (`14/20`).",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
        f"- Candidate Q eval: `{(CANDIDATE_Q_DIR / 'eval20_epochs1to5' / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Candidate R eval: `{(CANDIDATE_R_DIR / 'eval20_p20_alphas' / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Candidate R interpolation manifest: `{(CANDIDATE_R_DIR / 'checkpoints' / 'pos_to_anchor_union_p20_manifest.json').relative_to(ROOT)}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
