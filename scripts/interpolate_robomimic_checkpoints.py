#!/usr/bin/env python3
"""Interpolate Robomimic policy checkpoints for quick anchor-drift screens."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import torch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--name", type=str, default="interp")
    parser.add_argument("--alpha", type=float, action="append", required=True)
    return parser.parse_args()


def load_checkpoint(path: Path) -> dict:
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def interpolate_tensor(base: torch.Tensor, target: torch.Tensor, alpha: float) -> torch.Tensor:
    if not torch.is_floating_point(base):
        return base
    return base.mul(1.0 - alpha).add(target.to(dtype=base.dtype), alpha=alpha)


def main() -> None:
    args = parse_args()
    base = load_checkpoint(args.base)
    target = load_checkpoint(args.target)

    base_nets = base["model"]["nets"]
    target_nets = target["model"]["nets"]
    missing = sorted(set(base_nets) ^ set(target_nets))
    if missing:
        raise ValueError(f"checkpoint net keys differ: {missing[:10]}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for alpha in args.alpha:
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(f"alpha must be in [0, 1], got {alpha}")

        ckpt = copy.deepcopy(base)
        new_nets = ckpt["model"]["nets"]
        for key, base_tensor in base_nets.items():
            target_tensor = target_nets[key]
            if base_tensor.shape != target_tensor.shape:
                raise ValueError(
                    f"shape mismatch for {key}: {tuple(base_tensor.shape)} vs {tuple(target_tensor.shape)}"
                )
            new_nets[key] = interpolate_tensor(base_tensor, target_tensor, alpha)

        alpha_label = f"{alpha:.2f}".replace(".", "p")
        out_path = args.out_dir / f"{args.name}_alpha_{alpha_label}.pth"
        torch.save(ckpt, out_path)
        manifest_rows.append({"alpha": alpha, "checkpoint": str(out_path)})

    manifest_path = args.out_dir / f"{args.name}_manifest.json"
    manifest = {
        "base": str(args.base),
        "target": str(args.target),
        "checkpoints": manifest_rows,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(manifest_rows)} checkpoints to {args.out_dir}")
    print(f"wrote {manifest_path}")


if __name__ == "__main__":
    main()
