from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from copy import deepcopy
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_can_playback_check"))
    parser.add_argument(
        "--demo-source",
        choices=["valid_positive", "valid_negative", "valid_all", "labeled_positive"],
        default="valid_positive",
    )
    parser.add_argument("--max-demos", type=int, default=10)
    return parser.parse_args()


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


def make_env(env_meta: dict):
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
    os.environ.setdefault("MUJOCO_GL", "egl")
    import robosuite as suite

    return suite.make(env_name=env_meta["env_name"], **deepcopy(env_meta["env_kwargs"]))


def reset_to_demo_initial(env, group) -> None:
    env.reset()
    env.reset_from_xml_string(group.attrs["model_file"])
    env.sim.reset()
    env.sim.set_state_from_flattened(np.asarray(group["states"][0], dtype=np.float64))
    env.sim.forward()
    if hasattr(env, "update_state"):
        env.update_state()


def env_success(env, reward: float) -> bool:
    if hasattr(env, "is_success"):
        result = env.is_success()
        if isinstance(result, dict) and "task" in result:
            return bool(result["task"])
        return bool(result)
    if hasattr(env, "_check_success"):
        return bool(env._check_success())
    return reward > 0.0


def source_ids(split: dict, source: str) -> list[str]:
    if source == "valid_positive":
        return split["valid_positive_ids"]
    if source == "valid_negative":
        return split["valid_negative_ids"]
    if source == "valid_all":
        return split["valid_ids"]
    if source == "labeled_positive":
        return split["labeled_positive_ids"]
    raise ValueError(source)


def main() -> None:
    args = parse_args()
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    demo_ids = sorted(source_ids(split, args.demo_source), key=demo_sort_key)[: args.max_demos]
    args.out_dir.mkdir(parents=True, exist_ok=True)

    with h5py.File(split["hdf5_path"], "r") as f:
        env_meta = json.loads(f["data"].attrs["env_args"])
        env = make_env(env_meta)
        rows = []
        try:
            for demo_id in demo_ids:
                group = f["data"][demo_id]
                reset_to_demo_initial(env, group)
                total = 0.0
                success = False
                length = 0
                for i, action in enumerate(group["actions"]):
                    _obs, reward, done, _info = env.step(np.asarray(action, dtype=np.float32))
                    total += float(reward)
                    length = i + 1
                    success = success or env_success(env, float(reward))
                    if success or done:
                        break
                rows.append(
                    {
                        "demo_id": demo_id,
                        "playback_success": float(success),
                        "playback_return": total,
                        "playback_len": length,
                        "stored_return": float(np.asarray(group["rewards"]).sum()),
                        "stored_len": int(group["actions"].shape[0]),
                    }
                )
                print(
                    f"{demo_id}: success={float(success):.0f} return={total:.3f} "
                    f"len={length} stored_return={float(np.asarray(group['rewards']).sum()):.3f}"
                )
        finally:
            if hasattr(env, "close"):
                env.close()

    with (args.out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["demo_id", "playback_success", "playback_return", "playback_len", "stored_return", "stored_len"],
        )
        writer.writeheader()
        writer.writerows(rows)

    success_rate = float(np.mean([row["playback_success"] for row in rows])) if rows else 0.0
    report = [
        "# Robomimic Playback Check",
        "",
        f"Split path: `{args.split_path}`.",
        f"HDF5 path: `{split['hdf5_path']}`.",
        f"Demo source: `{args.demo_source}`.",
        f"Environment: `{env_meta['env_name']}` version `{env_meta.get('env_version')}`.",
        f"Demos replayed: `{len(rows)}`.",
        f"Playback success rate: `{success_rate:.3f}`.",
        "",
        "| demo | success | replay return | replay length | stored return | stored length |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        report.append(
            f"| {row['demo_id']} | {row['playback_success']:.0f} | {row['playback_return']:.3f} | "
            f"{row['playback_len']} | {row['stored_return']:.3f} | {row['stored_len']} |"
        )
    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Stored simulator XML/state plus stored actions replay successfully when this rate is high.",
            "- If learned policy rollouts fail while playback succeeds, the issue is policy strength or closed-loop imitation, not basic simulator reconstruction.",
        ]
    )
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
