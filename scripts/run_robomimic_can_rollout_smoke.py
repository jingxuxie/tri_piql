from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

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
from run_minari_bc_baselines import markdown_table, predict, train_bc  # noqa: E402


@dataclass(frozen=True)
class DemoBatch:
    observations: np.ndarray
    actions: np.ndarray
    demo_ids: np.ndarray


@dataclass(frozen=True)
class EvalInitialState:
    demo_id: str
    model_file: str
    state: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_can_rollout_smoke"))
    parser.add_argument("--bc-steps", type=int, default=1000)
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--eval-episodes", type=int, default=5)
    parser.add_argument("--eval-horizon", type=int, default=400)
    parser.add_argument(
        "--eval-init-mode",
        choices=["env_reset", "valid_positive_states", "valid_all_states"],
        default="env_reset",
    )
    parser.add_argument("--candidate-count", type=int, default=32)
    parser.add_argument("--noise-stds", type=float, nargs="+", default=[0.10])
    parser.add_argument("--action-penalties", type=float, nargs="+", default=[0.05])
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


def dataset_obs_keys(hdf5_path: str) -> list[str]:
    with h5py.File(hdf5_path, "r") as f:
        first_demo = sorted(f["data"].keys(), key=demo_sort_key)[0]
        return sorted(f["data"][first_demo]["obs"].keys())


def obs_vector_from_demo(group, obs_keys: list[str]) -> np.ndarray:
    obs_group = group["obs"]
    parts = [
        np.asarray(obs_group[key], dtype=np.float32).reshape((obs_group[key].shape[0], -1))
        for key in obs_keys
    ]
    return np.concatenate(parts, axis=1)


def obs_vector_from_env(obs: dict[str, np.ndarray], obs_keys: list[str]) -> np.ndarray:
    parts = []
    for key in obs_keys:
        if key in obs:
            value = obs[key]
        elif key == "object" and "object-state" in obs:
            value = obs["object-state"]
        else:
            raise KeyError(f"observation key {key!r} not found in env obs; available keys: {sorted(obs)}")
        parts.append(np.asarray(value, dtype=np.float32).reshape(-1))
    return np.concatenate(parts, axis=0).astype(np.float32, copy=False)


def load_batch(hdf5_path: str, demo_ids: list[str], obs_keys: list[str]) -> DemoBatch:
    obs_chunks = []
    action_chunks = []
    demo_chunks = []
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted(demo_ids, key=demo_sort_key):
            group = f["data"][demo_id]
            obs_chunks.append(obs_vector_from_demo(group, obs_keys))
            actions = np.asarray(group["actions"], dtype=np.float32)
            action_chunks.append(actions)
            demo_chunks.append(np.full((actions.shape[0],), demo_sort_key(demo_id), dtype=np.int32))
    if not obs_chunks:
        raise ValueError("no demos loaded")
    return DemoBatch(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        demo_ids=np.concatenate(demo_chunks, axis=0),
    )


def load_eval_initials(hdf5_path: str, demo_ids: list[str]) -> list[EvalInitialState]:
    initials = []
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted(demo_ids, key=demo_sort_key):
            group = f["data"][demo_id]
            initials.append(
                EvalInitialState(
                    demo_id=demo_id,
                    model_file=str(group.attrs["model_file"]),
                    state=np.asarray(group["states"][0], dtype=np.float64),
                )
            )
    return initials


def normalize(train_obs: np.ndarray, *arrays: np.ndarray) -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    mean = train_obs.mean(axis=0, keepdims=True)
    std = train_obs.std(axis=0, keepdims=True) + 1.0e-6
    return mean, std, [(array - mean) / std for array in arrays]


def load_env_metadata(hdf5_path: str) -> dict:
    with h5py.File(hdf5_path, "r") as f:
        return json.loads(f["data"].attrs["env_args"])


def make_env(env_meta: dict):
    # Avoid robosuite's numba cache issue under `conda run python -c` / script execution.
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
    os.environ.setdefault("MUJOCO_GL", "egl")
    import robosuite as suite

    env_kwargs = deepcopy(env_meta["env_kwargs"])
    return suite.make(env_name=env_meta["env_name"], **env_kwargs)


def action_bounds(env) -> tuple[np.ndarray, np.ndarray]:
    if hasattr(env, "action_spec"):
        spec = env.action_spec
        if isinstance(spec, tuple) and len(spec) == 2:
            return np.asarray(spec[0], dtype=np.float32), np.asarray(spec[1], dtype=np.float32)
    return (
        -np.ones((env.action_dim,), dtype=np.float32),
        np.ones((env.action_dim,), dtype=np.float32),
    )


def env_success(env, reward: float) -> bool:
    if hasattr(env, "is_success"):
        result = env.is_success()
        if isinstance(result, dict) and "task" in result:
            return bool(result["task"])
        return bool(result)
    if hasattr(env, "_check_success"):
        return bool(env._check_success())
    return reward > 0.0


def reset_env(env, initial_state: EvalInitialState | None) -> dict[str, np.ndarray]:
    if initial_state is None:
        return env.reset()
    env.reset()
    env.reset_from_xml_string(initial_state.model_file)
    env.sim.reset()
    env.sim.set_state_from_flattened(initial_state.state)
    env.sim.forward()
    if hasattr(env, "update_state"):
        env.update_state()
    return env._get_observations(force_update=True)


def sigmoid(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    return 1.0 / (1.0 + np.exp(-np.clip(x, -60.0, 60.0)))


def classifier_logits(params, observations: np.ndarray, actions: np.ndarray) -> np.ndarray:
    return predict(params, state_action_features(observations, actions)).reshape(-1)


def rollout_policy(
    *,
    env_meta: dict,
    obs_keys: list[str],
    obs_mean: np.ndarray,
    obs_std: np.ndarray,
    eval_episodes: int,
    eval_horizon: int,
    eval_initials: list[EvalInitialState] | None,
    seed: int,
    policy_fn: Callable[[np.ndarray, np.random.Generator, np.ndarray, np.ndarray], np.ndarray],
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
            initial = None
            if eval_initials:
                initial = eval_initials[episode % len(eval_initials)]
            obs = reset_env(env, initial)
            total = 0.0
            success = False
            length = 0
            for t in range(eval_horizon):
                feature = obs_vector_from_env(obs, obs_keys)[None, :]
                feature = (feature - obs_mean) / obs_std
                action = policy_fn(feature.astype(np.float32), rng, low, high)
                action = np.clip(action, low, high)
                obs, reward, done, _info = env.step(action)
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


def bc_policy(params):
    def policy(feature: np.ndarray, _rng: np.random.Generator, _low: np.ndarray, _high: np.ndarray) -> np.ndarray:
        return predict(params, feature, batch_size=1)[0]

    return policy


def rerank_policy(
    bc_params,
    classifier_params,
    *,
    candidate_count: int,
    noise_std: float,
    action_penalty: float,
):
    def policy(feature: np.ndarray, rng: np.random.Generator, low: np.ndarray, high: np.ndarray) -> np.ndarray:
        base = np.clip(predict(bc_params, feature, batch_size=1)[0], low, high)
        candidates = np.empty((candidate_count, base.shape[0]), dtype=np.float32)
        candidates[0] = base
        if candidate_count > 1:
            noise = rng.normal(0.0, noise_std, size=(candidate_count - 1, base.shape[0])).astype(np.float32)
            candidates[1:] = np.clip(base[None, :] + noise, low, high)
        features = np.repeat(feature.astype(np.float32), candidate_count, axis=0)
        logits = classifier_logits(classifier_params, features, candidates)
        deviations = np.mean((candidates - base[None, :]) ** 2, axis=1)
        scores = logits - action_penalty * deviations
        return candidates[int(np.argmax(scores))]

    return policy


def add_method_row(
    rows: list[dict[str, float | str]],
    *,
    method: str,
    env_meta: dict,
    obs_keys: list[str],
    obs_mean: np.ndarray,
    obs_std: np.ndarray,
    args: argparse.Namespace,
    eval_initials: list[EvalInitialState] | None,
    policy_fn,
    seed_offset: int,
) -> None:
    metrics = rollout_policy(
        env_meta=env_meta,
        obs_keys=obs_keys,
        obs_mean=obs_mean,
        obs_std=obs_std,
        eval_episodes=args.eval_episodes,
        eval_horizon=args.eval_horizon,
        eval_initials=eval_initials,
        seed=args.seed + seed_offset,
        policy_fn=policy_fn,
    )
    row = {"method": method, **metrics}
    rows.append(row)
    print(
        f"{method}: success={row['success_rate']:.3f} "
        f"return={row['avg_return']:.3f} len={row['avg_len']:.1f}"
    )


def main() -> None:
    args = parse_args()
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    env_meta = load_env_metadata(hdf5_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    labeled_pos = load_batch(hdf5_path, split["labeled_positive_ids"], obs_keys)
    labeled_neg = load_batch(hdf5_path, split["labeled_negative_ids"], obs_keys)
    unlabeled = load_batch(hdf5_path, split["unlabeled_ids"], obs_keys)
    valid_pos = load_batch(hdf5_path, split["valid_positive_ids"], obs_keys)
    valid_neg = load_batch(hdf5_path, split["valid_negative_ids"], obs_keys)

    train_obs = np.concatenate([labeled_pos.observations, labeled_neg.observations, unlabeled.observations], axis=0)
    obs_mean, obs_std, normalized = normalize(
        train_obs,
        labeled_pos.observations,
        labeled_neg.observations,
        unlabeled.observations,
        valid_pos.observations,
        valid_neg.observations,
    )
    lp_obs, ln_obs, unl_obs, vp_obs, vn_obs = normalized
    labeled_pos = DemoBatch(lp_obs, labeled_pos.actions, labeled_pos.demo_ids)
    labeled_neg = DemoBatch(ln_obs, labeled_neg.actions, labeled_neg.demo_ids)
    unlabeled = DemoBatch(unl_obs, unlabeled.actions, unlabeled.demo_ids)
    valid_pos = DemoBatch(vp_obs, valid_pos.actions, valid_pos.demo_ids)
    valid_neg = DemoBatch(vn_obs, valid_neg.actions, valid_neg.demo_ids)

    eval_initials = None
    eval_initial_ids: list[str] = []
    if args.eval_init_mode == "valid_positive_states":
        eval_initial_ids = split["valid_positive_ids"]
    elif args.eval_init_mode == "valid_all_states":
        eval_initial_ids = split["valid_ids"]
    if eval_initial_ids:
        eval_initials = load_eval_initials(hdf5_path, eval_initial_ids)

    classifier, classifier_history = train_state_action_classifier(
        labeled_pos.observations,
        labeled_pos.actions,
        labeled_neg.observations,
        labeled_neg.actions,
        seed=args.seed + 10,
        steps=args.classifier_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )
    train_pos_logits = classifier_logits(classifier, labeled_pos.observations, labeled_pos.actions)
    train_neg_logits = classifier_logits(classifier, labeled_neg.observations, labeled_neg.actions)
    valid_pos_logits = classifier_logits(classifier, valid_pos.observations, valid_pos.actions)
    valid_neg_logits = classifier_logits(classifier, valid_neg.observations, valid_neg.actions)
    unl_prob = sigmoid(classifier_logits(classifier, unlabeled.observations, unlabeled.actions))

    train_sets = {
        "bc_labeled_positive": (
            labeled_pos.observations,
            labeled_pos.actions,
            np.ones((labeled_pos.actions.shape[0],), dtype=np.float32),
        ),
        "bc_pos_unlabeled": (
            np.concatenate([labeled_pos.observations, unlabeled.observations], axis=0),
            np.concatenate([labeled_pos.actions, unlabeled.actions], axis=0),
            np.ones((labeled_pos.actions.shape[0] + unlabeled.actions.shape[0],), dtype=np.float32),
        ),
        "bc_all": (
            np.concatenate([labeled_pos.observations, labeled_neg.observations, unlabeled.observations], axis=0),
            np.concatenate([labeled_pos.actions, labeled_neg.actions, unlabeled.actions], axis=0),
            np.ones((labeled_pos.actions.shape[0] + labeled_neg.actions.shape[0] + unlabeled.actions.shape[0],), dtype=np.float32),
        ),
        "weighted_bc_state_action": (
            np.concatenate([labeled_pos.observations, labeled_neg.observations, unlabeled.observations], axis=0),
            np.concatenate([labeled_pos.actions, labeled_neg.actions, unlabeled.actions], axis=0),
            np.concatenate(
                [
                    np.ones((labeled_pos.actions.shape[0],), dtype=np.float32),
                    np.zeros((labeled_neg.actions.shape[0],), dtype=np.float32),
                    unl_prob.astype(np.float32),
                ],
                axis=0,
            ),
        ),
    }

    params_by_method = {}
    histories = {"state_action_classifier": classifier_history}
    for i, (method, (obs, actions, weights)) in enumerate(train_sets.items()):
        params, history = train_bc(
            obs,
            actions,
            weights,
            seed=args.seed + 100 + i,
            steps=args.bc_steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
        )
        params_by_method[method] = params
        histories[method] = history

    rows: list[dict[str, float | str]] = []
    for i, method in enumerate(train_sets):
        add_method_row(
            rows,
            method=method,
            env_meta=env_meta,
            obs_keys=obs_keys,
            obs_mean=obs_mean,
            obs_std=obs_std,
            args=args,
            eval_initials=eval_initials,
            policy_fn=bc_policy(params_by_method[method]),
            seed_offset=10_000 + i * 1_000,
        )

    for noise_std in args.noise_stds:
        for action_penalty in args.action_penalties:
            method = f"bc_positive_sa_rerank_noise{noise_std:g}_penalty{action_penalty:g}"
            add_method_row(
                rows,
                method=method,
                env_meta=env_meta,
                obs_keys=obs_keys,
                obs_mean=obs_mean,
                obs_std=obs_std,
                args=args,
                eval_initials=eval_initials,
                policy_fn=rerank_policy(
                    params_by_method["bc_labeled_positive"],
                    classifier,
                    candidate_count=args.candidate_count,
                    noise_std=noise_std,
                    action_penalty=action_penalty,
                ),
                seed_offset=20_000 + int(noise_std * 10_000) + int(action_penalty * 1_000),
            )

    with (args.out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "success_rate", "avg_return", "avg_len"])
        writer.writeheader()
        writer.writerows(rows)

    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "obs_keys": obs_keys,
        "env_name": env_meta["env_name"],
        "env_version": env_meta.get("env_version"),
        "seed": args.seed,
        "bc_steps": args.bc_steps,
        "classifier_steps": args.classifier_steps,
        "eval_episodes": args.eval_episodes,
        "eval_horizon": args.eval_horizon,
        "eval_init_mode": args.eval_init_mode,
        "eval_initial_ids": eval_initial_ids,
        "candidate_count": args.candidate_count,
        "noise_stds": args.noise_stds,
        "action_penalties": args.action_penalties,
        "transition_counts": {
            "labeled_positive": int(labeled_pos.actions.shape[0]),
            "labeled_negative": int(labeled_neg.actions.shape[0]),
            "unlabeled": int(unlabeled.actions.shape[0]),
            "valid_positive": int(valid_pos.actions.shape[0]),
            "valid_negative": int(valid_neg.actions.shape[0]),
        },
        "state_action_classifier": {
            "train_labeled_accuracy": float(0.5 * ((train_pos_logits > 0).mean() + (train_neg_logits < 0).mean())),
            "valid_labeled_accuracy": float(0.5 * ((valid_pos_logits > 0).mean() + (valid_neg_logits < 0).mean())),
            "train_pos_logit_mean": float(train_pos_logits.mean()),
            "train_neg_logit_mean": float(train_neg_logits.mean()),
            "valid_pos_logit_mean": float(valid_pos_logits.mean()),
            "valid_neg_logit_mean": float(valid_neg_logits.mean()),
            "unlabeled_prob_mean": float(unl_prob.mean()),
        },
        "histories": histories,
    }
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report = [
        "# Robomimic Can Rollout Smoke",
        "",
        f"Split path: `{args.split_path}`.",
        f"HDF5 path: `{hdf5_path}`.",
        f"Environment: `{env_meta['env_name']}` version `{env_meta.get('env_version')}`.",
        f"Observation keys: `{obs_keys}`.",
        f"BC steps: `{args.bc_steps}`.",
        f"State-action classifier steps: `{args.classifier_steps}`.",
        f"Evaluation episodes: `{args.eval_episodes}`.",
        f"Evaluation horizon: `{args.eval_horizon}`.",
        f"Evaluation init mode: `{args.eval_init_mode}`.",
        f"Candidate count: `{args.candidate_count}`.",
        "",
        "## Rollout Metrics",
        "",
        markdown_table(rows),
        "",
        "## State-Action Classifier",
        "",
        f"- Train labeled accuracy: `{diagnostics['state_action_classifier']['train_labeled_accuracy']:.3f}`.",
        f"- Held-out validation accuracy: `{diagnostics['state_action_classifier']['valid_labeled_accuracy']:.3f}`.",
        f"- Validation positive/negative logit mean: `{diagnostics['state_action_classifier']['valid_pos_logit_mean']:.3f}` / `{diagnostics['state_action_classifier']['valid_neg_logit_mean']:.3f}`.",
        f"- Unlabeled positive probability mean: `{diagnostics['state_action_classifier']['unlabeled_prob_mean']:.3f}`.",
        "",
        "## Interpretation",
        "",
        "- This is a short simulator smoke, not a final Robomimic benchmark.",
        "- It tests whether the scarce-label policies trained from low-dimensional paired data can produce nonzero Can task success under the recovered robosuite environment.",
        "- If all policies are near zero, the immediate issue is rollout-capable imitation strength, not the tri-signal objective.",
    ]
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
