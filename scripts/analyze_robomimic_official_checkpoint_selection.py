from __future__ import annotations

import argparse
import csv
import glob
import json
import re
import sys
from pathlib import Path

import h5py
import numpy as np
import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[1]
ROBOMIMIC_ROOT = ROOT / "external" / "robomimic"
for path in (ROOT, ROBOMIMIC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from robomimic.algo import algo_factory  # noqa: E402
import robomimic.utils.file_utils as FileUtils  # noqa: E402
import robomimic.utils.obs_utils as ObsUtils  # noqa: E402
import robomimic.utils.train_utils as TrainUtils  # noqa: E402


def parse_key_value(value: str, *, arg_name: str) -> tuple[str, str]:
    if "=" not in value:
        raise ValueError(f"{arg_name} entries must be NAME=VALUE, got {value!r}")
    name, rhs = value.split("=", 1)
    name = name.strip()
    rhs = rhs.strip()
    if not name or not rhs:
        raise ValueError(f"{arg_name} entries must be NAME=VALUE, got {value!r}")
    return name, rhs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-path", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Run name and checkpoint glob as NAME=GLOB.",
    )
    parser.add_argument(
        "--eval-metrics",
        action="append",
        default=[],
        help="Optional rollout metrics CSV as NAME=PATH. NAME should match a --run name.",
    )
    parser.add_argument(
        "--score-filters",
        nargs="+",
        default=["train_support", "valid_all", "valid_positive", "labeled_positive"],
        choices=["train_support", "valid_all", "valid_positive", "valid_negative", "labeled_positive", "labeled_negative"],
    )
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--max-batches", type=int, default=120)
    parser.add_argument("--max-train-batches", type=int, default=50)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--mask-prefix", default="tri_lift_mg_ckptsel")
    return parser.parse_args()


def write_mask(hdf5_path: str, key: str, demo_ids: list[str]) -> None:
    encoded = np.asarray([demo_id.encode("utf-8") for demo_id in demo_ids])
    with h5py.File(hdf5_path, "a") as f:
        if "mask" not in f:
            f.create_group("mask")
        if key in f["mask"]:
            del f["mask"][key]
        f["mask"].create_dataset(key, data=encoded)


def checkpoint_epoch(path: Path) -> int:
    match = re.search(r"model_epoch_(\d+)", path.stem)
    if not match:
        return 10**9
    return int(match.group(1))


def load_eval_metrics(path: Path) -> dict[int, dict[str, float]]:
    rows: dict[int, dict[str, float]] = {}
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epoch = checkpoint_epoch(Path(row["checkpoint_name"]))
            rows[epoch] = {
                "rollout_success": float(row["success_rate"]),
                "rollout_return": float(row["avg_return"]),
                "rollout_len": float(row["avg_len"]),
            }
    return rows


def make_common_masks(split: dict, prefix: str) -> dict[str, str]:
    hdf5_path = split["hdf5_path"]
    specs = {
        "valid_all": list(split["valid_ids"]),
        "valid_positive": list(split["valid_positive_ids"]),
        "valid_negative": list(split["valid_negative_ids"]),
        "labeled_positive": list(split["labeled_positive_ids"]),
        "labeled_negative": list(split["labeled_negative_ids"]),
    }
    keys = {}
    for name, demo_ids in specs.items():
        key = f"{prefix}_{name}"
        write_mask(hdf5_path, key, demo_ids)
        keys[name] = key
    return keys


def score_checkpoint(
    *,
    checkpoint: Path,
    filter_key: str,
    batch_size: int,
    max_batches: int,
    device: torch.device,
) -> dict[str, float | int]:
    ckpt_dict = FileUtils.load_dict_from_checkpoint(str(checkpoint))
    config, _ = FileUtils.config_from_checkpoint(ckpt_dict=ckpt_dict)
    shape_meta = ckpt_dict["shape_metadata"]
    with config.values_unlocked():
        config.train.cuda = device.type == "cuda"
        config.train.batch_size = batch_size
        config.train.num_data_workers = 0
        config.train.hdf5_filter_key = filter_key
        for dataset_cfg in config.train.data:
            dataset_cfg["filter_key"] = filter_key

    ObsUtils.initialize_obs_utils_with_config(config)
    model = algo_factory(
        algo_name=config.algo_name,
        config=config,
        obs_key_shapes=shape_meta["all_shapes"],
        ac_dim=shape_meta["ac_dim"],
        device=device,
    )
    model.deserialize(ckpt_dict["model"])
    model.set_eval()

    dataset = TrainUtils.dataset_factory(config, obs_keys=shape_meta["all_obs_keys"], filter_by_attribute=filter_key)
    loader = DataLoader(
        dataset=dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        drop_last=False,
    )
    num_batches = min(len(loader), max_batches)
    if num_batches <= 0:
        raise ValueError(f"filter {filter_key!r} produced no batches for {checkpoint}")
    with torch.no_grad():
        log = TrainUtils.run_epoch(
            model=model,
            data_loader=loader,
            epoch=0,
            validate=True,
            num_steps=num_batches,
            obs_normalization_stats=None,
        )
    return {
        "num_sequences": int(len(dataset)),
        "num_batches_scored": int(num_batches),
        "loss": float(log["Loss"]),
        "log_likelihood": float(log["Log_Likelihood"]),
    }


def markdown_table(rows: list[dict[str, str | int | float]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        rendered = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                rendered.append(f"{value:.3f}")
            else:
                rendered.append(str(value))
        lines.append("| " + " | ".join(rendered) + " |")
    return "\n".join(lines)


def mean(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(np.mean(values))


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    common_filter_keys = make_common_masks(split, args.mask_prefix)

    run_specs = [parse_key_value(value, arg_name="--run") for value in args.run]
    eval_metrics = {
        name: load_eval_metrics(Path(path))
        for name, path in [parse_key_value(value, arg_name="--eval-metrics") for value in args.eval_metrics]
    }

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("requested CUDA scoring but torch.cuda.is_available() is false")
    device = torch.device(args.device)

    rows: list[dict[str, str | int | float]] = []
    for run_name, checkpoint_pattern in run_specs:
        checkpoints = sorted((Path(path) for path in glob.glob(checkpoint_pattern)), key=checkpoint_epoch)
        if not checkpoints:
            raise FileNotFoundError(f"no checkpoints matched {checkpoint_pattern!r} for run {run_name}")
        first_ckpt = FileUtils.load_dict_from_checkpoint(str(checkpoints[0]))
        first_config, _ = FileUtils.config_from_checkpoint(ckpt_dict=first_ckpt)
        train_filter_key = first_config.train.hdf5_filter_key
        filter_keys = {
            "train_support": train_filter_key,
            **common_filter_keys,
        }
        for checkpoint in checkpoints:
            epoch = checkpoint_epoch(checkpoint)
            rollout = eval_metrics.get(run_name, {}).get(epoch, {})
            for filter_name in args.score_filters:
                max_batches = args.max_train_batches if filter_name == "train_support" else args.max_batches
                metrics = score_checkpoint(
                    checkpoint=checkpoint,
                    filter_key=filter_keys[filter_name],
                    batch_size=args.batch_size,
                    max_batches=max_batches,
                    device=device,
                )
                rows.append(
                    {
                        "run": run_name,
                        "checkpoint_epoch": int(epoch),
                        "checkpoint": str(checkpoint),
                        "filter_name": filter_name,
                        "filter_key": filter_keys[filter_name],
                        **metrics,
                        "rollout_success": rollout.get("rollout_success", float("nan")),
                        "rollout_return": rollout.get("rollout_return", float("nan")),
                        "rollout_len": rollout.get("rollout_len", float("nan")),
                    }
                )

    csv_path = args.out_dir / "checkpoint_scores.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    selected_rows = []
    for run_name, _pattern in run_specs:
        run_rows = [row for row in rows if row["run"] == run_name]
        rollout_rows = {
            int(row["checkpoint_epoch"]): float(row["rollout_success"])
            for row in run_rows
            if not np.isnan(float(row["rollout_success"]))
        }
        rollout_best_epoch = ""
        rollout_best_success = float("nan")
        if rollout_rows:
            rollout_best_epoch = max(rollout_rows, key=lambda epoch: rollout_rows[epoch])
            rollout_best_success = rollout_rows[rollout_best_epoch]
        for filter_name in args.score_filters:
            candidates = [row for row in run_rows if row["filter_name"] == filter_name]
            selected = max(candidates, key=lambda row: float(row["log_likelihood"]))
            selected_rows.append(
                {
                    "run": run_name,
                    "filter": filter_name,
                    "selected_epoch": int(selected["checkpoint_epoch"]),
                    "selected_log_likelihood": float(selected["log_likelihood"]),
                    "selected_loss": float(selected["loss"]),
                    "selected_rollout_success": float(selected["rollout_success"]),
                    "rollout_best_epoch": rollout_best_epoch,
                    "rollout_best_success": rollout_best_success,
                }
            )

    selected_csv = args.out_dir / "selected_checkpoints.csv"
    with selected_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = list(selected_rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selected_rows)

    methods = sorted({str(row["run"]).rsplit("_seed", 1)[0] for row in selected_rows})
    aggregate_rows = []
    for filter_name in args.score_filters:
        for method in methods:
            method_rows = [
                row
                for row in selected_rows
                if row["filter"] == filter_name and str(row["run"]).rsplit("_seed", 1)[0] == method
            ]
            aggregate_rows.append(
                {
                    "filter": filter_name,
                    "method": method,
                    "mean_selected_success": mean([float(row["selected_rollout_success"]) for row in method_rows]),
                    "mean_rollout_best_success": mean([float(row["rollout_best_success"]) for row in method_rows]),
                }
            )

    report = [
        "# Robomimic Official Checkpoint Selection Analysis",
        "",
        f"Split path: `{args.split_path}`.",
        f"Device: `{device}`.",
        f"Batch size: `{args.batch_size}`.",
        f"Max validation batches: `{args.max_batches}`.",
        f"Max train-support batches: `{args.max_train_batches}`.",
        "",
        "Offline score is Robomimic validation log-likelihood; higher is better.",
        "",
        "## Selected Checkpoints",
        "",
        markdown_table(
            selected_rows,
            [
                "run",
                "filter",
                "selected_epoch",
                "selected_log_likelihood",
                "selected_rollout_success",
                "rollout_best_epoch",
                "rollout_best_success",
            ],
        ),
        "",
        "## Aggregate Selection Outcome",
        "",
        markdown_table(
            aggregate_rows,
            [
                "filter",
                "method",
                "mean_selected_success",
                "mean_rollout_best_success",
            ],
        ),
        "",
        "## Files",
        "",
        f"- `checkpoint_scores.csv`: per-checkpoint offline scores and rollout metrics.",
        f"- `selected_checkpoints.csv`: best checkpoint per offline filter.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
