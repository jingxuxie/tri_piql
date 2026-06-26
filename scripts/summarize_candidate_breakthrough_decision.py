#!/usr/bin/env python3
"""Summarize the current candidate-breakthrough decision state."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BREAKTHROUGH = ROOT / "results" / "candidate_breakthrough"
FRESH = ROOT / "results" / "candidate_g_fresh_preflight"
CAN_FRESH_VALIDATION = ROOT / "results" / "candidate_f_can_fresh_validation"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def row_where(rows: list[dict[str, str]], **criteria: object) -> dict[str, str]:
    for row in rows:
        if all(row.get(key) == str(value) for key, value in criteria.items()):
            return row
    raise KeyError(f"no row matching {criteria}")


def count(row: dict[str, str], key: str, denom: int) -> str:
    return f"{int(float(row[key]))}/{denom}"


def parse_count(value: str) -> tuple[int, int] | None:
    if not value or "/" not in value:
        return None
    successes, episodes = value.split("/", 1)
    return int(successes), int(episodes)


def successes(rows: list[dict[str, str]], **criteria: object) -> int:
    return int(float(row_where(rows, **criteria)["successes"]))


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def main() -> None:
    can_rows = read_csv(BREAKTHROUGH / "candidate_f_frozen_matrix_summary.csv")
    can_total = row_where(can_rows, split="total")
    fresh_can_rows = read_csv(FRESH / "candidate_f_fresh_can_smokes_summary.csv")
    fresh_validation_rows = read_csv(
        CAN_FRESH_VALIDATION / "tables" / "candidate_f_can_fresh_validation_status.csv"
    )
    lift_rows = read_csv(BREAKTHROUGH / "candidate_f_lift_transfer_audit.csv")
    lift_total = row_where(lift_rows, split="total")

    k_rows = read_csv(FRESH / "candidate_k_confidence_router_summary.csv")
    m_rows = read_csv(FRESH / "candidate_m_temporal_confidence_router_summary.csv")
    n_rows = read_csv(FRESH / "candidate_n_persistent_confidence_router_summary.csv")
    p_rows = read_csv(FRESH / "candidate_p_posinit_anchor_union_screen_summary.csv")
    qr_rows = read_csv(FRESH / "candidate_qr_anchor_protection_screen_summary.csv")
    s_rows = read_csv(FRESH / "candidate_s_labeled_initial_risk_summary.csv")
    d_rows = read_csv(BREAKTHROUGH / "candidate_d_endpoint_screen_summary.csv")
    t_rows = read_csv(BREAKTHROUGH / "candidate_t_policy_interpolation_screen_summary.csv")
    u_rows = read_csv(BREAKTHROUGH / "candidate_u_anchor_l2_screen_summary.csv")
    v_rows = read_csv(BREAKTHROUGH / "candidate_v_anchor_logprob_screen_summary.csv")
    w_rows = read_csv(BREAKTHROUGH / "candidate_w_two_feature_gate_summary.csv")

    k_lift606_router = row_where(
        k_rows,
        split="lift606",
        method="confidence_router_thr6p27",
        protocol="50 valid-positive starts",
    )
    k_lift606_positive = row_where(
        k_rows,
        split="lift606",
        method="positive_only_nn",
        protocol="50 valid-positive starts",
    )
    k_lift707_router = row_where(k_rows, split="lift707", method="confidence_router_thr6p27")
    k_lift707_positive = row_where(k_rows, split="lift707", method="positive_only_nn")

    m_best = max(m_rows, key=lambda row: int(float(row["successes"])))
    n_best = max(n_rows, key=lambda row: int(float(row["successes"])))
    p_candidate = row_where(p_rows, method="candidate_p_epoch20_posinit_finetune")
    p_positive = row_where(p_rows, method="positive_only_nn")
    d_positive = row_where(d_rows, method_id="positive_only_nn_top40")
    d_candidate_c = row_where(d_rows, method_id="candidate_c_sequence_mask_e200")
    d_best_negative = max(
        [row for row in d_rows if row["kind"] in {"candidate_d", "candidate_x"}],
        key=lambda row: int(row["success_count"]),
    )
    qr_best = max(
        [row for row in qr_rows if row["group"] in {"candidate_q_short_finetune", "candidate_r_interpolation"}],
        key=lambda row: int(float(row["successes"])),
    )
    s_lift606 = row_where(s_rows, split="lift606", feature_set="policy", quantile="0.25")
    s_lift707 = row_where(s_rows, split="lift707", feature_set="policy", quantile="0.25")
    t_positive = row_where(t_rows, method="positive_only_nn_top40")
    t_best = max(
        [row for row in t_rows if row["group"] == "candidate_t_interpolation"],
        key=lambda row: int(row["success_count"]),
    )
    u_positive = row_where(u_rows, method="positive_only_nn_top40")
    u_best = max(
        [row for row in u_rows if row["group"] == "candidate_u_anchor_l2"],
        key=lambda row: int(row["success_count"]),
    )
    v_best_first20 = max(
        [
            row
            for row in v_rows
            if row["split"] == "404"
            and row["protocol"] == "first20"
            and row["group"] == "candidate_v_anchor_logprob"
        ],
        key=lambda row: int(row["success_count"]),
    )
    v_positive_first20 = row_where(v_rows, split="404", protocol="first20", method="positive_only_nn_top40")
    v_eval50_404 = row_where(v_rows, split="404", protocol="eval50", group="candidate_v_anchor_logprob")
    v_positive50_404 = row_where(v_rows, split="404", protocol="eval50", method="positive_only_nn_top40")
    v_eval50_505 = row_where(v_rows, split="505", protocol="eval50", group="candidate_v_anchor_logprob")
    v_positive50_505 = row_where(v_rows, split="505", protocol="eval50", method="positive_only_nn_top40")
    w_404 = row_where(w_rows, split="404")
    w_505 = row_where(w_rows, split="505")
    w_total = row_where(w_rows, split="total")

    fresh_candidate_f = row_where(fresh_can_rows, method="candidate_f")
    fresh_positive = row_where(fresh_can_rows, method="positive_only_nn")
    fresh_weighted = row_where(fresh_can_rows, method="weighted_bc")
    claim_ready_validation = [
        row
        for row in fresh_validation_rows
        if row["candidate_f_eval50"] == "1"
        and row["positive_only_nn_eval50"] == "1"
        and row["weighted_bc_eval50"] == "1"
        and row["triage_bc_eval50"] == "1"
    ]
    candidate_f_validation_success = sum(
        parse_count(row["candidate_f_success50"])[0]  # type: ignore[index]
        for row in claim_ready_validation
        if parse_count(row["candidate_f_success50"]) is not None
    )
    candidate_f_validation_episodes = sum(
        parse_count(row["candidate_f_success50"])[1]  # type: ignore[index]
        for row in claim_ready_validation
        if parse_count(row["candidate_f_success50"]) is not None
    )
    best_validation_success = sum(
        parse_count(row["best_baseline_success50"])[0]  # type: ignore[index]
        for row in claim_ready_validation
        if parse_count(row["best_baseline_success50"]) is not None
    )
    best_validation_episodes = sum(
        parse_count(row["best_baseline_success50"])[1]  # type: ignore[index]
        for row in claim_ready_validation
        if parse_count(row["best_baseline_success50"]) is not None
    )
    worse_validation_rows = sum(row["candidate_f_no_worse_best50"] == "0" for row in claim_ready_validation)
    max_allowed_worse = 1

    evidence_rows = [
        {
            "area": "Can discovery matrix",
            "status": "promising but scoped",
            "key_result": (
                f"Candidate F {count(can_total, 'candidate_f', 250)} vs "
                f"positive {count(can_total, 'positive', 250)}, "
                f"weighted {count(can_total, 'weighted', 250)}, "
                f"triage {count(can_total, 'triage', 250)}, "
                f"per-split oracle {count(can_total, 'best_baseline', 250)}"
            ),
            "decision": "Keep as Can 40p/80b discovery evidence, not a general robotics claim.",
            "artifact": "results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md",
        },
        {
            "area": "Fresh Can smokes",
            "status": "neutral",
            "key_result": (
                f"Candidate F {fresh_candidate_f['successes']}/{fresh_candidate_f['episodes']} "
                f"ties positive-only {fresh_positive['successes']}/{fresh_positive['episodes']}; "
                f"weighted is {fresh_weighted['successes']}/{fresh_weighted['episodes']}"
            ),
            "decision": "Historical smoke only; superseded by the failed predeclared fresh validation matrix.",
            "artifact": "results/candidate_g_fresh_preflight/candidate_f_fresh_can_smokes_REPORT.md",
        },
        {
            "area": "Fresh Can validation",
            "status": "failed early",
            "key_result": (
                f"Candidate F {candidate_f_validation_success}/{candidate_f_validation_episodes} "
                f"vs best completed baselines {best_validation_success}/{best_validation_episodes}; "
                f"worse on {worse_validation_rows}/{len(claim_ready_validation)} completed validation rows, "
                f"while the 4/5 no-worse gate allows at most {max_allowed_worse}"
            ),
            "decision": "Stop Candidate F scaling; the predeclared fresh validation gate is already impossible.",
            "artifact": "results/candidate_f_can_fresh_validation/tables/candidate_f_can_fresh_validation_STATUS.md",
        },
        {
            "area": "Lift transfer",
            "status": "not transferred",
            "key_result": (
                f"Can-style Candidate F transfer {count(lift_total, 'can_style_success', 250)} "
                f"vs Lift oracle {count(lift_total, 'best_baseline', 250)}; "
                f"tail-severity diagnostic {count(lift_total, 'tail_severity_success', 250)} is not frozen"
            ),
            "decision": "Treat Lift as a limitation or abstention case until a new frozen proxy exists.",
            "artifact": "results/candidate_breakthrough/candidate_f_lift_transfer_audit_REPORT.md",
        },
        {
            "area": "Lift routers",
            "status": "rejected",
            "key_result": (
                f"Best local confidence gate {k_lift606_router['successes']}/{k_lift606_router['episodes']} "
                f"beats Lift606 positive {k_lift606_positive['successes']}/{k_lift606_positive['episodes']}, "
                f"but transfers to Lift707 at {k_lift707_router['successes']}/{k_lift707_router['episodes']} "
                f"vs positive {k_lift707_positive['successes']}/{k_lift707_positive['episodes']}; "
                f"temporal {m_best['successes']}/{m_best['episodes']}, persistent {n_best['successes']}/{n_best['episodes']}"
            ),
            "decision": "Stop scalar initial-threshold, temporal-confidence, and persistence router tuning.",
            "artifact": "results/candidate_g_fresh_preflight/candidate_k_confidence_router_screen_REPORT.md",
        },
        {
            "area": "Anchor-union training",
            "status": "rejected",
            "key_result": (
                f"Positive-init fine-tune {p_candidate['successes']}/{p_candidate['episodes']} "
                f"and best Q/R rescue {qr_best['successes']}/{qr_best['episodes']} "
                f"remain below positive-only {p_positive['successes']}/{p_positive['episodes']}"
            ),
            "decision": "Stop lower-weight triage-extra BC targets; a future training candidate needs a different objective.",
            "artifact": "results/candidate_g_fresh_preflight/candidate_qr_anchor_protection_screen_REPORT.md",
        },
        {
            "area": "Transition-level objectives",
            "status": "rejected",
            "key_result": (
                f"Can404 sequence-mask {d_candidate_c['success_count']}/{d_candidate_c['eval_episodes']} "
                f"and best negative-action hinge {d_best_negative['success_count']}/{d_best_negative['eval_episodes']} "
                f"remain below positive-only {d_positive['success_count']}/{d_positive['eval_episodes']}"
            ),
            "decision": "Stop the current transition-weight, sequence-mask, and nearest-negative hinge recipes unchanged.",
            "artifact": "results/candidate_breakthrough/candidate_d_endpoint_screen_REPORT.md",
        },
        {
            "area": "Policy interpolation",
            "status": "rejected",
            "key_result": (
                f"Best Can404 positive-to-weighted interpolation {t_best['successes']} "
                f"at alpha {t_best['alpha']} vs positive-only {t_positive['successes']}"
            ),
            "decision": "Stop naive parameter interpolation; anchor preservation needs an explicit objective, not weight averaging.",
            "artifact": "results/candidate_breakthrough/candidate_t_policy_interpolation_screen_REPORT.md",
        },
        {
            "area": "Anchor-L2 fine-tuning",
            "status": "neutral/rejected",
            "key_result": (
                f"Best Can404 positive-initialized sequence-mask fine-tune {u_best['successes']} "
                f"at epoch {u_best['train_epochs']} vs positive-only {u_positive['successes']}"
            ),
            "decision": "Do not scale normalized parameter-L2 anchoring; use output-level anchoring or a different objective if continuing training-side work.",
            "artifact": "results/candidate_breakthrough/candidate_u_anchor_l2_screen_REPORT.md",
        },
        {
            "area": "Output-anchor fine-tuning",
            "status": "failed first validation",
            "key_result": (
                f"Best Can404 first-20 output-anchor checkpoint {v_best_first20['successes']} "
                f"vs positive-only {v_positive_first20['successes']}; "
                f"Can404 50-episode check {v_eval50_404['successes']} ties positive-only {v_positive50_404['successes']}; "
                f"frozen Can505 check {v_eval50_505['successes']} vs positive-only {v_positive50_505['successes']}"
            ),
            "decision": "Do not scale as a paper-facing method; output anchoring is informative but failed the first non-404 validation gate.",
            "artifact": "results/candidate_breakthrough/candidate_v_anchor_logprob_screen_REPORT.md",
        },
        {
            "area": "Two-feature weighted-rescue gate",
            "status": "diagnostic/rejected",
            "key_result": (
                f"Candidate W {w_total['candidate_w']} ties Candidate E {w_total['candidate_e']} "
                f"over splits 404+505; split404 {w_404['candidate_w']} but split505 "
                f"{w_505['candidate_w']} vs positive-only {w_505['positive']}"
            ),
            "decision": "Do not promote scalar initial support-distance plus margin gating; it preserves the known rescue but does not clear validation.",
            "artifact": "results/candidate_breakthrough/candidate_w_two_feature_gate_REPORT.md",
        },
        {
            "area": "Labeled initial-risk gate",
            "status": "rejected",
            "key_result": (
                f"Primary q25 policy gate: Lift606 {s_lift606['successes']}/{s_lift606['episodes']} "
                f"vs positive {s_lift606['positive']}/{s_lift606['episodes']}; "
                f"Lift707 {s_lift707['successes']}/{s_lift707['episodes']} "
                f"vs positive {s_lift707['positive']}/{s_lift707['episodes']}"
            ),
            "decision": "Do not spend live endpoint budget on this learned initial-risk proxy.",
            "artifact": "results/candidate_g_fresh_preflight/candidate_s_labeled_initial_risk_router_REPORT.md",
        },
    ]

    csv_path = BREAKTHROUGH / "candidate_breakthrough_decision_summary.csv"
    report_path = BREAKTHROUGH / "candidate_breakthrough_decision_REPORT.md"
    write_csv(
        csv_path,
        evidence_rows,
        ["area", "status", "key_result", "decision", "artifact"],
    )

    can_display = [
        {
            "split": row["split"],
            "candidate_f_source": row["candidate_f_source"],
            "positive": count(row, "positive", 250 if row["split"] == "total" else 50),
            "weighted": count(row, "weighted", 250 if row["split"] == "total" else 50),
            "triage": count(row, "triage", 250 if row["split"] == "total" else 50),
            "best_baseline": count(row, "best_baseline", 250 if row["split"] == "total" else 50),
            "candidate_f": count(row, "candidate_f", 250 if row["split"] == "total" else 50),
            "delta": row["delta_vs_best_baseline"],
        }
        for row in can_rows
    ]

    fresh_display = [
        {
            "method": row["method"],
            "successes": f"{row['successes']}/{row['episodes']}",
        }
        for row in fresh_can_rows
    ]
    fresh_validation_display = [
        {
            "seed": row["seed"],
            "candidate_f_branch": row["candidate_f_branch"],
            "positive": row["positive_only_nn_success50"],
            "weighted": row["weighted_bc_success50"],
            "triage": row["triage_bc_success50"],
            "candidate_f": row["candidate_f_success50"],
            "best_baseline": row["best_baseline_success50"],
            "delta": row["candidate_f_delta_vs_best50"],
            "no_worse": row["candidate_f_no_worse_best50"],
        }
        for row in claim_ready_validation
    ]

    lift_display = [
        {
            "split": row["split"],
            "positive": count(row, "positive", 250 if row["split"] == "total" else 50),
            "weighted": count(row, "weighted", 250 if row["split"] == "total" else 50),
            "triage": count(row, "triage", 250 if row["split"] == "total" else 50),
            "best": count(row, "best_baseline", 250 if row["split"] == "total" else 50),
            "can_style": count(row, "can_style_success", 250 if row["split"] == "total" else 50),
            "tail_severity": count(row, "tail_severity_success", 250 if row["split"] == "total" else 50),
        }
        for row in lift_rows
    ]

    lines = [
        "# Candidate-Breakthrough Decision Report",
        "",
        "**Status: no general methods-dominance claim yet.** The current search",
        "produced one clean Can-only discovery result, but the predeclared fresh",
        "Can validation gate failed early and the Lift follow-ups reject the",
        "deployable routers and simple anchor-union policy-training variants",
        "tested so far.",
        "",
        "## Decision Summary",
        "",
        *table(evidence_rows, ["area", "status", "key_result", "decision", "artifact"]),
        "",
        "## Candidate F Can Discovery Matrix",
        "",
        *table(
            can_display,
            [
                "split",
                "candidate_f_source",
                "positive",
                "weighted",
                "triage",
                "best_baseline",
                "candidate_f",
                "delta",
            ],
        ),
        "",
        "Read: Candidate F is the strongest completed candidate on Can 40p/80b,",
        "but most of its aggregate edge comes from the split-404 rescue. It should",
        "be reported as scoped Can evidence.",
        "",
        "## Fresh Can Smoke Check",
        "",
        *table(fresh_display, ["method", "successes"]),
        "",
        "Read: the two fresh first-20 Can smokes are neutral. They do not erase the",
        "Can discovery matrix, but they did not justify a methods claim by themselves.",
        "",
        "## Fresh Can Frozen Validation",
        "",
        *table(
            fresh_validation_display,
            [
                "seed",
                "candidate_f_branch",
                "positive",
                "weighted",
                "triage",
                "candidate_f",
                "best_baseline",
                "delta",
                "no_worse",
            ],
        ),
        "",
        "Read: the predeclared fresh Can validation matrix failed early. Candidate F",
        "is worse than the best completed baseline on both completed validation",
        "rows, so the 4/5 no-worse gate is impossible even before running the",
        "remaining seeds.",
        "",
        "## Lift Transfer Check",
        "",
        *table(lift_display, ["split", "positive", "weighted", "triage", "best", "can_style", "tail_severity"]),
        "",
        "Read: direct Can-style transfer is below the Lift per-split baseline",
        "oracle. The tail-severity rule is diagnostic because the mild/severe",
        "cutoff was discovered after looking at completed Lift rows.",
        "",
        "## Recommended Paper Action",
        "",
        "- Keep the main paper framing as a precision-coverage study, with",
        "  controlled diagnostics and careful Robomimic branch-selection results.",
        "- Move Candidate F to scoped Can discovery / failed-development evidence;",
        "  do not spend more endpoint budget on the remaining fresh validation seeds",
        "  for a methods-dominance claim.",
        "- Treat Lift as a limitation/abstention case for now. The tested router",
        "  proxies and anchor-union policy-training variants should not be tuned",
        "  further without a materially different objective or proxy.",
        "- Do not claim weighted BC is bad. The evidence says weighted BC is strong",
        "  in some coverage-heavy regimes and hard/anchor support is strong in",
        "  others.",
        "",
        "## Artifacts",
        "",
        f"- Decision CSV: `{csv_path.relative_to(ROOT)}`.",
        "- Can matrix: `results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md`.",
        "- Fresh Can smokes: `results/candidate_g_fresh_preflight/candidate_f_fresh_can_smokes_REPORT.md`.",
        "- Fresh Can validation: `results/candidate_f_can_fresh_validation/tables/candidate_f_can_fresh_validation_STATUS.md`.",
        "- Lift transfer audit: `results/candidate_breakthrough/candidate_f_lift_transfer_audit_REPORT.md`.",
        "- Lift router reports: `results/candidate_g_fresh_preflight/candidate_k_confidence_router_screen_REPORT.md`,",
        "  `results/candidate_g_fresh_preflight/candidate_l_calibrated_confidence_router_REPORT.md`,",
        "  `results/candidate_g_fresh_preflight/candidate_m_temporal_confidence_router_REPORT.md`, and",
        "  `results/candidate_g_fresh_preflight/candidate_n_persistent_confidence_router_REPORT.md`.",
        "- Training-side reports: `results/candidate_g_fresh_preflight/candidate_o_lift_anchor_union_screen_REPORT.md`,",
        "  `results/candidate_g_fresh_preflight/candidate_p_posinit_anchor_union_screen_REPORT.md`, and",
        "  `results/candidate_g_fresh_preflight/candidate_qr_anchor_protection_screen_REPORT.md`.",
        "- Transition-level reports: `results/candidate_breakthrough/candidate_a_endpoint_screen_REPORT.md`,",
        "  `results/candidate_breakthrough/candidate_c_endpoint_screen_REPORT.md`, and",
        "  `results/candidate_breakthrough/candidate_d_endpoint_screen_REPORT.md`.",
        "- Policy-composition and anchor reports: `results/candidate_breakthrough/candidate_t_policy_interpolation_screen_REPORT.md`,",
        "  `results/candidate_breakthrough/candidate_u_anchor_l2_screen_REPORT.md`, and",
        "  `results/candidate_breakthrough/candidate_v_anchor_logprob_screen_REPORT.md`.",
        "- Candidate V failure analysis: `results/candidate_breakthrough/candidate_v_failure_analysis_REPORT.md`.",
        "- Candidate W two-feature gate: `results/candidate_breakthrough/candidate_w_two_feature_gate_REPORT.md`.",
        "- Learned initial-risk report: `results/candidate_g_fresh_preflight/candidate_s_labeled_initial_risk_router_REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
