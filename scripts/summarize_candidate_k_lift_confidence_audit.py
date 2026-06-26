#!/usr/bin/env python3
"""Audit Lift606 deployable policy-confidence features for Candidate K."""

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
    build_scorer,
    choose_obs_keys,
    score_action,
)
from run_robomimic_can_rollout_smoke import (  # noqa: E402
    action_bounds,
    load_env_metadata,
    load_eval_initials,
    make_env,
    reset_env,
)


OUT = ROOT / "results" / "candidate_g_fresh_preflight"
SPLIT_PATH = OUT / "splits" / "lift_mg_mg_sparse_split606" / "split_indices.json"


@dataclass(frozen=True)
class PolicySpec:
    method_id: str
    checkpoint: Path


POLICIES = (
    PolicySpec(
        "positive",
        OUT
        / "per_seed"
        / "lift_mg_mg_sparse_split606_positive_only_nn_policy0"
        / "train"
        / "lift_mg_mg_sparse_split606_positive_only_nn_policy0_official_bc_rnn"
        / "20260626054343"
        / "models"
        / "model_epoch_200.pth",
    ),
    PolicySpec(
        "triage",
        OUT
        / "per_seed"
        / "lift_mg_mg_sparse_split606_triage_bc_policy0"
        / "train"
        / "lift_mg_mg_sparse_split606_triage_bc_policy0_official_bc_rnn"
        / "20260626053731"
        / "models"
        / "model_epoch_200.pth",
    ),
    PolicySpec(
        "weighted",
        OUT
        / "per_seed"
        / "lift_mg_mg_sparse_split606_weighted_bc_policy0"
        / "train"
        / "lift_mg_mg_sparse_split606_weighted_bc_policy0_official_bc_rnn"
        / "20260626055327"
        / "models"
        / "model_epoch_200.pth",
    ),
)

OUTCOME_FILES = {
    "positive": OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv",
    "triage": OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv",
    "weighted": OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def outcomes_by_demo(path: Path, limit: int = 20) -> dict[str, int]:
    rows = read_csv(path)[:limit]
    return {row["initial_demo_id"]: int(float(row["success"])) for row in rows}


def fmt(value: float) -> float:
    return round(float(value), 6)


def get_first_step_distribution(policy, obs: dict[str, np.ndarray], obs_keys: tuple[str, ...]):
    """Return learned-scale first-step GMM distribution for a rollout policy."""
    rollout_obs = obs_for_policy(obs, list(obs_keys))
    tensor_obs = policy._prepare_observation(rollout_obs, batched_ob=False)
    algo = policy.policy
    algo.set_eval()
    algo.reset()
    batch_size = next(iter(tensor_obs.values())).shape[0]
    rnn_state = algo.nets["policy"].get_rnn_init_state(batch_size=batch_size, device=algo.device)
    net = algo.nets["policy"]
    old_low_noise_eval = getattr(net, "low_noise_eval", None)
    if old_low_noise_eval is not None:
        net.low_noise_eval = False
    try:
        with torch.no_grad():
            dist, _state = net.forward_train_step(tensor_obs, rnn_state=rnn_state)
    finally:
        if old_low_noise_eval is not None:
            net.low_noise_eval = old_low_noise_eval
    return dist


def dist_features(dist) -> tuple[np.ndarray, dict[str, float]]:
    probs = dist.mixture_distribution.probs.detach().cpu().numpy()[0]
    logits = dist.mixture_distribution.logits.detach().cpu().numpy()[0]
    loc = dist.component_distribution.base_dist.loc.detach().cpu().numpy()[0]
    scale = dist.component_distribution.base_dist.scale.detach().cpu().numpy()[0]
    top = int(np.argmax(probs))
    action = loc[top].astype(np.float32, copy=False)
    entropy = -float(np.sum(probs * np.log(probs + 1.0e-12)))
    return action, {
        "top_mode": top,
        "top_prob": float(probs[top]),
        "entropy": entropy,
        "logit_gap": float(np.max(logits) - np.partition(logits, -2)[-2]),
        "top_scale_mean": float(np.mean(scale[top])),
        "top_scale_max": float(np.max(scale[top])),
    }


def log_prob(dist, action: np.ndarray) -> float:
    action_t = torch.as_tensor(action, dtype=torch.float32, device=dist.mixture_distribution.logits.device).view(1, -1)
    with torch.no_grad():
        return float(dist.log_prob(action_t).detach().cpu().numpy()[0])


def threshold_candidates(values: list[float]) -> list[float]:
    unique = sorted(set(values))
    if not unique:
        return []
    mids = [(a + b) / 2.0 for a, b in zip(unique, unique[1:])]
    return [unique[0] - 1.0e-6, *mids, unique[-1] + 1.0e-6]


def scan_feature_thresholds(rows: list[dict[str, object]], feature_names: list[str]) -> list[dict[str, object]]:
    """Scan one-feature gates that keep positive or switch to triage."""
    out = []
    for feature in feature_names:
        values = [float(row[feature]) for row in rows]
        for threshold in threshold_candidates(values):
            for direction in ("gt", "lt"):
                successes = 0
                switches = 0
                for row in rows:
                    value = float(row[feature])
                    switch = value > threshold if direction == "gt" else value < threshold
                    switches += int(switch)
                    successes += int(row["triage_success"] if switch else row["positive_success"])
                out.append(
                    {
                        "feature": feature,
                        "direction": direction,
                        "threshold": fmt(threshold),
                        "successes": successes,
                        "episodes": len(rows),
                        "switches": switches,
                    }
                )
    out.sort(key=lambda row: (-int(row["successes"]), int(row["switches"]), row["feature"], row["direction"]))
    return out


def top_rows(rows: list[dict[str, object]], n: int = 12) -> list[dict[str, object]]:
    best = int(rows[0]["successes"])
    selected = [row for row in rows if int(row["successes"]) == best]
    return selected[:n]


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
    split = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    env_meta = load_env_metadata(hdf5_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    policies = {}
    first_ckpt_dict = None
    for spec in POLICIES:
        policy, ckpt_dict = FileUtils.policy_from_checkpoint(
            ckpt_path=str(spec.checkpoint),
            device=device,
            verbose=False,
        )
        policies[spec.method_id] = policy
        first_ckpt_dict = first_ckpt_dict or ckpt_dict

    class Args:
        obs_keys = "checkpoint"
        support_mode = "labeled"
        positive_anchor_diagnostics = None

    obs_keys = choose_obs_keys(Args, first_ckpt_dict)
    scorer = build_scorer(Args, split, hdf5_path, obs_keys)
    eval_initials = load_eval_initials(hdf5_path, split["valid_positive_ids"])[:20]
    outcomes = {name: outcomes_by_demo(path) for name, path in OUTCOME_FILES.items()}

    env = make_env(env_meta)
    low, high = action_bounds(env)
    rows: list[dict[str, object]] = []
    try:
        for initial in eval_initials:
            obs = reset_env(env, initial)
            dists = {
                name: get_first_step_distribution(policy, obs, obs_keys)
                for name, policy in policies.items()
            }
            actions = {}
            dist_features_by_policy = {}
            for name, dist in dists.items():
                action, features = dist_features(dist)
                actions[name] = np.clip(action, low, high)
                dist_features_by_policy[name] = features

            row: dict[str, object] = {"initial_demo_id": initial.demo_id}
            for name in ("positive", "triage", "weighted"):
                features = dist_features_by_policy[name]
                row[f"{name}_top_prob"] = fmt(features["top_prob"])
                row[f"{name}_entropy"] = fmt(features["entropy"])
                row[f"{name}_logit_gap"] = fmt(features["logit_gap"])
                row[f"{name}_top_scale_mean"] = fmt(features["top_scale_mean"])
                row[f"{name}_top_scale_max"] = fmt(features["top_scale_max"])
                margin, pos_dist, neg_dist = score_action(
                    scorer=scorer,
                    obs=obs,
                    action=actions[name],
                    chunk_size=2048,
                )
                row[f"{name}_support_margin"] = fmt(margin)
                row[f"{name}_support_pos_dist"] = fmt(pos_dist)
                row[f"{name}_support_neg_dist"] = fmt(neg_dist)

            for a, b in (("positive", "triage"), ("positive", "weighted"), ("triage", "weighted")):
                row[f"{a}_{b}_action_l2"] = fmt(np.linalg.norm(actions[a] - actions[b]))
                row[f"{a}_logp_under_{b}"] = fmt(log_prob(dists[b], actions[a]))
                row[f"{b}_logp_under_{a}"] = fmt(log_prob(dists[a], actions[b]))

            row["triage_minus_positive_top_prob"] = fmt(float(row["triage_top_prob"]) - float(row["positive_top_prob"]))
            row["triage_minus_positive_entropy"] = fmt(float(row["triage_entropy"]) - float(row["positive_entropy"]))
            row["triage_minus_positive_support_margin"] = fmt(
                float(row["triage_support_margin"]) - float(row["positive_support_margin"])
            )
            row["triage_minus_positive_logit_gap"] = fmt(float(row["triage_logit_gap"]) - float(row["positive_logit_gap"]))
            row["positive_success"] = outcomes["positive"][initial.demo_id]
            row["triage_success"] = outcomes["triage"][initial.demo_id]
            row["weighted_success"] = outcomes["weighted"][initial.demo_id]
            row["oracle_success"] = max(
                int(row["positive_success"]),
                int(row["triage_success"]),
                int(row["weighted_success"]),
            )
            rows.append(row)
    finally:
        if hasattr(env, "close"):
            env.close()

    feature_names = [
        "positive_top_prob",
        "positive_entropy",
        "positive_logit_gap",
        "positive_top_scale_mean",
        "positive_top_scale_max",
        "positive_support_margin",
        "positive_support_pos_dist",
        "triage_top_prob",
        "triage_entropy",
        "triage_logit_gap",
        "triage_support_margin",
        "triage_minus_positive_top_prob",
        "triage_minus_positive_entropy",
        "triage_minus_positive_support_margin",
        "triage_minus_positive_logit_gap",
        "positive_triage_action_l2",
        "positive_weighted_action_l2",
        "positive_logp_under_triage",
        "triage_logp_under_positive",
    ]
    threshold_rows = scan_feature_thresholds(rows, feature_names)
    best_threshold_rows = top_rows(threshold_rows)

    feature_csv = OUT / "candidate_k_lift_confidence_features.csv"
    threshold_csv = OUT / "candidate_k_lift_confidence_threshold_audit.csv"
    report_path = OUT / "candidate_k_lift_confidence_audit_REPORT.md"
    fieldnames = list(rows[0].keys())
    write_csv(feature_csv, rows, fieldnames)
    write_csv(
        threshold_csv,
        threshold_rows,
        ["feature", "direction", "threshold", "successes", "episodes", "switches"],
    )

    positive_total = sum(int(row["positive_success"]) for row in rows)
    triage_total = sum(int(row["triage_success"]) for row in rows)
    weighted_total = sum(int(row["weighted_success"]) for row in rows)
    oracle_total = sum(int(row["oracle_success"]) for row in rows)
    best_threshold_total = int(best_threshold_rows[0]["successes"])
    lines = [
        "# Candidate K Lift606 Confidence-Feature Audit",
        "",
        "Candidate K asks whether richer deployable first-step policy features can",
        "identify when Lift606 should leave the positive-only anchor for triage.",
        "This is an offline audit over existing first-20 rollouts, not a validated",
        "router result.",
        "",
        "## Outcome Ceiling",
        "",
        f"- Positive-only: `{positive_total}/20`.",
        f"- Triage: `{triage_total}/20`.",
        f"- Weighted: `{weighted_total}/20`.",
        f"- Non-deployable oracle over the three policies: `{oracle_total}/20`.",
        f"- Best one-feature positive-to-triage threshold in this audit: `{best_threshold_total}/20`.",
        "",
        "## Best One-Feature Gates",
        "",
        *table(best_threshold_rows, ["feature", "direction", "threshold", "successes", "episodes", "switches"]),
        "",
        "## Read",
        "",
    ]
    if best_threshold_total > positive_total:
        lines.extend(
            [
                "- Unlike nearest support-margin routing, at least one first-step",
                "  confidence feature beats positive-only in this exploratory audit.",
                "- This is post-hoc on 20 starts, so it is only a candidate generator.",
                "  The next step is a tiny live router evaluation with the simplest",
                "  winning feature and then a fresh split check if it survives.",
            ]
        )
    else:
        lines.extend(
            [
                "- No audited first-step confidence feature beats positive-only on these",
                "  20 starts.",
                "- Candidate B likely needs temporal features observed during rollout,",
                "  not a pure initial-state gate.",
            ]
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Feature CSV: `{feature_csv.relative_to(ROOT)}`.",
            f"- Threshold audit CSV: `{threshold_csv.relative_to(ROOT)}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
