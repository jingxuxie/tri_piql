from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_minari_bc_baselines import normalize, predict, train_bc  # noqa: E402
from run_minari_action_rerank_smoke import (  # noqa: E402
    state_action_features,
    train_state_action_classifier,
)


@dataclass(frozen=True)
class PointSpec:
    start: tuple[float, float] = (0.08, 0.08)
    goal: tuple[float, float] = (0.92, 0.92)
    trap: tuple[float, float] = (0.50, 0.50)
    goal_radius: float = 0.075
    trap_radius: float = 0.105
    max_action: float = 0.045
    max_steps: int = 70


@dataclass(frozen=True)
class Trajectory:
    observations: np.ndarray
    actions: np.ndarray
    hidden_good: bool
    label: str

    @property
    def length(self) -> int:
        return int(self.actions.shape[0])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/continuous_pointnav_smoke"))
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--bad-fracs", type=float, nargs="+", default=[0.50, 0.75, 0.90])
    parser.add_argument("--n-pos", type=int, default=10)
    parser.add_argument("--n-neg", type=int, default=20)
    parser.add_argument("--n-unlabeled", type=int, default=180)
    parser.add_argument("--positive-prefix-steps", type=int, default=16)
    parser.add_argument("--bc-steps", type=int, default=12000)
    parser.add_argument("--classifier-steps", type=int, default=3000)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--eval-episodes", type=int, default=30)
    parser.add_argument("--eval-noise", type=float, default=0.015)
    parser.add_argument("--candidate-count", type=int, default=64)
    parser.add_argument("--noise-std", type=float, default=0.035)
    parser.add_argument("--action-penalty", type=float, default=0.10)
    parser.add_argument("--top-unlabeled-frac", type=float, default=0.25)
    parser.add_argument("--top-unlabeled-fracs", type=float, nargs="+", default=None)
    parser.add_argument("--gap-select-max-fracs", type=float, nargs="+", default=[])
    parser.add_argument("--gap-select-min-frac", type=float, default=0.02)
    parser.add_argument("--posterior-priors", type=float, nargs="+", default=[])
    parser.add_argument("--posterior-temperature", type=float, default=0.05)
    return parser.parse_args()


def clip_action(action: np.ndarray, spec: PointSpec) -> np.ndarray:
    return np.clip(action, -spec.max_action, spec.max_action).astype(np.float32)


def action_toward(position: np.ndarray, target: np.ndarray, spec: PointSpec, rng: np.random.Generator, noise: float) -> np.ndarray:
    delta = target - position
    norm = float(np.linalg.norm(delta))
    if norm > spec.max_action:
        delta = delta / (norm + 1.0e-8) * spec.max_action
    action = delta + rng.normal(0.0, noise, size=2)
    return clip_action(action, spec)


def rollout_waypoints(
    spec: PointSpec,
    waypoints: list[tuple[float, float]],
    *,
    rng: np.random.Generator,
    noise: float,
    label: str,
    hidden_good: bool,
    prefix_steps: int | None = None,
) -> Trajectory:
    position = np.asarray(spec.start, dtype=np.float32)
    observations: list[np.ndarray] = []
    actions: list[np.ndarray] = []
    waypoint_idx = 0
    for _ in range(spec.max_steps):
        target = np.asarray(waypoints[min(waypoint_idx, len(waypoints) - 1)], dtype=np.float32)
        if np.linalg.norm(position - target) < 0.025 and waypoint_idx < len(waypoints) - 1:
            waypoint_idx += 1
            target = np.asarray(waypoints[waypoint_idx], dtype=np.float32)
        action = action_toward(position, target, spec, rng, noise)
        observations.append(position.copy())
        actions.append(action.copy())
        position = np.clip(position + action, 0.0, 1.0).astype(np.float32)
        if prefix_steps is not None and len(actions) >= prefix_steps:
            break
        if np.linalg.norm(position - np.asarray(spec.goal, dtype=np.float32)) < spec.goal_radius:
            break
        if np.linalg.norm(position - np.asarray(spec.trap, dtype=np.float32)) < spec.trap_radius:
            break
    return Trajectory(
        observations=np.asarray(observations, dtype=np.float32),
        actions=np.asarray(actions, dtype=np.float32),
        hidden_good=hidden_good,
        label=label,
    )


def make_dataset(args: argparse.Namespace, spec: PointSpec, seed: int, bad_frac: float) -> dict[str, list[Trajectory]]:
    rng = np.random.default_rng(seed)
    safe_waypoints = [(0.08, 0.92), spec.goal]
    bad_waypoints = [spec.trap, spec.goal]
    positives = [
        rollout_waypoints(
            spec,
            safe_waypoints,
            rng=rng,
            noise=0.004,
            label="+",
            hidden_good=True,
            prefix_steps=args.positive_prefix_steps,
        )
        for _ in range(args.n_pos)
    ]
    negatives = [
        rollout_waypoints(
            spec,
            bad_waypoints,
            rng=rng,
            noise=0.006,
            label="-",
            hidden_good=False,
        )
        for _ in range(args.n_neg)
    ]
    unlabeled = []
    for _ in range(args.n_unlabeled):
        if rng.random() < bad_frac:
            unlabeled.append(
                rollout_waypoints(spec, bad_waypoints, rng=rng, noise=0.010, label="u", hidden_good=False)
            )
        else:
            unlabeled.append(
                rollout_waypoints(spec, safe_waypoints, rng=rng, noise=0.010, label="u", hidden_good=True)
            )
    return {"pos": positives, "neg": negatives, "unlabeled": unlabeled}


def flatten(trajs: list[Trajectory]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    observations = np.concatenate([traj.observations for traj in trajs], axis=0)
    actions = np.concatenate([traj.actions for traj in trajs], axis=0)
    hidden_good = np.concatenate(
        [np.full((traj.length,), float(traj.hidden_good), dtype=np.float32) for traj in trajs],
        axis=0,
    )
    return observations, actions, hidden_good


def normalize_obs(obs: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((obs - mean) / std).astype(np.float32, copy=False)


def sigmoid(logits: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(logits, -60.0, 60.0)))


def frac_tag(value: float) -> str:
    return f"{value:.3g}".replace(".", "p")


def stable_method_offset(method: str) -> int:
    value = 17
    for char in method:
        value = (value * 131 + ord(char)) % 100_000
    return value


def calibrate_posteriors(scores: np.ndarray, prior: float, temperature: float) -> tuple[np.ndarray, float]:
    prior = float(np.clip(prior, 1.0e-4, 1.0 - 1.0e-4))
    temperature = max(float(temperature), 1.0e-4)
    low = float(scores.min() - 20.0 * temperature)
    high = float(scores.max() + 20.0 * temperature)
    for _ in range(80):
        mid = 0.5 * (low + high)
        q = sigmoid((scores - mid) / temperature)
        if float(q.mean()) > prior:
            low = mid
        else:
            high = mid
    bias = 0.5 * (low + high)
    return sigmoid((scores - bias) / temperature).astype(np.float32), bias


def select_by_score_gap(scores: np.ndarray, max_frac: float, min_frac: float) -> tuple[int, float]:
    max_count = max(1, int(round(float(max_frac) * len(scores))))
    max_count = min(max_count, len(scores))
    min_count = max(1, int(round(float(min_frac) * len(scores))))
    min_count = min(min_count, max_count)
    if max_count <= min_count:
        return max_count, 0.0
    diffs = scores[: max_count - 1] - scores[1:max_count]
    start = min_count - 1
    local_idx = int(np.argmax(diffs[start:]))
    cut_idx = start + local_idx
    return cut_idx + 1, float(diffs[cut_idx])


def evaluate_policy(
    spec: PointSpec,
    params,
    obs_mean: np.ndarray,
    obs_std: np.ndarray,
    *,
    seed: int,
    episodes: int,
    eval_noise: float,
    classifier_params=None,
    candidate_count: int = 64,
    noise_std: float = 0.035,
    action_penalty: float = 0.10,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    successes = []
    traps = []
    lengths = []
    returns = []
    goal = np.asarray(spec.goal, dtype=np.float32)
    trap = np.asarray(spec.trap, dtype=np.float32)
    for _ in range(episodes):
        position = np.asarray(spec.start, dtype=np.float32) + rng.normal(0.0, eval_noise, size=2)
        position = np.clip(position, 0.0, 1.0).astype(np.float32)
        success = False
        hit_trap = False
        total = 0.0
        length = spec.max_steps
        for t in range(spec.max_steps):
            obs = ((position[None, :] - obs_mean) / obs_std).astype(np.float32)
            base = clip_action(predict(params, obs, batch_size=1)[0], spec)
            if classifier_params is None:
                action = base
            else:
                candidates = np.empty((candidate_count, 2), dtype=np.float32)
                candidates[0] = base
                noise = rng.normal(0.0, noise_std, size=(candidate_count - 1, 2)).astype(np.float32)
                candidates[1:] = np.clip(base[None, :] + noise, -spec.max_action, spec.max_action)
                repeated = np.repeat(obs, candidate_count, axis=0)
                logits = predict(classifier_params, state_action_features(repeated, candidates), batch_size=65_536).reshape(-1)
                deviations = np.mean((candidates - base[None, :]) ** 2, axis=1)
                action = candidates[int(np.argmax(logits - action_penalty * deviations))]
            position = np.clip(position + action, 0.0, 1.0).astype(np.float32)
            total -= 0.01
            length = t + 1
            if np.linalg.norm(position - trap) < spec.trap_radius:
                hit_trap = True
                total -= 1.0
                break
            if np.linalg.norm(position - goal) < spec.goal_radius:
                success = True
                total += 1.0
                break
        successes.append(float(success))
        traps.append(float(hit_trap))
        lengths.append(float(length))
        returns.append(float(total))
    return {
        "success_rate": float(np.mean(successes)),
        "trap_rate": float(np.mean(traps)),
        "avg_return": float(np.mean(returns)),
        "avg_len": float(np.mean(lengths)),
    }


def run_one(args: argparse.Namespace, seed: int, bad_frac: float) -> tuple[list[dict], dict]:
    spec = PointSpec()
    top_fracs = args.top_unlabeled_fracs if args.top_unlabeled_fracs is not None else [args.top_unlabeled_frac]
    posterior_priors = args.posterior_priors
    data = make_dataset(args, spec, seed, bad_frac)
    pos_obs, pos_actions, _ = flatten(data["pos"])
    neg_obs, neg_actions, _ = flatten(data["neg"])
    unl_obs, unl_actions, unl_good = flatten(data["unlabeled"])
    hidden_good_trajs = [traj for traj in data["unlabeled"] if traj.hidden_good]
    oracle_obs, oracle_actions, _ = flatten(data["pos"] + hidden_good_trajs)

    train_obs = np.concatenate([pos_obs, neg_obs, unl_obs], axis=0)
    obs_mean, obs_std, [pos_x, neg_x, unl_x, oracle_x] = normalize(train_obs, pos_obs, neg_obs, unl_obs, oracle_obs)
    classifier, classifier_history = train_state_action_classifier(
        pos_x,
        pos_actions,
        neg_x,
        neg_actions,
        seed=seed + 11,
        steps=args.classifier_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )
    unl_prob = sigmoid(predict(classifier, state_action_features(unl_x, unl_actions)).reshape(-1))
    pos_prob = sigmoid(predict(classifier, state_action_features(pos_x, pos_actions)).reshape(-1))
    neg_prob = sigmoid(predict(classifier, state_action_features(neg_x, neg_actions)).reshape(-1))
    scored_unlabeled = []
    for traj in data["unlabeled"]:
        traj_x = normalize_obs(traj.observations, obs_mean, obs_std)
        traj_prob = sigmoid(predict(classifier, state_action_features(traj_x, traj.actions)).reshape(-1))
        scored_unlabeled.append((float(traj_prob.mean()), traj))
    scored_unlabeled.sort(key=lambda item: item[0], reverse=True)
    traj_scores = np.asarray([score for score, _traj in scored_unlabeled], dtype=np.float32)
    selected_by_frac = {}
    selected_stats_by_frac = {}
    for top_frac in top_fracs:
        top_count = max(1, int(round(top_frac * len(scored_unlabeled))))
        selected_unlabeled = [traj for _score, traj in scored_unlabeled[:top_count]]
        selected_obs_raw, selected_actions, selected_good = flatten(selected_unlabeled)
        selected_x = normalize_obs(selected_obs_raw, obs_mean, obs_std)
        selected_by_frac[top_frac] = (selected_x, selected_actions)
        selected_stats_by_frac[str(top_frac)] = {
            "count": len(selected_unlabeled),
            "hidden_good": int(sum(traj.hidden_good for traj in selected_unlabeled)),
            "hidden_bad": int(sum(not traj.hidden_good for traj in selected_unlabeled)),
            "selected_transitions": int(selected_actions.shape[0]),
            "selected_hidden_good_transitions": int(selected_good.sum()),
            "selected_hidden_bad_transitions": int((1.0 - selected_good).sum()),
            "score_mean": float(np.mean([score for score, _traj in scored_unlabeled[:top_count]])),
        }
    selected_by_gap = {}
    selected_stats_by_gap = {}
    for max_frac in args.gap_select_max_fracs:
        top_count, gap = select_by_score_gap(traj_scores, max_frac, args.gap_select_min_frac)
        selected_unlabeled = [traj for _score, traj in scored_unlabeled[:top_count]]
        selected_obs_raw, selected_actions, selected_good = flatten(selected_unlabeled)
        selected_x = normalize_obs(selected_obs_raw, obs_mean, obs_std)
        selected_by_gap[max_frac] = (selected_x, selected_actions, top_count / len(scored_unlabeled))
        selected_stats_by_gap[str(max_frac)] = {
            "count": len(selected_unlabeled),
            "selected_frac": float(top_count / len(scored_unlabeled)),
            "max_frac": float(max_frac),
            "min_frac": float(args.gap_select_min_frac),
            "score_gap": float(gap),
            "hidden_good": int(sum(traj.hidden_good for traj in selected_unlabeled)),
            "hidden_bad": int(sum(not traj.hidden_good for traj in selected_unlabeled)),
            "selected_transitions": int(selected_actions.shape[0]),
            "selected_hidden_good_transitions": int(selected_good.sum()),
            "selected_hidden_bad_transitions": int((1.0 - selected_good).sum()),
            "score_mean": float(np.mean([score for score, _traj in scored_unlabeled[:top_count]])),
        }
    posterior_by_prior = {}
    posterior_stats_by_prior = {}
    for prior in posterior_priors:
        q_traj, bias = calibrate_posteriors(traj_scores, prior, args.posterior_temperature)
        weighted_obs = []
        weighted_actions = []
        weighted_weights = []
        demo_good_weight = 0.0
        demo_bad_weight = 0.0
        transition_good_weight = 0.0
        transition_bad_weight = 0.0
        for q_value, (_score, traj) in zip(q_traj, scored_unlabeled, strict=True):
            traj_x = normalize_obs(traj.observations, obs_mean, obs_std)
            weight = np.full((traj.length,), float(q_value), dtype=np.float32)
            weighted_obs.append(traj_x)
            weighted_actions.append(traj.actions)
            weighted_weights.append(weight)
            if traj.hidden_good:
                demo_good_weight += float(q_value)
                transition_good_weight += float(weight.sum())
            else:
                demo_bad_weight += float(q_value)
                transition_bad_weight += float(weight.sum())
        obs_weighted = np.concatenate(weighted_obs, axis=0)
        actions_weighted = np.concatenate(weighted_actions, axis=0)
        weights_weighted = np.concatenate(weighted_weights, axis=0)
        posterior_by_prior[prior] = (obs_weighted, actions_weighted, weights_weighted)
        posterior_stats_by_prior[str(prior)] = {
            "prior": float(prior),
            "temperature": float(args.posterior_temperature),
            "bias": float(bias),
            "posterior_mean": float(q_traj.mean()),
            "demo_good_weight": float(demo_good_weight),
            "demo_bad_weight": float(demo_bad_weight),
            "demo_weight_purity": float(demo_good_weight / max(1.0e-8, demo_good_weight + demo_bad_weight)),
            "transition_good_weight": float(transition_good_weight),
            "transition_bad_weight": float(transition_bad_weight),
            "transition_weight_purity": float(
                transition_good_weight / max(1.0e-8, transition_good_weight + transition_bad_weight)
            ),
        }

    train_sets = {
        "bc_positive_prefix": (
            pos_x,
            pos_actions,
            np.ones((pos_actions.shape[0],), dtype=np.float32),
        ),
        "bc_pos_unlabeled": (
            np.concatenate([pos_x, unl_x], axis=0),
            np.concatenate([pos_actions, unl_actions], axis=0),
            np.ones((pos_actions.shape[0] + unl_actions.shape[0],), dtype=np.float32),
        ),
        "bc_all": (
            np.concatenate([pos_x, neg_x, unl_x], axis=0),
            np.concatenate([pos_actions, neg_actions, unl_actions], axis=0),
            np.ones((pos_actions.shape[0] + neg_actions.shape[0] + unl_actions.shape[0],), dtype=np.float32),
        ),
        "weighted_bc_state_action": (
            np.concatenate([pos_x, neg_x, unl_x], axis=0),
            np.concatenate([pos_actions, neg_actions, unl_actions], axis=0),
            np.concatenate(
                [
                    np.ones((pos_actions.shape[0],), dtype=np.float32),
                    np.zeros((neg_actions.shape[0],), dtype=np.float32),
                    unl_prob.astype(np.float32),
                ],
                axis=0,
            ),
        ),
        "oracle_good_bc": (
            oracle_x,
            oracle_actions,
            np.ones((oracle_actions.shape[0],), dtype=np.float32),
        ),
    }
    for top_frac, (selected_x, selected_actions) in selected_by_frac.items():
        method = f"tri_signal_top_demo_bc_frac{frac_tag(top_frac)}"
        train_sets[method] = (
            np.concatenate([pos_x, selected_x], axis=0),
            np.concatenate([pos_actions, selected_actions], axis=0),
            np.ones((pos_actions.shape[0] + selected_actions.shape[0],), dtype=np.float32),
        )
    for max_frac, (selected_x, selected_actions, selected_frac) in selected_by_gap.items():
        method = f"tri_signal_gap_demo_bc_max{frac_tag(max_frac)}"
        train_sets[method] = (
            np.concatenate([pos_x, selected_x], axis=0),
            np.concatenate([pos_actions, selected_actions], axis=0),
            np.ones((pos_actions.shape[0] + selected_actions.shape[0],), dtype=np.float32),
        )
        q_traj, _bias = calibrate_posteriors(traj_scores, selected_frac, args.posterior_temperature)
        weighted_obs = []
        weighted_actions = []
        weighted_weights = []
        for q_value, (_score, traj) in zip(q_traj, scored_unlabeled, strict=True):
            weighted_obs.append(normalize_obs(traj.observations, obs_mean, obs_std))
            weighted_actions.append(traj.actions)
            weighted_weights.append(np.full((traj.length,), float(q_value), dtype=np.float32))
        method = f"tri_signal_gap_posterior_bc_max{frac_tag(max_frac)}"
        posterior_x = np.concatenate(weighted_obs, axis=0)
        posterior_actions = np.concatenate(weighted_actions, axis=0)
        posterior_weights = np.concatenate(weighted_weights, axis=0)
        train_sets[method] = (
            np.concatenate([pos_x, posterior_x], axis=0),
            np.concatenate([pos_actions, posterior_actions], axis=0),
            np.concatenate([np.ones((pos_actions.shape[0],), dtype=np.float32), posterior_weights], axis=0),
        )
    for prior, (posterior_x, posterior_actions, posterior_weights) in posterior_by_prior.items():
        method = f"tri_signal_posterior_bc_prior{frac_tag(prior)}"
        train_sets[method] = (
            np.concatenate([pos_x, posterior_x], axis=0),
            np.concatenate([pos_actions, posterior_actions], axis=0),
            np.concatenate([np.ones((pos_actions.shape[0],), dtype=np.float32), posterior_weights], axis=0),
        )

    params_by_method = {}
    histories = {"state_action_classifier": classifier_history}
    rows = []
    for method, (x, actions, weights) in train_sets.items():
        method_offset = stable_method_offset(method)
        params, history = train_bc(
            x,
            actions,
            weights,
            seed=seed + 101 + method_offset,
            steps=args.bc_steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
        )
        params_by_method[method] = params
        histories[method] = history
        metrics = evaluate_policy(
            spec,
            params,
            obs_mean,
            obs_std,
            seed=seed + 10_000 + method_offset,
            episodes=args.eval_episodes,
            eval_noise=args.eval_noise,
        )
        rows.append({"seed": seed, "bad_frac": bad_frac, "method": method, **metrics})

    rerank_metrics = evaluate_policy(
        spec,
        params_by_method["bc_pos_unlabeled"],
        obs_mean,
        obs_std,
        seed=seed + 20_000 + stable_method_offset("tri_signal_rerank"),
        episodes=args.eval_episodes,
        eval_noise=args.eval_noise,
        classifier_params=classifier,
        candidate_count=args.candidate_count,
        noise_std=args.noise_std,
        action_penalty=args.action_penalty,
    )
    rows.append({"seed": seed, "bad_frac": bad_frac, "method": "tri_signal_rerank", **rerank_metrics})

    diagnostics = {
        "seed": seed,
        "bad_frac": bad_frac,
        "transition_counts": {
            "positive": int(pos_actions.shape[0]),
            "negative": int(neg_actions.shape[0]),
            "unlabeled": int(unl_actions.shape[0]),
            "unlabeled_hidden_good": int(unl_good.sum()),
            "unlabeled_hidden_bad": int((1.0 - unl_good).sum()),
        },
        "selected_unlabeled_demos_by_frac": selected_stats_by_frac,
        "selected_unlabeled_demos_by_gap": selected_stats_by_gap,
        "posterior_diagnostics_by_prior": posterior_stats_by_prior,
        "classifier": {
            "pos_prob_mean": float(pos_prob.mean()),
            "neg_prob_mean": float(neg_prob.mean()),
            "unlabeled_prob_mean": float(unl_prob.mean()),
            "unlabeled_hidden_good_prob_mean": float(unl_prob[unl_good > 0.5].mean()) if np.any(unl_good > 0.5) else float("nan"),
            "unlabeled_hidden_bad_prob_mean": float(unl_prob[unl_good <= 0.5].mean()) if np.any(unl_good <= 0.5) else float("nan"),
            "labeled_accuracy": float(0.5 * ((pos_prob > 0.5).mean() + (neg_prob < 0.5).mean())),
        },
        "histories": histories,
    }
    return rows, diagnostics


def summarize(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[float, str], list[dict]] = {}
    for row in rows:
        grouped.setdefault((float(row["bad_frac"]), str(row["method"])), []).append(row)
    summary = []
    for (bad_frac, method), items in sorted(grouped.items()):
        out = {"bad_frac": bad_frac, "method": method, "n_runs": len(items)}
        for key in ["success_rate", "trap_rate", "avg_return", "avg_len"]:
            vals = np.asarray([float(item[key]) for item in items], dtype=np.float64)
            out[f"{key}_mean"] = float(vals.mean())
            out[f"{key}_std"] = float(vals.std(ddof=0))
        summary.append(out)
    return summary


def markdown_table(summary: list[dict]) -> str:
    lines = [
        "| bad_frac | method | runs | success | trap | return | length |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            f"| {row['bad_frac']:.2f} | {row['method']} | {row['n_runs']} | "
            f"{row['success_rate_mean']:.3f} +/- {row['success_rate_std']:.3f} | "
            f"{row['trap_rate_mean']:.3f} +/- {row['trap_rate_std']:.3f} | "
            f"{row['avg_return_mean']:.3f} +/- {row['avg_return_std']:.3f} | "
            f"{row['avg_len_mean']:.1f} +/- {row['avg_len_std']:.1f} |"
        )
    return "\n".join(lines)


def summarize_selection(diagnostics: list[dict]) -> list[dict]:
    if not diagnostics:
        return []
    grouped: dict[tuple[float, float], list[dict]] = {}
    for item in diagnostics:
        bad_frac = float(item["bad_frac"])
        for key, selected in item["selected_unlabeled_demos_by_frac"].items():
            grouped.setdefault((bad_frac, float(key)), []).append(selected)
    rows = []
    for (bad_frac, top_frac), items in sorted(grouped.items()):
        demo_purity = []
        transition_purity = []
        hidden_good = []
        hidden_bad = []
        for selected in items:
            demo_purity.append(selected["hidden_good"] / max(1, selected["count"]))
            transition_purity.append(
                selected["selected_hidden_good_transitions"] / max(1, selected["selected_transitions"])
            )
            hidden_good.append(selected["hidden_good"])
            hidden_bad.append(selected["hidden_bad"])
        rows.append(
            {
                "bad_frac": bad_frac,
                "top_unlabeled_frac": top_frac,
                "demo_purity_mean": float(np.mean(demo_purity)),
                "demo_purity_std": float(np.std(demo_purity, ddof=0)),
                "transition_purity_mean": float(np.mean(transition_purity)),
                "transition_purity_std": float(np.std(transition_purity, ddof=0)),
                "hidden_good_demo_mean": float(np.mean(hidden_good)),
                "hidden_bad_demo_mean": float(np.mean(hidden_bad)),
            }
        )
    return rows


def summarize_posteriors(diagnostics: list[dict]) -> list[dict]:
    if not diagnostics or not diagnostics[0].get("posterior_diagnostics_by_prior"):
        return []
    grouped: dict[tuple[float, float], list[dict]] = {}
    for item in diagnostics:
        bad_frac = float(item["bad_frac"])
        for key, posterior in item["posterior_diagnostics_by_prior"].items():
            grouped.setdefault((bad_frac, float(key)), []).append(posterior)
    rows = []
    for (bad_frac, prior), items in sorted(grouped.items()):
        demo_purity = []
        transition_purity = []
        posterior_mean = []
        for posterior in items:
            demo_purity.append(posterior["demo_weight_purity"])
            transition_purity.append(posterior["transition_weight_purity"])
            posterior_mean.append(posterior["posterior_mean"])
        rows.append(
            {
                "bad_frac": bad_frac,
                "prior": prior,
                "posterior_mean": float(np.mean(posterior_mean)),
                "demo_weight_purity_mean": float(np.mean(demo_purity)),
                "demo_weight_purity_std": float(np.std(demo_purity, ddof=0)),
                "transition_weight_purity_mean": float(np.mean(transition_purity)),
                "transition_weight_purity_std": float(np.std(transition_purity, ddof=0)),
            }
        )
    return rows


def summarize_gap_selection(diagnostics: list[dict]) -> list[dict]:
    grouped: dict[tuple[float, float], list[dict]] = {}
    for item in diagnostics:
        bad_frac = float(item["bad_frac"])
        for key, selected in item.get("selected_unlabeled_demos_by_gap", {}).items():
            grouped.setdefault((bad_frac, float(key)), []).append(selected)
    rows = []
    for (bad_frac, max_frac), items in sorted(grouped.items()):
        demo_purity = []
        transition_purity = []
        hidden_good = []
        hidden_bad = []
        selected_frac = []
        score_gap = []
        for selected in items:
            demo_purity.append(selected["hidden_good"] / max(1, selected["count"]))
            transition_purity.append(
                selected["selected_hidden_good_transitions"] / max(1, selected["selected_transitions"])
            )
            hidden_good.append(selected["hidden_good"])
            hidden_bad.append(selected["hidden_bad"])
            selected_frac.append(selected["selected_frac"])
            score_gap.append(selected["score_gap"])
        rows.append(
            {
                "bad_frac": bad_frac,
                "max_frac": max_frac,
                "selected_frac_mean": float(np.mean(selected_frac)),
                "selected_frac_std": float(np.std(selected_frac, ddof=0)),
                "score_gap_mean": float(np.mean(score_gap)),
                "score_gap_std": float(np.std(score_gap, ddof=0)),
                "demo_purity_mean": float(np.mean(demo_purity)),
                "demo_purity_std": float(np.std(demo_purity, ddof=0)),
                "transition_purity_mean": float(np.mean(transition_purity)),
                "transition_purity_std": float(np.std(transition_purity, ddof=0)),
                "hidden_good_demo_mean": float(np.mean(hidden_good)),
                "hidden_bad_demo_mean": float(np.mean(hidden_bad)),
            }
        )
    return rows


def selection_markdown_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    lines = [
        "| bad_frac | top frac | demo purity | transition purity | good demos | bad demos |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['bad_frac']:.2f} | {row['top_unlabeled_frac']:.2f} | "
            f"{row['demo_purity_mean']:.3f} +/- {row['demo_purity_std']:.3f} | "
            f"{row['transition_purity_mean']:.3f} +/- {row['transition_purity_std']:.3f} | "
            f"{row['hidden_good_demo_mean']:.1f} | {row['hidden_bad_demo_mean']:.1f} |"
        )
    return "\n".join(lines)


def gap_selection_markdown_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    lines = [
        "| bad_frac | max frac | selected frac | score gap | demo purity | transition purity | good demos | bad demos |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['bad_frac']:.2f} | {row['max_frac']:.2f} | "
            f"{row['selected_frac_mean']:.3f} +/- {row['selected_frac_std']:.3f} | "
            f"{row['score_gap_mean']:.3f} +/- {row['score_gap_std']:.3f} | "
            f"{row['demo_purity_mean']:.3f} +/- {row['demo_purity_std']:.3f} | "
            f"{row['transition_purity_mean']:.3f} +/- {row['transition_purity_std']:.3f} | "
            f"{row['hidden_good_demo_mean']:.1f} | {row['hidden_bad_demo_mean']:.1f} |"
        )
    return "\n".join(lines)


def posterior_markdown_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    lines = [
        "| bad_frac | prior | posterior mean | demo weight purity | transition weight purity |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['bad_frac']:.2f} | {row['prior']:.2f} | {row['posterior_mean']:.3f} | "
            f"{row['demo_weight_purity_mean']:.3f} +/- {row['demo_weight_purity_std']:.3f} | "
            f"{row['transition_weight_purity_mean']:.3f} +/- {row['transition_weight_purity_std']:.3f} |"
        )
    return "\n".join(lines)


def write_artifacts(args: argparse.Namespace, rows: list[dict], diagnostics: list[dict], *, status: str) -> Path:
    with (args.out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["seed", "bad_frac", "method", "success_rate", "trap_rate", "avg_return", "avg_len"],
        )
        writer.writeheader()
        writer.writerows(rows)
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    summary = summarize(rows)
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    selection_summary = summarize_selection(diagnostics)
    (args.out_dir / "selection_summary.json").write_text(json.dumps(selection_summary, indent=2), encoding="utf-8")
    gap_selection_summary = summarize_gap_selection(diagnostics)
    (args.out_dir / "gap_selection_summary.json").write_text(
        json.dumps(gap_selection_summary, indent=2), encoding="utf-8"
    )
    posterior_summary = summarize_posteriors(diagnostics)
    (args.out_dir / "posterior_summary.json").write_text(json.dumps(posterior_summary, indent=2), encoding="utf-8")
    report = [
        "# Continuous PointNav Tri-Signal Smoke",
        "",
        f"Status: `{status}`.",
        f"Completed seed/fraction runs: `{len(diagnostics)}`.",
        f"Seeds: `{args.seeds}`.",
        f"Bad fractions: `{args.bad_fracs}`.",
        f"Positive prefix steps: `{args.positive_prefix_steps}`.",
        f"BC steps: `{args.bc_steps}`; classifier steps: `{args.classifier_steps}`.",
        f"Evaluation episodes per row: `{args.eval_episodes}`.",
        f"Top unlabeled demo fractions: `{args.top_unlabeled_fracs if args.top_unlabeled_fracs is not None else [args.top_unlabeled_frac]}`.",
        f"Gap selection max fractions: `{getattr(args, 'gap_select_max_fracs', [])}`; min fraction: `{getattr(args, 'gap_select_min_frac', 0.02)}`.",
        f"Posterior priors: `{args.posterior_priors}`; posterior temperature: `{args.posterior_temperature}`.",
        "",
        "## Metrics",
        "",
        markdown_table(summary),
        "",
        "## Selection Diagnostics",
        "",
        selection_markdown_table(selection_summary),
        "",
        "## Gap Selection Diagnostics",
        "",
        gap_selection_markdown_table(gap_selection_summary),
        "",
        "## Posterior Diagnostics",
        "",
        posterior_markdown_table(posterior_summary),
        "",
        "## Interpretation",
        "",
        "- This is a controlled continuous-action bridge task between GridWorld and Robomimic.",
        "- Positive labels are route prefixes, so positive-only BC lacks full-route support.",
        "- Unlabeled data contains hidden safe full routes and hidden bad shortcut trajectories through the trap.",
        "- `tri_signal_rerank` uses a mixed-data BC proposal but reranks candidate actions with the explicit good/bad state-action classifier.",
        "- `tri_signal_top_demo_bc` selects high-scoring unlabeled trajectories by mean state-action classifier probability, then clones their transitions.",
        "- `tri_signal_posterior_bc` calibrates soft trajectory weights to an assumed unlabeled-good prior and trains weighted BC.",
        "- `tri_signal_gap_demo_bc` and `tri_signal_gap_posterior_bc` choose an unlabeled support size by the largest classifier-score gap within an allowed prefix.",
        "- A useful result should beat mixed-data BC and classifier-weighted BC while approaching the hidden-good oracle.",
    ]
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    diagnostics: list[dict] = []
    for bad_frac in args.bad_fracs:
        for seed in args.seeds:
            local_rows, local_diagnostics = run_one(args, seed, bad_frac)
            rows.extend(local_rows)
            diagnostics.append(local_diagnostics)
            top_rows = [row for row in local_rows if str(row["method"]).startswith("tri_signal_top_demo_bc")]
            top_best = max(top_rows, key=lambda row: float(row["success_rate"]))
            rerank = next(row for row in local_rows if row["method"] == "tri_signal_rerank")
            wbc = next(row for row in local_rows if row["method"] == "weighted_bc_state_action")
            print(
                f"seed={seed} bad_frac={bad_frac:.2f}: "
                f"best_top_demo={top_best['method']}:{top_best['success_rate']:.3f}, "
                f"rerank_success={rerank['success_rate']:.3f}, "
                f"weighted_success={wbc['success_rate']:.3f}"
                ,
                flush=True,
            )
            write_artifacts(args, rows, diagnostics, status="partial")

    report_path = write_artifacts(args, rows, diagnostics, status="complete")
    print(f"wrote {report_path}", flush=True)


if __name__ == "__main__":
    main()
