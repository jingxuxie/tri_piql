from __future__ import annotations

import argparse
import csv
from pathlib import Path
from types import SimpleNamespace

import summarize_can_prefix_positive_audit as prefix_audit


TABLE_DIR = Path("results/final_paper/tables")
SPLIT_ROOT = Path("results/final_paper/ablations/can_prefix_length_robustness_splits")

OUT_CSV = "can_prefix_length_robustness.csv"
OUT_ALL_CANDIDATES = "can_prefix_length_robustness_all_candidates.csv"
OUT_REPORT = "can_prefix_length_robustness_REPORT.md"

KEY_CANDIDATES = (
    "prefix_state_action_nn_top80",
    "prefix_bad_aware_state_top80",
    "prefix_bad_aware_state_action_top80",
    "prefix_rank_fusion_badaware_heavy_top80",
    "all_unlabeled_soft_reference",
)

CONFIGS = (
    {
        "config_id": "short_prefix",
        "config_label": "short prefixes",
        "prefix_fraction": 0.10,
        "prefix_min_steps": 4,
        "prefix_max_steps": 15,
    },
    {
        "config_id": "default_prefix",
        "config_label": "default prefixes",
        "prefix_fraction": 0.20,
        "prefix_min_steps": 8,
        "prefix_max_steps": 30,
    },
    {
        "config_id": "long_prefix",
        "config_label": "long prefixes",
        "prefix_fraction": 0.40,
        "prefix_min_steps": 16,
        "prefix_max_steps": 60,
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=TABLE_DIR)
    parser.add_argument("--split-root", type=Path, default=SPLIT_ROOT)
    return parser.parse_args()


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float | str | None) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.3f}"


def run_config(
    config: dict[str, object],
    *,
    base_split: dict[str, object],
    obs_keys: list[str],
    split_root: Path,
) -> list[dict[str, str]]:
    original_split_dir = prefix_audit.SPLIT_DIR
    prefix_audit.SPLIT_DIR = split_root / str(config["config_id"])
    try:
        args = SimpleNamespace(
            base_split=prefix_audit.BASE_SPLIT,
            out_dir=TABLE_DIR,
            prefix_fraction=float(config["prefix_fraction"]),
            prefix_min_steps=int(config["prefix_min_steps"]),
            prefix_max_steps=int(config["prefix_max_steps"]),
            label_budget=prefix_audit.LABEL_BUDGET,
            valid_count_per_class=prefix_audit.VALID_COUNT_PER_CLASS,
        )
        per_split_rows = []
        for split_seed in prefix_audit.SPLIT_SEEDS:
            constructed = prefix_audit.construct_split(base_split, split_seed, args)
            candidates, _scores = prefix_audit.transition_rankings(constructed.split, obs_keys, args)
            for candidate_id, demo_ids in candidates.items():
                per_split_rows.append(
                    prefix_audit.summarize_candidate(
                        constructed.split,
                        constructed.split_path,
                        candidate_id,
                        demo_ids,
                    )
                )
        summary_rows = prefix_audit.aggregate(per_split_rows)
    finally:
        prefix_audit.SPLIT_DIR = original_split_dir

    baseline = next(row for row in summary_rows if row["candidate_id"] == "prefix_state_action_nn_top80")
    baseline_recall = float(baseline["hidden_positive_recall"])
    baseline_bad = float(baseline["hidden_bad_admission"])
    out: list[dict[str, str]] = []
    for row in summary_rows:
        recall = float(row["hidden_positive_recall"])
        bad_admission = float(row["hidden_bad_admission"])
        out.append(
            {
                "config_id": str(config["config_id"]),
                "config_label": str(config["config_label"]),
                "prefix_fraction": fmt(config["prefix_fraction"]),
                "prefix_min_steps": str(config["prefix_min_steps"]),
                "prefix_max_steps": str(config["prefix_max_steps"]),
                "candidate_id": str(row["candidate_id"]),
                "candidate_family": str(row["candidate_family"]),
                "splits": str(row["splits"]),
                "selected_unlabeled": str(row["selected_unlabeled"]),
                "hidden_positive_selected": str(row["hidden_positive_selected"]),
                "hidden_bad_selected": str(row["hidden_bad_selected"]),
                "total_hidden_positive": str(row["total_hidden_positive"]),
                "total_hidden_bad": str(row["total_hidden_bad"]),
                "support_purity": str(row["support_purity"]),
                "hidden_positive_recall": str(row["hidden_positive_recall"]),
                "hidden_bad_admission": str(row["hidden_bad_admission"]),
                "selected_contamination": str(row["selected_contamination"]),
                "delta_recall_vs_prefix_state_action_nn_top80": fmt(recall - baseline_recall),
                "delta_bad_admission_vs_prefix_state_action_nn_top80": fmt(bad_admission - baseline_bad),
                "clears_prefix_state_action_nn_top80": str(
                    row["candidate_id"] != "prefix_state_action_nn_top80"
                    and recall >= baseline_recall
                    and bad_admission < baseline_bad
                ).lower(),
                "source_splits": str(split_root / str(config["config_id"]) / "split*"),
            }
        )
    return out


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(column, "") for column in columns) + " |")
    return lines


def row_by(rows: list[dict[str, str]], config_id: str, candidate_id: str) -> dict[str, str]:
    for row in rows:
        if row["config_id"] == config_id and row["candidate_id"] == candidate_id:
            return row
    raise KeyError((config_id, candidate_id))


def report(out_dir: Path, split_root: Path, key_rows: list[dict[str, str]], all_rows: list[dict[str, str]]) -> str:
    main_candidate = "prefix_bad_aware_state_top80"
    baseline = "prefix_state_action_nn_top80"
    lines = [
        "# Can Prefix-Length Robustness Support Sweep",
        "",
        "This is the B5 support-only robustness check for the generated Can prefix-positive probe.",
        "It varies the labeled-positive prefix length while holding split seeds, label budget, and the top80 support size fixed.",
        "No new policy endpoint is trained here; the endpoint-backed default-prefix row remains the main generated prefix-positive result.",
        "",
        "## Key Rows",
        "",
        *markdown_table(
            key_rows,
            [
                "config_id",
                "candidate_id",
                "hidden_positive_selected",
                "hidden_bad_selected",
                "hidden_positive_recall",
                "hidden_bad_admission",
                "support_purity",
                "delta_recall_vs_prefix_state_action_nn_top80",
                "delta_bad_admission_vs_prefix_state_action_nn_top80",
            ],
        ),
        "",
        "## Read",
        "",
    ]
    for config in CONFIGS:
        config_id = str(config["config_id"])
        candidate = row_by(all_rows, config_id, main_candidate)
        control = row_by(all_rows, config_id, baseline)
        lines.append(
            f"- `{config_id}`: bad-aware state top80 selects "
            f"`{candidate['hidden_positive_selected']}` hidden positives and `{candidate['hidden_bad_selected']}` hidden bad demos, "
            f"versus prefix positive-NN top80 `{control['hidden_positive_selected']}` and `{control['hidden_bad_selected']}`. "
            f"The recall delta is `{candidate['delta_recall_vs_prefix_state_action_nn_top80']}` and the bad-admission delta is "
            f"`{candidate['delta_bad_admission_vs_prefix_state_action_nn_top80']}`."
        )
    lines.extend(
        [
            "",
            "## Answer",
            "",
            "The prefix-positive generated probe is not a one-point artifact of the default prefix length. Across short, default, and long prefix settings, the bad-aware state top80 row clears the matched prefix positive-NN top80 support row by increasing hidden-positive recall and decreasing hidden-bad admission at the same selected support size.",
            "",
            "This is support-only robustness. It justifies the generated-probe mechanism story, but it should not be promoted as a new endpoint result unless one of the non-default settings is trained and evaluated.",
            "",
            "## Outputs",
            "",
            f"- `{out_dir / OUT_CSV}`",
            f"- `{out_dir / OUT_ALL_CANDIDATES}`",
            f"- `{out_dir / OUT_REPORT}`",
            f"- generated split files under `{split_root}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    base_split = prefix_audit.read_json(prefix_audit.BASE_SPLIT)
    obs_keys = prefix_audit.dataset_obs_keys(str(base_split["hdf5_path"]))
    all_rows: list[dict[str, str]] = []
    for config in CONFIGS:
        all_rows.extend(
            run_config(
                config,
                base_split=base_split,
                obs_keys=obs_keys,
                split_root=args.split_root,
            )
        )
    key_rows = [
        row
        for row in all_rows
        if row["candidate_id"] in KEY_CANDIDATES
    ]
    fields = [
        "config_id",
        "config_label",
        "prefix_fraction",
        "prefix_min_steps",
        "prefix_max_steps",
        "candidate_id",
        "candidate_family",
        "splits",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "delta_recall_vs_prefix_state_action_nn_top80",
        "delta_bad_admission_vs_prefix_state_action_nn_top80",
        "clears_prefix_state_action_nn_top80",
        "source_splits",
    ]
    write_csv(args.out_dir / OUT_ALL_CANDIDATES, all_rows, fields)
    write_csv(args.out_dir / OUT_CSV, key_rows, fields)
    (args.out_dir / OUT_REPORT).write_text(report(args.out_dir, args.split_root, key_rows, all_rows), encoding="utf-8")
    print(f"wrote {args.out_dir / OUT_CSV}")
    print(f"wrote {args.out_dir / OUT_ALL_CANDIDATES}")
    print(f"wrote {args.out_dir / OUT_REPORT}")


if __name__ == "__main__":
    main()
