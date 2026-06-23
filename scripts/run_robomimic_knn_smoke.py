from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_minari_action_rerank_smoke import state_action_features, train_state_action_classifier  # noqa: E402
from run_minari_bc_baselines import markdown_table  # noqa: E402
from run_minari_bc_baselines import predict  # noqa: E402
from run_robomimic_can_rollout_smoke import (  # noqa: E402
    DemoBatch,
    dataset_obs_keys,
    load_batch,
    load_env_metadata,
    load_eval_initials,
    normalize,
    rollout_policy,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_can_knn_smoke"))
    parser.add_argument(
        "--source",
        choices=["labeled_positive", "all_train_positive", "positive_plus_classifier_unlabeled"],
        default="labeled_positive",
    )
    parser.add_argument(
        "--eval-init-mode",
        choices=["env_reset", "valid_positive_states"],
        default="valid_positive_states",
    )
    parser.add_argument("--eval-episodes", type=int, default=5)
    parser.add_argument("--eval-horizon", type=int, default=400)
    parser.add_argument("--k-values", type=int, nargs="+", default=[1, 3, 5])
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-4)
    parser.add_argument("--unlabeled-threshold", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def train_positive_ids(split: dict) -> list[str]:
    positives = set(split["all_positive_ids"])
    return [demo_id for demo_id in split["train_ids"] if demo_id in positives]


def knn_policy(train_obs: np.ndarray, train_actions: np.ndarray, *, k: int):
    train_obs = np.asarray(train_obs, dtype=np.float32)
    train_actions = np.asarray(train_actions, dtype=np.float32)

    def policy(feature: np.ndarray, _rng: np.random.Generator, _low: np.ndarray, _high: np.ndarray) -> np.ndarray:
        diff = train_obs - feature[0]
        dist = np.einsum("ij,ij->i", diff, diff)
        if k <= 1:
            return train_actions[int(np.argmin(dist))]
        idx = np.argpartition(dist, kth=min(k, dist.size - 1))[:k]
        local_dist = dist[idx]
        weights = np.exp(-(local_dist - local_dist.min()) / (local_dist.std() + 1.0e-6))
        weights = weights / (weights.sum() + 1.0e-6)
        return np.sum(train_actions[idx] * weights[:, None], axis=0)

    return policy


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def main() -> None:
    args = parse_args()
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    env_meta = load_env_metadata(hdf5_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.source == "all_train_positive":
        source_ids = train_positive_ids(split)
    else:
        source_ids = split["labeled_positive_ids"]

    pos_raw = load_batch(hdf5_path, split["labeled_positive_ids"], obs_keys)
    neg_raw = load_batch(hdf5_path, split["labeled_negative_ids"], obs_keys)
    unl_raw = load_batch(hdf5_path, split["unlabeled_ids"], obs_keys)
    all_train_obs = np.concatenate([pos_raw.observations, neg_raw.observations, unl_raw.observations], axis=0)
    normalize_inputs = [pos_raw.observations, neg_raw.observations, unl_raw.observations]
    if args.source == "all_train_positive":
        all_pos_raw = load_batch(hdf5_path, source_ids, obs_keys)
        normalize_inputs.append(all_pos_raw.observations)
    obs_mean, obs_std, normalized = normalize(all_train_obs, *normalize_inputs)
    pos_obs, neg_obs, unl_obs = normalized[:3]
    pos = DemoBatch(pos_obs, pos_raw.actions, pos_raw.demo_ids)
    neg = DemoBatch(neg_obs, neg_raw.actions, neg_raw.demo_ids)
    unl = DemoBatch(unl_obs, unl_raw.actions, unl_raw.demo_ids)

    classifier_metrics = None
    selected_unlabeled = 0
    if args.source == "all_train_positive":
        all_pos_obs = normalized[3]
        library = DemoBatch(all_pos_obs, all_pos_raw.actions, all_pos_raw.demo_ids)
    elif args.source == "positive_plus_classifier_unlabeled":
        classifier, _history = train_state_action_classifier(
            pos.observations,
            pos.actions,
            neg.observations,
            neg.actions,
            seed=args.seed + 77,
            steps=args.classifier_steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
        )
        pos_logits = predict(classifier, state_action_features(pos.observations, pos.actions)).reshape(-1)
        neg_logits = predict(classifier, state_action_features(neg.observations, neg.actions)).reshape(-1)
        unl_logits = predict(classifier, state_action_features(unl.observations, unl.actions)).reshape(-1)
        unl_prob = sigmoid(unl_logits)
        keep = unl_prob >= args.unlabeled_threshold
        selected_unlabeled = int(keep.sum())
        if selected_unlabeled == 0:
            keep[np.argmax(unl_prob)] = True
            selected_unlabeled = 1
        library = DemoBatch(
            np.concatenate([pos.observations, unl.observations[keep]], axis=0),
            np.concatenate([pos.actions, unl.actions[keep]], axis=0),
            np.concatenate([pos.demo_ids, unl.demo_ids[keep]], axis=0),
        )
        classifier_metrics = {
            "labeled_accuracy": float(0.5 * ((pos_logits > 0).mean() + (neg_logits < 0).mean())),
            "pos_logit_mean": float(pos_logits.mean()),
            "neg_logit_mean": float(neg_logits.mean()),
            "unlabeled_prob_mean": float(unl_prob.mean()),
            "selected_unlabeled_transitions": selected_unlabeled,
        }
    else:
        library = pos

    eval_initials = None
    eval_initial_ids: list[str] = []
    if args.eval_init_mode == "valid_positive_states":
        eval_initial_ids = split["valid_positive_ids"]
        eval_initials = load_eval_initials(hdf5_path, eval_initial_ids)

    rows = []
    for k in args.k_values:
        method = f"knn_positive_k{k}_{args.source}"
        metrics = rollout_policy(
            env_meta=env_meta,
            obs_keys=obs_keys,
            obs_mean=obs_mean,
            obs_std=obs_std,
            eval_episodes=args.eval_episodes,
            eval_horizon=args.eval_horizon,
            eval_initials=eval_initials,
            seed=args.seed + 1000 * k,
            policy_fn=knn_policy(library.observations, library.actions, k=k),
        )
        row = {"method": method, **metrics}
        rows.append(row)
        print(
            f"{method}: success={row['success_rate']:.3f} "
            f"return={row['avg_return']:.3f} len={row['avg_len']:.1f}"
        )

    with (args.out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "success_rate", "avg_return", "avg_len"])
        writer.writeheader()
        writer.writerows(rows)

    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "source": args.source,
        "source_demo_count": len(source_ids),
        "source_transition_count": int(library.actions.shape[0]),
        "selected_unlabeled_transitions": selected_unlabeled,
        "classifier": classifier_metrics,
        "obs_keys": obs_keys,
        "env_name": env_meta["env_name"],
        "env_version": env_meta.get("env_version"),
        "eval_init_mode": args.eval_init_mode,
        "eval_initial_ids": eval_initial_ids,
        "eval_episodes": args.eval_episodes,
        "eval_horizon": args.eval_horizon,
        "k_values": args.k_values,
    }
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    report = [
        "# Robomimic Can KNN Smoke",
        "",
        f"Split path: `{args.split_path}`.",
        f"Source: `{args.source}`.",
        f"Source demos: `{len(source_ids)}`.",
        f"Source transitions: `{library.actions.shape[0]}`.",
        f"Selected unlabeled transitions: `{selected_unlabeled}`.",
        f"Evaluation init mode: `{args.eval_init_mode}`.",
        f"Evaluation episodes: `{args.eval_episodes}`.",
        f"Evaluation horizon: `{args.eval_horizon}`.",
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
                ]
            )
        ),
        "",
        "## Interpretation",
        "",
        "- This is a nonparametric sanity check for low-dimensional state support.",
        "- If KNN succeeds while the MLP BC fails, the immediate issue is the actor parameterization.",
        "- If KNN also fails, Robomimic Can likely needs a sequence-aware or official Robomimic imitation backbone before testing Tri-PIQL.",
    ]
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
