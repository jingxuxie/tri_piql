#!/usr/bin/env python3
"""Prepare Candidate O positive-anchored Lift union training artifacts."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import h5py
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"
SPLIT_PATH = OUT / "splits" / "lift_mg_mg_sparse_split606" / "split_indices.json"
POS_SETUP = OUT / "per_seed" / "lift_mg_mg_sparse_split606_positive_only_nn_policy0" / "setup"
TRIAGE_SETUP = OUT / "per_seed" / "lift_mg_mg_sparse_split606_triage_bc_policy0" / "setup"
ARTIFACT_DIR = OUT / "candidate_o_lift606_positive_anchor_union"
FILTER_KEY = "candidate_o_lift606_positive_anchor_union_train"
VALID_FILTER_KEY = "candidate_o_lift606_positive_anchor_union_valid_positive"
EXTRA_TRIAGE_WEIGHT = 0.25


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def write_mask(hdf5_path: Path, key: str, demo_ids: list[str]) -> None:
    encoded = np.asarray([demo_id.encode("utf-8") for demo_id in demo_ids])
    with h5py.File(hdf5_path, "a") as f:
        mask = f.require_group("mask")
        if key in mask:
            old = [item.decode("utf-8") for item in mask[key][:]]
            if old == demo_ids:
                return
            del mask[key]
        max_len = max(len(demo_id) for demo_id in demo_ids)
        mask.create_dataset(key, data=encoded.astype(f"S{max_len}"))


def write_weights(
    *,
    hdf5_path: Path,
    out_path: Path,
    train_demo_ids: list[str],
    full_weight_ids: set[str],
    triage_extra_ids: set[str],
) -> dict[str, object]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "candidate": "candidate_o_lift606_positive_anchor_union",
        "source_split": str(SPLIT_PATH.relative_to(ROOT)),
        "hdf5_path": str(hdf5_path),
        "filter_key": FILTER_KEY,
        "valid_filter_key": VALID_FILTER_KEY,
        "weight_rule": {
            "labeled_positive_and_positive_nn_selected": 1.0,
            "triage_only_extra_selected": EXTRA_TRIAGE_WEIGHT,
        },
        "train_demo_count": len(train_demo_ids),
        "triage_extra_count": len(triage_extra_ids),
    }
    with h5py.File(hdf5_path, "r") as src, h5py.File(out_path, "w") as dst:
        dst.attrs["metadata_json"] = json.dumps(metadata, sort_keys=True)
        data_group = dst.create_group("data")
        for demo_id in train_demo_ids:
            length = int(src["data"][demo_id]["actions"].shape[0])
            weight = EXTRA_TRIAGE_WEIGHT if demo_id in triage_extra_ids else 1.0
            demo_group = data_group.create_group(demo_id)
            demo_group.create_dataset("loss_weight", data=np.full((length,), weight, dtype=np.float32))
    return metadata


def main() -> None:
    split = read_json(SPLIT_PATH)
    hdf5_path = ROOT / split["hdf5_path"]
    pos_diag = read_json(POS_SETUP / "diagnostics.json")
    triage_diag = read_json(TRIAGE_SETUP / "diagnostics.json")
    pos_config = read_json(POS_SETUP / "config.json")

    labeled_positive = list(split["labeled_positive_ids"])
    pos_selected = set(pos_diag["selected_unlabeled_demos"])
    triage_selected = set(triage_diag["selected_unlabeled_demos"])
    union_selected = sorted(pos_selected | triage_selected, key=demo_sort_key)
    train_demo_ids = list(labeled_positive) + union_selected
    full_weight_ids = set(labeled_positive) | pos_selected
    triage_extra_ids = triage_selected - pos_selected

    write_mask(hdf5_path, FILTER_KEY, train_demo_ids)
    write_mask(hdf5_path, VALID_FILTER_KEY, list(split["valid_positive_ids"]))

    weight_path = ARTIFACT_DIR / "candidate_o_loss_weights.hdf5"
    metadata = write_weights(
        hdf5_path=hdf5_path,
        out_path=weight_path,
        train_demo_ids=train_demo_ids,
        full_weight_ids=full_weight_ids,
        triage_extra_ids=triage_extra_ids,
    )

    config = json.loads(json.dumps(pos_config))
    config["experiment"]["name"] = "candidate_o_lift606_positive_anchor_union_seed0"
    config["experiment"]["save"]["every_n_epochs"] = 50
    config["experiment"]["save"]["epochs"] = [100]
    config["train"]["hdf5_filter_key"] = FILTER_KEY
    config["train"]["data"][0]["filter_key"] = FILTER_KEY
    config["train"]["output_dir"] = str((ARTIFACT_DIR / "train").resolve())
    config_path = ARTIFACT_DIR / "config.json"
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    diagnostics = {
        **metadata,
        "config_path": str(config_path.relative_to(ROOT)),
        "weights_path": str(weight_path.relative_to(ROOT)),
        "positive_selected_count": len(pos_selected),
        "triage_selected_count": len(triage_selected),
        "overlap_selected_count": len(pos_selected & triage_selected),
        "positive_only_extra_count": len(pos_selected - triage_selected),
        "triage_only_extra_count": len(triage_extra_ids),
        "train_demo_ids": train_demo_ids,
        "full_weight_demo_ids": sorted(full_weight_ids, key=demo_sort_key),
        "triage_extra_demo_ids": sorted(triage_extra_ids, key=demo_sort_key),
    }
    diagnostics_path = ARTIFACT_DIR / "diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2) + "\n", encoding="utf-8")

    report_path = ARTIFACT_DIR / "candidate_o_lift_anchor_union_preflight_REPORT.md"
    report = [
        "# Candidate O Lift606 Positive-Anchor Union Preflight",
        "",
        "Candidate O is a policy-training change for the Lift branch: keep the",
        "positive-only selected support at full loss weight and add triage-only",
        f"extra demos at loss weight `{EXTRA_TRIAGE_WEIGHT}`.",
        "",
        "## Support",
        "",
        f"- Labeled positives: `{len(labeled_positive)}`.",
        f"- Positive-NN selected unlabeled demos: `{len(pos_selected)}`.",
        f"- Triage selected unlabeled demos: `{len(triage_selected)}`.",
        f"- Overlap selected demos: `{len(pos_selected & triage_selected)}`.",
        f"- Positive-only extra demos: `{len(pos_selected - triage_selected)}`.",
        f"- Triage-only extra demos: `{len(triage_extra_ids)}`.",
        f"- Candidate O train demos: `{len(train_demo_ids)}`.",
        "",
        "## Artifacts",
        "",
        f"- Config: `{config_path.relative_to(ROOT)}`.",
        f"- Loss weights: `{weight_path.relative_to(ROOT)}`.",
        f"- Diagnostics: `{diagnostics_path.relative_to(ROOT)}`.",
        f"- HDF5 train mask: `{FILTER_KEY}`.",
        f"- HDF5 valid-positive mask: `{VALID_FILTER_KEY}`.",
    ]
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    # Preserve a copy of the source config for easier provenance comparison.
    shutil.copyfile(POS_SETUP / "config.json", ARTIFACT_DIR / "source_positive_config.json")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
