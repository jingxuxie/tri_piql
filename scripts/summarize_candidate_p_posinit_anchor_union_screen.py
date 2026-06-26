#!/usr/bin/env python3
"""Summarize Candidate P positive-initialized Lift anchor-union screen."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"
CANDIDATE_O_DIR = OUT / "candidate_o_lift606_positive_anchor_union"
CANDIDATE_P_DIR = OUT / "candidate_p_lift606_posinit_anchor_union"

BASELINES = [
    ("positive_only_nn", OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv"),
    ("triage_bc", OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv"),
    ("weighted_bc", OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv"),
    ("initial_confidence_q25", OUT / "lift606_router_confidence_labeledpos_q25_eval20" / "episode_metrics.csv"),
]

RUNS = [
    ("candidate_o_epoch50_from_scratch", CANDIDATE_O_DIR / "eval20_epoch50" / "episode_metrics.csv"),
    ("candidate_o_epoch100_from_scratch", CANDIDATE_O_DIR / "eval20_epoch100" / "episode_metrics.csv"),
    ("candidate_p_epoch20_posinit_finetune", CANDIDATE_P_DIR / "eval20_epoch20" / "episode_metrics.csv"),
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
    all_rows = [summarize_episode_csv(name, path) for name, path in BASELINES + RUNS]

    summary_csv = OUT / "candidate_p_posinit_anchor_union_screen_summary.csv"
    report_path = OUT / "candidate_p_posinit_anchor_union_screen_REPORT.md"
    write_csv(summary_csv, all_rows, ["method", "successes", "episodes", "avg_len"])

    display_rows = [
        {
            **row,
            "successes": f"{row['successes']}/{row['episodes']}",
        }
        for row in all_rows
    ]
    lines = [
        "# Candidate P Positive-Initialized Anchor-Union Screen",
        "",
        "**Status: rejected at the Lift606 development gate.** Candidate P",
        "tests whether starting from the positive-only policy can prevent the",
        "Candidate O anchor-union training collapse.",
        "",
        "## Training Recipe",
        "",
        "- Initialize BC-RNN-GMM policy weights from the Lift606 positive-only NN",
        "  epoch-200 checkpoint.",
        "- Fine-tune for `20` epochs x `100` steps on the Candidate O",
        "  positive-anchor union training set.",
        "- Loss weights match Candidate O: labeled positives and positive-NN",
        "  selected demos `1.0`, triage-only extras `0.25`.",
        "- Evaluate the epoch-20 checkpoint on the same Lift606 first-20",
        "  valid-positive starts used by the recent router and training-side",
        "  screens.",
        "",
        "## Lift606 First-20 Results",
        "",
        *table(display_rows, ["method", "successes", "avg_len"]),
        "",
        "## Read",
        "",
        "- Positive initialization prevents the severe from-scratch Candidate O",
        "  collapse, improving from `5/20` at Candidate O epoch 100 to `11/20`.",
        "- The fine-tune still damages the positive-only anchor behavior:",
        "  Candidate P is below positive-only (`14/20`), triage (`13/20`), and",
        "  the initial confidence q25 router (`18/20`).",
        "- Do not continue this anchor-union fine-tune recipe to a longer run.",
        "  The failure mode is not just random initialization; admitting the",
        "  triage-only extras with a constant positive loss still moves the",
        "  policy in the wrong direction.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
        f"- Candidate P eval: `{(CANDIDATE_P_DIR / 'eval20_epoch20' / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Candidate P checkpoint: `{(CANDIDATE_P_DIR / 'train' / 'candidate_p_lift606_posinit_anchor_union_e20_seed0' / '20260626071736' / 'models' / 'model_epoch_20.pth').relative_to(ROOT)}`.",
        f"- Candidate O comparison report: `{(OUT / 'candidate_o_lift_anchor_union_screen_REPORT.md').relative_to(ROOT)}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
