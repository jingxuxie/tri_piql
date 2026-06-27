#!/usr/bin/env python3
"""Summarize five-split CAU-alone Can endpoint evidence."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(".")
OUT_DIR = ROOT / "results" / "sota_candidate"
V02_CAN_SUMMARY = ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_can_endpoint_summary.csv"
SPLITS = (101, 202, 303, 404, 505)
CAU_METRICS = {
    split: OUT_DIR / f"cau_action_conflict_can{split}_b005_m05_eval50" / "metrics.csv"
    for split in SPLITS
}
CAU_REPORTS = {
    split: OUT_DIR / f"cau_action_conflict_can{split}_b005_m05_eval50" / "REPORT.md"
    for split in SPLITS
}
METHODS = (
    "cau_action_conflict",
    "positive_only_nn",
    "weighted_bc",
    "triage_bc",
    "positive_nn_risk_union_top40",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def metric_success(path: Path) -> tuple[int, int, float]:
    rows = read_csv(path)
    if len(rows) != 1:
        raise AssertionError(f"expected one metric row in {path}, found {len(rows)}")
    row = rows[0]
    episodes = int(row["eval_episodes"])
    rate = float(row["success_rate"])
    successes = round(rate * episodes)
    return int(successes), episodes, float(row["avg_len"])


def by_split_method(rows: list[dict[str, str]]) -> dict[tuple[int, str], dict[str, str]]:
    out = {}
    for row in rows:
        out[(int(row["split_seed"]), row["method_id"])] = row
    return out


def score(successes: int, episodes: int) -> str:
    return f"{successes}/{episodes}"


def main() -> None:
    v02_rows = by_split_method(read_csv(V02_CAN_SUMMARY))
    rows: list[dict[str, object]] = []
    per_split_best_old = 0
    per_split_best_non_oracle = 0

    for split in SPLITS:
        cau_success, cau_episodes, cau_avg_len = metric_success(CAU_METRICS[split])
        positive = v02_rows[(split, "positive_only_nn")]
        weighted = v02_rows[(split, "weighted_bc")]
        triage = v02_rows[(split, "triage_bc")]
        v02_selected = v02_rows[(split, "positive_nn_risk_union_top40")]
        old_baseline_successes = [
            int(positive["success_count"]),
            int(weighted["success_count"]),
            int(triage["success_count"]),
        ]
        best_old = max(old_baseline_successes)
        best_non_oracle = max(best_old, int(v02_selected["success_count"]))
        per_split_best_old += best_old
        per_split_best_non_oracle += best_non_oracle
        rows.append(
            {
                "split_seed": split,
                "cau_successes": cau_success,
                "eval_episodes": cau_episodes,
                "positive_only_successes": positive["success_count"],
                "weighted_bc_successes": weighted["success_count"],
                "triage_bc_successes": triage["success_count"],
                "v02_selected_successes": v02_selected["success_count"],
                "best_old_baseline_successes": best_old,
                "best_non_oracle_successes": best_non_oracle,
                "delta_vs_positive_only": cau_success - int(positive["success_count"]),
                "delta_vs_best_old_baseline": cau_success - best_old,
                "delta_vs_v02_selected": cau_success - int(v02_selected["success_count"]),
                "delta_vs_best_non_oracle": cau_success - best_non_oracle,
                "cau_avg_len": f"{cau_avg_len:.1f}",
                "cau_report": str(CAU_REPORTS[split]),
            }
        )

    totals = {
        method: 0
        for method in METHODS
    }
    for split in SPLITS:
        totals["cau_action_conflict"] += next(row["cau_successes"] for row in rows if row["split_seed"] == split)
        for method in METHODS[1:]:
            totals[method] += int(v02_rows[(split, method)]["success_count"])
    episodes = sum(int(row["eval_episodes"]) for row in rows)

    summary_rows = [
        {
            "method_id": "cau_action_conflict",
            "successes": totals["cau_action_conflict"],
            "eval_episodes": episodes,
            "delta_vs_cau": 0,
        },
        {
            "method_id": "positive_only_nn",
            "successes": totals["positive_only_nn"],
            "eval_episodes": episodes,
            "delta_vs_cau": totals["positive_only_nn"] - totals["cau_action_conflict"],
        },
        {
            "method_id": "weighted_bc",
            "successes": totals["weighted_bc"],
            "eval_episodes": episodes,
            "delta_vs_cau": totals["weighted_bc"] - totals["cau_action_conflict"],
        },
        {
            "method_id": "triage_bc_v01",
            "successes": totals["triage_bc"],
            "eval_episodes": episodes,
            "delta_vs_cau": totals["triage_bc"] - totals["cau_action_conflict"],
        },
        {
            "method_id": "best_old_baseline_per_split",
            "successes": per_split_best_old,
            "eval_episodes": episodes,
            "delta_vs_cau": per_split_best_old - totals["cau_action_conflict"],
        },
        {
            "method_id": "v02_selected_union",
            "successes": totals["positive_nn_risk_union_top40"],
            "eval_episodes": episodes,
            "delta_vs_cau": totals["positive_nn_risk_union_top40"] - totals["cau_action_conflict"],
        },
        {
            "method_id": "best_non_oracle_per_split",
            "successes": per_split_best_non_oracle,
            "eval_episodes": episodes,
            "delta_vs_cau": per_split_best_non_oracle - totals["cau_action_conflict"],
        },
    ]

    per_split_csv = OUT_DIR / "cau_action_conflict_can_five_split_endpoint.csv"
    summary_csv = OUT_DIR / "cau_action_conflict_can_five_split_endpoint_summary.csv"
    report_path = OUT_DIR / "CAU_ACTION_CONFLICT_CAN_FIVE_SPLIT_ENDPOINT_REPORT.md"
    write_csv(
        per_split_csv,
        rows,
        [
            "split_seed",
            "cau_successes",
            "eval_episodes",
            "positive_only_successes",
            "weighted_bc_successes",
            "triage_bc_successes",
            "v02_selected_successes",
            "best_old_baseline_successes",
            "best_non_oracle_successes",
            "delta_vs_positive_only",
            "delta_vs_best_old_baseline",
            "delta_vs_v02_selected",
            "delta_vs_best_non_oracle",
            "cau_avg_len",
            "cau_report",
        ],
    )
    write_csv(summary_csv, summary_rows, ["method_id", "successes", "eval_episodes", "delta_vs_cau"])

    lines = [
        "# CAU Action-Conflict Can Five-Split Endpoint",
        "",
        "This report aggregates the epoch-200, 50-episode Can evaluations for the fixed CAU action-conflict recipe.",
        "It is a follow-up to the original first-20 Can404 screen, not a new frozen paper method.",
        "",
        "## Aggregate Read",
        "",
        f"- CAU action-conflict: `{score(totals['cau_action_conflict'], episodes)}`.",
        f"- Positive-only NN: `{score(totals['positive_only_nn'], episodes)}`.",
        f"- Weighted BC: `{score(totals['weighted_bc'], episodes)}`.",
        f"- TRIAGE-BC v0.1: `{score(totals['triage_bc'], episodes)}`.",
        f"- Best old baseline per split: `{score(per_split_best_old, episodes)}`.",
        f"- v0.2 selected union branch: `{score(totals['positive_nn_risk_union_top40'], episodes)}`.",
        f"- Best non-oracle per split including v0.2: `{score(per_split_best_non_oracle, episodes)}`.",
        "",
        "## Per-Split Results",
        "",
        "| split | CAU | positive | weighted | v0.1 | v0.2 selected | delta vs best old | delta vs v0.2 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {split_seed} | {cau_successes}/{eval_episodes} | {positive_only_successes}/{eval_episodes} | "
            "{weighted_bc_successes}/{eval_episodes} | {triage_bc_successes}/{eval_episodes} | "
            "{v02_selected_successes}/{eval_episodes} | {delta_vs_best_old_baseline:+d} | "
            "{delta_vs_v02_selected:+d} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- The first-20 Can404 rejection was too pessimistic for CAU as a broad Can follow-up: over five 50-episode Can splits, CAU edges the best old non-oracle baseline per split by `1/250` and beats every fixed old branch in aggregate.",
            "- CAU is still not SOTA-dominance evidence: it loses split404 to positive-only by `4/50`, loses split101 to weighted by `4/50`, and remains `4/250` below the v0.2 selected union branch in aggregate.",
            "- The useful next research direction is not the current CAU gate; it is either a CAU-plus-v0.2 portfolio that avoids the split101/v0.2 gap and the split404 CAU loss, or a stronger state-conditional policy-quality signal.",
            "",
            "## Artifacts",
            "",
            f"- Per-split CSV: `{per_split_csv}`.",
            f"- Summary CSV: `{summary_csv}`.",
        ]
    )
    for split in SPLITS:
        lines.append(f"- Split{split} CAU eval: `{CAU_REPORTS[split]}`.")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = {
        "cau_action_conflict": 193,
        "positive_only_nn": 174,
        "weighted_bc": 158,
        "triage_bc": 171,
        "v02_selected": 197,
        "best_old": 192,
        "best_non_oracle": 209,
    }
    actual = {
        "cau_action_conflict": totals["cau_action_conflict"],
        "positive_only_nn": totals["positive_only_nn"],
        "weighted_bc": totals["weighted_bc"],
        "triage_bc": totals["triage_bc"],
        "v02_selected": totals["positive_nn_risk_union_top40"],
        "best_old": per_split_best_old,
        "best_non_oracle": per_split_best_non_oracle,
    }
    if actual != expected:
        raise AssertionError(f"unexpected CAU five-split aggregate: {actual}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
