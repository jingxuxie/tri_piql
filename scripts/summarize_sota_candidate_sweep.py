#!/usr/bin/env python3
"""Aggregate the focused SOTA-candidate sweep into one paper-facing report."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"
SUMMARY_PATHS = {
    "sm_rwbc": DEFAULT_OUT_DIR / "sm_rwbc_can404_screen_summary.csv",
    "cau": DEFAULT_OUT_DIR / "cau_action_conflict_can404_screen_summary.csv",
    "ccg": DEFAULT_OUT_DIR / "ccg_distill_lift_preflight_summary.csv",
    "safeexpand": DEFAULT_OUT_DIR / "safeexpand_can404_screen_summary.csv",
    "demo_pref": DEFAULT_OUT_DIR / "demo_preference_can404_screen_summary.csv",
    "iql": DEFAULT_OUT_DIR / "iql_awbc_can404_screen_summary.csv",
    "anchored_iql": DEFAULT_OUT_DIR / "anchored_iql_awbc_can404_screen_summary.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
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


def ccg_row(
    rows: list[dict[str, str]],
    *,
    evidence_group: str,
    split: str,
    method: str,
) -> dict[str, str]:
    for row in rows:
        if (
            row["evidence_group"] == evidence_group
            and row["split"] == split
            and row["method"] == method
        ):
            return row
    raise KeyError((evidence_group, split, method))


def best_rows(rows: list[dict[str, str]], kind: str) -> list[dict[str, str]]:
    selected = [row for row in rows if row["kind"] == kind]
    if not selected:
        raise KeyError(kind)
    return selected


def best_success_row(rows: list[dict[str, str]], kind: str) -> dict[str, str]:
    return max(best_rows(rows, kind), key=lambda row: int(row["success_count"]))


def row_by_screen_checkpoint(
    rows: list[dict[str, str]],
    *,
    screen_id: str,
    checkpoint_name: str,
) -> dict[str, str]:
    for row in rows:
        if row["screen_id"] == screen_id and row["checkpoint_name"] == checkpoint_name:
            return row
    raise KeyError((screen_id, checkpoint_name))


def score(successes: int, episodes: int) -> str:
    return f"{successes}/{episodes}"


def selector_mode_total(rows: list[dict[str, str]], mode: str) -> dict[str, int]:
    selected = [
        row
        for row in rows
        if row["selector_mode"] == mode and row["heldout_split"] != "pooled_resubstitution"
    ]
    keys = [
        "test_episodes",
        "test_positive_successes",
        "test_cau_successes",
        "test_routed_successes",
        "test_gains_vs_positive",
        "test_losses_vs_positive",
        "test_opened_episodes",
    ]
    return {key: sum(int(row[key]) for row in selected) for key in keys}


def selector_baseline_total(rows: list[dict[str, str]]) -> dict[str, int]:
    keys = [
        "episodes",
        "positive_successes",
        "cau_successes",
        "oracle_switch_successes",
    ]
    return {key: sum(int(row[key]) for row in rows) for key in keys}


def learned_router_total(rows: list[dict[str, str]], mode: str) -> dict[str, int]:
    selected = [
        row
        for row in rows
        if row["selector_mode"] == mode and row["heldout_split"].isdigit()
    ]
    keys = [
        "test_episodes",
        "test_positive_successes",
        "test_cau_successes",
        "test_oracle_switch_successes",
        "test_routed_successes",
        "test_gains_vs_positive",
        "test_losses_vs_positive",
        "test_opened_episodes",
    ]
    return {key: sum(int(row[key]) for row in selected) for key in keys}


def learned_router_fresh(rows: list[dict[str, str]], mode: str) -> dict[str, str]:
    for row in rows:
        if row["selector_mode"] == mode and row["heldout_split"] == "fresh909":
            return row
    raise KeyError((mode, "fresh909"))


def add_endpoint_candidate(
    out_rows: list[dict[str, object]],
    *,
    candidate_id: str,
    family: str,
    gate: str,
    summary_rows: list[dict[str, str]],
    candidate_kind: str,
    report_path: Path,
    key_readout: str,
    secondary_evidence: str = "",
) -> None:
    candidate = best_success_row(summary_rows, candidate_kind)
    positive = row_by_method(summary_rows, "positive_only_nn_top40")
    positive_success = int(positive["success_count"])
    episodes = int(candidate["eval_episodes"])
    reference_rows = [
        row
        for row in summary_rows
        if row["kind"] in {"baseline", "previous_candidate", "previous_sota_candidate"}
    ]
    best_reference = max(reference_rows, key=lambda row: int(row["success_count"]))
    candidate_success = int(candidate["success_count"])
    out_rows.append(
        {
            "candidate_id": candidate_id,
            "family": family,
            "decision_level": "endpoint_screen",
            "primary_gate": gate,
            "best_candidate_method": candidate["label"],
            "best_candidate_score": score(candidate_success, episodes),
            "positive_score": score(positive_success, int(positive["eval_episodes"])),
            "best_matched_reference": best_reference["label"],
            "best_matched_reference_score": score(
                int(best_reference["success_count"]),
                int(best_reference["eval_episodes"]),
            ),
            "delta_vs_positive": candidate_success - positive_success,
            "status": "reject",
            "key_readout": key_readout,
            "secondary_evidence": secondary_evidence,
            "report_path": str(report_path),
        }
    )


def main() -> None:
    args = parse_args()
    summaries = {name: read_csv(path) for name, path in SUMMARY_PATHS.items()}

    rows: list[dict[str, object]] = []
    add_endpoint_candidate(
        rows,
        candidate_id="1",
        family="Sequence-Masked Risk-Weighted BC",
        gate="Can404 valid-positive starts",
        summary_rows=summaries["sm_rwbc"],
        candidate_kind="sota_candidate_1",
        report_path=DEFAULT_OUT_DIR / "sm_rwbc_can404_screen_REPORT.md",
        key_readout="Transition weights reduced hidden-bad mass, but broad-pool training still lost the positive-only anchor.",
    )
    add_endpoint_candidate(
        rows,
        candidate_id="2",
        family="Contrastive Action-Unlikelihood BC",
        gate="Can404 valid-positive starts",
        summary_rows=summaries["cau"],
        candidate_kind="sota_candidate_2",
        report_path=DEFAULT_OUT_DIR / "cau_action_conflict_can404_screen_REPORT.md",
        key_readout="Action-conflict negatives repaired the worst hinge regression and tied Candidate C, but did not beat positive-only.",
    )

    ccg_rows = summaries["ccg"]
    ccg_transfer = ccg_row(
        ccg_rows,
        evidence_group="live_router",
        split="lift707",
        method="confidence_router_thr6p27",
    )
    ccg_positive = ccg_row(
        ccg_rows,
        evidence_group="live_router",
        split="lift707",
        method="positive_only_nn",
    )
    ccg_dev = ccg_row(
        ccg_rows,
        evidence_group="live_router",
        split="lift606",
        method="confidence_router_thr6p27",
    )
    ccg_dev_positive = ccg_row(
        ccg_rows,
        evidence_group="live_router",
        split="lift606",
        method="positive_only_nn",
    )
    ccg_leaky = ccg_row(
        ccg_rows,
        evidence_group="leaky_upper_bound",
        split="lift707",
        method="best_lift707_leaky_triage_minus_positive_logit_gap",
    )
    rows.append(
        {
            "candidate_id": "3",
            "family": "Conformal Confidence-Gated Specialist Distillation",
            "decision_level": "preflight_transfer_gate",
            "primary_gate": "Lift707 fixed-threshold transfer",
            "best_candidate_method": "confidence_router_thr6p27",
            "best_candidate_score": score(int(ccg_transfer["successes"]), int(ccg_transfer["episodes"])),
            "positive_score": score(int(ccg_positive["successes"]), int(ccg_positive["episodes"])),
            "best_matched_reference": "Positive-only NN",
            "best_matched_reference_score": score(
                int(ccg_positive["successes"]),
                int(ccg_positive["episodes"]),
            ),
            "delta_vs_positive": int(ccg_transfer["successes"]) - int(ccg_positive["successes"]),
            "status": "preflight_no_go",
            "key_readout": "Development-router headroom did not transfer to Lift707, and training-side single-policy proxies damaged the anchor.",
            "secondary_evidence": (
                f"Lift606 dev router {ccg_dev['successes']}/{ccg_dev['episodes']} "
                f"vs positive {ccg_dev_positive['successes']}/{ccg_dev_positive['episodes']}; "
                f"Lift707 leaky diagnostic upper bound {ccg_leaky['successes']}/{ccg_leaky['episodes']}."
            ),
            "report_path": str(DEFAULT_OUT_DIR / "ccg_distill_lift_preflight_REPORT.md"),
        }
    )

    add_endpoint_candidate(
        rows,
        candidate_id="4",
        family="Safe Support Expansion",
        gate="Can404 valid-positive starts",
        summary_rows=summaries["safeexpand"],
        candidate_kind="sota_candidate_4",
        report_path=DEFAULT_OUT_DIR / "safeexpand_can404_screen_REPORT.md",
        key_readout="A one-demo certified expansion improved the support audit slightly but degraded endpoint behavior.",
    )
    demo_rows = summaries["demo_pref"]
    demo_collapse = row_by_method(demo_rows, "demo_pref_refcenter_w1_e10")
    add_endpoint_candidate(
        rows,
        candidate_id="5",
        family="Preference-Style Sequence Objective",
        gate="Can404 valid-positive starts",
        summary_rows=demo_rows,
        candidate_kind="sota_candidate_5",
        report_path=DEFAULT_OUT_DIR / "demo_preference_can404_screen_REPORT.md",
        key_readout="Reference-centered demo preference stayed below positive-only and introduced a severe unstable checkpoint.",
        secondary_evidence=f"Epoch 10 checkpoint collapsed to {demo_collapse['success_count']}/{demo_collapse['eval_episodes']}.",
    )

    anchored_rows = summaries["anchored_iql"]
    unanchored = row_by_method(summaries["iql"], "iql_awbc_norm_topq_e100")
    add_endpoint_candidate(
        rows,
        candidate_id="6",
        family="Classifier-Reward IQL-AWBC",
        gate="Can404 valid-positive starts",
        summary_rows=anchored_rows,
        candidate_kind="sota_candidate_6_anchor_followup",
        report_path=DEFAULT_OUT_DIR / "anchored_iql_awbc_can404_screen_REPORT.md",
        key_readout="Output anchoring repaired total collapse but IQL-derived advantage weights still failed the anchor.",
        secondary_evidence=f"Unanchored IQL-AWBC epoch 100 reached {unanchored['success_count']}/{unanchored['eval_episodes']}.",
    )

    fieldnames = [
        "candidate_id",
        "family",
        "decision_level",
        "primary_gate",
        "best_candidate_method",
        "best_candidate_score",
        "positive_score",
        "best_matched_reference",
        "best_matched_reference_score",
        "delta_vs_positive",
        "status",
        "key_readout",
        "secondary_evidence",
        "report_path",
    ]
    summary_csv = args.out_dir / "sota_candidate_sweep_summary.csv"
    report_path = args.out_dir / "SOTA_CANDIDATE_SWEEP_REPORT.md"
    write_csv(summary_csv, rows, fieldnames)
    fresh_fallback_first20 = row_by_screen_checkpoint(
        read_csv(args.out_dir / "can505_cau_fallback_fresh_validation_summary.csv"),
        screen_id="first20",
        checkpoint_name="model_epoch_200",
    )
    fresh_fallback_eval50 = row_by_screen_checkpoint(
        read_csv(args.out_dir / "can505_cau_fallback_fresh_validation_summary.csv"),
        screen_id="eval50",
        checkpoint_name="model_epoch_200",
    )
    fresh_fallback_303 = row_by_screen_checkpoint(
        read_csv(args.out_dir / "can303_cau_fallback_fresh_validation_summary.csv"),
        screen_id="first20",
        checkpoint_name="model_epoch_200",
    )
    two_feature_gate_101 = row_by_screen_checkpoint(
        read_csv(args.out_dir / "cau_two_feature_gate_fresh_validation_summary.csv"),
        screen_id="eval50",
        checkpoint_name="model_epoch_200",
    )
    two_feature_gate_202 = row_by_screen_checkpoint(
        [
            row
            for row in read_csv(args.out_dir / "cau_two_feature_gate_fresh_validation_summary.csv")
            if row["split"] == "202"
        ],
        screen_id="eval50",
        checkpoint_name="model_epoch_200",
    )
    cau_five_split = {
        row["method_id"]: row
        for row in read_csv(args.out_dir / "cau_action_conflict_can_five_split_endpoint_summary.csv")
    }
    cau_v02_portfolio = read_csv(args.out_dir / "cau_v02_portfolio_preflight_gate_scan.csv")[0]
    cau_v02_fresh606_rows = read_csv(args.out_dir / "cau_v02_fresh606_endpoint_validation_summary.csv")
    cau_gmm_followup_rows = read_csv(args.out_dir / "cau_gmm_router_followup_summary.csv")
    cau_selector_rows = read_csv(args.out_dir / "cau_selector_feature_loo_rows.csv")
    cau_selector_baselines = read_csv(args.out_dir / "cau_selector_feature_split_baselines.csv")
    cau_policy_selector_rows = read_csv(args.out_dir / "cau_policy_feature_selector_loo_rows.csv")
    cau_policy_selector_baselines = read_csv(args.out_dir / "cau_policy_feature_split_baselines.csv")
    cau_policy_fresh909 = {
        row["method_id"]: row
        for row in read_csv(args.out_dir / "cau_policy_feature_fresh909_summary.csv")
    }
    cau_policy_learned_rows = read_csv(args.out_dir / "cau_policy_feature_learned_router_summary.csv")
    cau_sequence_support = {
        row["screen_id"]: row
        for row in read_csv(args.out_dir / "cau_sequence_support_router_summary.csv")
    }

    def fresh606_row(method_id: str, checkpoint_name: str = "model_epoch_200") -> dict[str, str]:
        for row in cau_v02_fresh606_rows:
            if row["method_id"] == method_id and row["checkpoint_name"] == checkpoint_name:
                return row
        raise KeyError((method_id, checkpoint_name))

    fresh606_positive = fresh606_row("positive_only_nn")
    fresh606_cau = fresh606_row("cau_action_conflict")
    fresh606_union = fresh606_row("positive_nn_risk_union_top40")
    fresh606_fusion = fresh606_row("positive_nn_risk_fusion_top40")
    fresh606_expanded = fresh606_row("cau_action_conflict_expanded_mask")

    def followup_row(artifact_id: str) -> dict[str, str]:
        for row in cau_gmm_followup_rows:
            if row["artifact_id"] == artifact_id:
                return row
        raise KeyError(artifact_id)

    can606_gmm_q25 = followup_row("can606_gmm_q25")
    can606_gmm_posthoc = followup_row("can606_gmm_posthoc_best")
    can707_gmm_router = followup_row("can707_gmm_router_eval20")
    can707_cau_first20 = followup_row("can707_cau_eval20")
    can707_positive50 = followup_row("can707_positive_eval50")
    can707_weighted50 = followup_row("can707_weighted_eval50")
    can707_cau50 = followup_row("can707_cau_eval50")
    can808_positive50 = followup_row("can808_positive_eval50")
    can808_candidate_e50 = followup_row("can808_candidate_e_eval50")
    can808_cau50 = followup_row("can808_cau_e200_eval50")
    selector_baseline = selector_baseline_total(cau_selector_baselines)
    selector_safe = selector_mode_total(cau_selector_rows, "safe_zero_loss")
    selector_best = selector_mode_total(cau_selector_rows, "best_delta")
    policy_selector_baseline = selector_baseline_total(cau_policy_selector_baselines)
    policy_selector_safe = selector_mode_total(cau_policy_selector_rows, "safe_zero_loss")
    policy_selector_best = selector_mode_total(cau_policy_selector_rows, "best_delta")
    learned_safe = learned_router_total(cau_policy_learned_rows, "safe_zero_loss")
    learned_best = learned_router_total(cau_policy_learned_rows, "best_delta")
    learned_fresh_safe = learned_router_fresh(cau_policy_learned_rows, "safe_zero_loss")
    learned_fresh_best = learned_router_fresh(cau_policy_learned_rows, "best_delta")
    seq909 = cau_sequence_support["split909_thr005"]
    seq808 = cau_sequence_support["split808_thr005"]
    seq707 = cau_sequence_support["split707_thr005"]
    seq606 = cau_sequence_support["split606_thr005_heldout"]
    seq101_eval50 = cau_sequence_support["split101_thr005_eval50"]
    seq101_persistent = cau_sequence_support["split101_persistent_thr005_k10_eval50"]
    seq606_eval50 = cau_sequence_support["split606_thr005_eval50"]
    seq005_rows = [seq909, seq808, seq707]
    seq005_episodes = sum(int(row["episodes"]) for row in seq005_rows)
    seq005_router = sum(int(row["router_successes"]) for row in seq005_rows)
    seq005_positive = sum(int(row["positive_successes"]) for row in seq005_rows)
    seq005_cau = sum(int(row["cau_successes"]) for row in seq005_rows)
    seq005_gains = sum(int(row["gains_vs_positive"]) for row in seq005_rows)
    seq005_losses = sum(int(row["losses_vs_positive"]) for row in seq005_rows)
    seq005_with_heldout_rows = seq005_rows + [seq606]
    seq005_with_heldout_episodes = sum(int(row["episodes"]) for row in seq005_with_heldout_rows)
    seq005_with_heldout_router = sum(int(row["router_successes"]) for row in seq005_with_heldout_rows)
    seq005_with_heldout_positive = sum(int(row["positive_successes"]) for row in seq005_with_heldout_rows)
    seq005_with_heldout_cau = sum(int(row["cau_successes"]) for row in seq005_with_heldout_rows)
    seq_eval50_rows = [seq606_eval50, seq101_eval50]
    seq_eval50_episodes = sum(int(row["episodes"]) for row in seq_eval50_rows)
    seq_eval50_router = sum(int(row["router_successes"]) for row in seq_eval50_rows)
    seq_eval50_positive = sum(int(row["positive_successes"]) for row in seq_eval50_rows)
    seq_eval50_cau = sum(int(row["cau_successes"]) for row in seq_eval50_rows)
    seq_eval50_gains = sum(int(row["gains_vs_positive"]) for row in seq_eval50_rows)
    seq_eval50_losses = sum(int(row["losses_vs_positive"]) for row in seq_eval50_rows)

    endpoint_rows = [row for row in rows if row["decision_level"] == "endpoint_screen"]
    best_endpoint = max(
        endpoint_rows,
        key=lambda row: int(str(row["best_candidate_score"]).split("/", maxsplit=1)[0]),
    )
    if any(row["status"] not in {"reject", "preflight_no_go"} for row in rows):
        raise AssertionError("all sweep rows should be rejected or preflight no-go")

    lines = [
        "# SOTA Candidate Sweep Summary",
        "",
        "This report aggregates the focused candidate sweep from `triage_bc_sota_candidate_plan.md`.",
        "It is intended as paper-facing claim-boundary evidence, not as a new method result.",
        "",
        "## Decision",
        "",
        "- The focused SOTA-candidate sweep is negative: no candidate clears its first-stage gate.",
        (
            "- The best Can404 endpoint candidates in this sweep reach "
            f"`{best_endpoint['best_candidate_score']}`, while the matched positive-only anchor is "
            f"`{best_endpoint['positive_score']}`."
        ),
        "- CCG-Distill has development headroom on Lift606, but the fixed confidence signal fails the Lift707 transfer gate.",
        (
            "- First-state policy-distribution features improve the offline CAU selector audit, "
            "but the pooled frozen rule transfers neutrally on fresh split909 by opening no CAU starts."
        ),
        "- A linear learned router over those policy features also fails, opening all CAU starts on fresh split909.",
        "- A per-step support-margin router is the strongest current sequence-aware diagnostic, but the two 50-episode no-retune checks are not enough for a method claim.",
        "- The paper should stay framed as a precision/coverage empirical study unless a future router or state-conditional policy-quality signal captures CAU-dominant splits while preserving positive-only anchors.",
        "",
        "## Aggregate Table",
        "",
        "| candidate | primary gate | best candidate | positive | best matched reference | delta vs positive | status |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {candidate_id}. {family} | {primary_gate} | {best_candidate_score} | {positive_score} | {best_matched_reference_score} | {delta_vs_positive} | {status} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Readout",
            "",
            "- Support or transition-mass diagnostics were not sufficient predictors of endpoint success: SM-RWBC, SafeExpand, and IQL-AWBC improved local diagnostics but failed Can404.",
            "- Action-level and preference-style objectives can match the older Candidate C screen but still do not beat the positive-only anchor.",
            "- The Can404 anchor-overlap audit shows the near-miss candidates trade away positive-only successes: CAU gains 2 starts but loses 3 positive-only starts, while Demo-DPO gains 1 and loses 2.",
            "- A post-hoc feature-gate upper bound gives one CAU-plus-positive hypothesis at 18/20 with zero same-screen anchor losses, but the threshold is selected on Can404 endpoint outcomes and must be treated as a fresh-validation hypothesis only.",
            (
                "- The frozen CAU-plus-positive fallback passes one fresh split-505 screen and its "
                f"50-episode confirmation: first-20 routed {fresh_fallback_first20['routed_successes']}/"
                f"{fresh_fallback_first20['eval_episodes']} versus positive-only "
                f"{fresh_fallback_first20['positive_successes']}/{fresh_fallback_first20['eval_episodes']}; "
                f"50-episode routed {fresh_fallback_eval50['routed_successes']}/"
                f"{fresh_fallback_eval50['eval_episodes']} versus positive-only "
                f"{fresh_fallback_eval50['positive_successes']}/{fresh_fallback_eval50['eval_episodes']}; "
                f"both have {fresh_fallback_eval50['losses_vs_positive']} anchor losses at epoch 200."
            ),
            (
                "- The next predeclared fresh split-303 screen is neutral for the deployable fallback: "
                f"CAU alone reaches {fresh_fallback_303['cau_successes']}/"
                f"{fresh_fallback_303['eval_episodes']}, but routed fallback remains "
                f"{fresh_fallback_303['routed_successes']}/{fresh_fallback_303['eval_episodes']} "
                f"versus positive-only {fresh_fallback_303['positive_successes']}/"
                f"{fresh_fallback_303['eval_episodes']}, with "
                f"{fresh_fallback_303['losses_vs_positive']} anchor losses."
            ),
            (
                "- A two-feature gate selected on completed 303/404/505 screens "
                "(`initial_anchor_pos_dist_mean <= 1.273665 or initial_anchor_neg_dist_mean > 3.131861`) "
                "has stronger fresh follow-up but still does not clear a methods/SOTA bar: split101 confirms at "
                f"{two_feature_gate_101['routed_successes']}/{two_feature_gate_101['eval_episodes']} routed "
                f"versus positive-only {two_feature_gate_101['positive_successes']}/{two_feature_gate_101['eval_episodes']} "
                f"with {two_feature_gate_101['losses_vs_positive']} losses, while split202 50-episode confirmation is neutral at "
                f"{two_feature_gate_202['routed_successes']}/{two_feature_gate_202['eval_episodes']} versus "
                f"{two_feature_gate_202['positive_successes']}/{two_feature_gate_202['eval_episodes']} despite CAU alone reaching "
                f"{two_feature_gate_202['cau_successes']}/{two_feature_gate_202['eval_episodes']}."
            ),
            (
                "- The 50-episode five-split CAU-alone follow-up changes the original first20 readout from a hard rejection to a useful method seed: "
                f"CAU reaches {cau_five_split['cau_action_conflict']['successes']}/{cau_five_split['cau_action_conflict']['eval_episodes']} "
                f"versus positive-only {cau_five_split['positive_only_nn']['successes']}/{cau_five_split['positive_only_nn']['eval_episodes']}, "
                f"weighted BC {cau_five_split['weighted_bc']['successes']}/{cau_five_split['weighted_bc']['eval_episodes']}, "
                f"TRIAGE-BC v0.1 {cau_five_split['triage_bc_v01']['successes']}/{cau_five_split['triage_bc_v01']['eval_episodes']}, "
                f"and best old baseline per split {cau_five_split['best_old_baseline_per_split']['successes']}/{cau_five_split['best_old_baseline_per_split']['eval_episodes']}; "
                f"it still trails v0.2 selected union {cau_five_split['v02_selected_union']['successes']}/{cau_five_split['v02_selected_union']['eval_episodes']} "
                "and the best non-oracle per split including v0.2."
            ),
            (
                "- A post-hoc CAU-plus-v0.2 portfolio preflight was the best pre-fresh hypothesis, not claim evidence: "
                f"`{cau_v02_portfolio['gate_id']}` selects CAU on splits "
                f"{cau_v02_portfolio['selected_cau_splits']} and v0.2 on splits "
                f"{cau_v02_portfolio['selected_v02_splits']}, reaching "
                f"{cau_v02_portfolio['selected_successes']}/{cau_v02_portfolio['eval_episodes']} "
                f"({int(cau_v02_portfolio['delta_vs_always_v02']):+d} versus always-v0.2, "
                f"{int(cau_v02_portfolio['delta_vs_always_cau']):+d} versus always-CAU)."
            ),
            (
                "- The first fresh split606 endpoint validation rejects promoting that portfolio unchanged: "
                f"the gate-selected CAU branch reaches {fresh606_cau['success_count']}/{fresh606_cau['eval_episodes']} "
                f"versus positive-only {fresh606_positive['success_count']}/{fresh606_positive['eval_episodes']}; "
                f"frozen v0.2 union reaches {fresh606_union['success_count']}/{fresh606_union['eval_episodes']}, "
                f"the cleaner risk-fusion diagnostic reaches {fresh606_fusion['success_count']}/{fresh606_fusion['eval_episodes']}, "
                f"and the proper 130-demo expanded-mask CAU diagnostic reaches "
                f"{fresh606_expanded['success_count']}/{fresh606_expanded['eval_episodes']}."
            ),
            (
                "- The GMM-confidence router follow-up gives a useful negative/positive split: "
                f"labeled q25 calibration is neutral on split606 at {can606_gmm_q25['score']}, "
                f"a same-screen split606 threshold can reach {can606_gmm_posthoc['score']} but is post-hoc, "
                f"and that frozen threshold fails split707 at {can707_gmm_router['score']} while CAU alone reaches "
                f"{can707_cau_first20['score']} first-20 and {can707_cau50['score']} on the 50-episode confirmation "
                f"versus positive-only {can707_positive50['score']} and weighted BC {can707_weighted50['score']}."
            ),
            (
                "- The next fixed-CAU validation on split808 is negative against the strongest baseline: "
                f"CAU reaches {can808_cau50['score']} versus positive-only {can808_positive50['score']} "
                f"and the older Candidate E gate {can808_candidate_e50['score']}. This turns the split707 "
                "win into useful heterogeneity evidence, not a promotable fixed-method dominance result."
            ),
            (
                "- The leave-one-split-out CAU selector feature audit confirms that the remaining headroom is not captured by simple initial support-distance features: "
                f"positive-only is {selector_baseline['positive_successes']}/{selector_baseline['episodes']}, "
                f"always-CAU is {selector_baseline['cau_successes']}/{selector_baseline['episodes']}, "
                f"and the per-episode oracle switch is {selector_baseline['oracle_switch_successes']}/{selector_baseline['episodes']}; "
                f"the safe selector reaches {selector_safe['test_routed_successes']}/{selector_safe['test_episodes']} "
                f"with {selector_safe['test_gains_vs_positive']} gains and {selector_safe['test_losses_vs_positive']} losses, "
                f"while the best-delta selector reaches {selector_best['test_routed_successes']}/{selector_best['test_episodes']} "
                f"with {selector_best['test_gains_vs_positive']} gains and {selector_best['test_losses_vs_positive']} losses."
            ),
            (
                "- Replacing support-distance features with first-state policy-distribution features gives a stronger offline selector signal but still does not create a deployable router: "
                f"positive-only is {policy_selector_baseline['positive_successes']}/{policy_selector_baseline['episodes']}, "
                f"always-CAU is {policy_selector_baseline['cau_successes']}/{policy_selector_baseline['episodes']}, "
                f"and the per-episode oracle switch is {policy_selector_baseline['oracle_switch_successes']}/{policy_selector_baseline['episodes']}; "
                f"the safe held-out selector reaches {policy_selector_safe['test_routed_successes']}/{policy_selector_safe['test_episodes']} "
                f"with {policy_selector_safe['test_gains_vs_positive']} gains and {policy_selector_safe['test_losses_vs_positive']} losses, "
                f"while the best-delta selector reaches {policy_selector_best['test_routed_successes']}/{policy_selector_best['test_episodes']} "
                f"with {policy_selector_best['test_gains_vs_positive']} gains and {policy_selector_best['test_losses_vs_positive']} losses. "
                f"The pooled frozen rule on fresh split909 reaches {cau_policy_fresh909['cau_policy_feature_gate']['screen_score']} "
                f"versus positive-only {cau_policy_fresh909['positive_only_nn']['screen_score']} and CAU-alone "
                f"{cau_policy_fresh909['cau_action_conflict']['screen_score']}, with "
                f"{cau_policy_fresh909['cau_policy_feature_gate']['gate_open_episodes']} CAU opens."
            ),
            (
                "- A linear learned router over the same first-state policy features also fails the transfer test: "
                f"LOO safe reaches {learned_safe['test_routed_successes']}/{learned_safe['test_episodes']} "
                f"with {learned_safe['test_gains_vs_positive']} gains and {learned_safe['test_losses_vs_positive']} losses, "
                f"while LOO best-delta reaches {learned_best['test_routed_successes']}/{learned_best['test_episodes']} "
                f"with {learned_best['test_gains_vs_positive']} gains and {learned_best['test_losses_vs_positive']} losses. "
                f"Training on completed splits and freezing to split909 opens all CAU starts, giving "
                f"{learned_fresh_safe['test_routed_successes']}/{learned_fresh_safe['test_episodes']} safe "
                f"and {learned_fresh_best['test_routed_successes']}/{learned_fresh_best['test_episodes']} best-delta "
                f"versus positive-only {learned_fresh_safe['test_positive_successes']}/{learned_fresh_safe['test_episodes']}."
            ),
            (
                "- The per-step support-margin router is the strongest sequence-aware CAU follow-up so far, but it remains a validation candidate rather than a paper claim: "
                f"fixed threshold 0.05 aggregates to {score(seq005_router, seq005_episodes)} across splits 909/808/707 "
                f"versus positive-only {score(seq005_positive, seq005_episodes)} and CAU {score(seq005_cau, seq005_episodes)}, "
                f"with {seq005_gains} gains and {seq005_losses} loss versus positive-only. "
                f"Per split it reaches {seq909['router_score']} on split909, {seq808['router_score']} on split808, "
                f"and {seq707['router_score']} on split707. "
                f"The first no-retune held-out guardrail on split606 is neutral at {seq606['router_score']} "
                f"versus positive-only {seq606['positive_score']} and CAU {seq606['cau_score']}; including split606, "
                f"the same threshold is {score(seq005_with_heldout_router, seq005_with_heldout_episodes)} "
                f"versus positive-only {score(seq005_with_heldout_positive, seq005_with_heldout_episodes)} "
                f"and CAU {score(seq005_with_heldout_cau, seq005_with_heldout_episodes)}. "
                f"The 50-episode split606 validation is stronger: {seq606_eval50['router_score']} router "
                f"versus positive-only {seq606_eval50['positive_score']} and CAU {seq606_eval50['cau_score']}, "
                f"with {seq606_eval50['gains_vs_positive']} gains and {seq606_eval50['losses_vs_positive']} losses "
                "versus positive-only. "
                f"The next 50-episode split101 no-retune check is mixed-negative: {seq101_eval50['router_score']} "
                f"versus positive-only {seq101_eval50['positive_score']} but below CAU {seq101_eval50['cau_score']}. "
                f"Across these two 50-episode validations, the router is {score(seq_eval50_router, seq_eval50_episodes)} "
                f"versus positive-only {score(seq_eval50_positive, seq_eval50_episodes)} and CAU "
                f"{score(seq_eval50_cau, seq_eval50_episodes)}, with {seq_eval50_gains} gains and "
                f"{seq_eval50_losses} losses versus positive-only. "
                f"A persistent support-margin variant also fails split101, reaching {seq101_persistent['router_score']} "
                f"versus non-persistent {seq101_eval50['router_score']} and CAU {seq101_eval50['cau_score']}."
            ),
            "- The IQL-AWBC branch is especially diagnostic: classifier-reward advantages separated labeled positives and negatives offline, yet extraction collapsed without anchoring and remained weak with anchoring.",
            "- The responsible paper use remains a development appendix: CAU action-conflict is a useful but inconsistent Can method seed, and the hidden-label-free router needed to preserve anchors and select it is still unresolved.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{summary_csv}`.",
            f"- Anchor-overlap report: `{args.out_dir / 'CAN404_ANCHOR_OVERLAP_REPORT.md'}`.",
            f"- Anchor feature-gate preflight: `{args.out_dir / 'CAN404_ANCHOR_FEATURE_GATE_PREFLIGHT_REPORT.md'}`.",
            f"- CAU fallback fresh split-505 validation: `{args.out_dir / 'CAN505_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md'}`.",
            f"- CAU fallback fresh split-303 validation: `{args.out_dir / 'CAN303_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md'}`.",
            f"- CAU two-feature gate audit: `{args.out_dir / 'CAU_GATE_FEATURE_AUDIT_REPORT.md'}`.",
            f"- CAU two-feature gate fresh validation: `{args.out_dir / 'CAU_TWO_FEATURE_GATE_FRESH_VALIDATION_REPORT.md'}`.",
            f"- CAU five-split endpoint follow-up: `{args.out_dir / 'CAU_ACTION_CONFLICT_CAN_FIVE_SPLIT_ENDPOINT_REPORT.md'}`.",
            f"- CAU plus v0.2 portfolio preflight: `{args.out_dir / 'CAU_V02_PORTFOLIO_PREFLIGHT_REPORT.md'}`.",
            f"- CAU plus v0.2 fresh606 validation: `{args.out_dir / 'CAU_V02_FRESH606_ENDPOINT_VALIDATION_REPORT.md'}`.",
            f"- CAU/GMM router follow-up: `{args.out_dir / 'CAU_GMM_ROUTER_FOLLOWUP_REPORT.md'}`.",
            f"- CAU selector feature LOO audit: `{args.out_dir / 'CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md'}`.",
            f"- CAU policy-feature selector LOO audit: `{args.out_dir / 'CAU_POLICY_FEATURE_SELECTOR_LOO_AUDIT_REPORT.md'}`.",
            f"- CAU policy-feature fresh split909 screen: `{args.out_dir / 'CAU_POLICY_FEATURE_FRESH909_REPORT.md'}`.",
            f"- CAU policy-feature learned-router audit: `{args.out_dir / 'CAU_POLICY_FEATURE_LEARNED_ROUTER_AUDIT_REPORT.md'}`.",
            f"- CAU sequence support-margin router: `{args.out_dir / 'CAU_SEQUENCE_SUPPORT_ROUTER_REPORT.md'}`.",
        ]
    )
    for row in rows:
        lines.append(f"- Candidate {row['candidate_id']} report: `{row['report_path']}`.")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = {
        "1": ("10/20", -7),
        "2": ("16/20", -1),
        "3": ("10/20", -2),
        "4": ("12/20", -5),
        "5": ("16/20", -1),
        "6": ("13/20", -4),
    }
    actual = {str(row["candidate_id"]): (row["best_candidate_score"], row["delta_vs_positive"]) for row in rows}
    if actual != expected:
        raise AssertionError(f"unexpected sweep summary: {actual}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
