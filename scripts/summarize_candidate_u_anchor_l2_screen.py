#!/usr/bin/env python3
"""Summarize Candidate U anchor-L2 fine-tuning screen."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
CANDIDATE_DIR = OUT / "candidate_u_anchor_l2_can404_w1000_e20_eval20"
TRAIN_DIR = (
    OUT
    / "candidate_u_anchor_l2_can404_w1000_e20_train"
    / "candidate_u_anchor_l2_can404_w1000_e20"
    / "20260626095223"
)


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


def row_where(rows: list[dict[str, str]], **criteria: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in criteria.items()):
            return row
    raise KeyError(f"no row matching {criteria}")


def epoch_from_name(name: str) -> int:
    return int(name.removeprefix("model_epoch_"))


def main() -> None:
    baseline_rows = read_csv(OUT / "candidate_c_endpoint_screen_summary.csv")
    metrics_rows = read_csv(CANDIDATE_DIR / "metrics.csv")

    positive = row_where(baseline_rows, method_id="positive_only_nn_top40")
    weighted = row_where(baseline_rows, method_id="weighted_bc_full_pool")
    candidate_c = row_where(baseline_rows, method_id="candidate_c_sequence_mask_e200")
    positive_success = int(positive["success_count"])

    rows: list[dict[str, object]] = [
        {
            "group": "baseline",
            "method": "positive_only_nn_top40",
            "train_epochs": positive["train_epochs"],
            "successes": f"{positive['success_count']}/{positive['eval_episodes']}",
            "success_count": int(positive["success_count"]),
            "eval_episodes": int(positive["eval_episodes"]),
            "avg_len": positive["avg_len"],
            "delta_vs_positive": 0,
        },
        {
            "group": "baseline",
            "method": "weighted_bc_full_pool",
            "train_epochs": weighted["train_epochs"],
            "successes": f"{weighted['success_count']}/{weighted['eval_episodes']}",
            "success_count": int(weighted["success_count"]),
            "eval_episodes": int(weighted["eval_episodes"]),
            "avg_len": weighted["avg_len"],
            "delta_vs_positive": int(weighted["success_count"]) - positive_success,
        },
        {
            "group": "previous_candidate",
            "method": "candidate_c_sequence_mask_e200",
            "train_epochs": candidate_c["train_epochs"],
            "successes": f"{candidate_c['success_count']}/{candidate_c['eval_episodes']}",
            "success_count": int(candidate_c["success_count"]),
            "eval_episodes": int(candidate_c["eval_episodes"]),
            "avg_len": candidate_c["avg_len"],
            "delta_vs_positive": int(candidate_c["success_count"]) - positive_success,
        },
    ]
    for row in metrics_rows:
        episodes = int(row["eval_episodes"])
        successes = int(round(float(row["success_rate"]) * episodes))
        rows.append(
            {
                "group": "candidate_u_anchor_l2",
                "method": row["checkpoint_name"],
                "train_epochs": epoch_from_name(row["checkpoint_name"]),
                "successes": f"{successes}/{episodes}",
                "success_count": successes,
                "eval_episodes": episodes,
                "avg_len": f"{float(row['avg_len']):.1f}",
                "delta_vs_positive": successes - positive_success,
            }
        )

    candidate_rows = [row for row in rows if row["group"] == "candidate_u_anchor_l2"]
    best_candidate = max(candidate_rows, key=lambda row: int(row["success_count"]))
    if int(best_candidate["success_count"]) > positive_success:
        raise AssertionError(
            "Candidate U unexpectedly beat the positive-only anchor; review before marking rejected."
        )

    summary_path = OUT / "candidate_u_anchor_l2_screen_summary.csv"
    report_path = OUT / "candidate_u_anchor_l2_screen_REPORT.md"
    write_csv(
        summary_path,
        rows,
        [
            "group",
            "method",
            "train_epochs",
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
            "train_epochs": row["train_epochs"],
            "successes": row["successes"],
            "avg_len": row["avg_len"],
            "delta_vs_positive": row["delta_vs_positive"],
        }
        for row in rows
    ]
    lines = [
        "# Candidate U Anchor-L2 Fine-Tuning Screen",
        "",
        "**Status: neutral/rejected at the Can split-404 first-20 gate.** Candidate U",
        "tests whether positive-only initialization plus explicit parameter-space",
        "anchor regularization can preserve the positive-only policy while adding",
        "Candidate C sequence-mask coverage.",
        "",
        "## Can Split-404 First-20 Results",
        "",
        *table(display_rows, ["group", "method", "train_epochs", "successes", "avg_len", "delta_vs_positive"]),
        "",
        "## Read",
        "",
        "- The positive-only anchor is `17/20` on the matched first-20 protocol.",
        "- The best Candidate U checkpoint is epoch `5` at `17/20`, matching but",
        "  not improving over the positive-only anchor.",
        "- Later checkpoints degrade to `16/20`, `14/20`, and `16/20`, so the",
        "  extra sequence-mask fine-tuning does not create robust endpoint gain.",
        "- This rejects normalized parameter-L2 anchoring as the needed",
        "  preservation mechanism. If this line is revisited, it should use a",
        "  local output/distribution anchor on positive states, not only parameter",
        "  drift.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_path.relative_to(ROOT)}`.",
        f"- Eval report: `{(CANDIDATE_DIR / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Train directory: `{TRAIN_DIR.relative_to(ROOT)}`.",
        "- Init checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth`.",
        "- Transition weights: `results/candidate_breakthrough/candidate_c_sequence_mask_preflight/candidate_c_sequence_mask_weights.hdf5`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
