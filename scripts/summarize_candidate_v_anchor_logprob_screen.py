#!/usr/bin/env python3
"""Summarize Candidate V output-anchor fine-tuning screen."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
EVAL20_404 = OUT / "candidate_v_anchor_logprob_can404_w10_e20_eval20"
EVAL50_404 = OUT / "candidate_v_anchor_logprob_can404_w10_e10_eval50"
EVAL20_505 = OUT / "candidate_v_anchor_logprob_can505_w10_e10_eval20"
EVAL50_505 = OUT / "candidate_v_anchor_logprob_can505_w10_e10_eval50"
TRAIN_DIR_404 = (
    OUT
    / "candidate_v_anchor_logprob_can404_w10_e20_train"
    / "candidate_v_anchor_logprob_can404_w10_e20"
    / "20260626100527"
)
TRAIN_DIR_505 = (
    OUT
    / "candidate_v_anchor_logprob_can505_w10_e20_train"
    / "candidate_v_anchor_logprob_can505_w10_e20"
    / "20260626101921"
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


def eval_row(
    row: dict[str, str],
    *,
    split: str,
    protocol: str,
    group: str,
    positive_success: int,
) -> dict[str, object]:
    episodes = int(row["eval_episodes"])
    successes = int(round(float(row["success_rate"]) * episodes))
    return {
        "split": split,
        "protocol": protocol,
        "group": group,
        "method": row["checkpoint_name"],
        "train_epochs": epoch_from_name(row["checkpoint_name"]),
        "successes": f"{successes}/{episodes}",
        "success_count": successes,
        "eval_episodes": episodes,
        "avg_len": f"{float(row['avg_len']):.1f}",
        "delta_vs_positive": successes - positive_success,
    }


def baseline_row(
    row: dict[str, str],
    *,
    split: str,
    protocol: str,
    group: str,
    method: str,
    positive_success: int,
) -> dict[str, object]:
    success_count = int(row["success_count"])
    episodes = int(row["eval_episodes"])
    return {
        "split": split,
        "protocol": protocol,
        "group": group,
        "method": method,
        "train_epochs": "",
        "successes": f"{success_count}/{episodes}",
        "success_count": success_count,
        "eval_episodes": episodes,
        "avg_len": row["avg_len"],
        "delta_vs_positive": success_count - positive_success,
    }


def count_row(
    *,
    split: str,
    protocol: str,
    group: str,
    method: str,
    success_count: int,
    eval_episodes: int,
    positive_success: int,
    avg_len: str = "",
) -> dict[str, object]:
    return {
        "split": split,
        "protocol": protocol,
        "group": group,
        "method": method,
        "train_epochs": "",
        "successes": f"{success_count}/{eval_episodes}",
        "success_count": success_count,
        "eval_episodes": eval_episodes,
        "avg_len": avg_len,
        "delta_vs_positive": success_count - positive_success,
    }


def main() -> None:
    split404_rows = read_csv(OUT / "candidate_e_endpoint_screen_summary.csv")
    split505_first20_rows = read_csv(OUT / "candidate_e_multisplit_screen_first20_summary.csv")
    split505_matrix_rows = read_csv(OUT / "candidate_f_frozen_matrix_summary.csv")
    eval20_404_rows = read_csv(EVAL20_404 / "metrics.csv")
    eval50_404_rows = read_csv(EVAL50_404 / "metrics.csv")
    eval20_505_rows = read_csv(EVAL20_505 / "metrics.csv")
    eval50_505_rows = read_csv(EVAL50_505 / "metrics.csv")

    positive20_404 = row_where(split404_rows, method_id="positive_only_nn_top40_first20")
    positive50_404 = row_where(split404_rows, method_id="positive_only_nn_top40")
    weighted50_404 = row_where(split404_rows, method_id="weighted_bc_full_pool")
    candidate_e50_404 = row_where(split404_rows, method_id="candidate_e_initial_gate_weighted_e200")
    first20_505 = row_where(split505_first20_rows, split="505")
    matrix_505 = row_where(split505_matrix_rows, split="505")

    positive20_404_success = int(positive20_404["success_count"])
    positive50_404_success = int(positive50_404["success_count"])
    positive20_505_success = int(first20_505["positive_first20"])
    positive50_505_success = int(matrix_505["positive"])

    rows: list[dict[str, object]] = [
        baseline_row(
            positive20_404,
            split="404",
            protocol="first20",
            group="baseline",
            method="positive_only_nn_top40",
            positive_success=positive20_404_success,
        )
    ]
    rows.extend(
        eval_row(
            row,
            split="404",
            protocol="first20",
            group="candidate_v_anchor_logprob",
            positive_success=positive20_404_success,
        )
        for row in eval20_404_rows
    )
    rows.extend(
        [
            baseline_row(
                positive50_404,
                split="404",
                protocol="eval50",
                group="baseline",
                method="positive_only_nn_top40",
                positive_success=positive50_404_success,
            ),
            baseline_row(
                weighted50_404,
                split="404",
                protocol="eval50",
                group="baseline",
                method="weighted_bc_full_pool",
                positive_success=positive50_404_success,
            ),
            baseline_row(
                candidate_e50_404,
                split="404",
                protocol="eval50",
                group="router_reference",
                method="candidate_e_initial_gate_weighted_e200",
                positive_success=positive50_404_success,
            ),
        ]
    )
    rows.extend(
        eval_row(
            row,
            split="404",
            protocol="eval50",
            group="candidate_v_anchor_logprob",
            positive_success=positive50_404_success,
        )
        for row in eval50_404_rows
    )
    rows.extend(
        [
            count_row(
                split="505",
                protocol="first20",
                group="baseline",
                method="positive_only_nn_top40",
                success_count=positive20_505_success,
                eval_episodes=20,
                positive_success=positive20_505_success,
            ),
            count_row(
                split="505",
                protocol="first20",
                group="baseline",
                method="weighted_bc_full_pool",
                success_count=int(first20_505["weighted_first20"]),
                eval_episodes=20,
                positive_success=positive20_505_success,
            ),
            count_row(
                split="505",
                protocol="first20",
                group="router_reference",
                method="candidate_e_initial_gate_weighted_e200",
                success_count=int(first20_505["candidate_e_first20"]),
                eval_episodes=20,
                positive_success=positive20_505_success,
            ),
        ]
    )
    rows.extend(
        eval_row(
            row,
            split="505",
            protocol="first20",
            group="candidate_v_anchor_logprob",
            positive_success=positive20_505_success,
        )
        for row in eval20_505_rows
    )
    rows.extend(
        [
            count_row(
                split="505",
                protocol="eval50",
                group="baseline",
                method="positive_only_nn_top40",
                success_count=positive50_505_success,
                eval_episodes=50,
                positive_success=positive50_505_success,
            ),
            count_row(
                split="505",
                protocol="eval50",
                group="baseline",
                method="weighted_bc_full_pool",
                success_count=int(matrix_505["weighted"]),
                eval_episodes=50,
                positive_success=positive50_505_success,
            ),
            count_row(
                split="505",
                protocol="eval50",
                group="router_reference",
                method="candidate_e_initial_gate_weighted_e200",
                success_count=int(matrix_505["candidate_f"]),
                eval_episodes=50,
                positive_success=positive50_505_success,
            ),
        ]
    )
    rows.extend(
        eval_row(
            row,
            split="505",
            protocol="eval50",
            group="candidate_v_anchor_logprob",
            positive_success=positive50_505_success,
        )
        for row in eval50_505_rows
    )

    first20_candidates = [
        row
        for row in rows
        if row["split"] == "404" and row["protocol"] == "first20" and row["group"] == "candidate_v_anchor_logprob"
    ]
    best_first20 = max(first20_candidates, key=lambda row: int(row["success_count"]))
    eval50_404_candidate = row_where(
        [{key: str(value) for key, value in row.items()} for row in rows],
        split="404",
        protocol="eval50",
        group="candidate_v_anchor_logprob",
    )
    eval50_505_candidate = row_where(
        [{key: str(value) for key, value in row.items()} for row in rows],
        split="505",
        protocol="eval50",
        group="candidate_v_anchor_logprob",
    )

    summary_path = OUT / "candidate_v_anchor_logprob_screen_summary.csv"
    report_path = OUT / "candidate_v_anchor_logprob_screen_REPORT.md"
    write_csv(
        summary_path,
        rows,
        [
            "split",
            "protocol",
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
            "split": row["split"],
            "protocol": row["protocol"],
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
        "# Candidate V Output-Anchor Fine-Tuning Screen",
        "",
        "**Status: failed first frozen validation.** Candidate V",
        "uses positive-only initialization, Candidate C sequence-mask weights, and",
        "a frozen-policy output anchor: the fine-tuned policy is penalized when it",
        "assigns lower log-probability than the initialized policy on high-weight",
        "timesteps.",
        "",
        "## Can Split Results",
        "",
        *table(display_rows, ["split", "protocol", "group", "method", "train_epochs", "successes", "avg_len", "delta_vs_positive"]),
        "",
        "## Read",
        "",
        f"- Best first-20 Candidate V checkpoint: epoch `{best_first20['train_epochs']}` at `{best_first20['successes']}`,",
        "  which is `+1/20` over the positive-only anchor and above previous",
        "  training-side screens on this gate.",
        f"- The split-404 50-episode check for that checkpoint is `{eval50_404_candidate['successes']}`,",
        "  exactly tied with positive-only `39/50` and below the Candidate E router",
        "  reference `46/50`.",
        f"- Frozen split-505 validation reaches `{eval50_505_candidate['successes']}`,",
        "  below positive-only `40/50` despite passing the first-20 stability check",
        "  (`16/20` versus positive-only `15/20`).",
        "- Candidate V is therefore not a scalable breakthrough. It remains useful",
        "  evidence that output anchoring is a better direction than parameter L2,",
        "  but it fails the first non-404 validation gate.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_path.relative_to(ROOT)}`.",
        f"- Split-404 first-20 eval report: `{(EVAL20_404 / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Split-404 50-episode eval report: `{(EVAL50_404 / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Split-505 first-20 eval report: `{(EVAL20_505 / 'REPORT.md').relative_to(ROOT)}`.",
        f"- Split-505 50-episode eval report: `{(EVAL50_505 / 'REPORT.md').relative_to(ROOT)}`.",
        "- Failure analysis: `results/candidate_breakthrough/candidate_v_failure_analysis_REPORT.md`.",
        f"- Split-404 train directory: `{TRAIN_DIR_404.relative_to(ROOT)}`.",
        f"- Split-505 train directory: `{TRAIN_DIR_505.relative_to(ROOT)}`.",
        "- Validation freeze: `METHOD_FREEZE_CANDIDATE_V.md`.",
        "- Split-404 init checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth`.",
        "- Split-404 transition weights: `results/candidate_breakthrough/candidate_c_sequence_mask_preflight/candidate_c_sequence_mask_weights.hdf5`.",
        "- Split-505 init checkpoint: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_positive_only_nn_policy0/train/can_paired_pos40_bad80_split505_positive_only_nn_policy0_official_bc_rnn/20260625144918/models/model_epoch_200.pth`.",
        "- Split-505 transition weights: `results/candidate_breakthrough/candidate_v_split505_sequence_mask_preflight/candidate_c_sequence_mask_weights.hdf5`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
