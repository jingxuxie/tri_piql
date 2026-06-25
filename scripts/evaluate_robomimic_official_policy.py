from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
ROBOMIMIC_ROOT = ROOT / "external" / "robomimic"
for path in (ROOT, SCRIPT_DIR, ROBOMIMIC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import robomimic.utils.file_utils as FileUtils  # noqa: E402
import robomimic.utils.torch_utils as TorchUtils  # noqa: E402
from run_robomimic_can_rollout_smoke import (  # noqa: E402
    action_bounds,
    env_success,
    load_env_metadata,
    load_eval_initials,
    make_env,
    reset_env,
)


def checkpoint_table(rows: list[dict[str, float | str]]) -> str:
    header = "| checkpoint | success_rate | avg_return | avg_len | eval_episodes |"
    separator = "|---|---:|---:|---:|---:|"
    lines = [header, separator]
    for row in rows:
        lines.append(
            f"| {row['checkpoint_name']} | {float(row['success_rate']):.3f} | "
            f"{float(row['avg_return']):.3f} | {float(row['avg_len']):.1f} | "
            f"{int(row['eval_episodes'])} |"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, action="append", default=[])
    parser.add_argument("--checkpoint-glob", type=str, action="append", default=[])
    parser.add_argument("--eval-episodes", type=int, default=10)
    parser.add_argument("--eval-horizon", type=int, default=400)
    parser.add_argument(
        "--eval-init-mode",
        choices=["env_reset", "valid_positive_states", "valid_all_states"],
        default="valid_positive_states",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--verbose-load", action="store_true")
    return parser.parse_args()


def checkpoint_sort_key(path: Path) -> tuple[int, str]:
    stem = path.stem
    if stem.startswith("model_epoch_"):
        try:
            return int(stem.removeprefix("model_epoch_")), str(path)
        except ValueError:
            pass
    return 10**9, str(path)


def resolve_checkpoints(args: argparse.Namespace) -> list[Path]:
    checkpoints = [path.expanduser().resolve() for path in args.checkpoint]
    for pattern in args.checkpoint_glob:
        checkpoints.extend(sorted(Path().glob(pattern)))
    unique = sorted({path.resolve() for path in checkpoints}, key=checkpoint_sort_key)
    if not unique:
        raise ValueError("no checkpoints provided; use --checkpoint or --checkpoint-glob")
    missing = [path for path in unique if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing checkpoint(s): {missing}")
    return unique


def obs_for_policy(obs: dict[str, np.ndarray], obs_keys: list[str]) -> dict[str, np.ndarray]:
    policy_obs = {}
    for key in obs_keys:
        if key in obs:
            value = obs[key]
        elif key == "object" and "object-state" in obs:
            value = obs["object-state"]
        else:
            raise KeyError(f"observation key {key!r} missing; available keys: {sorted(obs)}")
        policy_obs[key] = np.asarray(value, dtype=np.float32)
    return policy_obs


def make_device(name: str):
    if name == "auto":
        return TorchUtils.get_torch_device(try_to_use_cuda=True)
    if name == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("requested CUDA device, but torch.cuda.is_available() is false")
        return torch.device("cuda")
    return torch.device("cpu")


def rollout_checkpoint(
    *,
    checkpoint: Path,
    env_meta: dict,
    eval_initials,
    eval_episodes: int,
    eval_horizon: int,
    seed: int,
    device,
    verbose_load: bool,
) -> tuple[dict[str, float | str], list[dict[str, float | str]]]:
    policy, ckpt_dict = FileUtils.policy_from_checkpoint(
        ckpt_path=str(checkpoint),
        device=device,
        verbose=verbose_load,
    )
    obs_keys = list(ckpt_dict["shape_metadata"]["all_shapes"].keys())
    env = make_env(env_meta)
    low, high = action_bounds(env)
    episode_rows: list[dict[str, float | str]] = []
    successes = []
    returns = []
    lengths = []
    np.random.seed(seed)
    torch.manual_seed(seed)
    try:
        for episode in range(eval_episodes):
            np.random.seed(seed + episode)
            initial = eval_initials[episode % len(eval_initials)] if eval_initials else None
            obs = reset_env(env, initial)
            policy.start_episode()
            total_return = 0.0
            success = False
            length = 0
            for t in range(eval_horizon):
                action = policy(obs_for_policy(obs, obs_keys))
                action = np.clip(np.asarray(action, dtype=np.float32), low, high)
                obs, reward, done, _info = env.step(action)
                total_return += float(reward)
                length = t + 1
                success = success or env_success(env, float(reward))
                if success or done:
                    break
            successes.append(float(success))
            returns.append(total_return)
            lengths.append(float(length))
            episode_rows.append(
                {
                    "checkpoint": str(checkpoint),
                    "episode": episode,
                    "initial_demo_id": initial.demo_id if initial else "",
                    "success": float(success),
                    "return": total_return,
                    "length": float(length),
                }
            )
    finally:
        if hasattr(env, "close"):
            env.close()
    row = {
        "checkpoint": str(checkpoint),
        "checkpoint_name": checkpoint.stem,
        "success_rate": float(np.mean(successes)),
        "avg_return": float(np.mean(returns)),
        "avg_len": float(np.mean(lengths)),
        "eval_episodes": eval_episodes,
    }
    return row, episode_rows


def main() -> None:
    # Robosuite/MuJoCo defaults are easiest to keep explicit here because this script
    # is usually launched through conda from a non-interactive shell.
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
    os.environ.setdefault("MUJOCO_GL", "egl")
    args = parse_args()
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    env_meta = load_env_metadata(hdf5_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.eval_init_mode == "valid_positive_states":
        eval_initial_ids = split["valid_positive_ids"]
    elif args.eval_init_mode == "valid_all_states":
        eval_initial_ids = split["valid_ids"]
    else:
        eval_initial_ids = []
    eval_initials = load_eval_initials(hdf5_path, eval_initial_ids) if eval_initial_ids else None

    checkpoints = resolve_checkpoints(args)
    device = make_device(args.device)
    rows = []
    episode_rows = []
    for i, checkpoint in enumerate(checkpoints):
        row, ckpt_episode_rows = rollout_checkpoint(
            checkpoint=checkpoint,
            env_meta=env_meta,
            eval_initials=eval_initials,
            eval_episodes=args.eval_episodes,
            eval_horizon=args.eval_horizon,
            seed=args.seed + i * 1000,
            device=device,
            verbose_load=args.verbose_load,
        )
        rows.append(row)
        episode_rows.extend(ckpt_episode_rows)
        print(
            f"{checkpoint.name}: success={row['success_rate']:.3f} "
            f"return={row['avg_return']:.3f} len={row['avg_len']:.1f}",
            flush=True,
        )

    with (args.out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["checkpoint", "checkpoint_name", "success_rate", "avg_return", "avg_len", "eval_episodes"],
        )
        writer.writeheader()
        writer.writerows(rows)
    with (args.out_dir / "episode_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["checkpoint", "episode", "initial_demo_id", "success", "return", "length"],
        )
        writer.writeheader()
        writer.writerows(episode_rows)

    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "env_name": env_meta["env_name"],
        "env_version": env_meta.get("env_version"),
        "eval_init_mode": args.eval_init_mode,
        "eval_initial_ids": eval_initial_ids,
        "eval_episodes": args.eval_episodes,
        "eval_horizon": args.eval_horizon,
        "seed": args.seed,
        "device": str(device),
        "checkpoints": [str(path) for path in checkpoints],
    }
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    report = [
        "# Official Robomimic Policy Evaluation",
        "",
        f"Split path: `{args.split_path}`.",
        f"HDF5 path: `{hdf5_path}`.",
        f"Environment: `{env_meta['env_name']}` version `{env_meta.get('env_version')}`.",
        f"Eval init mode: `{args.eval_init_mode}`.",
        f"Eval episodes: `{args.eval_episodes}`.",
        f"Eval horizon: `{args.eval_horizon}`.",
        f"Device: `{device}`.",
        "",
        "## Rollout Metrics",
        "",
        checkpoint_table(rows),
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
