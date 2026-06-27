#!/usr/bin/env python3
"""Leave-one-split-out audit for hidden-label-free CAU selector features.

This is a development diagnostic. It asks whether simple initial support-distance
features can select between positive-only and CAU without seeing endpoint labels
on the held-out split. It reuses completed endpoint rollouts; it does not run new
policy evaluations.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(".")
OUT_DIR = ROOT / "results" / "sota_candidate"

FEATURES = (
    "initial_anchor_pos_dist_mean",
    "initial_anchor_neg_dist_mean",
    "initial_anchor_margin_mean",
)
THRESHOLD_QUANTILES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)


SPLITS: dict[int, dict[str, object]] = {
    101: {
        "feature_path": ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split101_eval20/episode_metrics.csv",
        "positive_path": ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split101_positive_only_nn_policy0/eval/episode_metrics.csv",
        "cau_path": OUT_DIR / "cau_action_conflict_can101_b005_m05_eval50/episode_metrics.csv",
        "eval_episodes": 50,
        "positive_substr": "positive_only",
        "cau_substr": "cau_action_conflict",
    },
    202: {
        "feature_path": ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split202_eval20/episode_metrics.csv",
        "positive_path": ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_positive_only_nn_policy0/eval/episode_metrics.csv",
        "cau_path": OUT_DIR / "cau_action_conflict_can202_b005_m05_eval50/episode_metrics.csv",
        "eval_episodes": 50,
        "positive_substr": "positive_only",
        "cau_substr": "cau_action_conflict",
    },
    303: {
        "feature_path": ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split303_eval20/episode_metrics.csv",
        "positive_path": ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split303_positive_only_nn_policy0/eval/episode_metrics.csv",
        "cau_path": OUT_DIR / "cau_action_conflict_can303_b005_m05_eval50/episode_metrics.csv",
        "eval_episodes": 50,
        "positive_substr": "positive_only",
        "cau_substr": "cau_action_conflict",
    },
    404: {
        "feature_path": ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split404_eval20_isolated_rng/episode_metrics.csv",
        "positive_path": ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/eval/episode_metrics.csv",
        "cau_path": OUT_DIR / "cau_action_conflict_can404_b005_m05_eval50/episode_metrics.csv",
        "eval_episodes": 50,
        "positive_substr": "positive_only",
        "cau_substr": "cau_action_conflict",
    },
    505: {
        "feature_path": ROOT / "results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split505_eval20_isolated_rng/episode_metrics.csv",
        "positive_path": ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_positive_only_nn_policy0/eval/episode_metrics.csv",
        "cau_path": OUT_DIR / "cau_action_conflict_can505_b005_m05_eval50/episode_metrics.csv",
        "eval_episodes": 50,
        "positive_substr": "positive_only",
        "cau_substr": "cau_action_conflict",
    },
    606: {
        "feature_path": ROOT / "results/candidate_g_fresh_preflight/can606_candidate_e_gate_eval20/episode_metrics.csv",
        "positive_path": ROOT / "results/candidate_g_fresh_preflight/can606_positive_epoch200_eval20/episode_metrics.csv",
        "cau_path": OUT_DIR / "cau_action_conflict_can606_b005_m05_eval20/episode_metrics.csv",
        "eval_episodes": 20,
        "positive_substr": "positive_only",
        "cau_substr": "cau_action_conflict",
    },
    707: {
        "feature_path": ROOT / "results/candidate_g_fresh_preflight/can707_candidate_e_gate_eval20/episode_metrics.csv",
        "positive_path": OUT_DIR / "can707_positive_weighted_cau_eval50/episode_metrics.csv",
        "cau_path": OUT_DIR / "can707_positive_weighted_cau_eval50/episode_metrics.csv",
        "eval_episodes": 50,
        "positive_substr": "positive_only",
        "cau_substr": "cau_action_conflict",
    },
    808: {
        "feature_path": ROOT / "results/candidate_f_can_fresh_validation/candidate_e_eval/can808_candidate_e_gate_eval50/episode_metrics.csv",
        "positive_path": ROOT / "results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_positive_only_nn_policy0/eval/episode_metrics.csv",
        "cau_path": OUT_DIR / "cau_action_conflict_can808_b005_m05_eval50/episode_metrics.csv",
        "eval_episodes": 50,
        "positive_substr": "positive_only",
        "cau_substr": "cau_action_conflict",
    },
}


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
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


def checkpoint_matches(row: dict[str, str], substring: str) -> bool:
    checkpoint = row.get("checkpoint", "")
    checkpoint_name = row.get("checkpoint_name", "")
    if Path(checkpoint).stem != "model_epoch_200" and checkpoint_name != "model_epoch_200":
        return False
    if substring in checkpoint:
        return True
    if checkpoint_name == substring:
        return True
    return False


def read_successes(path: Path, *, substring: str, eval_episodes: int) -> dict[tuple[int, str], int]:
    out: dict[tuple[int, str], int] = {}
    for row in read_csv(path):
        if not checkpoint_matches(row, substring):
            continue
        episode = int(row["episode"])
        if episode >= eval_episodes:
            continue
        out[(episode, row["initial_demo_id"])] = int(float(row["success"]))
    if len(out) != eval_episodes:
        raise AssertionError(f"{path} {substring}: found {len(out)} rows, expected {eval_episodes}")
    return out


def read_features(path: Path) -> dict[str, dict[str, float]]:
    totals: dict[str, dict[str, float]] = {}
    counts: dict[str, int] = {}
    for row in read_csv(path):
        demo_id = row["initial_demo_id"]
        counts[demo_id] = counts.get(demo_id, 0) + 1
        totals.setdefault(demo_id, {feature: 0.0 for feature in FEATURES})
        totals[demo_id]["initial_anchor_pos_dist_mean"] += float(row["initial_anchor_pos_dist"])
        totals[demo_id]["initial_anchor_neg_dist_mean"] += float(row["initial_anchor_neg_dist"])
        totals[demo_id]["initial_anchor_margin_mean"] += float(row["initial_anchor_margin"])
    return {
        demo_id: {feature: value / counts[demo_id] for feature, value in values.items()}
        for demo_id, values in totals.items()
    }


def load_rows() -> list[EpisodeRow]:
    rows: list[EpisodeRow] = []
    for split, spec in SPLITS.items():
        features = read_features(spec["feature_path"])  # type: ignore[arg-type]
        eval_episodes = int(spec["eval_episodes"])
        positive = read_successes(
            spec["positive_path"],  # type: ignore[arg-type]
            substring=str(spec["positive_substr"]),
            eval_episodes=eval_episodes,
        )
        cau = read_successes(
            spec["cau_path"],  # type: ignore[arg-type]
            substring=str(spec["cau_substr"]),
            eval_episodes=eval_episodes,
        )
        if sorted(positive) != sorted(cau):
            raise AssertionError(f"split {split}: positive and CAU episode keys differ")
        missing = sorted({demo_id for _episode, demo_id in positive} - set(features))
        if missing:
            raise AssertionError(f"split {split}: missing feature rows for {missing}")
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
        open_here = fn(row)
        opened += int(open_here)
        success = row.cau_success if open_here else row.positive_success
        routed += success
        gains += int(success == 1 and row.positive_success == 0)
        losses += int(success == 0 and row.positive_success == 1)
    return {
        "episodes": len(rows),
        "positive_successes": positive,
        "cau_successes": cau,
        "routed_successes": routed,
        "delta_vs_positive": routed - positive,
        "delta_vs_cau": routed - cau,
        "gains_vs_positive": gains,
        "losses_vs_positive": losses,
        "opened_episodes": opened,
    }


def thresholds(rows: list[EpisodeRow], feature: str) -> list[float]:
    values = sorted({row.features[feature] for row in rows})
    if len(values) <= 1:
        return values
    out = []
    for quantile in THRESHOLD_QUANTILES:
        index = round(quantile * (len(values) - 1))
        out.append(values[index])
    return sorted(set(out))


def candidate_specs(rows: list[EpisodeRow]) -> list[GateSpec]:
    specs = [GateSpec("always_positive"), GateSpec("always_cau")]
    for feature in FEATURES:
        for threshold in thresholds(rows, feature):
            for direction in ("le", "gt"):
                specs.append(GateSpec("one_feature", feature, direction, threshold))
    for idx, feature_1 in enumerate(FEATURES):
        for feature_2 in FEATURES[idx + 1 :]:
            for threshold_1 in thresholds(rows, feature_1):
                for threshold_2 in thresholds(rows, feature_2):
                    for direction_1 in ("le", "gt"):
                        for direction_2 in ("le", "gt"):
                            for operator in ("and", "or"):
                                specs.append(
                                    GateSpec(
                                        "two_feature",
                                        feature_1,
                                        direction_1,
                                        threshold_1,
                                        feature_2,
                                        direction_2,
                                        threshold_2,
                                        operator,
                                    )
                                )
    return specs


def train_score_safe(metrics: dict[str, int]) -> tuple[int, int, int, int, int]:
    zero_loss = int(metrics["losses_vs_positive"] == 0)
    useful = int(metrics["delta_vs_positive"] > 0 and metrics["opened_episodes"] > 0)
    return (
        zero_loss,
        useful,
        metrics["delta_vs_positive"],
        metrics["gains_vs_positive"],
        -metrics["opened_episodes"],
    )


def train_score_best_delta(metrics: dict[str, int]) -> tuple[int, int, int]:
    return (
        metrics["delta_vs_positive"],
        -metrics["losses_vs_positive"],
        metrics["gains_vs_positive"],
    )


def select_gate(specs: list[GateSpec], rows: list[EpisodeRow], *, mode: str) -> tuple[GateSpec, dict[str, int]]:
    if mode == "safe":
        key = train_score_safe
    elif mode == "best_delta":
        key = train_score_best_delta
    else:
        raise AssertionError(mode)
    scored = [(key(metrics := evaluate(spec, rows)), spec, metrics) for spec in specs]
    _score, spec, metrics = max(scored, key=lambda item: item[0])
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
    return {key: metrics[key] for key in [
        "episodes",
        "positive_successes",
        "cau_successes",
        "routed_successes",
        "delta_vs_positive",
        "delta_vs_cau",
        "gains_vs_positive",
        "losses_vs_positive",
        "opened_episodes",
    ]}


def make_row(
    *,
    selector_mode: str,
    heldout_split: str,
    spec: GateSpec,
    train_metrics: dict[str, int],
    test_metrics: dict[str, int],
) -> dict[str, object]:
    return {
        "selector_mode": selector_mode,
        "heldout_split": heldout_split,
        **spec_row(spec),
        **{f"train_{key}": value for key, value in metric_row(train_metrics).items()},
        **{f"test_{key}": value for key, value in metric_row(test_metrics).items()},
    }


def aggregate_rows(rows: list[dict[str, object]], mode: str) -> dict[str, int]:
    selected = [row for row in rows if row["selector_mode"] == mode and row["heldout_split"] != "pooled_resubstitution"]
    keys = [
        "test_episodes",
        "test_positive_successes",
        "test_cau_successes",
        "test_routed_successes",
        "test_delta_vs_positive",
        "test_delta_vs_cau",
        "test_gains_vs_positive",
        "test_losses_vs_positive",
        "test_opened_episodes",
    ]
    return {key: sum(int(row[key]) for row in selected) for key in keys}


def split_baseline_rows(rows: list[EpisodeRow]) -> list[dict[str, object]]:
    out = []
    for split in sorted({row.split for row in rows}):
        split_rows = [row for row in rows if row.split == split]
        positive = sum(row.positive_success for row in split_rows)
        cau = sum(row.cau_success for row in split_rows)
        oracle = sum(max(row.positive_success, row.cau_success) for row in split_rows)
        out.append(
            {
                "split": split,
                "episodes": len(split_rows),
                "positive_successes": positive,
                "cau_successes": cau,
                "oracle_switch_successes": oracle,
                "cau_delta_vs_positive": cau - positive,
                "oracle_delta_vs_positive": oracle - positive,
            }
        )
    return out


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def write_report(out_dir: Path, selector_rows: list[dict[str, object]], baseline_rows: list[dict[str, object]]) -> None:
    report_path = out_dir / "CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md"
    safe = aggregate_rows(selector_rows, "safe_zero_loss")
    best = aggregate_rows(selector_rows, "best_delta")
    total_episodes = sum(int(row["episodes"]) for row in baseline_rows)
    total_positive = sum(int(row["positive_successes"]) for row in baseline_rows)
    total_cau = sum(int(row["cau_successes"]) for row in baseline_rows)
    total_oracle = sum(int(row["oracle_switch_successes"]) for row in baseline_rows)
    safe_score = f"{safe['test_routed_successes']}/{safe['test_episodes']}"
    best_score = f"{best['test_routed_successes']}/{best['test_episodes']}"
    lines = [
        "# CAU Selector Feature LOO Audit",
        "",
        "This development audit tests whether simple hidden-label-free initial support-distance features can select between positive-only and CAU across completed Can CAU splits.",
        "Thresholds are chosen from a coarse quantile grid to test robust signal rather than endpoint-specific threshold mining.",
        "",
        "## Decision",
        "",
        (
            f"- Baselines over the audited splits: positive-only `{total_positive}/{total_episodes}`, "
            f"always-CAU `{total_cau}/{total_episodes}`, and per-episode oracle switch `{total_oracle}/{total_episodes}`."
        ),
        (
            f"- Leave-one-split-out safe selector score: `{safe_score}` with "
            f"`{safe['test_gains_vs_positive']}` gains and `{safe['test_losses_vs_positive']}` losses versus positive-only."
        ),
        (
            f"- Leave-one-split-out best-delta selector score: `{best_score}` with "
            f"`{best['test_gains_vs_positive']}` gains and `{best['test_losses_vs_positive']}` losses versus positive-only."
        ),
    ]
    if safe["test_routed_successes"] <= total_positive:
        lines.append(
            "- The support-distance features do not provide a deployable CAU selector; preserving anchors collapses back to positive-only or fails to improve it."
        )
    elif safe["test_losses_vs_positive"] > 0:
        lines.append(
            "- The safe selector improves count but still loses positive-only starts on held-out splits, so it is not deployable under the current hard anchor-loss stop rule."
        )
    else:
        lines.append(
            "- The safe selector shows a possible deployable signal, but this is still endpoint-outcome-selected development evidence and would need a fresh live rollout."
        )
    lines.extend(
        [
            "",
            "## Split Baselines",
            "",
            *markdown_table(
                baseline_rows,
                [
                    "split",
                    "episodes",
                    "positive_successes",
                    "cau_successes",
                    "oracle_switch_successes",
                    "cau_delta_vs_positive",
                    "oracle_delta_vs_positive",
                ],
            ),
            "",
            "## Leave-One-Split-Out Rows",
            "",
            *markdown_table(
                selector_rows,
                [
                    "selector_mode",
                    "heldout_split",
                    "gate_label",
                    "feature_1",
                    "direction_1",
                    "threshold_1",
                    "feature_2",
                    "direction_2",
                    "threshold_2",
                    "operator",
                    "test_routed_successes",
                    "test_positive_successes",
                    "test_cau_successes",
                    "test_gains_vs_positive",
                    "test_losses_vs_positive",
                    "test_opened_episodes",
                ],
            ),
            "",
            "## Artifacts",
            "",
            f"- Selector CSV: `{out_dir / 'cau_selector_feature_loo_rows.csv'}`.",
            f"- Split baseline CSV: `{out_dir / 'cau_selector_feature_split_baselines.csv'}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = load_rows()
    selector_rows: list[dict[str, object]] = []
    specs = candidate_specs(rows)
    for mode, label in [("safe", "safe_zero_loss"), ("best_delta", "best_delta")]:
        spec, train_metrics = select_gate(specs, rows, mode=mode)
        selector_rows.append(
            make_row(
                selector_mode=label,
                heldout_split="pooled_resubstitution",
                spec=spec,
                train_metrics=train_metrics,
                test_metrics=train_metrics,
            )
        )
        for heldout in sorted({row.split for row in rows}):
            train_rows = [row for row in rows if row.split != heldout]
            test_rows = [row for row in rows if row.split == heldout]
            heldout_specs = candidate_specs(train_rows)
            spec, train_metrics = select_gate(heldout_specs, train_rows, mode=mode)
            test_metrics = evaluate(spec, test_rows)
            selector_rows.append(
                make_row(
                    selector_mode=label,
                    heldout_split=str(heldout),
                    spec=spec,
                    train_metrics=train_metrics,
                    test_metrics=test_metrics,
                )
            )
    baseline_rows = split_baseline_rows(rows)
    selector_fieldnames = list(selector_rows[0])
    baseline_fieldnames = list(baseline_rows[0])
    write_csv(args.out_dir / "cau_selector_feature_loo_rows.csv", selector_rows, selector_fieldnames)
    write_csv(args.out_dir / "cau_selector_feature_split_baselines.csv", baseline_rows, baseline_fieldnames)
    write_report(args.out_dir, selector_rows, baseline_rows)
    print(f"wrote {args.out_dir / 'CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md'}")


if __name__ == "__main__":
    main()
