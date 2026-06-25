from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import h5py
import numpy as np


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    family: str
    train_demo_ids: tuple[str, ...]
    metrics_path: Path | None
    episode_metrics_path: Path | None
    source_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/final_paper/splits/can_paired_pos40_bad80_split11/split_indices.json"),
    )
    parser.add_argument(
        "--out-prefix",
        type=Path,
        default=Path("results/final_paper/tables/v02_policy_coverage_diagnostic"),
    )
    parser.add_argument(
        "--per-seed-root",
        type=Path,
        default=Path("results/final_paper/per_seed"),
    )
    parser.add_argument(
        "--risk-endpoint-root",
        type=Path,
        default=Path("results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/split11"),
    )
    parser.add_argument(
        "--feature-kind",
        choices=["initial_state", "initial_obs"],
        default="initial_state",
        help="Feature used for nearest-neighbor coverage. initial_state matches the evaluator reset state.",
    )
    return parser.parse_args()


def repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (ROOT / path).resolve()


def rel_path(path: Path | None) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def decode_demo_ids(raw: Iterable[object]) -> list[str]:
    out = []
    for item in raw:
        if isinstance(item, bytes):
            out.append(item.decode("utf-8"))
        else:
            out.append(str(item))
    return out


def method_from_per_seed_dir(path: Path) -> str:
    name = path.name
    match = re.match(r"can_paired_pos40_bad80_split\d+_(.+)_policy\d+$", name)
    if match:
        return match.group(1)
    return name


def family_from_method(method_id: str) -> str:
    if method_id in {"bc_all_mixed", "all_train_positive_oracle"}:
        return "oracle_or_control"
    if method_id == "weighted_bc":
        return "weighted"
    if method_id in {"triage_bc"}:
        return "triage_v01"
    if method_id.startswith("positive") or "positive_nn" in method_id:
        return "positive_only"
    if "risk" in method_id or "bad_neighbor" in method_id:
        return "action_risk"
    return "other"


def train_ids_from_hdf5_mask(hdf5_path: Path, filter_key: str) -> list[str]:
    with h5py.File(hdf5_path, "r") as f:
        return decode_demo_ids(f["mask"][filter_key][()])


def train_ids_from_config(config_path: Path, hdf5_path: Path) -> list[str]:
    config = read_json(config_path)
    filter_key = config["train"]["hdf5_filter_key"]
    return train_ids_from_hdf5_mask(hdf5_path, filter_key)


def discover_per_seed_specs(args: argparse.Namespace, split_path: Path, hdf5_path: Path) -> list[MethodSpec]:
    specs: list[MethodSpec] = []
    for diagnostics_path in sorted(args.per_seed_root.glob("can_paired_pos40_bad80_split*_policy0/setup/diagnostics.json")):
        diagnostics = read_json(diagnostics_path)
        if repo_path(Path(diagnostics["split_path"])) != repo_path(split_path):
            continue
        method_dir = diagnostics_path.parents[1]
        method_id = method_from_per_seed_dir(method_dir)
        train_ids = diagnostics.get("train_demo_ids") or train_ids_from_hdf5_mask(
            hdf5_path, diagnostics["train_filter_key"]
        )
        eval_dir = method_dir / "eval"
        specs.append(
            MethodSpec(
                method_id=method_id,
                family=family_from_method(method_id),
                train_demo_ids=tuple(train_ids),
                metrics_path=eval_dir / "metrics.csv",
                episode_metrics_path=eval_dir / "episode_metrics.csv",
                source_path=diagnostics_path,
            )
        )
    return specs


def discover_risk_specs(args: argparse.Namespace, split_path: Path, hdf5_path: Path) -> list[MethodSpec]:
    specs: list[MethodSpec] = []
    if not args.risk_endpoint_root.exists():
        return specs
    for diagnostics_path in sorted(args.risk_endpoint_root.glob("*/setup/diagnostics.json")):
        diagnostics = read_json(diagnostics_path)
        if repo_path(Path(diagnostics["split_path"])) != repo_path(split_path):
            continue
        method_id = diagnostics["candidate_id"]
        train_ids = diagnostics.get("train_demo_ids")
        if not train_ids:
            train_ids = train_ids_from_config(diagnostics_path.with_name("config.json"), hdf5_path)
        candidate_dir = diagnostics_path.parents[1]
        specs.append(
            MethodSpec(
                method_id=method_id,
                family=family_from_method(method_id),
                train_demo_ids=tuple(train_ids),
                metrics_path=candidate_dir / "eval" / "metrics.csv",
                episode_metrics_path=candidate_dir / "eval" / "episode_metrics.csv",
                source_path=diagnostics_path,
            )
        )
    return specs


def load_features(hdf5_path: Path, demo_ids: list[str], feature_kind: str) -> dict[str, np.ndarray]:
    features: dict[str, np.ndarray] = {}
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in demo_ids:
            group = f["data"][demo_id]
            if feature_kind == "initial_state":
                feature = np.asarray(group["states"][0], dtype=np.float64).reshape(-1)
            else:
                obs_group = group["obs"]
                parts = [
                    np.asarray(obs_group[key][0], dtype=np.float64).reshape(-1)
                    for key in sorted(obs_group.keys())
                ]
                feature = np.concatenate(parts)
            features[demo_id] = feature
    return features


def obs_matrix(group) -> np.ndarray:
    obs_group = group["obs"]
    parts = [
        np.asarray(obs_group[key], dtype=np.float64).reshape((obs_group[key].shape[0], -1))
        for key in sorted(obs_group.keys())
    ]
    return np.concatenate(parts, axis=1)


def load_transition_features(hdf5_path: Path, demo_ids: list[str]) -> dict[str, np.ndarray]:
    features: dict[str, np.ndarray] = {}
    with h5py.File(hdf5_path, "r") as f:
        for demo_id in demo_ids:
            group = f["data"][demo_id]
            obs = obs_matrix(group)
            actions = np.asarray(group["actions"], dtype=np.float64).reshape((obs.shape[0], -1))
            features[demo_id] = np.concatenate([obs, actions], axis=1)
    return features


def normalize_features(features: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    demo_ids = sorted(features, key=demo_sort_key)
    matrix = np.stack([features[demo_id] for demo_id in demo_ids], axis=0)
    mean = matrix.mean(axis=0, keepdims=True)
    std = matrix.std(axis=0, keepdims=True) + 1.0e-8
    normalized = (matrix - mean) / std
    return {demo_id: normalized[i] for i, demo_id in enumerate(demo_ids)}


def normalize_transition_features(features: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    demo_ids = sorted(features, key=demo_sort_key)
    matrix = np.concatenate([features[demo_id] for demo_id in demo_ids], axis=0)
    mean = matrix.mean(axis=0, keepdims=True)
    std = matrix.std(axis=0, keepdims=True) + 1.0e-8
    return {demo_id: ((features[demo_id] - mean) / std).astype(np.float32) for demo_id in demo_ids}


def nearest(query: np.ndarray, candidate_ids: list[str], features: dict[str, np.ndarray]) -> tuple[str, float]:
    if not candidate_ids:
        return "", math.inf
    matrix = np.stack([features[demo_id] for demo_id in candidate_ids], axis=0)
    distances = np.linalg.norm(matrix - query.reshape(1, -1), axis=1)
    idx = int(np.argmin(distances))
    return candidate_ids[idx], float(distances[idx])


def transition_matrix(demo_ids: list[str], features: dict[str, np.ndarray]) -> np.ndarray | None:
    if not demo_ids:
        return None
    return np.concatenate([features[demo_id] for demo_id in demo_ids], axis=0).astype(np.float32, copy=False)


def mean_nearest_transition_distance(query: np.ndarray, candidates: np.ndarray | None, chunk_size: int = 256) -> float:
    if candidates is None or candidates.shape[0] == 0:
        return math.inf
    mins = []
    candidates_t = candidates.T
    candidate_norms = np.sum(candidates * candidates, axis=1, keepdims=True).T
    for start in range(0, query.shape[0], chunk_size):
        block = query[start : start + chunk_size].astype(np.float32, copy=False)
        block_norms = np.sum(block * block, axis=1, keepdims=True)
        # Squared Euclidean distance via ||x||^2 + ||y||^2 - 2 x.y avoids a
        # large temporary (query, candidate, feature) tensor.
        d2 = block_norms + candidate_norms - 2.0 * block @ candidates_t
        d2 = np.maximum(d2, 0.0)
        mins.append(np.sqrt(np.min(d2, axis=1)))
    return float(np.mean(np.concatenate(mins, axis=0)))


def endpoint_success(metrics_path: Path | None) -> float:
    if metrics_path is None or not metrics_path.exists():
        return math.nan
    rows = read_csv(metrics_path)
    if not rows:
        return math.nan
    return float(rows[-1]["success_rate"])


def per_initial_success(episode_metrics_path: Path | None) -> dict[str, float]:
    if episode_metrics_path is None or not episode_metrics_path.exists():
        return {}
    buckets: dict[str, list[float]] = defaultdict(list)
    for row in read_csv(episode_metrics_path):
        buckets[row["initial_demo_id"]].append(float(row["success"]))
    return {demo_id: float(np.mean(values)) for demo_id, values in buckets.items()}


def fmt(value: float, digits: int = 3) -> str:
    if math.isnan(value):
        return "nan"
    if math.isinf(value):
        return "inf"
    return f"{value:.{digits}f}"


def mean(values: list[float]) -> float:
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return math.nan
    return float(np.mean(finite))


def percentile(values: list[float], q: float) -> float:
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return math.nan
    return float(np.quantile(finite, q))


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys):
        raise ValueError(f"length mismatch: {len(xs)} vs {len(ys)}")
    pairs = [(x, y) for x, y in zip(xs, ys) if math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 2:
        return math.nan
    x_arr = np.asarray([x for x, _ in pairs], dtype=np.float64)
    y_arr = np.asarray([y for _, y in pairs], dtype=np.float64)
    if float(x_arr.std()) == 0.0 or float(y_arr.std()) == 0.0:
        return math.nan
    return float(np.corrcoef(x_arr, y_arr)[0, 1])


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, separator]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    split_path = args.split_path
    split = read_json(split_path)
    hdf5_path = repo_path(Path(split["hdf5_path"]))
    positive_ids = set(split["all_positive_ids"])
    negative_ids = set(split["all_negative_ids"])
    valid_positive_ids = list(split["valid_positive_ids"])
    all_ids = sorted(positive_ids | negative_ids, key=demo_sort_key)

    specs = discover_per_seed_specs(args, split_path, hdf5_path)
    specs.extend(discover_risk_specs(args, split_path, hdf5_path))
    dedup: dict[str, MethodSpec] = {}
    for spec in specs:
        dedup[spec.method_id] = spec
    specs = sorted(dedup.values(), key=lambda spec: spec.method_id)
    if not specs:
        raise ValueError(f"no method specs discovered for {split_path}")

    raw_features = load_features(hdf5_path, all_ids, args.feature_kind)
    features = normalize_features(raw_features)
    transition_features = normalize_transition_features(load_transition_features(hdf5_path, all_ids))

    summary_rows: list[dict[str, object]] = []
    per_initial_rows: list[dict[str, object]] = []

    for spec in specs:
        train_ids = sorted(set(spec.train_demo_ids), key=demo_sort_key)
        train_pos_ids = [demo_id for demo_id in train_ids if demo_id in positive_ids]
        train_bad_ids = [demo_id for demo_id in train_ids if demo_id in negative_ids]
        train_transition_matrix = transition_matrix(train_ids, transition_features)
        train_pos_transition_matrix = transition_matrix(train_pos_ids, transition_features)
        train_bad_transition_matrix = transition_matrix(train_bad_ids, transition_features)
        init_success = per_initial_success(spec.episode_metrics_path)

        any_dists = []
        pos_dists = []
        bad_dists = []
        transition_any_dists = []
        transition_pos_dists = []
        transition_bad_dists = []
        margins = []
        bad_closer = 0
        nearest_bad_any = 0
        success_by_start = []

        for demo_id in valid_positive_ids:
            query = features[demo_id]
            nearest_any, any_dist = nearest(query, train_ids, features)
            nearest_pos, pos_dist = nearest(query, train_pos_ids, features)
            nearest_bad, bad_dist = nearest(query, train_bad_ids, features)
            transition_query = transition_features[demo_id]
            transition_any_dist = mean_nearest_transition_distance(transition_query, train_transition_matrix)
            transition_pos_dist = mean_nearest_transition_distance(transition_query, train_pos_transition_matrix)
            transition_bad_dist = mean_nearest_transition_distance(transition_query, train_bad_transition_matrix)
            margin = bad_dist - pos_dist
            success = init_success.get(demo_id, math.nan)
            any_label = "positive" if nearest_any in positive_ids else "bad" if nearest_any in negative_ids else ""
            any_dists.append(any_dist)
            pos_dists.append(pos_dist)
            bad_dists.append(bad_dist)
            transition_any_dists.append(transition_any_dist)
            transition_pos_dists.append(transition_pos_dist)
            transition_bad_dists.append(transition_bad_dist)
            margins.append(margin)
            bad_closer += int(math.isfinite(bad_dist) and math.isfinite(pos_dist) and bad_dist < pos_dist)
            nearest_bad_any += int(any_label == "bad")
            success_by_start.append(success)
            per_initial_rows.append(
                {
                    "method_id": spec.method_id,
                    "family": spec.family,
                    "valid_initial_demo_id": demo_id,
                    "initial_success_rate": fmt(success),
                    "nearest_any_demo_id": nearest_any,
                    "nearest_any_label": any_label,
                    "nearest_any_distance": fmt(any_dist),
                    "nearest_positive_demo_id": nearest_pos,
                    "nearest_positive_distance": fmt(pos_dist),
                    "nearest_bad_demo_id": nearest_bad,
                    "nearest_bad_distance": fmt(bad_dist),
                    "bad_minus_positive_distance": fmt(margin),
                    "transition_nn_any_mean": fmt(transition_any_dist),
                    "transition_nn_positive_mean": fmt(transition_pos_dist),
                    "transition_nn_bad_mean": fmt(transition_bad_dist),
                }
            )

        endpoint = endpoint_success(spec.metrics_path)
        summary_rows.append(
            {
                "method_id": spec.method_id,
                "family": spec.family,
                "endpoint_success": fmt(endpoint),
                "train_demo_count": len(train_ids),
                "train_positive_count": len(train_pos_ids),
                "train_bad_count": len(train_bad_ids),
                "valid_nn_any_mean": fmt(mean(any_dists)),
                "valid_nn_positive_mean": fmt(mean(pos_dists)),
                "valid_nn_positive_p90": fmt(percentile(pos_dists, 0.90)),
                "valid_nn_positive_max": fmt(max(pos_dists) if pos_dists else math.nan),
                "valid_nn_bad_mean": fmt(mean(bad_dists)),
                "valid_transition_nn_any_mean": fmt(mean(transition_any_dists)),
                "valid_transition_nn_positive_mean": fmt(mean(transition_pos_dists)),
                "valid_transition_nn_positive_p90": fmt(percentile(transition_pos_dists, 0.90)),
                "valid_transition_nn_positive_max": fmt(
                    max(transition_pos_dists) if transition_pos_dists else math.nan
                ),
                "valid_transition_nn_bad_mean": fmt(mean(transition_bad_dists)),
                "valid_bad_closer_count": bad_closer,
                "valid_nearest_any_bad_count": nearest_bad_any,
                "valid_bad_minus_positive_mean": fmt(mean(margins)),
                "per_initial_success_mean": fmt(mean(success_by_start)),
                "success_vs_positive_distance_corr": fmt(pearson(pos_dists, success_by_start)),
                "success_vs_transition_positive_distance_corr": fmt(
                    pearson(transition_pos_dists, success_by_start)
                ),
                "metrics_path": rel_path(spec.metrics_path),
                "episode_metrics_path": rel_path(spec.episode_metrics_path),
                "source_path": rel_path(spec.source_path),
            }
        )

    out_prefix = args.out_prefix
    summary_path = out_prefix.with_suffix(".csv")
    per_initial_path = out_prefix.with_name(out_prefix.name + "_per_initial.csv")
    report_path = out_prefix.with_name(out_prefix.name + "_REPORT.md")
    write_csv(
        summary_path,
        summary_rows,
        fieldnames=[
            "method_id",
            "family",
            "endpoint_success",
            "train_demo_count",
            "train_positive_count",
            "train_bad_count",
            "valid_nn_any_mean",
            "valid_nn_positive_mean",
            "valid_nn_positive_p90",
            "valid_nn_positive_max",
            "valid_nn_bad_mean",
            "valid_transition_nn_any_mean",
            "valid_transition_nn_positive_mean",
            "valid_transition_nn_positive_p90",
            "valid_transition_nn_positive_max",
            "valid_transition_nn_bad_mean",
            "valid_bad_closer_count",
            "valid_nearest_any_bad_count",
            "valid_bad_minus_positive_mean",
            "per_initial_success_mean",
            "success_vs_positive_distance_corr",
            "success_vs_transition_positive_distance_corr",
            "metrics_path",
            "episode_metrics_path",
            "source_path",
        ],
    )
    write_csv(
        per_initial_path,
        per_initial_rows,
        fieldnames=[
            "method_id",
            "family",
            "valid_initial_demo_id",
            "initial_success_rate",
            "nearest_any_demo_id",
            "nearest_any_label",
            "nearest_any_distance",
            "nearest_positive_demo_id",
            "nearest_positive_distance",
            "nearest_bad_demo_id",
            "nearest_bad_distance",
            "bad_minus_positive_distance",
            "transition_nn_any_mean",
            "transition_nn_positive_mean",
            "transition_nn_bad_mean",
        ],
    )

    endpoint_values = [float(row["endpoint_success"]) for row in summary_rows if row["endpoint_success"] != "nan"]
    pos_dist_values = [float(row["valid_nn_positive_mean"]) for row in summary_rows if row["endpoint_success"] != "nan"]
    transition_pos_dist_values = [
        float(row["valid_transition_nn_positive_mean"]) for row in summary_rows if row["endpoint_success"] != "nan"
    ]
    bad_count_values = [float(row["train_bad_count"]) for row in summary_rows if row["endpoint_success"] != "nan"]
    margin_values = [
        float(row["valid_bad_minus_positive_mean"]) for row in summary_rows if row["endpoint_success"] != "nan"
    ]
    corr_rows = [
        {
            "proxy": "valid_nn_positive_mean",
            "correlation_with_endpoint": fmt(pearson(pos_dist_values, endpoint_values)),
        },
        {
            "proxy": "valid_transition_nn_positive_mean",
            "correlation_with_endpoint": fmt(pearson(transition_pos_dist_values, endpoint_values)),
        },
        {
            "proxy": "train_bad_count",
            "correlation_with_endpoint": fmt(pearson(bad_count_values, endpoint_values)),
        },
        {
            "proxy": "valid_bad_minus_positive_mean",
            "correlation_with_endpoint": fmt(pearson(margin_values, endpoint_values)),
        },
    ]
    ranked = sorted(summary_rows, key=lambda row: float(row["endpoint_success"]) if row["endpoint_success"] != "nan" else -1.0, reverse=True)
    compact_rows = [
        {
            "method": row["method_id"],
            "success": row["endpoint_success"],
            "train pos/bad": f"{row['train_positive_count']}/{row['train_bad_count']}",
            "valid pos-NN mean": row["valid_nn_positive_mean"],
            "valid pos-NN max": row["valid_nn_positive_max"],
            "traj pos-NN mean": row["valid_transition_nn_positive_mean"],
            "bad closer": row["valid_bad_closer_count"],
            "bad margin": row["valid_bad_minus_positive_mean"],
        }
        for row in ranked
    ]

    report = [
        "# v0.2 Policy-Coverage Diagnostic",
        "",
        f"Split: `{split_path}`.",
        f"Feature kind: `{args.feature_kind}`.",
        f"Summary CSV: `{summary_path}`.",
        f"Per-initial CSV: `{per_initial_path}`.",
        "",
        "This diagnostic is hidden-label-audit evidence, not a selector freeze. It asks whether",
        "candidate train sets cover the valid-positive reset states used by endpoint evaluation.",
        "Initial distances are nearest-neighbor distances in standardized initial demo state space.",
        "Trajectory distances are mean transition-level nearest-neighbor distances in standardized",
        "low-dimensional observation-action space.",
        "",
        "## Endpoint and Coverage Summary",
        "",
        markdown_table(
            compact_rows,
            [
                "method",
                "success",
                "train pos/bad",
                "valid pos-NN mean",
                "valid pos-NN max",
                "traj pos-NN mean",
                "bad closer",
                "bad margin",
            ],
        ),
        "",
        "## Proxy Correlations",
        "",
        markdown_table(corr_rows, ["proxy", "correlation_with_endpoint"]),
        "",
        "## Immediate Read",
        "",
        "- Treat these correlations as descriptive only; this split has few methods and shared valid starts.",
        "- A useful v0.2 proxy should penalize bad-demo admission while preserving coverage of valid-positive start states and expert transitions.",
        "- If a high-purity candidate loses despite good support labels, inspect the per-initial CSV for uncovered reset states or trajectories.",
    ]
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"wrote {summary_path}")
    print(f"wrote {per_initial_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
