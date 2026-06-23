from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


DEFAULT_ANALYSES = [
    (
        "can_paired_80p80b",
        Path("results/robomimic_selector_score_analysis_balanced_80p80b"),
        "hard_coverage",
        "coverage-aware score-gap is the best fixed-20k policy row",
    ),
    (
        "can_paired_40p80b",
        Path("results/robomimic_selector_score_analysis_pos40_bad80"),
        "hard_mass_capped",
        "mass-capped support is best at fixed 15k/20k",
    ),
    (
        "can_paired_20p80b",
        Path("results/robomimic_selector_score_analysis_stress_p20_b80"),
        "hard_precision",
        "top20 precision branch is best at fixed 20k",
    ),
    (
        "lift_mg_sparse",
        Path("results/robomimic_lift_mg_selector_score_analysis"),
        "hard_threshold",
        "pos-min hard support is best at fixed 20k",
    ),
    (
        "can_mg_sparse",
        Path("results/robomimic_selector_score_analysis_can_mg"),
        "soft_weighting",
        "weighted sampler is the best matched three-seed fixed-20k control but remains diagnostic",
    ),
]


POLICY_ROWS = [
    {
        "analysis": "can_paired_80p80b",
        "best_hard_method": "coverage-aware score-gap",
        "best_hard_20k": "0.900",
        "soft_weighted_20k": "",
        "all_demo_20k": "",
        "oracle_positive_20k": "",
        "source": "results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_paired_40p80b",
        "best_hard_method": "mass-capped adaptive",
        "best_hard_20k": "0.733",
        "soft_weighted_20k": "0.567",
        "all_demo_20k": "",
        "oracle_positive_20k": "",
        "source": "results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_paired_20p80b",
        "best_hard_method": "top20 precision",
        "best_hard_20k": "0.667",
        "soft_weighted_20k": "",
        "all_demo_20k": "",
        "oracle_positive_20k": "",
        "source": "results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md",
    },
    {
        "analysis": "lift_mg_sparse",
        "best_hard_method": "pos-min calibrated threshold",
        "best_hard_20k": "0.667",
        "soft_weighted_20k": "0.533",
        "all_demo_20k": "0.200",
        "oracle_positive_20k": "0.633",
        "source": "results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md",
    },
    {
        "analysis": "can_mg_sparse",
        "best_hard_method": "pos-p10 calibrated threshold",
        "best_hard_20k": "0.167",
        "soft_weighted_20k": "0.333",
        "all_demo_20k": "0.100",
        "oracle_positive_20k": "0.200",
        "source": "results/robomimic_can_mg_official_bc_rnn_controls_3seed_summary/REPORT.md",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_hard_soft_tradeoff_summary"))
    parser.add_argument(
        "--plateau-score-threshold",
        type=float,
        default=0.95,
        help="Score floor used to count high-confidence unlabeled plateau demos.",
    )
    parser.add_argument(
        "--soft-plateau-count",
        type=int,
        default=400,
        help="Mean number of high-confidence plateau demos above which soft weighting is recommended.",
    )
    parser.add_argument(
        "--hard-purity-floor",
        type=float,
        default=0.70,
        help="Support-analysis purity floor used for the candidate hard/soft recommendation.",
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(statistics.fmean(values))


def mean_int(values: list[float]) -> float:
    return round(mean(values), 1)


def rows_for(rows: list[dict[str, str]], key: str, value: str) -> list[dict[str, str]]:
    return [row for row in rows if row[key] == value]


def aggregate_rule(rows: list[dict[str, str]], threshold_name: str) -> dict[str, str]:
    selected = rows_for(rows, "threshold_name", threshold_name)
    if not selected:
        return {
            "rule": "",
            "selected": "",
            "hidden_positive": "",
            "hidden_bad": "",
            "purity": "",
            "mode": "",
        }
    rules = sorted({row["rule"] for row in selected})
    return {
        "rule": threshold_name,
        "selected": f"{mean_int([float(row['selected_demo_count']) for row in selected]):.1f}",
        "hidden_positive": f"{mean_int([float(row['selected_hidden_positive_demos']) for row in selected]):.1f}",
        "hidden_bad": f"{mean_int([float(row['selected_hidden_bad_demos']) for row in selected]):.1f}",
        "purity": f"{mean([float(row['selected_hidden_positive_purity']) for row in selected]):.3f}",
        "mode": ",".join(rules),
    }


def aggregate_precision(precision_rows: list[dict[str, str]], k: int) -> dict[str, float]:
    selected = [row for row in precision_rows if int(row["k"]) == k]
    return {
        "selected": mean([float(row["selected_demo_count"]) for row in selected]),
        "hidden_positive": mean([float(row["selected_hidden_positive_demos"]) for row in selected]),
        "hidden_bad": mean([float(row["selected_hidden_bad_demos"]) for row in selected]),
        "purity": mean([float(row["selected_hidden_positive_purity"]) for row in selected]),
        "score_min": mean([float(row["selected_score_min"]) for row in selected]),
        "score_mean": mean([float(row["selected_score_mean"]) for row in selected]),
    }


def plateau_count(rank_rows: list[dict[str, str]], threshold: float) -> float:
    counts_by_seed: dict[int, int] = {}
    for row in rank_rows:
        seed = int(row["seed"])
        counts_by_seed.setdefault(seed, 0)
        if float(row["score"]) >= threshold:
            counts_by_seed[seed] += 1
    return mean([float(value) for value in counts_by_seed.values()])


def best_pure_prefix(precision_rows: list[dict[str, str]], purity_floor: float) -> tuple[int, float]:
    by_k = sorted({int(row["k"]) for row in precision_rows})
    best_k = 0
    best_purity = float("nan")
    for k in by_k:
        agg = aggregate_precision(precision_rows, k)
        if agg["purity"] >= purity_floor:
            best_k = k
            best_purity = agg["purity"]
    return best_k, best_purity


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def recommendation(
    *,
    plateau_mean: float,
    best_hard_k: int,
    best_hard_purity: float,
    soft_plateau_count: int,
    hard_purity_floor: float,
) -> tuple[str, str]:
    if plateau_mean >= soft_plateau_count and best_hard_k < 0.5 * plateau_mean:
        return (
            "soft_weighting_candidate",
            "large high-score plateau but the clean hard prefix is much smaller than the plateau",
        )
    if best_hard_purity >= hard_purity_floor and best_hard_k > 0:
        return (
            "hard_support_candidate",
            "there is a sufficiently pure high-score prefix for support selection",
        )
    return (
        "ambiguous_candidate",
        "support frontier is not clean enough for a hard-only or soft-only decision",
    )


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    diagnostic_rows: list[dict[str, str]] = []
    rule_rows: list[dict[str, str]] = []
    for analysis_name, analysis_dir, observed_policy_mode, policy_note in DEFAULT_ANALYSES:
        selection_rows = read_rows(analysis_dir / "selection_rules.csv")
        precision_rows = read_rows(analysis_dir / "precision_at_k.csv")
        rank_rows = read_rows(analysis_dir / "demo_rankings.csv")

        plateau_mean = plateau_count(rank_rows, args.plateau_score_threshold)
        best_k, best_purity = best_pure_prefix(precision_rows, args.hard_purity_floor)
        top20 = aggregate_precision(precision_rows, 20)
        top80 = aggregate_precision(precision_rows, 80)
        available_ks = sorted({int(row["k"]) for row in precision_rows})
        wide_k = 320 if 320 in available_ks else max(available_ks)
        wide = aggregate_precision(precision_rows, wide_k)
        candidate_mode, candidate_reason = recommendation(
            plateau_mean=plateau_mean,
            best_hard_k=best_k,
            best_hard_purity=best_purity,
            soft_plateau_count=args.soft_plateau_count,
            hard_purity_floor=args.hard_purity_floor,
        )

        diagnostic_rows.append(
            {
                "analysis": analysis_name,
                "observed_policy_mode": observed_policy_mode,
                "candidate_mode_from_support": candidate_mode,
                "candidate_reason": candidate_reason,
                "plateau_score_threshold": f"{args.plateau_score_threshold:.2f}",
                "mean_plateau_demo_count": f"{plateau_mean:.1f}",
                "best_prefix_k_at_purity_floor": str(best_k),
                "best_prefix_purity": f"{best_purity:.3f}" if best_k else "",
                "top20_purity": f"{top20['purity']:.3f}",
                "top20_hidden_positive": f"{top20['hidden_positive']:.1f}",
                "top80_purity": f"{top80['purity']:.3f}",
                "top80_hidden_positive": f"{top80['hidden_positive']:.1f}",
                "wide_prefix_k": str(wide_k),
                "wide_prefix_purity": f"{wide['purity']:.3f}",
                "wide_prefix_hidden_positive": f"{wide['hidden_positive']:.1f}",
                "policy_note": policy_note,
                "analysis_dir": str(analysis_dir),
            }
        )

        for rule_name in ["adaptive_masscap", "score_gap_posx", "pos_min", "pos_p10", "top_posx2"]:
            agg = aggregate_rule(selection_rows, rule_name)
            if agg["rule"]:
                rule_rows.append({"analysis": analysis_name, **agg})

    write_csv(args.out_dir / "diagnostic_summary.csv", diagnostic_rows)
    write_csv(args.out_dir / "rule_summary.csv", rule_rows)
    write_csv(args.out_dir / "policy_anchor_summary.csv", POLICY_ROWS)

    report = [
        "# Robomimic Hard-vs-Soft Score Conversion Diagnostic",
        "",
        "This support-only diagnostic consolidates the existing selector-score analyses. It does not use new policy training.",
        "",
        "The purpose is to turn the weighted-BC baseline result into a method question: when should the classifier score become hard selected support, and when should it remain a soft sampling weight?",
        "",
        "## Files",
        "",
        "- `diagnostic_summary.csv`: one row per split with support-frontier features and a candidate hard/soft recommendation.",
        "- `rule_summary.csv`: aggregate composition for existing threshold and adaptive rules.",
        "- `policy_anchor_summary.csv`: fixed-20k policy anchors from the current reports.",
        "",
        "## Candidate Rule",
        "",
        f"- Count the mean number of unlabeled demos with trajectory score at least `{args.plateau_score_threshold:.2f}`.",
        f"- Find the largest top-k prefix with mean hidden-positive purity at least `{args.hard_purity_floor:.2f}` in the support diagnostic.",
        f"- If the high-score plateau is at least `{args.soft_plateau_count}` demos but the largest clean prefix is less than half of that plateau, mark the split as a soft-weighting candidate.",
        "- Otherwise, if a clean prefix exists, mark the split as a hard-support candidate.",
        "",
        "The support purity part uses hidden labels for diagnosis only. A final algorithm should replace it with a hidden-label-free proxy such as score-plateau length, score curvature, validation likelihood on labeled positives, or a predeclared purity model.",
        "",
        "## Summary",
        "",
        "| analysis | observed policy mode | support candidate | score>=0.95 demos | best clean k | top20 purity | top80 purity | note |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in diagnostic_rows:
        report.append(
            f"| {row['analysis']} | {row['observed_policy_mode']} | {row['candidate_mode_from_support']} | "
            f"{row['mean_plateau_demo_count']} | {row['best_prefix_k_at_purity_floor']} | "
            f"{row['top20_purity']} | {row['top80_purity']} | {row['policy_note']} |"
        )
    report.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Paired Can and Lift have clean enough high-score prefixes to support hard selected training data.",
            "- Can MG has a much larger high-score plateau and purity decays only as support gets broad; the matched three-seed controls make soft weighting the best fixed-20k row, but the absolute success remains modest.",
            "- A hidden-label-free router candidate that removes the diagnostic purity term is summarized in `results/robomimic_hidden_free_router_summary/REPORT.md`.",
            "- This reframes weighted BC as a branch of the method family rather than a weak baseline. The next method step is to freeze and validate the hidden-label-free hard/soft router.",
        ]
    )
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
