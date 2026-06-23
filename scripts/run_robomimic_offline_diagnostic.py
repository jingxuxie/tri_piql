from __future__ import annotations

import argparse
import csv
import json
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

from run_minari_action_rerank_smoke import state_action_features, train_state_action_classifier
from run_minari_bc_baselines import TransitionData, init_mlp, mlp_apply, predict, train_bc


@dataclass(frozen=True)
class DemoBatch:
    observations: np.ndarray
    actions: np.ndarray
    demo_ids: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-path", type=Path, default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_can_paired_offline"))
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


def obs_vector(group) -> np.ndarray:
    obs_group = group["obs"]
    parts = [np.asarray(obs_group[key], dtype=np.float32).reshape((obs_group[key].shape[0], -1)) for key in sorted(obs_group.keys())]
    return np.concatenate(parts, axis=1)


def load_batch(hdf5_path: str, demo_ids: list[str]) -> DemoBatch:
    obs_chunks = []
    action_chunks = []
    demo_chunks = []
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted(demo_ids, key=demo_sort_key):
            group = f["data"][demo_id]
            obs = obs_vector(group)
            actions = np.asarray(group["actions"], dtype=np.float32)
            obs_chunks.append(obs)
            action_chunks.append(actions)
            demo_chunks.append(np.full((actions.shape[0],), demo_sort_key(demo_id), dtype=np.int32))
    return DemoBatch(
        observations=np.concatenate(obs_chunks, axis=0),
        actions=np.concatenate(action_chunks, axis=0),
        demo_ids=np.concatenate(demo_chunks, axis=0),
    )


def normalize(train_obs: np.ndarray, *arrays: np.ndarray):
    mean = train_obs.mean(axis=0, keepdims=True)
    std = train_obs.std(axis=0, keepdims=True) + 1.0e-6
    return mean, std, [(array - mean) / std for array in arrays]


def mse(params, observations: np.ndarray, actions: np.ndarray) -> float:
    pred = predict(params, observations)
    return float(np.mean((pred - actions) ** 2))


def classifier_logits(params, observations: np.ndarray, actions: np.ndarray) -> np.ndarray:
    return predict(params, state_action_features(observations, actions)).reshape(-1)


def pairwise_auc(pos_scores: np.ndarray, neg_scores: np.ndarray) -> float:
    return float(
        (pos_scores[:, None] > neg_scores[None, :]).mean()
        + 0.5 * (pos_scores[:, None] == neg_scores[None, :]).mean()
    )


def main() -> None:
    args = parse_args()
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    labeled_pos = load_batch(hdf5_path, split["labeled_positive_ids"])
    labeled_neg = load_batch(hdf5_path, split["labeled_negative_ids"])
    unlabeled = load_batch(hdf5_path, split["unlabeled_ids"])
    valid_pos = load_batch(hdf5_path, split["valid_positive_ids"])
    valid_neg = load_batch(hdf5_path, split["valid_negative_ids"])

    train_obs = np.concatenate([labeled_pos.observations, labeled_neg.observations, unlabeled.observations], axis=0)
    _, _, normalized = normalize(
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
    unl_logits = classifier_logits(classifier, unlabeled.observations, unlabeled.actions)
    unl_prob = 1.0 / (1.0 + np.exp(-unl_logits))

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

    rows = []
    histories = {"state_action_classifier": classifier_history}
    for i, (method, (obs, actions, weights)) in enumerate(train_sets.items()):
        params, history = train_bc(
            obs,
            actions,
            weights,
            seed=args.seed + 100 + i,
            steps=args.steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
        )
        histories[method] = history
        pos_mse = mse(params, valid_pos.observations, valid_pos.actions)
        neg_mse = mse(params, valid_neg.observations, valid_neg.actions)
        rows.append(
            {
                "method": method,
                "valid_positive_mse": pos_mse,
                "valid_negative_mse": neg_mse,
                "negative_minus_positive_mse": neg_mse - pos_mse,
            }
        )
        print(f"{method}: pos_mse={pos_mse:.5f} neg_mse={neg_mse:.5f} gap={neg_mse - pos_mse:.5f}")

    classifier_metrics = {
        "train_labeled_accuracy": float(
            0.5 * ((train_pos_logits > 0).mean() + (train_neg_logits < 0).mean())
        ),
        "valid_labeled_accuracy": float(
            0.5 * ((valid_pos_logits > 0).mean() + (valid_neg_logits < 0).mean())
        ),
        "valid_auc": pairwise_auc(valid_pos_logits, valid_neg_logits),
        "train_pos_logit_mean": float(train_pos_logits.mean()),
        "train_neg_logit_mean": float(train_neg_logits.mean()),
        "valid_pos_logit_mean": float(valid_pos_logits.mean()),
        "valid_neg_logit_mean": float(valid_neg_logits.mean()),
        "unlabeled_prob_mean": float(unl_prob.mean()),
    }

    metrics_path = args.out_dir / "metrics.csv"
    with metrics_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["method", "valid_positive_mse", "valid_negative_mse", "negative_minus_positive_mse"],
        )
        writer.writeheader()
        writer.writerows(rows)

    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "seed": args.seed,
        "steps": args.steps,
        "classifier_steps": args.classifier_steps,
        "transition_counts": {
            "labeled_positive": int(labeled_pos.actions.shape[0]),
            "labeled_negative": int(labeled_neg.actions.shape[0]),
            "unlabeled": int(unlabeled.actions.shape[0]),
            "valid_positive": int(valid_pos.actions.shape[0]),
            "valid_negative": int(valid_neg.actions.shape[0]),
        },
        "classifier": classifier_metrics,
        "histories": histories,
    }
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report = [
        "# Robomimic Can Paired Offline Diagnostic",
        "",
        f"Split path: `{args.split_path}`.",
        f"HDF5 path: `{hdf5_path}`.",
        f"Labeled demos: `{len(split['labeled_positive_ids'])}` positive, `{len(split['labeled_negative_ids'])}` negative.",
        f"Unlabeled demos: `{len(split['unlabeled_ids'])}`.",
        f"Validation demos: `{len(split['valid_positive_ids'])}` positive, `{len(split['valid_negative_ids'])}` negative.",
        "",
        "## Policy Offline Metrics",
        "",
        "| method | valid positive MSE | valid negative MSE | neg-pos MSE gap |",
        "|---|---:|---:|---:|",
    ]
    for row in rows:
        report.append(
            f"| {row['method']} | {row['valid_positive_mse']:.5f} | {row['valid_negative_mse']:.5f} | {row['negative_minus_positive_mse']:.5f} |"
        )
    report.extend(
        [
            "",
            "## State-Action Classifier",
            "",
            f"- Train labeled accuracy: `{classifier_metrics['train_labeled_accuracy']:.3f}`.",
            f"- Valid labeled accuracy: `{classifier_metrics['valid_labeled_accuracy']:.3f}`.",
            f"- Valid positive-vs-negative AUC: `{classifier_metrics['valid_auc']:.3f}`.",
            f"- Valid positive/negative logit mean: `{classifier_metrics['valid_pos_logit_mean']:.3f}` / `{classifier_metrics['valid_neg_logit_mean']:.3f}`.",
            f"- Unlabeled positive probability mean: `{classifier_metrics['unlabeled_prob_mean']:.3f}`.",
            "",
            "## Interpretation",
            "",
            "- This is an offline-only viability check before installing/evaluating full robosuite rollouts.",
            "- A useful signal is high held-out positive-vs-negative classifier AUC and lower action MSE on held-out positive demonstrations than held-out negative demonstrations.",
        ]
    )
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
