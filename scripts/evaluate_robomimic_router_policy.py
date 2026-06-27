from __future__ import annotations

import argparse
import copy
import csv
import json
import os
import random
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
import robomimic.utils.torch_utils as TorchUtils  # noqa: E402
from run_robomimic_can_rollout_smoke import (  # noqa: E402
    action_bounds,
    env_success,
    load_env_metadata,
    load_eval_initials,
    make_env,
    reset_env,
)
from evaluate_robomimic_official_policy import obs_for_policy  # noqa: E402


STANDARD_LOW_DIM_OBS = [
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "object",
]


@dataclass(frozen=True)
class SupportScorer:
    obs_keys: tuple[str, ...]
    mean: np.ndarray
    std: np.ndarray
    positive: np.ndarray
    negative: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a hard router over trained Robomimic policies."
    )
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--policy",
        action="append",
        required=True,
        help="Policy spec as NAME=CHECKPOINT_PATH. The first policy is the default tie-breaker.",
    )
    parser.add_argument(
        "--policy-bias",
        action="append",
        default=[],
        help="Optional per-policy score bias as NAME=FLOAT. Useful to preserve a strong anchor.",
    )
    parser.add_argument("--eval-episodes", type=int, default=20)
    parser.add_argument("--eval-horizon", type=int, default=400)
    parser.add_argument(
        "--eval-init-mode",
        choices=["env_reset", "valid_positive_states", "valid_all_states"],
        default="valid_positive_states",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--obs-keys", choices=["checkpoint", "standard"], default="checkpoint")
    parser.add_argument(
        "--support-mode",
        choices=["labeled", "labeled_plus_positive_anchor"],
        default="labeled",
        help="State-action support used for action scoring.",
    )
    parser.add_argument(
        "--positive-anchor-diagnostics",
        type=Path,
        default=None,
        help=(
            "Diagnostics JSON containing selected_unlabeled_demos to add to positive "
            "support when --support-mode=labeled_plus_positive_anchor."
        ),
    )
    parser.add_argument(
        "--router-mode",
        choices=[
            "margin",
            "positive_anchor_margin",
            "positive_anchor_margin_persistent",
            "initial_anchor_pos_dist_force_alt",
            "initial_anchor_pos_dist_margin_force_alt",
            "initial_gmm_feature_force_alt",
            "initial_policy_feature_gate",
            "temporal_gmm_feature",
            "temporal_gmm_feature_persistent",
        ],
        default="positive_anchor_margin",
        help=(
            "margin picks max(score + bias). positive_anchor_margin only leaves the first policy "
            "when another policy beats it by --switch-threshold. initial_anchor_pos_dist_force_alt "
            "uses the first policy unless its initial action is farther than --initial-gate-threshold "
            "from positive support, then uses the second policy for the full episode. "
            "initial_anchor_pos_dist_margin_force_alt additionally requires the initial anchor "
            "support margin to exceed --initial-gate-margin-threshold before forcing the second policy. "
            "positive_anchor_margin_persistent uses the same support-margin gate as "
            "positive_anchor_margin, then commits to the alternate policy after "
            "--temporal-persistence-steps consecutive openings. "
            "initial_gmm_feature_force_alt gates on a first-step learned-scale GMM feature. "
            "initial_policy_feature_gate gates on a first-step policy agreement/support feature. "
            "temporal_gmm_feature recomputes that feature at every step and switches only for "
            "the current step. temporal_gmm_feature_persistent switches to the second policy "
            "for the rest of the episode after a run of low-confidence steps."
        ),
    )
    parser.add_argument("--switch-threshold", type=float, default=0.0)
    parser.add_argument("--initial-gate-threshold", type=float, default=3.0)
    parser.add_argument("--initial-gate-margin-threshold", type=float, default=0.0)
    parser.add_argument(
        "--initial-feature",
        choices=["anchor_logp_under_alt", "anchor_entropy", "anchor_top_prob"],
        default="anchor_logp_under_alt",
    )
    parser.add_argument("--initial-feature-threshold", type=float, default=0.0)
    parser.add_argument(
        "--initial-feature-threshold-source",
        choices=[
            "literal",
            "labeled_positive_quantile",
            "labeled_negative_quantile",
            "labeled_positive_sequence_quantile",
            "labeled_negative_sequence_quantile",
        ],
        default="literal",
        help=(
            "Use the literal threshold, or calibrate it as a quantile of the initial "
            "GMM feature over labeled positive / labeled negative starts. The sequence "
            "variants calibrate over all timesteps in labeled demonstration sequences."
        ),
    )
    parser.add_argument("--initial-feature-quantile", type=float, default=0.25)
    parser.add_argument(
        "--initial-feature-direction",
        choices=["gt", "lt"],
        default="lt",
        help="Open the initial GMM feature gate when feature is greater-than or less-than the threshold.",
    )
    parser.add_argument(
        "--initial-policy-feature",
        choices=[
            "anchor_top_prob",
            "anchor_entropy",
            "anchor_logit_gap",
            "anchor_top_scale_mean",
            "anchor_support_margin",
            "anchor_support_pos_dist",
            "anchor_support_neg_dist",
            "alt_top_prob",
            "alt_entropy",
            "alt_logit_gap",
            "alt_top_scale_mean",
            "alt_support_margin",
            "alt_support_pos_dist",
            "alt_support_neg_dist",
            "alt_minus_anchor_top_prob",
            "alt_minus_anchor_entropy",
            "alt_minus_anchor_logit_gap",
            "alt_minus_anchor_support_margin",
            "anchor_alt_action_l2",
            "anchor_logp_self",
            "anchor_logp_under_alt",
            "anchor_logp_margin_vs_alt",
            "alt_logp_self",
            "alt_logp_under_anchor",
            "alt_logp_margin_vs_anchor",
        ],
        default="alt_logp_margin_vs_anchor",
        help="First policy-feature gate feature. Anchor is the first --policy; alt is the second.",
    )
    parser.add_argument("--initial-policy-feature-threshold", type=float, default=0.0)
    parser.add_argument(
        "--initial-policy-feature-direction",
        choices=["gt", "lt"],
        default="gt",
    )
    parser.add_argument(
        "--initial-policy-feature-2",
        choices=[
            "",
            "anchor_top_prob",
            "anchor_entropy",
            "anchor_logit_gap",
            "anchor_top_scale_mean",
            "anchor_support_margin",
            "anchor_support_pos_dist",
            "anchor_support_neg_dist",
            "alt_top_prob",
            "alt_entropy",
            "alt_logit_gap",
            "alt_top_scale_mean",
            "alt_support_margin",
            "alt_support_pos_dist",
            "alt_support_neg_dist",
            "alt_minus_anchor_top_prob",
            "alt_minus_anchor_entropy",
            "alt_minus_anchor_logit_gap",
            "alt_minus_anchor_support_margin",
            "anchor_alt_action_l2",
            "anchor_logp_self",
            "anchor_logp_under_alt",
            "anchor_logp_margin_vs_alt",
            "alt_logp_self",
            "alt_logp_under_anchor",
            "alt_logp_margin_vs_anchor",
        ],
        default="",
        help="Optional second first-policy-feature gate feature.",
    )
    parser.add_argument("--initial-policy-feature-threshold-2", type=float, default=0.0)
    parser.add_argument(
        "--initial-policy-feature-direction-2",
        choices=["gt", "lt"],
        default="gt",
    )
    parser.add_argument(
        "--initial-policy-feature-operator",
        choices=["and", "or"],
        default="and",
    )
    parser.add_argument(
        "--temporal-persistence-steps",
        type=int,
        default=10,
        help="Consecutive temporal feature gate openings required before persistent switching.",
    )
    parser.add_argument(
        "--shared-policy-rng",
        action="store_true",
        help=(
            "Use one global RNG stream for all policy calls. By default each policy gets "
            "an isolated RNG stream so non-selected stochastic policies cannot perturb "
            "the selected policy's future samples."
        ),
    )
    parser.add_argument("--chunk-size", type=int, default=2048)
    parser.add_argument("--verbose-load", action="store_true")
    return parser.parse_args()


def parse_policy_specs(values: list[str]) -> list[tuple[str, Path]]:
    specs = []
    seen = set()
    for value in values:
        if "=" not in value:
            raise ValueError(f"policy spec must be NAME=PATH, got {value!r}")
        name, path = value.split("=", 1)
        name = name.strip()
        if not name:
            raise ValueError(f"empty policy name in {value!r}")
        if name in seen:
            raise ValueError(f"duplicate policy name {name!r}")
        seen.add(name)
        specs.append((name, Path(path)))
    return specs


def parse_biases(values: list[str]) -> dict[str, float]:
    biases = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"bias spec must be NAME=FLOAT, got {value!r}")
        name, raw = value.split("=", 1)
        biases[name.strip()] = float(raw)
    return biases


def make_device(name: str):
    if name == "auto":
        return TorchUtils.get_torch_device(try_to_use_cuda=True)
    if name == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("requested CUDA device, but torch.cuda.is_available() is false")
        return torch.device("cuda")
    return torch.device("cpu")


def capture_rng_state(device: torch.device) -> dict[str, object]:
    state: dict[str, object] = {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch_cpu": torch.random.get_rng_state().clone(),
    }
    if device.type == "cuda":
        state["torch_cuda"] = torch.cuda.get_rng_state(device).clone()
    else:
        state["torch_cuda"] = None
    return state


def clone_rng_state(state: dict[str, object]) -> dict[str, object]:
    numpy_state = state["numpy"]
    assert isinstance(numpy_state, tuple)
    cloned_numpy_state = (
        numpy_state[0],
        numpy_state[1].copy(),
        numpy_state[2],
        numpy_state[3],
        numpy_state[4],
    )
    cloned = {
        "python": copy.deepcopy(state["python"]),
        "numpy": cloned_numpy_state,
        "torch_cpu": state["torch_cpu"].clone(),
        "torch_cuda": None,
    }
    if state["torch_cuda"] is not None:
        cloned["torch_cuda"] = state["torch_cuda"].clone()
    return cloned


def restore_rng_state(state: dict[str, object], device: torch.device) -> None:
    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.random.set_rng_state(state["torch_cpu"])
    if device.type == "cuda" and state["torch_cuda"] is not None:
        torch.cuda.set_rng_state(state["torch_cuda"], device)


def call_policy_with_isolated_rng(
    *,
    policy,
    policy_obs: dict[str, np.ndarray],
    policy_rng_state: dict[str, object],
    device: torch.device,
) -> tuple[np.ndarray, dict[str, object]]:
    global_state = capture_rng_state(device)
    restore_rng_state(policy_rng_state, device)
    action = np.asarray(policy(policy_obs), dtype=np.float32)
    next_policy_state = capture_rng_state(device)
    restore_rng_state(global_state, device)
    return action, next_policy_state


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def obs_vector_from_demo(group, obs_keys: tuple[str, ...]) -> np.ndarray:
    obs_group = group["obs"]
    parts = [
        np.asarray(obs_group[key], dtype=np.float32).reshape((obs_group[key].shape[0], -1))
        for key in obs_keys
    ]
    return np.concatenate(parts, axis=1)


def obs_vector_from_env(obs: dict[str, np.ndarray], obs_keys: tuple[str, ...]) -> np.ndarray:
    parts = []
    for key in obs_keys:
        if key in obs:
            value = obs[key]
        elif key == "object" and "object-state" in obs:
            value = obs["object-state"]
        else:
            raise KeyError(f"observation key {key!r} missing; available keys: {sorted(obs)}")
        parts.append(np.asarray(value, dtype=np.float32).reshape(-1))
    return np.concatenate(parts, axis=0).astype(np.float32, copy=False)


def policy_obs_from_demo(group, t: int, obs_keys: tuple[str, ...]) -> dict[str, np.ndarray]:
    obs_group = group["obs"]
    out = {}
    for key in obs_keys:
        if key in obs_group:
            out[key] = np.asarray(obs_group[key][t])
        elif key == "object" and "object-state" in obs_group:
            out[key] = np.asarray(obs_group["object-state"][t])
        else:
            raise KeyError(f"observation key {key!r} missing from demo {group.name}")
    return out


def stack_state_action(hdf5_path: str, demo_ids: list[str], obs_keys: tuple[str, ...]) -> np.ndarray:
    rows = []
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted(demo_ids, key=demo_sort_key):
            group = f["data"][demo_id]
            obs = obs_vector_from_demo(group, obs_keys)
            actions = np.asarray(group["actions"], dtype=np.float32).reshape((obs.shape[0], -1))
            rows.append(np.concatenate([obs, actions], axis=1))
    if not rows:
        raise ValueError("empty support demo list")
    return np.concatenate(rows, axis=0).astype(np.float32, copy=False)


def choose_obs_keys(args: argparse.Namespace, ckpt_dict: dict) -> tuple[str, ...]:
    if args.obs_keys == "standard":
        return tuple(STANDARD_LOW_DIM_OBS)
    return tuple(ckpt_dict["shape_metadata"]["all_shapes"].keys())


def build_scorer(args: argparse.Namespace, split: dict, hdf5_path: str, obs_keys: tuple[str, ...]) -> SupportScorer:
    positive_ids = list(split["labeled_positive_ids"])
    negative_ids = list(split["labeled_negative_ids"])
    if args.support_mode == "labeled_plus_positive_anchor":
        # This adds the clean no-bad-label anchor selected by the positive-only NN baseline.
        diagnostics_path = args.positive_anchor_diagnostics or (
            ROOT
            / "results"
            / "final_paper_v02"
            / "per_seed"
            / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
            / "setup"
            / "diagnostics.json"
        )
        if diagnostics_path.exists():
            diagnostics = json.loads(diagnostics_path.read_text(encoding="utf-8"))
            positive_ids = list(dict.fromkeys([*positive_ids, *diagnostics["selected_unlabeled_demos"]]))
        elif args.positive_anchor_diagnostics is not None:
            raise FileNotFoundError(diagnostics_path)
    positive = stack_state_action(hdf5_path, positive_ids, obs_keys)
    negative = stack_state_action(hdf5_path, negative_ids, obs_keys)
    fit = np.concatenate([positive, negative], axis=0)
    mean = fit.mean(axis=0, keepdims=True).astype(np.float32)
    std = (fit.std(axis=0, keepdims=True) + 1.0e-6).astype(np.float32)
    return SupportScorer(
        obs_keys=obs_keys,
        mean=mean,
        std=std,
        positive=((positive - mean) / std).astype(np.float32),
        negative=((negative - mean) / std).astype(np.float32),
    )


def nearest_dist(query: np.ndarray, support: np.ndarray, chunk_size: int) -> float:
    q = query.reshape(1, -1).astype(np.float32, copy=False)
    best = np.inf
    for start in range(0, support.shape[0], chunk_size):
        block = support[start : start + chunk_size]
        diff = block - q
        dist = np.sqrt(np.sum(diff * diff, axis=1))
        block_best = float(np.min(dist))
        if block_best < best:
            best = block_best
    return best


def score_action(
    *,
    scorer: SupportScorer,
    obs: dict[str, np.ndarray],
    action: np.ndarray,
    chunk_size: int,
) -> tuple[float, float, float]:
    obs_vec = obs_vector_from_env(obs, scorer.obs_keys)
    feature = np.concatenate([obs_vec, np.asarray(action, dtype=np.float32).reshape(-1)], axis=0)
    feature = ((feature.reshape(1, -1) - scorer.mean) / scorer.std).reshape(-1).astype(np.float32, copy=False)
    pos_dist = nearest_dist(feature, scorer.positive, chunk_size)
    neg_dist = nearest_dist(feature, scorer.negative, chunk_size)
    margin = neg_dist - pos_dist
    return margin, pos_dist, neg_dist


def select_policy(
    *,
    scores: dict[str, float],
    policy_order: list[str],
    biases: dict[str, float],
    router_mode: str,
    switch_threshold: float,
) -> str:
    biased = {name: scores[name] + biases.get(name, 0.0) for name in policy_order}
    if router_mode == "margin":
        return max(policy_order, key=lambda name: (biased[name], -policy_order.index(name)))
    anchor = policy_order[0]
    best_alt = max(policy_order[1:], key=lambda name: (biased[name], -policy_order.index(name))) if len(policy_order) > 1 else anchor
    if biased[best_alt] > biased[anchor] + switch_threshold:
        return best_alt
    return anchor


def initial_anchor_pos_dist_gate(
    *,
    scorer: SupportScorer,
    obs: dict[str, np.ndarray],
    actions: dict[str, np.ndarray],
    policy_order: list[str],
    threshold: float,
    margin_threshold: float | None,
    chunk_size: int,
) -> tuple[bool, str, dict[str, float]]:
    if len(policy_order) < 2:
        raise ValueError("initial anchor force-alt routers require at least two policies")
    anchor = policy_order[0]
    alt = policy_order[1]
    margin, pos_dist, neg_dist = score_action(
        scorer=scorer,
        obs=obs,
        action=actions[anchor],
        chunk_size=chunk_size,
    )
    gate_open = pos_dist > threshold
    if margin_threshold is not None:
        gate_open = gate_open and margin > margin_threshold
    return gate_open, alt if gate_open else anchor, {
        "initial_anchor_margin": margin,
        "initial_anchor_pos_dist": pos_dist,
        "initial_anchor_neg_dist": neg_dist,
    }


def learned_step_distribution(policy, policy_obs: dict[str, np.ndarray]):
    tensor_obs = policy._prepare_observation(policy_obs, batched_ob=False)
    algo = policy.policy
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


def rollout_step_distribution(policy, policy_obs: dict[str, np.ndarray]):
    """Return a learned-scale GMM distribution at the policy's current rollout RNN state."""
    tensor_obs = policy._prepare_observation(policy_obs, batched_ob=False)
    algo = policy.policy
    batch_size = next(iter(tensor_obs.values())).shape[0]
    net = algo.nets["policy"]
    reset_rnn = algo._rnn_hidden_state is None or algo._rnn_counter % algo._rnn_horizon == 0
    if reset_rnn:
        rnn_state = net.get_rnn_init_state(batch_size=batch_size, device=algo.device)
        obs_to_use = tensor_obs
    else:
        rnn_state = algo._rnn_hidden_state
        obs_to_use = algo._open_loop_obs if getattr(algo, "_rnn_is_open_loop", False) else tensor_obs
    old_low_noise_eval = getattr(net, "low_noise_eval", None)
    if old_low_noise_eval is not None:
        net.low_noise_eval = False
    try:
        with torch.no_grad():
            dist, _state = net.forward_train_step(obs_to_use, rnn_state=rnn_state)
    finally:
        if old_low_noise_eval is not None:
            net.low_noise_eval = old_low_noise_eval
    return dist


def top_mode_action_and_features(dist, low: np.ndarray, high: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    probs = dist.mixture_distribution.probs.detach().cpu().numpy()[0]
    logits = dist.mixture_distribution.logits.detach().cpu().numpy()[0]
    loc = dist.component_distribution.base_dist.loc.detach().cpu().numpy()[0]
    scale = dist.component_distribution.base_dist.scale.detach().cpu().numpy()[0]
    top = int(np.argmax(probs))
    entropy = -float(np.sum(probs * np.log(probs + 1.0e-12)))
    action = np.clip(loc[top].astype(np.float32, copy=False), low, high)
    return action, {
        "top_prob": float(probs[top]),
        "entropy": entropy,
        "logit_gap": float(np.max(logits) - np.partition(logits, -2)[-2]),
        "top_scale_mean": float(np.mean(scale[top])),
    }


def action_log_prob(dist, action: np.ndarray) -> float:
    device = dist.mixture_distribution.logits.device
    action_t = torch.as_tensor(action, dtype=torch.float32, device=device).view(1, -1)
    with torch.no_grad():
        return float(dist.log_prob(action_t).detach().cpu().numpy()[0])


def initial_gmm_feature_value(
    *,
    policies: dict[str, object],
    policy_obs: dict[str, np.ndarray],
    policy_order: list[str],
    feature_name: str,
    low: np.ndarray,
    high: np.ndarray,
) -> float:
    if len(policy_order) < 2:
        raise ValueError("initial_gmm_feature_force_alt requires at least two policies")
    anchor = policy_order[0]
    alt = policy_order[1]
    anchor_dist = learned_step_distribution(policies[anchor], policy_obs)
    alt_dist = learned_step_distribution(policies[alt], policy_obs)
    anchor_action, anchor_features = top_mode_action_and_features(anchor_dist, low, high)
    if feature_name == "anchor_logp_under_alt":
        return action_log_prob(alt_dist, anchor_action)
    if feature_name == "anchor_entropy":
        return anchor_features["entropy"]
    if feature_name == "anchor_top_prob":
        return anchor_features["top_prob"]
    raise ValueError(feature_name)


def rollout_gmm_feature_value(
    *,
    policies: dict[str, object],
    policy_obs: dict[str, np.ndarray],
    policy_order: list[str],
    feature_name: str,
    low: np.ndarray,
    high: np.ndarray,
) -> float:
    if len(policy_order) < 2:
        raise ValueError("temporal GMM feature routing requires at least two policies")
    anchor = policy_order[0]
    alt = policy_order[1]
    anchor_dist = rollout_step_distribution(policies[anchor], policy_obs)
    alt_dist = rollout_step_distribution(policies[alt], policy_obs)
    anchor_action, anchor_features = top_mode_action_and_features(anchor_dist, low, high)
    if feature_name == "anchor_logp_under_alt":
        return action_log_prob(alt_dist, anchor_action)
    if feature_name == "anchor_entropy":
        return anchor_features["entropy"]
    if feature_name == "anchor_top_prob":
        return anchor_features["top_prob"]
    raise ValueError(feature_name)


def initial_gmm_feature_gate(
    *,
    policies: dict[str, object],
    policy_obs: dict[str, np.ndarray],
    policy_order: list[str],
    feature_name: str,
    threshold: float,
    direction: str,
    low: np.ndarray,
    high: np.ndarray,
) -> tuple[bool, str, dict[str, object]]:
    if len(policy_order) < 2:
        raise ValueError("initial_gmm_feature_force_alt requires at least two policies")
    anchor = policy_order[0]
    alt = policy_order[1]
    feature_value = initial_gmm_feature_value(
        policies=policies,
        policy_obs=policy_obs,
        policy_order=policy_order,
        feature_name=feature_name,
        low=low,
        high=high,
    )
    gate_open = feature_value > threshold if direction == "gt" else feature_value < threshold
    return gate_open, alt if gate_open else anchor, {
        "initial_feature_name": feature_name,
        "initial_feature_value": feature_value,
        "initial_feature_threshold": threshold,
        "initial_feature_direction": direction,
    }


def _passes_threshold(value: float, direction: str, threshold: float) -> bool:
    if direction == "gt":
        return value > threshold
    if direction == "lt":
        return value < threshold
    raise ValueError(direction)


def initial_policy_feature_values(
    *,
    policies: dict[str, object],
    policy_obs: dict[str, np.ndarray],
    policy_order: list[str],
    scorer: SupportScorer,
    obs: dict[str, np.ndarray],
    low: np.ndarray,
    high: np.ndarray,
    chunk_size: int,
) -> dict[str, float]:
    if len(policy_order) < 2:
        raise ValueError("initial_policy_feature_gate requires at least two policies")
    anchor = policy_order[0]
    alt = policy_order[1]
    anchor_dist = learned_step_distribution(policies[anchor], policy_obs)
    alt_dist = learned_step_distribution(policies[alt], policy_obs)
    anchor_action, anchor_features = top_mode_action_and_features(anchor_dist, low, high)
    alt_action, alt_features = top_mode_action_and_features(alt_dist, low, high)
    anchor_margin, anchor_pos_dist, anchor_neg_dist = score_action(
        scorer=scorer,
        obs=obs,
        action=anchor_action,
        chunk_size=chunk_size,
    )
    alt_margin, alt_pos_dist, alt_neg_dist = score_action(
        scorer=scorer,
        obs=obs,
        action=alt_action,
        chunk_size=chunk_size,
    )
    anchor_logp_self = action_log_prob(anchor_dist, anchor_action)
    anchor_logp_under_alt = action_log_prob(alt_dist, anchor_action)
    alt_logp_self = action_log_prob(alt_dist, alt_action)
    alt_logp_under_anchor = action_log_prob(anchor_dist, alt_action)
    return {
        "anchor_top_prob": anchor_features["top_prob"],
        "anchor_entropy": anchor_features["entropy"],
        "anchor_logit_gap": anchor_features["logit_gap"],
        "anchor_top_scale_mean": anchor_features["top_scale_mean"],
        "anchor_support_margin": anchor_margin,
        "anchor_support_pos_dist": anchor_pos_dist,
        "anchor_support_neg_dist": anchor_neg_dist,
        "alt_top_prob": alt_features["top_prob"],
        "alt_entropy": alt_features["entropy"],
        "alt_logit_gap": alt_features["logit_gap"],
        "alt_top_scale_mean": alt_features["top_scale_mean"],
        "alt_support_margin": alt_margin,
        "alt_support_pos_dist": alt_pos_dist,
        "alt_support_neg_dist": alt_neg_dist,
        "alt_minus_anchor_top_prob": alt_features["top_prob"] - anchor_features["top_prob"],
        "alt_minus_anchor_entropy": alt_features["entropy"] - anchor_features["entropy"],
        "alt_minus_anchor_logit_gap": alt_features["logit_gap"] - anchor_features["logit_gap"],
        "alt_minus_anchor_support_margin": alt_margin - anchor_margin,
        "anchor_alt_action_l2": float(np.linalg.norm(anchor_action - alt_action)),
        "anchor_logp_self": anchor_logp_self,
        "anchor_logp_under_alt": anchor_logp_under_alt,
        "anchor_logp_margin_vs_alt": anchor_logp_self - anchor_logp_under_alt,
        "alt_logp_self": alt_logp_self,
        "alt_logp_under_anchor": alt_logp_under_anchor,
        "alt_logp_margin_vs_anchor": alt_logp_self - alt_logp_under_anchor,
    }


def initial_policy_feature_gate(
    *,
    args: argparse.Namespace,
    policies: dict[str, object],
    policy_obs: dict[str, np.ndarray],
    policy_order: list[str],
    scorer: SupportScorer,
    obs: dict[str, np.ndarray],
    low: np.ndarray,
    high: np.ndarray,
    chunk_size: int,
) -> tuple[bool, str, dict[str, object]]:
    if len(policy_order) < 2:
        raise ValueError("initial_policy_feature_gate requires at least two policies")
    values = initial_policy_feature_values(
        policies=policies,
        policy_obs=policy_obs,
        policy_order=policy_order,
        scorer=scorer,
        obs=obs,
        low=low,
        high=high,
        chunk_size=chunk_size,
    )
    first_value = values[args.initial_policy_feature]
    first_open = _passes_threshold(
        first_value,
        args.initial_policy_feature_direction,
        args.initial_policy_feature_threshold,
    )
    second_value = ""
    if args.initial_policy_feature_2:
        second_value = values[args.initial_policy_feature_2]
        second_open = _passes_threshold(
            float(second_value),
            args.initial_policy_feature_direction_2,
            args.initial_policy_feature_threshold_2,
        )
        gate_open = first_open and second_open if args.initial_policy_feature_operator == "and" else first_open or second_open
    else:
        gate_open = first_open
    alt = policy_order[1]
    anchor = policy_order[0]
    return gate_open, alt if gate_open else anchor, {
        "initial_feature_name": args.initial_policy_feature,
        "initial_feature_value": first_value,
        "initial_feature_threshold": args.initial_policy_feature_threshold,
        "initial_feature_direction": args.initial_policy_feature_direction,
        "initial_feature_2_name": args.initial_policy_feature_2,
        "initial_feature_2_value": second_value,
        "initial_feature_2_threshold": (
            args.initial_policy_feature_threshold_2 if args.initial_policy_feature_2 else ""
        ),
        "initial_feature_2_direction": (
            args.initial_policy_feature_direction_2 if args.initial_policy_feature_2 else ""
        ),
        "initial_feature_operator": (
            args.initial_policy_feature_operator if args.initial_policy_feature_2 else ""
        ),
    }


def temporal_gmm_feature_gate(
    *,
    policies: dict[str, object],
    policy_obs: dict[str, np.ndarray],
    policy_order: list[str],
    feature_name: str,
    threshold: float,
    direction: str,
    low: np.ndarray,
    high: np.ndarray,
) -> tuple[bool, str, dict[str, object]]:
    if len(policy_order) < 2:
        raise ValueError("temporal_gmm_feature requires at least two policies")
    anchor = policy_order[0]
    alt = policy_order[1]
    feature_value = rollout_gmm_feature_value(
        policies=policies,
        policy_obs=policy_obs,
        policy_order=policy_order,
        feature_name=feature_name,
        low=low,
        high=high,
    )
    gate_open = feature_value > threshold if direction == "gt" else feature_value < threshold
    return gate_open, alt if gate_open else anchor, {
        "initial_feature_name": feature_name,
        "initial_feature_value": feature_value,
        "initial_feature_threshold": threshold,
        "initial_feature_direction": direction,
    }


def calibrate_initial_feature_threshold(
    *,
    args: argparse.Namespace,
    split: dict,
    hdf5_path: str,
    env,
    policies: dict[str, object],
    policy_order: list[str],
    obs_keys: tuple[str, ...],
    low: np.ndarray,
    high: np.ndarray,
) -> tuple[float, list[float], list[str]]:
    if args.initial_feature_threshold_source == "literal":
        return args.initial_feature_threshold, [], []
    if args.initial_feature_threshold_source in {"labeled_positive_quantile", "labeled_positive_sequence_quantile"}:
        calibration_ids = split["labeled_positive_ids"]
    elif args.initial_feature_threshold_source in {"labeled_negative_quantile", "labeled_negative_sequence_quantile"}:
        calibration_ids = split["labeled_negative_ids"]
    else:
        raise ValueError(args.initial_feature_threshold_source)
    if not 0.0 <= args.initial_feature_quantile <= 1.0:
        raise ValueError("--initial-feature-quantile must be in [0, 1]")
    values: list[float] = []
    if args.initial_feature_threshold_source.endswith("_sequence_quantile"):
        with h5py.File(hdf5_path, "r") as f:
            for demo_id in calibration_ids:
                for policy in policies.values():
                    policy.start_episode()
                group = f["data"][demo_id]
                horizon = int(group["actions"].shape[0])
                for t in range(horizon):
                    policy_obs = policy_obs_from_demo(group, t, obs_keys)
                    values.append(
                        rollout_gmm_feature_value(
                            policies=policies,
                            policy_obs=policy_obs,
                            policy_order=policy_order,
                            feature_name=args.initial_feature,
                            low=low,
                            high=high,
                        )
                    )
                    for policy in policies.values():
                        _ = policy(policy_obs)
    else:
        calibration_initials = load_eval_initials(hdf5_path, calibration_ids)
        for initial in calibration_initials:
            obs = reset_env(env, initial)
            policy_obs = obs_for_policy(obs, list(obs_keys))
            values.append(
                initial_gmm_feature_value(
                    policies=policies,
                    policy_obs=policy_obs,
                    policy_order=policy_order,
                    feature_name=args.initial_feature,
                    low=low,
                    high=high,
                )
            )
    threshold = float(np.quantile(np.asarray(values, dtype=np.float32), args.initial_feature_quantile))
    return threshold, values, calibration_ids


def checkpoint_table(rows: list[dict[str, object]]) -> str:
    header = "| router | success_rate | avg_return | avg_len | eval_episodes |"
    separator = "|---|---:|---:|---:|---:|"
    lines = [header, separator]
    for row in rows:
        lines.append(
            f"| {row['router_name']} | {float(row['success_rate']):.3f} | "
            f"{float(row['avg_return']):.3f} | {float(row['avg_len']):.1f} | "
            f"{int(row['eval_episodes'])} |"
        )
    return "\n".join(lines)


def main() -> None:
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
    os.environ.setdefault("MUJOCO_GL", "egl")
    args = parse_args()
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    env_meta = load_env_metadata(hdf5_path)
    policy_specs = parse_policy_specs(args.policy)
    policy_order = [name for name, _path in policy_specs]
    biases = parse_biases(args.policy_bias)
    device = make_device(args.device)

    policies = {}
    first_ckpt_dict = None
    for name, checkpoint in policy_specs:
        policy, ckpt_dict = FileUtils.policy_from_checkpoint(
            ckpt_path=str(checkpoint),
            device=device,
            verbose=args.verbose_load,
        )
        policies[name] = policy
        if first_ckpt_dict is None:
            first_ckpt_dict = ckpt_dict
    if first_ckpt_dict is None:
        raise ValueError("no policies loaded")
    obs_keys = choose_obs_keys(args, first_ckpt_dict)
    scorer = build_scorer(args, split, hdf5_path, obs_keys)

    if args.eval_init_mode == "valid_positive_states":
        eval_initial_ids = split["valid_positive_ids"]
    elif args.eval_init_mode == "valid_all_states":
        eval_initial_ids = split["valid_ids"]
    else:
        eval_initial_ids = []
    eval_initials = load_eval_initials(hdf5_path, eval_initial_ids) if eval_initial_ids else None

    env = make_env(env_meta)
    low, high = action_bounds(env)
    effective_initial_feature_threshold, calibration_values, calibration_ids = calibrate_initial_feature_threshold(
        args=args,
        split=split,
        hdf5_path=hdf5_path,
        env=env,
        policies=policies,
        policy_order=policy_order,
        obs_keys=obs_keys,
        low=low,
        high=high,
    )
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    base_policy_rng_state = capture_rng_state(device)
    policy_rng_states = {
        name: clone_rng_state(base_policy_rng_state)
        for name in policy_order
    }
    successes = []
    returns = []
    lengths = []
    episode_rows = []
    choice_counts = {name: 0 for name in policy_order}
    try:
        for episode in range(args.eval_episodes):
            np.random.seed(args.seed + episode)
            initial = eval_initials[episode % len(eval_initials)] if eval_initials else None
            obs = reset_env(env, initial)
            for policy in policies.values():
                policy.start_episode()
            total_return = 0.0
            success = False
            length = 0
            episode_choice_counts = {name: 0 for name in policy_order}
            episode_gate_open = False
            episode_forced_policy = ""
            initial_gate_features = {
                "initial_anchor_margin": "",
                "initial_anchor_pos_dist": "",
                "initial_anchor_neg_dist": "",
                "initial_feature_name": "",
                "initial_feature_value": "",
                "initial_feature_threshold": "",
                "initial_feature_direction": "",
                "initial_feature_2_name": "",
                "initial_feature_2_value": "",
                "initial_feature_2_threshold": "",
                "initial_feature_2_direction": "",
                "initial_feature_operator": "",
            }
            temporal_gate_open_count = 0
            temporal_feature_values: list[float] = []
            temporal_consecutive_open = 0
            temporal_persistent_policy = ""
            temporal_persistent_switch_step = ""
            for t in range(args.eval_horizon):
                policy_obs = obs_for_policy(obs, list(obs_keys))
                step_temporal_policy = ""
                if args.router_mode in {"temporal_gmm_feature", "temporal_gmm_feature_persistent"}:
                    temporal_gate_open, step_temporal_policy, step_features = temporal_gmm_feature_gate(
                        policies=policies,
                        policy_obs=policy_obs,
                        policy_order=policy_order,
                        feature_name=args.initial_feature,
                        threshold=effective_initial_feature_threshold,
                        direction=args.initial_feature_direction,
                        low=low,
                        high=high,
                    )
                    temporal_gate_open_count += int(temporal_gate_open)
                    temporal_feature_values.append(float(step_features["initial_feature_value"]))
                    if args.router_mode == "temporal_gmm_feature_persistent":
                        if temporal_gate_open:
                            temporal_consecutive_open += 1
                        else:
                            temporal_consecutive_open = 0
                        if (
                            not temporal_persistent_policy
                            and temporal_consecutive_open >= args.temporal_persistence_steps
                        ):
                            temporal_persistent_policy = step_temporal_policy
                            temporal_persistent_switch_step = t
                    if t == 0:
                        episode_gate_open = temporal_gate_open
                        episode_forced_policy = step_temporal_policy
                        initial_gate_features = step_features
                actions = {}
                for name, policy in policies.items():
                    if args.shared_policy_rng:
                        raw_action = np.asarray(policy(policy_obs), dtype=np.float32)
                    else:
                        raw_action, policy_rng_states[name] = call_policy_with_isolated_rng(
                            policy=policy,
                            policy_obs=policy_obs,
                            policy_rng_state=policy_rng_states[name],
                            device=device,
                        )
                    actions[name] = np.clip(raw_action, low, high)
                if t == 0 and args.router_mode in {
                    "initial_anchor_pos_dist_force_alt",
                    "initial_anchor_pos_dist_margin_force_alt",
                }:
                    episode_gate_open, episode_forced_policy, initial_gate_features = initial_anchor_pos_dist_gate(
                        scorer=scorer,
                        obs=obs,
                        actions=actions,
                        policy_order=policy_order,
                        threshold=args.initial_gate_threshold,
                        margin_threshold=(
                            args.initial_gate_margin_threshold
                            if args.router_mode == "initial_anchor_pos_dist_margin_force_alt"
                            else None
                        ),
                        chunk_size=args.chunk_size,
                    )
                if t == 0 and args.router_mode == "initial_gmm_feature_force_alt":
                    episode_gate_open, episode_forced_policy, initial_gate_features = initial_gmm_feature_gate(
                        policies=policies,
                        policy_obs=policy_obs,
                        policy_order=policy_order,
                        feature_name=args.initial_feature,
                        threshold=effective_initial_feature_threshold,
                        direction=args.initial_feature_direction,
                        low=low,
                        high=high,
                    )
                if t == 0 and args.router_mode == "initial_policy_feature_gate":
                    episode_gate_open, episode_forced_policy, initial_gate_features = initial_policy_feature_gate(
                        args=args,
                        policies=policies,
                        policy_obs=policy_obs,
                        policy_order=policy_order,
                        scorer=scorer,
                        obs=obs,
                        low=low,
                        high=high,
                        chunk_size=args.chunk_size,
                    )
                raw_scores = {}
                pos_dists = {}
                neg_dists = {}
                for name, action in actions.items():
                    margin, pos_dist, neg_dist = score_action(
                        scorer=scorer,
                        obs=obs,
                        action=action,
                        chunk_size=args.chunk_size,
                    )
                    raw_scores[name] = margin
                    pos_dists[name] = pos_dist
                    neg_dists[name] = neg_dist
                if args.router_mode == "positive_anchor_margin_persistent":
                    anchor = policy_order[0]
                    best_alt = (
                        max(
                            policy_order[1:],
                            key=lambda name: (
                                raw_scores[name] + biases.get(name, 0.0),
                                -policy_order.index(name),
                            ),
                        )
                        if len(policy_order) > 1
                        else anchor
                    )
                    anchor_score = raw_scores[anchor] + biases.get(anchor, 0.0)
                    alt_score = raw_scores[best_alt] + biases.get(best_alt, 0.0)
                    support_margin_gap = alt_score - anchor_score
                    temporal_gate_open = bool(support_margin_gap > args.switch_threshold)
                    step_temporal_policy = best_alt if temporal_gate_open else anchor
                    temporal_gate_open_count += int(temporal_gate_open)
                    temporal_feature_values.append(float(support_margin_gap))
                    if temporal_gate_open:
                        temporal_consecutive_open += 1
                    else:
                        temporal_consecutive_open = 0
                    if (
                        not temporal_persistent_policy
                        and temporal_consecutive_open >= args.temporal_persistence_steps
                    ):
                        temporal_persistent_policy = step_temporal_policy
                        temporal_persistent_switch_step = t
                    if t == 0:
                        episode_gate_open = temporal_gate_open
                        episode_forced_policy = step_temporal_policy
                        initial_gate_features = {
                            "initial_feature_name": "support_margin_gap",
                            "initial_feature_value": support_margin_gap,
                            "initial_feature_threshold": args.switch_threshold,
                            "initial_feature_direction": "gt",
                            "initial_feature_2_name": "",
                            "initial_feature_2_value": "",
                            "initial_feature_2_threshold": "",
                            "initial_feature_2_direction": "",
                            "initial_feature_operator": "",
                        }
                if args.router_mode in {
                    "initial_anchor_pos_dist_force_alt",
                    "initial_anchor_pos_dist_margin_force_alt",
                    "initial_gmm_feature_force_alt",
                    "initial_policy_feature_gate",
                }:
                    selected = episode_forced_policy
                elif args.router_mode == "temporal_gmm_feature":
                    selected = step_temporal_policy
                elif args.router_mode == "temporal_gmm_feature_persistent":
                    selected = temporal_persistent_policy or policy_order[0]
                elif args.router_mode == "positive_anchor_margin_persistent":
                    selected = temporal_persistent_policy or policy_order[0]
                else:
                    selected = select_policy(
                        scores=raw_scores,
                        policy_order=policy_order,
                        biases=biases,
                        router_mode=args.router_mode,
                        switch_threshold=args.switch_threshold,
                    )
                choice_counts[selected] += 1
                episode_choice_counts[selected] += 1
                obs, reward, done, _info = env.step(actions[selected])
                total_return += float(reward)
                length = t + 1
                success = success or env_success(env, float(reward))
                if success or done:
                    break
            successes.append(float(success))
            returns.append(total_return)
            lengths.append(float(length))
            episode_rows.append(
                {
                    "episode": episode,
                    "initial_demo_id": initial.demo_id if initial else "",
                    "success": float(success),
                    "return": total_return,
                    "length": float(length),
                    "initial_gate_open": int(episode_gate_open),
                    "initial_forced_policy": episode_forced_policy,
                    **initial_gate_features,
                    "temporal_gate_open_count": temporal_gate_open_count,
                    "temporal_persistence_steps": args.temporal_persistence_steps,
                    "temporal_persistent_switch_step": temporal_persistent_switch_step,
                    "temporal_persistent_policy": temporal_persistent_policy,
                    "temporal_feature_min": min(temporal_feature_values) if temporal_feature_values else "",
                    "temporal_feature_mean": (
                        float(np.mean(temporal_feature_values)) if temporal_feature_values else ""
                    ),
                    "temporal_feature_max": max(temporal_feature_values) if temporal_feature_values else "",
                    **{f"choices_{name}": episode_choice_counts[name] for name in policy_order},
                }
            )
    finally:
        if hasattr(env, "close"):
            env.close()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    router_name = (
        f"{args.router_mode}_{args.support_mode}_thr{args.switch_threshold:g}_"
        f"initthr{args.initial_gate_threshold:g}_initmarginthr{args.initial_gate_margin_threshold:g}_"
        + "_".join(f"{name}bias{biases.get(name, 0.0):g}" for name in policy_order)
    )
    metrics_row = {
        "router_name": router_name,
        "success_rate": float(np.mean(successes)),
        "avg_return": float(np.mean(returns)),
        "avg_len": float(np.mean(lengths)),
        "eval_episodes": args.eval_episodes,
        **{f"choices_{name}": choice_counts[name] for name in policy_order},
    }
    with (args.out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "router_name",
            "success_rate",
            "avg_return",
            "avg_len",
            "eval_episodes",
            *[f"choices_{name}" for name in policy_order],
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(metrics_row)
    with (args.out_dir / "episode_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "episode",
            "initial_demo_id",
            "success",
            "return",
            "length",
            "initial_gate_open",
            "initial_forced_policy",
            "initial_anchor_margin",
            "initial_anchor_pos_dist",
            "initial_anchor_neg_dist",
            "initial_feature_name",
            "initial_feature_value",
            "initial_feature_threshold",
            "initial_feature_direction",
            "initial_feature_2_name",
            "initial_feature_2_value",
            "initial_feature_2_threshold",
            "initial_feature_2_direction",
            "initial_feature_operator",
            "temporal_gate_open_count",
            "temporal_persistence_steps",
            "temporal_persistent_switch_step",
            "temporal_persistent_policy",
            "temporal_feature_min",
            "temporal_feature_mean",
            "temporal_feature_max",
            *[f"choices_{name}" for name in policy_order],
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(episode_rows)
    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "env_name": env_meta["env_name"],
        "env_version": env_meta.get("env_version"),
        "policies": {name: str(path) for name, path in policy_specs},
        "policy_order": policy_order,
        "policy_biases": biases,
        "router_mode": args.router_mode,
        "support_mode": args.support_mode,
        "positive_anchor_diagnostics": str(args.positive_anchor_diagnostics) if args.positive_anchor_diagnostics else None,
        "switch_threshold": args.switch_threshold,
        "initial_gate_threshold": args.initial_gate_threshold,
        "initial_gate_margin_threshold": args.initial_gate_margin_threshold,
        "initial_feature": args.initial_feature,
        "initial_feature_threshold": args.initial_feature_threshold,
        "effective_initial_feature_threshold": effective_initial_feature_threshold,
        "initial_feature_threshold_source": args.initial_feature_threshold_source,
        "initial_feature_quantile": args.initial_feature_quantile,
        "initial_feature_calibration_ids": calibration_ids,
        "initial_feature_calibration_values": calibration_values,
        "initial_feature_direction": args.initial_feature_direction,
        "initial_policy_feature": args.initial_policy_feature,
        "initial_policy_feature_threshold": args.initial_policy_feature_threshold,
        "initial_policy_feature_direction": args.initial_policy_feature_direction,
        "initial_policy_feature_2": args.initial_policy_feature_2,
        "initial_policy_feature_threshold_2": args.initial_policy_feature_threshold_2,
        "initial_policy_feature_direction_2": args.initial_policy_feature_direction_2,
        "initial_policy_feature_operator": args.initial_policy_feature_operator,
        "temporal_persistence_steps": args.temporal_persistence_steps,
        "isolated_policy_rng": not args.shared_policy_rng,
        "obs_keys": list(obs_keys),
        "eval_init_mode": args.eval_init_mode,
        "eval_initial_ids": eval_initial_ids,
        "eval_episodes": args.eval_episodes,
        "eval_horizon": args.eval_horizon,
        "seed": args.seed,
        "device": str(device),
    }
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    report = [
        "# Robomimic Router Policy Evaluation",
        "",
        f"Split path: `{args.split_path}`.",
        f"Eval init mode: `{args.eval_init_mode}`.",
        f"Eval episodes: `{args.eval_episodes}`.",
        f"Eval horizon: `{args.eval_horizon}`.",
        f"Router mode: `{args.router_mode}`.",
        f"Support mode: `{args.support_mode}`.",
        f"Switch threshold: `{args.switch_threshold}`.",
        f"Initial gate threshold: `{args.initial_gate_threshold}`.",
        f"Initial gate margin threshold: `{args.initial_gate_margin_threshold}`.",
        f"Initial feature: `{args.initial_feature}`.",
        f"Initial feature threshold: `{args.initial_feature_threshold}`.",
        f"Effective initial feature threshold: `{effective_initial_feature_threshold}`.",
        f"Initial feature threshold source: `{args.initial_feature_threshold_source}`.",
        f"Initial feature quantile: `{args.initial_feature_quantile}`.",
        f"Initial feature direction: `{args.initial_feature_direction}`.",
        f"Initial policy feature: `{args.initial_policy_feature}`.",
        f"Initial policy feature threshold: `{args.initial_policy_feature_threshold}`.",
        f"Initial policy feature direction: `{args.initial_policy_feature_direction}`.",
        f"Initial policy feature 2: `{args.initial_policy_feature_2}`.",
        f"Initial policy feature threshold 2: `{args.initial_policy_feature_threshold_2}`.",
        f"Initial policy feature direction 2: `{args.initial_policy_feature_direction_2}`.",
        f"Initial policy feature operator: `{args.initial_policy_feature_operator}`.",
        f"Temporal persistence steps: `{args.temporal_persistence_steps}`.",
        f"Isolated policy RNG: `{not args.shared_policy_rng}`.",
        f"Policies: `{', '.join(policy_order)}`.",
        "",
        "## Metrics",
        "",
        checkpoint_table([metrics_row]),
        "",
        "## Action Choice Counts",
        "",
        "| policy | count |",
        "| --- | ---: |",
        *[f"| {name} | {choice_counts[name]} |" for name in policy_order],
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(
        f"{router_name}: success={metrics_row['success_rate']:.3f} "
        f"return={metrics_row['avg_return']:.3f} len={metrics_row['avg_len']:.1f}",
        flush=True,
    )
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
