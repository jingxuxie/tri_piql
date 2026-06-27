#!/usr/bin/env python3
"""Summarize the predeclared split-505 CAU fallback validation.

The route is frozen from the Can404 post-hoc feature-gate audit:
use CAU action-conflict only when
``initial_anchor_pos_dist_mean > 2.883``; otherwise use positive-only.
This script does not fit a threshold on split 505.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"
FEATURE_CSV = ROOT / "results" / "candidate_breakthrough" / "candidate_v_failure_analysis_per_initial.csv"
POSITIVE_EPISODES = (
    ROOT
    / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_positive_only_nn_policy0/eval/episode_metrics.csv"
)
CAU_EPISODES = ROOT / "results/sota_candidate/cau_action_conflict_can505_b005_m05_eval20/episode_metrics.csv"
CAU_EPISODES_50 = ROOT / "results/sota_candidate/cau_action_conflict_can505_b005_m05_eval50/episode_metrics.csv"

SPLIT = "505"
GATE_FEATURE = "initial_anchor_pos_dist_mean"
GATE_DIRECTION = "gt"
GATE_THRESHOLD = 2.883
THRESHOLD_SOURCE = "Can404 post-hoc anchor feature-gate preflight"


@dataclass(frozen=True)
class CheckpointResult:
    checkpoint_name: str
    positive_successes: int
    cau_successes: int
    routed_successes: int
    gains: int
    losses: int
    opened_episodes: int
    opened_initials: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_split_features() -> dict[str, float]:
    features: dict[str, float] = {}
    with FEATURE_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["split"] == SPLIT:
                features[row["initial_demo_id"]] = float(row[GATE_FEATURE])
    if not features:
        raise AssertionError(f"no split-{SPLIT} rows in {FEATURE_CSV}")
    return features


def read_episode_successes(
    path: Path,
    *,
    checkpoint_name: str | None,
    max_episodes: int,
) -> dict[tuple[int, str], int]:
    rows: dict[tuple[int, str], int] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            episode = int(row["episode"])
            if episode >= max_episodes:
                continue
            if checkpoint_name is not None and Path(row["checkpoint"]).stem != checkpoint_name:
                continue
            rows[(episode, row["initial_demo_id"])] = int(float(row["success"]))
    if len(rows) != max_episodes:
        raise AssertionError(f"{path} {checkpoint_name} has {len(rows)} rows, expected {max_episodes}")
    return rows


def gate_open(feature_value: float) -> bool:
    if GATE_DIRECTION == "gt":
        return feature_value > GATE_THRESHOLD
    raise AssertionError(f"unsupported gate direction {GATE_DIRECTION}")


def summarize_checkpoint(
    *,
    screen_id: str,
    checkpoint_name: str,
    positive: dict[tuple[int, str], int],
    cau: dict[tuple[int, str], int],
    features: dict[str, float],
) -> tuple[CheckpointResult, list[dict[str, object]]]:
    keys = sorted(positive)
    if keys != sorted(cau):
        raise AssertionError("positive and CAU episode keys differ")

    per_episode: list[dict[str, object]] = []
    routed_successes = 0
    gains = 0
    losses = 0
    opened_episodes = 0
    opened_initials: set[str] = set()
    for episode, demo_id in keys:
        if demo_id not in features:
            raise AssertionError(f"missing feature row for {demo_id}")
        open_gate = gate_open(features[demo_id])
        if open_gate:
            opened_episodes += 1
            opened_initials.add(demo_id)
        positive_success = positive[(episode, demo_id)]
        cau_success = cau[(episode, demo_id)]
        routed_success = cau_success if open_gate else positive_success
        routed_successes += routed_success
        gains += int(routed_success == 1 and positive_success == 0)
        losses += int(routed_success == 0 and positive_success == 1)
        per_episode.append(
            {
                "split": SPLIT,
                "screen_id": screen_id,
                "checkpoint_name": checkpoint_name,
                "episode": episode,
                "initial_demo_id": demo_id,
                GATE_FEATURE: f"{features[demo_id]:.6f}",
                "gate_open": int(open_gate),
                "positive_success": positive_success,
                "cau_success": cau_success,
                "routed_success": routed_success,
                "gain_vs_positive": int(routed_success == 1 and positive_success == 0),
                "loss_vs_positive": int(routed_success == 0 and positive_success == 1),
            }
        )

    result = CheckpointResult(
        checkpoint_name=checkpoint_name,
        positive_successes=sum(positive.values()),
        cau_successes=sum(cau.values()),
        routed_successes=routed_successes,
        gains=gains,
        losses=losses,
        opened_episodes=opened_episodes,
        opened_initials=tuple(sorted(opened_initials, key=lambda x: int(x.split("_")[-1]))),
    )
    return result, per_episode


def main() -> None:
    args = parse_args()
    features = read_split_features()
    eval_specs = [
        ("first20", 20, CAU_EPISODES, ["model_epoch_100", "model_epoch_200"]),
        ("eval50", 50, CAU_EPISODES_50, ["model_epoch_200"]),
    ]

    summary_rows: list[dict[str, object]] = []
    per_episode_rows: list[dict[str, object]] = []
    results: dict[tuple[str, str], CheckpointResult] = {}
    for screen_id, eval_episodes, cau_path, checkpoint_names in eval_specs:
        positive = read_episode_successes(
            POSITIVE_EPISODES,
            checkpoint_name="model_epoch_200",
            max_episodes=eval_episodes,
        )
        for checkpoint_name in checkpoint_names:
            cau = read_episode_successes(cau_path, checkpoint_name=checkpoint_name, max_episodes=eval_episodes)
            result, per_episode = summarize_checkpoint(
                screen_id=screen_id,
                checkpoint_name=checkpoint_name,
                positive=positive,
                cau=cau,
                features=features,
            )
            results[(screen_id, checkpoint_name)] = result
            per_episode_rows.extend(per_episode)
            summary_rows.append(
                {
                    "split": SPLIT,
                    "screen_id": screen_id,
                    "checkpoint_name": result.checkpoint_name,
                    "threshold_source": THRESHOLD_SOURCE,
                    "gate_feature": GATE_FEATURE,
                    "gate_direction": GATE_DIRECTION,
                    "gate_threshold": f"{GATE_THRESHOLD:.6f}",
                    "opened_initial_demo_ids": " ".join(result.opened_initials),
                    "opened_initial_count": len(result.opened_initials),
                    "opened_episodes": result.opened_episodes,
                    "positive_successes": result.positive_successes,
                    "cau_successes": result.cau_successes,
                    "routed_successes": result.routed_successes,
                    "eval_episodes": eval_episodes,
                    "gains_vs_positive": result.gains,
                    "losses_vs_positive": result.losses,
                    "delta_vs_positive": result.routed_successes - result.positive_successes,
                    "status": "fresh_screen_positive"
                    if result.gains > 0 and result.losses == 0
                    else "fresh_screen_mixed",
                }
            )

    expected_open = ("demo_29", "demo_39", "demo_53")
    for key, result in results.items():
        if result.opened_initials != expected_open:
            raise AssertionError(f"{key}: unexpected open initials {result.opened_initials}")
    expected = {
        ("first20", "model_epoch_100"): (15, 12, 15, 1, 1),
        ("first20", "model_epoch_200"): (15, 15, 16, 1, 0),
        ("eval50", "model_epoch_200"): (40, 43, 41, 1, 0),
    }
    actual = {
        key: (
            result.positive_successes,
            result.cau_successes,
            result.routed_successes,
            result.gains,
            result.losses,
        )
        for key, result in results.items()
    }
    if actual != expected:
        raise AssertionError(f"unexpected split-{SPLIT} fallback results: {actual}")

    summary_csv = args.out_dir / "can505_cau_fallback_fresh_validation_summary.csv"
    per_episode_csv = args.out_dir / "can505_cau_fallback_fresh_validation_per_episode.csv"
    report_path = args.out_dir / "CAN505_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md"
    write_csv(
        summary_csv,
        summary_rows,
        [
            "split",
            "screen_id",
            "checkpoint_name",
            "threshold_source",
            "gate_feature",
            "gate_direction",
            "gate_threshold",
            "opened_initial_demo_ids",
            "opened_initial_count",
            "opened_episodes",
            "positive_successes",
            "cau_successes",
            "routed_successes",
            "eval_episodes",
            "gains_vs_positive",
            "losses_vs_positive",
            "delta_vs_positive",
            "status",
        ],
    )
    write_csv(
        per_episode_csv,
        per_episode_rows,
        [
            "split",
            "screen_id",
            "checkpoint_name",
            "episode",
            "initial_demo_id",
            GATE_FEATURE,
            "gate_open",
            "positive_success",
            "cau_success",
            "routed_success",
            "gain_vs_positive",
            "loss_vs_positive",
        ],
    )

    first20_best = results[("first20", "model_epoch_200")]
    eval50_best = results[("eval50", "model_epoch_200")]
    lines = [
        "# Can505 CAU Fallback Fresh Validation",
        "",
        "This report evaluates the CAU-plus-positive fallback rule frozen from the Can404 post-hoc feature-gate audit.",
        "The split-505 threshold is not refit: route to CAU action-conflict only when",
        f"`{GATE_FEATURE} {GATE_DIRECTION} {GATE_THRESHOLD:.3f}`, otherwise use positive-only.",
        "",
        "## Summary",
        "",
        f"- Opened split-505 initials: `{', '.join(first20_best.opened_initials)}`.",
        (
            "- First-20 screen: positive-only "
            f"`{first20_best.positive_successes}/20`, CAU alone `{first20_best.cau_successes}/20`, "
            f"frozen fallback `{first20_best.routed_successes}/20`, gains `{first20_best.gains}`, "
            f"losses `{first20_best.losses}`."
        ),
        (
            "- 50-episode confirmation: positive-only "
            f"`{eval50_best.positive_successes}/50`, CAU alone `{eval50_best.cau_successes}/50`, "
            f"frozen fallback `{eval50_best.routed_successes}/50`, gains `{eval50_best.gains}`, "
            f"losses `{eval50_best.losses}`."
        ),
        "- This is one fresh split, not yet a methods-dominance result.",
        "",
        "## Checkpoints",
        "",
        "| screen | checkpoint | positive | CAU alone | routed | gains | losses | status |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in summary_rows:
        lines.append(
            "| {screen_id} | {checkpoint_name} | {positive_successes}/{eval_episodes} | {cau_successes}/{eval_episodes} | {routed_successes}/{eval_episodes} | {gains_vs_positive} | {losses_vs_positive} | {status} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The frozen fallback passes the first-20 screen and the 50-episode confirmation: both add one success without losing any positive-only successes.",
            "- CAU alone is stronger on the 50-episode check, but the fallback remains the anchor-safe deployable rule because it preserves positive-only starts by construction.",
            "- This is enough to justify another predeclared fresh split, but not enough to change the paper to a SOTA-dominance claim.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{summary_csv}`.",
            f"- Per-episode CSV: `{per_episode_csv}`.",
            f"- CAU split-505 preflight: `{args.out_dir / 'cau_action_conflict_can505_preflight' / 'cau_preflight_REPORT.md'}`.",
            f"- CAU split-505 first-20 eval: `{args.out_dir / 'cau_action_conflict_can505_b005_m05_eval20' / 'REPORT.md'}`.",
            f"- CAU split-505 50-episode eval: `{args.out_dir / 'cau_action_conflict_can505_b005_m05_eval50' / 'REPORT.md'}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
