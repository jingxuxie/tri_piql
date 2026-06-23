from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import jax
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_minari_bc_baselines import markdown_table  # noqa: E402
from run_robomimic_can_rollout_smoke import (  # noqa: E402
    DemoBatch,
    action_bounds,
    dataset_obs_keys,
    env_success,
    load_env_metadata,
    load_eval_initials,
    make_env,
    obs_vector_from_env,
    reset_env,
)
from run_robomimic_gmm_smoke import (  # noqa: E402
    build_library,
    gmm_predict_np,
    source_batches,
    train_gmm_policy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_can_window_gmm_smoke"))
    parser.add_argument(
        "--source",
        choices=[
            "labeled_positive",
            "positive_plus_classifier_unlabeled",
            "positive_plus_classifier_top_unlabeled_demos",
            "positive_plus_classifier_diverse_unlabeled_demos",
            "positive_plus_classifier_gap_unlabeled_demos",
            "all_train_positive",
        ],
        default="positive_plus_classifier_gap_unlabeled_demos",
    )
    parser.add_argument("--eval-init-mode", choices=["env_reset", "valid_positive_states"], default="valid_positive_states")
    parser.add_argument("--eval-episodes", type=int, default=5)
    parser.add_argument("--eval-horizon", type=int, default=400)
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument("--eval-checkpoints", type=int, nargs="*", default=[])
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--components", type=int, default=5)
    parser.add_argument("--context-len", type=int, default=4)
    parser.add_argument("--include-time", action="store_true")
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
    parser.add_argument("--unlabeled-weight-mode", choices=["one", "prob"], default="prob")
    parser.add_argument("--policy-modes", nargs="+", choices=["mode", "mean", "sample"], default=["mode"])
    parser.add_argument("--sample-temperature", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def normalize_features(train_x: np.ndarray, *arrays: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    mean = train_x.mean(axis=0, keepdims=True)
    std = train_x.std(axis=0, keepdims=True) + 1.0e-6
    return mean, std, [((array - mean) / std).astype(np.float32) for array in arrays]


def make_window_features(
    obs: np.ndarray,
    actions: np.ndarray,
    demo_ids: np.ndarray,
    *,
    context_len: int,
    include_time: bool,
) -> np.ndarray:
    if context_len < 1:
        raise ValueError("context_len must be at least 1")
    obs_dim = obs.shape[1]
    action_dim = actions.shape[1]
    feature_dim = context_len * obs_dim + context_len * action_dim + (1 if include_time else 0)
    features = np.zeros((obs.shape[0], feature_dim), dtype=np.float32)
    offset_actions = context_len * obs_dim
    offset_time = offset_actions + context_len * action_dim

    for demo_id in np.unique(demo_ids):
        idx = np.flatnonzero(demo_ids == demo_id)
        local_obs = obs[idx]
        local_actions = actions[idx]
        denom = max(1, idx.shape[0] - 1)
        for local_t, global_i in enumerate(idx):
            for slot in range(context_len):
                obs_src = local_t - (context_len - 1 - slot)
                if obs_src >= 0:
                    start = slot * obs_dim
                    features[global_i, start : start + obs_dim] = local_obs[obs_src]
                act_src = local_t - (context_len - slot)
                if act_src >= 0:
                    start = offset_actions + slot * action_dim
                    features[global_i, start : start + action_dim] = local_actions[act_src]
            if include_time:
                features[global_i, offset_time] = min(1.0, float(local_t) / float(denom))
    return features


def eval_window_feature(
    obs_history: list[np.ndarray],
    action_history: list[np.ndarray],
    *,
    context_len: int,
    obs_dim: int,
    action_dim: int,
    include_time: bool,
    t: int,
    eval_horizon: int,
) -> np.ndarray:
    feature_dim = context_len * obs_dim + context_len * action_dim + (1 if include_time else 0)
    feature = np.zeros((feature_dim,), dtype=np.float32)
    offset_actions = context_len * obs_dim
    offset_time = offset_actions + context_len * action_dim

    obs_tail = obs_history[-context_len:]
    obs_pad = context_len - len(obs_tail)
    for slot, item in enumerate(obs_tail, start=obs_pad):
        start = slot * obs_dim
        feature[start : start + obs_dim] = item

    action_tail = action_history[-context_len:]
    action_pad = context_len - len(action_tail)
    for slot, item in enumerate(action_tail, start=action_pad):
        start = offset_actions + slot * action_dim
        feature[start : start + action_dim] = item

    if include_time:
        feature[offset_time] = min(1.0, float(t) / float(max(1, eval_horizon - 1)))
    return feature


def gmm_action(
    params,
    feature: np.ndarray,
    *,
    components: int,
    action_dim: int,
    min_log_std: float,
    max_log_std: float,
    mode: str,
    sample_temperature: float,
    rng: np.random.Generator,
) -> np.ndarray:
    logits, means, log_stds = gmm_predict_np(
        params,
        feature[None, :],
        components=components,
        action_dim=action_dim,
        min_log_std=min_log_std,
        max_log_std=max_log_std,
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
        component = int(rng.choice(components, p=probs))
        std = np.exp(local_log_stds[component]) * sample_temperature
        return rng.normal(local_means[component], std).astype(np.float32)
    raise ValueError(mode)


def rollout_window_policy(
    *,
    params,
    env_meta: dict,
    obs_keys: list[str],
    obs_mean: np.ndarray,
    obs_std: np.ndarray,
    window_mean: np.ndarray,
    window_std: np.ndarray,
    eval_episodes: int,
    eval_horizon: int,
    eval_initials,
    seed: int,
    args: argparse.Namespace,
    action_dim: int,
    mode: str,
) -> dict[str, float]:
    env = make_env(env_meta)
    low, high = action_bounds(env)
    returns = []
    lengths = []
    successes = []
    rng = np.random.default_rng(seed)
    np.random.seed(seed)
    obs_dim = int(obs_mean.shape[1])
    try:
        for episode in range(eval_episodes):
            np.random.seed(seed + episode)
            initial = eval_initials[episode % len(eval_initials)] if eval_initials else None
            obs = reset_env(env, initial)
            obs_history: list[np.ndarray] = []
            action_history: list[np.ndarray] = []
            total = 0.0
            success = False
            length = 0
            for t in range(eval_horizon):
                raw_obs = obs_vector_from_env(obs, obs_keys)[None, :]
                norm_obs = ((raw_obs - obs_mean) / obs_std).reshape(-1).astype(np.float32)
                obs_history.append(norm_obs)
                raw_feature = eval_window_feature(
                    obs_history,
                    action_history,
                    context_len=args.context_len,
                    obs_dim=obs_dim,
                    action_dim=action_dim,
                    include_time=args.include_time,
                    t=t,
                    eval_horizon=eval_horizon,
                )[None, :]
                feature = ((raw_feature - window_mean) / window_std).reshape(-1).astype(np.float32)
                action = gmm_action(
                    params,
                    feature,
                    components=args.components,
                    action_dim=action_dim,
                    min_log_std=args.min_log_std,
                    max_log_std=args.max_log_std,
                    mode=mode,
                    sample_temperature=args.sample_temperature,
                    rng=rng,
                )
                action = np.clip(action, low, high).astype(np.float32, copy=False)
                obs, reward, done, _info = env.step(action)
                action_history.append(action)
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
    args.feature_mode = "obs"
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
    del classifier
    action_dim = int(library.actions.shape[1])
    raw_window = make_window_features(
        library.observations,
        library.actions,
        library.demo_ids,
        context_len=args.context_len,
        include_time=args.include_time,
    )
    window_mean, window_std, [window_x] = normalize_features(raw_window, raw_window)
    checkpoint_steps = sorted({step for step in [*args.eval_checkpoints, args.steps] if 1 <= step <= args.steps})

    params, gmm_history, checkpoints = train_gmm_policy(
        window_x,
        library.actions,
        weights,
        seed=args.seed + 701,
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
    checkpoints.setdefault(args.steps, params)

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
            method = f"window{args.context_len}_gmm_{mode}_{args.source}"
            if args.include_time:
                method = f"{method}_time"
            if include_step_suffix:
                method = f"{method}_step{checkpoint_step}"
            metrics = rollout_window_policy(
                params=checkpoint_params,
                env_meta=env_meta,
                obs_keys=obs_keys,
                obs_mean=obs_mean,
                obs_std=obs_std,
                window_mean=window_mean,
                window_std=window_std,
                eval_episodes=args.eval_episodes,
                eval_horizon=args.eval_horizon,
                eval_initials=eval_initials,
                seed=args.seed + 3000 + 37 * len(rows),
                args=args,
                action_dim=action_dim,
                mode=mode,
            )
            row = {"method": method, "checkpoint_step": checkpoint_step, **metrics}
            rows.append(row)
            print(
                f"{method}: success={row['success_rate']:.3f} "
                f"return={row['avg_return']:.3f} len={row['avg_len']:.1f}"
            )

    with (args.out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "checkpoint_step", "success_rate", "avg_return", "avg_len"])
        writer.writeheader()
        writer.writerows(rows)

    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "source": args.source,
        "seed": args.seed,
        "source_transition_count": int(library.actions.shape[0]),
        "selected_unlabeled_transitions": int(selected_unlabeled),
        "selected_unlabeled_demos": selected_demo_ids,
        "selected_hidden_positive_demos": int(selected_hidden_positive_demos),
        "selection_diagnostics": selection_diagnostics,
        "classifier": classifier_metrics,
        "context_len": int(args.context_len),
        "include_time": bool(args.include_time),
        "window_feature_dim": int(window_x.shape[1]),
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
        "policy_modes": args.policy_modes,
        "sample_temperature": args.sample_temperature,
        "gmm_history": gmm_history,
    }
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report = [
        "# Robomimic Can Window-GMM Policy Smoke",
        "",
        f"Split path: `{args.split_path}`.",
        f"Seed: `{args.seed}`.",
        f"Source: `{args.source}`.",
        f"Context length: `{args.context_len}`.",
        f"Include time: `{args.include_time}`.",
        f"Window feature dimension: `{window_x.shape[1]}`.",
        f"Source transitions: `{library.actions.shape[0]}`.",
        f"Selected unlabeled transitions: `{selected_unlabeled}`.",
        f"Selected unlabeled demos: `{len(selected_demo_ids)}`.",
        f"Selected hidden-positive demos: `{selected_hidden_positive_demos}`.",
        f"Selection diagnostics: `{selection_diagnostics}`.",
        f"Components: `{args.components}`.",
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
        "- This tests whether fixed-length observation/action history improves the local GMM extractor while keeping the same score-gap selected support.",
        "- It is a fast local substitute for a full recurrent Robomimic BC backbone.",
    ]
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
