#!/usr/bin/env python3
"""Matched-start anchor-overlap audit for the Can404 SOTA-candidate screens."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    label: str
    role: str
    episode_metrics: Path
    checkpoint_name: str


METHODS = [
    MethodSpec(
        "positive_only_nn_top40",
        "Positive-only NN top40",
        "anchor_baseline",
        ROOT
        / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/eval/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "weighted_bc_full_pool",
        "Weighted BC full pool",
        "baseline",
        ROOT
        / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/eval/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "v01_triage_bc",
        "v0.1 TRIAGE-BC",
        "baseline",
        ROOT
        / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_triage_bc_policy0/eval/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "bc_all_mixed",
        "All-demo BC",
        "diagnostic_control",
        ROOT
        / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_bc_all_mixed_policy0/eval/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "all_positive_oracle",
        "All-positive oracle",
        "oracle_control",
        ROOT
        / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_all_train_positive_oracle_policy0/eval/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "candidate_c_sequence_mask",
        "Candidate C sequence mask",
        "previous_candidate",
        ROOT / "results/candidate_breakthrough/candidate_c_mask_can404_e200_eval20_epoch200/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "sm_rwbc",
        "SM-RWBC m0.03 lambda2 combined",
        "sota_candidate",
        ROOT / "results/sota_candidate/sm_rwbc_can404_m003_lam2_combined_eval20/episode_metrics.csv",
        "model_epoch_100",
    ),
    MethodSpec(
        "cau_action_conflict",
        "CAU action-conflict",
        "sota_candidate",
        ROOT / "results/sota_candidate/cau_action_conflict_can404_b005_m05_eval20/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "safeexpand",
        "SafeExpand demo103",
        "sota_candidate",
        ROOT / "results/sota_candidate/safeexpand_can404_demo103_eval20/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "demo_dpo_refcenter",
        "Demo-DPO ref-centered",
        "sota_candidate",
        ROOT / "results/sota_candidate/demo_pref_refcenter_can404_w1_e20_eval20/episode_metrics.csv",
        "model_epoch_5",
    ),
    MethodSpec(
        "iql_awbc_norm_topq",
        "IQL-AWBC norm-topq",
        "sota_candidate_diagnostic",
        ROOT / "results/sota_candidate/iql_awbc_can404_norm_topq_e100_eval20/episode_metrics.csv",
        "model_epoch_100",
    ),
    MethodSpec(
        "anchored_iql_awbc",
        "Anchored IQL-AWBC",
        "sota_candidate",
        ROOT / "results/sota_candidate/anchored_iql_awbc_can404_w10_e20_eval20/episode_metrics.csv",
        "model_epoch_10",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def checkpoint_matches(checkpoint: str, checkpoint_name: str) -> bool:
    return Path(checkpoint).stem == checkpoint_name


def read_episode_successes(spec: MethodSpec, max_episodes: int = 20) -> dict[tuple[int, str], int]:
    rows: dict[tuple[int, str], int] = {}
    with spec.episode_metrics.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            episode = int(row["episode"])
            if episode >= max_episodes:
                continue
            if not checkpoint_matches(row["checkpoint"], spec.checkpoint_name):
                continue
            key = (episode, row["initial_demo_id"])
            rows[key] = int(float(row["success"]))
    if len(rows) != max_episodes:
        raise AssertionError(f"{spec.method_id} has {len(rows)} matched rows, expected {max_episodes}")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    by_method = {spec.method_id: read_episode_successes(spec) for spec in METHODS}
    positive = by_method["positive_only_nn_top40"]
    oracle = by_method["all_positive_oracle"]

    positive_successes = sum(positive.values())
    rows: list[dict[str, object]] = []
    for spec in METHODS:
        successes = by_method[spec.method_id]
        keys = sorted(positive)
        gains = sum(successes[key] == 1 and positive[key] == 0 for key in keys)
        losses = sum(successes[key] == 0 and positive[key] == 1 for key in keys)
        retained = sum(successes[key] == 1 and positive[key] == 1 for key in keys)
        shared_failures = sum(successes[key] == 0 and positive[key] == 0 for key in keys)
        oracle_solved_losses = sum(
            successes[key] == 0 and positive[key] == 1 and oracle[key] == 1 for key in keys
        )
        rows.append(
            {
                "method_id": spec.method_id,
                "label": spec.label,
                "role": spec.role,
                "checkpoint": spec.checkpoint_name,
                "success_count": sum(successes.values()),
                "eval_episodes": len(successes),
                "delta_vs_positive": sum(successes.values()) - positive_successes,
                "gains_vs_positive": gains,
                "losses_vs_positive": losses,
                "retained_positive_successes": retained,
                "shared_positive_failures": shared_failures,
                "oracle_solved_positive_losses": oracle_solved_losses,
            }
        )

    fieldnames = [
        "method_id",
        "label",
        "role",
        "checkpoint",
        "success_count",
        "eval_episodes",
        "delta_vs_positive",
        "gains_vs_positive",
        "losses_vs_positive",
        "retained_positive_successes",
        "shared_positive_failures",
        "oracle_solved_positive_losses",
    ]
    summary_csv = args.out_dir / "can404_anchor_overlap_summary.csv"
    report_path = args.out_dir / "CAN404_ANCHOR_OVERLAP_REPORT.md"
    write_csv(summary_csv, rows, fieldnames)

    row_map = {row["method_id"]: row for row in rows}
    candidate_rows = [row for row in rows if row["role"] == "sota_candidate"]
    best_candidate = max(candidate_rows, key=lambda row: int(row["success_count"]))
    close_candidates = [
        row
        for row in candidate_rows
        if int(row["success_count"]) >= positive_successes - 1
    ]
    broad_failures = [
        row
        for row in rows
        if row["method_id"] in {"weighted_bc_full_pool", "bc_all_mixed", "sm_rwbc", "safeexpand"}
    ]

    lines = [
        "# Can404 Anchor-Overlap Diagnostic",
        "",
        "This report compares the focused SOTA-candidate Can404 screens on the same first `20` valid-positive-start episodes.",
        "It asks whether a candidate preserves the positive-only anchor or trades away starts that positive-only already solves.",
        "",
        "## Summary",
        "",
        f"- Positive-only NN top40 solves `{positive_successes}/20`; the all-positive oracle solves `{row_map['all_positive_oracle']['success_count']}/20`.",
        (
            f"- The best focused SOTA candidates reach `{best_candidate['success_count']}/20`; "
            f"they do not beat the positive-only anchor."
        ),
        "- The near-miss candidates mainly fail by losing positive-only successes, not by discovering many new solvable starts.",
        "- This supports the stop rule in `triage_bc_sota_candidate_plan.md`: do not scale another candidate unless a preflight shows explicit anchor preservation plus new-start gains.",
        "",
        "## Matched-Start Table",
        "",
        "| method | role | score | gains vs positive | losses vs positive | oracle-solved losses |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {label} | {role} | {success_count}/{eval_episodes} | {gains_vs_positive} | {losses_vs_positive} | {oracle_solved_positive_losses} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Readout",
            "",
        ]
    )
    for row in close_candidates:
        lines.append(
            "- `{label}` reaches `{success_count}/20`, with `{gains_vs_positive}` gains over positive-only but `{losses_vs_positive}` positive-only losses.".format(
                **row
            )
        )
    for row in broad_failures:
        lines.append(
            "- `{label}` reaches `{success_count}/20` and loses `{losses_vs_positive}` positive-only successes.".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Interpretation: the failed candidates are not simply missing a little extra coverage. The common failure mode is anchor damage: objectives that add broad coverage, risk weighting, support expansion, or auxiliary losses often break starts the positive-only policy already solves. A future method should be screened first for `losses_vs_positive = 0` or an explicit abstain/fallback rule before any longer endpoint matrix.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{summary_csv}`.",
            f"- Report: `{report_path}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = {
        "positive_only_nn_top40": (17, 0, 0),
        "weighted_bc_full_pool": (13, 2, 6),
        "candidate_c_sequence_mask": (16, 0, 1),
        "sm_rwbc": (10, 2, 9),
        "cau_action_conflict": (16, 2, 3),
        "safeexpand": (12, 1, 6),
        "demo_dpo_refcenter": (16, 1, 2),
        "anchored_iql_awbc": (13, 1, 5),
    }
    actual = {
        str(row["method_id"]): (
            int(row["success_count"]),
            int(row["gains_vs_positive"]),
            int(row["losses_vs_positive"]),
        )
        for row in rows
        if row["method_id"] in expected
    }
    if actual != expected:
        raise AssertionError(f"unexpected Can404 anchor-overlap summary: {actual}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
