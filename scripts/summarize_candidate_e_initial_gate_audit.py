from __future__ import annotations

import csv
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
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
from evaluate_robomimic_official_policy import obs_for_policy  # noqa: E402
from evaluate_robomimic_router_policy import (  # noqa: E402
    build_scorer,
    choose_obs_keys,
    score_action,
)
from run_robomimic_can_rollout_smoke import (  # noqa: E402
    action_bounds,
    load_env_metadata,
    load_eval_initials,
    make_env,
    reset_env,
)


OUT_DIR = Path("results/candidate_breakthrough")
SPLIT_PATH = Path("results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json")
POSITIVE_CKPT = Path(
    "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/"
    "train/can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn/"
    "20260625141435/models/model_epoch_200.pth"
)
WEIGHTED_CKPT = Path(
    "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/"
    "train/can_paired_pos40_bad80_split404_weighted_bc_policy0_official_bc_rnn/"
    "20260625143118/models/model_epoch_200.pth"
)
CANDIDATE_C_CKPT = Path(
    "results/candidate_breakthrough/candidate_c_mask_can404_e200_train/"
    "candidate_c_mask_can404_e200_seed0/20260626023458/models/model_epoch_200.pth"
)

SUMMARY_OUT = OUT_DIR / "candidate_e_initial_gate_feature_audit.csv"
REPORT_OUT = OUT_DIR / "candidate_e_initial_gate_audit_REPORT.md"


@dataclass(frozen=True)
class PolicySpec:
    method_id: str
    label: str
    checkpoint: Path


POLICIES = (
    PolicySpec("positive", "Positive-only NN top40", POSITIVE_CKPT),
    PolicySpec("weighted", "Weighted BC full pool", WEIGHTED_CKPT),
    PolicySpec("candidate_c", "Candidate C sequence-mask e200", CANDIDATE_C_CKPT),
)

OUTCOME_SOURCES = {
    "positive_success": Path(
        "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/eval/episode_metrics.csv"
    ),
    "weighted_success": Path(
        "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_weighted_bc_policy0/eval/episode_metrics.csv"
    ),
    "candidate_c_success": Path("results/candidate_breakthrough/candidate_c_mask_can404_e200_eval20_epoch200/episode_metrics.csv"),
    "router_no_bias_success": Path("results/candidate_breakthrough/candidate_b_router_pos_weighted_margin_nobias_eval20/episode_metrics.csv"),
    "router_anchor_support_success": Path(
        "results/candidate_breakthrough/candidate_b_router_pos_weighted_anchor_support_eval20/episode_metrics.csv"
    ),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def per_initial_counts(path: Path, eval_episodes: int = 20) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    rows = read_csv(path)[:eval_episodes]
    if len(rows) != eval_episodes:
        raise ValueError(f"{path}: expected {eval_episodes} rows, found {len(rows)}")
    for row in rows:
        counts[row["initial_demo_id"]] += int(float(row["success"]))
    return dict(counts)


def fmt(value: float) -> str:
    return f"{value:.6f}"


def main() -> None:
    os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
    os.environ.setdefault("MUJOCO_GL", "egl")
    split = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    env_meta = load_env_metadata(hdf5_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    loaded = {}
    first_ckpt_dict = None
    for spec in POLICIES:
        policy, ckpt_dict = FileUtils.policy_from_checkpoint(ckpt_path=str(spec.checkpoint), device=device, verbose=False)
        loaded[spec.method_id] = policy
        if first_ckpt_dict is None:
            first_ckpt_dict = ckpt_dict
    if first_ckpt_dict is None:
        raise ValueError("no policies loaded")

    class Args:
        obs_keys = "checkpoint"
        support_mode = "labeled"

    obs_keys = choose_obs_keys(Args, first_ckpt_dict)
    scorer = build_scorer(Args, split, hdf5_path, obs_keys)
    eval_initial_ids = split["valid_positive_ids"]
    eval_initials = load_eval_initials(hdf5_path, eval_initial_ids)
    outcomes = {name: per_initial_counts(path) for name, path in OUTCOME_SOURCES.items()}

    env = make_env(env_meta)
    low, high = action_bounds(env)
    rows: list[dict[str, object]] = []
    try:
        for initial in eval_initials:
            obs = reset_env(env, initial)
            policy_obs = obs_for_policy(obs, list(obs_keys))
            row: dict[str, object] = {"initial_demo_id": initial.demo_id}
            for spec in POLICIES:
                policy = loaded[spec.method_id]
                policy.start_episode()
                action = np.clip(np.asarray(policy(policy_obs), dtype=np.float32), low, high)
                margin, pos_dist, neg_dist = score_action(
                    scorer=scorer,
                    obs=obs,
                    action=action,
                    chunk_size=2048,
                )
                row[f"{spec.method_id}_margin"] = fmt(margin)
                row[f"{spec.method_id}_pos_dist"] = fmt(pos_dist)
                row[f"{spec.method_id}_neg_dist"] = fmt(neg_dist)
            row["weighted_minus_positive_margin"] = fmt(
                float(row["weighted_margin"]) - float(row["positive_margin"])
            )
            row["candidate_c_minus_positive_margin"] = fmt(
                float(row["candidate_c_margin"]) - float(row["positive_margin"])
            )
            for name, counts in outcomes.items():
                row[name] = counts.get(initial.demo_id, 0)
            row["oracle_best_count"] = max(int(row[name]) for name in OUTCOME_SOURCES)
            rows.append(row)
    finally:
        if hasattr(env, "close"):
            env.close()

    fieldnames = [
        "initial_demo_id",
        "positive_margin",
        "positive_pos_dist",
        "positive_neg_dist",
        "weighted_margin",
        "weighted_pos_dist",
        "weighted_neg_dist",
        "candidate_c_margin",
        "candidate_c_pos_dist",
        "candidate_c_neg_dist",
        "weighted_minus_positive_margin",
        "candidate_c_minus_positive_margin",
        *OUTCOME_SOURCES.keys(),
        "oracle_best_count",
    ]
    write_csv(SUMMARY_OUT, rows, fieldnames)

    positive_wins = sum(int(row["positive_success"]) for row in rows)
    weighted_wins = sum(int(row["weighted_success"]) for row in rows)
    candidate_c_wins = sum(int(row["candidate_c_success"]) for row in rows)
    router_wins = sum(int(row["router_no_bias_success"]) for row in rows)
    oracle = sum(int(row["oracle_best_count"]) for row in rows)
    lines = [
        "# Candidate E Initial-Gate Feature Audit",
        "",
        "This audit computes first-step deployable support features for positive-only, weighted BC, and Candidate C.",
        "Rollout outcomes are included only to diagnose whether an initial-state gate has signal; they are not training labels for a deployable rule.",
        "",
        "## First-20 Outcome Ceiling",
        "",
        f"- Positive-only: `{positive_wins}/20`.",
        f"- Weighted BC: `{weighted_wins}/20`.",
        f"- Candidate C: `{candidate_c_wins}/20`.",
        f"- Best existing deployable router in this audit: `{router_wins}/20`.",
        f"- Per-initial oracle over listed methods: `{oracle}/20`.",
        "",
        "## Initial Features",
        "",
        "| initial | pos margin | weighted margin | cand C margin | weighted-pos | candC-pos | positive | weighted | cand C | router | oracle |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['initial_demo_id']} | {row['positive_margin']} | {row['weighted_margin']} | "
            f"{row['candidate_c_margin']} | {row['weighted_minus_positive_margin']} | "
            f"{row['candidate_c_minus_positive_margin']} | {row['positive_success']} | "
            f"{row['weighted_success']} | {row['candidate_c_success']} | {row['router_no_bias_success']} | "
            f"{row['oracle_best_count']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- A useful deployable gate must identify the `demo_39` coverage gap without switching away from `demo_189` and other positive-anchor successes.",
            "- If first-step margins cannot separate those cases, a router needs temporal confidence features rather than a pure initial-state rule.",
            "",
            "## Artifacts",
            "",
            f"- Feature CSV: `{SUMMARY_OUT}`.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
