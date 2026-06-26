#!/usr/bin/env python3
"""Summarize Candidate L split-calibrated confidence routing on Lift."""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

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


OUT = ROOT / "results" / "candidate_g_fresh_preflight"


@dataclass(frozen=True)
class SplitSpec:
    name: str
    split_path: Path
    positive_checkpoint: Path
    triage_checkpoint: Path
    positive_outcomes: Path
    triage_outcomes: Path
    calibrated_q25_dir: Path


SPLITS = (
    SplitSpec(
        name="lift606",
        split_path=OUT / "splits" / "lift_mg_mg_sparse_split606" / "split_indices.json",
        positive_checkpoint=OUT
        / "per_seed"
        / "lift_mg_mg_sparse_split606_positive_only_nn_policy0"
        / "train"
        / "lift_mg_mg_sparse_split606_positive_only_nn_policy0_official_bc_rnn"
        / "20260626054343"
        / "models"
        / "model_epoch_200.pth",
        triage_checkpoint=OUT
        / "per_seed"
        / "lift_mg_mg_sparse_split606_triage_bc_policy0"
        / "train"
        / "lift_mg_mg_sparse_split606_triage_bc_policy0_official_bc_rnn"
        / "20260626053731"
        / "models"
        / "model_epoch_200.pth",
        positive_outcomes=OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv",
        triage_outcomes=OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv",
        calibrated_q25_dir=OUT / "lift606_router_confidence_labeledpos_q25_eval20",
    ),
    SplitSpec(
        name="lift707",
        split_path=OUT / "splits" / "lift_mg_mg_sparse_split707" / "split_indices.json",
        positive_checkpoint=OUT
        / "per_seed"
        / "lift_mg_mg_sparse_split707_positive_only_nn_policy0"
        / "train"
        / "lift_mg_mg_sparse_split707_positive_only_nn_policy0_official_bc_rnn"
        / "20260626062239"
        / "models"
        / "model_epoch_200.pth",
        triage_checkpoint=OUT
        / "per_seed"
        / "lift_mg_mg_sparse_split707_triage_bc_policy0"
        / "train"
        / "lift_mg_mg_sparse_split707_triage_bc_policy0_official_bc_rnn"
        / "20260626062658"
        / "models"
        / "model_epoch_200.pth",
        positive_outcomes=OUT / "lift707_positive_epoch200_eval20" / "episode_metrics.csv",
        triage_outcomes=OUT / "lift707_triage_epoch200_eval20" / "episode_metrics.csv",
        calibrated_q25_dir=OUT / "lift707_router_confidence_labeledpos_q25_eval20",
    ),
)

FEATURE_NAMES = [
    "positive_top_prob",
    "positive_entropy",
    "positive_logit_gap",
    "positive_top_scale_mean",
    "positive_support_margin",
    "positive_support_pos_dist",
    "triage_top_prob",
    "triage_entropy",
    "triage_logit_gap",
    "triage_top_scale_mean",
    "triage_support_margin",
    "triage_minus_positive_top_prob",
    "triage_minus_positive_entropy",
    "triage_minus_positive_logit_gap",
    "triage_minus_positive_support_margin",
    "positive_triage_action_l2",
    "positive_logp_self",
    "positive_logp_under_triage",
    "positive_logp_margin_vs_triage",
    "triage_logp_self",
    "triage_logp_under_positive",
    "triage_logp_margin_vs_positive",
]


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


def outcomes_by_demo(path: Path, limit: int = 20) -> dict[str, int]:
    rows = read_csv(path)[:limit]
    return {row["initial_demo_id"]: int(float(row["success"])) for row in rows}


def metric_summary(path: Path) -> dict[str, object]:
    metrics = read_csv(path / "metrics.csv")[0]
    diagnostics = json.loads((path / "diagnostics.json").read_text(encoding="utf-8"))
    episodes = int(metrics["eval_episodes"])
    successes = int(round(float(metrics["success_rate"]) * episodes))
    return {
        "successes": successes,
        "episodes": episodes,
        "avg_len": float(metrics["avg_len"]),
        "choices_positive": int(metrics["choices_positive"]),
        "choices_triage": int(metrics["choices_triage"]),
        "effective_threshold": float(diagnostics["effective_initial_feature_threshold"]),
        "calibration_values": diagnostics["initial_feature_calibration_values"],
    }


def threshold_candidates(values: list[float]) -> list[float]:
    unique = sorted(set(values))
    if not unique:
        return []
    mids = [(left + right) / 2.0 for left, right in zip(unique, unique[1:])]
    return [unique[0] - 1.0e-6, *mids, unique[-1] + 1.0e-6]


def apply_gate(rows: list[dict[str, object]], feature: str, direction: str, threshold: float) -> dict[str, object]:
    successes = 0
    switches = 0
    switched_demos = []
    for row in rows:
        value = float(row[feature])
        switch = value > threshold if direction == "gt" else value < threshold
        switches += int(switch)
        if switch:
            switched_demos.append(row["initial_demo_id"])
        successes += int(row["triage_success"] if switch else row["positive_success"])
    return {
        "successes": successes,
        "episodes": len(rows),
        "switches": switches,
        "switched_demos": ",".join(str(demo_id) for demo_id in switched_demos),
    }


def scan_thresholds(rows: list[dict[str, object]], feature_names: list[str]) -> list[dict[str, object]]:
    out = []
    for feature in feature_names:
        values = [float(row[feature]) for row in rows]
        for threshold in threshold_candidates(values):
            for direction in ("gt", "lt"):
                result = apply_gate(rows, feature, direction, threshold)
                out.append(
                    {
                        "feature": feature,
                        "direction": direction,
                        "threshold": fmt(threshold),
                        **{key: result[key] for key in ("successes", "episodes", "switches")},
                    }
                )
    out.sort(key=lambda row: (-int(row["successes"]), int(row["switches"]), row["feature"], row["direction"]))
    return out


def policy_rows_for_split(spec: SplitSpec, device: torch.device) -> list[dict[str, object]]:
    split = json.loads(spec.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    env_meta = load_env_metadata(hdf5_path)
    policy_specs = {
        "positive": spec.positive_checkpoint,
        "triage": spec.triage_checkpoint,
    }
    policies = {}
    first_ckpt_dict = None
    for name, checkpoint in policy_specs.items():
        policy, ckpt_dict = FileUtils.policy_from_checkpoint(
            ckpt_path=str(checkpoint),
            device=device,
            verbose=False,
        )
        policies[name] = policy
        first_ckpt_dict = first_ckpt_dict or ckpt_dict

    class Args:
        obs_keys = "checkpoint"
        support_mode = "labeled"
        positive_anchor_diagnostics = None

    obs_keys = choose_obs_keys(Args, first_ckpt_dict)
    scorer = build_scorer(Args, split, hdf5_path, obs_keys)
    eval_initials = load_eval_initials(hdf5_path, split["valid_positive_ids"])[:20]
    outcomes = {
        "positive": outcomes_by_demo(spec.positive_outcomes),
        "triage": outcomes_by_demo(spec.triage_outcomes),
    }
    env = make_env(env_meta)
    low, high = action_bounds(env)
    rows: list[dict[str, object]] = []
    try:
        for episode, initial in enumerate(eval_initials):
            obs = reset_env(env, initial)
            policy_obs = obs_for_policy(obs, list(obs_keys))
            dists = {
                name: learned_step_distribution(policy, policy_obs)
                for name, policy in policies.items()
            }
            actions = {}
            features_by_policy = {}
            for name, dist in dists.items():
                action, features = top_mode_action_and_features(dist, low, high)
                actions[name] = action
                features_by_policy[name] = features

            row: dict[str, object] = {
                "split": spec.name,
                "episode": episode,
                "initial_demo_id": initial.demo_id,
            }
            for name in ("positive", "triage"):
                features = features_by_policy[name]
                row[f"{name}_top_prob"] = fmt(features["top_prob"])
                row[f"{name}_entropy"] = fmt(features["entropy"])
                row[f"{name}_logit_gap"] = fmt(features["logit_gap"])
                row[f"{name}_top_scale_mean"] = fmt(features["top_scale_mean"])
                margin, pos_dist, neg_dist = score_action(
                    scorer=scorer,
                    obs=obs,
                    action=actions[name],
                    chunk_size=2048,
                )
                row[f"{name}_support_margin"] = fmt(margin)
                row[f"{name}_support_pos_dist"] = fmt(pos_dist)
                row[f"{name}_support_neg_dist"] = fmt(neg_dist)

            row["positive_triage_action_l2"] = fmt(np.linalg.norm(actions["positive"] - actions["triage"]))
            row["positive_logp_self"] = fmt(action_log_prob(dists["positive"], actions["positive"]))
            row["positive_logp_under_triage"] = fmt(action_log_prob(dists["triage"], actions["positive"]))
            row["positive_logp_margin_vs_triage"] = fmt(
                float(row["positive_logp_self"]) - float(row["positive_logp_under_triage"])
            )
            row["triage_logp_self"] = fmt(action_log_prob(dists["triage"], actions["triage"]))
            row["triage_logp_under_positive"] = fmt(action_log_prob(dists["positive"], actions["triage"]))
            row["triage_logp_margin_vs_positive"] = fmt(
                float(row["triage_logp_self"]) - float(row["triage_logp_under_positive"])
            )
            row["triage_minus_positive_top_prob"] = fmt(float(row["triage_top_prob"]) - float(row["positive_top_prob"]))
            row["triage_minus_positive_entropy"] = fmt(float(row["triage_entropy"]) - float(row["positive_entropy"]))
            row["triage_minus_positive_logit_gap"] = fmt(float(row["triage_logit_gap"]) - float(row["positive_logit_gap"]))
            row["triage_minus_positive_support_margin"] = fmt(
                float(row["triage_support_margin"]) - float(row["positive_support_margin"])
            )
            row["positive_success"] = outcomes["positive"][initial.demo_id]
            row["triage_success"] = outcomes["triage"][initial.demo_id]
            row["oracle_success"] = max(int(row["positive_success"]), int(row["triage_success"]))
            rows.append(row)
    finally:
        if hasattr(env, "close"):
            env.close()
    return rows


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def main() -> None:
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
    os.environ.setdefault("MUJOCO_GL", "egl")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    rows_by_split = {spec.name: policy_rows_for_split(spec, device) for spec in SPLITS}
    all_rows = [row for rows in rows_by_split.values() for row in rows]
    dev_rows = rows_by_split["lift606"]
    fresh_rows = rows_by_split["lift707"]

    dev_scan = scan_thresholds(dev_rows, FEATURE_NAMES)
    fresh_scan = scan_thresholds(fresh_rows, FEATURE_NAMES)
    transfer_rows = []
    for row in dev_scan:
        fresh = apply_gate(fresh_rows, str(row["feature"]), str(row["direction"]), float(row["threshold"]))
        transfer_rows.append(
            {
                **row,
                "fresh_successes": fresh["successes"],
                "fresh_episodes": fresh["episodes"],
                "fresh_switches": fresh["switches"],
                "fresh_switched_demos": fresh["switched_demos"],
            }
        )

    feature_csv = OUT / "candidate_l_lift_cross_split_confidence_features.csv"
    transfer_csv = OUT / "candidate_l_lift606_to_707_threshold_transfer.csv"
    fresh_leaky_csv = OUT / "candidate_l_lift707_fresh_leaky_threshold_audit.csv"
    report_path = OUT / "candidate_l_calibrated_confidence_router_REPORT.md"
    write_csv(feature_csv, all_rows, list(all_rows[0].keys()))
    write_csv(
        transfer_csv,
        transfer_rows,
        [
            "feature",
            "direction",
            "threshold",
            "successes",
            "episodes",
            "switches",
            "fresh_successes",
            "fresh_episodes",
            "fresh_switches",
            "fresh_switched_demos",
        ],
    )
    write_csv(
        fresh_leaky_csv,
        fresh_scan,
        ["feature", "direction", "threshold", "successes", "episodes", "switches"],
    )

    q25 = {spec.name: metric_summary(spec.calibrated_q25_dir) for spec in SPLITS}
    split_summary = {}
    for name, rows in rows_by_split.items():
        split_summary[name] = {
            "positive": sum(int(row["positive_success"]) for row in rows),
            "triage": sum(int(row["triage_success"]) for row in rows),
            "oracle": sum(int(row["oracle_success"]) for row in rows),
            "episodes": len(rows),
        }

    best_dev_success = int(transfer_rows[0]["successes"])
    dev_best_transfer_rows = [
        row for row in transfer_rows if int(row["successes"]) == best_dev_success
    ]
    top_transfer = transfer_rows[:10]
    top_fresh_leaky = fresh_scan[:10]
    best_dev_best_transfer_fresh = max(int(row["fresh_successes"]) for row in dev_best_transfer_rows)
    best_fresh_leaky = int(top_fresh_leaky[0]["successes"])
    positive_fresh = split_summary["lift707"]["positive"]

    status = "rejected"
    if q25["lift707"]["successes"] > positive_fresh and best_dev_best_transfer_fresh > positive_fresh:
        status = "needs confirmation"

    lines = [
        "# Candidate L Calibrated Confidence Router",
        "",
        f"**Status: {status}.** Candidate L calibrates the Candidate K first-step",
        "GMM confidence threshold from labeled split data instead of carrying one",
        "global threshold across Lift splits.",
        "",
        "## Live Calibrated q25 Router",
        "",
        "| split | positive | triage | calibrated q25 | effective threshold | choices positive | choices triage |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name in ("lift606", "lift707"):
        summary = split_summary[name]
        metric = q25[name]
        lines.append(
            f"| {name} | {summary['positive']}/{summary['episodes']} | "
            f"{summary['triage']}/{summary['episodes']} | "
            f"{metric['successes']}/{metric['episodes']} | "
            f"{metric['effective_threshold']:.6f} | "
            f"{metric['choices_positive']} | {metric['choices_triage']} |"
        )

    lines.extend(
        [
            "",
            "The calibrated q25 threshold preserves Candidate K's Lift606 screen",
            "result, but it still fails the fresh Lift707 transfer check.",
            "",
            "## Development Threshold Transfer",
            "",
            "Top one-feature thresholds selected on Lift606, then applied unchanged",
            "to Lift707 using existing positive/triage outcome traces:",
            "",
            *table(
                top_transfer,
                [
                    "feature",
                    "direction",
                    "threshold",
                    "successes",
                    "switches",
                    "fresh_successes",
                    "fresh_switches",
                ],
            ),
            "",
            "## Fresh-Split Upper Bound",
            "",
            "This table is leaky and diagnostic only. It asks whether any one-step",
            "feature could have beaten positive-only on Lift707 if tuned on the",
            "same starts:",
            "",
            *table(top_fresh_leaky, ["feature", "direction", "threshold", "successes", "episodes", "switches"]),
            "",
            "## Read",
            "",
        ]
    )
    if best_dev_best_transfer_fresh <= positive_fresh:
        lines.extend(
            [
                "- None of the best Lift606-selected one-feature thresholds beats",
                f"  positive-only on Lift707 (`{positive_fresh}/20`); the best reaches",
                f"  `{best_dev_best_transfer_fresh}/20`.",
                f"- The leaky Lift707 upper bound is `{best_fresh_leaky}/20`, only one",
                "  success above positive-only, so initial confidence routing is a weak",
                "  abstraction for this Lift setting.",
                "- Candidate L should not be scaled as a frozen method. The next high-value",
                "  direction is temporal gating or a candidate that changes the trained policy,",
                "  not another fixed initial threshold.",
            ]
        )
    else:
        lines.extend(
            [
                "- At least one development-selected feature transfers on the offline",
                "  trace audit. It still needs a live router check before promotion.",
                "- The q25 labeled-positive calibration alone is insufficient.",
            ]
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Feature CSV: `{feature_csv.relative_to(ROOT)}`.",
            f"- Transfer audit CSV: `{transfer_csv.relative_to(ROOT)}`.",
            f"- Fresh leaky audit CSV: `{fresh_leaky_csv.relative_to(ROOT)}`.",
            f"- Lift606 q25 live eval: `{SPLITS[0].calibrated_q25_dir.relative_to(ROOT)}/REPORT.md`.",
            f"- Lift707 q25 live eval: `{SPLITS[1].calibrated_q25_dir.relative_to(ROOT)}/REPORT.md`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
