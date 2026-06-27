#!/usr/bin/env python3
"""LOO audit for CAU-vs-positive selectors based on policy distribution features.

This is a development diagnostic. It computes hidden-label-free first-state
features from the trained positive-only and CAU BC-RNN-GMM policies, then asks
whether simple threshold rules can select CAU without losing the positive-only
anchor on held-out Can splits. It reuses existing endpoint rollouts; it does not
run new policy evaluations.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
ROBOMIMIC_ROOT = ROOT / "external" / "robomimic"
for path in (ROOT, SCRIPT_DIR, ROBOMIMIC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import robomimic.utils.file_utils as FileUtils  # noqa: E402
from evaluate_robomimic_official_policy import obs_for_policy  # noqa: E402
from evaluate_robomimic_router_policy import (  # noqa: E402
    action_log_prob,
    build_scorer,
    choose_obs_keys,
    learned_step_distribution,
    score_action,
    top_mode_action_and_features,
)
from run_robomimic_can_rollout_smoke import (  # noqa: E402
    action_bounds,
    load_env_metadata,
    load_eval_initials,
    make_env,
    reset_env,
)


OUT_DIR = ROOT / "results" / "sota_candidate"
THRESHOLD_QUANTILES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
FEATURES = (
    "positive_top_prob",
    "positive_entropy",
    "positive_logit_gap",
    "positive_top_scale_mean",
    "positive_support_margin",
    "positive_support_pos_dist",
    "positive_support_neg_dist",
    "cau_top_prob",
    "cau_entropy",
    "cau_logit_gap",
    "cau_top_scale_mean",
    "cau_support_margin",
    "cau_support_pos_dist",
    "cau_support_neg_dist",
    "cau_minus_positive_top_prob",
    "cau_minus_positive_entropy",
    "cau_minus_positive_logit_gap",
    "cau_minus_positive_support_margin",
    "positive_cau_action_l2",
    "positive_logp_self",
    "positive_logp_under_cau",
    "positive_logp_margin_vs_cau",
    "cau_logp_self",
    "cau_logp_under_positive",
    "cau_logp_margin_vs_positive",
)
PAIR_FEATURES = (
    "cau_logp_margin_vs_positive",
    "cau_minus_positive_support_margin",
    "positive_logp_margin_vs_cau",
    "positive_cau_action_l2",
    "cau_support_margin",
    "positive_support_margin",
    "cau_minus_positive_logit_gap",
    "cau_top_scale_mean",
    "positive_top_prob",
)


@dataclass(frozen=True)
class SplitSpec:
    split: int
    split_path: Path
    positive_checkpoint: Path
    cau_checkpoint: Path
    positive_path: Path
    cau_path: Path
    eval_episodes: int
    positive_substr: str = "positive_only"
    cau_substr: str = "cau_action_conflict"


SPLITS = (
    SplitSpec(
        split=101,
        split_path=ROOT / "results/final_paper_v02/splits/can_paired_pos40_bad80_split101/split_indices.json",
        positive_checkpoint=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split101_positive_only_nn_policy0/train/can_paired_pos40_bad80_split101_positive_only_nn_policy0_official_bc_rnn/20260625090642/models/model_epoch_200.pth",
        cau_checkpoint=OUT_DIR / "cau_action_conflict_can101_b005_m05_e200_train/cau_action_conflict_can101_b005_m05_e200_seed0/20260626181515/models/model_epoch_200.pth",
        positive_path=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split101_positive_only_nn_policy0/eval/episode_metrics.csv",
        cau_path=OUT_DIR / "cau_action_conflict_can101_b005_m05_eval50/episode_metrics.csv",
        eval_episodes=50,
    ),
    SplitSpec(
        split=202,
        split_path=ROOT / "results/final_paper_v02/splits/can_paired_pos40_bad80_split202/split_indices.json",
        positive_checkpoint=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_positive_only_nn_policy0/train/can_paired_pos40_bad80_split202_positive_only_nn_policy0_official_bc_rnn/20260625093934/models/model_epoch_200.pth",
        cau_checkpoint=OUT_DIR / "cau_action_conflict_can202_b005_m05_e200_train/cau_action_conflict_can202_b005_m05_e200_seed0/20260626182949/models/model_epoch_200.pth",
        positive_path=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_positive_only_nn_policy0/eval/episode_metrics.csv",
        cau_path=OUT_DIR / "cau_action_conflict_can202_b005_m05_eval50/episode_metrics.csv",
        eval_episodes=50,
    ),
    SplitSpec(
        split=303,
        split_path=ROOT / "results/final_paper_v02/splits/can_paired_pos40_bad80_split303/split_indices.json",
        positive_checkpoint=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split303_positive_only_nn_policy0/train/can_paired_pos40_bad80_split303_positive_only_nn_policy0_official_bc_rnn/20260625100601/models/model_epoch_200.pth",
        cau_checkpoint=OUT_DIR / "cau_action_conflict_can303_b005_m05_e200_train/cau_action_conflict_can303_b005_m05_e200_seed0/20260626175322/models/model_epoch_200.pth",
        positive_path=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split303_positive_only_nn_policy0/eval/episode_metrics.csv",
        cau_path=OUT_DIR / "cau_action_conflict_can303_b005_m05_eval50/episode_metrics.csv",
        eval_episodes=50,
    ),
    SplitSpec(
        split=404,
        split_path=ROOT / "results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json",
        positive_checkpoint=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/20260625141435/models/model_epoch_200.pth",
        cau_checkpoint=OUT_DIR / "cau_action_conflict_can404_b005_m05_e200_train/cau_action_conflict_can404_b005_m05_e200_seed0/20260626131712/models/model_epoch_200.pth",
        positive_path=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/eval/episode_metrics.csv",
        cau_path=OUT_DIR / "cau_action_conflict_can404_b005_m05_eval50/episode_metrics.csv",
        eval_episodes=50,
    ),
    SplitSpec(
        split=505,
        split_path=ROOT / "results/final_paper_v02/splits/can_paired_pos40_bad80_split505/split_indices.json",
        positive_checkpoint=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_positive_only_nn_policy0/train/can_paired_pos40_bad80_split505_positive_only_nn_policy0_official_bc_rnn/20260625144918/models/model_epoch_200.pth",
        cau_checkpoint=OUT_DIR / "cau_action_conflict_can505_b005_m05_e200_train/cau_action_conflict_can505_b005_m05_e200_seed0/20260626172232/models/model_epoch_200.pth",
        positive_path=ROOT / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_positive_only_nn_policy0/eval/episode_metrics.csv",
        cau_path=OUT_DIR / "cau_action_conflict_can505_b005_m05_eval50/episode_metrics.csv",
        eval_episodes=50,
    ),
    SplitSpec(
        split=606,
        split_path=ROOT / "results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split606/split_indices.json",
        positive_checkpoint=ROOT / "results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split606_positive_only_nn_policy0/train/can_paired_pos40_bad80_split606_positive_only_nn_policy0_official_bc_rnn/20260626074013/models/model_epoch_200.pth",
        cau_checkpoint=OUT_DIR / "cau_action_conflict_can606_b005_m05_e200_train/cau_action_conflict_can606_b005_m05_e200_seed0/20260626193313/models/model_epoch_200.pth",
        positive_path=ROOT / "results/candidate_g_fresh_preflight/can606_positive_epoch200_eval20/episode_metrics.csv",
        cau_path=OUT_DIR / "cau_action_conflict_can606_b005_m05_eval20/episode_metrics.csv",
        eval_episodes=20,
    ),
    SplitSpec(
        split=707,
        split_path=ROOT / "results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split707/split_indices.json",
        positive_checkpoint=ROOT / "results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_positive_only_nn_policy0/train/can_paired_pos40_bad80_split707_positive_only_nn_policy0_official_bc_rnn/20260626051924/models/model_epoch_200.pth",
        cau_checkpoint=OUT_DIR / "cau_action_conflict_can707_b005_m05_e200_train/cau_action_conflict_can707_b005_m05_e200_seed0/20260626203825/models/model_epoch_200.pth",
        positive_path=OUT_DIR / "can707_positive_weighted_cau_eval50/episode_metrics.csv",
        cau_path=OUT_DIR / "can707_positive_weighted_cau_eval50/episode_metrics.csv",
        eval_episodes=50,
    ),
    SplitSpec(
        split=808,
        split_path=ROOT / "results/candidate_f_can_fresh_validation/splits/can_paired_pos40_bad80_split808/split_indices.json",
        positive_checkpoint=ROOT / "results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_positive_only_nn_policy0/train/can_paired_pos40_bad80_split808_positive_only_nn_policy0_official_bc_rnn/20260626081822/models/model_epoch_200.pth",
        cau_checkpoint=OUT_DIR / "cau_action_conflict_can808_b005_m05_e200_train/cau_action_conflict_can808_b005_m05_e200_seed0/20260626211232/models/model_epoch_200.pth",
        positive_path=ROOT / "results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_positive_only_nn_policy0/eval/episode_metrics.csv",
        cau_path=OUT_DIR / "cau_action_conflict_can808_b005_m05_eval50/episode_metrics.csv",
        eval_episodes=50,
    ),
)


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
    feature: str = ""
    direction: str = ""
    threshold: float = 0.0
    feature_2: str = ""
    direction_2: str = ""
    threshold_2: float = 0.0
    operator: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    return parser.parse_args()


def make_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if name == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("requested CUDA, but torch.cuda.is_available() is false")
    return torch.device(name)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float) -> float:
    return round(float(value), 6)


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


def load_policies(spec: SplitSpec, device: torch.device) -> tuple[dict[str, object], dict]:
    policies = {}
    first_ckpt_dict = None
    for name, checkpoint in {
        "positive": spec.positive_checkpoint,
        "cau": spec.cau_checkpoint,
    }.items():
        policy, ckpt_dict = FileUtils.policy_from_checkpoint(
            ckpt_path=str(checkpoint),
            device=device,
            verbose=False,
        )
        policies[name] = policy
        if first_ckpt_dict is None:
            first_ckpt_dict = ckpt_dict
    if first_ckpt_dict is None:
        raise AssertionError("no policies loaded")
    return policies, first_ckpt_dict


def policy_feature_rows_for_split(spec: SplitSpec, device: torch.device) -> list[dict[str, object]]:
    split = json.loads(spec.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    env_meta = load_env_metadata(hdf5_path)
    policies, first_ckpt_dict = load_policies(spec, device)

    class Args:
        obs_keys = "checkpoint"
        support_mode = "labeled"
        positive_anchor_diagnostics = None

    obs_keys = choose_obs_keys(Args, first_ckpt_dict)
    scorer = build_scorer(Args, split, hdf5_path, obs_keys)
    eval_initials = load_eval_initials(hdf5_path, split["valid_positive_ids"])
    positive = read_successes(
        spec.positive_path,
        substring=spec.positive_substr,
        eval_episodes=spec.eval_episodes,
    )
    cau = read_successes(
        spec.cau_path,
        substring=spec.cau_substr,
        eval_episodes=spec.eval_episodes,
    )
    if sorted(positive) != sorted(cau):
        raise AssertionError(f"split {spec.split}: positive and CAU episode keys differ")

    env = make_env(env_meta)
    low, high = action_bounds(env)
    rows: list[dict[str, object]] = []
    try:
        for episode in range(spec.eval_episodes):
            initial = eval_initials[episode % len(eval_initials)]
            key = (episode, initial.demo_id)
            if key not in positive:
                raise AssertionError(f"split {spec.split}: missing outcome for {key}")
            obs = reset_env(env, initial)
            policy_obs = obs_for_policy(obs, list(obs_keys))
            dists = {
                name: learned_step_distribution(policy, policy_obs)
                for name, policy in policies.items()
            }
            actions: dict[str, np.ndarray] = {}
            row: dict[str, object] = {
                "split": spec.split,
                "episode": episode,
                "initial_demo_id": initial.demo_id,
                "positive_success": positive[key],
                "cau_success": cau[key],
                "oracle_success": max(positive[key], cau[key]),
            }
            for name in ("positive", "cau"):
                action, features = top_mode_action_and_features(dists[name], low, high)
                actions[name] = action
                row[f"{name}_top_prob"] = fmt(features["top_prob"])
                row[f"{name}_entropy"] = fmt(features["entropy"])
                row[f"{name}_logit_gap"] = fmt(features["logit_gap"])
                row[f"{name}_top_scale_mean"] = fmt(features["top_scale_mean"])
                margin, pos_dist, neg_dist = score_action(
                    scorer=scorer,
                    obs=obs,
                    action=action,
                    chunk_size=2048,
                )
                row[f"{name}_support_margin"] = fmt(margin)
                row[f"{name}_support_pos_dist"] = fmt(pos_dist)
                row[f"{name}_support_neg_dist"] = fmt(neg_dist)

            row["positive_cau_action_l2"] = fmt(np.linalg.norm(actions["positive"] - actions["cau"]))
            row["positive_logp_self"] = fmt(action_log_prob(dists["positive"], actions["positive"]))
            row["positive_logp_under_cau"] = fmt(action_log_prob(dists["cau"], actions["positive"]))
            row["positive_logp_margin_vs_cau"] = fmt(
                float(row["positive_logp_self"]) - float(row["positive_logp_under_cau"])
            )
            row["cau_logp_self"] = fmt(action_log_prob(dists["cau"], actions["cau"]))
            row["cau_logp_under_positive"] = fmt(action_log_prob(dists["positive"], actions["cau"]))
            row["cau_logp_margin_vs_positive"] = fmt(
                float(row["cau_logp_self"]) - float(row["cau_logp_under_positive"])
            )
            row["cau_minus_positive_top_prob"] = fmt(float(row["cau_top_prob"]) - float(row["positive_top_prob"]))
            row["cau_minus_positive_entropy"] = fmt(float(row["cau_entropy"]) - float(row["positive_entropy"]))
            row["cau_minus_positive_logit_gap"] = fmt(float(row["cau_logit_gap"]) - float(row["positive_logit_gap"]))
            row["cau_minus_positive_support_margin"] = fmt(
                float(row["cau_support_margin"]) - float(row["positive_support_margin"])
            )
            rows.append(row)
    finally:
        if hasattr(env, "close"):
            env.close()
    return rows


def episode_rows_from_feature_rows(rows: list[dict[str, object]]) -> list[EpisodeRow]:
    out = []
    for row in rows:
        out.append(
            EpisodeRow(
                split=int(row["split"]),
                episode=int(row["episode"]),
                initial_demo_id=str(row["initial_demo_id"]),
                positive_success=int(row["positive_success"]),
                cau_success=int(row["cau_success"]),
                features={feature: float(row[feature]) for feature in FEATURES},
            )
        )
    return out


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
    first = predicate(spec.feature, spec.direction, spec.threshold)
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
    for idx, feature in enumerate(PAIR_FEATURES):
        for feature_2 in PAIR_FEATURES[idx + 1 :]:
            for threshold in thresholds(rows, feature):
                for threshold_2 in thresholds(rows, feature_2):
                    for direction in ("le", "gt"):
                        for direction_2 in ("le", "gt"):
                            for operator in ("and", "or"):
                                specs.append(
                                    GateSpec(
                                        "two_feature",
                                        feature,
                                        direction,
                                        threshold,
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
    key = train_score_safe if mode == "safe" else train_score_best_delta
    scored = [(key(metrics := evaluate(spec, rows)), spec, metrics) for spec in specs]
    _score, spec, metrics = max(scored, key=lambda item: item[0])
    return spec, metrics


def spec_row(spec: GateSpec) -> dict[str, object]:
    return {
        "gate_label": spec.label,
        "feature": spec.feature,
        "direction": spec.direction,
        "threshold": "" if spec.label in {"always_positive", "always_cau"} else f"{spec.threshold:.6f}",
        "feature_2": spec.feature_2,
        "direction_2": spec.direction_2,
        "threshold_2": "" if not spec.feature_2 else f"{spec.threshold_2:.6f}",
        "operator": spec.operator,
    }


def metric_row(metrics: dict[str, int]) -> dict[str, object]:
    keys = [
        "episodes",
        "positive_successes",
        "cau_successes",
        "routed_successes",
        "delta_vs_positive",
        "delta_vs_cau",
        "gains_vs_positive",
        "losses_vs_positive",
        "opened_episodes",
    ]
    return {key: metrics[key] for key in keys}


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


def write_report(
    out_dir: Path,
    selector_rows: list[dict[str, object]],
    baseline_rows: list[dict[str, object]],
) -> None:
    report_path = out_dir / "CAU_POLICY_FEATURE_SELECTOR_LOO_AUDIT_REPORT.md"
    safe = aggregate_rows(selector_rows, "safe_zero_loss")
    best = aggregate_rows(selector_rows, "best_delta")
    total_episodes = sum(int(row["episodes"]) for row in baseline_rows)
    total_positive = sum(int(row["positive_successes"]) for row in baseline_rows)
    total_cau = sum(int(row["cau_successes"]) for row in baseline_rows)
    total_oracle = sum(int(row["oracle_switch_successes"]) for row in baseline_rows)
    lines = [
        "# CAU Policy-Feature Selector LOO Audit",
        "",
        "This development audit tests first-state policy-distribution features for selecting between positive-only and CAU.",
        "Features include GMM confidence, entropy, action disagreement, cross-policy log-probability, and labeled support margins.",
        "Thresholds are selected from a coarse quantile grid using completed splits only, then evaluated leave-one-split-out.",
        "",
        "## Decision",
        "",
        (
            f"- Baselines over the audited splits: positive-only `{total_positive}/{total_episodes}`, "
            f"always-CAU `{total_cau}/{total_episodes}`, and per-episode oracle switch `{total_oracle}/{total_episodes}`."
        ),
        (
            f"- Leave-one-split-out safe selector score: `{safe['test_routed_successes']}/{safe['test_episodes']}` with "
            f"`{safe['test_gains_vs_positive']}` gains and `{safe['test_losses_vs_positive']}` losses versus positive-only."
        ),
        (
            f"- Leave-one-split-out best-delta selector score: `{best['test_routed_successes']}/{best['test_episodes']}` with "
            f"`{best['test_gains_vs_positive']}` gains and `{best['test_losses_vs_positive']}` losses versus positive-only."
        ),
    ]
    if safe["test_routed_successes"] > total_positive and safe["test_losses_vs_positive"] == 0:
        lines.append(
            "- This is a possible selector seed, but it is still endpoint-outcome-selected development evidence and needs a fresh live rollout before promotion."
        )
    elif best["test_routed_successes"] > total_positive:
        lines.append(
            "- Policy features expose some signal, but the useful rules still lose positive-only starts; do not deploy without a stricter anchor-preservation mechanism."
        )
    else:
        lines.append(
            "- These first-state policy features do not provide a deployable selector; the missing signal is not solved by simple one-feature policy confidence rules."
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
                    "feature",
                    "direction",
                    "threshold",
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
            f"- Feature CSV: `{out_dir / 'cau_policy_feature_rows.csv'}`.",
            f"- Selector CSV: `{out_dir / 'cau_policy_feature_selector_loo_rows.csv'}`.",
            f"- Split baseline CSV: `{out_dir / 'cau_policy_feature_split_baselines.csv'}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
    os.environ.setdefault("MUJOCO_GL", "egl")
    args = parse_args()
    device = make_device(args.device)
    feature_rows: list[dict[str, object]] = []
    for spec in SPLITS:
        feature_rows.extend(policy_feature_rows_for_split(spec, device))
    rows = episode_rows_from_feature_rows(feature_rows)
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
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "cau_policy_feature_rows.csv", feature_rows, list(feature_rows[0]))
    write_csv(args.out_dir / "cau_policy_feature_selector_loo_rows.csv", selector_rows, list(selector_rows[0]))
    write_csv(args.out_dir / "cau_policy_feature_split_baselines.csv", baseline_rows, list(baseline_rows[0]))
    write_report(args.out_dir, selector_rows, baseline_rows)
    print(f"wrote {args.out_dir / 'CAU_POLICY_FEATURE_SELECTOR_LOO_AUDIT_REPORT.md'}")


if __name__ == "__main__":
    main()
