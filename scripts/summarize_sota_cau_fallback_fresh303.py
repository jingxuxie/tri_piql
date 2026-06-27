#!/usr/bin/env python3
"""Summarize the predeclared split-303 CAU fallback validation.

The route is frozen from the Can404 post-hoc feature-gate audit:
use CAU action-conflict only when
``initial_anchor_pos_dist_mean > 2.883``; otherwise use positive-only.
This script does not fit a threshold on split 303.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"
FEATURE_EPISODES = (
    ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split303_eval20/episode_metrics.csv"
)
POSITIVE_EPISODES = (
    ROOT
    / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split303_positive_only_nn_policy0/eval/episode_metrics.csv"
)
CAU_EPISODES = ROOT / "results/sota_candidate/cau_action_conflict_can303_b005_m05_eval20/episode_metrics.csv"

SPLIT = "303"
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


def demo_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def read_split_features() -> dict[str, float]:
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    with FEATURE_EPISODES.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            demo_id = row["initial_demo_id"]
            totals[demo_id] = totals.get(demo_id, 0.0) + float(row["initial_anchor_pos_dist"])
            counts[demo_id] = counts.get(demo_id, 0) + 1
    if not totals:
        raise AssertionError(f"no feature rows in {FEATURE_EPISODES}")
    return {demo_id: totals[demo_id] / counts[demo_id] for demo_id in totals}


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
                "screen_id": "first20",
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
        opened_initials=tuple(sorted(opened_initials, key=demo_key)),
    )
    return result, per_episode


def status(result: CheckpointResult) -> str:
    if result.gains > 0 and result.losses == 0:
        return "fresh_screen_positive"
    if result.gains == 0 and result.losses == 0:
        return "fresh_screen_neutral"
    return "fresh_screen_mixed"


def main() -> None:
    args = parse_args()
    features = read_split_features()
    positive = read_episode_successes(POSITIVE_EPISODES, checkpoint_name="model_epoch_200", max_episodes=20)

    summary_rows: list[dict[str, object]] = []
    per_episode_rows: list[dict[str, object]] = []
    results: dict[str, CheckpointResult] = {}
    for checkpoint_name in ["model_epoch_100", "model_epoch_200"]:
        cau = read_episode_successes(CAU_EPISODES, checkpoint_name=checkpoint_name, max_episodes=20)
        result, per_episode = summarize_checkpoint(
            checkpoint_name=checkpoint_name,
            positive=positive,
            cau=cau,
            features=features,
        )
        results[checkpoint_name] = result
        per_episode_rows.extend(per_episode)
        summary_rows.append(
            {
                "split": SPLIT,
                "screen_id": "first20",
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
                "eval_episodes": 20,
                "gains_vs_positive": result.gains,
                "losses_vs_positive": result.losses,
                "delta_vs_positive": result.routed_successes - result.positive_successes,
                "status": status(result),
            }
        )

    expected_open = ("demo_39",)
    for key, result in results.items():
        if result.opened_initials != expected_open:
            raise AssertionError(f"{key}: unexpected open initials {result.opened_initials}")
    expected = {
        "model_epoch_100": (15, 14, 15, 0, 0),
        "model_epoch_200": (15, 17, 15, 0, 0),
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

    summary_csv = args.out_dir / "can303_cau_fallback_fresh_validation_summary.csv"
    per_episode_csv = args.out_dir / "can303_cau_fallback_fresh_validation_per_episode.csv"
    report_path = args.out_dir / "CAN303_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md"
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

    best = results["model_epoch_200"]
    lines = [
        "# Can303 CAU Fallback Fresh Validation",
        "",
        "This report evaluates the CAU-plus-positive fallback rule frozen from the Can404 post-hoc feature-gate audit.",
        "The split-303 threshold is not refit: route to CAU action-conflict only when",
        f"`{GATE_FEATURE} {GATE_DIRECTION} {GATE_THRESHOLD:.3f}`, otherwise use positive-only.",
        "",
        "## Summary",
        "",
        f"- Opened split-303 initials: `{', '.join(best.opened_initials)}`.",
        (
            "- First-20 screen: positive-only "
            f"`{best.positive_successes}/20`, CAU alone `{best.cau_successes}/20`, "
            f"frozen fallback `{best.routed_successes}/20`, gains `{best.gains}`, "
            f"losses `{best.losses}`."
        ),
        "- CAU alone improves on this split, but the frozen fallback does not open on the starts where CAU adds successes.",
        "- Because the predeclared first-20 fallback is neutral rather than positive, no 50-episode confirmation is run.",
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
            "- The frozen fallback preserves the positive-only anchor on split 303, but it does not improve the screen.",
            "- This blocks promotion of the fallback as SOTA-dominance evidence and argues against spending longer evaluations on this unchanged gate.",
            "- The remaining technical signal is that CAU alone can help some starts, but the current hidden-label-free gate does not identify those starts.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{summary_csv}`.",
            f"- Per-episode CSV: `{per_episode_csv}`.",
            f"- CAU split-303 preflight: `{args.out_dir / 'cau_action_conflict_can303_preflight' / 'cau_preflight_REPORT.md'}`.",
            f"- CAU split-303 first-20 eval: `{args.out_dir / 'cau_action_conflict_can303_b005_m05_eval20' / 'REPORT.md'}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
