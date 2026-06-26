#!/usr/bin/env python3
"""Summarize Candidate W two-feature initial weighted-rescue gate."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
PER_SEED = ROOT / "results" / "final_paper_v02" / "per_seed"


METHOD_PATHS = {
    "404": {
        "positive": PER_SEED / "can_paired_pos40_bad80_split404_positive_only_nn_policy0" / "eval" / "episode_metrics.csv",
        "weighted": PER_SEED / "can_paired_pos40_bad80_split404_weighted_bc_policy0" / "eval" / "episode_metrics.csv",
        "triage": PER_SEED / "can_paired_pos40_bad80_split404_triage_bc_policy0" / "eval" / "episode_metrics.csv",
        "candidate_e": OUT / "candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng" / "episode_metrics.csv",
        "candidate_v": OUT / "candidate_v_anchor_logprob_can404_w10_e10_eval50" / "episode_metrics.csv",
        "candidate_w": OUT / "candidate_w_two_feature_gate_split404_eval50" / "episode_metrics.csv",
    },
    "505": {
        "positive": PER_SEED / "can_paired_pos40_bad80_split505_positive_only_nn_policy0" / "eval" / "episode_metrics.csv",
        "weighted": PER_SEED / "can_paired_pos40_bad80_split505_weighted_bc_policy0" / "eval" / "episode_metrics.csv",
        "triage": PER_SEED / "can_paired_pos40_bad80_split505_triage_bc_policy0" / "eval" / "episode_metrics.csv",
        "candidate_e": OUT / "candidate_e_initial_posdist_gate_weighted_split505_eval50_isolated_rng" / "episode_metrics.csv",
        "candidate_v": OUT / "candidate_v_anchor_logprob_can505_w10_e10_eval50" / "episode_metrics.csv",
        "candidate_w": OUT / "candidate_w_two_feature_gate_split505_eval50" / "episode_metrics.csv",
    },
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


def aggregate_candidate_w_features(path: Path) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(path):
        grouped[row["initial_demo_id"]].append(row)
    out: dict[str, dict[str, object]] = {}
    for demo_id, rows in grouped.items():
        out[demo_id] = {
            "candidate_w_gate_opens": sum(int(row.get("initial_gate_open", "0")) for row in rows),
            "initial_anchor_pos_dist_mean": f"{sum(float(row['initial_anchor_pos_dist']) for row in rows) / len(rows):.3f}",
            "initial_anchor_neg_dist_mean": f"{sum(float(row['initial_anchor_neg_dist']) for row in rows) / len(rows):.3f}",
            "initial_anchor_margin_mean": f"{sum(float(row['initial_anchor_margin']) for row in rows) / len(rows):.3f}",
        }
    return out


def count_text(pair: tuple[int, int]) -> str:
    return f"{pair[0]}/{pair[1]}"


def count_success(value: str) -> int:
    return int(value.split("/", 1)[0])


def count_episodes(value: str) -> int:
    return int(value.split("/", 1)[1])


def main() -> None:
    rows: list[dict[str, object]] = []
    for split, method_paths in METHOD_PATHS.items():
        method_counts = {method: aggregate_successes(path) for method, path in method_paths.items()}
        features = aggregate_candidate_w_features(method_paths["candidate_w"])
        for demo_id in sorted(method_counts["positive"], key=demo_sort_key):
            positive = method_counts["positive"][demo_id][0]
            weighted = method_counts["weighted"][demo_id][0]
            triage = method_counts["triage"][demo_id][0]
            candidate_e = method_counts["candidate_e"][demo_id][0]
            candidate_v = method_counts["candidate_v"][demo_id][0]
            candidate_w = method_counts["candidate_w"][demo_id][0]
            best_baseline = max(positive, weighted, triage)
            row = {
                "split": split,
                "initial_demo_id": demo_id,
                "positive": count_text(method_counts["positive"][demo_id]),
                "weighted": count_text(method_counts["weighted"][demo_id]),
                "triage": count_text(method_counts["triage"][demo_id]),
                "candidate_e": count_text(method_counts["candidate_e"][demo_id]),
                "candidate_v": count_text(method_counts["candidate_v"][demo_id]),
                "candidate_w": count_text(method_counts["candidate_w"][demo_id]),
                "candidate_w_delta_vs_positive": candidate_w - positive,
                "candidate_w_delta_vs_candidate_e": candidate_w - candidate_e,
                "candidate_w_delta_vs_best_baseline": candidate_w - best_baseline,
                "candidate_w_unique_gain_over_positive": max(0, candidate_w - positive),
                "candidate_w_unique_gain_over_pos_e": max(0, candidate_w - max(positive, candidate_e)),
                "candidate_w_gate_opens": features[demo_id]["candidate_w_gate_opens"],
                "initial_anchor_pos_dist_mean": features[demo_id]["initial_anchor_pos_dist_mean"],
                "initial_anchor_neg_dist_mean": features[demo_id]["initial_anchor_neg_dist_mean"],
                "initial_anchor_margin_mean": features[demo_id]["initial_anchor_margin_mean"],
            }
            rows.append(row)

    summary_rows: list[dict[str, object]] = []
    for split in sorted(METHOD_PATHS):
        split_rows = [row for row in rows if row["split"] == split]
        totals = {}
        for key in ["positive", "weighted", "triage", "candidate_e", "candidate_v", "candidate_w"]:
            totals[key] = (
                f"{sum(count_success(str(row[key])) for row in split_rows)}/"
                f"{sum(count_episodes(str(row[key])) for row in split_rows)}"
            )
        summary_rows.append(
            {
                "split": split,
                **totals,
                "candidate_w_delta_vs_positive": sum(int(row["candidate_w_delta_vs_positive"]) for row in split_rows),
                "candidate_w_delta_vs_candidate_e": sum(int(row["candidate_w_delta_vs_candidate_e"]) for row in split_rows),
                "candidate_w_unique_gain_over_positive": sum(
                    int(row["candidate_w_unique_gain_over_positive"]) for row in split_rows
                ),
                "candidate_w_unique_gain_over_pos_e": sum(
                    int(row["candidate_w_unique_gain_over_pos_e"]) for row in split_rows
                ),
                "candidate_w_gate_opens": sum(int(row["candidate_w_gate_opens"]) for row in split_rows),
            }
        )
    summary_rows.append(
        {
            "split": "total",
            **{
                key: (
                    f"{sum(count_success(str(row[key])) for row in summary_rows)}/"
                    f"{sum(count_episodes(str(row[key])) for row in summary_rows)}"
                )
                for key in ["positive", "weighted", "triage", "candidate_e", "candidate_v", "candidate_w"]
            },
            "candidate_w_delta_vs_positive": sum(int(row["candidate_w_delta_vs_positive"]) for row in rows),
            "candidate_w_delta_vs_candidate_e": sum(int(row["candidate_w_delta_vs_candidate_e"]) for row in rows),
            "candidate_w_unique_gain_over_positive": sum(
                int(row["candidate_w_unique_gain_over_positive"]) for row in rows
            ),
            "candidate_w_unique_gain_over_pos_e": sum(
                int(row["candidate_w_unique_gain_over_pos_e"]) for row in rows
            ),
            "candidate_w_gate_opens": sum(int(row["candidate_w_gate_opens"]) for row in rows),
        }
    )

    per_initial_fields = [
        "split",
        "initial_demo_id",
        "positive",
        "weighted",
        "triage",
        "candidate_e",
        "candidate_v",
        "candidate_w",
        "candidate_w_delta_vs_positive",
        "candidate_w_delta_vs_candidate_e",
        "candidate_w_delta_vs_best_baseline",
        "candidate_w_unique_gain_over_positive",
        "candidate_w_unique_gain_over_pos_e",
        "candidate_w_gate_opens",
        "initial_anchor_pos_dist_mean",
        "initial_anchor_neg_dist_mean",
        "initial_anchor_margin_mean",
    ]
    summary_fields = [
        "split",
        "positive",
        "weighted",
        "triage",
        "candidate_e",
        "candidate_v",
        "candidate_w",
        "candidate_w_delta_vs_positive",
        "candidate_w_delta_vs_candidate_e",
        "candidate_w_unique_gain_over_positive",
        "candidate_w_unique_gain_over_pos_e",
        "candidate_w_gate_opens",
    ]
    per_initial_path = OUT / "candidate_w_two_feature_gate_per_initial.csv"
    summary_path = OUT / "candidate_w_two_feature_gate_summary.csv"
    report_path = OUT / "candidate_w_two_feature_gate_REPORT.md"
    write_csv(per_initial_path, rows, per_initial_fields)
    write_csv(summary_path, summary_rows, summary_fields)

    regressions = sorted(rows, key=lambda row: (int(row["candidate_w_delta_vs_positive"]), int(row["candidate_w_delta_vs_candidate_e"])))[:8]
    gains = [
        row
        for row in sorted(rows, key=lambda row: int(row["candidate_w_unique_gain_over_positive"]), reverse=True)
        if int(row["candidate_w_unique_gain_over_positive"]) > 0
    ]
    gate_rows = [row for row in rows if int(row["candidate_w_gate_opens"]) > 0]
    lines = [
        "# Candidate W Two-Feature Gate",
        "",
        "Candidate W is a frozen deploy-time variant of Candidate E. It uses",
        "positive-only by default and forces weighted BC for the full episode only",
        "when the initial positive-policy action has positive-support distance",
        "`> 3.0` and positive margin over negative support `> 0.0`.",
        "",
        "## Aggregate",
        "",
        *table(summary_rows, summary_fields),
        "",
        "## Gate Open Initials",
        "",
        *table(
            gate_rows,
            [
                "split",
                "initial_demo_id",
                "positive",
                "weighted",
                "candidate_e",
                "candidate_w",
                "candidate_w_gate_opens",
                "initial_anchor_pos_dist_mean",
                "initial_anchor_margin_mean",
            ],
        ),
        "",
        "## Candidate W Regressions",
        "",
        *table(
            regressions,
            [
                "split",
                "initial_demo_id",
                "positive",
                "candidate_e",
                "candidate_w",
                "candidate_w_delta_vs_positive",
                "candidate_w_delta_vs_candidate_e",
                "candidate_w_gate_opens",
            ],
        ),
        "",
        "## Candidate W Gains Over Positive",
        "",
        *table(
            gains,
            [
                "split",
                "initial_demo_id",
                "positive",
                "candidate_e",
                "candidate_w",
                "candidate_w_unique_gain_over_positive",
                "candidate_w_unique_gain_over_pos_e",
                "candidate_w_gate_opens",
            ],
        ),
        "",
        "## Read",
        "",
        "- Candidate W keeps the split-404 `demo_39` rescue and improves split 404",
        "  to `46/50`, matching Candidate E on that split.",
        "- Candidate W closes Candidate E's harmful split-505 `demo_29` gate, but",
        "  still reaches only `39/50` on split 505, below positive-only `40/50`.",
        "- Aggregate Candidate W is `85/100`, tying Candidate E and staying below",
        "  the positive-or-Candidate-E-or-Candidate-V per-initial oracle `93/100`.",
        "- The two-feature gate is therefore a useful diagnostic but not a new",
        "  paper-facing method. The remaining gap requires a more stable",
        "  state-conditional policy-quality signal, not another scalar initial",
        "  support threshold.",
        "",
        "## Artifacts",
        "",
        f"- Per-initial CSV: `{per_initial_path.relative_to(ROOT)}`.",
        f"- Summary CSV: `{summary_path.relative_to(ROOT)}`.",
        "- Split-404 eval: `results/candidate_breakthrough/candidate_w_two_feature_gate_split404_eval50/REPORT.md`.",
        "- Split-505 eval: `results/candidate_breakthrough/candidate_w_two_feature_gate_split505_eval50/REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
