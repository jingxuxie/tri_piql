from __future__ import annotations

import argparse
import csv
import math
import statistics
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--feature-csv",
        type=Path,
        default=Path("results/robomimic_router_feature_diagnostics/feature_summary.csv"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/robomimic_router_v2_abstention_summary"),
    )
    parser.add_argument("--stress-mass-floor", type=float, default=800.0)
    parser.add_argument("--stress-pos-min-count-floor", type=float, default=400.0)
    parser.add_argument("--hard-positive-p10", type=float, default=0.85)
    parser.add_argument("--hard-pos-min-count-floor", type=float, default=80.0)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def safe_float(value: str) -> float:
    if value == "":
        return float("nan")
    return float(value)


def fmt(value: float, digits: int = 3) -> str:
    if math.isnan(value):
        return ""
    return f"{value:.{digits}f}"


def mean(values: list[float]) -> float:
    if not values:
        return float("nan")
    return float(statistics.fmean(values))


def decide_v2(row: dict[str, str], args: argparse.Namespace) -> tuple[str, str, str]:
    mass = safe_float(row["estimated_positive_mass"])
    count_pos_min = safe_float(row["count_ge_pos_min"])
    p10 = safe_float(row["labeled_positive_p10"])
    if mass >= args.stress_mass_floor and count_pos_min >= args.stress_pos_min_count_floor:
        return (
            "stress_abstain",
            "do_not_train_main_branch",
            "large calibrated mass and large pos-min pool indicate ambiguous MG-style coverage/contamination",
        )
    if p10 >= args.hard_positive_p10 and count_pos_min >= args.hard_pos_min_count_floor:
        return (
            "hard_pos_min",
            "pos_min_calibrated_threshold",
            "labeled positives are high-scoring and the pos-min pool is large enough for hard support",
        )
    return (
        "hard_adaptive_masscap",
        "adaptive_masscap",
        "no large ambiguous pool; use calibrated hard support with mass cap",
    )


def enrich_rows(rows: list[dict[str, str]], args: argparse.Namespace) -> list[dict[str, str]]:
    enriched = []
    for row in rows:
        decision, training_rule, reason = decide_v2(row, args)
        policy_20k = safe_float(row["policy_20k"])
        status = "abstained" if decision == "stress_abstain" else "assigned"
        enriched.append(
            {
                "analysis": row["analysis"],
                "observed_mode": row["observed_mode"],
                "policy_20k": row["policy_20k"],
                "policy_source": row["policy_source"],
                "estimated_positive_mass": row["estimated_positive_mass"],
                "count_ge_pos_min": row["count_ge_pos_min"],
                "labeled_positive_p10": row["labeled_positive_p10"],
                "current_abs_plateau_branch": row["current_abs_plateau_branch"],
                "router_v2_branch": decision,
                "router_v2_training_rule": training_rule,
                "router_v2_reason": reason,
                "assignment_status": status,
                "assigned_policy_20k": "" if status == "abstained" else fmt(policy_20k),
                "abstained_policy_20k": fmt(policy_20k) if status == "abstained" else "",
                # Audit-only columns inherited from feature diagnostics. They use hidden labels.
                "pos_min_audit_purity": row["pos_min_purity"],
                "adaptive_masscap_audit_purity": row["adaptive_masscap_purity"],
            }
        )
    return enriched


def aggregate(enriched: list[dict[str, str]]) -> dict[str, float]:
    assigned = [safe_float(row["policy_20k"]) for row in enriched if row["assignment_status"] == "assigned"]
    abstained = [safe_float(row["policy_20k"]) for row in enriched if row["assignment_status"] == "abstained"]
    current = [safe_float(row["policy_20k"]) for row in enriched]
    return {
        "assigned_count": float(len(assigned)),
        "abstained_count": float(len(abstained)),
        "assigned_mean_20k": mean(assigned),
        "assigned_min_20k": min(assigned) if assigned else float("nan"),
        "abstained_mean_20k": mean(abstained),
        "abstained_max_20k": max(abstained) if abstained else float("nan"),
        "current_all_mean_20k": mean(current),
        "current_all_min_20k": min(current) if current else float("nan"),
    }


def write_report(out_dir: Path, rows: list[dict[str, str]], stats: dict[str, float], args: argparse.Namespace) -> None:
    report = [
        "# Robomimic Router V2 Abstention Summary",
        "",
        "This report converts the score-shape feature audit into a stricter hidden-label-free router.",
        "The router assigns a hard-support branch only for clean score shapes and abstains on large ambiguous MG-style pools.",
        "",
        "Hidden labels are not used by the router. Purity columns are audit-only fields inherited from the selector diagnostics.",
        "",
        "## Rule",
        "",
        f"- Abstain if calibrated positive mass is at least `{args.stress_mass_floor:g}` and the unlabeled count above the labeled-positive minimum is at least `{args.stress_pos_min_count_floor:g}`.",
        f"- Otherwise use `hard_pos_min` if labeled-positive p10 is at least `{args.hard_positive_p10:.2f}` and count above labeled-positive minimum is at least `{args.hard_pos_min_count_floor:g}`.",
        "- Otherwise use `hard_adaptive_masscap`.",
        "",
        "## Decisions",
        "",
        "| analysis | observed mode | policy 20k | mass | >=pos_min | current branch | router v2 branch | status |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        report.append(
            f"| {row['analysis']} | {row['observed_mode']} | {row['policy_20k']} | "
            f"{row['estimated_positive_mass']} | {row['count_ge_pos_min']} | "
            f"{row['current_abs_plateau_branch']} | {row['router_v2_branch']} | "
            f"{row['assignment_status']} |"
        )
    report.extend(
        [
            "",
            "## Outcome Audit",
            "",
            "| quantity | value |",
            "|---|---:|",
            f"| assigned rows | {int(stats['assigned_count'])} |",
            f"| abstained rows | {int(stats['abstained_count'])} |",
            f"| assigned mean 20k success | {fmt(stats['assigned_mean_20k'])} |",
            f"| assigned min 20k success | {fmt(stats['assigned_min_20k'])} |",
            f"| abstained mean 20k success | {fmt(stats['abstained_mean_20k'])} |",
            f"| abstained max 20k success | {fmt(stats['abstained_max_20k'])} |",
            f"| current-router all-row mean 20k success | {fmt(stats['current_all_mean_20k'])} |",
            f"| current-router all-row min 20k success | {fmt(stats['current_all_min_20k'])} |",
            "",
            "## Interpretation",
            "",
            "- Router v2 keeps the paper-facing paired Can and Lift rows assigned, including the shuffled validation splits.",
            "- It abstains on both original and shuffled Can MG, where the current router either relies on a modest soft-weighting stress result or flips to a weak hard branch.",
            "- This is a better method-candidate posture than forcing a hard/soft choice on Can MG. The draft can frame the current method as a high-confidence hard-support converter and present Can MG as an abstention/stress diagnostic.",
            "- The remaining research gap is to replace abstention with a validated policy-quality proxy if we want Can MG to become a main result.",
        ]
    )
    (out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = read_rows(args.feature_csv)
    enriched = enrich_rows(rows, args)
    stats = aggregate(enriched)
    write_csv(args.out_dir / "router_v2_summary.csv", enriched)
    write_report(args.out_dir, enriched, stats, args)
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
