from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import h5py
import jax
import jax.numpy as jnp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_minari_action_rerank_smoke import state_action_features, train_state_action_classifier  # noqa: E402
from run_minari_bc_baselines import init_mlp, markdown_table, mlp_apply, predict  # noqa: E402
from run_robomimic_can_rollout_smoke import (  # noqa: E402
    DemoBatch,
    action_bounds,
    classifier_logits,
    dataset_obs_keys,
    env_success,
    load_env_metadata,
    load_eval_initials,
    make_env,
    normalize,
    obs_vector_from_demo,
    obs_vector_from_env,
    reset_env,
    sigmoid,
)
from tri_piql.algos.tabular import _adam_update, _tree_zeros_like  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_can_gmm_smoke"))
    parser.add_argument(
        "--source",
        choices=[
            "labeled_positive",
            "positive_plus_classifier_unlabeled",
            "positive_plus_classifier_top_unlabeled_demos",
            "positive_plus_classifier_diverse_unlabeled_demos",
            "positive_plus_classifier_gap_unlabeled_demos",
            "positive_plus_classifier_adaptive_masscap_unlabeled_demos",
            "positive_plus_classifier_demo_threshold_unlabeled_demos",
            "positive_plus_classifier_weighted_unlabeled_demos",
            "positive_plus_positive_nn_top_unlabeled_demos",
            "all_train_positive",
        ],
        default="positive_plus_classifier_unlabeled",
    )
    parser.add_argument(
        "--eval-init-mode",
        choices=["env_reset", "valid_positive_states"],
        default="valid_positive_states",
    )
    parser.add_argument("--eval-episodes", type=int, default=5)
    parser.add_argument("--eval-horizon", type=int, default=400)
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument(
        "--eval-checkpoints",
        type=int,
        nargs="*",
        default=[],
        help="Optional optimizer steps to evaluate during one training run; final --steps is always included.",
    )
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--components", type=int, default=5)
    parser.add_argument(
        "--gmm-validation-frac",
        type=float,
        default=0.0,
        help="Hold out this fraction of source-support demos for checkpoint selection NLL. Disabled at 0.",
    )
    parser.add_argument("--gmm-validation-min-demos", type=int, default=2)
    parser.add_argument(
        "--checkpoint-selection-metric",
        choices=["support_val_nll", "support_val_mode_mse", "support_val_mean_mse"],
        default="support_val_nll",
    )
    parser.add_argument(
        "--retrain-selected-checkpoint",
        action="store_true",
        help="After support-validation checkpoint selection, retrain on full source support to the selected step and roll it out.",
    )
    parser.add_argument(
        "--feature-mode",
        choices=["obs", "obs_prev_action", "obs_time", "obs_prev_action_time"],
        default="obs",
    )
    parser.add_argument("--min-log-std", type=float, default=-5.0)
    parser.add_argument("--max-log-std", type=float, default=0.5)
    parser.add_argument("--unlabeled-threshold", type=float, default=0.9)
    parser.add_argument("--top-unlabeled-demos", type=int, default=40)
    parser.add_argument("--candidate-unlabeled-demos", type=int, default=120)
    parser.add_argument("--diversity-weight", type=float, default=0.35)
    parser.add_argument("--gap-select-max-unlabeled-demos", type=int, default=80)
    parser.add_argument("--gap-select-min-unlabeled-demos", type=int, default=4)
    parser.add_argument(
        "--gap-select-min-labeled-positive-multiplier",
        type=float,
        default=0.0,
        help=(
            "Optional hidden-label-free floor for score-gap selection. "
            "The effective minimum is max(--gap-select-min-unlabeled-demos, "
            "ceil(multiplier * number of labeled-positive demos))."
        ),
    )
    parser.add_argument("--adaptive-mass-cap-ratio", type=float, default=1.25)
    parser.add_argument(
        "--demo-threshold-rule",
        choices=["pos_min", "pos_p10", "mid_mean", "mid_minpos_maxneg", "neg_max"],
        default="pos_min",
        help="Demo-score threshold rule for positive_plus_classifier_demo_threshold_unlabeled_demos.",
    )
    parser.add_argument("--unlabeled-weight-mode", choices=["one", "prob"], default="prob")
    parser.add_argument("--policy-modes", nargs="+", default=["mode", "mean", "classifier_rerank"])
    parser.add_argument("--candidate-count", type=int, default=32)
    parser.add_argument("--sample-temperature", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


def train_positive_ids(split: dict) -> list[str]:
    positives = set(split["all_positive_ids"])
    return [demo_id for demo_id in split["train_ids"] if demo_id in positives]


def feature_batch_from_arrays(
    obs: np.ndarray,
    actions: np.ndarray,
    *,
    feature_mode: str,
    eval_horizon: int,
) -> np.ndarray:
    parts = [obs.astype(np.float32, copy=False)]
    if "prev_action" in feature_mode:
        prev = np.zeros_like(actions, dtype=np.float32)
        if actions.shape[0] > 1:
            prev[1:] = actions[:-1]
        parts.append(prev)
    if "time" in feature_mode:
        denom = max(1, min(eval_horizon, actions.shape[0]) - 1)
        t = (np.arange(actions.shape[0], dtype=np.float32) / float(denom)).clip(0.0, 1.0)[:, None]
        parts.append(t)
    return np.concatenate(parts, axis=1).astype(np.float32, copy=False)


def eval_feature(
    obs: dict[str, np.ndarray],
    obs_keys: list[str],
    *,
    feature_mode: str,
    prev_action: np.ndarray,
    t: int,
    eval_horizon: int,
) -> np.ndarray:
    raw_obs = obs_vector_from_env(obs, obs_keys)
    parts = [raw_obs]
    if "prev_action" in feature_mode:
        parts.append(prev_action.astype(np.float32, copy=False))
    if "time" in feature_mode:
        denom = max(1, eval_horizon - 1)
        parts.append(np.asarray([min(1.0, t / float(denom))], dtype=np.float32))
    return np.concatenate(parts, axis=0).astype(np.float32, copy=False)


def load_feature_batch(hdf5_path: str, demo_ids: list[str], obs_keys: list[str], *, feature_mode: str, eval_horizon: int) -> DemoBatch:
    obs_chunks = []
    action_chunks = []
    demo_chunks = []
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted(demo_ids, key=demo_sort_key):
            group = f["data"][demo_id]
            obs = obs_vector_from_demo(group, obs_keys)
            actions = np.asarray(group["actions"], dtype=np.float32)
            obs_chunks.append(feature_batch_from_arrays(obs, actions, feature_mode=feature_mode, eval_horizon=eval_horizon))
            action_chunks.append(actions)
            demo_chunks.append(np.full((actions.shape[0],), demo_sort_key(demo_id), dtype=np.int32))
    if not obs_chunks:
        raise ValueError("no demos loaded")
    return DemoBatch(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        demo_ids=np.concatenate(demo_chunks, axis=0),
    )


def split_gmm_output(
    output: jnp.ndarray,
    *,
    components: int,
    action_dim: int,
    min_log_std: float,
    max_log_std: float,
) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    logits = output[:, :components]
    mean_start = components
    mean_end = mean_start + components * action_dim
    means = output[:, mean_start:mean_end].reshape((-1, components, action_dim))
    log_stds = output[:, mean_end:].reshape((-1, components, action_dim))
    log_stds = jnp.clip(log_stds, min_log_std, max_log_std)
    return logits, means, log_stds


def train_gmm_policy(
    obs: np.ndarray,
    actions: np.ndarray,
    weights: np.ndarray,
    *,
    seed: int,
    steps: int,
    batch_size: int,
    hidden_dim: int,
    depth: int,
    lr: float,
    components: int,
    min_log_std: float,
    max_log_std: float,
    checkpoint_steps: set[int] | None = None,
) -> tuple[list[dict[str, jax.Array]], list[dict[str, float]], dict[int, list[dict[str, jax.Array]]]]:
    obs_j = jnp.asarray(obs, dtype=jnp.float32)
    act_j = jnp.asarray(actions, dtype=jnp.float32)
    w_j = jnp.asarray(weights, dtype=jnp.float32)
    action_dim = actions.shape[1]
    output_dim = components * (1 + 2 * action_dim)

    key = jax.random.PRNGKey(seed)
    key, init_key = jax.random.split(key)
    params = init_mlp(init_key, obs.shape[1], output_dim, hidden_dim, depth)
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))

    def loss_fn(local_params, idx):
        output = mlp_apply(local_params, obs_j[idx])
        logits, means, log_stds = split_gmm_output(
            output,
            components=components,
            action_dim=action_dim,
            min_log_std=min_log_std,
            max_log_std=max_log_std,
        )
        centered = (act_j[idx, None, :] - means) / jnp.exp(log_stds)
        log_prob = -0.5 * jnp.sum(centered**2 + 2.0 * log_stds + jnp.log(2.0 * jnp.pi), axis=-1)
        log_mix = jax.nn.log_softmax(logits, axis=-1)
        nll = -jax.nn.logsumexp(log_mix + log_prob, axis=-1)
        local_w = w_j[idx]
        return jnp.sum(local_w * nll) / (jnp.sum(local_w) + 1.0e-6)

    grad_fn = jax.value_and_grad(loss_fn)

    @jax.jit
    def step(local_params, local_opt_state, local_key, local_step):
        local_key, sample_key = jax.random.split(local_key)
        idx = jax.random.randint(sample_key, (batch_size,), minval=0, maxval=obs.shape[0])
        loss, grads = grad_fn(local_params, idx)
        local_params, local_opt_state = _adam_update(local_params, grads, local_opt_state, lr, local_step)
        return local_params, local_opt_state, local_key, loss

    checkpoint_steps = checkpoint_steps or {steps}
    history = []
    checkpoints = {}
    for step_id in range(1, steps + 1):
        params, opt_state, key, loss = step(params, opt_state, key, jnp.asarray(step_id, dtype=jnp.float32))
        if step_id == 1 or step_id % max(1, steps // 5) == 0 or step_id == steps:
            history.append({"step": step_id, "loss": float(loss)})
        if step_id in checkpoint_steps:
            checkpoints[step_id] = jax.tree.map(lambda x: x.copy(), params)
    return params, history, checkpoints


def gmm_predict_np(
    params,
    obs: np.ndarray,
    *,
    components: int,
    action_dim: int,
    min_log_std: float,
    max_log_std: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    output = mlp_apply(params, jnp.asarray(obs, dtype=jnp.float32))
    logits, means, log_stds = split_gmm_output(
        output,
        components=components,
        action_dim=action_dim,
        min_log_std=min_log_std,
        max_log_std=max_log_std,
    )
    return np.asarray(logits), np.asarray(means), np.asarray(log_stds)


def weighted_gmm_nll(
    params,
    obs: np.ndarray,
    actions: np.ndarray,
    weights: np.ndarray,
    *,
    components: int,
    action_dim: int,
    min_log_std: float,
    max_log_std: float,
) -> float:
    if obs.shape[0] == 0:
        return float("nan")
    obs_j = jnp.asarray(obs, dtype=jnp.float32)
    act_j = jnp.asarray(actions, dtype=jnp.float32)
    w_j = jnp.asarray(weights, dtype=jnp.float32)
    output = mlp_apply(params, obs_j)
    logits, means, log_stds = split_gmm_output(
        output,
        components=components,
        action_dim=action_dim,
        min_log_std=min_log_std,
        max_log_std=max_log_std,
    )
    centered = (act_j[:, None, :] - means) / jnp.exp(log_stds)
    log_prob = -0.5 * jnp.sum(centered**2 + 2.0 * log_stds + jnp.log(2.0 * jnp.pi), axis=-1)
    log_mix = jax.nn.log_softmax(logits, axis=-1)
    nll = -jax.nn.logsumexp(log_mix + log_prob, axis=-1)
    return float(jnp.sum(w_j * nll) / (jnp.sum(w_j) + 1.0e-6))


def weighted_gmm_action_mse(
    params,
    obs: np.ndarray,
    actions: np.ndarray,
    weights: np.ndarray,
    *,
    components: int,
    action_dim: int,
    min_log_std: float,
    max_log_std: float,
    mode: str,
) -> float:
    logits, means, _log_stds = gmm_predict_np(
        params,
        obs,
        components=components,
        action_dim=action_dim,
        min_log_std=min_log_std,
        max_log_std=max_log_std,
    )
    probs = np.exp(logits - logits.max(axis=1, keepdims=True))
    probs = probs / (probs.sum(axis=1, keepdims=True) + 1.0e-8)
    if mode == "mode":
        pred = means[np.arange(means.shape[0]), np.argmax(probs, axis=1)]
    elif mode == "mean":
        pred = np.sum(means * probs[:, :, None], axis=1)
    else:
        raise ValueError(mode)
    per_transition = np.mean((pred - actions) ** 2, axis=1)
    return float(np.sum(weights * per_transition) / (np.sum(weights) + 1.0e-6))


def checkpoint_validation_table(rows: list[dict]) -> str:
    lines = [
        "| checkpoint_step | support_train_nll | support_val_nll | support_val_mode_mse | support_val_mean_mse |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {int(row['checkpoint_step'])} | "
            f"{float(row['support_train_nll']):.3f} | "
            f"{float(row['support_val_nll']):.3f} | "
            f"{float(row['support_val_mode_mse']):.6f} | "
            f"{float(row['support_val_mean_mse']):.6f} |"
        )
    return "\n".join(lines)


def gmm_policy(params, *, args: argparse.Namespace, action_dim: int, mode: str, classifier=None):
    def policy(feature: np.ndarray, rng: np.random.Generator, low: np.ndarray, high: np.ndarray) -> np.ndarray:
        logits, means, log_stds = gmm_predict_np(
            params,
            feature,
            components=args.components,
            action_dim=action_dim,
            min_log_std=args.min_log_std,
            max_log_std=args.max_log_std,
        )
        local_logits = logits[0]
        local_means = means[0]
        local_log_stds = log_stds[0]
        probs = np.exp(local_logits - np.max(local_logits))
        probs = probs / (probs.sum() + 1.0e-8)
        if mode == "mode":
            return local_means[int(np.argmax(probs))]
        if mode == "mean":
            return np.sum(local_means * probs[:, None], axis=0)
        if mode == "sample":
            component = int(rng.choice(args.components, p=probs))
            std = np.exp(local_log_stds[component]) * args.sample_temperature
            return rng.normal(local_means[component], std).astype(np.float32)
        if mode == "classifier_rerank":
            if classifier is None:
                raise ValueError("classifier_rerank requires a classifier")
            candidates = np.empty((args.candidate_count, action_dim), dtype=np.float32)
            best_component = int(np.argmax(probs))
            candidates[0] = local_means[best_component]
            for i in range(1, args.candidate_count):
                component = int(rng.choice(args.components, p=probs))
                std = np.exp(local_log_stds[component]) * args.sample_temperature
                candidates[i] = rng.normal(local_means[component], std).astype(np.float32)
            candidates = np.clip(candidates, low, high)
            repeated_obs = np.repeat(feature.astype(np.float32), args.candidate_count, axis=0)
            logits_for_actions = classifier_logits(classifier, repeated_obs, candidates)
            return candidates[int(np.argmax(logits_for_actions))]
        raise ValueError(mode)

    return policy


def source_batches(args: argparse.Namespace, split: dict, hdf5_path: str, obs_keys: list[str]):
    pos_raw = load_feature_batch(
        hdf5_path,
        split["labeled_positive_ids"],
        obs_keys,
        feature_mode=args.feature_mode,
        eval_horizon=args.eval_horizon,
    )
    neg_raw = load_feature_batch(
        hdf5_path,
        split["labeled_negative_ids"],
        obs_keys,
        feature_mode=args.feature_mode,
        eval_horizon=args.eval_horizon,
    )
    unl_raw = load_feature_batch(
        hdf5_path,
        split["unlabeled_ids"],
        obs_keys,
        feature_mode=args.feature_mode,
        eval_horizon=args.eval_horizon,
    )
    normalize_inputs = [pos_raw.observations, neg_raw.observations, unl_raw.observations]
    all_pos_raw = None
    if args.source == "all_train_positive":
        all_pos_raw = load_feature_batch(
            hdf5_path,
            train_positive_ids(split),
            obs_keys,
            feature_mode=args.feature_mode,
            eval_horizon=args.eval_horizon,
        )
        normalize_inputs.append(all_pos_raw.observations)
    all_train_obs = np.concatenate([pos_raw.observations, neg_raw.observations, unl_raw.observations], axis=0)
    obs_mean, obs_std, normalized = normalize(all_train_obs, *normalize_inputs)
    pos_obs, neg_obs, unl_obs = normalized[:3]
    pos = DemoBatch(pos_obs, pos_raw.actions, pos_raw.demo_ids)
    neg = DemoBatch(neg_obs, neg_raw.actions, neg_raw.demo_ids)
    unl = DemoBatch(unl_obs, unl_raw.actions, unl_raw.demo_ids)
    if all_pos_raw is not None:
        all_pos = DemoBatch(normalized[3], all_pos_raw.actions, all_pos_raw.demo_ids)
    else:
        all_pos = None
    return obs_mean, obs_std, pos, neg, unl, all_pos


def select_diverse_demos(
    candidate_scores: list[tuple[int, float]],
    demo_reps: dict[int, np.ndarray],
    count: int,
    diversity_weight: float,
) -> list[int]:
    if not candidate_scores:
        return []
    count = min(count, len(candidate_scores))
    candidate_ids = [demo_index for demo_index, _score in candidate_scores]
    scores = np.asarray([score for _demo_index, score in candidate_scores], dtype=np.float64)
    score_min = float(scores.min())
    score_max = float(scores.max())
    score_norm = (scores - score_min) / (score_max - score_min + 1.0e-8)
    reps = np.stack([demo_reps[demo_index] for demo_index in candidate_ids], axis=0).astype(np.float64)
    reps = (reps - reps.mean(axis=0, keepdims=True)) / (reps.std(axis=0, keepdims=True) + 1.0e-6)

    selected_local = [int(np.argmax(score_norm))]
    selected_set = {selected_local[0]}
    while len(selected_local) < count:
        selected_reps = reps[selected_local]
        distances = np.sqrt(((reps[:, None, :] - selected_reps[None, :, :]) ** 2).mean(axis=2))
        min_dist = distances.min(axis=1)
        min_dist = min_dist / (float(min_dist.max()) + 1.0e-8)
        objective = score_norm + diversity_weight * min_dist
        for selected_idx in selected_set:
            objective[selected_idx] = -np.inf
        next_idx = int(np.argmax(objective))
        selected_local.append(next_idx)
        selected_set.add(next_idx)
    return [candidate_ids[idx] for idx in selected_local]


def select_gap_demos(
    demo_scores: list[tuple[int, float]],
    *,
    max_count: int,
    min_count: int,
) -> tuple[list[int], float]:
    if not demo_scores:
        return [], 0.0
    max_count = min(max(1, int(max_count)), len(demo_scores))
    min_count = min(max(1, int(min_count)), max_count)
    if max_count <= min_count:
        return [demo_index for demo_index, _score in demo_scores[:max_count]], 0.0
    scores = np.asarray([score for _demo_index, score in demo_scores[:max_count]], dtype=np.float64)
    gaps = scores[:-1] - scores[1:]
    start = min_count - 1
    cut_idx = start + int(np.argmax(gaps[start:]))
    selected_count = cut_idx + 1
    return [demo_index for demo_index, _score in demo_scores[:selected_count]], float(gaps[cut_idx])


def effective_gap_min_count(args: argparse.Namespace, split: dict) -> int:
    absolute_floor = int(args.gap_select_min_unlabeled_demos)
    multiplier = float(getattr(args, "gap_select_min_labeled_positive_multiplier", 0.0))
    if multiplier <= 0.0:
        return absolute_floor
    label_budget_floor = int(np.ceil(multiplier * len(split["labeled_positive_ids"])))
    return max(absolute_floor, label_budget_floor)


def positive_nn_transition_scores(pos_obs: np.ndarray, pos_actions: np.ndarray, unl_obs: np.ndarray, unl_actions: np.ndarray) -> np.ndarray:
    pos_x = state_action_features(pos_obs, pos_actions).astype(np.float32, copy=False)
    unl_x = state_action_features(unl_obs, unl_actions).astype(np.float32, copy=False)
    mean = np.mean(np.concatenate([pos_x, unl_x], axis=0), axis=0, keepdims=True)
    std = np.std(np.concatenate([pos_x, unl_x], axis=0), axis=0, keepdims=True) + 1.0e-6
    pos_x = (pos_x - mean) / std
    unl_x = (unl_x - mean) / std
    min_dist = np.full((unl_x.shape[0],), np.inf, dtype=np.float32)
    chunk = 2048
    for start in range(0, unl_x.shape[0], chunk):
        part = unl_x[start : start + chunk]
        distances = np.mean((part[:, None, :] - pos_x[None, :, :]) ** 2, axis=2)
        min_dist[start : start + chunk] = distances.min(axis=1)
    return -min_dist


def demo_mean_scores(batch: DemoBatch, scores: np.ndarray) -> list[tuple[int, float]]:
    demo_scores = []
    for demo_index in np.unique(batch.demo_ids):
        mask = batch.demo_ids == demo_index
        demo_scores.append((int(demo_index), float(scores[mask].mean())))
    demo_scores.sort(key=lambda item: item[1], reverse=True)
    return demo_scores


def build_library(args: argparse.Namespace, split: dict, pos: DemoBatch, neg: DemoBatch, unl: DemoBatch, all_pos: DemoBatch | None):
    classifier = None
    classifier_metrics = None
    selected_unlabeled = 0
    selected_demo_ids: list[str] = []
    selected_hidden_positive_demos = 0
    selection_diagnostics: dict[str, float | int | str] = {}
    if args.source == "labeled_positive":
        weights = np.ones((pos.actions.shape[0],), dtype=np.float32)
        return pos, weights, classifier, classifier_metrics, selected_unlabeled, selected_demo_ids, selected_hidden_positive_demos, selection_diagnostics
    if args.source == "all_train_positive":
        if all_pos is None:
            raise ValueError("all_pos batch missing")
        weights = np.ones((all_pos.actions.shape[0],), dtype=np.float32)
        return all_pos, weights, classifier, classifier_metrics, selected_unlabeled, selected_demo_ids, selected_hidden_positive_demos, selection_diagnostics
    if args.source == "positive_plus_positive_nn_top_unlabeled_demos":
        unl_scores = positive_nn_transition_scores(pos.observations, pos.actions, unl.observations, unl.actions)
        demo_scores = demo_mean_scores(unl, unl_scores)
        selected_order = [demo_index for demo_index, _score in demo_scores[: args.top_unlabeled_demos]]
        selected_demo_indices = set(selected_order)
        keep = np.asarray([int(demo_id) in selected_demo_indices for demo_id in unl.demo_ids], dtype=bool)
        selected_unlabeled = int(keep.sum())
        if selected_unlabeled == 0:
            keep[np.argmax(unl_scores)] = True
            selected_unlabeled = 1
        selected_demo_ids = [f"demo_{demo_index}" for demo_index in selected_order]
        hidden_positive = set(split["all_positive_ids"])
        selected_hidden_positive_demos = sum(1 for demo_id in selected_demo_ids if demo_id in hidden_positive)
        selected_hidden_bad_demos = len(selected_demo_ids) - selected_hidden_positive_demos
        selected_score_values = [score for demo_index, score in demo_scores if demo_index in selected_demo_indices]
        selection_diagnostics = {
            "selection_rule": "positive_nn_top",
            "requested_demos": int(args.top_unlabeled_demos),
            "selected_demo_count": len(selected_demo_ids),
            "selected_hidden_positive_demos": int(selected_hidden_positive_demos),
            "selected_hidden_bad_demos": int(selected_hidden_bad_demos),
            "selected_hidden_positive_purity": float(selected_hidden_positive_demos / max(1, len(selected_demo_ids))),
            "selected_score_mean": float(np.mean(selected_score_values)),
            "selected_score_min": float(min(selected_score_values)),
            "selected_score_max": float(max(selected_score_values)),
        }
        library = DemoBatch(
            np.concatenate([pos.observations, unl.observations[keep]], axis=0),
            np.concatenate([pos.actions, unl.actions[keep]], axis=0),
            np.concatenate([pos.demo_ids, unl.demo_ids[keep]], axis=0),
        )
        weights = np.ones((library.actions.shape[0],), dtype=np.float32)
        classifier_metrics = {
            "selection_score_type": "positive_nn_negative_distance",
            "selected_unlabeled_transitions": selected_unlabeled,
            "selected_unlabeled_score_mean": float(np.mean(unl_scores[keep])),
            "selected_unlabeled_demos": len(selected_demo_ids),
            "selected_hidden_positive_demos": int(selected_hidden_positive_demos),
        }
        return library, weights, classifier, classifier_metrics, selected_unlabeled, selected_demo_ids, selected_hidden_positive_demos, selection_diagnostics

    classifier, _history = train_state_action_classifier(
        pos.observations,
        pos.actions,
        neg.observations,
        neg.actions,
        seed=args.seed + 77,
        steps=args.classifier_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )
    pos_logits = predict(classifier, state_action_features(pos.observations, pos.actions)).reshape(-1)
    neg_logits = predict(classifier, state_action_features(neg.observations, neg.actions)).reshape(-1)
    unl_logits = predict(classifier, state_action_features(unl.observations, unl.actions)).reshape(-1)
    unl_prob = sigmoid(unl_logits)
    if args.source in {
        "positive_plus_classifier_top_unlabeled_demos",
        "positive_plus_classifier_diverse_unlabeled_demos",
        "positive_plus_classifier_gap_unlabeled_demos",
        "positive_plus_classifier_adaptive_masscap_unlabeled_demos",
        "positive_plus_classifier_demo_threshold_unlabeled_demos",
        "positive_plus_classifier_weighted_unlabeled_demos",
    }:
        demo_scores: list[tuple[int, float]] = []
        demo_reps: dict[int, np.ndarray] = {}
        for demo_index in np.unique(unl.demo_ids):
            mask = unl.demo_ids == demo_index
            demo_index_int = int(demo_index)
            demo_scores.append((demo_index_int, float(unl_prob[mask].mean())))
            demo_obs = unl.observations[mask]
            demo_reps[demo_index_int] = np.concatenate(
                [
                    demo_obs[0],
                    demo_obs[-1],
                    demo_obs.mean(axis=0),
                    demo_obs.std(axis=0),
                ],
                axis=0,
            ).astype(np.float32)
        demo_scores.sort(key=lambda item: item[1], reverse=True)
        if args.source == "positive_plus_classifier_weighted_unlabeled_demos":
            selected_order = [demo_index for demo_index, _score in demo_scores]
            selection_diagnostics.update(
                {
                    "selection_rule": "demo_probability_weighting",
                    "demo_scores": {f"demo_{demo_index}": float(score) for demo_index, score in demo_scores},
                    "selected_score_mean": float(np.mean([score for _demo_index, score in demo_scores])),
                    "selected_score_min": float(min(score for _demo_index, score in demo_scores)),
                    "selected_score_max": float(max(score for _demo_index, score in demo_scores)),
                }
            )
        elif args.source == "positive_plus_classifier_diverse_unlabeled_demos":
            candidate_scores = demo_scores[: min(args.candidate_unlabeled_demos, len(demo_scores))]
            selected_order = select_diverse_demos(candidate_scores, demo_reps, args.top_unlabeled_demos, args.diversity_weight)
            selection_diagnostics.update(
                {
                    "selection_rule": "diverse_top",
                    "candidate_demos": len(candidate_scores),
                    "requested_demos": int(args.top_unlabeled_demos),
                }
            )
        elif args.source == "positive_plus_classifier_gap_unlabeled_demos":
            gap_min_count = effective_gap_min_count(args, split)
            selected_order, score_gap = select_gap_demos(
                demo_scores,
                max_count=args.gap_select_max_unlabeled_demos,
                min_count=gap_min_count,
            )
            selection_diagnostics.update(
                {
                    "selection_rule": "score_gap",
                    "gap_select_max_unlabeled_demos": int(args.gap_select_max_unlabeled_demos),
                    "gap_select_min_unlabeled_demos": int(args.gap_select_min_unlabeled_demos),
                    "gap_select_min_labeled_positive_multiplier": float(
                        getattr(args, "gap_select_min_labeled_positive_multiplier", 0.0)
                    ),
                    "gap_select_effective_min_unlabeled_demos": int(gap_min_count),
                    "labeled_positive_demo_count": int(len(split["labeled_positive_ids"])),
                    "score_gap": float(score_gap),
                    "selected_score_mean": float(np.mean([score for demo_index, score in demo_scores if demo_index in set(selected_order)])),
                    "selected_score_min": float(min(score for demo_index, score in demo_scores if demo_index in set(selected_order))),
                    "selected_score_max": float(max(score for demo_index, score in demo_scores if demo_index in set(selected_order))),
                }
            )
        elif args.source == "positive_plus_classifier_adaptive_masscap_unlabeled_demos":
            gap_min_count = effective_gap_min_count(args, split)
            coverage_order, score_gap = select_gap_demos(
                demo_scores,
                max_count=args.gap_select_max_unlabeled_demos,
                min_count=gap_min_count,
            )

            def demo_mean_probs(batch: DemoBatch, probs: np.ndarray) -> list[float]:
                return [
                    float(probs[batch.demo_ids == demo_index].mean())
                    for demo_index in np.unique(batch.demo_ids)
                ]

            labeled_pos_scores = demo_mean_probs(pos, sigmoid(pos_logits))
            labeled_neg_scores = demo_mean_probs(neg, sigmoid(neg_logits))
            score_denom = max(1.0e-8, float(np.mean(labeled_pos_scores)) - float(np.mean(labeled_neg_scores)))
            estimated_positive_mass = float(
                np.sum(
                    [
                        np.clip((score - float(np.mean(labeled_neg_scores))) / score_denom, 0.0, 1.0)
                        for _demo_index, score in demo_scores
                    ]
                )
            )
            adaptive_precision_count = int(np.ceil(2.0 * len(split["labeled_positive_ids"])))
            mass_cap_limit = int(np.ceil(float(args.adaptive_mass_cap_ratio) * estimated_positive_mass))
            if estimated_positive_mass < gap_min_count:
                selected_order = [
                    demo_index
                    for demo_index, _score in demo_scores[: min(adaptive_precision_count, len(demo_scores))]
                ]
                adaptive_rule = "adaptive_masscap_precision_top_posx2"
            elif len(coverage_order) > mass_cap_limit:
                masscap_count = int(np.ceil(estimated_positive_mass))
                masscap_count = min(len(demo_scores), max(gap_min_count, masscap_count))
                selected_order = [demo_index for demo_index, _score in demo_scores[:masscap_count]]
                adaptive_rule = "adaptive_masscap_top_estimated_mass"
            else:
                selected_order = coverage_order
                adaptive_rule = "adaptive_masscap_coverage_gap"
            selected_order_set = set(selected_order)
            selection_diagnostics.update(
                {
                    "selection_rule": adaptive_rule,
                    "gap_select_max_unlabeled_demos": int(args.gap_select_max_unlabeled_demos),
                    "gap_select_min_unlabeled_demos": int(args.gap_select_min_unlabeled_demos),
                    "gap_select_min_labeled_positive_multiplier": float(
                        getattr(args, "gap_select_min_labeled_positive_multiplier", 0.0)
                    ),
                    "gap_select_effective_min_unlabeled_demos": int(gap_min_count),
                    "adaptive_mass_cap_ratio": float(args.adaptive_mass_cap_ratio),
                    "estimated_positive_mass": float(estimated_positive_mass),
                    "mass_cap_limit": int(mass_cap_limit),
                    "coverage_gap_selected_demo_count": int(len(coverage_order)),
                    "labeled_positive_demo_count": int(len(split["labeled_positive_ids"])),
                    "score_gap": float(score_gap),
                    "selected_score_mean": float(
                        np.mean([score for demo_index, score in demo_scores if demo_index in selected_order_set])
                    ),
                    "selected_score_min": float(
                        min(score for demo_index, score in demo_scores if demo_index in selected_order_set)
                    ),
                    "selected_score_max": float(
                        max(score for demo_index, score in demo_scores if demo_index in selected_order_set)
                    ),
                }
            )
        elif args.source == "positive_plus_classifier_demo_threshold_unlabeled_demos":
            def demo_mean_probs(batch: DemoBatch, probs: np.ndarray) -> list[float]:
                return [
                    float(probs[batch.demo_ids == demo_index].mean())
                    for demo_index in np.unique(batch.demo_ids)
                ]

            labeled_pos_scores = demo_mean_probs(pos, sigmoid(pos_logits))
            labeled_neg_scores = demo_mean_probs(neg, sigmoid(neg_logits))
            thresholds = {
                "pos_min": min(labeled_pos_scores),
                "pos_p10": float(np.quantile(labeled_pos_scores, 0.10)),
                "mid_mean": 0.5 * (float(np.mean(labeled_pos_scores)) + float(np.mean(labeled_neg_scores))),
                "mid_minpos_maxneg": 0.5 * (min(labeled_pos_scores) + max(labeled_neg_scores)),
                "neg_max": max(labeled_neg_scores),
            }
            threshold = float(thresholds[args.demo_threshold_rule])
            selected_order = [demo_index for demo_index, score in demo_scores if score >= threshold]
            if not selected_order:
                selected_order = [demo_scores[0][0]]
            selected_order_set = set(selected_order)
            selection_diagnostics.update(
                {
                    "selection_rule": "demo_threshold",
                    "demo_threshold_rule": args.demo_threshold_rule,
                    "demo_threshold": threshold,
                    "labeled_positive_demo_count": int(len(split["labeled_positive_ids"])),
                    "labeled_negative_demo_count": int(len(split["labeled_negative_ids"])),
                    "labeled_positive_score_min": float(min(labeled_pos_scores)),
                    "labeled_positive_score_p10": float(np.quantile(labeled_pos_scores, 0.10)),
                    "labeled_positive_score_mean": float(np.mean(labeled_pos_scores)),
                    "labeled_negative_score_max": float(max(labeled_neg_scores)),
                    "labeled_negative_score_mean": float(np.mean(labeled_neg_scores)),
                    "selected_score_mean": float(
                        np.mean([score for demo_index, score in demo_scores if demo_index in selected_order_set])
                    ),
                    "selected_score_min": float(
                        min(score for demo_index, score in demo_scores if demo_index in selected_order_set)
                    ),
                    "selected_score_max": float(
                        max(score for demo_index, score in demo_scores if demo_index in selected_order_set)
                    ),
                }
            )
        else:
            selected_order = [demo_index for demo_index, _score in demo_scores[: args.top_unlabeled_demos]]
            selection_diagnostics.update(
                {
                    "selection_rule": "fixed_top",
                    "requested_demos": int(args.top_unlabeled_demos),
                }
            )
        selected_demo_indices = set(selected_order)
        keep = np.asarray([int(demo_id) in selected_demo_indices for demo_id in unl.demo_ids], dtype=bool)
        selected_demo_ids = [f"demo_{demo_index}" for demo_index in selected_order]
        hidden_positive = set(split["all_positive_ids"])
        selected_hidden_positive_demos = sum(1 for demo_id in selected_demo_ids if demo_id in hidden_positive)
        selected_hidden_bad_demos = len(selected_demo_ids) - selected_hidden_positive_demos
        selection_diagnostics.update(
            {
                "selected_demo_count": len(selected_demo_ids),
                "selected_hidden_positive_demos": int(selected_hidden_positive_demos),
                "selected_hidden_bad_demos": int(selected_hidden_bad_demos),
                "selected_hidden_positive_purity": float(selected_hidden_positive_demos / max(1, len(selected_demo_ids))),
            }
        )
    else:
        keep = unl_prob >= args.unlabeled_threshold
        selection_diagnostics.update({"selection_rule": "transition_threshold"})
    selected_unlabeled = int(keep.sum())
    if selected_unlabeled == 0:
        keep[np.argmax(unl_prob)] = True
        selected_unlabeled = 1
    if args.unlabeled_weight_mode == "prob":
        selected_weights = unl_prob[keep].astype(np.float32)
    else:
        selected_weights = np.ones((selected_unlabeled,), dtype=np.float32)
    library = DemoBatch(
        np.concatenate([pos.observations, unl.observations[keep]], axis=0),
        np.concatenate([pos.actions, unl.actions[keep]], axis=0),
        np.concatenate([pos.demo_ids, unl.demo_ids[keep]], axis=0),
    )
    weights = np.concatenate([np.ones((pos.actions.shape[0],), dtype=np.float32), selected_weights], axis=0)
    classifier_metrics = {
        "labeled_accuracy": float(0.5 * ((pos_logits > 0).mean() + (neg_logits < 0).mean())),
        "pos_logit_mean": float(pos_logits.mean()),
        "neg_logit_mean": float(neg_logits.mean()),
        "unlabeled_prob_mean": float(unl_prob.mean()),
        "selected_unlabeled_transitions": selected_unlabeled,
        "selected_unlabeled_prob_mean": float(unl_prob[keep].mean()),
        "selected_unlabeled_demos": len(selected_demo_ids),
        "selected_hidden_positive_demos": selected_hidden_positive_demos,
    }
    return library, weights, classifier, classifier_metrics, selected_unlabeled, selected_demo_ids, selected_hidden_positive_demos, selection_diagnostics


def subset_batch(batch: DemoBatch, mask: np.ndarray) -> DemoBatch:
    return DemoBatch(
        observations=batch.observations[mask],
        actions=batch.actions[mask],
        demo_ids=batch.demo_ids[mask],
    )


def split_support_validation(
    library: DemoBatch,
    weights: np.ndarray,
    *,
    validation_frac: float,
    min_validation_demos: int,
    seed: int,
) -> tuple[DemoBatch, np.ndarray, DemoBatch | None, np.ndarray | None, dict]:
    if validation_frac <= 0.0:
        return library, weights, None, None, {"enabled": False}

    rng = np.random.default_rng(seed)
    unique_demo_ids = np.unique(library.demo_ids)
    if unique_demo_ids.shape[0] >= 2:
        shuffled = np.array(unique_demo_ids, copy=True)
        rng.shuffle(shuffled)
        requested = int(round(float(validation_frac) * float(unique_demo_ids.shape[0])))
        val_demo_count = min(
            unique_demo_ids.shape[0] - 1,
            max(1, int(min_validation_demos), requested),
        )
        val_demo_ids = set(int(demo_id) for demo_id in shuffled[:val_demo_count])
        val_mask = np.asarray([int(demo_id) in val_demo_ids for demo_id in library.demo_ids], dtype=bool)
        split_unit = "demo"
    else:
        order = rng.permutation(library.actions.shape[0])
        val_count = min(library.actions.shape[0] - 1, max(1, int(round(validation_frac * library.actions.shape[0]))))
        val_mask = np.zeros((library.actions.shape[0],), dtype=bool)
        val_mask[order[:val_count]] = True
        val_demo_ids = set(int(demo_id) for demo_id in unique_demo_ids)
        split_unit = "transition"

    if not val_mask.any() or val_mask.all():
        return library, weights, None, None, {
            "enabled": False,
            "reason": "validation split would be empty or consume all source support",
        }

    train_mask = ~val_mask
    train_library = subset_batch(library, train_mask)
    val_library = subset_batch(library, val_mask)
    diagnostics = {
        "enabled": True,
        "unit": split_unit,
        "requested_frac": float(validation_frac),
        "train_transitions": int(train_mask.sum()),
        "validation_transitions": int(val_mask.sum()),
        "train_demos": int(np.unique(train_library.demo_ids).shape[0]),
        "validation_demos": int(np.unique(val_library.demo_ids).shape[0]),
        "validation_demo_ids": [f"demo_{demo_id}" for demo_id in sorted(val_demo_ids)],
    }
    return train_library, weights[train_mask], val_library, weights[val_mask], diagnostics


def rollout_gmm_policy(
    *,
    env_meta: dict,
    obs_keys: list[str],
    obs_mean: np.ndarray,
    obs_std: np.ndarray,
    eval_episodes: int,
    eval_horizon: int,
    eval_initials,
    seed: int,
    feature_mode: str,
    policy_fn,
) -> dict[str, float]:
    env = make_env(env_meta)
    low, high = action_bounds(env)
    returns = []
    lengths = []
    successes = []
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    try:
        for episode in range(eval_episodes):
            np.random.seed(seed + episode)
            initial = eval_initials[episode % len(eval_initials)] if eval_initials else None
            obs = reset_env(env, initial)
            prev_action = np.zeros_like(low, dtype=np.float32)
            total = 0.0
            success = False
            length = 0
            for t in range(eval_horizon):
                feature = eval_feature(
                    obs,
                    obs_keys,
                    feature_mode=feature_mode,
                    prev_action=prev_action,
                    t=t,
                    eval_horizon=eval_horizon,
                )[None, :]
                feature = (feature - obs_mean) / obs_std
                action = policy_fn(feature.astype(np.float32), rng, low, high)
                action = np.clip(action, low, high)
                obs, reward, done, _info = env.step(action)
                prev_action = action.astype(np.float32, copy=False)
                total += float(reward)
                length = t + 1
                success = success or env_success(env, float(reward))
                if success or done:
                    break
            returns.append(total)
            lengths.append(length)
            successes.append(float(success))
    finally:
        if hasattr(env, "close"):
            env.close()
    return {
        "success_rate": float(np.mean(successes)),
        "avg_return": float(np.mean(returns)),
        "avg_len": float(np.mean(lengths)),
    }


def main() -> None:
    args = parse_args()
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    env_meta = load_env_metadata(hdf5_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    obs_mean, obs_std, pos, neg, unl, all_pos = source_batches(args, split, hdf5_path, obs_keys)
    (
        library,
        weights,
        classifier,
        classifier_metrics,
        selected_unlabeled,
        selected_demo_ids,
        selected_hidden_positive_demos,
        selection_diagnostics,
    ) = build_library(args, split, pos, neg, unl, all_pos)
    action_dim = library.actions.shape[1]
    train_library, train_weights, validation_library, validation_weights, validation_diagnostics = split_support_validation(
        library,
        weights,
        validation_frac=args.gmm_validation_frac,
        min_validation_demos=args.gmm_validation_min_demos,
        seed=args.seed + 313,
    )
    checkpoint_steps = sorted(
        {
            step
            for step in [*args.eval_checkpoints, args.steps]
            if 1 <= step <= args.steps
        }
    )

    gmm_params, gmm_history, checkpoints = train_gmm_policy(
        train_library.observations,
        train_library.actions,
        train_weights,
        seed=args.seed + 101,
        steps=args.steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
        components=args.components,
        min_log_std=args.min_log_std,
        max_log_std=args.max_log_std,
        checkpoint_steps=set(checkpoint_steps),
    )
    checkpoints.setdefault(args.steps, gmm_params)
    checkpoint_validation_rows = []
    selected_checkpoint_step = None
    selected_full_history = None
    if validation_library is not None and validation_weights is not None:
        for checkpoint_step in checkpoint_steps:
            checkpoint_params = checkpoints[checkpoint_step]
            checkpoint_validation_rows.append(
                {
                    "checkpoint_step": checkpoint_step,
                    "support_train_nll": weighted_gmm_nll(
                        checkpoint_params,
                        train_library.observations,
                        train_library.actions,
                        train_weights,
                        components=args.components,
                        action_dim=action_dim,
                        min_log_std=args.min_log_std,
                        max_log_std=args.max_log_std,
                    ),
                    "support_val_nll": weighted_gmm_nll(
                        checkpoint_params,
                        validation_library.observations,
                        validation_library.actions,
                        validation_weights,
                        components=args.components,
                        action_dim=action_dim,
                        min_log_std=args.min_log_std,
                        max_log_std=args.max_log_std,
                    ),
                    "support_train_mode_mse": weighted_gmm_action_mse(
                        checkpoint_params,
                        train_library.observations,
                        train_library.actions,
                        train_weights,
                        components=args.components,
                        action_dim=action_dim,
                        min_log_std=args.min_log_std,
                        max_log_std=args.max_log_std,
                        mode="mode",
                    ),
                    "support_val_mode_mse": weighted_gmm_action_mse(
                        checkpoint_params,
                        validation_library.observations,
                        validation_library.actions,
                        validation_weights,
                        components=args.components,
                        action_dim=action_dim,
                        min_log_std=args.min_log_std,
                        max_log_std=args.max_log_std,
                        mode="mode",
                    ),
                    "support_train_mean_mse": weighted_gmm_action_mse(
                        checkpoint_params,
                        train_library.observations,
                        train_library.actions,
                        train_weights,
                        components=args.components,
                        action_dim=action_dim,
                        min_log_std=args.min_log_std,
                        max_log_std=args.max_log_std,
                        mode="mean",
                    ),
                    "support_val_mean_mse": weighted_gmm_action_mse(
                        checkpoint_params,
                        validation_library.observations,
                        validation_library.actions,
                        validation_weights,
                        components=args.components,
                        action_dim=action_dim,
                        min_log_std=args.min_log_std,
                        max_log_std=args.max_log_std,
                        mode="mean",
                    ),
                }
            )
        selected_checkpoint_step = int(
            min(checkpoint_validation_rows, key=lambda row: row[args.checkpoint_selection_metric])["checkpoint_step"]
        )

    eval_initials = None
    eval_initial_ids: list[str] = []
    if args.eval_init_mode == "valid_positive_states":
        eval_initial_ids = split["valid_positive_ids"]
        eval_initials = load_eval_initials(hdf5_path, eval_initial_ids)

    rows = []
    include_step_suffix = len(checkpoint_steps) > 1
    for checkpoint_step in checkpoint_steps:
        checkpoint_params = checkpoints[checkpoint_step]
        for mode in args.policy_modes:
            method = f"gmm_{mode}_{args.source}"
            if validation_library is not None:
                method = f"{method}_supportval_train"
            if include_step_suffix:
                method = f"{method}_step{checkpoint_step}"
            if mode == "classifier_rerank" and classifier is None:
                continue
            metrics = rollout_gmm_policy(
                env_meta=env_meta,
                obs_keys=obs_keys,
                obs_mean=obs_mean,
                obs_std=obs_std,
                eval_episodes=args.eval_episodes,
                eval_horizon=args.eval_horizon,
                eval_initials=eval_initials,
                seed=args.seed + 1000 + 37 * len(rows),
                feature_mode=args.feature_mode,
                policy_fn=gmm_policy(checkpoint_params, args=args, action_dim=action_dim, mode=mode, classifier=classifier),
            )
            row = {"method": method, "checkpoint_step": checkpoint_step, **metrics}
            rows.append(row)
            print(
                f"{method}: success={row['success_rate']:.3f} "
                f"return={row['avg_return']:.3f} len={row['avg_len']:.1f}"
            )

    if args.retrain_selected_checkpoint and selected_checkpoint_step is not None:
        selected_params, selected_full_history, selected_checkpoints = train_gmm_policy(
            library.observations,
            library.actions,
            weights,
            seed=args.seed + 901,
            steps=selected_checkpoint_step,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
            components=args.components,
            min_log_std=args.min_log_std,
            max_log_std=args.max_log_std,
            checkpoint_steps={selected_checkpoint_step},
        )
        selected_params = selected_checkpoints.get(selected_checkpoint_step, selected_params)
        for mode in args.policy_modes:
            if mode == "classifier_rerank" and classifier is None:
                continue
            method = f"gmm_{mode}_{args.source}_{args.checkpoint_selection_metric}_selected_full_step{selected_checkpoint_step}"
            metrics = rollout_gmm_policy(
                env_meta=env_meta,
                obs_keys=obs_keys,
                obs_mean=obs_mean,
                obs_std=obs_std,
                eval_episodes=args.eval_episodes,
                eval_horizon=args.eval_horizon,
                eval_initials=eval_initials,
                seed=args.seed + 2000 + 37 * len(rows),
                feature_mode=args.feature_mode,
                policy_fn=gmm_policy(selected_params, args=args, action_dim=action_dim, mode=mode, classifier=classifier),
            )
            row = {"method": method, "checkpoint_step": selected_checkpoint_step, **metrics}
            rows.append(row)
            print(
                f"{method}: success={row['success_rate']:.3f} "
                f"return={row['avg_return']:.3f} len={row['avg_len']:.1f}"
            )

    with (args.out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "checkpoint_step", "success_rate", "avg_return", "avg_len"])
        writer.writeheader()
        writer.writerows(rows)
    if checkpoint_validation_rows:
        with (args.out_dir / "checkpoint_validation.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "checkpoint_step",
                    "support_train_nll",
                    "support_val_nll",
                    "support_train_mode_mse",
                    "support_val_mode_mse",
                    "support_train_mean_mse",
                    "support_val_mean_mse",
                ],
            )
            writer.writeheader()
            writer.writerows(checkpoint_validation_rows)

    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "source": args.source,
        "seed": args.seed,
        "source_transition_count": int(library.actions.shape[0]),
        "selected_unlabeled_transitions": selected_unlabeled,
        "selected_unlabeled_demos": selected_demo_ids,
        "selected_hidden_positive_demos": selected_hidden_positive_demos,
        "selection_diagnostics": selection_diagnostics,
        "gmm_validation": validation_diagnostics,
        "gmm_validation_checkpoint_rows": checkpoint_validation_rows,
        "gmm_checkpoint_selection_metric": args.checkpoint_selection_metric,
        "gmm_selected_checkpoint_step": selected_checkpoint_step,
        "gmm_retrain_selected_checkpoint": bool(args.retrain_selected_checkpoint),
        "top_unlabeled_demos": args.top_unlabeled_demos,
        "candidate_unlabeled_demos": args.candidate_unlabeled_demos,
        "diversity_weight": args.diversity_weight,
        "gap_select_max_unlabeled_demos": args.gap_select_max_unlabeled_demos,
        "gap_select_min_unlabeled_demos": args.gap_select_min_unlabeled_demos,
        "gap_select_min_labeled_positive_multiplier": args.gap_select_min_labeled_positive_multiplier,
        "unlabeled_threshold": args.unlabeled_threshold,
        "unlabeled_weight_mode": args.unlabeled_weight_mode,
        "classifier": classifier_metrics,
        "obs_keys": obs_keys,
        "env_name": env_meta["env_name"],
        "env_version": env_meta.get("env_version"),
        "eval_init_mode": args.eval_init_mode,
        "eval_initial_ids": eval_initial_ids,
        "eval_episodes": args.eval_episodes,
        "eval_horizon": args.eval_horizon,
        "steps": args.steps,
        "eval_checkpoints": checkpoint_steps,
        "components": args.components,
        "feature_mode": args.feature_mode,
        "policy_modes": args.policy_modes,
        "candidate_count": args.candidate_count,
        "sample_temperature": args.sample_temperature,
        "gmm_history": gmm_history,
        "gmm_selected_full_history": selected_full_history,
    }
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report = [
        "# Robomimic Can GMM Policy Smoke",
        "",
        f"Split path: `{args.split_path}`.",
        f"Seed: `{args.seed}`.",
        f"Source: `{args.source}`.",
        f"Source transitions: `{library.actions.shape[0]}`.",
        f"Selected unlabeled transitions: `{selected_unlabeled}`.",
        f"Selected unlabeled demos: `{len(selected_demo_ids)}`.",
        f"Selected hidden-positive demos: `{selected_hidden_positive_demos}`.",
        f"Selection diagnostics: `{selection_diagnostics}`.",
        f"Candidate unlabeled demos: `{args.candidate_unlabeled_demos}`.",
        f"Diversity weight: `{args.diversity_weight}`.",
        f"Gap max/min demos: `{args.gap_select_max_unlabeled_demos}` / `{args.gap_select_min_unlabeled_demos}`.",
        f"Gap min labeled-positive multiplier: `{args.gap_select_min_labeled_positive_multiplier}`.",
        f"Unlabeled threshold: `{args.unlabeled_threshold}`.",
        f"GMM support validation: `{validation_diagnostics}`.",
        f"GMM checkpoint selection metric: `{args.checkpoint_selection_metric}`.",
        f"GMM selected checkpoint: `{selected_checkpoint_step}`.",
        f"Retrain selected checkpoint on full support: `{args.retrain_selected_checkpoint}`.",
        f"Components: `{args.components}`.",
        f"Feature mode: `{args.feature_mode}`.",
        f"Policy modes: `{args.policy_modes}`.",
        f"Evaluation init mode: `{args.eval_init_mode}`.",
        f"Evaluation episodes: `{args.eval_episodes}`.",
        f"Evaluation horizon: `{args.eval_horizon}`.",
        f"Evaluated checkpoints: `{checkpoint_steps}`.",
        "",
        "## Metrics",
        "",
        markdown_table(rows),
        "",
        "## Checkpoint Selection",
        "",
        (
            checkpoint_validation_table(checkpoint_validation_rows)
            if checkpoint_validation_rows
            else "- Not used."
        ),
        "",
        "## Classifier",
        "",
        (
            "- Not used for this source."
            if classifier_metrics is None
            else "\n".join(
                [
                    f"- Labeled accuracy: `{classifier_metrics['labeled_accuracy']:.3f}`.",
                    f"- Positive/negative logit mean: `{classifier_metrics['pos_logit_mean']:.3f}` / `{classifier_metrics['neg_logit_mean']:.3f}`.",
                    f"- Unlabeled probability mean: `{classifier_metrics['unlabeled_prob_mean']:.3f}`.",
                    f"- Selected unlabeled transitions: `{classifier_metrics['selected_unlabeled_transitions']}`.",
                    f"- Selected unlabeled probability mean: `{classifier_metrics['selected_unlabeled_prob_mean']:.3f}`.",
                    f"- Selected hidden-positive demos: `{classifier_metrics['selected_hidden_positive_demos']}` / `{classifier_metrics['selected_unlabeled_demos']}`.",
                ]
            )
        ),
        "",
        "## Interpretation",
        "",
        "- This is a compact learned action-distribution extractor for the Robomimic support signal.",
        "- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.",
        "- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.",
    ]
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
