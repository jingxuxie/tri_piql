#!/usr/bin/env python3
"""Summarize the positive-anchored IQL-AWBC Can404 endpoint screen."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(".")
DEFAULT_EVAL_METRICS = (
    ROOT / "results" / "sota_candidate" / "anchored_iql_awbc_can404_w10_e20_eval20" / "metrics.csv"
)
DEFAULT_PREFLIGHT = ROOT / "results" / "sota_candidate" / "iql_awbc_can404_preflight" / "diagnostics.json"
DEFAULT_IQL_SUMMARY = ROOT / "results" / "sota_candidate" / "iql_awbc_can404_screen_summary.csv"
DEFAULT_CANDIDATE_V_METRICS = (
    ROOT / "results" / "candidate_breakthrough" / "candidate_v_anchor_logprob_can404_w10_e20_eval20" / "metrics.csv"
)
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-metrics", type=Path, default=DEFAULT_EVAL_METRICS)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--iql-summary", type=Path, default=DEFAULT_IQL_SUMMARY)
    parser.add_argument("--candidate-v-metrics", type=Path, default=DEFAULT_CANDIDATE_V_METRICS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
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


def row_by_method(rows: list[dict[str, str]], method_id: str) -> dict[str, str]:
    for row in rows:
        if row["method_id"] == method_id:
            return row
    raise KeyError(method_id)


def success_count_from_rate(row: dict[str, str]) -> int:
    return int(round(float(row["success_rate"]) * int(row["eval_episodes"])))


def copy_reference(
    rows: list[dict[str, object]],
    row: dict[str, str],
    kind: str,
    positive_success: int,
) -> None:
    success_count = int(row["success_count"])
    rows.append(
        {
            "method_id": row["method_id"],
            "label": row["label"],
            "kind": kind,
            "train_epochs": row["train_epochs"],
            "eval_episodes": row["eval_episodes"],
            "success_count": success_count,
            "success_rate": row["success_rate"],
            "avg_len": row["avg_len"],
            "delta_vs_positive": success_count - positive_success,
        }
    )


def main() -> None:
    args = parse_args()
    eval_rows = read_csv(args.eval_metrics)
    iql_rows = read_csv(args.iql_summary)
    candidate_v_rows = read_csv(args.candidate_v_metrics)
    diagnostics = json.loads(args.preflight.read_text(encoding="utf-8"))
    selected_summary = diagnostics["metadata"]["selected_summary"]
    q_diag = diagnostics["metadata"]["q_diagnostics"]

    positive = row_by_method(iql_rows, "positive_only_nn_top40")
    weighted = row_by_method(iql_rows, "weighted_bc_full_pool")
    candidate_c = row_by_method(iql_rows, "candidate_c_sequence_mask_e200")
    cau = row_by_method(iql_rows, "cau_action_conflict_b005_m05_e200")
    demo_pref = row_by_method(iql_rows, "demo_pref_refcenter_w1_e20")
    unanchored_e100 = row_by_method(iql_rows, "iql_awbc_norm_topq_e100")
    positive_success = int(positive["success_count"])

    rows: list[dict[str, object]] = []
    copy_reference(rows, positive, "baseline", positive_success)
    copy_reference(rows, weighted, "baseline", positive_success)
    copy_reference(rows, candidate_c, "previous_candidate", positive_success)
    copy_reference(rows, cau, "previous_sota_candidate", positive_success)
    copy_reference(rows, demo_pref, "previous_sota_candidate", positive_success)
    copy_reference(rows, unanchored_e100, "previous_iql_candidate", positive_success)

    for row in candidate_v_rows:
        success_count = success_count_from_rate(row)
        epoch = row["checkpoint_name"].removeprefix("model_epoch_")
        rows.append(
            {
                "method_id": f"candidate_v_output_anchor_e{epoch}",
                "label": f"Candidate V output-anchor e{epoch}",
                "kind": "previous_anchor_candidate",
                "train_epochs": epoch,
                "eval_episodes": row["eval_episodes"],
                "success_count": success_count,
                "success_rate": f"{float(row['success_rate']):.3f}",
                "avg_len": f"{float(row['avg_len']):.1f}",
                "delta_vs_positive": success_count - positive_success,
            }
        )

    for row in eval_rows:
        success_count = success_count_from_rate(row)
        epoch = row["checkpoint_name"].removeprefix("model_epoch_")
        rows.append(
            {
                "method_id": f"anchored_iql_awbc_w10_e{epoch}",
                "label": f"Anchored IQL-AWBC w10 e{epoch}",
                "kind": "sota_candidate_6_anchor_followup",
                "train_epochs": epoch,
                "eval_episodes": row["eval_episodes"],
                "success_count": success_count,
                "success_rate": f"{float(row['success_rate']):.3f}",
                "avg_len": f"{float(row['avg_len']):.1f}",
                "delta_vs_positive": success_count - positive_success,
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = args.out_dir / "anchored_iql_awbc_can404_screen_summary.csv"
    report_path = args.out_dir / "anchored_iql_awbc_can404_screen_REPORT.md"
    fieldnames = [
        "method_id",
        "label",
        "kind",
        "train_epochs",
        "eval_episodes",
        "success_count",
        "success_rate",
        "avg_len",
        "delta_vs_positive",
    ]
    write_csv(summary_csv, rows, fieldnames)

    anchor_rows = [row for row in rows if row["kind"] == "sota_candidate_6_anchor_followup"]
    best_anchor = max(anchor_rows, key=lambda row: int(row["success_count"]))
    best_v = max(
        [row for row in rows if row["kind"] == "previous_anchor_candidate"],
        key=lambda row: int(row["success_count"]),
    )
    decision = "reject"
    lines = [
        "# Anchored IQL-AWBC Can404 Screen",
        "",
        "This is a follow-up to the SOTA Candidate 6 IQL-AWBC failure.",
        "It initializes from the positive-only checkpoint and applies output-level anchor-logprob weight `10.0` while training on the selected IQL-AWBC norm-topq transition weights.",
        "",
        "## Setup",
        "",
        f"- Q/V advantage means, pos/neg/unlabeled: `{q_diag['pos_adv_mean']:.3f}` / `{q_diag['neg_adv_mean']:.3f}` / `{q_diag['unl_adv_mean']:.3f}`.",
        f"- IQL-AWBC selected hidden-bad mass fraction: `{selected_summary['hidden_bad_weighted_mass_fraction']:.3f}`.",
        "- Fine-tune: positive-only initialization, anchor-logprob weight `10.0`, epochs `5/10/15/20`.",
        "",
        "## Result",
        "",
        "| method | successes | success rate | avg len | delta vs positive |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {label} | {success_count}/{eval_episodes} | {success_rate} | {avg_len} | {delta_vs_positive} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Best anchored IQL-AWBC checkpoint: `{best_anchor['success_count']}/20`.",
            f"- Positive-only NN matched screen: `{positive_success}/20`.",
            f"- Prior Candidate V output-anchor best on this screen: `{best_v['success_count']}/20`.",
            f"- Decision: `{decision}` for this anchored IQL-AWBC recipe.",
            "",
            "Read: output anchoring repairs the total IQL-AWBC collapse but the IQL-derived weights still underperform both the positive-only anchor and the earlier non-IQL output-anchor recipe. Do not scale this combination unchanged.",
            "",
            "## Artifacts",
            "",
            f"- Eval report: `{args.eval_metrics.parent / 'REPORT.md'}`.",
            f"- Summary CSV: `{summary_csv}`.",
            "- Train directory: `results/sota_candidate/anchored_iql_awbc_can404_w10_e20_train/anchored_iql_awbc_can404_w10_e20_seed0/20260626142620/`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = {
        "positive_only_nn_top40": 17,
        "weighted_bc_full_pool": 13,
        "candidate_c_sequence_mask_e200": 16,
        "cau_action_conflict_b005_m05_e200": 16,
        "demo_pref_refcenter_w1_e20": 16,
        "iql_awbc_norm_topq_e100": 4,
        "candidate_v_output_anchor_e10": 18,
        "anchored_iql_awbc_w10_e5": 10,
        "anchored_iql_awbc_w10_e10": 13,
        "anchored_iql_awbc_w10_e15": 11,
        "anchored_iql_awbc_w10_e20": 12,
    }
    actual = {row["method_id"]: int(row["success_count"]) for row in rows}
    for key, value in expected.items():
        if actual.get(key) != value:
            raise AssertionError(f"{key}: expected {value}, got {actual.get(key)}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
