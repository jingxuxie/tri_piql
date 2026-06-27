from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(".")
DEFAULT_SPLIT_PATH = ROOT / "results" / "final_paper_v02" / "splits" / "can_paired_pos40_bad80_split404" / "split_indices.json"
DEFAULT_POSITIVE_DIAGNOSTICS = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
    / "setup"
    / "diagnostics.json"
)
DEFAULT_POSITIVE_SUPPORT = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
    / "support_audit.csv"
)
DEFAULT_SCORE_DIR = ROOT / "results" / "final_paper_v02" / "score_diagnostics" / "can_paired_pos40_bad80_split404_policy0"
DEFAULT_RISK_SUMMARY = (
    ROOT
    / "results"
    / "sota_candidate"
    / "sm_rwbc_can404_m003_lam2_combined_preflight"
    / "sm_rwbc_selected_demo_summary.csv"
)
DEFAULT_BASE_CONFIG = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
    / "setup"
    / "config.json"
)
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate" / "safeexpand_can404_demo103_preflight"
DEFAULT_TRAIN_OUTPUT_DIR = ROOT / "results" / "sota_candidate" / "safeexpand_can404_demo103_e200_train"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--positive-diagnostics", type=Path, default=DEFAULT_POSITIVE_DIAGNOSTICS)
    parser.add_argument("--positive-support", type=Path, default=DEFAULT_POSITIVE_SUPPORT)
    parser.add_argument("--score-dir", type=Path, default=DEFAULT_SCORE_DIR)
    parser.add_argument("--risk-summary", type=Path, default=DEFAULT_RISK_SUMMARY)
    parser.add_argument("--base-config", type=Path, default=DEFAULT_BASE_CONFIG)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--train-output-dir", type=Path, default=DEFAULT_TRAIN_OUTPUT_DIR)
    parser.add_argument("--experiment-name", default="safeexpand_can404_demo103_e200_seed0")
    parser.add_argument("--mask-prefix", default="sota_safeexpand_can404_demo103")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--score-threshold-name", default="pos_min")
    parser.add_argument("--risk-cap-name", default="anchor_q75")
    parser.add_argument("--num-epochs", type=int, default=200)
    parser.add_argument("--epoch-steps", type=int, default=100)
    parser.add_argument("--save-every-epochs", type=int, default=100)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def quantile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("empty quantile input")
    arr = np.asarray(values, dtype=np.float64)
    return float(np.quantile(arr, q))


def write_mask(hdf5_path: Path, key: str, demo_ids: list[str]) -> None:
    encoded = np.asarray([demo_id.encode("utf-8") for demo_id in demo_ids])
    with h5py.File(hdf5_path, "a") as f:
        if "mask" not in f:
            f.create_group("mask")
        if key in f["mask"]:
            del f["mask"][key]
        f["mask"].create_dataset(key, data=encoded)


def demo_index(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def fmt(value: float) -> str:
    return f"{value:.6f}"


def main() -> None:
    args = parse_args()
    split = read_json(args.split_path)
    positive_diagnostics = read_json(args.positive_diagnostics)
    score_summary = read_csv(args.score_dir / "score_summary.csv")[0]
    score_rows = read_csv(args.score_dir / "demo_rankings.csv")
    risk_rows = read_csv(args.risk_summary)
    support_rows = read_csv(args.positive_support)

    all_positive = set(split["all_positive_ids"])
    labeled_positive = list(split["labeled_positive_ids"])
    anchor_demo_ids = [row["demo_id"] for row in support_rows]
    anchor_set = set(anchor_demo_ids)
    score_by_demo = {row["demo_id"]: float(row["score"]) for row in score_rows}
    risk_by_demo = {
        row["demo_id"]: float(row["combined_risk_mean"])
        for row in risk_rows
        if row["role"] == "unlabeled_weighted" and row["combined_risk_mean"] != ""
    }

    anchor_risk_values = [risk_by_demo[demo_id] for demo_id in anchor_demo_ids if demo_id in risk_by_demo]
    score_thresholds = {
        "pos_min": float(score_summary["labeled_positive_min"]),
        "pos_p10": float(score_summary["labeled_positive_p10"]),
        "mid_minpos_maxneg": 0.5
        * (float(score_summary["labeled_positive_min"]) + float(score_summary["labeled_negative_max"])),
        "score_0p60": 0.60,
        "score_0p50": 0.50,
    }
    risk_caps = {
        "anchor_q50": quantile(anchor_risk_values, 0.50),
        "anchor_q75": quantile(anchor_risk_values, 0.75),
        "anchor_q90": quantile(anchor_risk_values, 0.90),
        "none": float("inf"),
    }
    if args.score_threshold_name not in score_thresholds:
        raise KeyError(args.score_threshold_name)
    if args.risk_cap_name not in risk_caps:
        raise KeyError(args.risk_cap_name)

    grid_rows: list[dict[str, object]] = []
    selected_additions: list[str] = []
    for score_name, score_threshold in score_thresholds.items():
        for risk_name, risk_cap in risk_caps.items():
            additions = [
                row["demo_id"]
                for row in score_rows
                if row["demo_id"] not in anchor_set
                and row["demo_id"] in risk_by_demo
                and float(row["score"]) >= score_threshold
                and risk_by_demo[row["demo_id"]] <= risk_cap
            ]
            hidden_positive = sum(1 for demo_id in additions if demo_id in all_positive)
            hidden_bad = len(additions) - hidden_positive
            grid_rows.append(
                {
                    "score_threshold_name": score_name,
                    "score_threshold": fmt(score_threshold),
                    "risk_cap_name": risk_name,
                    "risk_cap": "inf" if math.isinf(risk_cap) else fmt(risk_cap),
                    "added_demo_count": len(additions),
                    "added_hidden_positive": hidden_positive,
                    "added_hidden_bad": hidden_bad,
                    "added_purity": fmt(hidden_positive / max(1, len(additions))),
                    "added_demo_ids": " ".join(additions),
                }
            )
            if score_name == args.score_threshold_name and risk_name == args.risk_cap_name:
                selected_additions = additions

    train_demo_ids = list(dict.fromkeys([*labeled_positive, *anchor_demo_ids, *selected_additions]))
    selected_unlabeled = [*anchor_demo_ids, *selected_additions]
    selected_hidden_positive = sum(1 for demo_id in selected_unlabeled if demo_id in all_positive)
    selected_hidden_bad = len(selected_unlabeled) - selected_hidden_positive
    added_hidden_positive = sum(1 for demo_id in selected_additions if demo_id in all_positive)
    added_hidden_bad = len(selected_additions) - added_hidden_positive

    hdf5_path = Path(split["hdf5_path"])
    train_filter_key = f"{args.mask_prefix}_seed{args.seed}_train"
    valid_filter_key = f"{args.mask_prefix}_seed{args.seed}_valid_positive"
    write_mask(hdf5_path, train_filter_key, train_demo_ids)
    write_mask(hdf5_path, valid_filter_key, list(split["valid_positive_ids"]))

    config = read_json(args.base_config)
    config["experiment"]["name"] = args.experiment_name
    config["experiment"]["epoch_every_n_steps"] = args.epoch_steps
    config["experiment"]["save"]["every_n_epochs"] = args.save_every_epochs
    config["experiment"]["save"]["epochs"] = [args.num_epochs]
    config["train"]["data"][0]["filter_key"] = train_filter_key
    config["train"]["output_dir"] = str(args.train_output_dir.resolve())
    config["train"]["hdf5_filter_key"] = train_filter_key
    config["train"]["num_epochs"] = args.num_epochs
    config["train"]["seed"] = args.seed

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.train_output_dir.mkdir(parents=True, exist_ok=True)
    config_path = args.out_dir / "config.json"
    write_json(config_path, config)
    write_csv(
        args.out_dir / "safeexpand_grid_summary.csv",
        grid_rows,
        [
            "score_threshold_name",
            "score_threshold",
            "risk_cap_name",
            "risk_cap",
            "added_demo_count",
            "added_hidden_positive",
            "added_hidden_bad",
            "added_purity",
            "added_demo_ids",
        ],
    )
    support_rows_out = []
    for rank, demo_id in enumerate(selected_unlabeled, start=1):
        source = "positive_nn_anchor" if demo_id in anchor_set else "safeexpand_added"
        support_rows_out.append(
            {
                "rank": rank,
                "demo_id": demo_id,
                "source": source,
                "hidden_label": "positive" if demo_id in all_positive else "bad",
                "classifier_score": "" if demo_id not in score_by_demo else fmt(score_by_demo[demo_id]),
                "combined_risk_mean": "" if demo_id not in risk_by_demo else fmt(risk_by_demo[demo_id]),
            }
        )
    write_csv(
        args.out_dir / "safeexpand_support_audit.csv",
        support_rows_out,
        ["rank", "demo_id", "source", "hidden_label", "classifier_score", "combined_risk_mean"],
    )
    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": split["hdf5_path"],
        "base_positive_diagnostics": str(args.positive_diagnostics),
        "base_config": str(args.base_config),
        "score_dir": str(args.score_dir),
        "risk_summary": str(args.risk_summary),
        "score_threshold_name": args.score_threshold_name,
        "score_threshold": score_thresholds[args.score_threshold_name],
        "risk_cap_name": args.risk_cap_name,
        "risk_cap": risk_caps[args.risk_cap_name],
        "anchor_unlabeled_count": len(anchor_demo_ids),
        "anchor_hidden_positive": sum(1 for demo_id in anchor_demo_ids if demo_id in all_positive),
        "anchor_hidden_bad": sum(1 for demo_id in anchor_demo_ids if demo_id not in all_positive),
        "anchor_risk_q75": risk_caps["anchor_q75"],
        "anchor_risk_q90": risk_caps["anchor_q90"],
        "added_demo_ids": selected_additions,
        "added_hidden_positive": added_hidden_positive,
        "added_hidden_bad": added_hidden_bad,
        "selected_unlabeled_count": len(selected_unlabeled),
        "selected_hidden_positive": selected_hidden_positive,
        "selected_hidden_bad": selected_hidden_bad,
        "selected_unlabeled_purity": selected_hidden_positive / max(1, len(selected_unlabeled)),
        "train_demo_count": len(train_demo_ids),
        "train_demo_ids": train_demo_ids,
        "train_filter_key": train_filter_key,
        "valid_filter_key": valid_filter_key,
        "config_path": str(config_path),
        "train_output_dir": str(args.train_output_dir),
        "train_command": f"conda run -n tri-piql python -m robomimic.scripts.train --config {config_path}",
        "positive_only_train_demo_count": positive_diagnostics.get("train_demo_count"),
    }
    write_json(args.out_dir / "diagnostics.json", diagnostics)

    lines = [
        "# SafeExpand-BC Can404 Preflight",
        "",
        "This preflight tests Candidate 4 from `triage_bc_sota_candidate_plan.md`.",
        "It starts from the positive-only NN top40 support and only adds demos that pass a calibrated classifier certificate and an anchor-risk cap.",
        "",
        "## Selected Recipe",
        "",
        f"- Score threshold: `{args.score_threshold_name}` = `{score_thresholds[args.score_threshold_name]:.6f}`.",
        f"- Risk cap: `{args.risk_cap_name}` = `{risk_caps[args.risk_cap_name]:.6f}`.",
        f"- Added demos: `{', '.join(selected_additions) if selected_additions else 'none'}`.",
        f"- Added hidden-positive / hidden-bad diagnostic: `{added_hidden_positive}` / `{added_hidden_bad}`.",
        f"- Final selected unlabeled support: `{selected_hidden_positive}` hidden-positive, `{selected_hidden_bad}` hidden-bad out of `{len(selected_unlabeled)}`.",
        f"- Positive-only anchor support: `{diagnostics['anchor_hidden_positive']}` hidden-positive, `{diagnostics['anchor_hidden_bad']}` hidden-bad out of `{len(anchor_demo_ids)}`.",
        "",
        "## Read",
        "",
        "Relaxing the classifier certificate admits hidden-bad demos immediately on this split.",
        "The safe recipe is therefore a one-demo anchor-preserving expansion, not a broad support rescue.",
        "",
        "## Outputs",
        "",
        f"- Config: `{config_path}`.",
        f"- Diagnostics: `{args.out_dir / 'diagnostics.json'}`.",
        f"- Support audit: `{args.out_dir / 'safeexpand_support_audit.csv'}`.",
        f"- Grid summary: `{args.out_dir / 'safeexpand_grid_summary.csv'}`.",
    ]
    (args.out_dir / "safeexpand_preflight_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'safeexpand_preflight_REPORT.md'}")
    print(f"train filter {train_filter_key}: {len(train_demo_ids)} demos")


if __name__ == "__main__":
    main()
