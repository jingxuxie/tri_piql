#!/usr/bin/env python3
"""Summarize Candidate E first-20 screens across Can 40p/80b splits."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
FINAL = ROOT / "results" / "final_paper_v02" / "per_seed"

SPLITS = [101, 202, 303, 404, 505]
N_EPISODES = 20


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _endpoint_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if rows and "checkpoint" in rows[0]:
        checkpoints = {row["checkpoint"] for row in rows}
        if len(checkpoints) > 1:
            filtered = [row for row in rows if "model_epoch_200" in row["checkpoint"]]
            if filtered:
                return filtered
    return rows


def _success(rows: list[dict[str, str]], n: int = N_EPISODES) -> tuple[int, float]:
    subset = _endpoint_rows(rows)[:n]
    successes = sum(int(float(row["success"])) for row in subset)
    return successes, successes / len(subset)


def _baseline_csv(split: int, method: str) -> Path:
    run = FINAL / f"can_paired_pos40_bad80_split{split}_{method}_policy0"
    return run / "eval" / "episode_metrics.csv"


def _candidate_csv(split: int) -> Path:
    isolated = OUT / f"candidate_e_initial_posdist_gate_weighted_split{split}_eval20_isolated_rng" / "episode_metrics.csv"
    if isolated.exists():
        return isolated
    if split == 404:
        return OUT / "candidate_e_initial_posdist_gate_weighted_eval20" / "episode_metrics.csv"
    return OUT / f"candidate_e_initial_posdist_gate_weighted_split{split}_eval20" / "episode_metrics.csv"


def main() -> None:
    summary_rows: list[dict[str, object]] = []

    for split in SPLITS:
        row: dict[str, object] = {"split": split}
        for label, method in [
            ("positive_first20", "positive_only_nn"),
            ("weighted_first20", "weighted_bc"),
            ("triage_first20", "triage_bc"),
        ]:
            successes, rate = _success(_read_rows(_baseline_csv(split, method)))
            row[label] = successes
            row[label.replace("_first20", "_rate")] = f"{rate:.3f}"

        candidate_rows = _read_rows(_candidate_csv(split))
        candidate_success, candidate_rate = _success(candidate_rows)
        row["candidate_e_first20"] = candidate_success
        row["candidate_e_rate"] = f"{candidate_rate:.3f}"
        row["gate_opens"] = sum(int(row_.get("initial_gate_open", "0")) for row_ in candidate_rows)
        row["weighted_action_steps"] = sum(int(row_.get("choices_weighted", "0")) for row_ in candidate_rows)
        best_baseline = max(
            int(row["positive_first20"]),
            int(row["weighted_first20"]),
            int(row["triage_first20"]),
        )
        row["best_baseline_first20"] = best_baseline
        row["delta_vs_best_baseline"] = candidate_success - best_baseline
        row["checkpoint_note"] = "weighted last.pth" if split == 101 else "epoch200"
        row["denominator"] = N_EPISODES
        summary_rows.append(row)

    total = {
        "split": "total",
        "positive_first20": sum(int(row["positive_first20"]) for row in summary_rows),
        "weighted_first20": sum(int(row["weighted_first20"]) for row in summary_rows),
        "triage_first20": sum(int(row["triage_first20"]) for row in summary_rows),
        "candidate_e_first20": sum(int(row["candidate_e_first20"]) for row in summary_rows),
        "gate_opens": sum(int(row["gate_opens"]) for row in summary_rows),
        "weighted_action_steps": sum(int(row["weighted_action_steps"]) for row in summary_rows),
        "checkpoint_note": "split101 weighted uses last.pth",
        "denominator": len(SPLITS) * N_EPISODES,
        "best_baseline_first20": sum(int(row["best_baseline_first20"]) for row in summary_rows),
    }
    total["positive_rate"] = f"{int(total['positive_first20']) / (len(SPLITS) * N_EPISODES):.3f}"
    total["weighted_rate"] = f"{int(total['weighted_first20']) / (len(SPLITS) * N_EPISODES):.3f}"
    total["triage_rate"] = f"{int(total['triage_first20']) / (len(SPLITS) * N_EPISODES):.3f}"
    total["candidate_e_rate"] = f"{int(total['candidate_e_first20']) / (len(SPLITS) * N_EPISODES):.3f}"
    total["delta_vs_best_baseline"] = int(total["candidate_e_first20"]) - int(total["best_baseline_first20"])
    summary_rows_with_total = [*summary_rows, total]

    csv_path = OUT / "candidate_e_multisplit_screen_first20_summary.csv"
    fieldnames = [
        "split",
        "positive_first20",
        "positive_rate",
        "weighted_first20",
        "weighted_rate",
        "triage_first20",
        "triage_rate",
        "candidate_e_first20",
        "candidate_e_rate",
        "best_baseline_first20",
        "delta_vs_best_baseline",
        "gate_opens",
        "weighted_action_steps",
        "denominator",
        "checkpoint_note",
    ]
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows_with_total)

    report_path = OUT / "candidate_e_multisplit_screen_REPORT.md"
    lines = [
        "# Candidate E Multi-Split First-20 Screen",
        "",
        "Candidate E uses positive-only by default and switches to weighted BC for",
        "the full episode when the positive-only initial action has labeled",
        "positive-support distance greater than `3.0`.",
        "",
        "This regenerated report prefers isolated-RNG router outputs when present,",
        "so non-selected stochastic policies do not perturb selected-policy samples.",
        "",
        "Baseline entries are first-20 slices from existing 50-episode official",
        "baseline eval CSVs. Candidate E entries are fresh 20-episode router evals.",
        "",
        "| split | positive | weighted | triage | cand E | delta vs best | gate opens | weighted steps | note |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summary_rows_with_total:
        lines.append(
            "| {split} | {positive_first20}/{denominator} | "
            "{weighted_first20}/{denominator} | {triage_first20}/{denominator} | "
            "{candidate_e_first20}/{denominator} | "
            "{delta_vs_best_baseline:+d} | {gate_opens} | "
            "{weighted_action_steps} | {checkpoint_note} |".format(
                split=row["split"],
                positive_first20=row["positive_first20"],
                weighted_first20=row["weighted_first20"],
                triage_first20=row["triage_first20"],
                candidate_e_first20=row["candidate_e_first20"],
                denominator=row["denominator"],
                delta_vs_best_baseline=int(row["delta_vs_best_baseline"]),
                gate_opens=row["gate_opens"],
                weighted_action_steps=row["weighted_action_steps"],
                checkpoint_note=row["checkpoint_note"],
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Isolated-RNG evaluation strengthens Candidate E on split 404",
            "  (`19/20` first-20, `46/50` in the 50-episode follow-up).",
            "- Candidate E matches or beats the best first-20 baseline on splits 202,",
            "  303, 404, and 505, but remains badly below the weighted baseline on",
            "  split 101.",
            "- In aggregate Candidate E reaches `74/100`, beating every single",
            "  aggregate baseline but below the per-split baseline oracle (`76/100`).",
            "- On splits 202 and 303 the gate never opens, so Candidate E reduces to",
            "  the positive-only anchor. On split 101 the same threshold opens on two",
            "  long weighted episodes without rescue, while the split would prefer",
            "  broader weighted behavior overall.",
            "- The next version should calibrate the initial-distance threshold from",
            "  training-only support statistics or add a second confidence feature;",
            "  do not promote the hand-set threshold unchanged.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{csv_path.relative_to(ROOT)}`.",
            "- Router eval dirs:",
            "  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split101_eval20_isolated_rng`,",
            "  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split202_eval20_isolated_rng`,",
            "  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split303_eval20_isolated_rng`,",
            "  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split404_eval20_isolated_rng`,",
            "  `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split505_eval20_isolated_rng`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
