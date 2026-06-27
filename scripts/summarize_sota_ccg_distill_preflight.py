#!/usr/bin/env python3
"""Summarize the CCG-Distill viability preflight from prior Lift screens."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(".")
FRESH_DIR = ROOT / "results" / "candidate_g_fresh_preflight"
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh-dir", type=Path, default=FRESH_DIR)
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


def int_field(row: dict[str, str], key: str) -> int:
    return int(round(float(row[key])))


def find_row(rows: list[dict[str, str]], **matches: str) -> dict[str, str]:
    for row in rows:
        if all(row.get(key) == value for key, value in matches.items()):
            return row
    raise KeyError(matches)


def add_result(
    rows: list[dict[str, object]],
    *,
    evidence_group: str,
    split: str,
    method: str,
    successes: int,
    episodes: int,
    positive_successes: int,
    note: str,
) -> None:
    rows.append(
        {
            "evidence_group": evidence_group,
            "split": split,
            "method": method,
            "successes": successes,
            "episodes": episodes,
            "delta_vs_positive": successes - positive_successes,
            "note": note,
        }
    )


def main() -> None:
    args = parse_args()
    fresh = args.fresh_dir
    out_dir = args.out_dir

    candidate_k = read_csv(fresh / "candidate_k_confidence_router_summary.csv")
    transfer = read_csv(fresh / "candidate_l_lift606_to_707_threshold_transfer.csv")
    leaky_707 = read_csv(fresh / "candidate_l_lift707_fresh_leaky_threshold_audit.csv")
    temporal = read_csv(fresh / "candidate_m_temporal_confidence_router_summary.csv")
    persistent = read_csv(fresh / "candidate_n_persistent_confidence_router_summary.csv")
    candidate_o = read_csv(fresh / "candidate_o_lift_anchor_union_screen_summary.csv")
    candidate_p = read_csv(fresh / "candidate_p_posinit_anchor_union_screen_summary.csv")
    candidate_qr = read_csv(fresh / "candidate_qr_anchor_protection_screen_summary.csv")
    candidate_s = read_csv(fresh / "candidate_s_labeled_initial_risk_summary.csv")

    lift606_positive = int_field(
        find_row(
            candidate_k,
            split="lift606",
            method="positive_only_nn",
            protocol="20 valid-positive starts",
        ),
        "successes",
    )
    lift707_positive = int_field(
        find_row(
            candidate_k,
            split="lift707",
            method="positive_only_nn",
            protocol="20 valid-positive starts",
        ),
        "successes",
    )

    rows: list[dict[str, object]] = []
    for method in ["positive_only_nn", "triage_bc", "weighted_bc", "confidence_router_thr6p27"]:
        row = find_row(
            candidate_k,
            split="lift606",
            method=method,
            protocol="20 valid-positive starts",
        )
        add_result(
            rows,
            evidence_group="live_router",
            split="lift606",
            method=method,
            successes=int_field(row, "successes"),
            episodes=int_field(row, "episodes"),
            positive_successes=lift606_positive,
            note="Candidate K first-step confidence screen.",
        )

    for method in ["positive_only_nn", "triage_bc", "confidence_router_thr6p27"]:
        row = find_row(
            candidate_k,
            split="lift707",
            method=method,
            protocol="20 valid-positive starts",
        )
        add_result(
            rows,
            evidence_group="live_router",
            split="lift707",
            method=method,
            successes=int_field(row, "successes"),
            episodes=int_field(row, "episodes"),
            positive_successes=lift707_positive,
            note="Candidate K fixed threshold transfer.",
        )

    best_transfer_dev_successes = max(int_field(row, "successes") for row in transfer)
    best_transfer_pool = [
        row for row in transfer if int_field(row, "successes") == best_transfer_dev_successes
    ]
    best_transfer = max(best_transfer_pool, key=lambda row: int_field(row, "fresh_successes"))
    add_result(
        rows,
        evidence_group="calibrated_transfer",
        split="lift707",
        method=f"best_lift606_selected_{best_transfer['feature']}",
        successes=int_field(best_transfer, "fresh_successes"),
        episodes=int_field(best_transfer, "fresh_episodes"),
        positive_successes=lift707_positive,
        note="Best Lift606-selected one-feature threshold transferred to Lift707.",
    )

    best_leaky_707 = max(leaky_707, key=lambda row: int_field(row, "successes"))
    add_result(
        rows,
        evidence_group="leaky_upper_bound",
        split="lift707",
        method=f"best_lift707_leaky_{best_leaky_707['feature']}",
        successes=int_field(best_leaky_707, "successes"),
        episodes=int_field(best_leaky_707, "episodes"),
        positive_successes=lift707_positive,
        note="Diagnostic only: threshold selected on the same Lift707 starts.",
    )

    for row in temporal:
        add_result(
            rows,
            evidence_group="temporal_router",
            split="lift606",
            method=row["method"],
            successes=int_field(row, "successes"),
            episodes=int_field(row, "episodes"),
            positive_successes=lift606_positive,
            note="Per-step confidence gate.",
        )

    for row in persistent:
        add_result(
            rows,
            evidence_group="persistent_router",
            split="lift606",
            method=row["method"],
            successes=int_field(row, "successes"),
            episodes=int_field(row, "episodes"),
            positive_successes=lift606_positive,
            note="Temporal gate with hysteresis.",
        )

    training_rows = []
    for row in candidate_o:
        if row["method"].startswith("candidate_o"):
            training_rows.append(("anchor_union_from_scratch", row))
    for row in candidate_p:
        if row["method"].startswith("candidate_p"):
            training_rows.append(("positive_initialized_union", row))
    for row in candidate_qr:
        if row["group"].startswith("candidate_"):
            training_rows.append((row["group"], row))
    for group, row in training_rows:
        add_result(
            rows,
            evidence_group="training_side_anchor_union",
            split="lift606",
            method=row["method"],
            successes=int_field(row, "successes"),
            episodes=int_field(row, "episodes"),
            positive_successes=lift606_positive,
            note=f"{group}: closest prior evidence for training a single policy from mixed specialists.",
        )

    for split, positive in [("lift606", lift606_positive), ("lift707", lift707_positive)]:
        primary = find_row(candidate_s, split=split, feature_set="policy", quantile="0.25")
        add_result(
            rows,
            evidence_group="learned_initial_risk_gate",
            split=split,
            method="policy_feature_logistic_q25",
            successes=int_field(primary, "successes"),
            episodes=int_field(primary, "episodes"),
            positive_successes=positive,
            note="Balanced labeled positive/negative initial-state classifier.",
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = out_dir / "ccg_distill_lift_preflight_summary.csv"
    report_path = out_dir / "ccg_distill_lift_preflight_REPORT.md"
    fieldnames = [
        "evidence_group",
        "split",
        "method",
        "successes",
        "episodes",
        "delta_vs_positive",
        "note",
    ]
    write_csv(summary_csv, rows, fieldnames)

    live_606 = find_row(
        candidate_k,
        split="lift606",
        method="confidence_router_thr6p27",
        protocol="20 valid-positive starts",
    )
    live_707 = find_row(
        candidate_k,
        split="lift707",
        method="confidence_router_thr6p27",
        protocol="20 valid-positive starts",
    )
    best_training = max(training_rows, key=lambda item: int_field(item[1], "successes"))[1]
    best_temporal = max(temporal + persistent, key=lambda row: int_field(row, "successes"))

    lines = [
        "# CCG-Distill Lift Preflight",
        "",
        "This is the SOTA Candidate 3 preflight from `triage_bc_sota_candidate_plan.md`.",
        "It asks whether the existing Lift specialist/gate evidence is strong enough to justify a new distillation training run.",
        "",
        "## Decision",
        "",
        "**Status: preflight no-go.** Do not spend a fresh CCG-Distill train/eval cycle until the teacher-selection signal improves.",
        "",
        "The planned go/no-go criterion was to beat positive-only on both Lift606 and Lift707.",
        "Existing evidence does not clear the teacher-quality bar:",
        "",
        f"- Tuned first-step confidence router on Lift606: `{int_field(live_606, 'successes')}/20` versus positive-only `{lift606_positive}/20`.",
        f"- The same fixed router on Lift707: `{int_field(live_707, 'successes')}/20` versus positive-only `{lift707_positive}/20`.",
        f"- Best Lift606-selected threshold transferred to Lift707: `{best_transfer['fresh_successes']}/20`.",
        f"- Even the leaky Lift707 one-feature upper bound reaches only `{best_leaky_707['successes']}/20`.",
        f"- Best direct temporal/persistent confidence router on Lift606: `{best_temporal['successes']}/20`.",
        f"- Best single-policy anchor-union training proxy on Lift606: `{best_training['successes']}/20`.",
        "",
        "## Summary Table",
        "",
        "| evidence | split | method | successes | delta vs positive | note |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {evidence_group} | {split} | {method} | {successes}/{episodes} | {delta_vs_positive} | {note} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Candidate K showed real development-split headroom, so the policy set is not hopeless.",
            "- Candidate L/S show that labeled split calibration and learned initial-risk classification do not recover that headroom on Lift707.",
            "- Candidate M/N show that using the confidence feature per step is too twitchy even with persistence.",
            "- Candidate O/P/Q/R show that naive single-policy training over positive plus triage support damages the positive-only anchor.",
            "- A CCG-Distill implementation would mainly distill a weak/non-transferring gate, so the expected value is lower than moving to a genuinely different objective such as the Offline RL/IQL revisit.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{summary_csv}`.",
            "- Source router reports: `results/candidate_g_fresh_preflight/candidate_k_confidence_router_screen_REPORT.md`, `candidate_l_calibrated_confidence_router_REPORT.md`, `candidate_m_temporal_confidence_router_REPORT.md`, `candidate_n_persistent_confidence_router_REPORT.md`.",
            "- Source training-side reports: `results/candidate_g_fresh_preflight/candidate_o_lift_anchor_union_screen_REPORT.md`, `candidate_p_posinit_anchor_union_screen_REPORT.md`, `candidate_qr_anchor_protection_screen_REPORT.md`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = {
        ("live_router", "lift606", "positive_only_nn"): 14,
        ("live_router", "lift606", "confidence_router_thr6p27"): 18,
        ("live_router", "lift707", "positive_only_nn"): 12,
        ("live_router", "lift707", "confidence_router_thr6p27"): 10,
        ("calibrated_transfer", "lift707", f"best_lift606_selected_{best_transfer['feature']}"): 11,
        ("leaky_upper_bound", "lift707", f"best_lift707_leaky_{best_leaky_707['feature']}"): 13,
        ("temporal_router", "lift606", "temporal_sequence_q25"): 7,
        ("persistent_router", "lift606", "persistent_sequence_q25_k10"): 13,
        ("training_side_anchor_union", "lift606", "candidate_p_epoch20_posinit_finetune"): 11,
        ("learned_initial_risk_gate", "lift606", "policy_feature_logistic_q25"): 12,
        ("learned_initial_risk_gate", "lift707", "policy_feature_logistic_q25"): 12,
    }
    actual = {
        (str(row["evidence_group"]), str(row["split"]), str(row["method"])): int(row["successes"])
        for row in rows
    }
    for key, value in expected.items():
        if actual.get(key) != value:
            raise AssertionError(f"{key}: expected {value}, got {actual.get(key)}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
