from __future__ import annotations

import argparse
import csv
import json
import sys
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_id", help="Minari dataset id")
    parser.add_argument("--split-path", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=Path("results/minari_action_rerank_smoke"))
    parser.add_argument("--obs-keys", nargs="+", default=["observation", "desired_goal"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--bc-steps", type=int, default=700)
    parser.add_argument("--classifier-steps", type=int, default=500)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--max-train-transitions", type=int, default=150_000)
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--eval-horizon", type=int, default=800)
    parser.add_argument("--candidate-count", type=int, default=64)
    parser.add_argument("--noise-stds", type=float, nargs="+", default=[0.10, 0.25])
    parser.add_argument("--action-penalties", type=float, nargs="+", default=[0.05, 0.20])
    return parser.parse_args()


def state_action_features(observations: np.ndarray, actions: np.ndarray) -> np.ndarray:
    return np.concatenate([observations, actions], axis=-1).astype(np.float32, copy=False)


def train_state_action_classifier(
    pos_obs: np.ndarray,
    pos_actions: np.ndarray,
    neg_obs: np.ndarray,
    neg_actions: np.ndarray,
    *,
    seed: int,
    steps: int,
    batch_size: int,
    hidden_dim: int,
    depth: int,
    lr: float,
) -> tuple[list[dict[str, jax.Array]], list[dict[str, float]]]:
    pos_x = jnp.asarray(state_action_features(pos_obs, pos_actions), dtype=jnp.float32)
    neg_x = jnp.asarray(state_action_features(neg_obs, neg_actions), dtype=jnp.float32)
    key = jax.random.PRNGKey(seed)
    key, init_key = jax.random.split(key)
    params = init_mlp(init_key, pos_x.shape[1], 1, hidden_dim, depth)
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))
    half_batch = max(1, batch_size // 2)

    def loss_fn(local_params, pos_idx, neg_idx):
        pos_logits = mlp_apply(local_params, pos_x[pos_idx]).reshape(-1)
        neg_logits = mlp_apply(local_params, neg_x[neg_idx]).reshape(-1)
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


def predict_logits(params, features: np.ndarray, batch_size: int = 65_536) -> np.ndarray:
    return predict(params, features, batch_size=batch_size).reshape(-1)


def classifier_metrics(params, pos: TransitionData, neg: TransitionData, unl: TransitionData) -> dict[str, float]:
    pos_logits = predict_logits(params, state_action_features(pos.observations, pos.actions))
    neg_logits = predict_logits(params, state_action_features(neg.observations, neg.actions))
    unl_logits = predict_logits(params, state_action_features(unl.observations, unl.actions))
    pos_prob = 1.0 / (1.0 + np.exp(-pos_logits))
    neg_prob = 1.0 / (1.0 + np.exp(-neg_logits))
    unl_prob = 1.0 / (1.0 + np.exp(-unl_logits))
    return {
        "pos_prob_mean": float(pos_prob.mean()),
        "neg_prob_mean": float(neg_prob.mean()),
        "unlabeled_prob_mean": float(unl_prob.mean()),
        "labeled_accuracy": float(0.5 * ((pos_prob > 0.5).mean() + (neg_prob < 0.5).mean())),
        "pos_logit_mean": float(pos_logits.mean()),
        "neg_logit_mean": float(neg_logits.mean()),
        "unlabeled_logit_mean": float(unl_logits.mean()),
    }


def evaluate_rerank_policy(
    dataset,
    bc_params,
    classifier_params,
    obs_mean,
    obs_std,
    obs_keys: list[str],
    args: argparse.Namespace,
    method: str,
    *,
    noise_std: float,
    action_penalty: float,
) -> dict[str, float | str]:
    env = dataset.recover_environment()
    returns = []
    lengths = []
    successes = []
    action_low = np.asarray(env.action_space.low, dtype=np.float32)
    action_high = np.asarray(env.action_space.high, dtype=np.float32)
    rng = np.random.default_rng(args.seed + int(10_000 * noise_std) + int(1_000 * action_penalty))
    for episode in range(args.eval_episodes):
        obs, _ = env.reset(seed=args.seed + 20_000 + episode)
        total = 0.0
        success = False
        length = 0
        for t in range(args.eval_horizon):
            has_success_signal = False
            feature = obs_features(obs, obs_keys)[None, :]
            feature_norm = (feature - obs_mean) / obs_std
            base = predict(bc_params, feature_norm, batch_size=1)[0]
            base = np.clip(base, action_low, action_high)
            candidates = np.empty((args.candidate_count, base.shape[0]), dtype=np.float32)
            candidates[0] = base
            if args.candidate_count > 1:
                noise = rng.normal(0.0, noise_std, size=(args.candidate_count - 1, base.shape[0])).astype(np.float32)
                candidates[1:] = np.clip(base[None, :] + noise, action_low, action_high)
            obs_repeated = np.repeat(feature_norm.astype(np.float32), args.candidate_count, axis=0)
            logits = predict_logits(classifier_params, state_action_features(obs_repeated, candidates))
            deviations = np.mean((candidates - base[None, :]) ** 2, axis=1)
            scores = logits - action_penalty * deviations
            action = candidates[int(np.argmax(scores))]
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


def main() -> None:
    args = parse_args()
    import minari

    split_path = args.split_path or default_split_path(args.dataset_id)
    split = json.loads(split_path.read_text(encoding="utf-8"))
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

    bc_params, bc_history = train_bc(
        pos.observations,
        pos.actions,
        np.ones((pos.actions.shape[0],), dtype=np.float32),
        seed=args.seed + 10,
        steps=args.bc_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )

    obs_classifier, obs_classifier_history = train_transition_classifier(
        pos.observations,
        neg.observations,
        seed=args.seed + 20,
        steps=args.classifier_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )
    unl_obs_prob = np.asarray(jax.nn.sigmoid(jnp.asarray(predict(obs_classifier, unl.observations).reshape(-1))))
    weighted_bc_x = np.concatenate([pos.observations, neg.observations, unl.observations], axis=0)
    weighted_bc_a = np.concatenate([pos.actions, neg.actions, unl.actions], axis=0)
    weighted_bc_w = np.concatenate(
        [
            np.ones((pos.actions.shape[0],), dtype=np.float32),
            np.zeros((neg.actions.shape[0],), dtype=np.float32),
            unl_obs_prob.astype(np.float32),
        ],
        axis=0,
    )
    weighted_bc_params, weighted_bc_history = train_bc(
        weighted_bc_x,
        weighted_bc_a,
        weighted_bc_w,
        seed=args.seed + 30,
        steps=args.bc_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )

    sa_classifier, sa_classifier_history = train_state_action_classifier(
        pos.observations,
        pos.actions,
        neg.observations,
        neg.actions,
        seed=args.seed + 40,
        steps=args.classifier_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )
    sa_metrics = classifier_metrics(sa_classifier, pos, neg, unl)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    metrics = [
        evaluate_policy(dataset, bc_params, obs_mean, obs_std, args.obs_keys, args, "bc_positive"),
        evaluate_policy(dataset, weighted_bc_params, obs_mean, obs_std, args.obs_keys, args, "weighted_bc_obs_classifier"),
    ]
    for noise_std in args.noise_stds:
        for action_penalty in args.action_penalties:
            method = f"bc_sa_rerank_noise{noise_std:g}_penalty{action_penalty:g}"
            row = evaluate_rerank_policy(
                dataset,
                bc_params,
                sa_classifier,
                obs_mean,
                obs_std,
                args.obs_keys,
                args,
                method,
                noise_std=noise_std,
                action_penalty=action_penalty,
            )
            metrics.append(row)
            print(
                f"{method}: success={row['success_rate']:.3f} "
                f"return={row['avg_return']:.3f} len={row['avg_len']:.1f}"
            )
    for row in metrics[:2]:
        print(
            f"{row['method']}: success={row['success_rate']:.3f} "
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
        "obs_keys": args.obs_keys,
        "seed": args.seed,
        "bc_steps": args.bc_steps,
        "classifier_steps": args.classifier_steps,
        "eval_episodes": args.eval_episodes,
        "eval_horizon": args.eval_horizon,
        "candidate_count": args.candidate_count,
        "noise_stds": args.noise_stds,
        "action_penalties": args.action_penalties,
        "transition_counts": {
            "positive": int(pos.actions.shape[0]),
            "negative": int(neg.actions.shape[0]),
            "unlabeled": int(unl.actions.shape[0]),
        },
        "state_action_classifier": sa_metrics,
        "histories": {
            "bc_positive": bc_history,
            "weighted_bc_obs_classifier": weighted_bc_history,
            "obs_classifier": obs_classifier_history,
            "state_action_classifier": sa_classifier_history,
        },
    }
    diagnostics_path = args.out_dir / "diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report_path = args.out_dir / "REPORT.md"
    report_path.write_text(
        "\n".join(
            [
                f"# Minari Action Rerank Smoke: `{args.dataset_id}`",
                "",
                f"Split path: `{split_path}`.",
                f"Observation keys: `{args.obs_keys}`.",
                f"BC steps: `{args.bc_steps}`.",
                f"State-action classifier steps: `{args.classifier_steps}`.",
                f"Evaluation episodes: `{args.eval_episodes}`.",
                f"Candidate count: `{args.candidate_count}`.",
                "",
                "## Metrics",
                "",
                markdown_table(metrics),
                "",
                "## State-Action Classifier Diagnostics",
                "",
                f"- Labeled accuracy: `{sa_metrics['labeled_accuracy']:.3f}`.",
                f"- Positive/negative/unlabeled probability mean: `{sa_metrics['pos_prob_mean']:.3f}` / `{sa_metrics['neg_prob_mean']:.3f}` / `{sa_metrics['unlabeled_prob_mean']:.3f}`.",
                f"- Positive/negative/unlabeled logit mean: `{sa_metrics['pos_logit_mean']:.3f}` / `{sa_metrics['neg_logit_mean']:.3f}` / `{sa_metrics['unlabeled_logit_mean']:.3f}`.",
                "",
                "## Interpretation",
                "",
                "- This tests policy extraction by keeping positive BC as the anchor and using a learned state-action quality score only to rerank nearby candidate actions.",
                "- A positive result would show that bad-action information is useful without retraining the actor on noisy advantage weights.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
