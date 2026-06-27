#!/usr/bin/env python3
"""No-rollout learned-router audit for CAU-vs-positive policy features.

The threshold audits found useful policy-distribution features but weak
transfer. This script tests one slightly stronger, still interpretable class of
routers: standardized ridge scores trained to predict CAU-vs-positive endpoint
delta from first-state policy features, followed by a train-selected threshold.
It reuses existing endpoint rollouts and computes split909 first-state features
only if the cached rows are missing.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from summarize_sota_cau_policy_feature_selector_audit import (
    FEATURES,
    PAIR_FEATURES,
    OUT_DIR,
    ROOT,
    EpisodeRow,
    SplitSpec,
    candidate_specs,
    episode_rows_from_feature_rows,
    evaluate as evaluate_threshold_gate,
    make_device,
    policy_feature_rows_for_split,
    read_csv,
    select_gate as select_threshold_gate,
    write_csv,
)


DEV_FEATURE_ROWS = OUT_DIR / "cau_policy_feature_rows.csv"
FRESH909_FEATURE_ROWS = OUT_DIR / "cau_policy_feature_fresh909_rows.csv"
REPORT_PATH = OUT_DIR / "CAU_POLICY_FEATURE_LEARNED_ROUTER_AUDIT_REPORT.md"
SUMMARY_PATH = OUT_DIR / "cau_policy_feature_learned_router_summary.csv"

FRESH909 = SplitSpec(
    split=909,
    split_path=ROOT
    / "results"
    / "candidate_f_can_fresh_validation"
    / "splits"
    / "can_paired_pos40_bad80_split909"
    / "split_indices.json",
    positive_checkpoint=ROOT
    / "results"
    / "candidate_f_can_fresh_validation"
    / "per_seed"
    / "can_paired_pos40_bad80_split909_positive_only_nn_policy0"
    / "train"
    / "can_paired_pos40_bad80_split909_positive_only_nn_policy0_official_bc_rnn"
    / "20260626085846"
    / "models"
    / "model_epoch_200.pth",
    cau_checkpoint=OUT_DIR
    / "cau_action_conflict_can909_b005_m05_e200_train"
    / "cau_action_conflict_can909_b005_m05_e200_seed0"
    / "20260626220319"
    / "models"
    / "model_epoch_200.pth",
    positive_path=ROOT
    / "results"
    / "candidate_f_can_fresh_validation"
    / "per_seed"
    / "can_paired_pos40_bad80_split909_positive_only_nn_policy0"
    / "eval"
    / "episode_metrics.csv",
    cau_path=OUT_DIR
    / "cau_action_conflict_can909_b005_m05_eval20"
    / "episode_metrics.csv",
    eval_episodes=20,
)

FEATURE_GROUPS = {
    "policy_core": tuple(PAIR_FEATURES),
    "policy_only": tuple(
        feature
        for feature in FEATURES
        if "support" not in feature and "pos_dist" not in feature and "neg_dist" not in feature
    ),
    "all_policy_features": tuple(FEATURES),
}
ALPHAS = (0.01, 0.1, 1.0, 10.0, 100.0)
TARGETS = ("delta", "loss_averse")


@dataclass(frozen=True)
class RidgeGate:
    mode: str
    feature_group: str
    target: str
    alpha: float
    threshold: float
    mean: tuple[float, ...]
    scale: tuple[float, ...]
    coef: tuple[float, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cpu")
    parser.add_argument("--refresh-fresh909-features", action="store_true")
    return parser.parse_args()


def feature_fieldnames() -> list[str]:
    return [
        "split",
        "episode",
        "initial_demo_id",
        "positive_success",
        "cau_success",
        "oracle_success",
        *FEATURES,
    ]


def load_fresh909_rows(device_name: str, refresh: bool) -> list[EpisodeRow]:
    if refresh or not FRESH909_FEATURE_ROWS.exists():
        device = make_device(device_name)
        rows = policy_feature_rows_for_split(FRESH909, device)
        write_csv(FRESH909_FEATURE_ROWS, rows, feature_fieldnames())
    return episode_rows_from_feature_rows(read_csv(FRESH909_FEATURE_ROWS))


def target_value(row: EpisodeRow, target: str) -> float:
    delta = row.cau_success - row.positive_success
    if target == "delta":
        return float(delta)
    if target == "loss_averse":
        if delta > 0:
            return 1.0
        if delta < 0:
            return -3.0
        return 0.0
    raise AssertionError(target)


def design(rows: list[EpisodeRow], features: tuple[str, ...]) -> np.ndarray:
    return np.asarray([[row.features[feature] for feature in features] for row in rows], dtype=np.float64)


def fit_ridge(
    rows: list[EpisodeRow],
    *,
    feature_group: str,
    target: str,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features = FEATURE_GROUPS[feature_group]
    x = design(rows, features)
    mean = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale < 1e-8] = 1.0
    x_std = (x - mean) / scale
    x_aug = np.concatenate([np.ones((x_std.shape[0], 1)), x_std], axis=1)
    y = np.asarray([target_value(row, target) for row in rows], dtype=np.float64)
    penalty = np.eye(x_aug.shape[1], dtype=np.float64) * alpha
    penalty[0, 0] = 0.0
    coef = np.linalg.solve(x_aug.T @ x_aug + penalty, x_aug.T @ y)
    return mean, scale, coef


def score_rows(rows: list[EpisodeRow], gate: RidgeGate) -> np.ndarray:
    features = FEATURE_GROUPS[gate.feature_group]
    x = design(rows, features)
    mean = np.asarray(gate.mean, dtype=np.float64)
    scale = np.asarray(gate.scale, dtype=np.float64)
    coef = np.asarray(gate.coef, dtype=np.float64)
    x_std = (x - mean) / scale
    x_aug = np.concatenate([np.ones((x_std.shape[0], 1)), x_std], axis=1)
    return x_aug @ coef


def threshold_candidates(scores: np.ndarray) -> list[float]:
    unique = sorted(set(float(score) for score in scores))
    if not unique:
        return [0.0]
    candidates = [unique[-1] + 1e-6, unique[0] - 1e-6]
    for quantile in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        candidates.append(float(np.quantile(scores, quantile)))
    return sorted(set(candidates))


def evaluate_gate(gate: RidgeGate, rows: list[EpisodeRow]) -> dict[str, int]:
    scores = score_rows(rows, gate)
    positive = sum(row.positive_success for row in rows)
    cau = sum(row.cau_success for row in rows)
    routed = 0
    gains = 0
    losses = 0
    opened = 0
    for row, score in zip(rows, scores, strict=True):
        open_here = bool(score > gate.threshold)
        opened += int(open_here)
        success = row.cau_success if open_here else row.positive_success
        routed += success
        gains += int(success == 1 and row.positive_success == 0)
        losses += int(success == 0 and row.positive_success == 1)
    return {
        "episodes": len(rows),
        "positive_successes": positive,
        "cau_successes": cau,
        "oracle_switch_successes": sum(max(row.positive_success, row.cau_success) for row in rows),
        "routed_successes": routed,
        "delta_vs_positive": routed - positive,
        "delta_vs_cau": routed - cau,
        "gains_vs_positive": gains,
        "losses_vs_positive": losses,
        "opened_episodes": opened,
    }


def train_score(metrics: dict[str, int], mode: str) -> tuple[int, ...]:
    if mode == "safe_zero_loss":
        return (
            int(metrics["losses_vs_positive"] == 0),
            int(metrics["delta_vs_positive"] > 0 and metrics["opened_episodes"] > 0),
            metrics["delta_vs_positive"],
            metrics["gains_vs_positive"],
            -metrics["opened_episodes"],
        )
    if mode == "best_delta":
        return (
            metrics["delta_vs_positive"],
            -metrics["losses_vs_positive"],
            metrics["gains_vs_positive"],
            -metrics["opened_episodes"],
        )
    raise AssertionError(mode)


def select_gate(rows: list[EpisodeRow], mode: str) -> tuple[RidgeGate, dict[str, int]]:
    best: tuple[tuple[int, ...], RidgeGate, dict[str, int]] | None = None
    for feature_group in FEATURE_GROUPS:
        for target in TARGETS:
            for alpha in ALPHAS:
                mean, scale, coef = fit_ridge(
                    rows,
                    feature_group=feature_group,
                    target=target,
                    alpha=alpha,
                )
                base_gate = RidgeGate(
                    mode=mode,
                    feature_group=feature_group,
                    target=target,
                    alpha=alpha,
                    threshold=0.0,
                    mean=tuple(float(v) for v in mean),
                    scale=tuple(float(v) for v in scale),
                    coef=tuple(float(v) for v in coef),
                )
                scores = score_rows(rows, base_gate)
                for threshold in threshold_candidates(scores):
                    gate = RidgeGate(
                        mode=mode,
                        feature_group=feature_group,
                        target=target,
                        alpha=alpha,
                        threshold=threshold,
                        mean=base_gate.mean,
                        scale=base_gate.scale,
                        coef=base_gate.coef,
                    )
                    metrics = evaluate_gate(gate, rows)
                    candidate = (train_score(metrics, mode), gate, metrics)
                    if best is None or candidate[0] > best[0]:
                        best = candidate
    if best is None:
        raise AssertionError("no candidate gate selected")
    return best[1], best[2]


def split_rows(rows: list[EpisodeRow], split: int) -> list[EpisodeRow]:
    return [row for row in rows if row.split == split]


def metrics_with_prefix(metrics: dict[str, int], prefix: str) -> dict[str, int]:
    return {f"{prefix}_{key}": value for key, value in metrics.items()}


def make_summary_row(
    *,
    selector_mode: str,
    heldout_split: str,
    gate: RidgeGate,
    train_metrics: dict[str, int],
    test_metrics: dict[str, int],
) -> dict[str, object]:
    return {
        "selector_mode": selector_mode,
        "heldout_split": heldout_split,
        "feature_group": gate.feature_group,
        "target": gate.target,
        "alpha": gate.alpha,
        "threshold": f"{gate.threshold:.6f}",
        **metrics_with_prefix(train_metrics, "train"),
        **metrics_with_prefix(test_metrics, "test"),
    }


def aggregate(rows: list[dict[str, object]], mode: str, prefix: str = "test") -> dict[str, int]:
    selected = [
        row
        for row in rows
        if row["selector_mode"] == mode and str(row["heldout_split"]).isdigit()
    ]
    keys = [
        f"{prefix}_episodes",
        f"{prefix}_positive_successes",
        f"{prefix}_cau_successes",
        f"{prefix}_oracle_switch_successes",
        f"{prefix}_routed_successes",
        f"{prefix}_gains_vs_positive",
        f"{prefix}_losses_vs_positive",
        f"{prefix}_opened_episodes",
    ]
    return {key: sum(int(row[key]) for row in selected) for key in keys}


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def deterministic_initial_oracle(rows: list[EpisodeRow]) -> dict[str, int]:
    grouped: dict[str, list[int]] = {}
    for row in rows:
        stats = grouped.setdefault(row.initial_demo_id, [0, 0, 0])
        stats[0] += row.positive_success
        stats[1] += row.cau_success
        stats[2] += 1
    return {
        "episodes": len(rows),
        "unique_initials": len(grouped),
        "positive_successes": sum(stats[0] for stats in grouped.values()),
        "cau_successes": sum(stats[1] for stats in grouped.values()),
        "deterministic_initial_oracle_successes": sum(
            max(stats[0], stats[1]) for stats in grouped.values()
        ),
        "episode_oracle_successes": sum(max(row.positive_success, row.cau_success) for row in rows),
    }


def same_screen_threshold_upper_bounds(rows: list[EpisodeRow]) -> dict[str, dict[str, object]]:
    specs = candidate_specs(rows)
    out: dict[str, dict[str, object]] = {}
    for mode, label in (("safe", "safe_zero_loss"), ("best_delta", "best_delta")):
        spec, _metrics = select_threshold_gate(specs, rows, mode=mode)
        metrics = evaluate_threshold_gate(spec, rows)
        out[label] = {
            "gate_label": spec.label,
            "feature": spec.feature,
            "direction": spec.direction,
            "threshold": f"{spec.threshold:.6f}",
            "feature_2": spec.feature_2,
            "direction_2": spec.direction_2,
            "threshold_2": "" if not spec.feature_2 else f"{spec.threshold_2:.6f}",
            "operator": spec.operator,
            **metrics,
        }
    return out


def write_report(summary_rows: list[dict[str, object]], fresh_rows_raw: list[EpisodeRow]) -> None:
    loo_rows = [row for row in summary_rows if str(row["heldout_split"]).isdigit()]
    fresh_summary_rows = [row for row in summary_rows if row["heldout_split"] == "fresh909"]
    safe = aggregate(loo_rows, "safe_zero_loss")
    best = aggregate(loo_rows, "best_delta")
    fresh_safe = next(row for row in fresh_summary_rows if row["selector_mode"] == "safe_zero_loss")
    fresh_best = next(row for row in fresh_summary_rows if row["selector_mode"] == "best_delta")
    initial_oracle = deterministic_initial_oracle(fresh_rows_raw)
    same_screen = same_screen_threshold_upper_bounds(fresh_rows_raw)
    same_safe = same_screen["safe_zero_loss"]
    same_best = same_screen["best_delta"]
    lines = [
        "# CAU Policy-Feature Learned Router Audit",
        "",
        "This no-rollout diagnostic fits standardized ridge scores from first-state policy features to CAU-vs-positive endpoint deltas.",
        "Thresholds are selected on training splits only. The audit tests leave-one-split-out transfer across completed splits and a frozen train-on-completed evaluation on fresh split909.",
        "",
        "## Decision",
        "",
        (
            f"- LOO safe learned router: `{safe['test_routed_successes']}/{safe['test_episodes']}` "
            f"with `{safe['test_gains_vs_positive']}` gains and `{safe['test_losses_vs_positive']}` losses "
            "versus positive-only."
        ),
        (
            f"- LOO best-delta learned router: `{best['test_routed_successes']}/{best['test_episodes']}` "
            f"with `{best['test_gains_vs_positive']}` gains and `{best['test_losses_vs_positive']}` losses "
            "versus positive-only."
        ),
        (
            f"- Fresh split909 safe learned router: `{fresh_safe['test_routed_successes']}/{fresh_safe['test_episodes']}` "
            f"versus positive-only `{fresh_safe['test_positive_successes']}/{fresh_safe['test_episodes']}` "
            f"and CAU `{fresh_safe['test_cau_successes']}/{fresh_safe['test_episodes']}`, opening "
            f"`{fresh_safe['test_opened_episodes']}` CAU starts."
        ),
        (
            f"- Fresh split909 best-delta learned router: `{fresh_best['test_routed_successes']}/{fresh_best['test_episodes']}` "
            f"versus positive-only `{fresh_best['test_positive_successes']}/{fresh_best['test_episodes']}` "
            f"and CAU `{fresh_best['test_cau_successes']}/{fresh_best['test_episodes']}`, opening "
            f"`{fresh_best['test_opened_episodes']}` CAU starts."
        ),
        (
            f"- Fresh split909 deterministic first-state oracle is only "
            f"`{initial_oracle['deterministic_initial_oracle_successes']}/{initial_oracle['episodes']}` "
            f"over `{initial_oracle['unique_initials']}` repeated initial states; the per-episode oracle is "
            f"`{initial_oracle['episode_oracle_successes']}/{initial_oracle['episodes']}`."
        ),
        (
            f"- A same-screen threshold upper bound can reach `{same_safe['routed_successes']}/{same_safe['episodes']}` "
            f"with `{same_safe['gains_vs_positive']}` gains and `{same_safe['losses_vs_positive']}` losses "
            f"using `{same_safe['feature']} {same_safe['direction']} {same_safe['threshold']}`; this is post-hoc "
            "and only shows that one recoverable start exists. The same-screen best-delta upper bound reaches "
            f"`{same_best['routed_successes']}/{same_best['episodes']}` with "
            f"`{same_best['gains_vs_positive']}` gains and `{same_best['losses_vs_positive']}` losses."
        ),
        "- Treat this as a diagnostic only unless both LOO and fresh transfer improve the positive-only anchor with controlled losses.",
        "",
        "## Rows",
        "",
        *markdown_table(
            summary_rows,
            [
                "selector_mode",
                "heldout_split",
                "feature_group",
                "target",
                "alpha",
                "threshold",
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
        f"- Summary CSV: `{SUMMARY_PATH}`.",
        f"- Fresh split909 feature rows: `{FRESH909_FEATURE_ROWS}`.",
        f"- Development feature rows: `{DEV_FEATURE_ROWS}`.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    dev_rows = episode_rows_from_feature_rows(read_csv(DEV_FEATURE_ROWS))
    fresh_rows = load_fresh909_rows(args.device, args.refresh_fresh909_features)
    summary_rows: list[dict[str, object]] = []

    splits = sorted({row.split for row in dev_rows})
    for mode in ("safe_zero_loss", "best_delta"):
        for split in splits:
            train = [row for row in dev_rows if row.split != split]
            test = split_rows(dev_rows, split)
            gate, train_metrics = select_gate(train, mode)
            test_metrics = evaluate_gate(gate, test)
            summary_rows.append(
                make_summary_row(
                    selector_mode=mode,
                    heldout_split=str(split),
                    gate=gate,
                    train_metrics=train_metrics,
                    test_metrics=test_metrics,
                )
            )
        gate, train_metrics = select_gate(dev_rows, mode)
        test_metrics = evaluate_gate(gate, fresh_rows)
        summary_rows.append(
            make_summary_row(
                selector_mode=mode,
                heldout_split="fresh909",
                gate=gate,
                train_metrics=train_metrics,
                test_metrics=test_metrics,
            )
        )

    fieldnames = [
        "selector_mode",
        "heldout_split",
        "feature_group",
        "target",
        "alpha",
        "threshold",
        "train_episodes",
        "train_positive_successes",
        "train_cau_successes",
        "train_oracle_switch_successes",
        "train_routed_successes",
        "train_delta_vs_positive",
        "train_delta_vs_cau",
        "train_gains_vs_positive",
        "train_losses_vs_positive",
        "train_opened_episodes",
        "test_episodes",
        "test_positive_successes",
        "test_cau_successes",
        "test_oracle_switch_successes",
        "test_routed_successes",
        "test_delta_vs_positive",
        "test_delta_vs_cau",
        "test_gains_vs_positive",
        "test_losses_vs_positive",
        "test_opened_episodes",
    ]
    write_csv(SUMMARY_PATH, summary_rows, fieldnames)
    write_report(summary_rows, fresh_rows)
    print(f"wrote {REPORT_PATH}")
    print(f"wrote {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
