#!/usr/bin/env python3
"""Analyze Candidate V per-initial failures against baselines."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
PER_SEED = ROOT / "results" / "final_paper_v02" / "per_seed"


METHOD_PATHS = {
    "404": {
        "positive": PER_SEED
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "weighted": PER_SEED
        / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        "triage": PER_SEED
        / "can_paired_pos40_bad80_split404_triage_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        "candidate_e": OUT / "candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng" / "episode_metrics.csv",
        "candidate_v": OUT / "candidate_v_anchor_logprob_can404_w10_e10_eval50" / "episode_metrics.csv",
    },
    "505": {
        "positive": PER_SEED
        / "can_paired_pos40_bad80_split505_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "weighted": PER_SEED
        / "can_paired_pos40_bad80_split505_weighted_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        "triage": PER_SEED
        / "can_paired_pos40_bad80_split505_triage_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        "candidate_e": OUT / "candidate_e_initial_posdist_gate_weighted_split505_eval50_isolated_rng" / "episode_metrics.csv",
        "candidate_v": OUT / "candidate_v_anchor_logprob_can505_w10_e10_eval50" / "episode_metrics.csv",
    },
}

FEATURE_PATHS = {
    "404": OUT / "candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng" / "episode_metrics.csv",
    "505": OUT / "candidate_e_initial_posdist_gate_weighted_split505_eval50_isolated_rng" / "episode_metrics.csv",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def aggregate_successes(path: Path) -> dict[str, tuple[int, int]]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for row in read_csv(path):
        grouped[row["initial_demo_id"]].append(int(float(row["success"])))
    return {demo_id: (sum(values), len(values)) for demo_id, values in grouped.items()}


def aggregate_features(path: Path) -> dict[str, dict[str, object]]:
    rows = read_csv(path)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["initial_demo_id"]].append(row)
    out: dict[str, dict[str, object]] = {}
    for demo_id, demo_rows in grouped.items():
        if "initial_anchor_pos_dist" not in demo_rows[0]:
            continue
        out[demo_id] = {
            "candidate_e_gate_opens": sum(int(row.get("initial_gate_open", "0")) for row in demo_rows),
            "initial_anchor_pos_dist_mean": f"{sum(float(row['initial_anchor_pos_dist']) for row in demo_rows) / len(demo_rows):.3f}",
            "initial_anchor_margin_mean": f"{sum(float(row['initial_anchor_margin']) for row in demo_rows) / len(demo_rows):.3f}",
        }
    return out


def count_text(pair: tuple[int, int]) -> str:
    return f"{pair[0]}/{pair[1]}"


def main() -> None:
    rows: list[dict[str, object]] = []
    for split, method_paths in METHOD_PATHS.items():
        method_counts = {method: aggregate_successes(path) for method, path in method_paths.items()}
        features = aggregate_features(FEATURE_PATHS[split])
        initial_ids = sorted(method_counts["positive"], key=demo_sort_key)
        for demo_id in initial_ids:
            positive = method_counts["positive"][demo_id][0]
            weighted = method_counts["weighted"][demo_id][0]
            triage = method_counts["triage"][demo_id][0]
            candidate_e = method_counts["candidate_e"][demo_id][0]
            candidate_v = method_counts["candidate_v"][demo_id][0]
            best_baseline = max(positive, weighted, triage)
            oracle_pos_v = max(positive, candidate_v)
            oracle_pos_e_v = max(positive, candidate_e, candidate_v)
            row = {
                "split": split,
                "initial_demo_id": demo_id,
                "positive": count_text(method_counts["positive"][demo_id]),
                "weighted": count_text(method_counts["weighted"][demo_id]),
                "triage": count_text(method_counts["triage"][demo_id]),
                "candidate_e": count_text(method_counts["candidate_e"][demo_id]),
                "candidate_v": count_text(method_counts["candidate_v"][demo_id]),
                "candidate_v_delta_vs_positive": candidate_v - positive,
                "candidate_v_delta_vs_best_baseline": candidate_v - best_baseline,
                "candidate_v_unique_gain_over_positive": max(0, candidate_v - positive),
                "candidate_v_unique_gain_over_pos_e": max(0, candidate_v - max(positive, candidate_e)),
                "oracle_positive_v": f"{oracle_pos_v}/5",
                "oracle_positive_e_v": f"{oracle_pos_e_v}/5",
                "candidate_e_gate_opens": features.get(demo_id, {}).get("candidate_e_gate_opens", ""),
                "initial_anchor_pos_dist_mean": features.get(demo_id, {}).get("initial_anchor_pos_dist_mean", ""),
                "initial_anchor_margin_mean": features.get(demo_id, {}).get("initial_anchor_margin_mean", ""),
            }
            rows.append(row)

    summary_rows: list[dict[str, object]] = []
    for split in sorted(METHOD_PATHS):
        split_rows = [row for row in rows if row["split"] == split]
        totals = {}
        for key in ["positive", "weighted", "triage", "candidate_e", "candidate_v", "oracle_positive_v", "oracle_positive_e_v"]:
            successes = sum(int(str(row[key]).split("/")[0]) for row in split_rows)
            episodes = sum(int(str(row[key]).split("/")[1]) for row in split_rows)
            totals[key] = f"{successes}/{episodes}"
        summary_rows.append(
            {
                "split": split,
                **totals,
                "candidate_v_delta_vs_positive": sum(int(row["candidate_v_delta_vs_positive"]) for row in split_rows),
                "candidate_v_unique_gain_over_positive": sum(
                    int(row["candidate_v_unique_gain_over_positive"]) for row in split_rows
                ),
                "candidate_v_unique_gain_over_pos_e": sum(
                    int(row["candidate_v_unique_gain_over_pos_e"]) for row in split_rows
                ),
            }
        )
    total_rows = rows
    summary_rows.append(
        {
            "split": "total",
            **{
                key: f"{sum(int(str(row[key]).split('/')[0]) for row in summary_rows)}/"
                f"{sum(int(str(row[key]).split('/')[1]) for row in summary_rows)}"
                for key in ["positive", "weighted", "triage", "candidate_e", "candidate_v", "oracle_positive_v", "oracle_positive_e_v"]
            },
            "candidate_v_delta_vs_positive": sum(int(row["candidate_v_delta_vs_positive"]) for row in total_rows),
            "candidate_v_unique_gain_over_positive": sum(
                int(row["candidate_v_unique_gain_over_positive"]) for row in total_rows
            ),
            "candidate_v_unique_gain_over_pos_e": sum(int(row["candidate_v_unique_gain_over_pos_e"]) for row in total_rows),
        }
    )

    per_initial_path = OUT / "candidate_v_failure_analysis_per_initial.csv"
    summary_path = OUT / "candidate_v_failure_analysis_summary.csv"
    report_path = OUT / "candidate_v_failure_analysis_REPORT.md"
    per_initial_fields = [
        "split",
        "initial_demo_id",
        "positive",
        "weighted",
        "triage",
        "candidate_e",
        "candidate_v",
        "candidate_v_delta_vs_positive",
        "candidate_v_delta_vs_best_baseline",
        "candidate_v_unique_gain_over_positive",
        "candidate_v_unique_gain_over_pos_e",
        "oracle_positive_v",
        "oracle_positive_e_v",
        "candidate_e_gate_opens",
        "initial_anchor_pos_dist_mean",
        "initial_anchor_margin_mean",
    ]
    summary_fields = [
        "split",
        "positive",
        "weighted",
        "triage",
        "candidate_e",
        "candidate_v",
        "oracle_positive_v",
        "oracle_positive_e_v",
        "candidate_v_delta_vs_positive",
        "candidate_v_unique_gain_over_positive",
        "candidate_v_unique_gain_over_pos_e",
    ]
    write_csv(per_initial_path, rows, per_initial_fields)
    write_csv(summary_path, summary_rows, summary_fields)

    worst_v_rows = sorted(rows, key=lambda row: int(row["candidate_v_delta_vs_positive"]))[:6]
    gain_rows = [
        row
        for row in sorted(rows, key=lambda row: int(row["candidate_v_unique_gain_over_positive"]), reverse=True)
        if int(row["candidate_v_unique_gain_over_positive"]) > 0
    ]
    lines = [
        "# Candidate V Failure Analysis",
        "",
        "This report compares Candidate V against positive-only, weighted BC, triage,",
        "and the Candidate E router by held-out initial state on Can splits 404 and",
        "505. Counts are successes over the 5 repeated rollouts for each validation",
        "initial.",
        "",
        "## Aggregate",
        "",
        *table(summary_rows, summary_fields),
        "",
        "## Worst Candidate V Regressions",
        "",
        *table(
            worst_v_rows,
            [
                "split",
                "initial_demo_id",
                "positive",
                "candidate_e",
                "candidate_v",
                "candidate_v_delta_vs_positive",
                "initial_anchor_pos_dist_mean",
                "candidate_e_gate_opens",
            ],
        ),
        "",
        "## Candidate V Unique Gains Over Positive",
        "",
        *table(
            gain_rows,
            [
                "split",
                "initial_demo_id",
                "positive",
                "candidate_e",
                "candidate_v",
                "candidate_v_unique_gain_over_positive",
                "candidate_v_unique_gain_over_pos_e",
                "initial_anchor_pos_dist_mean",
            ],
        ),
        "",
        "## Read",
        "",
        "- Candidate V does not solve the split-404 `demo_39` coverage gap: it is",
        "  `0/5`, while Candidate E routes that initial to weighted BC and reaches",
        "  `5/5`.",
        "- Candidate V's aggregate unique gain over positive-only is small and is",
        "  not unique once Candidate E is available.",
        "- The split-505 validation failure is concentrated in recurring anchor",
        "  regressions, especially `demo_89`, where Candidate V is `0/5`.",
        "- This supports stopping Candidate V unchanged. The core unsolved problem",
        "  is not just preserving log-probability on high-weight training timesteps;",
        "  it is identifying state-specific weighted-coverage rescue cases without",
        "  damaging strong positive anchors.",
        "",
        "## Artifacts",
        "",
        f"- Per-initial CSV: `{per_initial_path.relative_to(ROOT)}`.",
        f"- Summary CSV: `{summary_path.relative_to(ROOT)}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
