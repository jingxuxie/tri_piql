#!/usr/bin/env python3
"""Summarize Candidate T policy-space interpolation screen."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
CANDIDATE_DIR = OUT / "candidate_t_policy_interpolation_can404"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def baseline_row(rows: list[dict[str, str]], method_id: str) -> dict[str, str]:
    matches = [row for row in rows if row["method_id"] == method_id]
    if len(matches) != 1:
        raise ValueError(f"expected one baseline row for {method_id}, found {len(matches)}")
    return matches[0]


def alpha_from_name(name: str) -> str:
    return name.removeprefix("pos_to_weighted_alpha_").replace("p", ".")


def main() -> None:
    baseline_rows = read_csv(OUT / "candidate_b_router_screen_summary.csv")
    metrics_rows = read_csv(CANDIDATE_DIR / "eval20" / "metrics.csv")
    manifest = json.loads((CANDIDATE_DIR / "pos_to_weighted_manifest.json").read_text(encoding="utf-8"))

    positive = baseline_row(baseline_rows, "positive_only_nn_top40")
    weighted = baseline_row(baseline_rows, "weighted_bc_full_pool")
    positive_success = int(positive["success_count"])
    weighted_success = int(weighted["success_count"])

    rows: list[dict[str, object]] = [
        {
            "group": "baseline",
            "method": "positive_only_nn_top40",
            "alpha": "",
            "successes": f"{positive_success}/{positive['eval_episodes']}",
            "success_count": positive_success,
            "eval_episodes": int(positive["eval_episodes"]),
            "avg_len": positive["avg_len"],
            "delta_vs_positive": 0,
        },
        {
            "group": "baseline",
            "method": "weighted_bc_full_pool",
            "alpha": "1.00",
            "successes": f"{weighted_success}/{weighted['eval_episodes']}",
            "success_count": weighted_success,
            "eval_episodes": int(weighted["eval_episodes"]),
            "avg_len": weighted["avg_len"],
            "delta_vs_positive": weighted_success - positive_success,
        },
    ]
    for row in metrics_rows:
        episodes = int(row["eval_episodes"])
        successes = int(round(float(row["success_rate"]) * episodes))
        rows.append(
            {
                "group": "candidate_t_interpolation",
                "method": row["checkpoint_name"],
                "alpha": alpha_from_name(row["checkpoint_name"]),
                "successes": f"{successes}/{episodes}",
                "success_count": successes,
                "eval_episodes": episodes,
                "avg_len": f"{float(row['avg_len']):.1f}",
                "delta_vs_positive": successes - positive_success,
            }
        )

    candidate_rows = [row for row in rows if row["group"] == "candidate_t_interpolation"]
    best_candidate = max(candidate_rows, key=lambda row: int(row["success_count"]))
    if int(best_candidate["success_count"]) >= positive_success:
        raise AssertionError(
            "Candidate T unexpectedly matched or beat the positive-only anchor; "
            "review before marking this screen rejected."
        )

    summary_path = OUT / "candidate_t_policy_interpolation_screen_summary.csv"
    report_path = OUT / "candidate_t_policy_interpolation_screen_REPORT.md"
    write_csv(
        summary_path,
        rows,
        [
            "group",
            "method",
            "alpha",
            "successes",
            "success_count",
            "eval_episodes",
            "avg_len",
            "delta_vs_positive",
        ],
    )

    display_rows = [
        {
            "group": row["group"],
            "method": row["method"],
            "alpha": row["alpha"],
            "successes": row["successes"],
            "avg_len": row["avg_len"],
            "delta_vs_positive": row["delta_vs_positive"],
        }
        for row in rows
    ]
    lines = [
        "# Candidate T Policy-Interpolation Screen",
        "",
        "**Status: rejected at the Can split-404 first-20 gate.** Candidate T",
        "tests whether a small policy-space move from the positive-only checkpoint",
        "toward the weighted-BC checkpoint can preserve anchor behavior while",
        "absorbing broad-coverage behavior, without a rollout-time router.",
        "",
        "## Can Split-404 First-20 Results",
        "",
        *table(display_rows, ["group", "method", "alpha", "successes", "avg_len", "delta_vs_positive"]),
        "",
        "## Read",
        "",
        "- The positive-only anchor is `17/20` on the matched first-20 protocol.",
        "- The best interpolation is alpha `0.05` at `16/20`; alpha `0.10` falls",
        "  to `13/20`, and alpha `0.20` collapses to `3/20`.",
        "- This rejects naive policy-space interpolation as an anchor-preserving",
        "  way to combine positive-only and weighted-coverage behavior on the",
        "  known split-404 bottleneck.",
        "- A future training-side candidate needs an explicit objective that",
        "  preserves the anchor policy locally; simple parameter averaging is not",
        "  enough.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_path.relative_to(ROOT)}`.",
        f"- Eval report: `{(CANDIDATE_DIR / 'eval20' / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Interpolation manifest: `{(CANDIDATE_DIR / 'pos_to_weighted_manifest.json').relative_to(ROOT)}`.",
        f"- Base checkpoint: `{manifest['base']}`.",
        f"- Target checkpoint: `{manifest['target']}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
