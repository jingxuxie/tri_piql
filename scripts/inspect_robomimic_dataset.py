from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("hdf5_path", type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_inspection/can_paired_low_dim"))
    parser.add_argument("--label-budget", type=int, default=10)
    parser.add_argument(
        "--split-seed",
        type=int,
        default=0,
        help="Seed for fallback train/valid splits and optional shuffled label pools.",
    )
    parser.add_argument(
        "--fallback-valid-positive-count",
        type=int,
        default=20,
        help="Positive holdout demos to reserve when the HDF5 file has no valid mask.",
    )
    parser.add_argument(
        "--fallback-valid-negative-count",
        type=int,
        default=20,
        help="Negative holdout demos to reserve when the HDF5 file has no valid mask.",
    )
    parser.add_argument(
        "--shuffle-label-pools",
        action="store_true",
        help="Shuffle train positives / negatives before taking scarce labels and unlabeled caps.",
    )
    parser.add_argument(
        "--unlabeled-positive-count",
        type=int,
        default=None,
        help="Optional cap on hidden-positive unlabeled train demos after labeled positives are removed.",
    )
    parser.add_argument(
        "--unlabeled-negative-count",
        type=int,
        default=None,
        help="Optional cap on hidden-negative unlabeled train demos after labeled negatives are removed.",
    )
    return parser.parse_args()


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


def decode_mask_values(values) -> list[str]:
    out = []
    for value in values:
        if isinstance(value, bytes):
            out.append(value.decode("utf-8"))
        else:
            out.append(str(value))
    return out


def shuffled(values: list[str], rng: np.random.Generator) -> list[str]:
    out = list(values)
    rng.shuffle(out)
    return out


def stats(values: np.ndarray) -> dict[str, float | int]:
    quantiles = np.quantile(values, [0.0, 0.10, 0.25, 0.50, 0.75, 0.90, 1.0])
    return {
        "count": int(values.size),
        "mean": float(values.mean()),
        "std": float(values.std()),
        "min": float(quantiles[0]),
        "p10": float(quantiles[1]),
        "p25": float(quantiles[2]),
        "p50": float(quantiles[3]),
        "p75": float(quantiles[4]),
        "p90": float(quantiles[5]),
        "max": float(quantiles[6]),
    }


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    with h5py.File(args.hdf5_path, "r") as f:
        demo_ids = sorted(f["data"].keys(), key=demo_sort_key)
        mask = {key: decode_mask_values(f["mask"][key][()]) for key in f["mask"].keys()} if "mask" in f else {}
        rows = []
        env_args = json.loads(f["data"].attrs["env_args"]) if "env_args" in f["data"].attrs else {}
        is_paired_can = "can" in args.hdf5_path.parts and "paired" in args.hdf5_path.parts
        for demo_id in demo_ids:
            demo = f["data"][demo_id]
            rewards = np.asarray(demo["rewards"])
            actions = np.asarray(demo["actions"])
            dones = np.asarray(demo["dones"])
            demo_return = float(rewards.sum())
            demo_success = int(demo_return > 0.0)
            demo_index = demo_sort_key(demo_id)
            rows.append(
                {
                    "demo_id": demo_id,
                    "demo_index": demo_index,
                    "pair_id": demo_index // 2 if is_paired_can else "",
                    "pair_role": (
                        "negative" if demo_index % 2 == 0 else "positive"
                    )
                    if is_paired_can
                    else ("success" if demo_success else "failure"),
                    "length": int(actions.shape[0]),
                    "return": demo_return,
                    "success": demo_success,
                    "done_last": int(dones[-1]),
                }
            )
        obs_shapes = {key: list(f["data"][demo_ids[0]]["obs"][key].shape[1:]) for key in f["data"][demo_ids[0]]["obs"].keys()}
        action_shape = list(f["data"][demo_ids[0]]["actions"].shape[1:])

    returns = np.asarray([row["return"] for row in rows], dtype=np.float64)
    lengths = np.asarray([row["length"] for row in rows], dtype=np.float64)
    positives = [row["demo_id"] for row in rows if row["success"] == 1]
    negatives = [row["demo_id"] for row in rows if row["success"] == 0]
    has_train_mask = "train" in mask
    has_valid_mask = "valid" in mask
    if has_train_mask or has_valid_mask:
        train_ids = mask.get("train", demo_ids)
        valid_ids = mask.get("valid", [])
        used_fallback_split = False
    else:
        split_rng = np.random.default_rng(args.split_seed)
        shuffled_pos = shuffled(positives, split_rng)
        shuffled_neg = shuffled(negatives, split_rng)
        n_valid_pos = min(args.fallback_valid_positive_count, len(shuffled_pos))
        n_valid_neg = min(args.fallback_valid_negative_count, len(shuffled_neg))
        valid_ids = sorted([*shuffled_pos[:n_valid_pos], *shuffled_neg[:n_valid_neg]], key=demo_sort_key)
        valid_set = set(valid_ids)
        train_ids = [demo_id for demo_id in demo_ids if demo_id not in valid_set]
        used_fallback_split = True
    train_pos = [demo_id for demo_id in train_ids if demo_id in positives]
    train_neg = [demo_id for demo_id in train_ids if demo_id in negatives]
    valid_pos = [demo_id for demo_id in valid_ids if demo_id in positives]
    valid_neg = [demo_id for demo_id in valid_ids if demo_id in negatives]
    if args.shuffle_label_pools:
        label_rng = np.random.default_rng(args.split_seed + 7919)
        train_pos = shuffled(train_pos, label_rng)
        train_neg = shuffled(train_neg, label_rng)

    n_pos = min(args.label_budget, len(train_pos))
    n_neg = min(args.label_budget, len(train_neg))
    labeled_pos = train_pos[:n_pos]
    labeled_neg = train_neg[:n_neg]
    labeled = set(labeled_pos + labeled_neg)
    unlabeled_pos_pool = [demo_id for demo_id in train_pos if demo_id not in labeled]
    unlabeled_neg_pool = [demo_id for demo_id in train_neg if demo_id not in labeled]
    n_unlabeled_pos = len(unlabeled_pos_pool) if args.unlabeled_positive_count is None else min(args.unlabeled_positive_count, len(unlabeled_pos_pool))
    n_unlabeled_neg = len(unlabeled_neg_pool) if args.unlabeled_negative_count is None else min(args.unlabeled_negative_count, len(unlabeled_neg_pool))
    unlabeled = sorted(
        [*unlabeled_pos_pool[:n_unlabeled_pos], *unlabeled_neg_pool[:n_unlabeled_neg]],
        key=demo_sort_key,
    )

    summary = {
        "hdf5_path": str(args.hdf5_path),
        "n_demos": len(demo_ids),
        "n_positive": len(positives),
        "n_negative": len(negatives),
        "env_name": env_args.get("env_name"),
        "return_stats": stats(returns),
        "length_stats": stats(lengths),
        "mask_sizes": {key: len(value) for key, value in mask.items()},
        "obs_shapes": obs_shapes,
        "action_shape": action_shape,
        "default_split": {
            "label_budget": args.label_budget,
            "split_seed": args.split_seed,
            "used_fallback_split": used_fallback_split,
            "unlabeled_positive_count": n_unlabeled_pos,
            "unlabeled_negative_count": n_unlabeled_neg,
            "labeled_positive_ids": labeled_pos,
            "labeled_negative_ids": labeled_neg,
            "unlabeled_ids": unlabeled,
            "valid_positive_ids": valid_pos,
            "valid_negative_ids": valid_neg,
        },
    }

    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (args.out_dir / "episodes.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["demo_id", "demo_index", "pair_id", "pair_role", "length", "return", "success", "done_last"],
        )
        writer.writeheader()
        writer.writerows(rows)
    (args.out_dir / "split_indices.json").write_text(
        json.dumps(
            {
                "hdf5_path": str(args.hdf5_path),
                "label_budget": args.label_budget,
                "split_seed": args.split_seed,
                "used_fallback_split": used_fallback_split,
                "unlabeled_positive_count": n_unlabeled_pos,
                "unlabeled_negative_count": n_unlabeled_neg,
                "all_positive_ids": positives,
                "all_negative_ids": negatives,
                "train_ids": train_ids,
                "valid_ids": valid_ids,
                "labeled_positive_ids": labeled_pos,
                "labeled_negative_ids": labeled_neg,
                "unlabeled_ids": unlabeled,
                "valid_positive_ids": valid_pos,
                "valid_negative_ids": valid_neg,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    report = [
        "# Robomimic Inspection",
        "",
        f"HDF5 path: `{args.hdf5_path}`.",
        f"Environment: `{summary['env_name']}`.",
        "",
        "## Dataset",
        "",
        f"- Demos: `{len(demo_ids)}`.",
        f"- Positive demos: `{len(positives)}`.",
        f"- Negative demos: `{len(negatives)}`.",
        f"- Return p10/p50/p90: `{summary['return_stats']['p10']:.3f}` / `{summary['return_stats']['p50']:.3f}` / `{summary['return_stats']['p90']:.3f}`.",
        f"- Length p10/p50/p90: `{summary['length_stats']['p10']:.1f}` / `{summary['length_stats']['p50']:.1f}` / `{summary['length_stats']['p90']:.1f}`.",
        f"- Masks: `{summary['mask_sizes']}`.",
        f"- Fallback split used: `{used_fallback_split}`.",
        f"- Observation keys: `{list(obs_shapes.keys())}`.",
        f"- Action shape: `{action_shape}`.",
        "",
        "## Default Tri-Signal Split",
        "",
        f"- Labeled positives: `{len(labeled_pos)}`.",
        f"- Labeled negatives: `{len(labeled_neg)}`.",
        f"- Unlabeled train demos: `{len(unlabeled)}`.",
        f"- Hidden-positive unlabeled demos: `{n_unlabeled_pos}`.",
        f"- Hidden-negative unlabeled demos: `{n_unlabeled_neg}`.",
        f"- Validation positives: `{len(valid_pos)}`.",
        f"- Validation negatives: `{len(valid_neg)}`.",
        "",
        "## Interpretation",
        "",
    ]
    if is_paired_can:
        report.extend(
            [
                "- The paired dataset is exactly balanced: even demo ids are failures, odd demo ids are paired successes.",
                "- This is a strong target for testing scarce good/bad labels plus a large unlabeled mixed pool.",
            ]
        )
    else:
        report.extend(
            [
                "- Positive and negative labels are derived from total sparse reward, not from paired same-initial-state demonstrations.",
                "- This is useful for cross-task mixed-quality validation, but it is a weaker bad-demo setting than Can Paired.",
            ]
        )
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
