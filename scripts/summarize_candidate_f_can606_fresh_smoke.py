#!/usr/bin/env python3
"""Summarize fresh Can606 Candidate F no-tail branch smoke."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"

RUNS = [
    ("positive_only_nn", OUT / "can606_positive_epoch200_eval20"),
    ("weighted_bc", OUT / "can606_weighted_epoch200_eval20"),
    ("candidate_e_gate", OUT / "can606_candidate_e_gate_eval20"),
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


def summarize_run(method: str, run_dir: Path) -> dict[str, object]:
    metrics = read_csv(run_dir / "metrics.csv")[0]
    episodes = int(metrics["eval_episodes"])
    successes = int(round(float(metrics["success_rate"]) * episodes))
    row = {
        "method": method,
        "successes": successes,
        "episodes": episodes,
        "avg_len": round(float(metrics["avg_len"]), 3),
        "gate_opens": "",
        "choices_positive": "",
        "choices_weighted": "",
        "artifact": str(run_dir.relative_to(ROOT)),
    }
    if method == "candidate_e_gate":
        episode_rows = read_csv(run_dir / "episode_metrics.csv")
        row["gate_opens"] = sum(int(r["initial_gate_open"]) for r in episode_rows)
        row["choices_positive"] = int(metrics["choices_positive"])
        row["choices_weighted"] = int(metrics["choices_weighted"])
    return row


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def main() -> None:
    rows = [summarize_run(method, run_dir) for method, run_dir in RUNS]
    summary_csv = OUT / "candidate_f_can606_fresh_smoke_summary.csv"
    report_path = OUT / "candidate_f_can606_fresh_smoke_REPORT.md"
    write_csv(
        summary_csv,
        rows,
        [
            "method",
            "successes",
            "episodes",
            "avg_len",
            "gate_opens",
            "choices_positive",
            "choices_weighted",
            "artifact",
        ],
    )

    display_rows = [
        {
            **row,
            "successes": f"{row['successes']}/{row['episodes']}",
        }
        for row in rows
    ]
    split = json.loads((OUT / "splits" / "can_paired_pos40_bad80_split606" / "split_indices.json").read_text())
    lines = [
        "# Candidate F Can606 Fresh Smoke",
        "",
        "**Status: neutral fresh Can no-tail check.** Candidate F would use the",
        "Candidate E initial-distance gate on Can606 because the positive-NN",
        "selected support has no classifier-probability tail in the fresh",
        "preflight.",
        "",
        f"Split seed: `{split['split_seed']}`. Eval protocol: `20` valid-positive",
        "starts, horizon `400`, policy seed `0`, epoch `200` checkpoints.",
        "",
        "## Results",
        "",
        *table(display_rows, ["method", "successes", "avg_len", "gate_opens", "artifact"]),
        "",
        "## Read",
        "",
        "- Candidate E gate ties positive-only on this fresh no-tail Can split:",
        "  both reach `16/20`.",
        "- Weighted BC is weaker at `14/20`.",
        "- The gate opens on `2/20` episodes, both for the repeated `demo_39`",
        "  initial state. This does not create a net first-20 improvement.",
        "- This is not a Candidate F validation win, but it is also not a fresh",
        "  Can no-tail failure. A 50-episode continuation is only worth running",
        "  as part of a broader fresh Can-only matrix.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
        "- Positive-only eval: `results/candidate_g_fresh_preflight/can606_positive_epoch200_eval20/REPORT.md`.",
        "- Weighted eval: `results/candidate_g_fresh_preflight/can606_weighted_epoch200_eval20/REPORT.md`.",
        "- Candidate E gate eval: `results/candidate_g_fresh_preflight/can606_candidate_e_gate_eval20/REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
