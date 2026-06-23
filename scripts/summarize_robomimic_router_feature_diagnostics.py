from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path


ANALYSES = [
    {
        "analysis": "can_paired_80p80b",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_balanced_80p80b"),
        "observed_mode": "hard",
        "policy_20k": "0.900",
        "policy_source": "results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_paired_40p80b",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_pos40_bad80"),
        "observed_mode": "hard",
        "policy_20k": "0.733",
        "policy_source": "results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_paired_20p80b",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_stress_p20_b80"),
        "observed_mode": "hard",
        "policy_20k": "0.667",
        "policy_source": "results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md",
    },
    {
        "analysis": "lift_mg_sparse",
        "analysis_dir": Path("results/robomimic_lift_mg_selector_score_analysis"),
        "observed_mode": "hard",
        "policy_20k": "0.667",
        "policy_source": "results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_mg_sparse",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_can_mg"),
        "observed_mode": "soft",
        "policy_20k": "0.333",
        "policy_source": "results/robomimic_can_mg_official_bc_rnn_controls_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_paired_40p80b_shuffle42",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_pos40_bad80_shuffle42"),
        "observed_mode": "hard_validation",
        "policy_20k": "0.633",
        "policy_source": "results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_3seed_summary/REPORT.md",
    },
    {
        "analysis": "lift_mg_sparse_shuffle42",
        "analysis_dir": Path("results/robomimic_lift_mg_selector_score_analysis_shuffle42"),
        "observed_mode": "hard_validation",
        "policy_20k": "0.600",
        "policy_source": "results/robomimic_lift_mg_shuffle42_posmin_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_mg_sparse_shuffle42",
        "analysis_dir": Path("results/robomimic_selector_score_analysis_can_mg_shuffle42"),
        "observed_mode": "fragile",
        "policy_20k": "0.100",
        "policy_source": "results/robomimic_can_mg_shuffle42_router_branch_seed0_summary/REPORT.md",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/robomimic_router_feature_diagnostics"),
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(statistics.fmean(values))


def safe_float(value: str) -> float:
    if value == "":
        return float("nan")
    return float(value)


def fmt(value: float, digits: int = 3) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def group_by_seed(rows: list[dict[str, str]]) -> dict[int, list[dict[str, str]]]:
    grouped: dict[int, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(int(row["seed"]), []).append(row)
    return grouped


def count_scores(rows: list[dict[str, str]], threshold: float) -> int:
    return sum(1 for row in rows if float(row["score"]) >= threshold)


def threshold_counts(
    rank_rows: list[dict[str, str]],
    score_rows: list[dict[str, str]],
) -> dict[str, float]:
    ranks_by_seed = group_by_seed(rank_rows)
    scores_by_seed = {int(row["seed"]): row for row in score_rows}
    count_keys = {
        "count_ge_0p90": [],
        "count_ge_0p95": [],
        "count_ge_0p98": [],
        "count_ge_0p99": [],
        "count_ge_pos_min": [],
        "count_ge_pos_p10": [],
        "count_ge_pos_p50": [],
        "count_ge_neg_max": [],
    }
    estimated_positive_mass = []
    unlabeled_count = []
    for seed, rows in ranks_by_seed.items():
        score_row = scores_by_seed[seed]
        pos_mean = float(score_row["labeled_positive_mean"])
        neg_mean = float(score_row["labeled_negative_mean"])
        denom = max(1.0e-8, pos_mean - neg_mean)
        estimated_positive_mass.append(
            sum(
                min(1.0, max(0.0, (float(row["score"]) - neg_mean) / denom))
                for row in rows
            )
        )
        unlabeled_count.append(float(len(rows)))
        count_keys["count_ge_0p90"].append(float(count_scores(rows, 0.90)))
        count_keys["count_ge_0p95"].append(float(count_scores(rows, 0.95)))
        count_keys["count_ge_0p98"].append(float(count_scores(rows, 0.98)))
        count_keys["count_ge_0p99"].append(float(count_scores(rows, 0.99)))
        count_keys["count_ge_pos_min"].append(float(count_scores(rows, float(score_row["labeled_positive_min"]))))
        count_keys["count_ge_pos_p10"].append(float(count_scores(rows, float(score_row["labeled_positive_p10"]))))
        count_keys["count_ge_pos_p50"].append(float(count_scores(rows, float(score_row["labeled_positive_p50"]))))
        count_keys["count_ge_neg_max"].append(float(count_scores(rows, float(score_row["labeled_negative_max"]))))
    return {
        **{key: mean(values) for key, values in count_keys.items()},
        "estimated_positive_mass": mean(estimated_positive_mass),
        "unlabeled_count": mean(unlabeled_count),
    }


def aggregate_rule(rule_rows: list[dict[str, str]], threshold_name: str) -> dict[str, float | str]:
    selected = [row for row in rule_rows if row["threshold_name"] == threshold_name]
    if not selected:
        return {
            f"{threshold_name}_selected": float("nan"),
            f"{threshold_name}_hidden_positive": float("nan"),
            f"{threshold_name}_hidden_bad": float("nan"),
            f"{threshold_name}_purity": float("nan"),
            f"{threshold_name}_rule": "",
        }
    return {
        f"{threshold_name}_selected": mean([float(row["selected_demo_count"]) for row in selected]),
        f"{threshold_name}_hidden_positive": mean([float(row["selected_hidden_positive_demos"]) for row in selected]),
        f"{threshold_name}_hidden_bad": mean([float(row["selected_hidden_bad_demos"]) for row in selected]),
        f"{threshold_name}_purity": mean([float(row["selected_hidden_positive_purity"]) for row in selected]),
        f"{threshold_name}_rule": ",".join(sorted({row["rule"] for row in selected})),
    }


def feature_row(spec: dict[str, object]) -> dict[str, str]:
    analysis_dir = spec["analysis_dir"]
    score_rows = read_rows(analysis_dir / "score_summary.csv")
    rank_rows = read_rows(analysis_dir / "demo_rankings.csv")
    rule_rows = read_rows(analysis_dir / "selection_rules.csv")
    counts = threshold_counts(rank_rows, score_rows)
    labeled_positive_count = mean([float(row["labeled_positive_demo_count"]) for row in score_rows])
    labeled_negative_count = mean([float(row["labeled_negative_demo_count"]) for row in score_rows])
    labeled_positive_p10 = mean([float(row["labeled_positive_p10"]) for row in score_rows])
    labeled_positive_mean = mean([float(row["labeled_positive_mean"]) for row in score_rows])
    labeled_negative_mean = mean([float(row["labeled_negative_mean"]) for row in score_rows])
    pos_min = aggregate_rule(rule_rows, "pos_min")
    pos_p10 = aggregate_rule(rule_rows, "pos_p10")
    adaptive_masscap = aggregate_rule(rule_rows, "adaptive_masscap")
    row = {
        "analysis": str(spec["analysis"]),
        "analysis_dir": str(analysis_dir),
        "observed_mode": str(spec["observed_mode"]),
        "policy_20k": str(spec["policy_20k"]),
        "policy_source": str(spec["policy_source"]),
        "labeled_positive_count": fmt(labeled_positive_count, 1),
        "labeled_negative_count": fmt(labeled_negative_count, 1),
        "labeled_positive_p10": fmt(labeled_positive_p10),
        "labeled_positive_mean": fmt(labeled_positive_mean),
        "labeled_negative_mean": fmt(labeled_negative_mean),
    }
    for key, value in counts.items():
        row[key] = fmt(value, 1)
    row["soft_floor"] = fmt(max(400.0, 40.0 * labeled_positive_count), 1)
    row["threshold_floor"] = fmt(4.0 * labeled_positive_count, 1)
    for rule_data in [pos_min, pos_p10, adaptive_masscap]:
        for key, value in rule_data.items():
            row[key] = value if isinstance(value, str) else fmt(value, 3 if "purity" in key else 1)
    row["current_abs_plateau_branch"] = current_abs_plateau_branch(row)
    row["mass_only_branch"] = mass_only_branch(row)
    row["large_posmin_branch"] = large_posmin_branch(row)
    row["stress_abstain_branch"] = stress_abstain_branch(row)
    return row


def current_abs_plateau_branch(row: dict[str, str]) -> str:
    plateau = safe_float(row["count_ge_0p95"])
    soft_floor = safe_float(row["soft_floor"])
    p10 = safe_float(row["labeled_positive_p10"])
    threshold_floor = safe_float(row["threshold_floor"])
    if plateau >= soft_floor:
        return "soft_weighted"
    if p10 >= 0.85 and plateau >= threshold_floor:
        return "hard_pos_min"
    return "hard_adaptive_masscap"


def mass_only_branch(row: dict[str, str]) -> str:
    mass = safe_float(row["estimated_positive_mass"])
    p10 = safe_float(row["labeled_positive_p10"])
    if mass >= 800.0:
        return "soft_weighted"
    if p10 >= 0.85:
        return "hard_pos_min"
    return "hard_adaptive_masscap"


def large_posmin_branch(row: dict[str, str]) -> str:
    pos_min_count = safe_float(row["count_ge_pos_min"])
    p10 = safe_float(row["labeled_positive_p10"])
    if pos_min_count >= 800.0:
        return "soft_weighted"
    if p10 >= 0.85 and pos_min_count >= 80.0:
        return "hard_pos_min"
    return "hard_adaptive_masscap"


def stress_abstain_branch(row: dict[str, str]) -> str:
    pos_min_count = safe_float(row["count_ge_pos_min"])
    mass = safe_float(row["estimated_positive_mass"])
    p10 = safe_float(row["labeled_positive_p10"])
    if mass >= 800.0 and pos_min_count >= 400.0:
        return "stress_abstain"
    if p10 >= 0.85 and pos_min_count >= 80.0:
        return "hard_pos_min"
    return "hard_adaptive_masscap"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_report(out_dir: Path, rows: list[dict[str, str]]) -> None:
    report = [
        "# Robomimic Router Feature Diagnostics",
        "",
        "This report audits hidden-label-free score-shape features for the hard/soft router.",
        "Hidden labels are used only in audit columns inherited from selector analyses, not in branch decisions.",
        "",
        "## Candidate Branch Rules",
        "",
        "- `current_abs_plateau`: current router; soft if the unlabeled count with score >= 0.95 reaches `max(400, 40 x labeled positives)`.",
        "- `mass_only`: soft if calibrated estimated positive mass is at least 800 demos.",
        "- `large_posmin`: soft if the count above the labeled-positive minimum score is at least 800 demos.",
        "- `stress_abstain`: abstain from choosing hard or soft when calibrated mass is at least 800 and the pos-min count is at least 400; otherwise choose hard support.",
        "",
        "## Score-Shape Features",
        "",
        "| analysis | observed mode | policy 20k | mass | >=0.95 | >=pos_min | pos_min purity | current | mass_only | large_posmin | stress_abstain |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|---|",
    ]
    for row in rows:
        report.append(
            f"| {row['analysis']} | {row['observed_mode']} | {row['policy_20k']} | "
            f"{row['estimated_positive_mass']} | {row['count_ge_0p95']} | "
            f"{row['count_ge_pos_min']} | {row['pos_min_purity']} | "
            f"{row['current_abs_plateau_branch']} | {row['mass_only_branch']} | "
            f"{row['large_posmin_branch']} | {row['stress_abstain_branch']} |"
        )
    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The current absolute-plateau trigger fits the original Can MG row but flips on the shuffled Can MG split.",
            "- A mass-only alternative would mark both Can MG splits as soft-like, but the shuffled seed-0 soft policy is still weak; a large-pos-min alternative keeps the same Can MG branch flip as the current rule.",
            "- The most defensible next method direction is not another fixed threshold; it is an abstention or validation-proxy branch for large bad-dominated MG pools until a stronger policy anchor exists.",
            "- Paired Can and Lift remain the cleaner hard-support evidence. Can MG remains a stress diagnostic for score-to-policy conversion.",
        ]
    )
    (out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = [feature_row(spec) for spec in ANALYSES]
    write_csv(args.out_dir / "feature_summary.csv", rows)
    write_report(args.out_dir, rows)
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
