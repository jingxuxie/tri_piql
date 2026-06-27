from __future__ import annotations

import argparse
import csv
import json
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
DEFAULT_BASE_CONFIG = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
    / "setup"
    / "config.json"
)
DEFAULT_INIT_CHECKPOINT = (
    ROOT
    / "results"
    / "final_paper_v02"
    / "per_seed"
    / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
    / "train"
    / "can_paired_pos40_bad80_split404_positive_only_nn_policy0_official_bc_rnn"
    / "20260625141435"
    / "models"
    / "model_epoch_200.pth"
)
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate" / "demo_pref_can404_lpos_lneg_preflight"
DEFAULT_TRAIN_OUTPUT_DIR = ROOT / "results" / "sota_candidate" / "demo_pref_can404_lpos_lneg_e20_train"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT_PATH)
    parser.add_argument("--positive-diagnostics", type=Path, default=DEFAULT_POSITIVE_DIAGNOSTICS)
    parser.add_argument("--positive-support", type=Path, default=DEFAULT_POSITIVE_SUPPORT)
    parser.add_argument("--base-config", type=Path, default=DEFAULT_BASE_CONFIG)
    parser.add_argument("--init-checkpoint", type=Path, default=DEFAULT_INIT_CHECKPOINT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--train-output-dir", type=Path, default=DEFAULT_TRAIN_OUTPUT_DIR)
    parser.add_argument("--experiment-name", default="demo_pref_can404_lpos_lneg_e20_seed0")
    parser.add_argument("--mask-prefix", default="sota_demo_pref_can404_lpos_lneg")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--num-epochs", type=int, default=20)
    parser.add_argument("--epoch-steps", type=int, default=100)
    parser.add_argument("--save-every-epochs", type=int, default=5)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_mask(hdf5_path: Path, key: str, demo_ids: list[str]) -> None:
    encoded = np.asarray([demo_id.encode("utf-8") for demo_id in demo_ids])
    with h5py.File(hdf5_path, "a") as f:
        if "mask" not in f:
            f.create_group("mask")
        if key in f["mask"]:
            del f["mask"][key]
        f["mask"].create_dataset(key, data=encoded)


def demo_length(f: h5py.File, demo_id: str) -> int:
    return int(f["data"][demo_id]["actions"].shape[0])


def main() -> None:
    args = parse_args()
    split = read_json(args.split_path)
    positive_diagnostics = read_json(args.positive_diagnostics)
    support_rows = read_csv(args.positive_support)
    base_config = read_json(args.base_config)
    hdf5_path = Path(split["hdf5_path"])
    all_positive = set(split["all_positive_ids"])
    labeled_positive = list(split["labeled_positive_ids"])
    labeled_negative = list(split["labeled_negative_ids"])
    positive_support_unlabeled = [row["demo_id"] for row in support_rows]
    positive_support_train = list(positive_diagnostics["train_demo_ids"])
    train_demo_ids = list(dict.fromkeys([*positive_support_train, *labeled_negative]))

    train_filter_key = f"{args.mask_prefix}_seed{args.seed}_train"
    valid_filter_key = f"{args.mask_prefix}_seed{args.seed}_valid_positive"
    write_mask(hdf5_path, train_filter_key, train_demo_ids)
    write_mask(hdf5_path, valid_filter_key, list(split["valid_positive_ids"]))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.train_output_dir.mkdir(parents=True, exist_ok=True)
    transition_path = args.out_dir / "demo_preference_weights.hdf5"
    rows = []
    with h5py.File(hdf5_path, "r") as data_f, h5py.File(transition_path, "w") as out_f:
        out_f.attrs["metadata_json"] = json.dumps(
            {
                "split_path": str(args.split_path),
                "source": "positive_nn_support_bc_plus_labeled_pos_neg_preference",
                "loss_weight": "1 for positive-NN support demos, 0 for added labeled negatives",
                "sample_weight": "1 for every train demo so preference negatives are sampled",
                "preference_label": "+1 labeled positive, -1 labeled negative, 0 otherwise",
            },
            sort_keys=True,
        )
        data_group = out_f.create_group("data")
        for demo_id in train_demo_ids:
            length = demo_length(data_f, demo_id)
            is_positive_support = demo_id in positive_support_train
            is_labeled_positive = demo_id in labeled_positive
            is_labeled_negative = demo_id in labeled_negative
            loss_weight = np.ones((length,), dtype=np.float32) if is_positive_support else np.zeros((length,), dtype=np.float32)
            sample_weight = np.ones((length,), dtype=np.float32)
            preference_label = np.zeros((length,), dtype=np.float32)
            if is_labeled_positive:
                preference_label[:] = 1.0
            elif is_labeled_negative:
                preference_label[:] = -1.0
            group = data_group.create_group(demo_id)
            group.create_dataset("loss_weight", data=loss_weight)
            group.create_dataset("sample_weight", data=sample_weight)
            group.create_dataset("preference_label", data=preference_label)
            rows.append(
                {
                    "demo_id": demo_id,
                    "role": (
                        "labeled_positive_preference"
                        if is_labeled_positive
                        else "labeled_negative_preference"
                        if is_labeled_negative
                        else "positive_nn_bc_support"
                    ),
                    "hidden_label": "positive" if demo_id in all_positive else "bad",
                    "transition_count": length,
                    "loss_weight_mean": float(loss_weight.mean()),
                    "sample_weight_mean": float(sample_weight.mean()),
                    "preference_label": int(preference_label[0]),
                }
            )

    config = base_config
    config["experiment"]["name"] = args.experiment_name
    config["experiment"]["epoch_every_n_steps"] = args.epoch_steps
    config["experiment"]["save"]["every_n_epochs"] = args.save_every_epochs
    config["experiment"]["save"]["epochs"] = [args.num_epochs]
    config["train"]["data"][0]["filter_key"] = train_filter_key
    config["train"]["output_dir"] = str(args.train_output_dir.resolve())
    config["train"]["hdf5_filter_key"] = train_filter_key
    config["train"]["num_epochs"] = args.num_epochs
    config["train"]["seed"] = args.seed
    config_path = args.out_dir / "config.json"
    write_json(config_path, config)

    write_csv(
        args.out_dir / "demo_preference_support_audit.csv",
        rows,
        [
            "demo_id",
            "role",
            "hidden_label",
            "transition_count",
            "loss_weight_mean",
            "sample_weight_mean",
            "preference_label",
        ],
    )
    labeled_pos_transitions = sum(row["transition_count"] for row in rows if row["role"] == "labeled_positive_preference")
    labeled_neg_transitions = sum(row["transition_count"] for row in rows if row["role"] == "labeled_negative_preference")
    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": str(hdf5_path),
        "positive_diagnostics": str(args.positive_diagnostics),
        "positive_support_unlabeled_count": len(positive_support_unlabeled),
        "positive_support_train_count": len(positive_support_train),
        "labeled_positive_count": len(labeled_positive),
        "labeled_negative_count": len(labeled_negative),
        "train_demo_count": len(train_demo_ids),
        "train_demo_ids": train_demo_ids,
        "labeled_positive_transitions": labeled_pos_transitions,
        "labeled_negative_transitions": labeled_neg_transitions,
        "transition_weights_path": str(transition_path),
        "train_filter_key": train_filter_key,
        "valid_filter_key": valid_filter_key,
        "config_path": str(config_path),
        "init_checkpoint": str(args.init_checkpoint),
        "train_output_dir": str(args.train_output_dir),
    }
    write_json(args.out_dir / "diagnostics.json", diagnostics)

    lines = [
        "# Demo Preference Can404 Preflight",
        "",
        "This preflight tests Candidate 5 from `triage_bc_sota_candidate_plan.md`.",
        "It initializes from the positive-only policy, keeps BC on the positive-NN support, and adds a demo-level preference term over labeled positives versus labeled negatives.",
        "",
        "## Selected Recipe",
        "",
        f"- Positive-NN BC support train demos: `{len(positive_support_train)}`.",
        f"- Added labeled negative preference demos: `{len(labeled_negative)}`.",
        f"- Labeled positive preference demos: `{len(labeled_positive)}`.",
        f"- Train demos in mask: `{len(train_demo_ids)}`.",
        f"- Labeled positive / negative preference transitions: `{labeled_pos_transitions}` / `{labeled_neg_transitions}`.",
        f"- Init checkpoint: `{args.init_checkpoint}`.",
        "",
        "## Training Command Template",
        "",
        "```bash",
        "conda run -n tri-piql python scripts/train_robomimic_official_transition_weighted.py \\",
        f"  --config {config_path} \\",
        f"  --transition-weights {transition_path} \\",
        f"  --init-checkpoint {args.init_checkpoint} \\",
        "  --demo-preference-weight 0.2 \\",
        "  --demo-preference-temperature 1.0 \\",
        "  --demo-preference-margin 1.0 \\",
        "  --anchor-logprob-weight 10.0 \\",
        "  --anchor-logprob-min-weight 0.999 \\",
        "  --num-epochs 20 --epoch-steps 100 --save-every-epochs 5 --device cuda",
        "```",
        "",
        "## Outputs",
        "",
        f"- Config: `{config_path}`.",
        f"- Transition weights: `{transition_path}`.",
        f"- Diagnostics: `{args.out_dir / 'diagnostics.json'}`.",
        f"- Support audit: `{args.out_dir / 'demo_preference_support_audit.csv'}`.",
    ]
    (args.out_dir / "demo_preference_preflight_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'demo_preference_preflight_REPORT.md'}")
    print(f"train filter {train_filter_key}: {len(train_demo_ids)} demos")


if __name__ == "__main__":
    main()
