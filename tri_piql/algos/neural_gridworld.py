from __future__ import annotations

from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np

from tri_piql.algos.tabular import (
    TriPiqlResult,
    _adam_update,
    _flatten_transitions,
    _pairwise_auc,
    _soft_value_iteration,
    _traj_returns,
    _tree_zeros_like,
)
from tri_piql.envs.gridworld import GridSpec, transition_tables


@dataclass(frozen=True)
class NeuralConfig:
    hidden_dim: int = 64
    depth: int = 2
    lr: float = 3.0e-3
    gamma: float = 0.97
    vi_tau: float = 0.2
    vi_iterations: int = 60
    q_temperature: float = 0.8
    unlabeled_good_prior: float = 0.35
    feature_mode: str = "coords"


def state_action_features(spec: GridSpec, mode: str = "coords") -> np.ndarray:
    features = []
    for state in range(spec.num_states):
        x = state % spec.width
        y = state // spec.width
        x_norm = 2.0 * x / max(1, spec.width - 1) - 1.0
        y_norm = 2.0 * y / max(1, spec.height - 1) - 1.0
        for action in range(spec.num_actions):
            action_onehot = np.eye(spec.num_actions, dtype=np.float32)[action]
            if mode == "onehot":
                state_onehot = np.eye(spec.num_states, dtype=np.float32)[state]
                feat = np.concatenate([state_onehot, action_onehot])
            elif mode == "coords":
                next_xy = np.array([x, y], dtype=np.float32)
                if action == 0:
                    next_xy[1] = max(0.0, next_xy[1] - 1.0)
                elif action == 1:
                    next_xy[0] = min(float(spec.width - 1), next_xy[0] + 1.0)
                elif action == 2:
                    next_xy[1] = min(float(spec.height - 1), next_xy[1] + 1.0)
                elif action == 3:
                    next_xy[0] = max(0.0, next_xy[0] - 1.0)
                next_x = 2.0 * next_xy[0] / max(1, spec.width - 1) - 1.0
                next_y = 2.0 * next_xy[1] / max(1, spec.height - 1) - 1.0
                terminal_hint = float((int(next_xy[0]), int(next_xy[1])) in {spec.goal, spec.trap})
                feat = np.concatenate(
                    [
                        np.array([x_norm, y_norm, next_x, next_y, terminal_hint], dtype=np.float32),
                        action_onehot,
                    ]
                )
            else:
                raise ValueError(f"unknown feature mode: {mode}")
            features.append(feat)
    return np.asarray(features, dtype=np.float32).reshape(spec.num_states, spec.num_actions, -1)


def _init_mlp(key: jax.Array, input_dim: int, hidden_dim: int, depth: int):
    sizes = [input_dim] + [hidden_dim] * depth + [1]
    keys = jax.random.split(key, len(sizes) - 1)
    layers = []
    for i, (fan_in, fan_out) in enumerate(zip(sizes[:-1], sizes[1:], strict=True)):
        scale = 0.7 / np.sqrt(fan_in) if i < len(sizes) - 2 else 0.05 / np.sqrt(fan_in)
        layers.append(
            {
                "w": scale * jax.random.normal(keys[i], (fan_in, fan_out), dtype=jnp.float32),
                "b": jnp.zeros((fan_out,), dtype=jnp.float32),
            }
        )
    return layers


def _mlp_apply(layers, features: jnp.ndarray) -> jnp.ndarray:
    x = features.reshape((-1, features.shape[-1]))
    for layer in layers[:-1]:
        x = jnp.tanh(x @ layer["w"] + layer["b"])
    out = x @ layers[-1]["w"] + layers[-1]["b"]
    return out.reshape(features.shape[:2])


def _param_l2(params) -> jnp.ndarray:
    leaves = jax.tree_util.tree_leaves(params["reward_mlp"])
    return sum(jnp.mean(leaf**2) for leaf in leaves) / max(1, len(leaves))


def train_neural_gridworld_tri_piql(
    spec: GridSpec,
    pos_batch: dict[str, np.ndarray],
    neg_batch: dict[str, np.ndarray],
    unlabeled_batch: dict[str, np.ndarray],
    unlabeled_latent_good: np.ndarray,
    seed: int,
    steps: int = 1000,
    config: NeuralConfig | None = None,
    log_every: int = 100,
) -> TriPiqlResult:
    if config is None:
        config = NeuralConfig()

    features_np = state_action_features(spec, config.feature_mode)
    features = jnp.asarray(features_np)
    key = jax.random.PRNGKey(seed)
    params = {
        "reward_mlp": _init_mlp(key, features.shape[-1], config.hidden_dim, config.depth),
        "bias": jnp.array(0.0, dtype=jnp.float32),
    }
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))

    next_states_np, terminal_np, state_terminal_np = transition_tables(spec)
    next_states = jnp.asarray(next_states_np)
    terminal = jnp.asarray(terminal_np)
    state_terminal = jnp.asarray(state_terminal_np)
    pos = {k: jnp.asarray(v) for k, v in pos_batch.items() if k != "true_returns"}
    neg = {k: jnp.asarray(v) for k, v in neg_batch.items() if k != "true_returns"}
    unl = {k: jnp.asarray(v) for k, v in unlabeled_batch.items() if k != "true_returns"}
    pos_s, pos_a, pos_m = _flatten_transitions(pos)
    neg_s, neg_a, neg_m = _flatten_transitions(neg)
    unl_s, unl_a, unl_m = _flatten_transitions(unl)
    unl_traj_mask = unl["mask"]

    def loss_fn(local_params):
        local_reward = _mlp_apply(local_params["reward_mlp"], features)
        q_values, values = _soft_value_iteration(
            local_reward,
            next_states,
            terminal,
            state_terminal,
            config.gamma,
            config.vi_tau,
            config.vi_iterations,
        )
        del values
        advantages = q_values - jnp.mean(q_values, axis=1, keepdims=True)

        pos_returns = _traj_returns(local_reward, pos)
        neg_returns = _traj_returns(local_reward, neg)
        unl_returns = _traj_returns(local_reward, unl)
        all_returns = jnp.concatenate([pos_returns, neg_returns, unl_returns])
        returns_mean = jax.lax.stop_gradient(jnp.mean(all_returns))
        returns_std = jax.lax.stop_gradient(jnp.std(all_returns) + 1.0e-4)
        pos_norm = (pos_returns - returns_mean) / returns_std
        neg_norm = (neg_returns - returns_mean) / returns_std
        unl_norm = (unl_returns - returns_mean) / returns_std

        rank_loss = jnp.mean(jax.nn.softplus(0.6 - pos_norm[:, None] + neg_norm[None, :]))
        q_pos = jax.nn.sigmoid((pos_norm - local_params["bias"]) / config.q_temperature)
        q_neg = jax.nn.sigmoid((neg_norm - local_params["bias"]) / config.q_temperature)
        q_unl = jnp.clip(
            jax.nn.sigmoid((unl_norm - local_params["bias"]) / config.q_temperature), 0.03, 0.97
        )
        q_label_loss = jnp.mean(jax.nn.softplus(-3.0 * (q_pos - 0.5))) + jnp.mean(
            jax.nn.softplus(3.0 * (q_neg - 0.5))
        )
        prior_loss = (jnp.mean(q_unl) - config.unlabeled_good_prior) ** 2
        entropy_loss = jnp.mean(q_unl * jnp.log(q_unl) + (1.0 - q_unl) * jnp.log(1.0 - q_unl))

        pos_adv = advantages[pos_s, pos_a]
        neg_adv = advantages[neg_s, neg_a]
        unl_adv = advantages[unl_s, unl_a].reshape(unl["mask"].shape)
        good_adv_loss = jnp.sum(jax.nn.softplus(0.15 - pos_adv) * pos_m) / jnp.sum(pos_m)
        bad_adv_loss = jnp.sum(jax.nn.softplus(0.15 + neg_adv) * neg_m) / jnp.sum(neg_m)
        q_stop = jax.lax.stop_gradient(q_unl)[:, None]
        unl_signed_loss = jnp.sum(
            (
                q_stop * jax.nn.softplus(0.10 - unl_adv)
                + (1.0 - q_stop) * jax.nn.softplus(0.10 + unl_adv)
            )
            * unl_traj_mask
        ) / jnp.sum(unl_traj_mask)
        adv_loss = good_adv_loss + bad_adv_loss + 0.35 * unl_signed_loss

        dataset_s = jnp.concatenate([pos_s, unl_s])
        dataset_a = jnp.concatenate([pos_a, unl_a])
        dataset_m = jnp.concatenate([pos_m, unl_m])
        conservative = jnp.sum(
            (jax.nn.logsumexp(q_values[dataset_s], axis=1) - q_values[dataset_s, dataset_a])
            * dataset_m
        ) / jnp.sum(dataset_m)
        reward_l2 = jnp.mean(local_reward**2)

        loss = (
            1.2 * rank_loss
            + 0.8 * q_label_loss
            + 1.0 * adv_loss
            + 0.10 * conservative
            + 0.20 * prior_loss
            + 0.02 * entropy_loss
            + 0.01 * reward_l2
            + 0.002 * _param_l2(local_params)
        )
        metrics = {
            "loss": loss,
            "rank_loss": rank_loss,
            "q_label_loss": q_label_loss,
            "adv_loss": adv_loss,
            "conservative": conservative,
            "reward_l2": reward_l2,
            "prior_loss": prior_loss,
            "q_pos": jnp.mean(q_pos),
            "q_neg": jnp.mean(q_neg),
            "q_unl": jnp.mean(q_unl),
            "pos_return": jnp.mean(pos_returns),
            "neg_return": jnp.mean(neg_returns),
            "good_adv": jnp.sum(pos_adv * pos_m) / jnp.sum(pos_m),
            "bad_adv": jnp.sum(neg_adv * neg_m) / jnp.sum(neg_m),
        }
        return loss, metrics

    value_and_grad = jax.value_and_grad(loss_fn, has_aux=True)

    @jax.jit
    def train_step(local_params, local_opt_state, local_step):
        (_, local_metrics), local_grads = value_and_grad(local_params)
        local_params, local_opt_state = _adam_update(
            local_params, local_grads, local_opt_state, config.lr, local_step
        )
        return local_params, local_opt_state, local_metrics

    history: list[dict[str, float]] = []
    for step in range(1, steps + 1):
        params, opt_state, metrics = train_step(params, opt_state, jnp.asarray(step, dtype=jnp.float32))
        if step == 1 or step % log_every == 0 or step == steps:
            history.append({k: float(v) for k, v in metrics.items()})

    final_reward = np.asarray(_mlp_apply(params["reward_mlp"], features))
    q_values, values = _soft_value_iteration(
        jnp.asarray(final_reward),
        next_states,
        terminal,
        state_terminal,
        config.gamma,
        config.vi_tau,
        config.vi_iterations,
    )
    del values
    q_values_np = np.asarray(q_values)
    advantages = q_values_np - q_values_np.mean(axis=1, keepdims=True)

    pos_returns = np.asarray(_traj_returns(jnp.asarray(final_reward), pos))
    neg_returns = np.asarray(_traj_returns(jnp.asarray(final_reward), neg))
    unl_returns = np.asarray(_traj_returns(jnp.asarray(final_reward), unl))
    all_returns = np.concatenate([pos_returns, neg_returns, unl_returns])
    mean = all_returns.mean()
    std = all_returns.std() + 1.0e-4
    pos_norm = (pos_returns - mean) / std
    neg_norm = (neg_returns - mean) / std
    unl_norm = (unl_returns - mean) / std
    bias = float(params["bias"])
    q_pos = 1.0 / (1.0 + np.exp(-((pos_norm - bias) / config.q_temperature)))
    q_neg = 1.0 / (1.0 + np.exp(-((neg_norm - bias) / config.q_temperature)))
    q_unl = np.clip(1.0 / (1.0 + np.exp(-((unl_norm - bias) / config.q_temperature))), 0.03, 0.97)

    pos_mask = np.asarray(pos["mask"]).reshape(-1)
    neg_mask = np.asarray(neg["mask"]).reshape(-1)
    pos_s_np = np.asarray(pos_s)
    pos_a_np = np.asarray(pos_a)
    neg_s_np = np.asarray(neg_s)
    neg_a_np = np.asarray(neg_a)
    pos_adv = advantages[pos_s_np, pos_a_np]
    neg_adv = advantages[neg_s_np, neg_a_np]
    pos_reward_flat = final_reward[pos_s_np, pos_a_np]
    neg_reward_flat = final_reward[neg_s_np, neg_a_np]

    goal_rewards = []
    trap_rewards = []
    for state in range(spec.num_states):
        for action in range(spec.num_actions):
            ns = int(next_states_np[state, action])
            if terminal_np[state, action] > 0.5:
                xy = (ns % spec.width, ns // spec.width)
                if xy == spec.goal:
                    goal_rewards.append(final_reward[state, action])
                elif xy == spec.trap:
                    trap_rewards.append(final_reward[state, action])

    return TriPiqlResult(
        reward=final_reward,
        q_unlabeled=q_unl,
        q_pos_mean=float(q_pos.mean()),
        q_neg_mean=float(q_neg.mean()),
        q_unlabeled_mean=float(q_unl.mean()),
        q_unlabeled_hidden_good_mean=float(q_unl[unlabeled_latent_good > 0.5].mean()),
        q_unlabeled_hidden_bad_mean=float(q_unl[unlabeled_latent_good <= 0.5].mean()),
        q_unlabeled_auc=_pairwise_auc(q_unl, unlabeled_latent_good),
        pos_return_mean=float(pos_returns.mean()),
        neg_return_mean=float(neg_returns.mean()),
        rank_gap=float(pos_returns.mean() - neg_returns.mean()),
        good_adv_mean=float((pos_adv * pos_mask).sum() / pos_mask.sum()),
        bad_adv_mean=float((neg_adv * neg_mask).sum() / neg_mask.sum()),
        pos_transition_reward_mean=float((pos_reward_flat * pos_mask).sum() / pos_mask.sum()),
        neg_transition_reward_mean=float((neg_reward_flat * neg_mask).sum() / neg_mask.sum()),
        goal_transition_reward_mean=float(np.mean(goal_rewards)),
        trap_transition_reward_mean=float(np.mean(trap_rewards)),
        loss_history=history,
    )
