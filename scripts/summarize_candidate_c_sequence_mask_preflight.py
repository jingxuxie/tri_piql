from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(".")
DEFAULT_SPLIT_PATH = ROOT / "results" / "final_paper_v02" / "splits" / "can_paired_pos40_bad80_split404" / "split_indices.json"
DEFAULT_WEIGHTED_DIAGNOSTICS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
    / "setup"
    / "diagnostics.json"
)
DEFAULT_POSITIVE_DIAGNOSTICS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
    / "setup"
    / "diagnostics.json"
)
DEFAULT_SCORE_RANKINGS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "score_diagnostics"
    / "can_paired_pos40_bad80_split404_policy0"
    / "demo_rankings.csv"
)
DEFAULT_OUT_DIR = ROOT / "results" / "candidate_breakthrough" / "candidate_c_sequence_mask_preflight"

STANDARD_LOW_DIM_OBS = [
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "object",
]


@dataclass(frozen=True)
class DemoArrays:
    features: np.ndarray
    actions: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--weighted-diagnostics", type=Path, default=DEFAULT_WEIGHTED_DIAGNOSTICS)
    parser.add_argument("--positive-diagnostics", type=Path, default=DEFAULT_POSITIVE_DIAGNOSTICS)
    parser.add_argument("--score-rankings", type=Path, default=DEFAULT_SCORE_RANKINGS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--score-threshold", type=float, default=0.20)
    parser.add_argument("--margin-threshold", type=float, default=2.0)
    parser.add_argument("--chunk-size", type=int, default=2048)
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def sorted_demos(demo_ids: list[str]) -> list[str]:
    return sorted(demo_ids, key=demo_sort_key)


def obs_vector(group) -> np.ndarray:
    actions = group["actions"]
    obs_group = group["obs"]
    parts = [
        np.asarray(obs_group[key], dtype=np.float32).reshape((actions.shape[0], -1))
        for key in STANDARD_LOW_DIM_OBS
    ]
    return np.concatenate(parts, axis=1).astype(np.float32, copy=False)


def load_arrays(hdf5_path: str, demo_ids: list[str]) -> dict[str, DemoArrays]:
    out = {}
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in sorted_demos(demo_ids):
            group = f["data"][demo_id]
            obs = obs_vector(group)
            actions = np.asarray(group["actions"], dtype=np.float32)
            out[demo_id] = DemoArrays(
                features=np.concatenate([obs, actions], axis=1).astype(np.float32, copy=False),
                actions=actions,
            )
    return out


def nearest_dist(query: np.ndarray, reference: np.ndarray, *, chunk_size: int) -> np.ndarray:
    out = np.empty((query.shape[0],), dtype=np.float32)
    ref_t = reference.T
    ref_norm = np.sum(reference * reference, axis=1, keepdims=True).T
    for start in range(0, query.shape[0], chunk_size):
        end = min(start + chunk_size, query.shape[0])
        block = query[start:end]
        dist2 = np.sum(block * block, axis=1, keepdims=True) + ref_norm - 2.0 * block @ ref_t
        out[start:end] = np.sqrt(np.maximum(np.min(dist2, axis=1), 0.0)).astype(np.float32)
    return out


def score_by_demo(path: Path) -> dict[str, float]:
    return {row["demo_id"]: float(row["score"]) for row in read_csv(path)}


def fmt(value: float) -> str:
    return f"{value:.6f}"


def write_weight_hdf5(path: Path, weights: dict[str, dict[str, np.ndarray]], metadata: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        f.attrs["metadata_json"] = json.dumps(metadata, sort_keys=True)
        data_group = f.create_group("data")
        for demo_id in sorted_demos(list(weights)):
            demo_group = data_group.create_group(demo_id)
            for key, value in weights[demo_id].items():
                demo_group.create_dataset(key, data=value.astype(np.float32), compression="gzip")


def write_report(path: Path, summary: dict[str, object], output_paths: dict[str, Path]) -> None:
    lines = [
        "# Candidate C Sequence-Mask Preflight",
        "",
        "This preflight keeps the positive-only NN train pool at full weight and adds only",
        "locally safe transitions from the broader weighted-BC pool.",
        "",
        "## Rule",
        "",
        f"- Demo classifier threshold: `{summary['score_threshold']}`.",
        f"- Transition safety margin threshold: `{summary['margin_threshold']}`.",
        "- Margin is nearest labeled-negative state-action distance minus nearest labeled-positive state-action distance.",
        "",
        "## Mass",
        "",
        f"- Anchor demos: `{summary['anchor_demo_count']}`.",
        f"- Extra demos considered: `{summary['extra_demo_count']}`.",
        f"- Extra hidden-positive demos with selected transitions: `{summary['extra_positive_demo_count']}`.",
        f"- Extra hidden-bad demos with selected transitions: `{summary['extra_bad_demo_count']}`.",
        f"- Extra hidden-positive transition mass: `{summary['extra_positive_mass']}`.",
        f"- Extra hidden-bad transition mass: `{summary['extra_bad_mass']}`.",
        f"- Extra hidden-bad masked fraction: `{summary['extra_bad_masked_fraction']:.3f}`.",
        f"- Total masked mass fraction from extra demos: `{summary['extra_mass_fraction_total']:.3f}`.",
        "",
        "## Read",
        "",
        "- The broad pool is highly contaminated outside the positive-only anchor, so this mask is deliberately conservative.",
        "- This is a trainable Candidate C input, but the preflight does not by itself prove policy improvement.",
        "",
        "## Outputs",
        "",
        f"- Mask HDF5: `{output_paths['weights_hdf5']}`.",
        f"- Per-demo summary CSV: `{output_paths['summary_csv']}`.",
        f"- Recipe JSON: `{output_paths['recipe_json']}`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    split = read_json(args.split_path)
    weighted = read_json(args.weighted_diagnostics)
    positive = read_json(args.positive_diagnostics)
    scores = score_by_demo(args.score_rankings)
    hdf5_path = split["hdf5_path"]
    train_ids = list(weighted["train_demo_ids"])
    anchor_ids = set(positive["train_demo_ids"])
    extra_ids = [demo_id for demo_id in train_ids if demo_id not in anchor_ids]
    all_positive = set(split["all_positive_ids"])

    arrays = load_arrays(hdf5_path, sorted_demos(list(set(train_ids) | set(split["labeled_negative_ids"]))))
    fit = np.concatenate([arrays[demo_id].features for demo_id in train_ids + list(split["labeled_negative_ids"])], axis=0)
    mean = fit.mean(axis=0, keepdims=True)
    std = fit.std(axis=0, keepdims=True) + 1.0e-6
    normalized = {demo_id: ((arrays[demo_id].features - mean) / std).astype(np.float32) for demo_id in arrays}
    positive_ref = np.concatenate([normalized[demo_id] for demo_id in split["labeled_positive_ids"]], axis=0)
    negative_ref = np.concatenate([normalized[demo_id] for demo_id in split["labeled_negative_ids"]], axis=0)

    weights: dict[str, dict[str, np.ndarray]] = {}
    rows: list[dict[str, object]] = []
    extra_pos_mass = 0
    extra_bad_mass = 0
    extra_pos_demos = 0
    extra_bad_demos = 0
    total_mass = 0
    total_transition_count = 0

    for demo_id in sorted_demos(train_ids):
        length = arrays[demo_id].actions.shape[0]
        total_transition_count += length
        loss_weight = np.zeros((length,), dtype=np.float32)
        margin = np.zeros((length,), dtype=np.float32)
        pos_dist = np.zeros((length,), dtype=np.float32)
        neg_dist = np.zeros((length,), dtype=np.float32)
        role = "anchor"
        if demo_id in anchor_ids:
            loss_weight.fill(1.0)
        else:
            role = "extra_masked"
            pos_dist = nearest_dist(normalized[demo_id], positive_ref, chunk_size=args.chunk_size)
            neg_dist = nearest_dist(normalized[demo_id], negative_ref, chunk_size=args.chunk_size)
            margin = neg_dist - pos_dist
            if scores.get(demo_id, 0.0) >= args.score_threshold:
                loss_weight = (margin > args.margin_threshold).astype(np.float32)

        selected = int(np.sum(loss_weight > 0.0))
        total_mass += selected
        hidden_label = "positive" if demo_id in all_positive else "bad"
        if role == "extra_masked" and selected > 0:
            if hidden_label == "positive":
                extra_pos_mass += selected
                extra_pos_demos += 1
            else:
                extra_bad_mass += selected
                extra_bad_demos += 1
        weights[demo_id] = {
            "loss_weight": loss_weight,
            "mask": loss_weight,
            "positive_distance": pos_dist,
            "negative_distance": neg_dist,
            "safety_margin": margin,
        }
        finite_margin = margin if role == "extra_masked" else np.asarray([], dtype=np.float32)
        rows.append(
            {
                "demo_id": demo_id,
                "role": role,
                "hidden_label": "labeled_or_anchor" if role == "anchor" else hidden_label,
                "classifier_score": fmt(float(scores.get(demo_id, 1.0 if role == "anchor" else 0.0))),
                "transition_count": length,
                "selected_transition_count": selected,
                "selected_fraction": fmt(selected / max(1, length)),
                "margin_mean": "" if finite_margin.size == 0 else fmt(float(np.mean(finite_margin))),
                "margin_p25": "" if finite_margin.size == 0 else fmt(float(np.quantile(finite_margin, 0.25))),
                "margin_p50": "" if finite_margin.size == 0 else fmt(float(np.quantile(finite_margin, 0.50))),
                "margin_p75": "" if finite_margin.size == 0 else fmt(float(np.quantile(finite_margin, 0.75))),
            }
        )

    summary = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "weighted_diagnostics": str(args.weighted_diagnostics),
        "positive_diagnostics": str(args.positive_diagnostics),
        "score_rankings": str(args.score_rankings),
        "score_threshold": float(args.score_threshold),
        "margin_threshold": float(args.margin_threshold),
        "train_demo_count": len(train_ids),
        "anchor_demo_count": len(anchor_ids),
        "extra_demo_count": len(extra_ids),
        "extra_positive_demo_count": int(extra_pos_demos),
        "extra_bad_demo_count": int(extra_bad_demos),
        "extra_positive_mass": int(extra_pos_mass),
        "extra_bad_mass": int(extra_bad_mass),
        "extra_bad_masked_fraction": extra_bad_mass / max(1, extra_pos_mass + extra_bad_mass),
        "total_selected_mass": int(total_mass),
        "total_transition_count": int(total_transition_count),
        "extra_mass_fraction_total": (extra_pos_mass + extra_bad_mass) / max(1, total_mass),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    weights_hdf5 = args.out_dir / "candidate_c_sequence_mask_weights.hdf5"
    summary_csv = args.out_dir / "candidate_c_sequence_mask_summary.csv"
    recipe_json = args.out_dir / "candidate_c_sequence_mask_recipe.json"
    report_path = args.out_dir / "candidate_c_sequence_mask_preflight_REPORT.md"
    write_weight_hdf5(weights_hdf5, weights, summary)
    write_csv(
        summary_csv,
        rows,
        [
            "demo_id",
            "role",
            "hidden_label",
            "classifier_score",
            "transition_count",
            "selected_transition_count",
            "selected_fraction",
            "margin_mean",
            "margin_p25",
            "margin_p50",
            "margin_p75",
        ],
    )
    recipe_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(
        report_path,
        summary,
        {"weights_hdf5": weights_hdf5, "summary_csv": summary_csv, "recipe_json": recipe_json},
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
