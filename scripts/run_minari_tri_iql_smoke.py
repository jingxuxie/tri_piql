from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_minari_bc_baselines import (  # noqa: E402
    TransitionData,
    default_split_path,
    evaluate_policy,
    init_mlp,
    markdown_table,
    mlp_apply,
    normalize,
    obs_features,
    predict,
    train_bc,
    train_transition_classifier,
)
from run_minari_tri_piql_smoke import (  # noqa: E402
    load_episode_label_scores,
    pairwise_auc,
    rank_correlation,
    split_dir_from_path,
)
from tri_piql.algos.tabular import _adam_update, _tree_zeros_like  # noqa: E402


@dataclass(frozen=True)
class StepData:
    observations: np.ndarray
    actions: np.ndarray
    next_observations: np.ndarray
    episode_ids: np.ndarray


@dataclass(frozen=True)
class IqlTrajectoryBatch:
    observations: np.ndarray
    actions: np.ndarray
    next_observations: np.ndarray
    mask: np.ndarray
    episode_ids: np.ndarray
    label_scores: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_id", help="Minari dataset id")
    parser.add_argument("--split-path", type=Path, default=None)
    parser.add_argument("--episodes-csv", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path("results/minari_tri_iql_smoke"))
    parser.add_argument("--obs-keys", nargs="+", default=["observation", "desired_goal"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--actor-steps", type=int, default=700)
    parser.add_argument("--classifier-steps", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--traj-batch-size", type=int, default=12)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--max-train-transitions", type=int, default=150_000)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--eval-horizon", type=int, default=800)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--expectile", type=float, default=0.70)
    parser.add_argument("--q-temperature", type=float, default=1.0)
    parser.add_argument("--actor-temperature", type=float, default=1.0)
    parser.add_argument("--unlabeled-good-prior", type=float, default=0.50)
    parser.add_argument("--trajectory-reduction", choices=["sum", "sqrt_len", "mean"], default="sum")
    return parser.parse_args()


def load_step_data(dataset, episode_ids: list[int], obs_keys: list[str]) -> StepData:
    obs_chunks: list[np.ndarray] = []
    next_obs_chunks: list[np.ndarray] = []
    action_chunks: list[np.ndarray] = []
    episode_chunks: list[np.ndarray] = []
    for episode in dataset.iterate_episodes(episode_indices=np.asarray(episode_ids, dtype=np.int64)):
        actions = np.asarray(episode.actions, dtype=np.float32)
        obs = np.asarray(
            [obs_features(episode.observations, obs_keys, t=t) for t in range(actions.shape[0])],
            dtype=np.float32,
        )
        next_obs = np.asarray(
            [obs_features(episode.observations, obs_keys, t=t + 1) for t in range(actions.shape[0])],
            dtype=np.float32,
        )
        obs_chunks.append(obs)
        next_obs_chunks.append(next_obs)
        action_chunks.append(actions)
        episode_chunks.append(np.full((actions.shape[0],), int(episode.id), dtype=np.int64))
    if not obs_chunks:
        raise ValueError("no transitions loaded")
    return StepData(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        next_observations=np.concatenate(next_obs_chunks, axis=0),
        episode_ids=np.concatenate(episode_chunks, axis=0),
    )


def cap_step_data(data: StepData, max_transitions: int, seed: int) -> StepData:
    if data.observations.shape[0] <= max_transitions:
        return data
    rng = np.random.default_rng(seed)
    idx = np.sort(rng.choice(data.observations.shape[0], size=max_transitions, replace=False))
    return StepData(data.observations[idx], data.actions[idx], data.next_observations[idx], data.episode_ids[idx])


def normalize_step_data(data: StepData, mean: np.ndarray, std: np.ndarray) -> StepData:
    return StepData(
        observations=(data.observations - mean) / std,
        actions=data.actions,
        next_observations=(data.next_observations - mean) / std,
        episode_ids=data.episode_ids,
    )


def load_iql_trajectory_batch(
    dataset,
    episode_ids: list[int],
    obs_keys: list[str],
    label_scores: dict[int, float],
) -> IqlTrajectoryBatch:
    raw_obs: list[np.ndarray] = []
    raw_next: list[np.ndarray] = []
    raw_actions: list[np.ndarray] = []
    ids: list[int] = []
    scores: list[float] = []
    max_len = 1
    for episode in dataset.iterate_episodes(episode_indices=np.asarray(episode_ids, dtype=np.int64)):
        actions = np.asarray(episode.actions, dtype=np.float32)
        obs = np.asarray(
            [obs_features(episode.observations, obs_keys, t=t) for t in range(actions.shape[0])],
            dtype=np.float32,
        )
        next_obs = np.asarray(
            [obs_features(episode.observations, obs_keys, t=t + 1) for t in range(actions.shape[0])],
            dtype=np.float32,
        )
        raw_obs.append(obs)
        raw_next.append(next_obs)
        raw_actions.append(actions)
        ids.append(int(episode.id))
        scores.append(float(label_scores.get(int(episode.id), np.sum(episode.rewards))))
        max_len = max(max_len, int(actions.shape[0]))
    if not raw_obs:
        raise ValueError("no trajectories loaded")

    obs_dim = raw_obs[0].shape[-1]
    action_dim = raw_actions[0].shape[-1]
    obs = np.zeros((len(raw_obs), max_len, obs_dim), dtype=np.float32)
    next_obs = np.zeros((len(raw_next), max_len, obs_dim), dtype=np.float32)
    actions = np.zeros((len(raw_actions), max_len, action_dim), dtype=np.float32)
    mask = np.zeros((len(raw_obs), max_len), dtype=np.float32)
    for i, (obs_i, next_i, actions_i) in enumerate(zip(raw_obs, raw_next, raw_actions, strict=True)):
        length = actions_i.shape[0]
        obs[i, :length] = obs_i
        next_obs[i, :length] = next_i
        actions[i, :length] = actions_i
        mask[i, :length] = 1.0
    return IqlTrajectoryBatch(
        observations=obs,
        actions=actions,
        next_observations=next_obs,
        mask=mask,
        episode_ids=np.asarray(ids, dtype=np.int64),
        label_scores=np.asarray(scores, dtype=np.float32),
    )


def normalize_iql_trajectory_batch(batch: IqlTrajectoryBatch, mean: np.ndarray, std: np.ndarray) -> IqlTrajectoryBatch:
    return IqlTrajectoryBatch(
        observations=(batch.observations - mean[:, None, :]) / std[:, None, :],
        actions=batch.actions,
        next_observations=(batch.next_observations - mean[:, None, :]) / std[:, None, :],
        mask=batch.mask,
        episode_ids=batch.episode_ids,
        label_scores=batch.label_scores,
    )


def q_apply(params, observations: jnp.ndarray, actions: jnp.ndarray) -> jnp.ndarray:
    x = jnp.concatenate([observations, actions], axis=-1)
    flat = x.reshape((-1, x.shape[-1]))
    return mlp_apply(params["q"], flat).reshape(x.shape[:-1])


def v_apply(params, observations: jnp.ndarray) -> jnp.ndarray:
    flat = observations.reshape((-1, observations.shape[-1]))
    return mlp_apply(params["v"], flat).reshape(observations.shape[:-1])


def reward_apply(params, observations: jnp.ndarray, actions: jnp.ndarray, next_observations: jnp.ndarray) -> jnp.ndarray:
    x = jnp.concatenate([observations, actions, next_observations], axis=-1)
    flat = x.reshape((-1, x.shape[-1]))
    return mlp_apply(params["reward"], flat).reshape(x.shape[:-1])


def param_l2(params) -> jnp.ndarray:
    leaves = []
    for key in ("q", "v", "reward"):
        leaves.extend(jax.tree_util.tree_leaves(params[key]))
    return sum(jnp.mean(leaf**2) for leaf in leaves) / max(1, len(leaves))


def expectile_loss(diff: jnp.ndarray, expectile: float) -> jnp.ndarray:
    weight = jnp.where(diff > 0.0, expectile, 1.0 - expectile)
    return weight * diff**2


def reduce_trajectory_rewards(rewards: jnp.ndarray, mask: jnp.ndarray, reduction: str) -> jnp.ndarray:
    lengths = jnp.sum(mask, axis=1) + 1.0e-6
    total = jnp.sum(rewards * mask, axis=1)
    if reduction == "sum":
        return total
    if reduction == "sqrt_len":
        return total / jnp.sqrt(lengths)
    if reduction == "mean":
        return total / lengths
    raise ValueError(f"unknown trajectory reduction: {reduction}")


def train_tri_iql(
    pos: StepData,
    neg: StepData,
    unl: StepData,
    pos_traj: IqlTrajectoryBatch,
    neg_traj: IqlTrajectoryBatch,
    unl_traj: IqlTrajectoryBatch,
    *,
    action_low: np.ndarray,
    action_high: np.ndarray,
    seed: int,
    steps: int,
    batch_size: int,
    traj_batch_size: int,
    hidden_dim: int,
    depth: int,
    lr: float,
    gamma: float,
    expectile: float,
    q_temperature: float,
    unlabeled_good_prior: float,
    trajectory_reduction: str,
) -> tuple[dict[str, object], list[dict[str, float]]]:
    obs_dim = pos.observations.shape[1]
    action_dim = pos.actions.shape[1]
    key = jax.random.PRNGKey(seed)
    key, q_key, v_key, r_key = jax.random.split(key, 4)
    params = {
        "q": init_mlp(q_key, obs_dim + action_dim, 1, hidden_dim, depth),
        "v": init_mlp(v_key, obs_dim, 1, hidden_dim, depth),
        "reward": init_mlp(r_key, obs_dim + action_dim + obs_dim, 1, hidden_dim, depth),
        "bias": jnp.array(0.0, dtype=jnp.float32),
    }
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))

    pos_x = jnp.asarray(pos.observations, dtype=jnp.float32)
    pos_a = jnp.asarray(pos.actions, dtype=jnp.float32)
    pos_n = jnp.asarray(pos.next_observations, dtype=jnp.float32)
    neg_x = jnp.asarray(neg.observations, dtype=jnp.float32)
    neg_a = jnp.asarray(neg.actions, dtype=jnp.float32)
    neg_n = jnp.asarray(neg.next_observations, dtype=jnp.float32)
    unl_x = jnp.asarray(unl.observations, dtype=jnp.float32)
    unl_a = jnp.asarray(unl.actions, dtype=jnp.float32)
    unl_n = jnp.asarray(unl.next_observations, dtype=jnp.float32)

    pos_to = jnp.asarray(pos_traj.observations, dtype=jnp.float32)
    pos_ta = jnp.asarray(pos_traj.actions, dtype=jnp.float32)
    pos_tn = jnp.asarray(pos_traj.next_observations, dtype=jnp.float32)
    pos_tm = jnp.asarray(pos_traj.mask, dtype=jnp.float32)
    neg_to = jnp.asarray(neg_traj.observations, dtype=jnp.float32)
    neg_ta = jnp.asarray(neg_traj.actions, dtype=jnp.float32)
    neg_tn = jnp.asarray(neg_traj.next_observations, dtype=jnp.float32)
    neg_tm = jnp.asarray(neg_traj.mask, dtype=jnp.float32)
    unl_to = jnp.asarray(unl_traj.observations, dtype=jnp.float32)
    unl_ta = jnp.asarray(unl_traj.actions, dtype=jnp.float32)
    unl_tn = jnp.asarray(unl_traj.next_observations, dtype=jnp.float32)
    unl_tm = jnp.asarray(unl_traj.mask, dtype=jnp.float32)
    low = jnp.asarray(action_low, dtype=jnp.float32)
    high = jnp.asarray(action_high, dtype=jnp.float32)
    half_batch = max(1, batch_size // 2)

    def trajectory_return(local_params, obs_b, act_b, next_b, mask_b):
        rewards = reward_apply(local_params, obs_b, act_b, next_b)
        return reduce_trajectory_rewards(rewards, mask_b, trajectory_reduction)

    def transition_losses(local_params, obs_b, act_b, next_b):
        q = q_apply(local_params, obs_b, act_b)
        v = v_apply(local_params, obs_b)
        next_v = v_apply(local_params, next_b)
        reward = reward_apply(local_params, obs_b, act_b, next_b)
        td = (q - reward - gamma * next_v) ** 2
        value = expectile_loss(jax.lax.stop_gradient(q) - v, expectile)
        adv = q - v
        return q, v, reward, adv, td, value

    def loss_fn(local_params, pos_idx, neg_idx, unl_idx, pos_eidx, neg_eidx, unl_eidx, rand_actions):
        pos_q, pos_v, pos_r, pos_adv, pos_td, pos_value = transition_losses(
            local_params, pos_x[pos_idx], pos_a[pos_idx], pos_n[pos_idx]
        )
        neg_q, neg_v, neg_r, neg_adv, neg_td, neg_value = transition_losses(
            local_params, neg_x[neg_idx], neg_a[neg_idx], neg_n[neg_idx]
        )
        unl_q, unl_v, unl_r, unl_adv, unl_td, unl_value = transition_losses(
            local_params, unl_x[unl_idx], unl_a[unl_idx], unl_n[unl_idx]
        )

        pos_ret = trajectory_return(local_params, pos_to[pos_eidx], pos_ta[pos_eidx], pos_tn[pos_eidx], pos_tm[pos_eidx])
        neg_ret = trajectory_return(local_params, neg_to[neg_eidx], neg_ta[neg_eidx], neg_tn[neg_eidx], neg_tm[neg_eidx])
        unl_ret = trajectory_return(local_params, unl_to[unl_eidx], unl_ta[unl_eidx], unl_tn[unl_eidx], unl_tm[unl_eidx])
        all_ret = jnp.concatenate([pos_ret, neg_ret, unl_ret])
        ret_mean = jax.lax.stop_gradient(jnp.mean(all_ret))
        ret_std = jax.lax.stop_gradient(jnp.std(all_ret) + 1.0e-4)
        pos_norm = (pos_ret - ret_mean) / ret_std
        neg_norm = (neg_ret - ret_mean) / ret_std
        unl_norm = (unl_ret - ret_mean) / ret_std

        rank_loss = jnp.mean(jax.nn.softplus(0.5 - pos_norm[:, None] + neg_norm[None, :]))
        q_pos = jax.nn.sigmoid((pos_norm - local_params["bias"]) / q_temperature)
        q_neg = jax.nn.sigmoid((neg_norm - local_params["bias"]) / q_temperature)
        q_unl = jnp.clip(jax.nn.sigmoid((unl_norm - local_params["bias"]) / q_temperature), 0.03, 0.97)
        q_label_loss = jnp.mean(jax.nn.softplus(-3.0 * (q_pos - 0.5))) + jnp.mean(
            jax.nn.softplus(3.0 * (q_neg - 0.5))
        )
        prior_loss = (jnp.mean(q_unl) - unlabeled_good_prior) ** 2
        entropy_loss = jnp.mean(q_unl * jnp.log(q_unl) + (1.0 - q_unl) * jnp.log(1.0 - q_unl))

        good_adv_loss = jnp.mean(jax.nn.softplus(0.15 - pos_adv))
        bad_adv_loss = jnp.mean(jax.nn.softplus(0.15 + neg_adv))
        unl_traj_q = q_apply(local_params, unl_to[unl_eidx], unl_ta[unl_eidx])
        unl_traj_v = v_apply(local_params, unl_to[unl_eidx])
        unl_traj_adv = unl_traj_q - unl_traj_v
        unl_mask = unl_tm[unl_eidx]
        q_stop = jax.lax.stop_gradient(q_unl)[:, None]
        unl_adv_loss = jnp.sum(
            (
                q_stop * jax.nn.softplus(0.10 - unl_traj_adv)
                + (1.0 - q_stop) * jax.nn.softplus(0.10 + unl_traj_adv)
            )
            * unl_mask
        ) / (jnp.sum(unl_mask) + 1.0e-6)
        adv_loss = good_adv_loss + bad_adv_loss + 0.35 * unl_adv_loss

        td_loss = jnp.mean(jnp.concatenate([pos_td, neg_td, unl_td]))
        value_loss = jnp.mean(jnp.concatenate([pos_value, neg_value, unl_value]))

        support_obs = jnp.concatenate([pos_x[pos_idx[:half_batch]], unl_x[unl_idx[:half_batch]]], axis=0)
        support_act = jnp.concatenate([pos_a[pos_idx[:half_batch]], unl_a[unl_idx[:half_batch]]], axis=0)
        support_q = q_apply(local_params, support_obs, support_act)
        rand_q = q_apply(local_params, support_obs, rand_actions)
        conservative = jnp.mean(jax.nn.softplus(0.05 + rand_q - support_q))

        scale_reg = (
            jnp.mean(pos_q**2)
            + jnp.mean(neg_q**2)
            + jnp.mean(unl_q**2)
            + jnp.mean(pos_v**2)
            + jnp.mean(neg_v**2)
            + jnp.mean(unl_v**2)
            + jnp.mean(pos_r**2)
            + jnp.mean(neg_r**2)
            + jnp.mean(unl_r**2)
        )

        loss = (
            0.6 * td_loss
            + 0.5 * value_loss
            + 1.0 * rank_loss
            + 0.7 * q_label_loss
            + 1.0 * adv_loss
            + 0.10 * conservative
            + 0.20 * prior_loss
            + 0.01 * entropy_loss
            + 0.002 * scale_reg
            + 0.001 * param_l2(local_params)
        )
        metrics = {
            "loss": loss,
            "td_loss": td_loss,
            "value_loss": value_loss,
            "rank_loss": rank_loss,
            "q_label_loss": q_label_loss,
            "adv_loss": adv_loss,
            "conservative": conservative,
            "prior_loss": prior_loss,
            "q_pos": jnp.mean(q_pos),
            "q_neg": jnp.mean(q_neg),
            "q_unl": jnp.mean(q_unl),
            "pos_adv": jnp.mean(pos_adv),
            "neg_adv": jnp.mean(neg_adv),
            "unl_adv": jnp.mean(unl_adv),
            "pos_reward": jnp.mean(pos_r),
            "neg_reward": jnp.mean(neg_r),
            "unl_reward": jnp.mean(unl_r),
            "pos_return": jnp.mean(pos_ret),
            "neg_return": jnp.mean(neg_ret),
        }
        return loss, metrics

    grad_fn = jax.value_and_grad(loss_fn, has_aux=True)

    @jax.jit
    def train_step(local_params, local_opt_state, local_key, local_step):
        keys = jax.random.split(local_key, 8)
        next_key = keys[0]
        pos_idx = jax.random.randint(keys[1], (batch_size,), minval=0, maxval=pos_x.shape[0])
        neg_idx = jax.random.randint(keys[2], (batch_size,), minval=0, maxval=neg_x.shape[0])
        unl_idx = jax.random.randint(keys[3], (batch_size,), minval=0, maxval=unl_x.shape[0])
        pos_eidx = jax.random.randint(keys[4], (traj_batch_size,), minval=0, maxval=pos_to.shape[0])
        neg_eidx = jax.random.randint(keys[5], (traj_batch_size,), minval=0, maxval=neg_to.shape[0])
        unl_eidx = jax.random.randint(keys[6], (traj_batch_size,), minval=0, maxval=unl_to.shape[0])
        rand_actions = jax.random.uniform(keys[7], (2 * half_batch, action_dim), minval=low, maxval=high)
        (_, metrics), grads = grad_fn(
            local_params, pos_idx, neg_idx, unl_idx, pos_eidx, neg_eidx, unl_eidx, rand_actions
        )
        local_params, local_opt_state = _adam_update(local_params, grads, local_opt_state, lr, local_step)
        return local_params, local_opt_state, next_key, metrics

    history: list[dict[str, float]] = []
    for step_id in range(1, steps + 1):
        params, opt_state, key, metrics = train_step(params, opt_state, key, jnp.asarray(step_id, dtype=jnp.float32))
        if step_id == 1 or step_id % max(1, steps // 5) == 0 or step_id == steps:
            history.append({"step": step_id, **{k: float(v) for k, v in metrics.items()}})
    return params, history


def predict_q_v(params, observations: np.ndarray, actions: np.ndarray, batch_size: int = 65_536) -> tuple[np.ndarray, np.ndarray]:
    q_values = []
    v_values = []
    for start in range(0, observations.shape[0], batch_size):
        obs_b = jnp.asarray(observations[start : start + batch_size], dtype=jnp.float32)
        act_b = jnp.asarray(actions[start : start + batch_size], dtype=jnp.float32)
        q_values.append(np.asarray(q_apply(params, obs_b, act_b)).reshape(-1))
        v_values.append(np.asarray(v_apply(params, obs_b)).reshape(-1))
    return np.concatenate(q_values, axis=0), np.concatenate(v_values, axis=0)


def predict_rewards(
    params,
    observations: np.ndarray,
    actions: np.ndarray,
    next_observations: np.ndarray,
    batch_size: int = 65_536,
) -> np.ndarray:
    rewards = []
    for start in range(0, observations.shape[0], batch_size):
        obs_b = jnp.asarray(observations[start : start + batch_size], dtype=jnp.float32)
        act_b = jnp.asarray(actions[start : start + batch_size], dtype=jnp.float32)
        next_b = jnp.asarray(next_observations[start : start + batch_size], dtype=jnp.float32)
        rewards.append(np.asarray(reward_apply(params, obs_b, act_b, next_b)).reshape(-1))
    return np.concatenate(rewards, axis=0)


def trajectory_reward_returns(params, batch: IqlTrajectoryBatch, reduction: str, episode_batch_size: int = 64) -> np.ndarray:
    out = []
    for start in range(0, batch.observations.shape[0], episode_batch_size):
        obs_b = batch.observations[start : start + episode_batch_size]
        act_b = batch.actions[start : start + episode_batch_size]
        next_b = batch.next_observations[start : start + episode_batch_size]
        mask_b = batch.mask[start : start + episode_batch_size]
        rewards = predict_rewards(
            params,
            obs_b.reshape((-1, obs_b.shape[-1])),
            act_b.reshape((-1, act_b.shape[-1])),
            next_b.reshape((-1, next_b.shape[-1])),
        ).reshape(mask_b.shape)
        lengths = mask_b.sum(axis=1) + 1.0e-6
        total = (rewards * mask_b).sum(axis=1)
        if reduction == "sum":
            out.append(total)
        elif reduction == "sqrt_len":
            out.append(total / np.sqrt(lengths))
        elif reduction == "mean":
            out.append(total / lengths)
        else:
            raise ValueError(f"unknown trajectory reduction: {reduction}")
    return np.concatenate(out, axis=0)


def build_iql_actor_weights(
    params,
    pos: StepData,
    neg: StepData,
    unl: StepData,
    unl_q_by_episode: dict[int, float],
    actor_temperature: float,
    normalize_advantage: bool,
    unlabeled_q_threshold: float | None = None,
    drop_unlabeled: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    pos_q, pos_v = predict_q_v(params, pos.observations, pos.actions)
    neg_q, neg_v = predict_q_v(params, neg.observations, neg.actions)
    unl_q_value, unl_v = predict_q_v(params, unl.observations, unl.actions)
    pos_adv = pos_q - pos_v
    neg_adv = neg_q - neg_v
    unl_adv = unl_q_value - unl_v
    if normalize_advantage:
        ref = pos_adv if drop_unlabeled else np.concatenate([pos_adv, unl_adv], axis=0)
        adv_mean = float(ref.mean())
        adv_std = float(ref.std() + 1.0e-6)
        pos_weight_adv = (pos_adv - adv_mean) / adv_std
        unl_weight_adv = (unl_adv - adv_mean) / adv_std
    else:
        adv_mean = 0.0
        adv_std = 1.0
        pos_weight_adv = pos_adv
        unl_weight_adv = unl_adv
    pos_w = np.exp(np.clip(pos_weight_adv / actor_temperature, -2.0, 2.0)).astype(np.float32)
    neg_w = np.zeros((neg.actions.shape[0],), dtype=np.float32)
    unl_q = np.asarray([unl_q_by_episode.get(int(eid), 0.0) for eid in unl.episode_ids], dtype=np.float32)
    unl_w = (unl_q * np.exp(np.clip(unl_weight_adv / actor_temperature, -2.0, 2.0))).astype(np.float32)
    if unlabeled_q_threshold is not None:
        unl_w = np.where(unl_q >= unlabeled_q_threshold, unl_w, 0.0).astype(np.float32)
    if drop_unlabeled:
        unl_w = np.zeros_like(unl_w)
    weights = np.concatenate([pos_w, neg_w, unl_w], axis=0)
    observations = np.concatenate([pos.observations, neg.observations, unl.observations], axis=0)
    actions = np.concatenate([pos.actions, neg.actions, unl.actions], axis=0)
    diagnostics = {
        "pos_adv_mean": float(pos_adv.mean()),
        "neg_adv_mean": float(neg_adv.mean()),
        "unlabeled_adv_mean": float(unl_adv.mean()),
        "pos_q_mean": float(pos_q.mean()),
        "neg_q_mean": float(neg_q.mean()),
        "unlabeled_q_value_mean": float(unl_q_value.mean()),
        "adv_weight_mean": adv_mean,
        "adv_weight_std": adv_std,
        "pos_actor_weight_mean": float(pos_w.mean()),
        "unlabeled_actor_weight_mean": float(unl_w.mean()),
        "unlabeled_kept_frac": float(np.mean(unl_w > 1.0e-6)),
        "unlabeled_q_threshold": None if unlabeled_q_threshold is None else float(unlabeled_q_threshold),
        "drop_unlabeled": bool(drop_unlabeled),
        "nonzero_weight_frac": float(np.mean(weights > 1.0e-6)),
    }
    return observations, actions, weights, diagnostics


def main() -> None:
    args = parse_args()
    import minari

    split_path = args.split_path or default_split_path(args.dataset_id)
    episodes_csv = args.episodes_csv or (split_dir_from_path(split_path) / "episodes.csv")
    split = json.loads(split_path.read_text(encoding="utf-8"))
    label_scores = load_episode_label_scores(episodes_csv)
    dataset = minari.load_dataset(args.dataset_id)

    pos_raw = load_step_data(dataset, split["positive_ids"], args.obs_keys)
    neg_raw = load_step_data(dataset, split["negative_ids"], args.obs_keys)
    unl_raw = load_step_data(dataset, split["unlabeled_ids"], args.obs_keys)
    all_train_x = np.concatenate([pos_raw.observations, neg_raw.observations, unl_raw.observations], axis=0)
    obs_mean, obs_std, _ = normalize(all_train_x, all_train_x)
    pos = cap_step_data(normalize_step_data(pos_raw, obs_mean, obs_std), args.max_train_transitions, args.seed)
    neg = cap_step_data(normalize_step_data(neg_raw, obs_mean, obs_std), args.max_train_transitions, args.seed + 1)
    unl = cap_step_data(normalize_step_data(unl_raw, obs_mean, obs_std), args.max_train_transitions, args.seed + 2)

    pos_traj = normalize_iql_trajectory_batch(
        load_iql_trajectory_batch(dataset, split["positive_ids"], args.obs_keys, label_scores), obs_mean, obs_std
    )
    neg_traj = normalize_iql_trajectory_batch(
        load_iql_trajectory_batch(dataset, split["negative_ids"], args.obs_keys, label_scores), obs_mean, obs_std
    )
    unl_traj = normalize_iql_trajectory_batch(
        load_iql_trajectory_batch(dataset, split["unlabeled_ids"], args.obs_keys, label_scores), obs_mean, obs_std
    )

    action_low = np.asarray(dataset.action_space.low, dtype=np.float32)
    action_high = np.asarray(dataset.action_space.high, dtype=np.float32)

    pos_bc = TransitionData(pos.observations, pos.actions, pos.episode_ids)
    neg_bc = TransitionData(neg.observations, neg.actions, neg.episode_ids)
    unl_bc = TransitionData(unl.observations, unl.actions, unl.episode_ids)
    classifier, classifier_history = train_transition_classifier(
        pos.observations,
        neg.observations,
        seed=args.seed + 101,
        steps=args.classifier_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )
    pos_prob = np.asarray(jax.nn.sigmoid(jnp.asarray(predict(classifier, pos.observations).reshape(-1))))
    neg_prob = np.asarray(jax.nn.sigmoid(jnp.asarray(predict(classifier, neg.observations).reshape(-1))))
    unl_prob = np.asarray(jax.nn.sigmoid(jnp.asarray(predict(classifier, unl.observations).reshape(-1))))
    classifier_metrics = {
        "pos_prob_mean": float(pos_prob.mean()),
        "neg_prob_mean": float(neg_prob.mean()),
        "unlabeled_prob_mean": float(unl_prob.mean()),
        "labeled_accuracy": float(0.5 * ((pos_prob > 0.5).mean() + (neg_prob < 0.5).mean())),
    }

    iql_params, iql_history = train_tri_iql(
        pos,
        neg,
        unl,
        pos_traj,
        neg_traj,
        unl_traj,
        action_low=action_low,
        action_high=action_high,
        seed=args.seed + 202,
        steps=args.steps,
        batch_size=args.batch_size,
        traj_batch_size=args.traj_batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
        gamma=args.gamma,
        expectile=args.expectile,
        q_temperature=args.q_temperature,
        unlabeled_good_prior=args.unlabeled_good_prior,
        trajectory_reduction=args.trajectory_reduction,
    )

    pos_returns = trajectory_reward_returns(iql_params, pos_traj, args.trajectory_reduction)
    neg_returns = trajectory_reward_returns(iql_params, neg_traj, args.trajectory_reduction)
    unl_returns = trajectory_reward_returns(iql_params, unl_traj, args.trajectory_reduction)
    all_returns = np.concatenate([pos_returns, neg_returns, unl_returns])
    ret_mean = all_returns.mean()
    ret_std = all_returns.std() + 1.0e-4
    q_bias = float(iql_params["bias"])
    q_pos = 1.0 / (1.0 + np.exp(-(((pos_returns - ret_mean) / ret_std) - q_bias) / args.q_temperature))
    q_neg = 1.0 / (1.0 + np.exp(-(((neg_returns - ret_mean) / ret_std) - q_bias) / args.q_temperature))
    q_unl = np.clip(
        1.0 / (1.0 + np.exp(-(((unl_returns - ret_mean) / ret_std) - q_bias) / args.q_temperature)), 0.03, 0.97
    )
    unl_q_by_episode = {int(eid): float(q) for eid, q in zip(unl_traj.episode_ids, q_unl, strict=True)}

    raw_x, raw_a, raw_w, raw_weight_diag = build_iql_actor_weights(
        iql_params,
        pos,
        neg,
        unl,
        unl_q_by_episode,
        args.actor_temperature,
        normalize_advantage=False,
    )
    norm_x, norm_a, norm_w, norm_weight_diag = build_iql_actor_weights(
        iql_params,
        pos,
        neg,
        unl,
        unl_q_by_episode,
        args.actor_temperature,
        normalize_advantage=True,
    )
    topq_threshold = float(np.quantile(q_unl, 0.75))
    topq_x, topq_a, topq_w, topq_weight_diag = build_iql_actor_weights(
        iql_params,
        pos,
        neg,
        unl,
        unl_q_by_episode,
        args.actor_temperature,
        normalize_advantage=True,
        unlabeled_q_threshold=topq_threshold,
    )
    pos_only_x, pos_only_a, pos_only_w, pos_only_weight_diag = build_iql_actor_weights(
        iql_params,
        pos,
        neg,
        unl,
        unl_q_by_episode,
        args.actor_temperature,
        normalize_advantage=True,
        drop_unlabeled=True,
    )

    weighted_bc_x = np.concatenate([pos.observations, neg.observations, unl.observations], axis=0)
    weighted_bc_a = np.concatenate([pos.actions, neg.actions, unl.actions], axis=0)
    weighted_bc_w = np.concatenate(
        [
            np.ones((pos.actions.shape[0],), dtype=np.float32),
            np.zeros((neg.actions.shape[0],), dtype=np.float32),
            unl_prob.astype(np.float32),
        ],
        axis=0,
    )

    q_diag = {
        "q_pos_mean": float(q_pos.mean()),
        "q_neg_mean": float(q_neg.mean()),
        "q_unlabeled_mean": float(q_unl.mean()),
        "pos_neg_auc": pairwise_auc(q_pos, q_neg),
        "rank_gap": float(pos_returns.mean() - neg_returns.mean()),
        "unlabeled_q_label_score_spearman": rank_correlation(q_unl, unl_traj.label_scores),
        "unlabeled_q_top_quartile_mean": float(q_unl[unl_traj.label_scores >= np.quantile(unl_traj.label_scores, 0.75)].mean()),
        "unlabeled_q_bottom_quartile_mean": float(
            q_unl[unl_traj.label_scores <= np.quantile(unl_traj.label_scores, 0.25)].mean()
        ),
        "q_bias": q_bias,
        "raw_adv_weights": raw_weight_diag,
        "normalized_adv_weights": norm_weight_diag,
        "topq_normalized_adv_weights": topq_weight_diag,
        "positive_only_normalized_adv_weights": pos_only_weight_diag,
    }

    train_sets = {
        "bc_positive": (
            pos_bc.observations,
            pos_bc.actions,
            np.ones((pos_bc.actions.shape[0],), dtype=np.float32),
        ),
        "weighted_bc_classifier": (weighted_bc_x, weighted_bc_a, weighted_bc_w),
        "tri_iql_awbc_raw": (raw_x, raw_a, raw_w),
        "tri_iql_awbc_norm": (norm_x, norm_a, norm_w),
        "tri_iql_awbc_topq": (topq_x, topq_a, topq_w),
        "tri_iql_awbc_pos_only": (pos_only_x, pos_only_a, pos_only_w),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    metrics = []
    histories = {"classifier": classifier_history, "tri_iql": iql_history}
    for i, (method, (x, actions, weights)) in enumerate(train_sets.items()):
        actor_params, history = train_bc(
            x,
            actions,
            weights,
            seed=args.seed + 300 + i,
            steps=args.actor_steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
        )
        histories[method] = history
        row = evaluate_policy(dataset, actor_params, obs_mean, obs_std, args.obs_keys, args, method)
        metrics.append(row)
        print(
            f"{method}: success={row['success_rate']:.3f} "
            f"return={row['avg_return']:.3f} len={row['avg_len']:.1f}"
        )

    metrics_path = args.out_dir / "metrics.csv"
    with metrics_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "success_rate", "avg_return", "avg_len"])
        writer.writeheader()
        writer.writerows(metrics)

    diagnostics = {
        "dataset_id": args.dataset_id,
        "split_path": str(split_path),
        "episodes_csv": str(episodes_csv),
        "obs_keys": args.obs_keys,
        "seed": args.seed,
        "steps": args.steps,
        "actor_steps": args.actor_steps,
        "classifier_steps": args.classifier_steps,
        "eval_episodes": args.eval_episodes,
        "eval_horizon": args.eval_horizon,
        "gamma": args.gamma,
        "expectile": args.expectile,
        "trajectory_reduction": args.trajectory_reduction,
        "transition_counts": {
            "positive": int(pos.actions.shape[0]),
            "negative": int(neg.actions.shape[0]),
            "unlabeled": int(unl.actions.shape[0]),
        },
        "trajectory_counts": {
            "positive": int(pos_traj.observations.shape[0]),
            "negative": int(neg_traj.observations.shape[0]),
            "unlabeled": int(unl_traj.observations.shape[0]),
            "max_len": int(max(pos_traj.observations.shape[1], neg_traj.observations.shape[1], unl_traj.observations.shape[1])),
        },
        "classifier": classifier_metrics,
        "tri_iql": q_diag,
        "histories": histories,
    }
    diagnostics_path = args.out_dir / "diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report_path = args.out_dir / "REPORT.md"
    report_path.write_text(
        "\n".join(
            [
                f"# Minari Tri-PIQL IQL Smoke: `{args.dataset_id}`",
                "",
                f"Split path: `{split_path}`.",
                f"Observation keys: `{args.obs_keys}`.",
                f"IQL/reward steps: `{args.steps}`.",
                f"Actor steps: `{args.actor_steps}`.",
                f"Classifier steps: `{args.classifier_steps}`.",
                f"Evaluation episodes: `{args.eval_episodes}`.",
                f"Trajectory reduction: `{args.trajectory_reduction}`.",
                "",
                "## Metrics",
                "",
                markdown_table(metrics),
                "",
                "## V/Q Diagnostics",
                "",
                f"- Learned q pos/neg/unlabeled mean: `{q_diag['q_pos_mean']:.3f}` / `{q_diag['q_neg_mean']:.3f}` / `{q_diag['q_unlabeled_mean']:.3f}`.",
                f"- Positive-vs-negative q AUC: `{q_diag['pos_neg_auc']:.3f}`.",
                f"- Learned reward trajectory gap: `{q_diag['rank_gap']:.3f}`.",
                f"- Unlabeled q vs label-score Spearman: `{q_diag['unlabeled_q_label_score_spearman']:.3f}`.",
                f"- Raw advantage pos/neg/unlabeled mean: `{raw_weight_diag['pos_adv_mean']:.3f}` / `{raw_weight_diag['neg_adv_mean']:.3f}` / `{raw_weight_diag['unlabeled_adv_mean']:.3f}`.",
                f"- Normalized actor weight pos/unlabeled mean: `{norm_weight_diag['pos_actor_weight_mean']:.3f}` / `{norm_weight_diag['unlabeled_actor_weight_mean']:.3f}`.",
                f"- Top-q actor threshold/kept fraction: `{topq_threshold:.3f}` / `{topq_weight_diag['unlabeled_kept_frac']:.3f}`.",
                "",
                "## Classifier Baseline Diagnostics",
                "",
                f"- Labeled accuracy: `{classifier_metrics['labeled_accuracy']:.3f}`.",
                f"- Positive/negative/unlabeled probability mean: `{classifier_metrics['pos_prob_mean']:.3f}` / `{classifier_metrics['neg_prob_mean']:.3f}` / `{classifier_metrics['unlabeled_prob_mean']:.3f}`.",
                "",
                "## Interpretation",
                "",
                "- This is a bounded real-data smoke for adding IQL-style V/Q structure to Tri-PIQL.",
                "- `tri_iql_awbc_raw` uses raw Q-V advantages; `tri_iql_awbc_norm` normalizes advantages before actor weighting.",
                "- `tri_iql_awbc_topq` keeps only top-quartile unlabeled trajectories by learned q; `tri_iql_awbc_pos_only` tests whether the advantage model helps without unlabeled data.",
                "- The relevant comparison is against BC-positive and classifier-weighted BC under the same split and rollout budget.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
