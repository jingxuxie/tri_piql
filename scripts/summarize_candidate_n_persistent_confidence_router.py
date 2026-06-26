#!/usr/bin/env python3
"""Summarize Candidate N persistent temporal confidence routing screens."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"

BASELINES = [
    ("positive_only_nn", OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv"),
    ("triage_bc", OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv"),
    ("weighted_bc", OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv"),
    ("initial_confidence_q25", OUT / "lift606_router_confidence_labeledpos_q25_eval20" / "episode_metrics.csv"),
    (
        "raw_temporal_sequence_q25",
        OUT / "lift606_router_temporal_confidence_labeledpos_seq_q25_eval20" / "episode_metrics.csv",
    ),
]

RUNS = [
    (
        "persistent_sequence_q25_k10",
        OUT / "lift606_router_persistent_confidence_labeledpos_seq_q25_k10_eval20",
    ),
    (
        "persistent_sequence_q25_k20",
        OUT / "lift606_router_persistent_confidence_labeledpos_seq_q25_k20_eval20",
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


def successes_from_episode_csv(path: Path, limit: int = 20) -> tuple[int, int, float]:
    rows = read_csv(path)[:limit]
    successes = sum(int(float(row["success"])) for row in rows)
    avg_len = sum(float(row["length"]) for row in rows) / len(rows)
    return successes, len(rows), avg_len


def summarize_run(name: str, path: Path) -> dict[str, object]:
    metrics = read_csv(path / "metrics.csv")[0]
    episodes = read_csv(path / "episode_metrics.csv")
    diagnostics = json.loads((path / "diagnostics.json").read_text(encoding="utf-8"))
    eval_episodes = int(metrics["eval_episodes"])
    successes = int(round(float(metrics["success_rate"]) * eval_episodes))
    switched = [row for row in episodes if row["temporal_persistent_policy"]]
    gate_counts = [float(row["temporal_gate_open_count"]) for row in episodes]
    return {
        "method": name,
        "successes": successes,
        "episodes": eval_episodes,
        "avg_len": round(float(metrics["avg_len"]), 3),
        "threshold": round(float(diagnostics["effective_initial_feature_threshold"]), 6),
        "threshold_source": diagnostics["initial_feature_threshold_source"],
        "persistence_steps": diagnostics["temporal_persistence_steps"],
        "switched_episodes": len(switched),
        "gate_open_mean": round(sum(gate_counts) / len(gate_counts), 3),
        "choices_positive": int(metrics["choices_positive"]),
        "choices_triage": int(metrics["choices_triage"]),
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
    baseline_rows = []
    for name, path in BASELINES:
        successes, episodes, avg_len = successes_from_episode_csv(path)
        baseline_rows.append(
            {
                "method": name,
                "successes": f"{successes}/{episodes}",
                "avg_len": round(avg_len, 3),
            }
        )
    run_rows = [summarize_run(name, path) for name, path in RUNS]

    summary_csv = OUT / "candidate_n_persistent_confidence_router_summary.csv"
    report_path = OUT / "candidate_n_persistent_confidence_router_REPORT.md"
    write_csv(
        summary_csv,
        run_rows,
        [
            "method",
            "successes",
            "episodes",
            "avg_len",
            "threshold",
            "threshold_source",
            "persistence_steps",
            "switched_episodes",
            "gate_open_mean",
            "choices_positive",
            "choices_triage",
        ],
    )

    lines = [
        "# Candidate N Persistent Confidence Router",
        "",
        "**Status: rejected at the Lift606 development gate.** Candidate N keeps",
        "Candidate M's temporal confidence feature but adds hysteresis: start from",
        "positive-only, require several consecutive low-confidence steps, then",
        "switch to triage for the rest of the episode.",
        "",
        "## Lift606 Context",
        "",
        *table(baseline_rows, ["method", "successes", "avg_len"]),
        "",
        "## Persistent Screens",
        "",
        *table(
            [
                {
                    **row,
                    "successes": f"{row['successes']}/{row['episodes']}",
                }
                for row in run_rows
            ],
            [
                "method",
                "successes",
                "avg_len",
                "threshold",
                "threshold_source",
                "persistence_steps",
                "switched_episodes",
                "gate_open_mean",
                "choices_positive",
                "choices_triage",
            ],
        ),
        "",
        "## Read",
        "",
        "- Persistence repairs most of the raw temporal over-switching damage, but",
        "  it still does not clear the positive-only dev baseline.",
        "- k10 reaches `13/20`, below positive-only `14/20` and far below the",
        "  initial confidence gate `18/20`.",
        "- k20 is stricter but worse at `11/20`, so simply delaying the switch is",
        "  not a useful Lift repair.",
        "- No fresh Lift707 eval was run for Candidate N. The router line should",
        "  stop here unless a learned gate or policy-training change gives a",
        "  stronger development-split signal.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
        "- k10 eval: `results/candidate_g_fresh_preflight/lift606_router_persistent_confidence_labeledpos_seq_q25_k10_eval20/REPORT.md`.",
        "- k20 eval: `results/candidate_g_fresh_preflight/lift606_router_persistent_confidence_labeledpos_seq_q25_k20_eval20/REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
