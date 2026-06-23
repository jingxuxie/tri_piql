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

from tri_piql.algos.tabular import _adam_update, _tree_zeros_like
from tri_piql.datasets import sanitize_dataset_id


@dataclass(frozen=True)
class TransitionData:
    observations: np.ndarray
    actions: np.ndarray
    episode_ids: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_id", help="Minari dataset id")
    parser.add_argument("--split-path", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path("results/minari_bc_smoke"))
    parser.add_argument("--obs-keys", nargs="+", default=["observation", "desired_goal"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=1500)
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=256)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--max-train-transitions", type=int, default=250_000)
    parser.add_argument("--eval-episodes", type=int, default=20)
    parser.add_argument("--eval-horizon", type=int, default=800)
    return parser.parse_args()


def default_split_path(dataset_id: str) -> Path:
    return Path("results/minari_inspection") / sanitize_dataset_id(dataset_id) / "split_indices.json"


def obs_features(observations, obs_keys: list[str], t: int | None = None) -> np.ndarray:
    arrays = []
    if isinstance(observations, dict):
        for key in obs_keys:
            if key not in observations:
                raise KeyError(f"observation key {key!r} not found; available keys: {sorted(observations)}")
            value = np.asarray(observations[key], dtype=np.float32)
            if t is not None:
                value = value[t]
            arrays.append(value.reshape(-1))
    else:
        value = np.asarray(observations, dtype=np.float32)
        if t is not None:
            value = value[t]
        arrays.append(value.reshape(-1))
    return np.concatenate(arrays).astype(np.float32, copy=False)


def load_transitions(dataset, episode_ids: list[int], obs_keys: list[str]) -> TransitionData:
    obs_chunks: list[np.ndarray] = []
    action_chunks: list[np.ndarray] = []
    episode_chunks: list[np.ndarray] = []
    for episode in dataset.iterate_episodes(episode_indices=np.asarray(episode_ids, dtype=np.int64)):
        actions = np.asarray(episode.actions, dtype=np.float32)
        features = np.asarray(
            [obs_features(episode.observations, obs_keys, t=t) for t in range(actions.shape[0])],
            dtype=np.float32,
        )
        obs_chunks.append(features)
        action_chunks.append(actions)
        episode_chunks.append(np.full((actions.shape[0],), int(episode.id), dtype=np.int64))
    if not obs_chunks:
        raise ValueError("no transitions loaded")
    return TransitionData(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        episode_ids=np.concatenate(episode_chunks, axis=0),
    )


def cap_transitions(data: TransitionData, max_transitions: int, seed: int) -> TransitionData:
    if data.observations.shape[0] <= max_transitions:
        return data
    rng = np.random.default_rng(seed)
    idx = np.sort(rng.choice(data.observations.shape[0], size=max_transitions, replace=False))
    return TransitionData(data.observations[idx], data.actions[idx], data.episode_ids[idx])


def normalize(train_x: np.ndarray, *arrays: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    mean = train_x.mean(axis=0, keepdims=True)
    std = train_x.std(axis=0, keepdims=True) + 1.0e-6
    return mean, std, [(array - mean) / std for array in arrays]


def init_mlp(key: jax.Array, input_dim: int, output_dim: int, hidden_dim: int, depth: int):
    sizes = [input_dim] + [hidden_dim] * depth + [output_dim]
    keys = jax.random.split(key, len(sizes) - 1)
    layers = []
    for i, (fan_in, fan_out) in enumerate(zip(sizes[:-1], sizes[1:], strict=True)):
        scale = np.sqrt(2.0 / fan_in) if i < len(sizes) - 2 else 0.01
        layers.append(
            {
                "w": scale * jax.random.normal(keys[i], (fan_in, fan_out), dtype=jnp.float32),
                "b": jnp.zeros((fan_out,), dtype=jnp.float32),
            }
        )
    return layers


def mlp_apply(params, x: jnp.ndarray) -> jnp.ndarray:
    for layer in params[:-1]:
        x = jax.nn.relu(x @ layer["w"] + layer["b"])
    return x @ params[-1]["w"] + params[-1]["b"]


def train_bc(
    x: np.ndarray,
    actions: np.ndarray,
    weights: np.ndarray,
    *,
    seed: int,
    steps: int,
    batch_size: int,
    hidden_dim: int,
    depth: int,
    lr: float,
) -> tuple[list[dict[str, jax.Array]], list[dict[str, float]]]:
    x_j = jnp.asarray(x, dtype=jnp.float32)
    a_j = jnp.asarray(actions, dtype=jnp.float32)
    w_j = jnp.asarray(weights, dtype=jnp.float32)
    key = jax.random.PRNGKey(seed)
    key, init_key = jax.random.split(key)
    params = init_mlp(init_key, x.shape[1], actions.shape[1], hidden_dim, depth)
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))

    def loss_fn(local_params, idx):
        pred = mlp_apply(local_params, x_j[idx])
        per_row = jnp.mean((pred - a_j[idx]) ** 2, axis=1)
        local_w = w_j[idx]
        return jnp.sum(local_w * per_row) / (jnp.sum(local_w) + 1.0e-6)

    grad_fn = jax.value_and_grad(loss_fn)

    @jax.jit
    def step(local_params, local_opt_state, local_key, local_step):
        local_key, sample_key = jax.random.split(local_key)
        idx = jax.random.randint(sample_key, (batch_size,), minval=0, maxval=x.shape[0])
        loss, grads = grad_fn(local_params, idx)
        local_params, local_opt_state = _adam_update(local_params, grads, local_opt_state, lr, local_step)
        return local_params, local_opt_state, local_key, loss

    history = []
    for step_id in range(1, steps + 1):
        params, opt_state, key, loss = step(params, opt_state, key, jnp.asarray(step_id, dtype=jnp.float32))
        if step_id == 1 or step_id % max(1, steps // 5) == 0 or step_id == steps:
            history.append({"step": step_id, "loss": float(loss)})
    return params, history


def train_transition_classifier(
    pos_x: np.ndarray,
    neg_x: np.ndarray,
    *,
    seed: int,
    steps: int,
    batch_size: int,
    hidden_dim: int,
    depth: int,
    lr: float,
) -> tuple[list[dict[str, jax.Array]], list[dict[str, float]]]:
    pos_j = jnp.asarray(pos_x, dtype=jnp.float32)
    neg_j = jnp.asarray(neg_x, dtype=jnp.float32)
    key = jax.random.PRNGKey(seed)
    key, init_key = jax.random.split(key)
    params = init_mlp(init_key, pos_x.shape[1], 1, hidden_dim, depth)
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))
    half_batch = max(1, batch_size // 2)

    def loss_fn(local_params, pos_idx, neg_idx):
        pos_logits = mlp_apply(local_params, pos_j[pos_idx]).reshape(-1)
        neg_logits = mlp_apply(local_params, neg_j[neg_idx]).reshape(-1)
        pos_loss = jnp.mean(jax.nn.softplus(-pos_logits))
        neg_loss = jnp.mean(jax.nn.softplus(neg_logits))
        return pos_loss + neg_loss

    grad_fn = jax.value_and_grad(loss_fn)

    @jax.jit
    def step(local_params, local_opt_state, local_key, local_step):
        local_key, pos_key, neg_key = jax.random.split(local_key, 3)
        pos_idx = jax.random.randint(pos_key, (half_batch,), minval=0, maxval=pos_x.shape[0])
        neg_idx = jax.random.randint(neg_key, (half_batch,), minval=0, maxval=neg_x.shape[0])
        loss, grads = grad_fn(local_params, pos_idx, neg_idx)
        local_params, local_opt_state = _adam_update(local_params, grads, local_opt_state, lr, local_step)
        return local_params, local_opt_state, local_key, loss

    history = []
    for step_id in range(1, steps + 1):
        params, opt_state, key, loss = step(params, opt_state, key, jnp.asarray(step_id, dtype=jnp.float32))
        if step_id == 1 or step_id % max(1, steps // 5) == 0 or step_id == steps:
            history.append({"step": step_id, "loss": float(loss)})
    return params, history


def predict(params, x: np.ndarray, batch_size: int = 65_536) -> np.ndarray:
    outs = []
    for start in range(0, x.shape[0], batch_size):
        out = mlp_apply(params, jnp.asarray(x[start : start + batch_size], dtype=jnp.float32))
        outs.append(np.asarray(out))
    return np.concatenate(outs, axis=0)


def evaluate_policy(dataset, params, obs_mean, obs_std, obs_keys: list[str], args: argparse.Namespace, method: str) -> dict[str, float | str]:
    env = dataset.recover_environment()
    returns = []
    lengths = []
    successes = []
    action_low = np.asarray(env.action_space.low, dtype=np.float32)
    action_high = np.asarray(env.action_space.high, dtype=np.float32)
    for episode in range(args.eval_episodes):
        obs, _ = env.reset(seed=args.seed + 10_000 + episode)
        total = 0.0
        success = False
        length = 0
        for t in range(args.eval_horizon):
            has_success_signal = False
            feature = obs_features(obs, obs_keys)[None, :]
            feature = (feature - obs_mean) / obs_std
            action = predict(params, feature, batch_size=1)[0]
            action = np.clip(action, action_low, action_high)
            obs, reward, terminated, truncated, info = env.step(action)
            total += float(reward)
            length = t + 1
            if "success" in info:
                has_success_signal = True
                success = success or bool(info["success"])
            else:
                success = success or reward > 0.0
            if (has_success_signal and success) or terminated or truncated:
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


def markdown_table(rows: list[dict[str, float | str]]) -> str:
    lines = ["| method | success | return | length |", "|---|---:|---:|---:|"]
    for row in rows:
        lines.append(
            f"| {row['method']} | {float(row['success_rate']):.3f} | "
            f"{float(row['avg_return']):.3f} | {float(row['avg_len']):.1f} |"
        )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    import minari

    split_path = args.split_path or default_split_path(args.dataset_id)
    split = json.loads(split_path.read_text(encoding="utf-8"))
    dataset = minari.load_dataset(args.dataset_id)
    pos = load_transitions(dataset, split["positive_ids"], args.obs_keys)
    neg = load_transitions(dataset, split["negative_ids"], args.obs_keys)
    unl = load_transitions(dataset, split["unlabeled_ids"], args.obs_keys)

    all_train_x = np.concatenate([pos.observations, neg.observations, unl.observations], axis=0)
    obs_mean, obs_std, [pos_x, neg_x, unl_x] = normalize(all_train_x, pos.observations, neg.observations, unl.observations)
    pos = cap_transitions(TransitionData(pos_x, pos.actions, pos.episode_ids), args.max_train_transitions, args.seed)
    neg = cap_transitions(TransitionData(neg_x, neg.actions, neg.episode_ids), args.max_train_transitions, args.seed + 1)
    unl = cap_transitions(TransitionData(unl_x, unl.actions, unl.episode_ids), args.max_train_transitions, args.seed + 2)

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
    pos_prob = jax.nn.sigmoid(jnp.asarray(predict(classifier, pos.observations).reshape(-1)))
    neg_prob = jax.nn.sigmoid(jnp.asarray(predict(classifier, neg.observations).reshape(-1)))
    unl_prob = np.asarray(jax.nn.sigmoid(jnp.asarray(predict(classifier, unl.observations).reshape(-1))))
    classifier_metrics = {
        "pos_prob_mean": float(np.asarray(pos_prob).mean()),
        "neg_prob_mean": float(np.asarray(neg_prob).mean()),
        "unlabeled_prob_mean": float(unl_prob.mean()),
        "labeled_accuracy": float(
            0.5 * (np.asarray(pos_prob > 0.5).mean() + np.asarray(neg_prob < 0.5).mean())
        ),
    }

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
        "weighted_bc_classifier": (
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
    metrics = []
    histories = {"classifier": classifier_history}
    for i, (method, (x, actions, weights)) in enumerate(train_sets.items()):
        params, history = train_bc(
            x,
            actions,
            weights,
            seed=args.seed + i,
            steps=args.steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
        )
        histories[method] = history
        row = evaluate_policy(dataset, params, obs_mean, obs_std, args.obs_keys, args, method)
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
    diagnostics_path = args.out_dir / "diagnostics.json"
    diagnostics_path.write_text(
        json.dumps(
            {
                "dataset_id": args.dataset_id,
                "split_path": str(split_path),
                "obs_keys": args.obs_keys,
                "seed": args.seed,
                "steps": args.steps,
                "classifier_steps": args.classifier_steps,
                "eval_episodes": args.eval_episodes,
                "eval_horizon": args.eval_horizon,
                "transition_counts": {
                    "positive": int(pos.actions.shape[0]),
                    "negative": int(neg.actions.shape[0]),
                    "unlabeled": int(unl.actions.shape[0]),
                },
                "classifier": classifier_metrics,
                "histories": histories,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text(
        "\n".join(
            [
                f"# Minari BC Smoke: `{args.dataset_id}`",
                "",
                f"Split path: `{split_path}`.",
                f"Observation keys: `{args.obs_keys}`.",
                f"Train steps per actor: `{args.steps}`.",
                f"Classifier steps: `{args.classifier_steps}`.",
                f"Evaluation episodes: `{args.eval_episodes}`.",
                "",
                "## Metrics",
                "",
                markdown_table(metrics),
                "",
                "## Classifier Diagnostics",
                "",
                f"- Labeled accuracy: `{classifier_metrics['labeled_accuracy']:.3f}`.",
                f"- Positive transition probability mean: `{classifier_metrics['pos_prob_mean']:.3f}`.",
                f"- Negative transition probability mean: `{classifier_metrics['neg_prob_mean']:.3f}`.",
                f"- Unlabeled transition probability mean: `{classifier_metrics['unlabeled_prob_mean']:.3f}`.",
                "",
                "## Interpretation",
                "",
                "- This is a train/eval pipeline smoke, not a final Tri-PIQL result.",
                "- `weighted_bc_classifier` is the relevant simple filtering baseline for the next Tri-PIQL comparison.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
