from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import summarize_hard_negative_can_action_conflict_audit as can_hn  # noqa: E402


ROOT = Path(".")
BASE_SPLIT = ROOT / "results" / "robomimic_inspection" / "lift_mg_low_dim_sparse" / "split_indices.json"
OUT_DIR = ROOT / "results" / "final_paper" / "ablations"
SPLIT_DIR = OUT_DIR / "lift_hard_negative_action_conflict_splits"

CONSTRUCTION_OUT = OUT_DIR / "lift_hard_negative_action_conflict_construction.csv"
PER_SPLIT_OUT = OUT_DIR / "lift_hard_negative_action_conflict_support_per_split.csv"
SUMMARY_OUT = OUT_DIR / "lift_hard_negative_action_conflict_summary.csv"
REPORT_OUT = OUT_DIR / "lift_hard_negative_action_conflict_REPORT.md"

SPLIT_SEEDS = (101, 202, 303)
SETTING_ID = "lift_hard_negative_action_conflict"
SETTING_LABEL = "Lift hard-negative/action-conflict"


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def retag_row(row: dict[str, object]) -> dict[str, object]:
    row = dict(row)
    row["setting_id"] = SETTING_ID
    row["setting_label"] = SETTING_LABEL
    return row


def construct_lift_split(base_split: dict[str, object], features: can_hn.DemoFeatures, split_seed: int) -> can_hn.ConstructedSplit:
    original_split_dir = can_hn.SPLIT_DIR
    can_hn.SPLIT_DIR = SPLIT_DIR
    try:
        constructed = can_hn.construct_split(base_split, features, split_seed)
    finally:
        can_hn.SPLIT_DIR = original_split_dir

    constructed.split["diagnostic_split_type"] = SETTING_ID
    constructed.split["construction_note"] = (
        "Lift generated hard-negative/action-conflict split. Labeled positives are a compact successful "
        "cluster; hidden positives are successful demos far from that cluster; labeled and unlabeled failures "
        "are ranked by near-positive state distance plus action conflict."
    )
    constructed.split_path.write_text(json.dumps(constructed.split, indent=2) + "\n", encoding="utf-8")
    return constructed


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [retag_row(row) for row in can_hn.aggregate(rows)]


def support_gate(summary_rows: list[dict[str, object]]) -> str:
    baseline = can_hn.row_by_id(summary_rows, "state_action_positive_nn_top40")
    base_recall = float(baseline["hidden_positive_recall"])
    base_bad = float(baseline["hidden_bad_admission"])
    cleared = []
    for row in summary_rows:
        if row["candidate_id"] == baseline["candidate_id"]:
            continue
        recall = float(row["hidden_positive_recall"] or 0.0)
        bad = float(row["hidden_bad_admission"] or 0.0)
        if recall >= base_recall and bad < base_bad:
            cleared.append(str(row["candidate_id"]))
    if cleared:
        return (
            "The Lift support gate is cleared by "
            + ", ".join(cleared)
            + ": these rows match or exceed state-action positive-NN recall while reducing hidden-bad admission."
        )
    return (
        "No tested hidden-label-free rule clears the Lift support gate against state-action positive-NN top40. "
        "Treat this as a construction diagnostic, not an endpoint-training trigger."
    )


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return lines


def report(construction_rows: list[dict[str, object]], summary_rows: list[dict[str, object]]) -> str:
    selected_ids = [
        "state_action_positive_nn_top40",
        "state_positive_nn_top40",
        "bad_aware_proxy_top40",
        "hybrid_pos40_filter_badaware80_refill40",
        "hybrid_rank_fusion_badaware_heavy_top40",
        "hybrid_rank_fusion_equal_top40",
        "all_unlabeled_soft_reference",
    ]
    selected_rows = [can_hn.row_by_id(summary_rows, candidate_id) for candidate_id in selected_ids]
    baseline = can_hn.row_by_id(summary_rows, "state_action_positive_nn_top40")
    bad_aware = can_hn.row_by_id(summary_rows, "bad_aware_proxy_top40")
    lines = [
        "# Lift Hard-Negative Action-Conflict Support Audit",
        "",
        "This is the first non-Can generated support diagnostic for the paper plan's Priority C1.",
        "It reuses the Lift MG low-dimensional sparse dataset and constructs compact-positive, hard-negative splits without policy training.",
        "Hidden success/failure labels are used only for construction and support audits, not for any deployable selection rule.",
        "",
        "## Construction Check",
        "",
        *markdown_table(
            construction_rows,
            [
                "split_seed",
                "hidden_positive_state_gap_mean",
                "unlabeled_bad_state_distance_mean",
                "unlabeled_bad_action_conflict_mean",
                "unlabeled_bad_hard_score_mean",
            ],
        ),
        "",
        "## Support Gate",
        "",
        "Rows aggregate over the three generated Lift split seeds.",
        "",
        "| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |",
        "|---|---|---:|---:|---:|---:|",
    ]
    lines.extend(can_hn.format_row(row) for row in selected_rows)
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                f"- State-action positive-NN top40 selects `{baseline['hidden_positive_selected']}/"
                f"{baseline['total_hidden_positive']}` hidden positives and `{baseline['hidden_bad_selected']}/"
                f"{baseline['total_hidden_bad']}` hidden bad demos."
            ),
            (
                f"- Bad-aware proxy top40 selects `{bad_aware['hidden_positive_selected']}/"
                f"{bad_aware['total_hidden_positive']}` hidden positives and `{bad_aware['hidden_bad_selected']}/"
                f"{bad_aware['total_hidden_bad']}` hidden bad demos."
            ),
            f"- {support_gate(summary_rows)}",
            "- This is support-only evidence. It is useful C1 evidence that the generated bad-label mechanism transfers beyond Can, but it is not a policy endpoint claim.",
            "",
            "## Outputs",
            "",
            f"- `{CONSTRUCTION_OUT}`",
            f"- `{PER_SPLIT_OUT}`",
            f"- `{SUMMARY_OUT}`",
            f"- `{REPORT_OUT}`",
            f"- `{SPLIT_DIR}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    base_split = can_hn.read_json(BASE_SPLIT)
    hdf5_path = str(base_split["hdf5_path"])
    obs_keys = can_hn.dataset_obs_keys(hdf5_path)
    all_demo_ids = can_hn.sorted_demos([*base_split["all_positive_ids"], *base_split["all_negative_ids"]])
    features = can_hn.load_demo_features(hdf5_path, all_demo_ids, obs_keys)

    construction_rows: list[dict[str, object]] = []
    per_split_rows: list[dict[str, object]] = []
    for split_seed in SPLIT_SEEDS:
        constructed = construct_lift_split(base_split, features, split_seed)
        split = constructed.split
        labels = {
            demo_id: "positive" if demo_id in set(split["all_positive_ids"]) else "bad"
            for demo_id in split["unlabeled_ids"]
        }
        candidates, _scores = can_hn.candidate_sets(split, obs_keys, features)
        construction_rows.append(constructed.construction_stats)
        for candidate_id, demo_ids in candidates.items():
            per_split_rows.append(
                retag_row(
                    can_hn.summarize_candidate(
                        split_seed=split_seed,
                        split_path=constructed.split_path,
                        candidate_id=candidate_id,
                        demo_ids=demo_ids,
                        labels=labels,
                        hard_scores=constructed.hard_scores,
                    )
                )
            )

    summary_rows = aggregate(per_split_rows)
    construction_fields = [
        "split_seed",
        "split_path",
        "positive_anchor_demo",
        "labeled_positive_count",
        "labeled_negative_count",
        "unlabeled_positive_count",
        "unlabeled_negative_count",
        "valid_positive_count",
        "valid_negative_count",
        "hidden_positive_state_gap_mean",
        "hidden_positive_state_gap_min",
        "unlabeled_bad_state_distance_mean",
        "valid_bad_state_distance_mean",
        "unlabeled_bad_action_conflict_mean",
        "valid_bad_action_conflict_mean",
        "unlabeled_bad_hard_score_mean",
        "valid_bad_hard_score_mean",
    ]
    support_fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "split_seed",
        "candidate_id",
        "candidate_family",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "selected_bad_hard_score_mean",
        "selected_demo_ids",
        "source",
    ]
    summary_fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "candidate_id",
        "candidate_family",
        "split_count",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
    ]
    write_csv(CONSTRUCTION_OUT, construction_rows, construction_fields)
    write_csv(PER_SPLIT_OUT, per_split_rows, support_fields)
    write_csv(SUMMARY_OUT, summary_rows, summary_fields)
    REPORT_OUT.write_text(report(construction_rows, summary_rows), encoding="utf-8")
    print(f"wrote {CONSTRUCTION_OUT}")
    print(f"wrote {PER_SPLIT_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
