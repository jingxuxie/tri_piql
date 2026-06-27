#!/usr/bin/env python3
"""Prepare a Robomimic config whose train mask matches a transition-weight HDF5."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import h5py


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-config", type=Path, required=True)
    parser.add_argument("--transition-weights", type=Path, required=True)
    parser.add_argument("--split-path", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mask-prefix", required=True)
    parser.add_argument("--experiment-name", required=True)
    parser.add_argument("--policy-seed", type=int, default=0)
    return parser.parse_args()


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_mask(hdf5_path: str, key: str, demo_ids: list[str]) -> None:
    encoded = [demo_id.encode("utf-8") for demo_id in demo_ids]
    with h5py.File(hdf5_path, "a") as f:
        mask_group = f.require_group("mask")
        if key in mask_group:
            del mask_group[key]
        mask_group.create_dataset(key, data=encoded)


def weight_demo_ids(path: Path) -> list[str]:
    with h5py.File(path, "r") as f:
        return sorted(f["data"].keys(), key=demo_sort_key)


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    split = read_json(args.split_path)
    config = read_json(args.base_config)
    train_demo_ids = weight_demo_ids(args.transition_weights)
    hdf5_path = split["hdf5_path"]
    train_filter_key = f"{args.mask_prefix}_seed{args.policy_seed}_train"
    valid_filter_key = f"{args.mask_prefix}_seed{args.policy_seed}_valid_positive"
    write_mask(hdf5_path, train_filter_key, train_demo_ids)
    write_mask(hdf5_path, valid_filter_key, list(split["valid_positive_ids"]))

    train_dir = args.out_dir / "train"
    setup_dir = args.out_dir / "setup"
    setup_dir.mkdir(parents=True, exist_ok=True)
    train_dir.mkdir(parents=True, exist_ok=True)

    config["experiment"]["name"] = args.experiment_name
    config["train"]["data"][0]["path"] = hdf5_path
    config["train"]["data"][0]["filter_key"] = train_filter_key
    config["train"]["output_dir"] = str(train_dir.resolve())
    config["train"]["hdf5_filter_key"] = train_filter_key
    config["train"]["hdf5_validation_filter_key"] = None

    config_path = setup_dir / "config.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    diagnostics = {
        "split_path": str(args.split_path),
        "base_config": str(args.base_config),
        "transition_weights": str(args.transition_weights),
        "hdf5_path": hdf5_path,
        "train_filter_key": train_filter_key,
        "valid_filter_key": valid_filter_key,
        "train_demo_count": len(train_demo_ids),
        "train_demo_ids": train_demo_ids,
        "config_path": str(config_path),
        "train_output_dir": str(train_dir),
    }
    (setup_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    write_csv(
        setup_dir / "train_demos.csv",
        [{"demo_id": demo_id} for demo_id in train_demo_ids],
        ["demo_id"],
    )
    (setup_dir / "REPORT.md").write_text(
        "\n".join(
            [
                "# Transition-Weighted Config Setup",
                "",
                f"- Split: `{args.split_path}`.",
                f"- Transition weights: `{args.transition_weights}`.",
                f"- Train filter key: `{train_filter_key}`.",
                f"- Train demos: `{len(train_demo_ids)}`.",
                f"- Config: `{config_path}`.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(diagnostics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
