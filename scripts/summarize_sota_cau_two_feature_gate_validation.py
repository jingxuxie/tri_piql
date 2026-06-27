#!/usr/bin/env python3
"""Summarize frozen two-feature CAU gate validation on fresh splits."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"
GATE_CSV = DEFAULT_OUT_DIR / "cau_gate_feature_audit_pooled_gate.csv"
GATE_SOURCE = "pooled split303/404/505 development gate"
SPLIT_SPECS = {
    101: {
        "feature_path": ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split101_eval20/episode_metrics.csv",
        "positive_path": ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split101_positive_only_nn_policy0/eval/episode_metrics.csv",
        "cau_eval20_path": ROOT / "results/sota_candidate/cau_action_conflict_can101_b005_m05_eval20/episode_metrics.csv",
        "cau_eval50_path": ROOT / "results/sota_candidate/cau_action_conflict_can101_b005_m05_eval50/episode_metrics.csv",
    },
    202: {
        "feature_path": ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split202_eval20/episode_metrics.csv",
        "positive_path": ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_positive_only_nn_policy0/eval/episode_metrics.csv",
        "cau_eval20_path": ROOT / "results/sota_candidate/cau_action_conflict_can202_b005_m05_eval20/episode_metrics.csv",
        "cau_eval50_path": ROOT / "results/sota_candidate/cau_action_conflict_can202_b005_m05_eval50/episode_metrics.csv",
    },
}
EXPECTED = {
    ("101", "first20", "model_epoch_100"): (7, 11, 7, 0, 0, 4, ("demo_39", "demo_105")),
    ("101", "first20", "model_epoch_200"): (7, 15, 9, 2, 0, 4, ("demo_39", "demo_105")),
    ("101", "eval50", "model_epoch_200"): (19, 33, 24, 5, 0, 10, ("demo_39", "demo_105")),
    ("202", "first20", "model_epoch_100"): (17, 13, 15, 0, 2, 4, ("demo_5", "demo_189")),
    ("202", "first20", "model_epoch_200"): (17, 16, 17, 0, 0, 4, ("demo_5", "demo_189")),
    ("202", "eval50", "model_epoch_200"): (40, 42, 40, 0, 0, 10, ("demo_5", "demo_189")),
}


@dataclass(frozen=True)
class Gate:
    feature_1: str
    direction_1: str
    threshold_1: float
    feature_2: str
    direction_2: str
    threshold_2: float
    operator: str


@dataclass(frozen=True)
class Result:
    split: str
    screen_id: str
    checkpoint_name: str
    positive_successes: int
    cau_successes: int
    routed_successes: int
    gains: int
    losses: int
    opened_episodes: int
    opened_initials: tuple[str, ...]
    eval_episodes: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def demo_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def load_gate() -> Gate:
    rows = read_csv(GATE_CSV)
    if len(rows) != 1:
        raise AssertionError(f"expected one gate row in {GATE_CSV}, found {len(rows)}")
    row = rows[0]
    return Gate(
        feature_1=row["feature_1"],
        direction_1=row["direction_1"],
        threshold_1=float(row["threshold_1"]),
        feature_2=row["feature_2"],
        direction_2=row["direction_2"],
        threshold_2=float(row["threshold_2"]),
        operator=row["operator"],
    )


def read_features(path: Path) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = {}
    counts: dict[str, int] = {}
    for row in read_csv(path):
        demo_id = row["initial_demo_id"]
        counts[demo_id] = counts.get(demo_id, 0) + 1
        totals.setdefault(
            demo_id,
            {
                "initial_anchor_pos_dist_mean": 0.0,
                "initial_anchor_margin_mean": 0.0,
                "initial_anchor_neg_dist_mean": 0.0,
            },
        )
        totals[demo_id]["initial_anchor_pos_dist_mean"] += float(row["initial_anchor_pos_dist"])
        totals[demo_id]["initial_anchor_margin_mean"] += float(row["initial_anchor_margin"])
        totals[demo_id]["initial_anchor_neg_dist_mean"] += float(row["initial_anchor_neg_dist"])
    return {
        demo_id: {feature: value / counts[demo_id] for feature, value in values.items()}
        for demo_id, values in totals.items()
    }


def read_successes(path: Path, *, checkpoint_name: str, max_episodes: int) -> dict[tuple[int, str], int]:
    rows: dict[tuple[int, str], int] = {}
    for row in read_csv(path):
        episode = int(row["episode"])
        if episode >= max_episodes:
            continue
        if Path(row["checkpoint"]).stem != checkpoint_name:
            continue
        rows[(episode, row["initial_demo_id"])] = int(float(row["success"]))
    if len(rows) != max_episodes:
        raise AssertionError(f"{path} {checkpoint_name} has {len(rows)} rows, expected {max_episodes}")
    return rows


def predicate(value: float, direction: str, threshold: float) -> bool:
    if direction == "le":
        return value <= threshold
    if direction == "gt":
        return value > threshold
    raise AssertionError(direction)


def gate_open(gate: Gate, features: dict[str, float]) -> bool:
    first = predicate(features[gate.feature_1], gate.direction_1, gate.threshold_1)
    second = predicate(features[gate.feature_2], gate.direction_2, gate.threshold_2)
    if gate.operator == "or":
        return first or second
    if gate.operator == "and":
        return first and second
    raise AssertionError(gate.operator)


def summarize(
    *,
    split: str,
    screen_id: str,
    checkpoint_name: str,
    positive: dict[tuple[int, str], int],
    cau: dict[tuple[int, str], int],
    features: dict[str, dict[str, float]],
    gate: Gate,
) -> tuple[Result, list[dict[str, object]]]:
    keys = sorted(positive)
    if keys != sorted(cau):
        raise AssertionError(f"split {split} {screen_id}: positive and CAU keys differ")
    rows: list[dict[str, object]] = []
    routed = 0
    gains = 0
    losses = 0
    opened = 0
    opened_initials: set[str] = set()
    for episode, demo_id in keys:
        open_here = gate_open(gate, features[demo_id])
        opened += int(open_here)
        if open_here:
            opened_initials.add(demo_id)
        positive_success = positive[(episode, demo_id)]
        cau_success = cau[(episode, demo_id)]
        routed_success = cau_success if open_here else positive_success
        routed += routed_success
        gains += int(routed_success == 1 and positive_success == 0)
        losses += int(routed_success == 0 and positive_success == 1)
        rows.append(
            {
                "split": split,
                "screen_id": screen_id,
                "checkpoint_name": checkpoint_name,
                "episode": episode,
                "initial_demo_id": demo_id,
                "initial_anchor_pos_dist_mean": f"{features[demo_id]['initial_anchor_pos_dist_mean']:.6f}",
                "initial_anchor_neg_dist_mean": f"{features[demo_id]['initial_anchor_neg_dist_mean']:.6f}",
                "gate_open": int(open_here),
                "positive_success": positive_success,
                "cau_success": cau_success,
                "routed_success": routed_success,
                "gain_vs_positive": int(routed_success == 1 and positive_success == 0),
                "loss_vs_positive": int(routed_success == 0 and positive_success == 1),
            }
        )
    result = Result(
        split=split,
        screen_id=screen_id,
        checkpoint_name=checkpoint_name,
        positive_successes=sum(positive.values()),
        cau_successes=sum(cau.values()),
        routed_successes=routed,
        gains=gains,
        losses=losses,
        opened_episodes=opened,
        opened_initials=tuple(sorted(opened_initials, key=demo_key)),
        eval_episodes=len(keys),
    )
    return result, rows


def status(result: Result) -> str:
    if result.gains > 0 and result.losses == 0:
        return "fresh_screen_positive"
    if result.gains == 0 and result.losses == 0:
        return "fresh_screen_neutral"
    return "fresh_screen_mixed"


def main() -> None:
    args = parse_args()
    gate = load_gate()
    summary_rows: list[dict[str, object]] = []
    per_episode_rows: list[dict[str, object]] = []
    results: dict[tuple[str, str, str], Result] = {}

    for split_int, spec in SPLIT_SPECS.items():
        split = str(split_int)
        features = read_features(spec["feature_path"])
        positive20 = read_successes(spec["positive_path"], checkpoint_name="model_epoch_200", max_episodes=20)
        cau20_path = spec["cau_eval20_path"]
        for checkpoint_name in ["model_epoch_100", "model_epoch_200"]:
            cau = read_successes(cau20_path, checkpoint_name=checkpoint_name, max_episodes=20)
            result, rows = summarize(
                split=split,
                screen_id="first20",
                checkpoint_name=checkpoint_name,
                positive=positive20,
                cau=cau,
                features=features,
                gate=gate,
            )
            results[(split, "first20", checkpoint_name)] = result
            per_episode_rows.extend(rows)
        if "cau_eval50_path" in spec:
            positive50 = read_successes(spec["positive_path"], checkpoint_name="model_epoch_200", max_episodes=50)
            cau50 = read_successes(spec["cau_eval50_path"], checkpoint_name="model_epoch_200", max_episodes=50)
            result, rows = summarize(
                split=split,
                screen_id="eval50",
                checkpoint_name="model_epoch_200",
                positive=positive50,
                cau=cau50,
                features=features,
                gate=gate,
            )
            results[(split, "eval50", "model_epoch_200")] = result
            per_episode_rows.extend(rows)

    for key, result in sorted(results.items()):
        actual = (
            result.positive_successes,
            result.cau_successes,
            result.routed_successes,
            result.gains,
            result.losses,
            result.opened_episodes,
            result.opened_initials,
        )
        expected = EXPECTED[key]
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")
        summary_rows.append(
            {
                "split": result.split,
                "screen_id": result.screen_id,
                "checkpoint_name": result.checkpoint_name,
                "gate_source": GATE_SOURCE,
                "gate_rule": (
                    f"{gate.feature_1} {gate.direction_1} {gate.threshold_1:.6f} "
                    f"{gate.operator} {gate.feature_2} {gate.direction_2} {gate.threshold_2:.6f}"
                ),
                "opened_initial_demo_ids": " ".join(result.opened_initials),
                "opened_initial_count": len(result.opened_initials),
                "opened_episodes": result.opened_episodes,
                "positive_successes": result.positive_successes,
                "cau_successes": result.cau_successes,
                "routed_successes": result.routed_successes,
                "eval_episodes": result.eval_episodes,
                "gains_vs_positive": result.gains,
                "losses_vs_positive": result.losses,
                "delta_vs_positive": result.routed_successes - result.positive_successes,
                "status": status(result),
            }
        )

    summary_csv = args.out_dir / "cau_two_feature_gate_fresh_validation_summary.csv"
    per_episode_csv = args.out_dir / "cau_two_feature_gate_fresh_validation_per_episode.csv"
    report_path = args.out_dir / "CAU_TWO_FEATURE_GATE_FRESH_VALIDATION_REPORT.md"
    write_csv(
        summary_csv,
        summary_rows,
        [
            "split",
            "screen_id",
            "checkpoint_name",
            "gate_source",
            "gate_rule",
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
            "initial_anchor_pos_dist_mean",
            "initial_anchor_neg_dist_mean",
            "gate_open",
            "positive_success",
            "cau_success",
            "routed_success",
            "gain_vs_positive",
            "loss_vs_positive",
        ],
    )

    split101_20 = results[("101", "first20", "model_epoch_200")]
    split101_50 = results[("101", "eval50", "model_epoch_200")]
    split202_20 = results[("202", "first20", "model_epoch_200")]
    split202_50 = results[("202", "eval50", "model_epoch_200")]
    lines = [
        "# CAU Two-Feature Gate Fresh Validation",
        "",
        "This report validates the two-feature CAU-plus-positive gate selected on completed split 303 / 404 / 505 screens.",
        "The split-101 and split-202 thresholds are frozen before evaluation:",
        f"`{gate.feature_1} {gate.direction_1} {gate.threshold_1:.6f} {gate.operator} {gate.feature_2} {gate.direction_2} {gate.threshold_2:.6f}`.",
        "",
        "## Summary",
        "",
        (
            "- Split101 first20: positive-only "
            f"`{split101_20.positive_successes}/20`, CAU alone `{split101_20.cau_successes}/20`, "
            f"routed `{split101_20.routed_successes}/20`, gains `{split101_20.gains}`, losses `{split101_20.losses}`."
        ),
        (
            "- Split101 50-episode confirmation: positive-only "
            f"`{split101_50.positive_successes}/50`, CAU alone `{split101_50.cau_successes}/50`, "
            f"routed `{split101_50.routed_successes}/50`, gains `{split101_50.gains}`, losses `{split101_50.losses}`."
        ),
        (
            "- Split202 first20: positive-only "
            f"`{split202_20.positive_successes}/20`, CAU alone `{split202_20.cau_successes}/20`, "
            f"routed `{split202_20.routed_successes}/20`, gains `{split202_20.gains}`, losses `{split202_20.losses}`."
        ),
        (
            "- Split202 50-episode confirmation: positive-only "
            f"`{split202_50.positive_successes}/50`, CAU alone `{split202_50.cau_successes}/50`, "
            f"routed `{split202_50.routed_successes}/50`, gains `{split202_50.gains}`, losses `{split202_50.losses}`."
        ),
        "",
        "## Checkpoints",
        "",
        "| split | screen | checkpoint | positive | CAU alone | routed | gains | losses | opened initials | status |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in summary_rows:
        lines.append(
            "| {split} | {screen_id} | {checkpoint_name} | {positive_successes}/{eval_episodes} | {cau_successes}/{eval_episodes} | {routed_successes}/{eval_episodes} | {gains_vs_positive} | {losses_vs_positive} | {opened_initial_demo_ids} | {status} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The frozen two-feature gate has one positive fresh split with 50-episode confirmation and one neutral 50-episode fresh split.",
            "- Split202 shows CAU-alone signal at 50 episodes, but the frozen gate does not route to the repaired starts; this exposes gate recall as the remaining bottleneck.",
            "- This is stronger than the one-feature fallback, but it is still not SOTA-dominance evidence because the gate was selected on earlier completed screens and split202 adds no routed gain.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{summary_csv}`.",
            f"- Per-episode CSV: `{per_episode_csv}`.",
            f"- Gate audit: `{args.out_dir / 'CAU_GATE_FEATURE_AUDIT_REPORT.md'}`.",
            f"- Split101 first20 eval: `{args.out_dir / 'cau_action_conflict_can101_b005_m05_eval20' / 'REPORT.md'}`.",
            f"- Split101 50-episode eval: `{args.out_dir / 'cau_action_conflict_can101_b005_m05_eval50' / 'REPORT.md'}`.",
            f"- Split202 first20 eval: `{args.out_dir / 'cau_action_conflict_can202_b005_m05_eval20' / 'REPORT.md'}`.",
            f"- Split202 50-episode eval: `{args.out_dir / 'cau_action_conflict_can202_b005_m05_eval50' / 'REPORT.md'}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
