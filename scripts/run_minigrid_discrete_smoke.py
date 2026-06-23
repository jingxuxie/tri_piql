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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_minari_bc_baselines import default_split_path, init_mlp, markdown_table, mlp_apply
from tri_piql.algos.tabular import _adam_update, _tree_zeros_like


@dataclass(frozen=True)
class DiscreteData:
    observations: np.ndarray
    actions: np.ndarray
    episode_ids: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_id", help="Minari dataset id")
    parser.add_argument("--split-path", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path("results/minigrid_discrete_smoke"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=700)
    parser.add_argument("--classifier-steps", type=int, default=500)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--eval-episodes", type=int, default=50)
    parser.add_argument("--eval-horizon", type=int, default=100)
    parser.add_argument("--rerank-alphas", type=float, nargs="+", default=[0.5, 1.0, 2.0])
    return parser.parse_args()


def obs_features(observations, t: int | None = None) -> np.ndarray:
    image = np.asarray(observations["image"], dtype=np.float32)
    direction = np.asarray(observations["direction"], dtype=np.int64)
    if t is not None:
        image = image[t]
        direction = direction[t]
    image_features = (image.reshape(-1) / 255.0).astype(np.float32, copy=False)
    direction_onehot = np.eye(4, dtype=np.float32)[int(direction)]
    return np.concatenate([image_features, direction_onehot], axis=0)


def load_discrete_data(dataset, episode_ids: list[int]) -> DiscreteData:
    obs_chunks: list[np.ndarray] = []
    action_chunks: list[np.ndarray] = []
    episode_chunks: list[np.ndarray] = []
    for episode in dataset.iterate_episodes(episode_indices=np.asarray(episode_ids, dtype=np.int64)):
        actions = np.asarray(episode.actions, dtype=np.int32)
        features = np.asarray([obs_features(episode.observations, t=t) for t in range(actions.shape[0])], dtype=np.float32)
        obs_chunks.append(features)
        action_chunks.append(actions)
        episode_chunks.append(np.full((actions.shape[0],), int(episode.id), dtype=np.int64))
    if not obs_chunks:
        raise ValueError("no transitions loaded")
    return DiscreteData(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        episode_ids=np.concatenate(episode_chunks, axis=0),
    )


def action_onehot(actions: np.ndarray, num_actions: int) -> np.ndarray:
    return np.eye(num_actions, dtype=np.float32)[actions.astype(np.int64)]


def state_action_features(observations: np.ndarray, actions: np.ndarray, num_actions: int) -> np.ndarray:
    return np.concatenate([observations, action_onehot(actions, num_actions)], axis=-1).astype(np.float32, copy=False)


def train_policy(
    observations: np.ndarray,
    actions: np.ndarray,
    weights: np.ndarray,
    *,
    num_actions: int,
    seed: int,
    steps: int,
    batch_size: int,
    hidden_dim: int,
    depth: int,
    lr: float,
) -> tuple[list[dict[str, jax.Array]], list[dict[str, float]]]:
    x = jnp.asarray(observations, dtype=jnp.float32)
    a = jnp.asarray(actions, dtype=jnp.int32)
    w = jnp.asarray(weights, dtype=jnp.float32)
    key = jax.random.PRNGKey(seed)
    key, init_key = jax.random.split(key)
    params = init_mlp(init_key, observations.shape[1], num_actions, hidden_dim, depth)
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))

    def loss_fn(local_params, idx):
        logits = mlp_apply(local_params, x[idx])
        nll = -jax.nn.log_softmax(logits)[jnp.arange(idx.shape[0]), a[idx]]
        local_w = w[idx]
        return jnp.sum(local_w * nll) / (jnp.sum(local_w) + 1.0e-6)

    grad_fn = jax.value_and_grad(loss_fn)

    @jax.jit
    def step(local_params, local_opt_state, local_key, local_step):
        local_key, sample_key = jax.random.split(local_key)
        idx = jax.random.randint(sample_key, (batch_size,), minval=0, maxval=observations.shape[0])
        loss, grads = grad_fn(local_params, idx)
        local_params, local_opt_state = _adam_update(local_params, grads, local_opt_state, lr, local_step)
        return local_params, local_opt_state, local_key, loss

    history = []
    for step_id in range(1, steps + 1):
        params, opt_state, key, loss = step(params, opt_state, key, jnp.asarray(step_id, dtype=jnp.float32))
        if step_id == 1 or step_id % max(1, steps // 5) == 0 or step_id == steps:
            history.append({"step": step_id, "loss": float(loss)})
    return params, history


def train_state_action_classifier(
    pos: DiscreteData,
    neg: DiscreteData,
    *,
    num_actions: int,
    seed: int,
    steps: int,
    batch_size: int,
    hidden_dim: int,
    depth: int,
    lr: float,
) -> tuple[list[dict[str, jax.Array]], list[dict[str, float]]]:
    pos_x = jnp.asarray(state_action_features(pos.observations, pos.actions, num_actions), dtype=jnp.float32)
    neg_x = jnp.asarray(state_action_features(neg.observations, neg.actions, num_actions), dtype=jnp.float32)
    key = jax.random.PRNGKey(seed)
    key, init_key = jax.random.split(key)
    params = init_mlp(init_key, pos_x.shape[1], 1, hidden_dim, depth)
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))
    half_batch = max(1, batch_size // 2)

    def loss_fn(local_params, pos_idx, neg_idx):
        pos_logits = mlp_apply(local_params, pos_x[pos_idx]).reshape(-1)
        neg_logits = mlp_apply(local_params, neg_x[neg_idx]).reshape(-1)
        return jnp.mean(jax.nn.softplus(-pos_logits)) + jnp.mean(jax.nn.softplus(neg_logits))

    grad_fn = jax.value_and_grad(loss_fn)

    @jax.jit
    def step(local_params, local_opt_state, local_key, local_step):
        local_key, pos_key, neg_key = jax.random.split(local_key, 3)
        pos_idx = jax.random.randint(pos_key, (half_batch,), minval=0, maxval=pos.observations.shape[0])
        neg_idx = jax.random.randint(neg_key, (half_batch,), minval=0, maxval=neg.observations.shape[0])
        loss, grads = grad_fn(local_params, pos_idx, neg_idx)
        local_params, local_opt_state = _adam_update(local_params, grads, local_opt_state, lr, local_step)
        return local_params, local_opt_state, local_key, loss

    history = []
    for step_id in range(1, steps + 1):
        params, opt_state, key, loss = step(params, opt_state, key, jnp.asarray(step_id, dtype=jnp.float32))
        if step_id == 1 or step_id % max(1, steps // 5) == 0 or step_id == steps:
            history.append({"step": step_id, "loss": float(loss)})
    return params, history


def predict_logits(params, observations: np.ndarray) -> np.ndarray:
    return np.asarray(mlp_apply(params, jnp.asarray(observations, dtype=jnp.float32)))


def classifier_logits(params, observations: np.ndarray, actions: np.ndarray, num_actions: int) -> np.ndarray:
    features = state_action_features(observations, actions, num_actions)
    return np.asarray(mlp_apply(params, jnp.asarray(features, dtype=jnp.float32))).reshape(-1)


def classifier_metrics(params, pos: DiscreteData, neg: DiscreteData, unl: DiscreteData, num_actions: int) -> dict[str, float]:
    pos_logits = classifier_logits(params, pos.observations, pos.actions, num_actions)
    neg_logits = classifier_logits(params, neg.observations, neg.actions, num_actions)
    unl_logits = classifier_logits(params, unl.observations, unl.actions, num_actions)
    pos_prob = 1.0 / (1.0 + np.exp(-pos_logits))
    neg_prob = 1.0 / (1.0 + np.exp(-neg_logits))
    unl_prob = 1.0 / (1.0 + np.exp(-unl_logits))
    return {
        "pos_prob_mean": float(pos_prob.mean()),
        "neg_prob_mean": float(neg_prob.mean()),
        "unlabeled_prob_mean": float(unl_prob.mean()),
        "labeled_accuracy": float(0.5 * ((pos_prob > 0.5).mean() + (neg_prob < 0.5).mean())),
    }


def evaluate_discrete_policy(
    dataset,
    policy_params,
    classifier_params,
    *,
    num_actions: int,
    rerank_alpha: float | None,
    args: argparse.Namespace,
    method: str,
) -> dict[str, float | str]:
    env = dataset.recover_environment()
    returns = []
    lengths = []
    successes = []
    all_actions = np.arange(num_actions, dtype=np.int32)
    for episode in range(args.eval_episodes):
        obs, _ = env.reset(seed=args.seed + 30_000 + episode)
        total = 0.0
        success = False
        length = 0
        for t in range(args.eval_horizon):
            feature = obs_features(obs)[None, :]
            policy_logits = predict_logits(policy_params, feature)[0]
            if rerank_alpha is None:
                action = int(np.argmax(policy_logits))
            else:
                obs_repeat = np.repeat(feature, num_actions, axis=0)
                cls_logits = classifier_logits(classifier_params, obs_repeat, all_actions, num_actions)
                scores = policy_logits + rerank_alpha * cls_logits
                action = int(np.argmax(scores))
            obs, reward, terminated, truncated, _ = env.step(action)
            total += float(reward)
            length = t + 1
            success = success or reward > 0.0
            if terminated or truncated:
                break
        returns.append(total)
        lengths.append(length)
        successes.append(float(success))
    env.close()
    return {
        "method": method,
        "success_rate": float(np.mean(successes)),
        "avg_return": float(np.mean(returns)),
        "avg_len": float(np.mean(lengths)),
    }


def main() -> None:
    args = parse_args()
    import minari

    split_path = args.split_path or default_split_path(args.dataset_id)
    split = json.loads(split_path.read_text(encoding="utf-8"))
    dataset = minari.load_dataset(args.dataset_id)
    num_actions = int(dataset.action_space.n)

    pos = load_discrete_data(dataset, split["positive_ids"])
    neg = load_discrete_data(dataset, split["negative_ids"])
    unl = load_discrete_data(dataset, split["unlabeled_ids"])
    all_obs = np.concatenate([pos.observations, neg.observations, unl.observations], axis=0)
    del all_obs

    classifier, classifier_history = train_state_action_classifier(
        pos,
        neg,
        num_actions=num_actions,
        seed=args.seed + 10,
        steps=args.classifier_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )
    cls_metrics = classifier_metrics(classifier, pos, neg, unl, num_actions)
    unl_prob = 1.0 / (1.0 + np.exp(-classifier_logits(classifier, unl.observations, unl.actions, num_actions)))

    train_sets = {
        "bc_positive": (
            pos.observations,
            pos.actions,
            np.ones((pos.actions.shape[0],), dtype=np.float32),
        ),
        "bc_pos_unlabeled": (
            np.concatenate([pos.observations, unl.observations], axis=0),
            np.concatenate([pos.actions, unl.actions], axis=0),
            np.ones((pos.actions.shape[0] + unl.actions.shape[0],), dtype=np.float32),
        ),
        "bc_all": (
            np.concatenate([pos.observations, neg.observations, unl.observations], axis=0),
            np.concatenate([pos.actions, neg.actions, unl.actions], axis=0),
            np.ones((pos.actions.shape[0] + neg.actions.shape[0] + unl.actions.shape[0],), dtype=np.float32),
        ),
        "weighted_bc_state_action": (
            np.concatenate([pos.observations, neg.observations, unl.observations], axis=0),
            np.concatenate([pos.actions, neg.actions, unl.actions], axis=0),
            np.concatenate(
                [
                    np.ones((pos.actions.shape[0],), dtype=np.float32),
                    np.zeros((neg.actions.shape[0],), dtype=np.float32),
                    unl_prob.astype(np.float32),
                ],
                axis=0,
            ),
        ),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    histories = {"state_action_classifier": classifier_history}
    metrics = []
    policy_params_by_name = {}
    for i, (method, (obs, actions, weights)) in enumerate(train_sets.items()):
        params, history = train_policy(
            obs,
            actions,
            weights,
            num_actions=num_actions,
            seed=args.seed + 100 + i,
            steps=args.steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
        )
        histories[method] = history
        policy_params_by_name[method] = params
        row = evaluate_discrete_policy(
            dataset,
            params,
            classifier,
            num_actions=num_actions,
            rerank_alpha=None,
            args=args,
            method=method,
        )
        metrics.append(row)
        print(f"{method}: success={row['success_rate']:.3f} return={row['avg_return']:.3f} len={row['avg_len']:.1f}")

    for alpha in args.rerank_alphas:
        method = f"bc_positive_sa_rerank_alpha{alpha:g}"
        row = evaluate_discrete_policy(
            dataset,
            policy_params_by_name["bc_positive"],
            classifier,
            num_actions=num_actions,
            rerank_alpha=alpha,
            args=args,
            method=method,
        )
        metrics.append(row)
        print(f"{method}: success={row['success_rate']:.3f} return={row['avg_return']:.3f} len={row['avg_len']:.1f}")

    metrics_path = args.out_dir / "metrics.csv"
    with metrics_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "success_rate", "avg_return", "avg_len"])
        writer.writeheader()
        writer.writerows(metrics)

    diagnostics = {
        "dataset_id": args.dataset_id,
        "split_path": str(split_path),
        "seed": args.seed,
        "steps": args.steps,
        "classifier_steps": args.classifier_steps,
        "eval_episodes": args.eval_episodes,
        "eval_horizon": args.eval_horizon,
        "num_actions": num_actions,
        "transition_counts": {
            "positive": int(pos.actions.shape[0]),
            "negative": int(neg.actions.shape[0]),
            "unlabeled": int(unl.actions.shape[0]),
        },
        "state_action_classifier": cls_metrics,
        "histories": histories,
    }
    diagnostics_path = args.out_dir / "diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report_path = args.out_dir / "REPORT.md"
    report_path.write_text(
        "\n".join(
            [
                f"# MiniGrid Discrete Smoke: `{args.dataset_id}`",
                "",
                f"Split path: `{split_path}`.",
                f"Policy steps: `{args.steps}`.",
                f"Classifier steps: `{args.classifier_steps}`.",
                f"Evaluation episodes: `{args.eval_episodes}`.",
                "",
                "## Metrics",
                "",
                markdown_table(metrics),
                "",
                "## State-Action Classifier Diagnostics",
                "",
                f"- Labeled accuracy: `{cls_metrics['labeled_accuracy']:.3f}`.",
                f"- Positive/negative/unlabeled probability mean: `{cls_metrics['pos_prob_mean']:.3f}` / `{cls_metrics['neg_prob_mean']:.3f}` / `{cls_metrics['unlabeled_prob_mean']:.3f}`.",
                "",
                "## Interpretation",
                "",
                "- This is a fast discrete-action real-data smoke for tri-signal filtering and reranking.",
                "- `weighted_bc_state_action` clones positives plus unlabeled transitions weighted by the state-action classifier.",
                "- Reranking uses the BC-positive policy logits plus a state-action classifier bonus.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
