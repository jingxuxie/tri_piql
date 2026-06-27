#!/usr/bin/env python3
"""Audit hidden-label-free CAU-vs-positive gates on completed Can screens.

This is a development audit only. It uses completed split 303 / 404 / 505
first-20 screens to decide whether a stronger gate is worth one fresh
validation. The frozen follow-up gate is then validated separately.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(".")
OUT_DIR = ROOT / "results" / "sota_candidate"
SPLITS = (303, 404, 505)
FEATURE_PATHS = {
    303: ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split303_eval20/episode_metrics.csv",
    404: ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split404_eval20_isolated_rng/episode_metrics.csv",
    505: ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split505_eval20_isolated_rng/episode_metrics.csv",
}
POSITIVE_PATHS = {
    split: ROOT
    / f"results/final_paper_v02/per_seed/can_paired_pos40_bad80_split{split}_positive_only_nn_policy0/eval/episode_metrics.csv"
    for split in SPLITS
}
CAU_PATHS = {
    303: ROOT / "results/sota_candidate/cau_action_conflict_can303_b005_m05_eval20/episode_metrics.csv",
    404: ROOT / "results/sota_candidate/cau_action_conflict_can404_b005_m05_eval20/episode_metrics.csv",
    505: ROOT / "results/sota_candidate/cau_action_conflict_can505_b005_m05_eval20/episode_metrics.csv",
}
FEATURES = ("initial_anchor_pos_dist_mean", "initial_anchor_margin_mean", "initial_anchor_neg_dist_mean")


@dataclass(frozen=True)
class EpisodeRow:
    split: int
    episode: int
    initial_demo_id: str
    positive_success: int
    cau_success: int
    features: dict[str, float]


@dataclass(frozen=True)
class GateSpec:
    label: str
    feature_1: str = ""
    direction_1: str = ""
    threshold_1: float = 0.0
    feature_2: str = ""
    direction_2: str = ""
    threshold_2: float = 0.0
    operator: str = ""


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def checkpoint_stem(path: str) -> str:
    return Path(path).stem


def read_features(path: Path) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = {}
    counts: dict[str, int] = {}
    for row in read_csv(path):
        demo_id = row["initial_demo_id"]
        counts[demo_id] = counts.get(demo_id, 0) + 1
        totals.setdefault(demo_id, {feature: 0.0 for feature in FEATURES})
        totals[demo_id]["initial_anchor_pos_dist_mean"] += float(row["initial_anchor_pos_dist"])
        totals[demo_id]["initial_anchor_margin_mean"] += float(row["initial_anchor_margin"])
        totals[demo_id]["initial_anchor_neg_dist_mean"] += float(row["initial_anchor_neg_dist"])
    return {
        demo_id: {feature: value / counts[demo_id] for feature, value in values.items()}
        for demo_id, values in totals.items()
    }


def read_successes(path: Path, *, max_episodes: int = 20) -> dict[tuple[int, str], int]:
    rows: dict[tuple[int, str], int] = {}
    for row in read_csv(path):
        episode = int(row["episode"])
        if episode >= max_episodes:
            continue
        if checkpoint_stem(row["checkpoint"]) != "model_epoch_200":
            continue
        rows[(episode, row["initial_demo_id"])] = int(float(row["success"]))
    if len(rows) != max_episodes:
        raise AssertionError(f"{path} has {len(rows)} model_epoch_200 rows, expected {max_episodes}")
    return rows


def load_rows() -> list[EpisodeRow]:
    rows: list[EpisodeRow] = []
    for split in SPLITS:
        features = read_features(FEATURE_PATHS[split])
        positive = read_successes(POSITIVE_PATHS[split])
        cau = read_successes(CAU_PATHS[split])
        if sorted(positive) != sorted(cau):
            raise AssertionError(f"split {split}: positive and CAU keys differ")
        for episode, demo_id in sorted(positive):
            rows.append(
                EpisodeRow(
                    split=split,
                    episode=episode,
                    initial_demo_id=demo_id,
                    positive_success=positive[(episode, demo_id)],
                    cau_success=cau[(episode, demo_id)],
                    features=features[demo_id],
                )
            )
    return rows


def predicate(feature: str, direction: str, threshold: float) -> Callable[[EpisodeRow], bool]:
    if direction == "le":
        return lambda row: row.features[feature] <= threshold
    if direction == "gt":
        return lambda row: row.features[feature] > threshold
    raise AssertionError(direction)


def gate(spec: GateSpec) -> Callable[[EpisodeRow], bool]:
    if spec.label == "always_positive":
        return lambda row: False
    if spec.label == "always_cau":
        return lambda row: True
    first = predicate(spec.feature_1, spec.direction_1, spec.threshold_1)
    if not spec.feature_2:
        return first
    second = predicate(spec.feature_2, spec.direction_2, spec.threshold_2)
    if spec.operator == "and":
        return lambda row: first(row) and second(row)
    if spec.operator == "or":
        return lambda row: first(row) or second(row)
    raise AssertionError(spec.operator)


def evaluate(spec: GateSpec, rows: list[EpisodeRow]) -> dict[str, int]:
    fn = gate(spec)
    positive = sum(row.positive_success for row in rows)
    cau = sum(row.cau_success for row in rows)
    routed = 0
    gains = 0
    losses = 0
    opened = 0
    for row in rows:
        opened_here = fn(row)
        opened += int(opened_here)
        success = row.cau_success if opened_here else row.positive_success
        routed += success
        gains += int(success == 1 and row.positive_success == 0)
        losses += int(success == 0 and row.positive_success == 1)
    return {
        "episodes": len(rows),
        "positive_successes": positive,
        "cau_successes": cau,
        "routed_successes": routed,
        "delta_vs_positive": routed - positive,
        "gains_vs_positive": gains,
        "losses_vs_positive": losses,
        "opened_episodes": opened,
    }


def thresholds(rows: list[EpisodeRow], feature: str) -> list[float]:
    values = sorted({row.features[feature] for row in rows})
    return [(left + right) / 2.0 for left, right in zip(values, values[1:])]


def candidate_specs(rows: list[EpisodeRow]) -> list[GateSpec]:
    specs = [GateSpec("always_positive"), GateSpec("always_cau")]
    for feature in FEATURES:
        for threshold in thresholds(rows, feature):
            for direction in ("le", "gt"):
                specs.append(
                    GateSpec(
                        label="one_feature",
                        feature_1=feature,
                        direction_1=direction,
                        threshold_1=threshold,
                    )
                )
    for i, feature_1 in enumerate(FEATURES):
        for feature_2 in FEATURES[i + 1 :]:
            for threshold_1 in thresholds(rows, feature_1):
                for threshold_2 in thresholds(rows, feature_2):
                    for direction_1 in ("le", "gt"):
                        for direction_2 in ("le", "gt"):
                            for operator in ("and", "or"):
                                specs.append(
                                    GateSpec(
                                        label="two_feature",
                                        feature_1=feature_1,
                                        direction_1=direction_1,
                                        threshold_1=threshold_1,
                                        feature_2=feature_2,
                                        direction_2=direction_2,
                                        threshold_2=threshold_2,
                                        operator=operator,
                                    )
                                )
    return specs


def train_score(metrics: dict[str, int]) -> tuple[int, int, int, int]:
    safe = int(metrics["losses_vs_positive"] == 0)
    if not safe:
        return (0, -999, -999, -metrics["opened_episodes"])
    return (
        1,
        metrics["delta_vs_positive"],
        metrics["gains_vs_positive"],
        -metrics["opened_episodes"],
    )


def select_gate(specs: list[GateSpec], rows: list[EpisodeRow]) -> tuple[GateSpec, dict[str, int]]:
    scored = [(train_score(metrics := evaluate(spec, rows)), spec, metrics) for spec in specs]
    _, spec, metrics = max(scored, key=lambda item: item[0])
    return spec, metrics


def spec_row(spec: GateSpec) -> dict[str, object]:
    return {
        "gate_label": spec.label,
        "feature_1": spec.feature_1,
        "direction_1": spec.direction_1,
        "threshold_1": "" if spec.label in {"always_positive", "always_cau"} else f"{spec.threshold_1:.6f}",
        "feature_2": spec.feature_2,
        "direction_2": spec.direction_2,
        "threshold_2": "" if not spec.feature_2 else f"{spec.threshold_2:.6f}",
        "operator": spec.operator,
    }


def metric_row(metrics: dict[str, int]) -> dict[str, object]:
    return {
        "episodes": metrics["episodes"],
        "positive_successes": metrics["positive_successes"],
        "cau_successes": metrics["cau_successes"],
        "routed_successes": metrics["routed_successes"],
        "delta_vs_positive": metrics["delta_vs_positive"],
        "gains_vs_positive": metrics["gains_vs_positive"],
        "losses_vs_positive": metrics["losses_vs_positive"],
        "opened_episodes": metrics["opened_episodes"],
    }


def main() -> None:
    rows = load_rows()
    specs = candidate_specs(rows)
    per_split_rows = []
    for split in SPLITS:
        split_rows = [row for row in rows if row.split == split]
        always_positive = evaluate(GateSpec("always_positive"), split_rows)
        always_cau = evaluate(GateSpec("always_cau"), split_rows)
        oracle = sum(max(row.positive_success, row.cau_success) for row in split_rows)
        per_split_rows.append(
            {
                "split": split,
                "episodes": len(split_rows),
                "positive_successes": always_positive["positive_successes"],
                "cau_successes": always_cau["cau_successes"],
                "positive_cau_oracle_successes": oracle,
                "cau_gains_vs_positive": always_cau["gains_vs_positive"],
                "cau_losses_vs_positive": always_cau["losses_vs_positive"],
            }
        )

    pooled_spec, pooled_train = select_gate(specs, rows)
    loso_rows = []
    for heldout_split in SPLITS:
        train_rows = [row for row in rows if row.split != heldout_split]
        test_rows = [row for row in rows if row.split == heldout_split]
        spec, train_metrics = select_gate(specs, train_rows)
        test_metrics = evaluate(spec, test_rows)
        loso_rows.append(
            {
                "heldout_split": heldout_split,
                **spec_row(spec),
                **{f"train_{key}": value for key, value in metric_row(train_metrics).items()},
                **{f"heldout_{key}": value for key, value in metric_row(test_metrics).items()},
            }
        )

    pooled_rows = [
        {
            "selection_scope": "pooled_303_404_505",
            **spec_row(pooled_spec),
            **metric_row(pooled_train),
        }
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    per_split_csv = OUT_DIR / "cau_gate_feature_audit_per_split.csv"
    loso_csv = OUT_DIR / "cau_gate_feature_audit_loso.csv"
    pooled_csv = OUT_DIR / "cau_gate_feature_audit_pooled_gate.csv"
    report_path = OUT_DIR / "CAU_GATE_FEATURE_AUDIT_REPORT.md"
    write_csv(
        per_split_csv,
        per_split_rows,
        [
            "split",
            "episodes",
            "positive_successes",
            "cau_successes",
            "positive_cau_oracle_successes",
            "cau_gains_vs_positive",
            "cau_losses_vs_positive",
        ],
    )
    write_csv(
        loso_csv,
        loso_rows,
        [
            "heldout_split",
            "gate_label",
            "feature_1",
            "direction_1",
            "threshold_1",
            "feature_2",
            "direction_2",
            "threshold_2",
            "operator",
            "train_episodes",
            "train_positive_successes",
            "train_cau_successes",
            "train_routed_successes",
            "train_delta_vs_positive",
            "train_gains_vs_positive",
            "train_losses_vs_positive",
            "train_opened_episodes",
            "heldout_episodes",
            "heldout_positive_successes",
            "heldout_cau_successes",
            "heldout_routed_successes",
            "heldout_delta_vs_positive",
            "heldout_gains_vs_positive",
            "heldout_losses_vs_positive",
            "heldout_opened_episodes",
        ],
    )
    write_csv(
        pooled_csv,
        pooled_rows,
        [
            "selection_scope",
            "gate_label",
            "feature_1",
            "direction_1",
            "threshold_1",
            "feature_2",
            "direction_2",
            "threshold_2",
            "operator",
            "episodes",
            "positive_successes",
            "cau_successes",
            "routed_successes",
            "delta_vs_positive",
            "gains_vs_positive",
            "losses_vs_positive",
            "opened_episodes",
        ],
    )

    lines = [
        "# CAU Gate Feature Audit",
        "",
        "This audit asks whether existing hidden-label-free initial-state features can decide when to use CAU action-conflict instead of positive-only NN.",
        "It uses completed split 303 / 404 / 505 first-20 screens and is development evidence only.",
        "",
        "## Per-Split Headroom",
        "",
        "| split | positive | CAU alone | positive/CAU oracle | CAU gains | CAU losses |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in per_split_rows:
        lines.append(
            "| {split} | {positive_successes}/{episodes} | {cau_successes}/{episodes} | {positive_cau_oracle_successes}/{episodes} | {cau_gains_vs_positive} | {cau_losses_vs_positive} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Best Pooled Development Gate",
            "",
            (
                f"- Gate: `{pooled_spec.feature_1} {pooled_spec.direction_1} {pooled_spec.threshold_1:.6f} "
                f"{pooled_spec.operator} {pooled_spec.feature_2} {pooled_spec.direction_2} {pooled_spec.threshold_2:.6f}`."
            ),
            (
                "- Pooled development result: routed "
                f"`{pooled_train['routed_successes']}/{pooled_train['episodes']}` versus positive-only "
                f"`{pooled_train['positive_successes']}/{pooled_train['episodes']}`, CAU alone "
                f"`{pooled_train['cau_successes']}/{pooled_train['episodes']}`, gains "
                f"`{pooled_train['gains_vs_positive']}`, losses `{pooled_train['losses_vs_positive']}`."
            ),
            "",
            "## Leave-One-Split-Out Check",
            "",
            "| held-out split | train routed | train losses | held-out routed | held-out losses | gate |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in loso_rows:
        gate_text = (
            f"{row['feature_1']} {row['direction_1']} {row['threshold_1']} "
            f"{row['operator']} {row['feature_2']} {row['direction_2']} {row['threshold_2']}"
        )
        lines.append(
            f"| {row['heldout_split']} | {row['train_routed_successes']}/{row['train_episodes']} | "
            f"{row['train_losses_vs_positive']} | {row['heldout_routed_successes']}/{row['heldout_episodes']} | "
            f"{row['heldout_losses_vs_positive']} | `{gate_text}` |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The pooled gate is promising enough for one frozen fresh validation, but it is not paper evidence because it is selected on completed screens.",
            "- Leave-one-split-out is fragile: the held-out split-404 check preserves total successes but incurs an anchor loss.",
            "- Freeze the pooled two-feature gate for the next unused split only; stop immediately if the fresh screen has any anchor loss or no gain.",
            "",
            "## Outputs",
            "",
            f"- Per-split CSV: `{per_split_csv}`.",
            f"- Leave-one-split-out CSV: `{loso_csv}`.",
            f"- Pooled gate CSV: `{pooled_csv}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected_gate = (
        "initial_anchor_pos_dist_mean",
        "le",
        "initial_anchor_neg_dist_mean",
        "gt",
        "or",
    )
    actual_gate = (
        pooled_spec.feature_1,
        pooled_spec.direction_1,
        pooled_spec.feature_2,
        pooled_spec.direction_2,
        pooled_spec.operator,
    )
    if actual_gate != expected_gate or pooled_train["routed_successes"] != 51 or pooled_train["losses_vs_positive"] != 0:
        raise AssertionError(f"unexpected pooled gate {pooled_spec} {pooled_train}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
