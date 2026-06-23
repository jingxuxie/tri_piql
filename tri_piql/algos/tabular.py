from __future__ import annotations

from dataclasses import dataclass

import jax
import jax.numpy as jnp
import numpy as np

from tri_piql.envs.gridworld import GridSpec, Trajectory, transition_tables


def softplus_np(x: np.ndarray) -> np.ndarray:
    return np.logaddexp(x, 0.0)


def fit_tabular_bc(
    spec: GridSpec,
    trajectories: list[Trajectory],
    weights: np.ndarray | None = None,
    alpha: float = 0.05,
) -> np.ndarray:
    counts = np.full((spec.num_states, spec.num_actions), alpha, dtype=np.float64)
    if weights is None:
        weights = np.ones((len(trajectories),), dtype=np.float64)
    for traj, weight in zip(trajectories, weights, strict=True):
        if weight <= 0.0:
            continue
        for state, action in zip(traj.states, traj.actions, strict=True):
            counts[int(state), int(action)] += float(weight)
    return counts / counts.sum(axis=1, keepdims=True)


def fit_transition_weighted_bc(
    spec: GridSpec,
    trajectories: list[Trajectory],
    transition_weights: list[np.ndarray],
    alpha: float = 0.05,
) -> np.ndarray:
    counts = np.full((spec.num_states, spec.num_actions), alpha, dtype=np.float64)
    for traj, weights in zip(trajectories, transition_weights, strict=True):
        for state, action, weight in zip(traj.states, traj.actions, weights, strict=True):
            if weight > 0.0:
                counts[int(state), int(action)] += float(weight)
    return counts / counts.sum(axis=1, keepdims=True)


def greedy_policy_from_probs(probs: np.ndarray):
    def policy(state: int) -> int:
        return int(np.argmax(probs[int(state)]))

    return policy


def trajectory_features(spec: GridSpec, trajectories: list[Trajectory]) -> np.ndarray:
    dim = spec.num_states + spec.num_actions + spec.num_states + 1
    feats = np.zeros((len(trajectories), dim), dtype=np.float64)
    for i, traj in enumerate(trajectories):
        state_counts = np.bincount(traj.states, minlength=spec.num_states).astype(np.float64)
        action_counts = np.bincount(traj.actions, minlength=spec.num_actions).astype(np.float64)
        if state_counts.sum() > 0:
            state_counts /= state_counts.sum()
        if action_counts.sum() > 0:
            action_counts /= action_counts.sum()
        final_onehot = np.zeros((spec.num_states,), dtype=np.float64)
        final_onehot[int(traj.next_states[-1])] = 1.0
        length_frac = traj.length / spec.max_steps
        feats[i] = np.concatenate(
            [state_counts, action_counts, final_onehot, [length_frac]]
        )
    return feats


@dataclass
class ClassifierResult:
    q_unlabeled: np.ndarray
    labeled_accuracy: float
    pos_prob_mean: float
    neg_prob_mean: float
    unlabeled_prob_mean: float


def fit_desirability_classifier(
    spec: GridSpec,
    positives: list[Trajectory],
    negatives: list[Trajectory],
    unlabeled: list[Trajectory],
    steps: int = 500,
    lr: float = 0.3,
    l2: float = 1.0e-3,
) -> ClassifierResult:
    labeled = positives + negatives
    x = trajectory_features(spec, labeled)
    y = np.concatenate([np.ones(len(positives)), np.zeros(len(negatives))])
    mean = x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True) + 1.0e-6
    x_norm = (x - mean) / std

    weights = np.zeros((x_norm.shape[1],), dtype=np.float64)
    bias = 0.0
    for _ in range(steps):
        logits = x_norm @ weights + bias
        probs = 1.0 / (1.0 + np.exp(-logits))
        err = probs - y
        grad_w = x_norm.T @ err / len(y) + l2 * weights
        grad_b = float(err.mean())
        weights -= lr * grad_w
        bias -= lr * grad_b

    labeled_probs = 1.0 / (1.0 + np.exp(-(x_norm @ weights + bias)))
    pred = labeled_probs >= 0.5
    acc = float(np.mean(pred == (y > 0.5)))

    xu = trajectory_features(spec, unlabeled)
    xu_norm = (xu - mean) / std
    q = 1.0 / (1.0 + np.exp(-(xu_norm @ weights + bias)))
    return ClassifierResult(
        q_unlabeled=q.astype(np.float64),
        labeled_accuracy=acc,
        pos_prob_mean=float(labeled_probs[: len(positives)].mean()),
        neg_prob_mean=float(labeled_probs[len(positives) :].mean()),
        unlabeled_prob_mean=float(q.mean()),
    )


@dataclass
class TriPiqlResult:
    reward: np.ndarray
    q_unlabeled: np.ndarray
    q_pos_mean: float
    q_neg_mean: float
    q_unlabeled_mean: float
    q_unlabeled_hidden_good_mean: float
    q_unlabeled_hidden_bad_mean: float
    q_unlabeled_auc: float
    pos_return_mean: float
    neg_return_mean: float
    rank_gap: float
    good_adv_mean: float
    bad_adv_mean: float
    pos_transition_reward_mean: float
    neg_transition_reward_mean: float
    goal_transition_reward_mean: float
    trap_transition_reward_mean: float
    loss_history: list[dict[str, float]]


def _adam_update(params, grads, opt_state, lr: float, step: int):
    beta1 = 0.9
    beta2 = 0.999
    eps = 1.0e-8
    m, v = opt_state
    m = jax.tree_util.tree_map(lambda old, g: beta1 * old + (1.0 - beta1) * g, m, grads)
    v = jax.tree_util.tree_map(lambda old, g: beta2 * old + (1.0 - beta2) * (g * g), v, grads)
    m_hat = jax.tree_util.tree_map(lambda val: val / (1.0 - beta1**step), m)
    v_hat = jax.tree_util.tree_map(lambda val: val / (1.0 - beta2**step), v)
    params = jax.tree_util.tree_map(
        lambda p, mh, vh: p - lr * mh / (jnp.sqrt(vh) + eps), params, m_hat, v_hat
    )
    return params, (m, v)


def _tree_zeros_like(tree):
    return jax.tree_util.tree_map(jnp.zeros_like, tree)


def _soft_value_iteration(
    reward: jnp.ndarray,
    next_states: jnp.ndarray,
    terminal: jnp.ndarray,
    state_terminal: jnp.ndarray,
    gamma: float,
    tau: float,
    iterations: int,
) -> tuple[jnp.ndarray, jnp.ndarray]:
    def body(_, value):
        q_values = reward + gamma * (1.0 - terminal) * value[next_states]
        new_value = tau * jax.nn.logsumexp(q_values / tau, axis=1)
        return jnp.where(state_terminal > 0.5, 0.0, new_value)

    value = jnp.zeros((reward.shape[0],), dtype=jnp.float32)
    value = jax.lax.fori_loop(0, iterations, body, value)
    q_values = reward + gamma * (1.0 - terminal) * value[next_states]
    return q_values, value


def _traj_returns(reward: jnp.ndarray, batch: dict[str, jnp.ndarray]) -> jnp.ndarray:
    r = reward[batch["states"], batch["actions"]]
    return jnp.sum(r * batch["mask"] * batch["discounts"], axis=1)


def _flatten_transitions(batch: dict[str, jnp.ndarray]) -> tuple[jnp.ndarray, jnp.ndarray, jnp.ndarray]:
    return (
        batch["states"].reshape(-1),
        batch["actions"].reshape(-1),
        batch["mask"].reshape(-1),
    )


def _pairwise_auc(scores: np.ndarray, labels: np.ndarray) -> float:
    pos = scores[labels > 0.5]
    neg = scores[labels <= 0.5]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    wins = (pos[:, None] > neg[None, :]).mean()
    ties = (pos[:, None] == neg[None, :]).mean()
    return float(wins + 0.5 * ties)


def train_tabular_tri_piql(
    spec: GridSpec,
    pos_batch: dict[str, np.ndarray],
    neg_batch: dict[str, np.ndarray],
    unlabeled_batch: dict[str, np.ndarray],
    unlabeled_latent_good: np.ndarray,
    seed: int,
    steps: int = 800,
    lr: float = 0.05,
    gamma: float = 0.97,
    vi_tau: float = 0.2,
    vi_iterations: int = 60,
    log_every: int = 100,
) -> TriPiqlResult:
    key = jax.random.PRNGKey(seed)
    reward = 0.01 * jax.random.normal(key, (spec.num_states, spec.num_actions), dtype=jnp.float32)
    params = {
        "reward": reward,
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
        local_reward = local_params["reward"]
        q_values, values = _soft_value_iteration(
            local_reward, next_states, terminal, state_terminal, gamma, vi_tau, vi_iterations
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
        q_pos = jax.nn.sigmoid((pos_norm - local_params["bias"]) / 0.8)
        q_neg = jax.nn.sigmoid((neg_norm - local_params["bias"]) / 0.8)
        q_unl = jnp.clip(jax.nn.sigmoid((unl_norm - local_params["bias"]) / 0.8), 0.03, 0.97)
        q_label_loss = jnp.mean(jax.nn.softplus(-3.0 * (q_pos - 0.5))) + jnp.mean(
            jax.nn.softplus(3.0 * (q_neg - 0.5))
        )
        prior_loss = (jnp.mean(q_unl) - 0.25) ** 2
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
            + 0.005 * reward_l2
        )
        metrics = {
            "loss": loss,
            "rank_loss": rank_loss,
            "q_label_loss": q_label_loss,
            "adv_loss": adv_loss,
            "conservative": conservative,
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
            local_params, local_grads, local_opt_state, lr, local_step
        )
        return local_params, local_opt_state, local_metrics

    history: list[dict[str, float]] = []
    for step in range(1, steps + 1):
        params, opt_state, metrics = train_step(params, opt_state, jnp.asarray(step, dtype=jnp.float32))
        if step == 1 or step % log_every == 0 or step == steps:
            history.append({k: float(v) for k, v in metrics.items()})

    final_reward = np.asarray(params["reward"])
    q_values, values = _soft_value_iteration(
        jnp.asarray(final_reward),
        next_states,
        terminal,
        state_terminal,
        gamma,
        vi_tau,
        vi_iterations,
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
    q_pos = 1.0 / (1.0 + np.exp(-((pos_norm - bias) / 0.8)))
    q_neg = 1.0 / (1.0 + np.exp(-((neg_norm - bias) / 0.8)))
    q_unl = np.clip(1.0 / (1.0 + np.exp(-((unl_norm - bias) / 0.8))), 0.03, 0.97)

    pos_mask = np.asarray(pos["mask"]).reshape(-1)
    neg_mask = np.asarray(neg["mask"]).reshape(-1)
    pos_adv = advantages[np.asarray(pos_s), np.asarray(pos_a)]
    neg_adv = advantages[np.asarray(neg_s), np.asarray(neg_a)]
    pos_reward_flat = final_reward[np.asarray(pos_s), np.asarray(pos_a)]
    neg_reward_flat = final_reward[np.asarray(neg_s), np.asarray(neg_a)]

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


def q_policy_from_reward(
    spec: GridSpec,
    reward: np.ndarray,
    gamma: float = 0.97,
    tau: float = 0.2,
    iterations: int = 60,
):
    next_states, terminal, state_terminal = transition_tables(spec)
    q_values, _ = _soft_value_iteration(
        jnp.asarray(reward, dtype=jnp.float32),
        jnp.asarray(next_states),
        jnp.asarray(terminal),
        jnp.asarray(state_terminal),
        gamma,
        tau,
        iterations,
    )
    q_np = np.asarray(q_values)

    def policy(state: int) -> int:
        return int(np.argmax(q_np[int(state)]))

    return policy, q_np
