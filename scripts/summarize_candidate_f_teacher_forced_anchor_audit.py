#!/usr/bin/env python3
"""Audit train-only teacher-forced signals for choosing a router anchor.

This is a preflight, not a new policy result. It asks whether labeled-positive
training demonstrations contain a deployable signal for choosing the default
policy anchor before using initial-state fallback rules.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import h5py
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
ROBOMIMIC_ROOT = ROOT / "external" / "robomimic"
for path in (ROOT, SCRIPT_DIR, ROBOMIMIC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import robomimic.utils.file_utils as FileUtils  # noqa: E402
from evaluate_robomimic_official_policy import obs_for_policy  # noqa: E402
from evaluate_robomimic_router_policy import (  # noqa: E402
    build_scorer,
    choose_obs_keys,
    score_action,
)


OUT = ROOT / "results" / "candidate_breakthrough"
FINAL = ROOT / "results" / "final_paper_v02"
SPLITS = [101, 202, 303, 404, 505]
METHODS = ["positive_only_nn", "weighted_bc", "triage_bc"]
METHOD_LABELS = {
    "positive_only_nn": "positive",
    "weighted_bc": "weighted",
    "triage_bc": "triage",
}
N_ENDPOINT_EPISODES = 20


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--max-demos", type=int, default=10)
    parser.add_argument("--max-steps-per-demo", type=int, default=120)
    parser.add_argument("--support-stride", type=int, default=10)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def endpoint_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if rows and "checkpoint" in rows[0]:
        checkpoints = {row["checkpoint"] for row in rows}
        if len(checkpoints) > 1:
            filtered = [row for row in rows if "model_epoch_200" in row["checkpoint"]]
            if filtered:
                return filtered
    return rows


def first20_success(split: int, method: str) -> int:
    path = (
        FINAL
        / "per_seed"
        / f"can_paired_pos40_bad80_split{split}_{method}_policy0"
        / "eval"
        / "episode_metrics.csv"
    )
    rows = endpoint_rows(read_csv(path))[:N_ENDPOINT_EPISODES]
    return sum(int(float(row["success"])) for row in rows)


def split_path(split: int) -> Path:
    return FINAL / "splits" / f"can_paired_pos40_bad80_split{split}" / "split_indices.json"


def checkpoint_path(split: int, method: str) -> Path:
    run_dir = FINAL / "per_seed" / f"can_paired_pos40_bad80_split{split}_{method}_policy0"
    matches = sorted(run_dir.glob("train*/**/models/model_epoch_200.pth"))
    if matches:
        return matches[-1]
    matches = sorted(run_dir.glob("train*/**/last.pth"))
    if matches:
        return matches[-1]
    raise FileNotFoundError(f"no endpoint checkpoint found for split {split} {method}")


def demo_obs_at(group: h5py.Group, obs_keys: tuple[str, ...], t: int) -> dict[str, np.ndarray]:
    obs_group = group["obs"]
    return {key: np.asarray(obs_group[key][t], dtype=np.float32) for key in obs_keys}


class ScorerArgs:
    obs_keys = "checkpoint"
    support_mode = "labeled"


def policy_metrics_for_split(
    *,
    split: int,
    method: str,
    device: torch.device,
    max_demos: int,
    max_steps_per_demo: int,
    support_stride: int,
) -> dict[str, float | int | str]:
    spath = split_path(split)
    split_data = json.loads(spath.read_text(encoding="utf-8"))
    ckpt = checkpoint_path(split, method)
    policy, ckpt_dict = FileUtils.policy_from_checkpoint(ckpt_path=str(ckpt), device=device, verbose=False)
    obs_keys = choose_obs_keys(ScorerArgs, ckpt_dict)
    scorer = build_scorer(ScorerArgs, split_data, split_data["hdf5_path"], obs_keys)

    l2_values: list[float] = []
    mse_values: list[float] = []
    first_l2_values: list[float] = []
    first_mse_values: list[float] = []
    margin_values: list[float] = []
    pos_dist_values: list[float] = []
    neg_dist_values: list[float] = []
    first_margin_values: list[float] = []
    first_pos_dist_values: list[float] = []
    first_neg_dist_values: list[float] = []

    demo_ids = list(split_data["labeled_positive_ids"])[:max_demos]
    with h5py.File(split_data["hdf5_path"], "r") as f:
        for demo_id in demo_ids:
            group = f["data"][demo_id]
            actions = np.asarray(group["actions"], dtype=np.float32)
            n_steps = min(actions.shape[0], max_steps_per_demo)
            policy.start_episode()
            for t in range(n_steps):
                obs = demo_obs_at(group, obs_keys, t)
                policy_obs = obs_for_policy(obs, list(obs_keys))
                with torch.no_grad():
                    pred = np.asarray(policy(policy_obs), dtype=np.float32).reshape(-1)
                target = actions[t].reshape(-1)
                diff = pred - target
                l2 = float(np.linalg.norm(diff))
                mse = float(np.mean(diff * diff))
                l2_values.append(l2)
                mse_values.append(mse)
                if t == 0:
                    first_l2_values.append(l2)
                    first_mse_values.append(mse)
                if t == 0 or t % support_stride == 0:
                    margin, pos_dist, neg_dist = score_action(
                        scorer=scorer,
                        obs=obs,
                        action=pred,
                        chunk_size=2048,
                    )
                    margin_values.append(float(margin))
                    pos_dist_values.append(float(pos_dist))
                    neg_dist_values.append(float(neg_dist))
                    if t == 0:
                        first_margin_values.append(float(margin))
                        first_pos_dist_values.append(float(pos_dist))
                        first_neg_dist_values.append(float(neg_dist))

    def mean(values: list[float]) -> float:
        return float(np.mean(values)) if values else float("nan")

    return {
        "split": split,
        "method": METHOD_LABELS[method],
        "checkpoint": str(ckpt.relative_to(ROOT)),
        "demo_count": len(demo_ids),
        "step_count": len(l2_values),
        "action_l2_mean": mean(l2_values),
        "action_mse_mean": mean(mse_values),
        "first_action_l2_mean": mean(first_l2_values),
        "first_action_mse_mean": mean(first_mse_values),
        "support_margin_mean": mean(margin_values),
        "support_pos_dist_mean": mean(pos_dist_values),
        "support_neg_dist_mean": mean(neg_dist_values),
        "first_support_margin_mean": mean(first_margin_values),
        "first_support_pos_dist_mean": mean(first_pos_dist_values),
        "first_support_neg_dist_mean": mean(first_neg_dist_values),
        "first20_success": first20_success(split, method),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def main() -> None:
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
    os.environ.setdefault("MUJOCO_GL", "egl")
    args = parse_args()
    device = torch.device(args.device)
    np.random.seed(0)
    torch.manual_seed(0)

    metric_rows: list[dict[str, object]] = []
    for split in SPLITS:
        for method in METHODS:
            metric_rows.append(
                policy_metrics_for_split(
                    split=split,
                    method=method,
                    device=device,
                    max_demos=args.max_demos,
                    max_steps_per_demo=args.max_steps_per_demo,
                    support_stride=args.support_stride,
                )
            )

    fieldnames = [
        "split",
        "method",
        "demo_count",
        "step_count",
        "action_l2_mean",
        "action_mse_mean",
        "first_action_l2_mean",
        "first_action_mse_mean",
        "support_margin_mean",
        "support_pos_dist_mean",
        "support_neg_dist_mean",
        "first_support_margin_mean",
        "first_support_pos_dist_mean",
        "first_support_neg_dist_mean",
        "first20_success",
        "checkpoint",
    ]
    metrics_csv = OUT / "candidate_f_teacher_forced_anchor_metrics.csv"
    write_csv(metrics_csv, metric_rows, fieldnames)

    by_split: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in metric_rows:
        by_split[int(row["split"])].append(row)

    rule_specs = {
        "min_action_l2": lambda rows: min(rows, key=lambda row: float(row["action_l2_mean"])),
        "min_first_action_l2": lambda rows: min(rows, key=lambda row: float(row["first_action_l2_mean"])),
        "max_support_margin": lambda rows: max(rows, key=lambda row: float(row["support_margin_mean"])),
        "min_support_pos_dist": lambda rows: min(rows, key=lambda row: float(row["support_pos_dist_mean"])),
        "max_first_support_margin": lambda rows: max(rows, key=lambda row: float(row["first_support_margin_mean"])),
    }
    rule_rows: list[dict[str, object]] = []
    for split in SPLITS:
        rows = by_split[split]
        best_endpoint = max(int(row["first20_success"]) for row in rows)
        endpoint_best_method = max(rows, key=lambda row: int(row["first20_success"]))["method"]
        for rule_name, chooser in rule_specs.items():
            chosen = chooser(rows)
            rule_rows.append(
                {
                    "split": split,
                    "rule": rule_name,
                    "chosen_method": chosen["method"],
                    "chosen_first20_success": chosen["first20_success"],
                    "endpoint_best_method": endpoint_best_method,
                    "endpoint_best_first20_success": best_endpoint,
                    "delta_vs_endpoint_best": int(chosen["first20_success"]) - best_endpoint,
                }
            )

    rule_csv = OUT / "candidate_f_teacher_forced_anchor_rules.csv"
    write_csv(
        rule_csv,
        rule_rows,
        [
            "split",
            "rule",
            "chosen_method",
            "chosen_first20_success",
            "endpoint_best_method",
            "endpoint_best_first20_success",
            "delta_vs_endpoint_best",
        ],
    )

    aggregate_lines = []
    for rule_name in rule_specs:
        selected = [row for row in rule_rows if row["rule"] == rule_name]
        total = sum(int(row["chosen_first20_success"]) for row in selected)
        best_total = sum(int(row["endpoint_best_first20_success"]) for row in selected)
        choices = ", ".join(f"{row['split']}:{row['chosen_method']}" for row in selected)
        aggregate_lines.append((rule_name, total, best_total, choices))

    report_path = OUT / "candidate_f_teacher_forced_anchor_audit_REPORT.md"
    lines = [
        "# Candidate F Teacher-Forced Anchor Audit",
        "",
        "This audit uses only labeled-positive training demonstrations to compare",
        "trained policy actions under teacher forcing. Endpoint first-20 counts",
        "are included only to see whether a train-only anchor rule would have",
        "selected the right baseline policy.",
        "",
        "## Per-Split Metrics",
        "",
        "| split | method | action L2 | first L2 | support margin | support pos dist | first20 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for split in SPLITS:
        for row in by_split[split]:
            lines.append(
                f"| {split} | {row['method']} | {fmt(row['action_l2_mean'])} | "
                f"{fmt(row['first_action_l2_mean'])} | {fmt(row['support_margin_mean'])} | "
                f"{fmt(row['support_pos_dist_mean'])} | {row['first20_success']}/20 |"
            )
    lines.extend(
        [
            "",
            "## Rule Aggregate",
            "",
            "| rule | selected first20 total | oracle baseline total | choices |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for rule_name, total, best_total, choices in aggregate_lines:
        lines.append(f"| {rule_name} | {total}/100 | {best_total}/100 | {choices} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- If a rule selects positive-only on split 101, it cannot solve the main",
            "  fixed-threshold failure because weighted BC is the best completed",
            "  first-20 baseline on that split.",
            "- A useful Candidate F anchor rule should approach the per-split baseline",
            "  oracle without using endpoint outcomes.",
            "",
            "## Artifacts",
            "",
            f"- Metrics CSV: `{metrics_csv.relative_to(ROOT)}`.",
            f"- Rule CSV: `{rule_csv.relative_to(ROOT)}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
