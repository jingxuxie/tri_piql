#!/usr/bin/env python3
"""Summarize Candidate S labeled initial-risk router on Lift."""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import h5py
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
    obs_vector_from_demo,
    obs_vector_from_env,
    policy_obs_from_demo,
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
FEATURE_QUANTILES = (0.10, 0.25, 0.50)
PRIMARY_FEATURE_SET = "policy"
PRIMARY_QUANTILE = 0.25


@dataclass(frozen=True)
class SplitSpec:
    name: str
    split_path: Path
    positive_checkpoint: Path
    triage_checkpoint: Path
    positive_outcomes: Path
    triage_outcomes: Path


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
    ),
)

POLICY_FEATURE_NAMES = [
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


def union_fieldnames(rows: list[dict[str, object]], preferred: list[str]) -> list[str]:
    seen = set()
    fields = []
    for name in preferred:
        if any(name in row for row in rows):
            fields.append(name)
            seen.add(name)
    for row in rows:
        for name in row:
            if name not in seen:
                fields.append(name)
                seen.add(name)
    return fields


def fmt(value: float) -> float:
    return round(float(value), 6)


def outcomes_by_demo(path: Path, limit: int = 20) -> dict[str, int]:
    rows = read_csv(path)[:limit]
    return {row["initial_demo_id"]: int(float(row["success"])) for row in rows}


def sigmoid(x: np.ndarray) -> np.ndarray:
    return np.where(x >= 0, 1.0 / (1.0 + np.exp(-x)), np.exp(x) / (1.0 + np.exp(x)))


def fit_balanced_logistic(
    x: np.ndarray,
    y: np.ndarray,
    *,
    l2: float = 1.0,
    lr: float = 0.2,
    steps: int = 4000,
) -> dict[str, np.ndarray]:
    mean = x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True) + 1.0e-6
    xs = (x - mean) / std
    xb = np.concatenate([np.ones((xs.shape[0], 1), dtype=np.float64), xs], axis=1)
    y = y.astype(np.float64)
    pos_count = max(float(np.sum(y == 1.0)), 1.0)
    neg_count = max(float(np.sum(y == 0.0)), 1.0)
    weights = np.where(y == 1.0, 0.5 / pos_count, 0.5 / neg_count)
    weights = weights / np.sum(weights)
    coef = np.zeros(xb.shape[1], dtype=np.float64)
    penalty = np.ones_like(coef)
    penalty[0] = 0.0
    for _step in range(steps):
        pred = sigmoid(xb @ coef)
        grad = xb.T @ (weights * (pred - y)) + l2 * penalty * coef / xs.shape[0]
        coef -= lr * grad
    return {"mean": mean, "std": std, "coef": coef}


def predict_positive_probability(model: dict[str, np.ndarray], x: np.ndarray) -> np.ndarray:
    xs = (x - model["mean"]) / model["std"]
    xb = np.concatenate([np.ones((xs.shape[0], 1), dtype=np.float64), xs], axis=1)
    return sigmoid(xb @ model["coef"])


def feature_row(
    *,
    obs: dict[str, np.ndarray],
    raw_obs_vector: np.ndarray,
    policies: dict[str, object],
    scorer,
    obs_keys: tuple[str, ...],
    low: np.ndarray,
    high: np.ndarray,
) -> dict[str, float]:
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

    row: dict[str, float] = {}
    for i, value in enumerate(raw_obs_vector.astype(np.float32, copy=False)):
        row[f"obs_{i:02d}"] = float(value)
    for name in ("positive", "triage"):
        features = features_by_policy[name]
        row[f"{name}_top_prob"] = features["top_prob"]
        row[f"{name}_entropy"] = features["entropy"]
        row[f"{name}_logit_gap"] = features["logit_gap"]
        row[f"{name}_top_scale_mean"] = features["top_scale_mean"]
        margin, pos_dist, neg_dist = score_action(
            scorer=scorer,
            obs=obs,
            action=actions[name],
            chunk_size=2048,
        )
        row[f"{name}_support_margin"] = margin
        row[f"{name}_support_pos_dist"] = pos_dist
        row[f"{name}_support_neg_dist"] = neg_dist

    row["positive_triage_action_l2"] = float(np.linalg.norm(actions["positive"] - actions["triage"]))
    row["positive_logp_self"] = action_log_prob(dists["positive"], actions["positive"])
    row["positive_logp_under_triage"] = action_log_prob(dists["triage"], actions["positive"])
    row["positive_logp_margin_vs_triage"] = row["positive_logp_self"] - row["positive_logp_under_triage"]
    row["triage_logp_self"] = action_log_prob(dists["triage"], actions["triage"])
    row["triage_logp_under_positive"] = action_log_prob(dists["positive"], actions["triage"])
    row["triage_logp_margin_vs_positive"] = row["triage_logp_self"] - row["triage_logp_under_positive"]
    row["triage_minus_positive_top_prob"] = row["triage_top_prob"] - row["positive_top_prob"]
    row["triage_minus_positive_entropy"] = row["triage_entropy"] - row["positive_entropy"]
    row["triage_minus_positive_logit_gap"] = row["triage_logit_gap"] - row["positive_logit_gap"]
    row["triage_minus_positive_support_margin"] = row["triage_support_margin"] - row["positive_support_margin"]
    return {key: fmt(value) for key, value in row.items()}


def feature_matrix(rows: list[dict[str, object]], columns: list[str]) -> np.ndarray:
    return np.asarray([[float(row[column]) for column in columns] for row in rows], dtype=np.float64)


def rows_for_split(spec: SplitSpec, device: torch.device) -> dict[str, object]:
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
    env = make_env(env_meta)
    low, high = action_bounds(env)
    outcomes = {
        "positive": outcomes_by_demo(spec.positive_outcomes),
        "triage": outcomes_by_demo(spec.triage_outcomes),
    }
    train_rows: list[dict[str, object]] = []
    eval_rows: list[dict[str, object]] = []
    try:
        with h5py.File(hdf5_path, "r") as f:
            labeled_pairs = [
                *[(demo_id, 1) for demo_id in split["labeled_positive_ids"]],
                *[(demo_id, 0) for demo_id in split["labeled_negative_ids"]],
            ]
            for demo_id, label in labeled_pairs:
                group = f["data"][demo_id]
                obs = policy_obs_from_demo(group, 0, obs_keys)
                raw_obs = obs_vector_from_demo(group, obs_keys)[0]
                row: dict[str, object] = {
                    "split": spec.name,
                    "row_type": "labeled",
                    "demo_id": demo_id,
                    "label": label,
                }
                row.update(
                    feature_row(
                        obs=obs,
                        raw_obs_vector=raw_obs,
                        policies=policies,
                        scorer=scorer,
                        obs_keys=obs_keys,
                        low=low,
                        high=high,
                    )
                )
                train_rows.append(row)

        eval_initials = load_eval_initials(hdf5_path, split["valid_positive_ids"])[:20]
        for episode, initial in enumerate(eval_initials):
            obs = reset_env(env, initial)
            raw_obs = obs_vector_from_env(obs, obs_keys)
            row = {
                "split": spec.name,
                "row_type": "eval",
                "episode": episode,
                "demo_id": initial.demo_id,
                "positive_success": outcomes["positive"][initial.demo_id],
                "triage_success": outcomes["triage"][initial.demo_id],
                "oracle_success": max(outcomes["positive"][initial.demo_id], outcomes["triage"][initial.demo_id]),
            }
            row.update(
                feature_row(
                    obs=obs,
                    raw_obs_vector=raw_obs,
                    policies=policies,
                    scorer=scorer,
                    obs_keys=obs_keys,
                    low=low,
                    high=high,
                )
            )
            eval_rows.append(row)
    finally:
        if hasattr(env, "close"):
            env.close()

    obs_feature_names = sorted(key for key in train_rows[0] if key.startswith("obs_"))
    return {
        "split": spec.name,
        "train_rows": train_rows,
        "eval_rows": eval_rows,
        "feature_sets": {
            "policy": POLICY_FEATURE_NAMES,
            "obs": obs_feature_names,
            "obs_policy": [*obs_feature_names, *POLICY_FEATURE_NAMES],
        },
    }


def evaluate_gate(
    *,
    split_name: str,
    feature_set: str,
    quantile: float,
    columns: list[str],
    train_rows: list[dict[str, object]],
    eval_rows: list[dict[str, object]],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    x_train = feature_matrix(train_rows, columns)
    y_train = np.asarray([int(row["label"]) for row in train_rows], dtype=np.float64)
    model = fit_balanced_logistic(x_train, y_train)
    train_scores = predict_positive_probability(model, x_train)
    positive_train_scores = train_scores[y_train == 1.0]
    threshold = float(np.quantile(positive_train_scores, quantile))
    x_eval = feature_matrix(eval_rows, columns)
    eval_scores = predict_positive_probability(model, x_eval)

    per_initial = []
    successes = 0
    switches = 0
    for row, score in zip(eval_rows, eval_scores):
        switch = float(score) < threshold
        selected = "triage" if switch else "positive"
        success = int(row[f"{selected}_success"])
        successes += success
        switches += int(switch)
        per_initial.append(
            {
                "split": split_name,
                "feature_set": feature_set,
                "quantile": quantile,
                "threshold": fmt(threshold),
                "demo_id": row["demo_id"],
                "score": fmt(score),
                "selected_policy": selected,
                "success": success,
                "positive_success": row["positive_success"],
                "triage_success": row["triage_success"],
            }
        )
    summary = {
        "split": split_name,
        "feature_set": feature_set,
        "quantile": quantile,
        "threshold": fmt(threshold),
        "successes": successes,
        "episodes": len(eval_rows),
        "switches": switches,
        "positive": sum(int(row["positive_success"]) for row in eval_rows),
        "triage": sum(int(row["triage_success"]) for row in eval_rows),
        "oracle": sum(int(row["oracle_success"]) for row in eval_rows),
        "train_labeled_positive_mean_score": fmt(float(np.mean(positive_train_scores))),
        "train_labeled_negative_mean_score": fmt(float(np.mean(train_scores[y_train == 0.0]))),
    }
    return summary, per_initial


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

    split_payloads = [rows_for_split(spec, device) for spec in SPLITS]
    feature_rows = []
    summary_rows = []
    per_initial_rows = []
    for payload in split_payloads:
        train_rows = payload["train_rows"]
        eval_rows = payload["eval_rows"]
        feature_rows.extend(train_rows)
        feature_rows.extend(eval_rows)
        for feature_set, columns in payload["feature_sets"].items():
            for quantile in FEATURE_QUANTILES:
                summary, per_initial = evaluate_gate(
                    split_name=str(payload["split"]),
                    feature_set=feature_set,
                    quantile=quantile,
                    columns=columns,
                    train_rows=train_rows,
                    eval_rows=eval_rows,
                )
                summary_rows.append(summary)
                per_initial_rows.extend(per_initial)

    primary_rows = [
        row
        for row in summary_rows
        if row["feature_set"] == PRIMARY_FEATURE_SET and float(row["quantile"]) == PRIMARY_QUANTILE
    ]
    best_rows = sorted(
        summary_rows,
        key=lambda row: (row["split"], -int(row["successes"]), int(row["switches"]), row["feature_set"], row["quantile"]),
    )

    feature_csv = OUT / "candidate_s_labeled_initial_risk_features.csv"
    summary_csv = OUT / "candidate_s_labeled_initial_risk_summary.csv"
    per_initial_csv = OUT / "candidate_s_labeled_initial_risk_per_initial.csv"
    report_path = OUT / "candidate_s_labeled_initial_risk_router_REPORT.md"

    feature_fieldnames = union_fieldnames(
        feature_rows,
        [
            "split",
            "row_type",
            "episode",
            "demo_id",
            "label",
            "positive_success",
            "triage_success",
            "oracle_success",
        ],
    )
    write_csv(feature_csv, feature_rows, feature_fieldnames)
    write_csv(
        summary_csv,
        summary_rows,
        [
            "split",
            "feature_set",
            "quantile",
            "threshold",
            "successes",
            "episodes",
            "switches",
            "positive",
            "triage",
            "oracle",
            "train_labeled_positive_mean_score",
            "train_labeled_negative_mean_score",
        ],
    )
    write_csv(
        per_initial_csv,
        per_initial_rows,
        [
            "split",
            "feature_set",
            "quantile",
            "threshold",
            "demo_id",
            "score",
            "selected_policy",
            "success",
            "positive_success",
            "triage_success",
        ],
    )

    primary_lift606 = next(row for row in primary_rows if row["split"] == "lift606")
    primary_lift707 = next(row for row in primary_rows if row["split"] == "lift707")
    primary_clears_dev = int(primary_lift606["successes"]) > int(primary_lift606["positive"])
    primary_clears_fresh = int(primary_lift707["successes"]) > int(primary_lift707["positive"])
    status = "rejected"
    if primary_clears_dev and primary_clears_fresh:
        status = "candidate"
    elif primary_clears_dev:
        status = "dev-only positive"

    top_by_split = []
    for split_name in ("lift606", "lift707"):
        top_by_split.extend([row for row in best_rows if row["split"] == split_name][:6])

    display_primary = [
        {
            **row,
            "successes": f"{row['successes']}/{row['episodes']}",
            "positive": f"{row['positive']}/{row['episodes']}",
            "triage": f"{row['triage']}/{row['episodes']}",
            "oracle": f"{row['oracle']}/{row['episodes']}",
        }
        for row in primary_rows
    ]
    display_top = [
        {
            **row,
            "successes": f"{row['successes']}/{row['episodes']}",
        }
        for row in top_by_split
    ]
    lines = [
        "# Candidate S Labeled Initial-Risk Router",
        "",
        f"**Status: {status}.** Candidate S trains a small balanced logistic",
        "classifier from labeled positive versus labeled negative initial states,",
        "then keeps the positive-only policy unless the classifier score falls",
        "below a labeled-positive quantile.",
        "",
        "The primary recipe is policy-feature logistic q25. Other feature sets and",
        "quantiles are diagnostic only.",
        "",
        "## Primary q25 Policy-Feature Gate",
        "",
        *table(
            display_primary,
            ["split", "successes", "positive", "triage", "oracle", "switches", "threshold"],
        ),
        "",
        "## Diagnostic Ablation Rows",
        "",
        *table(
            display_top,
            ["split", "feature_set", "quantile", "successes", "switches", "threshold"],
        ),
        "",
        "## Read",
        "",
    ]
    if status == "rejected":
        lines.extend(
            [
                "- Candidate S does not clear the development gate. The primary q25",
                f"  policy-feature gate reaches `{primary_lift606['successes']}/20` on",
                f"  Lift606 versus positive-only `{primary_lift606['positive']}/20`.",
                "- This means a labeled positive/negative initial classifier is not a",
                "  sufficient branch-quality proxy for the current Lift policy pair.",
                "- Do not spend live endpoint budget on this learned initial-risk gate.",
            ]
        )
    elif status == "dev-only positive":
        lines.extend(
            [
                "- Candidate S clears Lift606 but not the fresh Lift707 check under the",
                "  same recipe. It should not be promoted without a better transfer",
                "  story.",
                "- A live router run is optional only if we want to verify exact RNG",
                "  equivalence; the assembled outcome trace is enough for rejection.",
            ]
        )
    else:
        lines.extend(
            [
                "- Candidate S clears both the Lift606 development gate and the Lift707",
                "  fresh recipe check. The next step should be a live router eval with",
                "  the same classifier-gate rule before promoting it.",
            ]
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Feature CSV: `{feature_csv.relative_to(ROOT)}`.",
            f"- Summary CSV: `{summary_csv.relative_to(ROOT)}`.",
            f"- Per-initial CSV: `{per_initial_csv.relative_to(ROOT)}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
