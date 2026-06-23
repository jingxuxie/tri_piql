from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("hdf5_path", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--positive-train-mask", default="better_train")
    parser.add_argument("--negative-train-mask", default="worse_train")
    parser.add_argument("--positive-valid-mask", default="better_valid")
    parser.add_argument("--negative-valid-mask", default="worse_valid")
    parser.add_argument("--label-budget", type=int, default=10)
    parser.add_argument("--unlabeled-positive-count", type=int, default=80)
    parser.add_argument("--unlabeled-negative-count", type=int, default=80)
    parser.add_argument("--split-seed", type=int, default=0)
    return parser.parse_args()


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


def decode(values) -> list[str]:
    out = []
    for value in values:
        out.append(value.decode("utf-8") if isinstance(value, bytes) else str(value))
    return out


def shuffled(values: list[str], seed: int) -> list[str]:
    out = list(values)
    rng = np.random.default_rng(seed)
    rng.shuffle(out)
    return out


def read_mask(f: h5py.File, key: str) -> list[str]:
    if "mask" not in f or key not in f["mask"]:
        raise KeyError(f"mask {key!r} not found in {f.filename}")
    return sorted(decode(f["mask"][key][()]), key=demo_sort_key)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with h5py.File(args.hdf5_path, "r") as f:
        pos_train = read_mask(f, args.positive_train_mask)
        neg_train = read_mask(f, args.negative_train_mask)
        pos_valid = read_mask(f, args.positive_valid_mask)
        neg_valid = read_mask(f, args.negative_valid_mask)
        env_args = json.loads(f["data"].attrs["env_args"]) if "env_args" in f["data"].attrs else {}

    pos_train_ordered = shuffled(pos_train, args.split_seed + 101)
    neg_train_ordered = shuffled(neg_train, args.split_seed + 202)
    labeled_positive = pos_train_ordered[: args.label_budget]
    labeled_negative = neg_train_ordered[: args.label_budget]
    unlabeled_positive_pool = pos_train_ordered[args.label_budget :]
    unlabeled_negative_pool = neg_train_ordered[args.label_budget :]
    if args.unlabeled_positive_count > len(unlabeled_positive_pool):
        raise ValueError(
            f"requested {args.unlabeled_positive_count} unlabeled positives, "
            f"only {len(unlabeled_positive_pool)} available"
        )
    if args.unlabeled_negative_count > len(unlabeled_negative_pool):
        raise ValueError(
            f"requested {args.unlabeled_negative_count} unlabeled negatives, "
            f"only {len(unlabeled_negative_pool)} available"
        )
    unlabeled_positive = unlabeled_positive_pool[: args.unlabeled_positive_count]
    unlabeled_negative = unlabeled_negative_pool[: args.unlabeled_negative_count]
    train_ids = sorted([*pos_train, *neg_train], key=demo_sort_key)
    valid_ids = sorted([*pos_valid, *neg_valid], key=demo_sort_key)
    unlabeled_ids = sorted([*unlabeled_positive, *unlabeled_negative], key=demo_sort_key)

    split = {
        "hdf5_path": str(args.hdf5_path),
        "split_kind": "relative_quality_masks",
        "quality_positive_masks": [args.positive_train_mask, args.positive_valid_mask],
        "quality_negative_masks": [args.negative_train_mask, args.negative_valid_mask],
        "label_budget": args.label_budget,
        "split_seed": args.split_seed,
        "unlabeled_positive_count": len(unlabeled_positive),
        "unlabeled_negative_count": len(unlabeled_negative),
        "all_positive_ids": sorted([*pos_train, *pos_valid], key=demo_sort_key),
        "all_negative_ids": sorted([*neg_train, *neg_valid], key=demo_sort_key),
        "train_ids": train_ids,
        "valid_ids": valid_ids,
        "labeled_positive_ids": sorted(labeled_positive, key=demo_sort_key),
        "labeled_negative_ids": sorted(labeled_negative, key=demo_sort_key),
        "unlabeled_ids": unlabeled_ids,
        "valid_positive_ids": sorted(pos_valid, key=demo_sort_key),
        "valid_negative_ids": sorted(neg_valid, key=demo_sort_key),
    }
    (args.out_dir / "split_indices.json").write_text(json.dumps(split, indent=2), encoding="utf-8")
    report = [
        "# Robomimic Quality-Mask Split",
        "",
        f"HDF5 path: `{args.hdf5_path}`.",
        f"Environment: `{env_args.get('env_name')}`.",
        "",
        "This split uses Robomimic relative-quality masks, not sparse reward success/failure.",
        "It is useful as a cross-task score-calibration diagnostic, but should not be presented as a failure-demo benchmark.",
        "",
        "## Masks",
        "",
        f"- Positive train mask: `{args.positive_train_mask}` with `{len(pos_train)}` demos.",
        f"- Negative train mask: `{args.negative_train_mask}` with `{len(neg_train)}` demos.",
        f"- Positive valid mask: `{args.positive_valid_mask}` with `{len(pos_valid)}` demos.",
        f"- Negative valid mask: `{args.negative_valid_mask}` with `{len(neg_valid)}` demos.",
        "",
        "## Tri-Signal Split",
        "",
        f"- Labeled positives: `{len(labeled_positive)}`.",
        f"- Labeled negatives: `{len(labeled_negative)}`.",
        f"- Unlabeled demos: `{len(unlabeled_ids)}`.",
        f"- Hidden-positive unlabeled demos: `{len(unlabeled_positive)}`.",
        f"- Hidden-negative unlabeled demos: `{len(unlabeled_negative)}`.",
        f"- Validation positives: `{len(pos_valid)}`.",
        f"- Validation negatives: `{len(neg_valid)}`.",
        "",
        "## Files",
        "",
        "- `split_indices.json`: split file compatible with selector diagnostics.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
