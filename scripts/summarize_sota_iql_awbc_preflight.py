#!/usr/bin/env python3
"""Build a bounded classifier-reward IQL/AWBC preflight for Robomimic Can404."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

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
from run_minari_bc_baselines import init_mlp, mlp_apply, predict  # noqa: E402
from tri_piql.algos.tabular import _adam_update, _tree_zeros_like  # noqa: E402


DEFAULT_SPLIT_PATH = (
    ROOT / "results" / "final_paper_v02" / "splits" / "can_paired_pos40_bad80_split404" / "split_indices.json"
)
DEFAULT_WEIGHTED_DIAGNOSTICS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
    / "setup"
    / "diagnostics.json"
)
DEFAULT_SCORE_RANKINGS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "score_diagnostics"
    / "can_paired_pos40_bad80_split404_policy0"
    / "demo_rankings.csv"
)
DEFAULT_SM_RWBC_RECIPE = (
    ROOT / "results" / "sota_candidate" / "sm_rwbc_can404_m003_lam2_combined_preflight" / "sm_rwbc_recipe.json"
)
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate" / "iql_awbc_can404_preflight"

STANDARD_LOW_DIM_OBS = [
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "object",
]


@dataclass(frozen=True)
class DemoArrays:
    observations: np.ndarray
    actions: np.ndarray
    next_observations: np.ndarray


@dataclass(frozen=True)
class TransitionBatch:
    observations: np.ndarray
    actions: np.ndarray
    next_observations: np.ndarray
    demo_ids: np.ndarray
    timesteps: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--weighted-diagnostics", type=Path, default=DEFAULT_WEIGHTED_DIAGNOSTICS)
    parser.add_argument("--score-rankings", type=Path, default=DEFAULT_SCORE_RANKINGS)
    parser.add_argument("--sm-rwbc-recipe", type=Path, default=DEFAULT_SM_RWBC_RECIPE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--obs-keys", choices=["standard", "all"], default="standard")
    parser.add_argument("--steps", type=int, default=800)
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--expectile", type=float, default=0.70)
    parser.add_argument("--adv-margin", type=float, default=0.15)
    parser.add_argument("--actor-temperature", type=float, default=1.0)
    parser.add_argument("--topq", type=float, default=0.70)
    parser.add_argument("--selected-recipe", choices=["raw", "norm", "norm_topq"], default="norm_topq")
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def sorted_demos(demo_ids: list[str] | set[str]) -> list[str]:
    return sorted(demo_ids, key=demo_sort_key)


def dataset_obs_keys(hdf5_path: str) -> list[str]:
    with h5py.File(hdf5_path, "r") as f:
        first_demo = sorted(f["data"].keys(), key=demo_sort_key)[0]
        return sorted(f["data"][first_demo]["obs"].keys())


def obs_vector(obs_group, obs_keys: list[str]) -> np.ndarray:
    parts = [
        np.asarray(obs_group[key], dtype=np.float32).reshape((obs_group[key].shape[0], -1))
        for key in obs_keys
    ]
    return np.concatenate(parts, axis=1).astype(np.float32, copy=False)


def load_demo_arrays(hdf5_path: str, demo_ids: list[str], obs_keys: list[str]) -> dict[str, DemoArrays]:
    arrays: dict[str, DemoArrays] = {}
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted_demos(demo_ids):
            group = f["data"][demo_id]
            observations = obs_vector(group["obs"], obs_keys)
            next_observations = obs_vector(group["next_obs"], obs_keys)
            actions = np.asarray(group["actions"], dtype=np.float32)
            if observations.shape[0] != actions.shape[0] or next_observations.shape[0] != actions.shape[0]:
                raise ValueError(f"{demo_id}: observation/action length mismatch")
            arrays[demo_id] = DemoArrays(
                observations=observations,
                actions=actions,
                next_observations=next_observations,
            )
    return arrays


def stack_transitions(arrays: dict[str, DemoArrays], demo_ids: list[str]) -> TransitionBatch:
    obs_chunks: list[np.ndarray] = []
    next_chunks: list[np.ndarray] = []
    action_chunks: list[np.ndarray] = []
    demo_chunks: list[np.ndarray] = []
    timestep_chunks: list[np.ndarray] = []
    for demo_id in sorted_demos(demo_ids):
        demo = arrays[demo_id]
        length = demo.actions.shape[0]
        obs_chunks.append(demo.observations)
        next_chunks.append(demo.next_observations)
        action_chunks.append(demo.actions)
        demo_chunks.append(np.full((length,), demo_id, dtype=object))
        timestep_chunks.append(np.arange(length, dtype=np.int32))
    return TransitionBatch(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        next_observations=np.concatenate(next_chunks, axis=0),
        demo_ids=np.concatenate(demo_chunks, axis=0),
        timesteps=np.concatenate(timestep_chunks, axis=0),
    )


def standardize_fit(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = matrix.mean(axis=0, keepdims=True)
    std = matrix.std(axis=0, keepdims=True) + 1.0e-6
    return mean.astype(np.float32), std.astype(np.float32)


def standardize_apply(matrix: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((matrix - mean) / std).astype(np.float32, copy=False)


def normalize_arrays(arrays: dict[str, DemoArrays], obs_mean: np.ndarray, obs_std: np.ndarray) -> dict[str, DemoArrays]:
    return {
        demo_id: DemoArrays(
            observations=standardize_apply(demo.observations, obs_mean, obs_std),
            actions=demo.actions,
            next_observations=standardize_apply(demo.next_observations, obs_mean, obs_std),
        )
        for demo_id, demo in arrays.items()
    }


def score_by_demo(path: Path) -> dict[str, float]:
    return {row["demo_id"]: float(row["score"]) for row in read_csv(path)}


def q_apply(params, observations: jnp.ndarray, actions: jnp.ndarray) -> jnp.ndarray:
    x = jnp.concatenate([observations, actions], axis=-1)
    return mlp_apply(params["q"], x).reshape(x.shape[:-1])


def v_apply(params, observations: jnp.ndarray) -> jnp.ndarray:
    return mlp_apply(params["v"], observations).reshape(observations.shape[:-1])


def expectile_loss(diff: jnp.ndarray, expectile: float) -> jnp.ndarray:
    weight = jnp.where(diff > 0.0, expectile, 1.0 - expectile)
    return weight * diff**2


def param_l2(params) -> jnp.ndarray:
    leaves = []
    for key in ("q", "v"):
        leaves.extend(jax.tree_util.tree_leaves(params[key]))
    return sum(jnp.mean(leaf**2) for leaf in leaves) / max(1, len(leaves))


def train_iql_qv(
    *,
    pos: TransitionBatch,
    neg: TransitionBatch,
    unl: TransitionBatch,
    pos_rewards: np.ndarray,
    neg_rewards: np.ndarray,
    unl_rewards: np.ndarray,
    action_low: np.ndarray,
    action_high: np.ndarray,
    seed: int,
    steps: int,
    batch_size: int,
    hidden_dim: int,
    depth: int,
    lr: float,
    gamma: float,
    expectile: float,
    adv_margin: float,
) -> tuple[dict[str, object], list[dict[str, float]]]:
    obs_dim = pos.observations.shape[1]
    action_dim = pos.actions.shape[1]
    key = jax.random.PRNGKey(seed)
    key, q_key, v_key = jax.random.split(key, 3)
    params = {
        "q": init_mlp(q_key, obs_dim + action_dim, 1, hidden_dim, depth),
        "v": init_mlp(v_key, obs_dim, 1, hidden_dim, depth),
    }
    opt_state = (_tree_zeros_like(params), _tree_zeros_like(params))

    pos_x = jnp.asarray(pos.observations, dtype=jnp.float32)
    pos_a = jnp.asarray(pos.actions, dtype=jnp.float32)
    pos_n = jnp.asarray(pos.next_observations, dtype=jnp.float32)
    pos_r = jnp.asarray(pos_rewards, dtype=jnp.float32)
    neg_x = jnp.asarray(neg.observations, dtype=jnp.float32)
    neg_a = jnp.asarray(neg.actions, dtype=jnp.float32)
    neg_n = jnp.asarray(neg.next_observations, dtype=jnp.float32)
    neg_r = jnp.asarray(neg_rewards, dtype=jnp.float32)
    unl_x = jnp.asarray(unl.observations, dtype=jnp.float32)
    unl_a = jnp.asarray(unl.actions, dtype=jnp.float32)
    unl_n = jnp.asarray(unl.next_observations, dtype=jnp.float32)
    unl_r = jnp.asarray(unl_rewards, dtype=jnp.float32)
    low = jnp.asarray(action_low, dtype=jnp.float32)
    high = jnp.asarray(action_high, dtype=jnp.float32)
    half_batch = max(1, batch_size // 2)

    def transition_losses(local_params, obs_b, act_b, next_b, reward_b):
        q = q_apply(local_params, obs_b, act_b)
        v = v_apply(local_params, obs_b)
        next_v = v_apply(local_params, next_b)
        td = (q - reward_b - gamma * next_v) ** 2
        value = expectile_loss(jax.lax.stop_gradient(q) - v, expectile)
        adv = q - v
        return q, v, adv, td, value

    def loss_fn(local_params, pos_idx, neg_idx, unl_idx, rand_actions):
        pos_q, pos_v, pos_adv, pos_td, pos_value = transition_losses(
            local_params, pos_x[pos_idx], pos_a[pos_idx], pos_n[pos_idx], pos_r[pos_idx]
        )
        neg_q, neg_v, neg_adv, neg_td, neg_value = transition_losses(
            local_params, neg_x[neg_idx], neg_a[neg_idx], neg_n[neg_idx], neg_r[neg_idx]
        )
        unl_q, unl_v, unl_adv, unl_td, unl_value = transition_losses(
            local_params, unl_x[unl_idx], unl_a[unl_idx], unl_n[unl_idx], unl_r[unl_idx]
        )

        td_loss = jnp.mean(jnp.concatenate([pos_td, neg_td, unl_td]))
        value_loss = jnp.mean(jnp.concatenate([pos_value, neg_value, unl_value]))
        sign_loss = jnp.mean(jax.nn.softplus(adv_margin - pos_adv)) + jnp.mean(
            jax.nn.softplus(adv_margin + neg_adv)
        )

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
        )
        loss = (
            0.8 * td_loss
            + 0.5 * value_loss
            + 0.8 * sign_loss
            + 0.10 * conservative
            + 0.002 * scale_reg
            + 0.001 * param_l2(local_params)
        )
        metrics = {
            "loss": loss,
            "td_loss": td_loss,
            "value_loss": value_loss,
            "sign_loss": sign_loss,
            "conservative": conservative,
            "pos_adv": jnp.mean(pos_adv),
            "neg_adv": jnp.mean(neg_adv),
            "unl_adv": jnp.mean(unl_adv),
            "pos_q": jnp.mean(pos_q),
            "neg_q": jnp.mean(neg_q),
            "unl_q": jnp.mean(unl_q),
        }
        return loss, metrics

    grad_fn = jax.value_and_grad(loss_fn, has_aux=True)

    @jax.jit
    def train_step(local_params, local_opt_state, local_key, local_step):
        keys = jax.random.split(local_key, 6)
        next_key = keys[0]
        pos_idx = jax.random.randint(keys[1], (batch_size,), minval=0, maxval=pos_x.shape[0])
        neg_idx = jax.random.randint(keys[2], (batch_size,), minval=0, maxval=neg_x.shape[0])
        unl_idx = jax.random.randint(keys[3], (batch_size,), minval=0, maxval=unl_x.shape[0])
        rand_actions = jax.random.uniform(keys[4], (2 * half_batch, action_dim), minval=low, maxval=high)
        (_, metrics), grads = grad_fn(local_params, pos_idx, neg_idx, unl_idx, rand_actions)
        local_params, local_opt_state = _adam_update(local_params, grads, local_opt_state, lr, local_step)
        return local_params, local_opt_state, next_key, metrics

    history: list[dict[str, float]] = []
    for step_id in range(1, steps + 1):
        params, opt_state, key, metrics = train_step(params, opt_state, key, jnp.asarray(step_id, dtype=jnp.float32))
        if step_id == 1 or step_id % max(1, steps // 5) == 0 or step_id == steps:
            history.append({"step": step_id, **{k: float(v) for k, v in metrics.items()}})
    return params, history


def predict_q_v(params, batch: TransitionBatch, batch_size: int = 65_536) -> tuple[np.ndarray, np.ndarray]:
    q_values = []
    v_values = []
    for start in range(0, batch.actions.shape[0], batch_size):
        obs_b = jnp.asarray(batch.observations[start : start + batch_size], dtype=jnp.float32)
        act_b = jnp.asarray(batch.actions[start : start + batch_size], dtype=jnp.float32)
        q_values.append(np.asarray(q_apply(params, obs_b, act_b)).reshape(-1))
        v_values.append(np.asarray(v_apply(params, obs_b)).reshape(-1))
    return np.concatenate(q_values, axis=0), np.concatenate(v_values, axis=0)


def effective_sample_size(weights: np.ndarray) -> float:
    denom = float(np.sum(weights * weights))
    if denom <= 0.0:
        return 0.0
    total = float(np.sum(weights))
    return (total * total) / denom


def build_weight_outputs(
    *,
    arrays: dict[str, DemoArrays],
    train_ids: list[str],
    unlabeled_ids: list[str],
    labeled_positive_set: set[str],
    all_positive_set: set[str],
    scores: dict[str, float],
    unl_adv_by_key: dict[tuple[str, int], float],
    selected_recipe: str,
    actor_temperature: float,
    topq: float,
) -> tuple[dict[str, dict[str, np.ndarray]], list[dict[str, object]], list[dict[str, object]], dict[str, float]]:
    unl_adv_values = np.asarray([unl_adv_by_key[key] for key in sorted(unl_adv_by_key)], dtype=np.float32)
    adv_mean = float(np.mean(unl_adv_values))
    adv_std = float(np.std(unl_adv_values) + 1.0e-6)
    score_threshold = float(np.quantile([scores[demo_id] for demo_id in unlabeled_ids], topq))

    recipe_rows: list[dict[str, object]] = []
    recipe_weights_by_demo: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    recipe_summaries: dict[str, dict[str, float]] = {}
    for recipe in ["raw", "norm", "norm_topq"]:
        weights_by_demo: dict[str, dict[str, np.ndarray]] = {}
        rows: list[dict[str, object]] = []
        all_weights: list[np.ndarray] = []
        hidden_positive_weights: list[np.ndarray] = []
        hidden_bad_weights: list[np.ndarray] = []
        hidden_positive_mass = 0.0
        hidden_bad_mass = 0.0
        hidden_positive_transitions = 0
        hidden_bad_transitions = 0
        hidden_positive_demos = 0
        hidden_bad_demos = 0
        labeled_positive_mass = 0.0

        for demo_id in sorted_demos(train_ids):
            demo = arrays[demo_id]
            length = demo.actions.shape[0]
            score = float(scores.get(demo_id, 1.0 if demo_id in labeled_positive_set else 0.0))
            role = "labeled_positive"
            if demo_id in labeled_positive_set:
                weight = np.ones((length,), dtype=np.float32)
                advantage = np.zeros((length,), dtype=np.float32)
                labeled_positive_mass += float(np.sum(weight))
            else:
                role = "unlabeled_iql_awbc"
                advantage = np.asarray(
                    [unl_adv_by_key[(demo_id, timestep)] for timestep in range(length)],
                    dtype=np.float32,
                )
                if recipe == "raw":
                    weight_adv = advantage
                else:
                    weight_adv = (advantage - adv_mean) / adv_std
                weight = (score * np.exp(np.clip(weight_adv / actor_temperature, -2.0, 2.0))).astype(np.float32)
                max_weight = float(np.quantile(weight, 0.95) + 1.0e-6)
                weight = np.clip(weight / max_weight, 0.0, 1.0).astype(np.float32, copy=False)
                if recipe == "norm_topq" and score < score_threshold:
                    weight = np.zeros_like(weight)
                if demo_id in all_positive_set:
                    hidden_positive_demos += 1
                    hidden_positive_transitions += length
                    hidden_positive_mass += float(np.sum(weight))
                    hidden_positive_weights.append(weight)
                else:
                    hidden_bad_demos += 1
                    hidden_bad_transitions += length
                    hidden_bad_mass += float(np.sum(weight))
                    hidden_bad_weights.append(weight)

            all_weights.append(weight)
            weights_by_demo[demo_id] = {
                "loss_weight": weight,
                "iql_advantage": advantage.astype(np.float32),
                "classifier_score": np.full((length,), score, dtype=np.float32),
            }
            rows.append(
                {
                    "recipe": recipe,
                    "demo_id": demo_id,
                    "role": role,
                    "hidden_label": "labeled_positive"
                    if demo_id in labeled_positive_set
                    else ("positive" if demo_id in all_positive_set else "bad"),
                    "transition_count": length,
                    "classifier_score": f"{score:.6f}",
                    "advantage_mean": f"{float(np.mean(advantage)):.6f}",
                    "advantage_p90": f"{float(np.quantile(advantage, 0.90)):.6f}",
                    "weight_mean": f"{float(np.mean(weight)):.6f}",
                    "weight_min": f"{float(np.min(weight)):.6f}",
                    "weight_max": f"{float(np.max(weight)):.6f}",
                    "weight_mass": f"{float(np.sum(weight)):.6f}",
                }
            )

        flat_weights = np.concatenate(all_weights)
        hidden_positive_flat = (
            np.concatenate(hidden_positive_weights) if hidden_positive_weights else np.asarray([], dtype=np.float32)
        )
        hidden_bad_flat = np.concatenate(hidden_bad_weights) if hidden_bad_weights else np.asarray([], dtype=np.float32)
        hidden_unlabeled_mass = hidden_positive_mass + hidden_bad_mass
        hidden_unlabeled_transitions = hidden_positive_transitions + hidden_bad_transitions
        summary = {
            "recipe": recipe,
            "train_demo_count": float(len(train_ids)),
            "labeled_positive_count": float(len(labeled_positive_set)),
            "hidden_positive_demo_count": float(hidden_positive_demos),
            "hidden_bad_demo_count": float(hidden_bad_demos),
            "hidden_positive_transition_count": float(hidden_positive_transitions),
            "hidden_bad_transition_count": float(hidden_bad_transitions),
            "labeled_positive_mass": float(labeled_positive_mass),
            "hidden_positive_mass": float(hidden_positive_mass),
            "hidden_bad_mass": float(hidden_bad_mass),
            "hidden_bad_unweighted_transition_fraction": float(
                hidden_bad_transitions / max(1, hidden_unlabeled_transitions)
            ),
            "hidden_bad_weighted_mass_fraction": float(hidden_bad_mass / max(1.0, hidden_unlabeled_mass)),
            "hidden_positive_mean_weight": float(np.mean(hidden_positive_flat)) if hidden_positive_flat.size else 0.0,
            "hidden_bad_mean_weight": float(np.mean(hidden_bad_flat)) if hidden_bad_flat.size else 0.0,
            "all_transition_weight_mean": float(np.mean(flat_weights)),
            "all_transition_weight_min": float(np.min(flat_weights)),
            "all_transition_weight_max": float(np.max(flat_weights)),
            "transition_effective_sample_size": float(effective_sample_size(flat_weights)),
            "advantage_mean": adv_mean,
            "advantage_std": adv_std,
            "topq": float(topq),
            "score_threshold": score_threshold,
        }
        recipe_weights_by_demo[recipe] = weights_by_demo
        recipe_rows.extend(rows)
        recipe_summaries[recipe] = summary
        recipe_rows.append(
            {
                "recipe": recipe,
                "hidden_positive_mass": f"{hidden_positive_mass:.6f}",
                "hidden_bad_mass": f"{hidden_bad_mass:.6f}",
                "hidden_bad_weighted_mass_fraction": f"{summary['hidden_bad_weighted_mass_fraction']:.6f}",
                "hidden_positive_mean_weight": f"{summary['hidden_positive_mean_weight']:.6f}",
                "hidden_bad_mean_weight": f"{summary['hidden_bad_mean_weight']:.6f}",
                "transition_effective_sample_size": f"{summary['transition_effective_sample_size']:.6f}",
                "score_threshold": f"{score_threshold:.6f}",
            }
        )

    selected = recipe_weights_by_demo[selected_recipe]
    selected_rows = [row for row in recipe_rows if row.get("recipe") == selected_recipe and "demo_id" in row]
    selected_summary = recipe_summaries[selected_recipe]
    summary_rows = [
        {key: (f"{value:.6f}" if isinstance(value, float) else value) for key, value in summary.items()}
        for summary in recipe_summaries.values()
    ]
    return selected, selected_rows, summary_rows, selected_summary


def write_weight_hdf5(path: Path, weights_by_demo: dict[str, dict[str, np.ndarray]], metadata: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        f.attrs["metadata_json"] = json.dumps(metadata, sort_keys=True)
        data_group = f.create_group("data")
        for demo_id in sorted_demos(set(weights_by_demo)):
            demo_group = data_group.create_group(demo_id)
            for key, value in weights_by_demo[demo_id].items():
                demo_group.create_dataset(key, data=value.astype(np.float32), compression="gzip")


def fmt(value: float) -> str:
    if math.isnan(float(value)):
        return ""
    return f"{float(value):.6f}"


def jsonable_args(args: argparse.Namespace) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in vars(args).items():
        if isinstance(value, Path):
            out[key] = str(value)
        else:
            out[key] = value
    return out


def write_report(
    path: Path,
    *,
    selected_summary: dict[str, float],
    summary_rows: list[dict[str, object]],
    q_diagnostics: dict[str, float],
    classifier_metrics: dict[str, float],
    sm_rwbc_summary: dict[str, float] | None,
    output_paths: dict[str, Path],
    args: argparse.Namespace,
) -> None:
    lines = [
        "# SOTA Candidate 6 IQL-AWBC Can404 Preflight",
        "",
        "This is a bounded Offline RL / IQL revisit preflight from `triage_bc_sota_candidate_plan.md`.",
        "It trains a small classifier-reward Q/V model on the Can404 broad pool, then converts Q-V advantages into transition weights for the existing Robomimic BC-RNN-GMM extractor.",
        "",
        "## Setup",
        "",
        f"- Split: `{args.split_path}`.",
        f"- IQL/QV steps: `{args.steps}`.",
        f"- State-action classifier steps: `{args.classifier_steps}`.",
        f"- Selected extraction recipe: `{selected_summary['recipe']}`.",
        f"- Top-q score threshold for `norm_topq`: `{selected_summary['score_threshold']:.6f}`.",
        "",
        "## Q/V Diagnostics",
        "",
        f"- State-action classifier labeled accuracy: `{classifier_metrics['labeled_accuracy']:.3f}`.",
        f"- Classifier logit means, pos/neg/unlabeled: `{classifier_metrics['pos_logit_mean']:.3f}` / `{classifier_metrics['neg_logit_mean']:.3f}` / `{classifier_metrics['unl_logit_mean']:.3f}`.",
        f"- Learned advantage means, pos/neg/unlabeled: `{q_diagnostics['pos_adv_mean']:.3f}` / `{q_diagnostics['neg_adv_mean']:.3f}` / `{q_diagnostics['unl_adv_mean']:.3f}`.",
        f"- Learned Q means, pos/neg/unlabeled: `{q_diagnostics['pos_q_mean']:.3f}` / `{q_diagnostics['neg_q_mean']:.3f}` / `{q_diagnostics['unl_q_mean']:.3f}`.",
        "",
        "## Weight Summary",
        "",
        "| recipe | hidden-positive mass | hidden-bad mass | bad mass frac | pos mean w | bad mean w | ESS |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            "| {recipe} | {hidden_positive_mass} | {hidden_bad_mass} | {hidden_bad_weighted_mass_fraction} | {hidden_positive_mean_weight} | {hidden_bad_mean_weight} | {transition_effective_sample_size} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
        ]
    )
    sm_frac = None if sm_rwbc_summary is None else float(sm_rwbc_summary["hidden_bad_weighted_mass_fraction"])
    selected_frac = float(selected_summary["hidden_bad_weighted_mass_fraction"])
    selected_pos_mass = float(selected_summary["hidden_positive_mass"])
    if sm_frac is not None and selected_frac >= sm_frac:
        decision = "preflight_no_go"
        reason = "the selected IQL-AWBC weights do not reduce hidden-bad mass versus the already rejected SM-RWBC broad-pool screen."
    elif selected_pos_mass < 0.5 * float(selected_summary["labeled_positive_mass"]):
        decision = "preflight_no_go"
        reason = "the selected recipe preserves too little hidden-positive mass to justify a broad-pool endpoint run."
    else:
        decision = "candidate_for_short_endpoint"
        reason = "the selected recipe improves the hidden-bad mass diagnostic enough to justify a bounded Can404 endpoint screen."
    lines.extend(
        [
            f"- Decision: `{decision}`.",
            f"- Read: {reason}",
        ]
    )
    if sm_rwbc_summary is not None:
        lines.append(
            f"- Rejected SM-RWBC reference bad mass fraction: `{sm_rwbc_summary['hidden_bad_weighted_mass_fraction']:.3f}`."
        )
    lines.extend(
        [
            f"- Selected IQL-AWBC bad mass fraction: `{selected_frac:.3f}`.",
            f"- Selected IQL-AWBC hidden-positive mass: `{selected_pos_mass:.1f}`.",
            "",
            "## Artifacts",
            "",
            f"- Selected weights HDF5: `{output_paths['weights_hdf5']}`.",
            f"- Selected per-demo CSV: `{output_paths['selected_csv']}`.",
            f"- Recipe summary CSV: `{output_paths['summary_csv']}`.",
            f"- Diagnostics JSON: `{output_paths['diagnostics_json']}`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    split = read_json(args.split_path)
    weighted = read_json(args.weighted_diagnostics)
    hdf5_path = split["hdf5_path"]
    obs_keys = STANDARD_LOW_DIM_OBS if args.obs_keys == "standard" else dataset_obs_keys(hdf5_path)
    scores = score_by_demo(args.score_rankings)
    train_ids = sorted_demos(weighted["train_demo_ids"])
    labeled_positive_ids = sorted_demos(split["labeled_positive_ids"])
    labeled_negative_ids = sorted_demos(split["labeled_negative_ids"])
    labeled_positive_set = set(labeled_positive_ids)
    unlabeled_train_ids = [demo_id for demo_id in train_ids if demo_id not in labeled_positive_set]
    all_positive_set = set(split["all_positive_ids"])
    needed_ids = sorted_demos(set(train_ids) | set(labeled_negative_ids))
    arrays_raw = load_demo_arrays(hdf5_path, needed_ids, obs_keys)
    fit_obs = np.concatenate(
        [arrays_raw[demo_id].observations for demo_id in needed_ids]
        + [arrays_raw[demo_id].next_observations for demo_id in needed_ids],
        axis=0,
    )
    obs_mean, obs_std = standardize_fit(fit_obs)
    arrays = normalize_arrays(arrays_raw, obs_mean, obs_std)

    pos = stack_transitions(arrays, labeled_positive_ids)
    neg = stack_transitions(arrays, labeled_negative_ids)
    unl = stack_transitions(arrays, unlabeled_train_ids)
    action_low = np.min(np.concatenate([pos.actions, neg.actions, unl.actions], axis=0), axis=0)
    action_high = np.max(np.concatenate([pos.actions, neg.actions, unl.actions], axis=0), axis=0)

    classifier, classifier_history = train_state_action_classifier(
        pos.observations,
        pos.actions,
        neg.observations,
        neg.actions,
        seed=args.seed + 11,
        steps=args.classifier_steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
    )
    pos_logits = predict(classifier, state_action_features(pos.observations, pos.actions)).reshape(-1)
    neg_logits = predict(classifier, state_action_features(neg.observations, neg.actions)).reshape(-1)
    unl_logits = predict(classifier, state_action_features(unl.observations, unl.actions)).reshape(-1)
    all_logits = np.concatenate([pos_logits, neg_logits, unl_logits], axis=0)
    reward_mean = float(np.mean(all_logits))
    reward_std = float(np.std(all_logits) + 1.0e-6)
    pos_rewards = ((pos_logits - reward_mean) / reward_std).astype(np.float32)
    neg_rewards = ((neg_logits - reward_mean) / reward_std).astype(np.float32)
    unl_rewards = ((unl_logits - reward_mean) / reward_std).astype(np.float32)
    classifier_metrics = {
        "labeled_accuracy": float(0.5 * ((pos_logits > 0.0).mean() + (neg_logits < 0.0).mean())),
        "pos_logit_mean": float(pos_logits.mean()),
        "neg_logit_mean": float(neg_logits.mean()),
        "unl_logit_mean": float(unl_logits.mean()),
        "reward_mean": reward_mean,
        "reward_std": reward_std,
    }

    qv_params, qv_history = train_iql_qv(
        pos=pos,
        neg=neg,
        unl=unl,
        pos_rewards=pos_rewards,
        neg_rewards=neg_rewards,
        unl_rewards=unl_rewards,
        action_low=action_low,
        action_high=action_high,
        seed=args.seed + 23,
        steps=args.steps,
        batch_size=args.batch_size,
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
        gamma=args.gamma,
        expectile=args.expectile,
        adv_margin=args.adv_margin,
    )
    pos_q, pos_v = predict_q_v(qv_params, pos)
    neg_q, neg_v = predict_q_v(qv_params, neg)
    unl_q, unl_v = predict_q_v(qv_params, unl)
    pos_adv = pos_q - pos_v
    neg_adv = neg_q - neg_v
    unl_adv = unl_q - unl_v
    q_diagnostics = {
        "pos_adv_mean": float(pos_adv.mean()),
        "neg_adv_mean": float(neg_adv.mean()),
        "unl_adv_mean": float(unl_adv.mean()),
        "pos_q_mean": float(pos_q.mean()),
        "neg_q_mean": float(neg_q.mean()),
        "unl_q_mean": float(unl_q.mean()),
        "pos_v_mean": float(pos_v.mean()),
        "neg_v_mean": float(neg_v.mean()),
        "unl_v_mean": float(unl_v.mean()),
    }
    unl_adv_by_key = {
        (str(demo_id), int(timestep)): float(adv)
        for demo_id, timestep, adv in zip(unl.demo_ids, unl.timesteps, unl_adv, strict=True)
    }

    selected_weights, selected_rows, summary_rows, selected_summary = build_weight_outputs(
        arrays=arrays,
        train_ids=train_ids,
        unlabeled_ids=unlabeled_train_ids,
        labeled_positive_set=labeled_positive_set,
        all_positive_set=all_positive_set,
        scores=scores,
        unl_adv_by_key=unl_adv_by_key,
        selected_recipe=args.selected_recipe,
        actor_temperature=args.actor_temperature,
        topq=args.topq,
    )

    sm_rwbc_summary = None
    if args.sm_rwbc_recipe.exists():
        sm_rwbc = read_json(args.sm_rwbc_recipe)
        sm_rwbc_summary = sm_rwbc.get("selected_summary")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    weights_hdf5 = args.out_dir / "iql_awbc_loss_weights.hdf5"
    selected_csv = args.out_dir / "iql_awbc_selected_demo_summary.csv"
    summary_csv = args.out_dir / "iql_awbc_recipe_summary.csv"
    diagnostics_json = args.out_dir / "diagnostics.json"
    report_path = args.out_dir / "iql_awbc_preflight_REPORT.md"

    metadata = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "weighted_diagnostics": str(args.weighted_diagnostics),
        "score_rankings": str(args.score_rankings),
        "obs_keys": obs_keys,
        "selected_recipe": args.selected_recipe,
        "args": jsonable_args(args),
        "classifier_metrics": classifier_metrics,
        "q_diagnostics": q_diagnostics,
        "selected_summary": selected_summary,
    }
    write_weight_hdf5(weights_hdf5, selected_weights, metadata)
    write_csv(
        selected_csv,
        selected_rows,
        [
            "recipe",
            "demo_id",
            "role",
            "hidden_label",
            "transition_count",
            "classifier_score",
            "advantage_mean",
            "advantage_p90",
            "weight_mean",
            "weight_min",
            "weight_max",
            "weight_mass",
        ],
    )
    write_csv(
        summary_csv,
        summary_rows,
        [
            "recipe",
            "train_demo_count",
            "labeled_positive_count",
            "hidden_positive_demo_count",
            "hidden_bad_demo_count",
            "hidden_positive_transition_count",
            "hidden_bad_transition_count",
            "labeled_positive_mass",
            "hidden_positive_mass",
            "hidden_bad_mass",
            "hidden_bad_unweighted_transition_fraction",
            "hidden_bad_weighted_mass_fraction",
            "hidden_positive_mean_weight",
            "hidden_bad_mean_weight",
            "all_transition_weight_mean",
            "all_transition_weight_min",
            "all_transition_weight_max",
            "transition_effective_sample_size",
            "advantage_mean",
            "advantage_std",
            "topq",
            "score_threshold",
        ],
    )
    diagnostics = {
        "metadata": metadata,
        "classifier_history": classifier_history,
        "qv_history": qv_history,
        "summary_rows": summary_rows,
        "sm_rwbc_reference_summary": sm_rwbc_summary,
    }
    diagnostics_json.write_text(json.dumps(diagnostics, indent=2, sort_keys=True), encoding="utf-8")
    write_report(
        report_path,
        selected_summary=selected_summary,
        summary_rows=summary_rows,
        q_diagnostics=q_diagnostics,
        classifier_metrics=classifier_metrics,
        sm_rwbc_summary=sm_rwbc_summary,
        output_paths={
            "weights_hdf5": weights_hdf5,
            "selected_csv": selected_csv,
            "summary_csv": summary_csv,
            "diagnostics_json": diagnostics_json,
        },
        args=args,
    )
    print(
        json.dumps(
            {
                "report": str(report_path),
                "selected_recipe": args.selected_recipe,
                "selected_bad_mass_fraction": selected_summary["hidden_bad_weighted_mass_fraction"],
                "selected_hidden_positive_mass": selected_summary["hidden_positive_mass"],
                "pos_adv_mean": q_diagnostics["pos_adv_mean"],
                "neg_adv_mean": q_diagnostics["neg_adv_mean"],
                "unl_adv_mean": q_diagnostics["unl_adv_mean"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
