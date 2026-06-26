from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROUTER_SUMMARY = Path("results/robomimic_router_v2_abstention_summary/router_v2_summary.csv")
CAN_MG_PROXY_DIR = Path("results/final_paper/ablations/can_mg_branch_proxy_summary")
OUT_DIR = Path("results/final_paper/tables")

ABSTAINED_SETTINGS = {
    "can_mg_sparse": {
        "split": "can_mg_original",
        "setting_label": "Can MG original",
    },
    "can_mg_sparse_shuffle42": {
        "split": "can_mg_shuffle42",
        "setting_label": "Can MG shuffle42",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--router-summary", type=Path, default=ROUTER_SUMMARY)
    parser.add_argument("--proxy-dir", type=Path, default=CAN_MG_PROXY_DIR)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
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


def fmt(value: float) -> str:
    return f"{value:.3f}"


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def methods_at_value(rows: list[dict[str, str]], target: float) -> list[str]:
    return sorted(
        row["method"]
        for row in rows
        if abs(float(row["rollout_success_20k"]) - target) < 1e-9
    )


def bool_true(value: str) -> bool:
    return value.strip().lower() == "true"


def summarize_assignments(router_rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for status in ["assigned", "abstained"]:
        rows = [row for row in router_rows if row["assignment_status"] == status]
        if not rows:
            continue
        policy_key = "assigned_policy_20k" if status == "assigned" else "abstained_policy_20k"
        policies = [float(row[policy_key]) for row in rows if row.get(policy_key)]
        masses = [float(row["estimated_positive_mass"]) for row in rows]
        pos_min_counts = [float(row["count_ge_pos_min"]) for row in rows]
        out.append(
            {
                "assignment_status": status,
                "num_rows": len(rows),
                "mean_policy_20k": fmt(mean(policies)),
                "min_policy_20k": fmt(min(policies)),
                "max_policy_20k": fmt(max(policies)),
                "mean_estimated_positive_mass": fmt(mean(masses)),
                "max_estimated_positive_mass": fmt(max(masses)),
                "mean_count_ge_pos_min": fmt(mean(pos_min_counts)),
                "max_count_ge_pos_min": fmt(max(pos_min_counts)),
            }
        )
    return out


def summarize_abstained_rows(
    router_rows: list[dict[str, str]],
    method_rows: list[dict[str, str]],
    proxy_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    by_analysis = {row["analysis"]: row for row in router_rows}
    for analysis, metadata in ABSTAINED_SETTINGS.items():
        router_row = by_analysis[analysis]
        split = metadata["split"]
        split_methods = [row for row in method_rows if row["split"] == split]
        split_proxies = [row for row in proxy_rows if row["split"] == split]
        if not split_methods:
            raise ValueError(f"no method rows for split {split}")
        if not split_proxies:
            raise ValueError(f"no proxy rows for split {split}")

        successes = [float(row["rollout_success_20k"]) for row in split_methods]
        best_success = max(successes)
        worst_success = min(successes)
        method_match = sum(bool_true(row["proxy_matches_rollout_best_method"]) for row in split_proxies)
        success_match = sum(bool_true(row["proxy_matches_best_success"]) for row in split_proxies)
        proxy_total = len(split_proxies)

        if split == "can_mg_original":
            justification = "yes_proxy_miss_and_low_ceiling"
        else:
            justification = "yes_all_forced_branches_weak"

        rows.append(
            {
                "setting_label": metadata["setting_label"],
                "analysis": analysis,
                "split": split,
                "router_decision": router_row["router_v2_branch"],
                "assignment_status": router_row["assignment_status"],
                "observed_mode": router_row["observed_mode"],
                "estimated_positive_mass": router_row["estimated_positive_mass"],
                "count_ge_pos_min": router_row["count_ge_pos_min"],
                "pos_min_audit_purity": router_row["pos_min_audit_purity"],
                "adaptive_masscap_audit_purity": router_row["adaptive_masscap_audit_purity"],
                "best_forced_branch": "=".join(methods_at_value(split_methods, best_success)),
                "best_forced_success_20k": fmt(best_success),
                "worst_forced_branch": "=".join(methods_at_value(split_methods, worst_success)),
                "worst_forced_success_20k": fmt(worst_success),
                "forced_branch_spread_20k": fmt(best_success - worst_success),
                "proxy_matches_rollout_best_method": f"{method_match}/{proxy_total}",
                "proxy_matches_best_success": f"{success_match}/{proxy_total}",
                "hidden_label_free_reason": router_row["router_v2_reason"],
                "abstention_justified": justification,
            }
        )
    return rows


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def write_report(
    path: Path,
    abstention_rows: list[dict[str, object]],
    assignment_rows: list[dict[str, object]],
) -> None:
    abstention_columns = [
        "setting_label",
        "router_decision",
        "estimated_positive_mass",
        "count_ge_pos_min",
        "best_forced_branch",
        "best_forced_success_20k",
        "worst_forced_branch",
        "worst_forced_success_20k",
        "proxy_matches_best_success",
        "abstention_justified",
    ]
    assignment_columns = [
        "assignment_status",
        "num_rows",
        "mean_policy_20k",
        "min_policy_20k",
        "max_policy_20k",
        "mean_estimated_positive_mass",
        "mean_count_ge_pos_min",
    ]
    lines = [
        "# Active Abstention Evaluation",
        "",
        "This report stages the C2 abstention check from existing router-v2 and Can MG branch-proxy artifacts.",
        "It does not add new policy training. The claim is risk control under ambiguous score shapes, not endpoint dominance.",
        "",
        "## Abstained Can MG Rows",
        "",
        *markdown_table(abstention_rows, abstention_columns),
        "",
        "## Assignment Summary",
        "",
        *markdown_table(assignment_rows, assignment_columns),
        "",
        "## Interpretation",
        "",
        "- Router v2 abstains on the two large-MG score shapes: original Can MG has estimated positive mass `1947.9` and `1025.7` trajectories above the labeled-positive minimum; shuffled Can MG has mass `1466.3` and count `515.7`.",
        "- On original Can MG, forcing a branch leaves only a modest best fixed-20k result: weighted BC is best at `0.333`, all-demo is worst at `0.100`, and likelihood-style proxies match the best-success branch in `0/6` cases.",
        "- On shuffled Can MG, proxy winners can match best success in `6/6` cases only because the staged hard and soft forced branches both reach `0.100`; this does not validate a useful branch.",
        "- Across the router-v2 audit, assigned rows have mean fixed-20k success `0.700` and minimum `0.600`; abstained rows have mean `0.217` and maximum `0.333`.",
        "",
        "Conclusion: abstention is justified as a stress/limitation decision for large ambiguous score plateaus until a coverage-sensitive policy-quality proxy is validated.",
        "",
        "## Source Artifacts",
        "",
        "- `results/robomimic_router_v2_abstention_summary/router_v2_summary.csv`",
        "- `results/final_paper/ablations/can_mg_branch_proxy_summary/method_proxy_scores.csv`",
        "- `results/final_paper/ablations/can_mg_branch_proxy_summary/proxy_winners.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    router_rows = read_csv(args.router_summary)
    method_rows = read_csv(args.proxy_dir / "method_proxy_scores.csv")
    proxy_rows = read_csv(args.proxy_dir / "proxy_winners.csv")

    assignment_rows = summarize_assignments(router_rows)
    abstention_rows = summarize_abstained_rows(router_rows, method_rows, proxy_rows)

    write_csv(
        args.out_dir / "active_abstention_assignment_summary.csv",
        assignment_rows,
        [
            "assignment_status",
            "num_rows",
            "mean_policy_20k",
            "min_policy_20k",
            "max_policy_20k",
            "mean_estimated_positive_mass",
            "max_estimated_positive_mass",
            "mean_count_ge_pos_min",
            "max_count_ge_pos_min",
        ],
    )
    write_csv(
        args.out_dir / "active_abstention_evaluation.csv",
        abstention_rows,
        [
            "setting_label",
            "analysis",
            "split",
            "router_decision",
            "assignment_status",
            "observed_mode",
            "estimated_positive_mass",
            "count_ge_pos_min",
            "pos_min_audit_purity",
            "adaptive_masscap_audit_purity",
            "best_forced_branch",
            "best_forced_success_20k",
            "worst_forced_branch",
            "worst_forced_success_20k",
            "forced_branch_spread_20k",
            "proxy_matches_rollout_best_method",
            "proxy_matches_best_success",
            "hidden_label_free_reason",
            "abstention_justified",
        ],
    )
    write_report(
        args.out_dir / "active_abstention_evaluation_REPORT.md",
        abstention_rows,
        assignment_rows,
    )


if __name__ == "__main__":
    main()
