#!/usr/bin/env python3
"""Summarize Candidate O Lift positive-anchor union training screen."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"
ARTIFACT_DIR = OUT / "candidate_o_lift606_positive_anchor_union"

BASELINES = [
    ("positive_only_nn", OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv"),
    ("triage_bc", OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv"),
    ("weighted_bc", OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv"),
    ("initial_confidence_q25", OUT / "lift606_router_confidence_labeledpos_q25_eval20" / "episode_metrics.csv"),
]

RUNS = [
    ("candidate_o_epoch50", ARTIFACT_DIR / "eval20_epoch50" / "episode_metrics.csv"),
    ("candidate_o_epoch100", ARTIFACT_DIR / "eval20_epoch100" / "episode_metrics.csv"),
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


def summarize_episode_csv(name: str, path: Path, limit: int = 20) -> dict[str, object]:
    rows = read_csv(path)[:limit]
    successes = sum(int(float(row["success"])) for row in rows)
    avg_len = sum(float(row["length"]) for row in rows) / len(rows)
    return {
        "method": name,
        "successes": successes,
        "episodes": len(rows),
        "avg_len": round(avg_len, 3),
    }


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def main() -> None:
    diagnostics = json.loads((ARTIFACT_DIR / "diagnostics.json").read_text(encoding="utf-8"))
    baseline_rows = [summarize_episode_csv(name, path) for name, path in BASELINES]
    run_rows = [summarize_episode_csv(name, path) for name, path in RUNS]
    all_rows = baseline_rows + run_rows

    summary_csv = OUT / "candidate_o_lift_anchor_union_screen_summary.csv"
    report_path = OUT / "candidate_o_lift_anchor_union_screen_REPORT.md"
    write_csv(summary_csv, all_rows, ["method", "successes", "episodes", "avg_len"])

    display_rows = [
        {
            **row,
            "successes": f"{row['successes']}/{row['episodes']}",
        }
        for row in all_rows
    ]
    lines = [
        "# Candidate O Lift Positive-Anchor Union Screen",
        "",
        "**Status: rejected at the Lift606 development gate.** Candidate O is a",
        "training-side attempt to preserve positive-only behavior while admitting",
        "extra triage support at low loss weight.",
        "",
        "## Training Recipe",
        "",
        f"- Train demos: `{diagnostics['train_demo_count']}`.",
        f"- Positive-NN selected unlabeled demos: `{diagnostics['positive_selected_count']}`.",
        f"- Triage selected unlabeled demos: `{diagnostics['triage_selected_count']}`.",
        f"- Triage-only extra demos: `{diagnostics['triage_only_extra_count']}`.",
        "- Loss weights: labeled positives and positive-NN selected demos `1.0`,",
        "  triage-only extras `0.25`.",
        "- Training budget: `100` epochs x `100` steps, with epoch `50` and `100`",
        "  checkpoints evaluated.",
        "",
        "## Lift606 First-20 Results",
        "",
        *table(display_rows, ["method", "successes", "avg_len"]),
        "",
        "## Read",
        "",
        "- Candidate O collapses below every relevant Lift606 baseline.",
        "- The low-weight triage extras do not act like a harmless coverage",
        "  regularizer; the policy loses most positive-only anchor behavior by",
        "  epoch 50 and remains weak by epoch 100.",
        "- Do not continue this constant-demo-weight union recipe to 200 epochs.",
        "  A future training-side attempt needs either stronger anchor protection",
        "  or a different loss, not simply adding triage support at a smaller",
        "  constant weight.",
        "",
        "## Artifacts",
        "",
        f"- Preflight report: `{(ARTIFACT_DIR / 'candidate_o_lift_anchor_union_preflight_REPORT.md').relative_to(ROOT)}`.",
        f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
        f"- Epoch 50 eval: `{(ARTIFACT_DIR / 'eval20_epoch50' / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Epoch 100 eval: `{(ARTIFACT_DIR / 'eval20_epoch100' / 'REPORT.md').relative_to(ROOT)}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
