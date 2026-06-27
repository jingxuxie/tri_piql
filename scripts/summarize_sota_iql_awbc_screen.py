#!/usr/bin/env python3
"""Summarize the IQL-AWBC Can404 endpoint screen."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(".")
DEFAULT_EVAL_METRICS = ROOT / "results" / "sota_candidate" / "iql_awbc_can404_norm_topq_e100_eval20" / "metrics.csv"
DEFAULT_PREFLIGHT = ROOT / "results" / "sota_candidate" / "iql_awbc_can404_preflight" / "diagnostics.json"
DEFAULT_DEMO_PREF_SUMMARY = ROOT / "results" / "sota_candidate" / "demo_preference_can404_screen_summary.csv"
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-metrics", type=Path, default=DEFAULT_EVAL_METRICS)
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--demo-pref-summary", type=Path, default=DEFAULT_DEMO_PREF_SUMMARY)
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
    ref_rows = read_csv(args.demo_pref_summary)
    diagnostics = json.loads(args.preflight.read_text(encoding="utf-8"))
    selected_summary = diagnostics["metadata"]["selected_summary"]
    q_diag = diagnostics["metadata"]["q_diagnostics"]
    cls = diagnostics["metadata"]["classifier_metrics"]
    sm_ref = diagnostics["sm_rwbc_reference_summary"]

    positive = row_by_method(ref_rows, "positive_only_nn_top40")
    weighted = row_by_method(ref_rows, "weighted_bc_full_pool")
    candidate_c = row_by_method(ref_rows, "candidate_c_sequence_mask_e200")
    cau = row_by_method(ref_rows, "cau_action_conflict_b005_m05_e200")
    demo_pref = row_by_method(ref_rows, "demo_pref_refcenter_w1_e20")
    positive_success = int(positive["success_count"])

    rows: list[dict[str, object]] = []
    copy_reference(rows, positive, "baseline", positive_success)
    copy_reference(rows, weighted, "baseline", positive_success)
    copy_reference(rows, candidate_c, "previous_candidate", positive_success)
    copy_reference(rows, cau, "previous_sota_candidate", positive_success)
    copy_reference(rows, demo_pref, "previous_sota_candidate", positive_success)

    for eval_row in eval_rows:
        success_count = success_count_from_rate(eval_row)
        epoch = eval_row["checkpoint_name"].removeprefix("model_epoch_")
        rows.append(
            {
                "method_id": f"iql_awbc_norm_topq_e{epoch}",
                "label": f"IQL-AWBC norm-topq e{epoch}",
                "kind": "sota_candidate_6",
                "train_epochs": epoch,
                "eval_episodes": eval_row["eval_episodes"],
                "success_count": success_count,
                "success_rate": f"{float(eval_row['success_rate']):.3f}",
                "avg_len": f"{float(eval_row['avg_len']):.1f}",
                "delta_vs_positive": success_count - positive_success,
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = args.out_dir / "iql_awbc_can404_screen_summary.csv"
    report_path = args.out_dir / "iql_awbc_can404_screen_REPORT.md"
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

    candidate_rows = [row for row in rows if row["kind"] == "sota_candidate_6"]
    best_candidate = max(candidate_rows, key=lambda row: int(row["success_count"]))
    decision = "reject"
    lines = [
        "# IQL-AWBC Can404 Screen",
        "",
        "This is the first SOTA Candidate 6 endpoint screen from `triage_bc_sota_candidate_plan.md`.",
        "It uses a classifier-reward Q/V preflight to build advantage weights, then trains the official BC-RNN-GMM extractor on the selected norm-topq weights.",
        "",
        "## Offline Preflight Signal",
        "",
        f"- State-action classifier labeled accuracy: `{cls['labeled_accuracy']:.3f}`.",
        f"- Learned advantage means, pos/neg/unlabeled: `{q_diag['pos_adv_mean']:.3f}` / `{q_diag['neg_adv_mean']:.3f}` / `{q_diag['unl_adv_mean']:.3f}`.",
        f"- Selected hidden-bad weighted mass fraction: `{selected_summary['hidden_bad_weighted_mass_fraction']:.3f}`.",
        f"- Rejected SM-RWBC hidden-bad weighted mass fraction: `{sm_ref['hidden_bad_weighted_mass_fraction']:.3f}`.",
        f"- Selected hidden-positive mass: `{selected_summary['hidden_positive_mass']:.1f}`.",
        "",
        "## Endpoint Result",
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
            f"- Best IQL-AWBC checkpoint: `{best_candidate['success_count']}/20`.",
            f"- Positive-only NN matched screen: `{positive_success}/20`.",
            f"- Candidate C / CAU / Demo-DPO matched screen: `{candidate_c['success_count']}/20`, `{cau['success_count']}/20`, `{demo_pref['success_count']}/20`.",
            f"- Decision: `{decision}` for this classifier-reward IQL-AWBC norm-topq recipe.",
            "",
            "Read: the Q/V preflight separates positive and negative advantages and improves the hidden-bad mass diagnostic, but the endpoint policy collapses. Do not scale this recipe unchanged.",
            "",
            "## Artifacts",
            "",
            f"- Preflight report: `{args.preflight.parent / 'iql_awbc_preflight_REPORT.md'}`.",
            f"- Eval report: `{args.eval_metrics.parent / 'REPORT.md'}`.",
            f"- Summary CSV: `{summary_csv}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = {
        "positive_only_nn_top40": 17,
        "weighted_bc_full_pool": 13,
        "candidate_c_sequence_mask_e200": 16,
        "cau_action_conflict_b005_m05_e200": 16,
        "demo_pref_refcenter_w1_e20": 16,
        "iql_awbc_norm_topq_e50": 0,
        "iql_awbc_norm_topq_e100": 4,
    }
    actual = {row["method_id"]: int(row["success_count"]) for row in rows}
    for key, value in expected.items():
        if actual.get(key) != value:
            raise AssertionError(f"{key}: expected {value}, got {actual.get(key)}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
