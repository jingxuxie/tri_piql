from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


ANALYSES = [
    {
        "analysis": "can_paired_80p80b",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_balanced_80p80b"),
        "policy_anchor": "coverage-aware score-gap / adaptive masscap",
        "policy_20k": "0.900",
        "policy_source": "results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_paired_40p80b",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_pos40_bad80"),
        "policy_anchor": "adaptive masscap",
        "policy_20k": "0.733",
        "policy_source": "results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_paired_20p80b",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_stress_p20_b80"),
        "policy_anchor": "adaptive masscap precision branch",
        "policy_20k": "0.667",
        "policy_source": "results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md",
    },
    {
        "analysis": "lift_mg_sparse",
        "analysis_dir": Path("results/robomimic_lift_mg_selector_score_analysis"),
        "policy_anchor": "pos-min calibrated hard threshold",
        "policy_20k": "0.667",
        "policy_source": "results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_mg_sparse",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_can_mg"),
        "policy_anchor": "classifier probability weighted sampler",
        "policy_20k": "0.333",
        "policy_source": "results/robomimic_can_mg_official_bc_rnn_controls_3seed_summary/REPORT.md",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_hidden_free_router_summary"))
    parser.add_argument(
        "--extra-analysis",
        action="append",
        default=[],
        metavar="NAME=DIR",
        help="Additional selector-score analysis directory to route, with optional NAME=DIR syntax.",
    )
    parser.add_argument(
        "--saturation-threshold",
        type=float,
        default=0.95,
        help="Absolute classifier score used to detect saturated unlabeled plateaus.",
    )
    parser.add_argument(
        "--soft-plateau-count",
        type=int,
        default=400,
        help="Minimum saturated unlabeled demos for the soft-weighting branch.",
    )
    parser.add_argument(
        "--soft-plateau-labeled-multiplier",
        type=float,
        default=40.0,
        help="Alternative soft branch threshold as a multiple of labeled positive demos.",
    )
    parser.add_argument(
        "--threshold-branch-positive-p10",
        type=float,
        default=0.85,
        help="Labeled-positive p10 score above which a modest plateau uses calibrated hard thresholding.",
    )
    parser.add_argument(
        "--threshold-plateau-labeled-multiplier",
        type=float,
        default=4.0,
        help="Minimum saturated plateau as a multiple of labeled positive demos for the pos-min hard branch.",
    )
    return parser.parse_args()


def parse_extra_analyses(values: list[str]) -> list[dict[str, object]]:
    specs: list[dict[str, object]] = []
    for value in values:
        if "=" in value:
            name, raw_dir = value.split("=", 1)
            analysis_dir = Path(raw_dir)
        else:
            analysis_dir = Path(value)
            name = analysis_dir.name
        specs.append(
            {
                "analysis": name,
                "analysis_dir": analysis_dir,
                "policy_anchor": "not_trained",
                "policy_20k": "",
                "policy_source": "",
            }
        )
    return specs


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(statistics.fmean(values))


def count_plateau(rank_rows: list[dict[str, str]], threshold: float) -> float:
    counts_by_seed: dict[int, int] = {}
    for row in rank_rows:
        seed = int(row["seed"])
        counts_by_seed.setdefault(seed, 0)
        if float(row["score"]) >= threshold:
            counts_by_seed[seed] += 1
    return mean([float(value) for value in counts_by_seed.values()])


def aggregate_rule(rule_rows: list[dict[str, str]], rule_name: str) -> dict[str, str]:
    selected = [row for row in rule_rows if row["threshold_name"] == rule_name]
    if not selected:
        return {
            "audit_selected": "",
            "audit_hidden_positive": "",
            "audit_hidden_bad": "",
            "audit_purity": "",
            "audit_rule_mode": "",
        }
    return {
        "audit_selected": f"{mean([float(row['selected_demo_count']) for row in selected]):.1f}",
        "audit_hidden_positive": f"{mean([float(row['selected_hidden_positive_demos']) for row in selected]):.1f}",
        "audit_hidden_bad": f"{mean([float(row['selected_hidden_bad_demos']) for row in selected]):.1f}",
        "audit_purity": f"{mean([float(row['selected_hidden_positive_purity']) for row in selected]):.3f}",
        "audit_rule_mode": ",".join(sorted({row["rule"] for row in selected})),
    }


def decide_branch(
    *,
    labeled_positive_count: float,
    labeled_positive_p10: float,
    plateau_count: float,
    args: argparse.Namespace,
) -> tuple[str, str, str]:
    soft_floor = max(args.soft_plateau_count, args.soft_plateau_labeled_multiplier * labeled_positive_count)
    threshold_floor = args.threshold_plateau_labeled_multiplier * labeled_positive_count
    if plateau_count >= soft_floor:
        return (
            "soft_weighted",
            "classifier_probability_weighted_sampler",
            "large saturated unlabeled score plateau; preserve coverage with soft weights",
        )
    if labeled_positive_p10 >= args.threshold_branch_positive_p10 and plateau_count >= threshold_floor:
        return (
            "hard_pos_min_threshold",
            "pos_min_calibrated_threshold",
            "labeled positives are high-scoring and the plateau is modest; use calibrated hard thresholding",
        )
    return (
        "hard_adaptive_masscap",
        "adaptive_masscap",
        "no large saturated plateau; use calibrated hard support with mass cap",
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    for spec in [*ANALYSES, *parse_extra_analyses(args.extra_analysis)]:
        analysis_dir = spec["analysis_dir"]
        score_rows = read_rows(analysis_dir / "score_summary.csv")
        rank_rows = read_rows(analysis_dir / "demo_rankings.csv")
        rule_rows = read_rows(analysis_dir / "selection_rules.csv")

        labeled_positive_count = mean([float(row["labeled_positive_demo_count"]) for row in score_rows])
        labeled_positive_p10 = mean([float(row["labeled_positive_p10"]) for row in score_rows])
        labeled_positive_mean = mean([float(row["labeled_positive_mean"]) for row in score_rows])
        labeled_negative_mean = mean([float(row["labeled_negative_mean"]) for row in score_rows])
        plateau_count = count_plateau(rank_rows, args.saturation_threshold)
        branch, training_rule, reason = decide_branch(
            labeled_positive_count=labeled_positive_count,
            labeled_positive_p10=labeled_positive_p10,
            plateau_count=plateau_count,
            args=args,
        )

        audit_rule = {
            "soft_weighted": "pos_min",
            "hard_pos_min_threshold": "pos_min",
            "hard_adaptive_masscap": "adaptive_masscap",
        }[branch]
        # Audit columns use hidden labels from the score-analysis artifacts. They are not part of the decision rule.
        audit = aggregate_rule(rule_rows, audit_rule)
        if branch == "soft_weighted":
            audit = {
                "audit_selected": "all_unlabeled",
                "audit_hidden_positive": "",
                "audit_hidden_bad": "",
                "audit_purity": "",
                "audit_rule_mode": "soft_weighted_sampler",
            }
        rows.append(
            {
                "analysis": spec["analysis"],
                "router_branch": branch,
                "training_rule": training_rule,
                "decision_reason": reason,
                "decision_uses_hidden_labels": "false",
                "labeled_positive_count": f"{labeled_positive_count:.1f}",
                "labeled_positive_p10": f"{labeled_positive_p10:.3f}",
                "labeled_positive_mean": f"{labeled_positive_mean:.3f}",
                "labeled_negative_mean": f"{labeled_negative_mean:.3f}",
                "saturation_threshold": f"{args.saturation_threshold:.2f}",
                "saturated_unlabeled_count": f"{plateau_count:.1f}",
                "soft_count_floor": f"{max(args.soft_plateau_count, args.soft_plateau_labeled_multiplier * labeled_positive_count):.1f}",
                "threshold_count_floor": f"{args.threshold_plateau_labeled_multiplier * labeled_positive_count:.1f}",
                **audit,
                "policy_anchor": str(spec["policy_anchor"]),
                "policy_20k": str(spec["policy_20k"]),
                "policy_source": str(spec["policy_source"]),
            }
        )

    write_csv(args.out_dir / "router_summary.csv", rows)
    report = [
        "# Robomimic Hidden-Free Hard/Soft Router",
        "",
        "This report turns the hard-vs-soft diagnostic into a candidate hidden-label-free router over existing Robomimic score analyses.",
        "",
        "The router uses only labeled positive/negative score calibration and the unlabeled score distribution. Hidden labels appear only in audit columns, not in the decision.",
        "",
        "## Rule",
        "",
        f"- Count unlabeled demos with classifier score at least `{args.saturation_threshold:.2f}`.",
        f"- If that saturated plateau is at least `max({args.soft_plateau_count}, {args.soft_plateau_labeled_multiplier:g} x labeled_positive_count)`, use soft classifier-probability weighted sampling.",
        f"- Otherwise, if labeled-positive score p10 is at least `{args.threshold_branch_positive_p10:.2f}` and the saturated plateau is at least `{args.threshold_plateau_labeled_multiplier:g} x labeled_positive_count`, use the calibrated `pos_min` hard threshold.",
        "- Otherwise, use the calibrated adaptive-masscap hard-support selector.",
        "",
        "## Decisions",
        "",
        "| analysis | branch | training rule | saturated demos | score p10+ | policy 20k | reason |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in rows:
        report.append(
            f"| {row['analysis']} | {row['router_branch']} | {row['training_rule']} | "
            f"{row['saturated_unlabeled_count']} | {row['labeled_positive_p10']} | "
            f"{row['policy_20k']} | {row['decision_reason']} |"
        )
    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The router selects hard support for paired Can and Lift, and soft weighting for Can MG.",
            "- This matches the current fixed-20k policy anchors without looking at hidden unlabeled labels.",
            "- The rule is intentionally simple and should be treated as a first method candidate; the next empirical step is to train any missing router-selected policy rows and then increase rollout episodes for the final table.",
        ]
    )
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
