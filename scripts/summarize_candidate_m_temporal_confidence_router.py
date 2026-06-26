#!/usr/bin/env python3
"""Summarize Candidate M temporal confidence routing screens."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"

RUNS = [
    {
        "name": "temporal_initial_q25",
        "path": OUT / "lift606_router_temporal_confidence_labeledpos_q25_eval20",
        "description": "temporal gate, threshold from labeled-positive initial states q25",
    },
    {
        "name": "temporal_sequence_q25",
        "path": OUT / "lift606_router_temporal_confidence_labeledpos_seq_q25_eval20",
        "description": "temporal gate, threshold from all labeled-positive sequence timesteps q25",
    },
]

BASELINES = [
    ("positive_only_nn", OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv"),
    ("triage_bc", OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv"),
    ("weighted_bc", OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv"),
    ("initial_confidence_q25", OUT / "lift606_router_confidence_labeledpos_q25_eval20" / "episode_metrics.csv"),
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


def summarize_temporal_run(run: dict[str, object]) -> dict[str, object]:
    path = Path(run["path"])
    metrics = read_csv(path / "metrics.csv")[0]
    episodes = read_csv(path / "episode_metrics.csv")
    diagnostics = json.loads((path / "diagnostics.json").read_text(encoding="utf-8"))
    eval_episodes = int(metrics["eval_episodes"])
    successes = int(round(float(metrics["success_rate"]) * eval_episodes))
    gate_counts = [float(row["temporal_gate_open_count"]) for row in episodes]
    positive_counts = [float(row["choices_positive"]) for row in episodes]
    triage_counts = [float(row["choices_triage"]) for row in episodes]
    return {
        "method": run["name"],
        "description": run["description"],
        "successes": successes,
        "episodes": eval_episodes,
        "avg_len": round(float(metrics["avg_len"]), 3),
        "threshold_source": diagnostics["initial_feature_threshold_source"],
        "threshold": round(float(diagnostics["effective_initial_feature_threshold"]), 6),
        "calibration_values": len(diagnostics["initial_feature_calibration_values"]),
        "gate_open_mean": round(sum(gate_counts) / len(gate_counts), 3),
        "gate_open_min": int(min(gate_counts)),
        "gate_open_max": int(max(gate_counts)),
        "choices_positive": int(sum(positive_counts)),
        "choices_triage": int(sum(triage_counts)),
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
    temporal_rows = [summarize_temporal_run(run) for run in RUNS]
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

    summary_csv = OUT / "candidate_m_temporal_confidence_router_summary.csv"
    report_path = OUT / "candidate_m_temporal_confidence_router_REPORT.md"
    write_csv(
        summary_csv,
        temporal_rows,
        [
            "method",
            "description",
            "successes",
            "episodes",
            "avg_len",
            "threshold_source",
            "threshold",
            "calibration_values",
            "gate_open_mean",
            "gate_open_min",
            "gate_open_max",
            "choices_positive",
            "choices_triage",
        ],
    )

    lines = [
        "# Candidate M Temporal Confidence Router",
        "",
        "**Status: rejected at the Lift606 development gate.** Candidate M tests",
        "whether Candidate K/L's learned GMM confidence signal should be used",
        "during rollout rather than only as an initial episode gate.",
        "",
        "## Lift606 Baselines",
        "",
        *table(baseline_rows, ["method", "successes", "avg_len"]),
        "",
        "## Temporal Screens",
        "",
        *table(
            [
                {
                    **row,
                    "successes": f"{row['successes']}/{row['episodes']}",
                }
                for row in temporal_rows
            ],
            [
                "method",
                "successes",
                "avg_len",
                "threshold_source",
                "threshold",
                "calibration_values",
                "gate_open_mean",
                "gate_open_min",
                "gate_open_max",
                "choices_positive",
                "choices_triage",
            ],
        ),
        "",
        "## Read",
        "",
        "- Per-step temporal gating is much worse than positive-only and the",
        "  initial confidence gate on the development split.",
        "- Initial-state q25 calibration over-switches immediately: it chooses",
        "  triage for `2146` of `2253` executed timesteps.",
        "- Sequence-timestep q25 calibration lowers the threshold from `6.180339`",
        "  to `1.762162`, but still chooses triage for `1847` of `2165` executed",
        "  timesteps and remains at `7/20`.",
        "- Do not run a fresh Lift707 screen for this direct temporal router.",
        "  The next useful direction is a policy-training change or a less",
        "  twitchy learned gate with a predeclared hysteresis/persistence rule.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
        "- Initial-q25 eval: `results/candidate_g_fresh_preflight/lift606_router_temporal_confidence_labeledpos_q25_eval20/REPORT.md`.",
        "- Sequence-q25 eval: `results/candidate_g_fresh_preflight/lift606_router_temporal_confidence_labeledpos_seq_q25_eval20/REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
