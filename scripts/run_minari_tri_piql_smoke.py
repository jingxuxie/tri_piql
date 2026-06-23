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
    cap_transitions,
    default_split_path,
    evaluate_policy,
    init_mlp,
    load_transitions,
    markdown_table,
    mlp_apply,
    normalize,
    obs_features,
    predict,
    train_bc,
    train_transition_classifier,
)
from tri_piql.algos.tabular import _adam_update, _tree_zeros_like  # noqa: E402


@dataclass(frozen=True)
class TrajectoryBatch:
    observations: np.ndarray
    actions: np.ndarray
    mask: np.ndarray
    episode_ids: np.ndarray
    label_scores: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_id", help="Minari dataset id")
    parser.add_argument("--split-path", type=Path, default=None)
    parser.add_argument("--episodes-csv", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path("results/minari_tri_piql_smoke"))
    parser.add_argument("--obs-keys", nargs="+", default=["observation", "desired_goal"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=800)
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
    parser.add_argument("--q-temperature", type=float, default=1.0)
    parser.add_argument("--unlabeled-good-prior", type=float, default=0.50)
    parser.add_argument("--actor-temperature", type=float, default=1.0)
    return parser.parse_args()


def split_dir_from_path(split_path: Path) -> Path:
    return split_path.resolve().parent


def load_episode_label_scores(path: Path | None) -> dict[int, float]:
    if path is None or not path.exists():
        return {}
    scores: dict[int, float] = {}
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scores[int(row["episode_id"])] = float(row.get("label_score", row.get("trajectory_return", 0.0)))
    return scores


def load_trajectory_batch(
    dataset,
    episode_ids: list[int],
    obs_keys: list[str],
    label_scores: dict[int, float],
) -> TrajectoryBatch:
    raw_obs: list[np.ndarray] = []
    raw_actions: list[np.ndarray] = []
    ids: list[int] = []
    scores: list[float] = []
    max_len = 1
    for episode in dataset.iterate_episodes(episode_indices=np.asarray(episode_ids, dtype=np.int64)):
        actions = np.asarray(episode.actions, dtype=np.float32)
        features = np.asarray(
            [obs_features(episode.observations, obs_keys, t=t) for t in range(actions.shape[0])],
            dtype=np.float32,
        )
        raw_obs.append(features)
        raw_actions.append(actions)
        ids.append(int(episode.id))
        scores.append(float(label_scores.get(int(episode.id), np.sum(episode.rewards))))
        max_len = max(max_len, int(actions.shape[0]))

    if not raw_obs:
        raise ValueError("no trajectories loaded")

    obs_dim = raw_obs[0].shape[-1]
    action_dim = raw_actions[0].shape[-1]
    obs = np.zeros((len(raw_obs), max_len, obs_dim), dtype=np.float32)
    actions = np.zeros((len(raw_actions), max_len, action_dim), dtype=np.float32)
    mask = np.zeros((len(raw_obs), max_len), dtype=np.float32)
    for i, (obs_i, actions_i) in enumerate(zip(raw_obs, raw_actions, strict=True)):
        length = actions_i.shape[0]
        obs[i, :length] = obs_i
        actions[i, :length] = actions_i
        mask[i, :length] = 1.0
    return TrajectoryBatch(
        observations=obs,
        actions=actions,
        mask=mask,
        episode_ids=np.asarray(ids, dtype=np.int64),
        label_scores=np.asarray(scores, dtype=np.float32),
    )


def normalize_trajectory_batch(batch: TrajectoryBatch, mean: np.ndarray, std: np.ndarray) -> TrajectoryBatch:
    return TrajectoryBatch(
        observations=(batch.observations - mean[:, None, :]) / std[:, None, :],
        actions=batch.actions,
        mask=batch.mask,
        episode_ids=batch.episode_ids,
        label_scores=batch.label_scores,
    )


def score_apply(params, observations: jnp.ndarray, actions: jnp.ndarray) -> jnp.ndarray:
    x = jnp.concatenate([observations, actions], axis=-1)
    flat = x.reshape((-1, x.shape[-1]))
    scores = mlp_apply(params["score"], flat).reshape(x.shape[:-1])
    return scores


def param_l2(params) -> jnp.ndarray:
    leaves = jax.tree_util.tree_leaves(params["score"])
    return sum(jnp.mean(leaf**2) for leaf in leaves) / max(1, len(leaves))


def train_tri_piql_score(
    pos: TransitionData,
    neg: TransitionData,
    unl: TransitionData,
    pos_traj: TrajectoryBatch,
    neg_traj: TrajectoryBatch,
    unl_traj: TrajectoryBatch,
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
    q_temperature: float,
    unlabeled_good_prior: float,
) -> tuple[dict[str, object], list[dict[str, float]]]:
    obs_dim = pos.observations.shape[1]
    action_dim = pos.actions.shape[1]
    input_dim = obs_dim + action_dim
    key = jax.random.PRNGKey(seed)
    key, init_key = jax.random.split(key)
    params = {
        "score": init_mlp(init_key, input_dim, 1, hidden_dim, depth),
        "bias": jnp.array(0.0, dtype=jnp.float32),
    }
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))

    pos_x = jnp.asarray(pos.observations, dtype=jnp.float32)
    pos_a = jnp.asarray(pos.actions, dtype=jnp.float32)
    neg_x = jnp.asarray(neg.observations, dtype=jnp.float32)
    neg_a = jnp.asarray(neg.actions, dtype=jnp.float32)
    unl_x = jnp.asarray(unl.observations, dtype=jnp.float32)
    unl_a = jnp.asarray(unl.actions, dtype=jnp.float32)

    pos_to = jnp.asarray(pos_traj.observations, dtype=jnp.float32)
    pos_ta = jnp.asarray(pos_traj.actions, dtype=jnp.float32)
    pos_tm = jnp.asarray(pos_traj.mask, dtype=jnp.float32)
    neg_to = jnp.asarray(neg_traj.observations, dtype=jnp.float32)
    neg_ta = jnp.asarray(neg_traj.actions, dtype=jnp.float32)
    neg_tm = jnp.asarray(neg_traj.mask, dtype=jnp.float32)
    unl_to = jnp.asarray(unl_traj.observations, dtype=jnp.float32)
    unl_ta = jnp.asarray(unl_traj.actions, dtype=jnp.float32)
    unl_tm = jnp.asarray(unl_traj.mask, dtype=jnp.float32)
    low = jnp.asarray(action_low, dtype=jnp.float32)
    high = jnp.asarray(action_high, dtype=jnp.float32)
    half_batch = max(1, batch_size // 2)

    def trajectory_return(local_params, obs_b, act_b, mask_b):
        scores = score_apply(local_params, obs_b, act_b)
        lengths = jnp.sum(mask_b, axis=1) + 1.0e-6
        return jnp.sum(scores * mask_b, axis=1) / jnp.sqrt(lengths)

    def loss_fn(local_params, pos_idx, neg_idx, unl_idx, pos_eidx, neg_eidx, unl_eidx, rand_actions):
        pos_s = score_apply(local_params, pos_x[pos_idx], pos_a[pos_idx])
        neg_s = score_apply(local_params, neg_x[neg_idx], neg_a[neg_idx])
        unl_s = score_apply(local_params, unl_x[unl_idx], unl_a[unl_idx])

        pos_ret = trajectory_return(local_params, pos_to[pos_eidx], pos_ta[pos_eidx], pos_tm[pos_eidx])
        neg_ret = trajectory_return(local_params, neg_to[neg_eidx], neg_ta[neg_eidx], neg_tm[neg_eidx])
        unl_ret = trajectory_return(local_params, unl_to[unl_eidx], unl_ta[unl_eidx], unl_tm[unl_eidx])
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

        pos_signed = jnp.mean(jax.nn.softplus(0.15 - pos_s))
        neg_signed = jnp.mean(jax.nn.softplus(0.15 + neg_s))
        unl_traj_scores = score_apply(local_params, unl_to[unl_eidx], unl_ta[unl_eidx])
        unl_mask = unl_tm[unl_eidx]
        q_stop = jax.lax.stop_gradient(q_unl)[:, None]
        unl_signed = jnp.sum(
            (
                q_stop * jax.nn.softplus(0.10 - unl_traj_scores)
                + (1.0 - q_stop) * jax.nn.softplus(0.10 + unl_traj_scores)
            )
            * unl_mask
        ) / (jnp.sum(unl_mask) + 1.0e-6)

        support_obs = jnp.concatenate([pos_x[pos_idx[:half_batch]], unl_x[unl_idx[:half_batch]]], axis=0)
        support_act = jnp.concatenate([pos_a[pos_idx[:half_batch]], unl_a[unl_idx[:half_batch]]], axis=0)
        support_score = score_apply(local_params, support_obs, support_act)
        rand_score = score_apply(local_params, support_obs, rand_actions)
        conservative = jnp.mean(jax.nn.softplus(0.05 + rand_score - support_score))

        score_l2 = jnp.mean(pos_s**2) + jnp.mean(neg_s**2) + jnp.mean(unl_s**2)
        loss = (
            1.2 * rank_loss
            + 0.7 * q_label_loss
            + 1.0 * (pos_signed + neg_signed)
            + 0.35 * unl_signed
            + 0.10 * conservative
            + 0.20 * prior_loss
            + 0.01 * entropy_loss
            + 0.003 * score_l2
            + 0.001 * param_l2(local_params)
        )
        metrics = {
            "loss": loss,
            "rank_loss": rank_loss,
            "q_label_loss": q_label_loss,
            "pos_signed": pos_signed,
            "neg_signed": neg_signed,
            "unl_signed": unl_signed,
            "conservative": conservative,
            "prior_loss": prior_loss,
            "q_pos": jnp.mean(q_pos),
            "q_neg": jnp.mean(q_neg),
            "q_unl": jnp.mean(q_unl),
            "pos_score": jnp.mean(pos_s),
            "neg_score": jnp.mean(neg_s),
            "unl_score": jnp.mean(unl_s),
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


def predict_scores(params, observations: np.ndarray, actions: np.ndarray, batch_size: int = 65_536) -> np.ndarray:
    outs = []
    for start in range(0, observations.shape[0], batch_size):
        obs_b = jnp.asarray(observations[start : start + batch_size], dtype=jnp.float32)
        act_b = jnp.asarray(actions[start : start + batch_size], dtype=jnp.float32)
        outs.append(np.asarray(score_apply(params, obs_b, act_b)).reshape(-1))
    return np.concatenate(outs, axis=0)


def trajectory_scores(params, batch: TrajectoryBatch, episode_batch_size: int = 64) -> np.ndarray:
    out = []
    for start in range(0, batch.observations.shape[0], episode_batch_size):
        obs_b = batch.observations[start : start + episode_batch_size]
        act_b = batch.actions[start : start + episode_batch_size]
        mask_b = batch.mask[start : start + episode_batch_size]
        flat_scores = predict_scores(
            params,
            obs_b.reshape((-1, obs_b.shape[-1])),
            act_b.reshape((-1, act_b.shape[-1])),
        ).reshape(mask_b.shape)
        lengths = mask_b.sum(axis=1) + 1.0e-6
        out.append((flat_scores * mask_b).sum(axis=1) / np.sqrt(lengths))
    return np.concatenate(out, axis=0)


def pairwise_auc(pos_scores: np.ndarray, neg_scores: np.ndarray) -> float:
    if pos_scores.size == 0 or neg_scores.size == 0:
        return float("nan")
    return float(
        (
            (pos_scores[:, None] > neg_scores[None, :]).mean()
            + 0.5 * (pos_scores[:, None] == neg_scores[None, :]).mean()
        )
    )


def rank_correlation(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or y.size < 2:
        return float("nan")
    x_rank = np.argsort(np.argsort(x)).astype(np.float64)
    y_rank = np.argsort(np.argsort(y)).astype(np.float64)
    if np.std(x_rank) < 1.0e-8 or np.std(y_rank) < 1.0e-8:
        return float("nan")
    return float(np.corrcoef(x_rank, y_rank)[0, 1])


def build_tri_actor_weights(
    params,
    pos: TransitionData,
    neg: TransitionData,
    unl: TransitionData,
    unl_q_by_episode: dict[int, float],
    actor_temperature: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, float]]:
    pos_scores = predict_scores(params, pos.observations, pos.actions)
    neg_scores = predict_scores(params, neg.observations, neg.actions)
    unl_scores = predict_scores(params, unl.observations, unl.actions)
    score_mean = np.mean(np.concatenate([pos_scores, unl_scores]))
    score_std = np.std(np.concatenate([pos_scores, unl_scores])) + 1.0e-6
    pos_adv = (pos_scores - score_mean) / score_std
    unl_adv = (unl_scores - score_mean) / score_std
    pos_w = np.exp(np.clip(pos_adv / actor_temperature, -2.0, 2.0)).astype(np.float32)
    neg_w = np.zeros((neg.actions.shape[0],), dtype=np.float32)
    unl_q = np.asarray([unl_q_by_episode.get(int(eid), 0.0) for eid in unl.episode_ids], dtype=np.float32)
    unl_w = (unl_q * np.exp(np.clip(unl_adv / actor_temperature, -2.0, 2.0))).astype(np.float32)
    weights = np.concatenate([pos_w, neg_w, unl_w], axis=0)
    observations = np.concatenate([pos.observations, neg.observations, unl.observations], axis=0)
    actions = np.concatenate([pos.actions, neg.actions, unl.actions], axis=0)
    diagnostics = {
        "pos_transition_score_mean": float(np.mean(pos_scores)),
        "neg_transition_score_mean": float(np.mean(neg_scores)),
        "unl_transition_score_mean": float(np.mean(unl_scores)),
        "pos_actor_weight_mean": float(np.mean(pos_w)),
        "unl_actor_weight_mean": float(np.mean(unl_w)),
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

    pos_raw = load_transitions(dataset, split["positive_ids"], args.obs_keys)
    neg_raw = load_transitions(dataset, split["negative_ids"], args.obs_keys)
    unl_raw = load_transitions(dataset, split["unlabeled_ids"], args.obs_keys)
    all_train_x = np.concatenate([pos_raw.observations, neg_raw.observations, unl_raw.observations], axis=0)
    obs_mean, obs_std, [pos_x, neg_x, unl_x] = normalize(
        all_train_x, pos_raw.observations, neg_raw.observations, unl_raw.observations
    )
    pos = cap_transitions(TransitionData(pos_x, pos_raw.actions, pos_raw.episode_ids), args.max_train_transitions, args.seed)
    neg = cap_transitions(
        TransitionData(neg_x, neg_raw.actions, neg_raw.episode_ids), args.max_train_transitions, args.seed + 1
    )
    unl = cap_transitions(
        TransitionData(unl_x, unl_raw.actions, unl_raw.episode_ids), args.max_train_transitions, args.seed + 2
    )

    pos_traj = normalize_trajectory_batch(
        load_trajectory_batch(dataset, split["positive_ids"], args.obs_keys, label_scores), obs_mean, obs_std
    )
    neg_traj = normalize_trajectory_batch(
        load_trajectory_batch(dataset, split["negative_ids"], args.obs_keys, label_scores), obs_mean, obs_std
    )
    unl_traj = normalize_trajectory_batch(
        load_trajectory_batch(dataset, split["unlabeled_ids"], args.obs_keys, label_scores), obs_mean, obs_std
    )

    action_low = np.asarray(dataset.action_space.low, dtype=np.float32)
    action_high = np.asarray(dataset.action_space.high, dtype=np.float32)

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

    score_params, score_history = train_tri_piql_score(
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
        q_temperature=args.q_temperature,
        unlabeled_good_prior=args.unlabeled_good_prior,
    )
    pos_returns = trajectory_scores(score_params, pos_traj)
    neg_returns = trajectory_scores(score_params, neg_traj)
    unl_returns = trajectory_scores(score_params, unl_traj)
    all_returns = np.concatenate([pos_returns, neg_returns, unl_returns])
    ret_mean = all_returns.mean()
    ret_std = all_returns.std() + 1.0e-4
    q_bias = float(score_params["bias"])
    q_pos = 1.0 / (1.0 + np.exp(-(((pos_returns - ret_mean) / ret_std) - q_bias) / args.q_temperature))
    q_neg = 1.0 / (1.0 + np.exp(-(((neg_returns - ret_mean) / ret_std) - q_bias) / args.q_temperature))
    q_unl = np.clip(
        1.0 / (1.0 + np.exp(-(((unl_returns - ret_mean) / ret_std) - q_bias) / args.q_temperature)), 0.03, 0.97
    )
    unl_q_by_episode = {int(eid): float(q) for eid, q in zip(unl_traj.episode_ids, q_unl, strict=True)}
    label_score_corr = rank_correlation(q_unl, unl_traj.label_scores)
    q_diag = {
        "q_pos_mean": float(q_pos.mean()),
        "q_neg_mean": float(q_neg.mean()),
        "q_unlabeled_mean": float(q_unl.mean()),
        "pos_neg_auc": pairwise_auc(q_pos, q_neg),
        "rank_gap": float(pos_returns.mean() - neg_returns.mean()),
        "unlabeled_q_label_score_spearman": label_score_corr,
        "unlabeled_q_top_quartile_mean": float(q_unl[unl_traj.label_scores >= np.quantile(unl_traj.label_scores, 0.75)].mean()),
        "unlabeled_q_bottom_quartile_mean": float(
            q_unl[unl_traj.label_scores <= np.quantile(unl_traj.label_scores, 0.25)].mean()
        ),
        "q_bias": q_bias,
    }

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
    tri_x, tri_a, tri_w, tri_weight_diag = build_tri_actor_weights(
        score_params, pos, neg, unl, unl_q_by_episode, args.actor_temperature
    )
    unl_q_for_transitions = np.asarray([unl_q_by_episode.get(int(eid), 0.0) for eid in unl.episode_ids], dtype=np.float32)
    tri_q_only_w = np.concatenate(
        [
            np.ones((pos.actions.shape[0],), dtype=np.float32),
            np.zeros((neg.actions.shape[0],), dtype=np.float32),
            unl_q_for_transitions,
        ],
        axis=0,
    )

    train_sets = {
        "bc_positive": (
            pos.observations,
            pos.actions,
            np.ones((pos.actions.shape[0],), dtype=np.float32),
        ),
        "weighted_bc_classifier": (weighted_bc_x, weighted_bc_a, weighted_bc_w),
        "tri_piql_q_bc": (tri_x, tri_a, tri_q_only_w),
        "tri_piql_score_awbc": (tri_x, tri_a, tri_w),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    metrics = []
    histories = {"classifier": classifier_history, "tri_piql_score": score_history}
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
        "tri_piql_score": q_diag | tri_weight_diag,
        "histories": histories,
    }
    diagnostics_path = args.out_dir / "diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report_path = args.out_dir / "REPORT.md"
    report_path.write_text(
        "\n".join(
            [
                f"# Minari Tri-PIQL Smoke: `{args.dataset_id}`",
                "",
                f"Split path: `{split_path}`.",
                f"Observation keys: `{args.obs_keys}`.",
                f"Score steps: `{args.steps}`.",
                f"Actor steps: `{args.actor_steps}`.",
                f"Classifier steps: `{args.classifier_steps}`.",
                f"Evaluation episodes: `{args.eval_episodes}`.",
                "",
                "## Metrics",
                "",
                markdown_table(metrics),
                "",
                "## Score Diagnostics",
                "",
                f"- Learned q pos/neg/unlabeled mean: `{q_diag['q_pos_mean']:.3f}` / `{q_diag['q_neg_mean']:.3f}` / `{q_diag['q_unlabeled_mean']:.3f}`.",
                f"- Learned q bias: `{q_diag['q_bias']:.3f}`.",
                f"- Positive-vs-negative q AUC: `{q_diag['pos_neg_auc']:.3f}`.",
                f"- Learned trajectory score gap: `{q_diag['rank_gap']:.3f}`.",
                f"- Unlabeled q vs label-score Spearman: `{q_diag['unlabeled_q_label_score_spearman']:.3f}`.",
                f"- Unlabeled q top/bottom quartile mean: `{q_diag['unlabeled_q_top_quartile_mean']:.3f}` / `{q_diag['unlabeled_q_bottom_quartile_mean']:.3f}`.",
                f"- Transition score pos/neg/unlabeled mean: `{tri_weight_diag['pos_transition_score_mean']:.3f}` / `{tri_weight_diag['neg_transition_score_mean']:.3f}` / `{tri_weight_diag['unl_transition_score_mean']:.3f}`.",
                "",
                "## Classifier Baseline Diagnostics",
                "",
                f"- Labeled accuracy: `{classifier_metrics['labeled_accuracy']:.3f}`.",
                f"- Positive/negative/unlabeled probability mean: `{classifier_metrics['pos_prob_mean']:.3f}` / `{classifier_metrics['neg_prob_mean']:.3f}` / `{classifier_metrics['unlabeled_prob_mean']:.3f}`.",
                "",
                "## Interpretation",
                "",
                "- This is a short real-data smoke for the Tri-PIQL mechanism, not a final benchmark row.",
                "- The score model uses positive-vs-negative trajectory ranking, signed good/bad transition constraints, latent unlabeled trajectory weights, and a random-action conservative term.",
                "- `tri_piql_q_bc` tests whether latent trajectory weighting alone is useful before applying the score advantage exponent.",
                "- The promoted comparison is `tri_piql_score_awbc` and `tri_piql_q_bc` against `weighted_bc_classifier` under the same split and rollout budget.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
