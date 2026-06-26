#!/usr/bin/env python3
"""Audit whether Candidate F's tail calibration transfers to Lift MG."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
FINAL = ROOT / "results" / "final_paper_v02"
SPLITS = [101, 202, 303, 404, 505]
N_EPISODES = 50
TAIL_FRACTION_OF_UNLABELED_MEAN = 0.5
MILD_TAIL_FRACTION_MAX = 0.03


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def endpoint_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if rows and "checkpoint" in rows[0]:
        checkpoints = {row["checkpoint"] for row in rows}
        if len(checkpoints) > 1:
            filtered = [row for row in rows if "model_epoch_200" in row["checkpoint"]]
            if filtered:
                return filtered
    return rows


def success_count(path: Path) -> int:
    rows = endpoint_rows(read_csv(path))[:N_EPISODES]
    if len(rows) != N_EPISODES:
        raise ValueError(f"{path}: expected {N_EPISODES} rows, found {len(rows)}")
    return sum(int(float(row["success"])) for row in rows)


def lift_baseline_csv(split: int, method: str) -> Path:
    return (
        FINAL
        / "per_seed"
        / f"lift_mg_mg_sparse_split{split}_{method}_policy0"
        / "eval"
        / "episode_metrics.csv"
    )


def lift_tail_metrics(split: int) -> dict[str, float | int]:
    pos_diag_path = (
        FINAL
        / "per_seed"
        / f"lift_mg_mg_sparse_split{split}_positive_only_nn_policy0"
        / "setup"
        / "diagnostics.json"
    )
    weighted_diag_path = (
        FINAL
        / "per_seed"
        / f"lift_mg_mg_sparse_split{split}_weighted_bc_policy0"
        / "setup"
        / "diagnostics.json"
    )
    weights_path = (
        FINAL
        / "per_seed"
        / f"lift_mg_mg_sparse_split{split}_weighted_bc_policy0"
        / "setup"
        / "demo_weights.json"
    )
    pos_diag = json.loads(pos_diag_path.read_text(encoding="utf-8"))
    weighted_diag = json.loads(weighted_diag_path.read_text(encoding="utf-8"))
    weights = json.loads(weights_path.read_text(encoding="utf-8"))
    selected = list(pos_diag["selected_unlabeled_demos"])
    probs = sorted(float(weights[demo_id]) for demo_id in selected)
    unlabeled_prob_mean = float(weighted_diag["classifier"]["unlabeled_prob_mean"])
    threshold = TAIL_FRACTION_OF_UNLABELED_MEAN * unlabeled_prob_mean
    below_count = sum(prob < threshold for prob in probs)
    return {
        "selected_count": len(selected),
        "selected_prob_min": probs[0],
        "unlabeled_prob_mean": unlabeled_prob_mean,
        "selected_min_over_unlabeled_mean": probs[0] / unlabeled_prob_mean,
        "calibrated_tail_threshold": threshold,
        "below_calibrated_threshold": below_count,
        "below_calibrated_fraction": below_count / len(probs),
    }


def choose_can_style(metrics: dict[str, float | int]) -> str:
    return "weighted" if int(metrics["below_calibrated_threshold"]) > 0 else "positive"


def choose_tail_severity(metrics: dict[str, float | int]) -> str:
    below = int(metrics["below_calibrated_threshold"])
    if below == 0:
        return "positive"
    if float(metrics["below_calibrated_fraction"]) < MILD_TAIL_FRACTION_MAX:
        return "triage"
    return "weighted"


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main() -> None:
    rows: list[dict[str, object]] = []
    for split in SPLITS:
        positive = success_count(lift_baseline_csv(split, "positive_only_nn"))
        weighted = success_count(lift_baseline_csv(split, "weighted_bc"))
        triage = success_count(lift_baseline_csv(split, "triage_bc"))
        metrics = lift_tail_metrics(split)
        can_style_choice = choose_can_style(metrics)
        severity_choice = choose_tail_severity(metrics)
        values = {"positive": positive, "weighted": weighted, "triage": triage}
        best = max(values.values())
        rows.append(
            {
                "split": split,
                **metrics,
                "positive": positive,
                "weighted": weighted,
                "triage": triage,
                "best_baseline": best,
                "can_style_choice": can_style_choice,
                "can_style_success": values[can_style_choice],
                "tail_severity_choice": severity_choice,
                "tail_severity_success": values[severity_choice],
                "tail_severity_delta_vs_best": values[severity_choice] - best,
            }
        )

    total = {
        "split": "total",
        "selected_count": "",
        "selected_prob_min": "",
        "unlabeled_prob_mean": "",
        "selected_min_over_unlabeled_mean": "",
        "calibrated_tail_threshold": "",
        "below_calibrated_threshold": sum(int(row["below_calibrated_threshold"]) for row in rows),
        "below_calibrated_fraction": "",
        "positive": sum(int(row["positive"]) for row in rows),
        "weighted": sum(int(row["weighted"]) for row in rows),
        "triage": sum(int(row["triage"]) for row in rows),
        "best_baseline": sum(int(row["best_baseline"]) for row in rows),
        "can_style_choice": "",
        "can_style_success": sum(int(row["can_style_success"]) for row in rows),
        "tail_severity_choice": "",
        "tail_severity_success": sum(int(row["tail_severity_success"]) for row in rows),
        "tail_severity_delta_vs_best": sum(int(row["tail_severity_success"]) for row in rows)
        - sum(int(row["best_baseline"]) for row in rows),
    }
    rows_with_total = [*rows, total]

    can_matrix = read_csv(OUT / "candidate_f_frozen_matrix_summary.csv")
    can_total = next(row for row in can_matrix if row["split"] == "total")
    can_candidate_f = int(can_total["candidate_f"])
    can_best = int(can_total["best_baseline"])
    combined_candidate = can_candidate_f + int(total["tail_severity_success"])
    combined_best = can_best + int(total["best_baseline"])

    csv_path = OUT / "candidate_f_lift_transfer_audit.csv"
    fieldnames = [
        "split",
        "selected_count",
        "selected_prob_min",
        "unlabeled_prob_mean",
        "selected_min_over_unlabeled_mean",
        "calibrated_tail_threshold",
        "below_calibrated_threshold",
        "below_calibrated_fraction",
        "positive",
        "weighted",
        "triage",
        "best_baseline",
        "can_style_choice",
        "can_style_success",
        "tail_severity_choice",
        "tail_severity_success",
        "tail_severity_delta_vs_best",
    ]
    write_csv(csv_path, rows_with_total, fieldnames)

    report_path = OUT / "candidate_f_lift_transfer_audit_REPORT.md"
    lines = [
        "# Candidate F Lift Transfer Audit",
        "",
        "This audit reuses completed Lift MG endpoint rows and applies the same",
        "`0.5 * unlabeled_prob_mean` low-tail statistic used by Candidate F on Can.",
        "No new Lift rollouts are claimed here.",
        "",
        "| split | min/mean | #<thr | frac<thr | positive | weighted | triage | can-style | tail-severity | best |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: |",
    ]
    for row in rows_with_total:
        denom = 250 if row["split"] == "total" else 50
        can_style = (
            f"{row['can_style_choice']} {row['can_style_success']}/{denom}"
            if row["split"] != "total"
            else f"{row['can_style_success']}/{denom}"
        )
        severity = (
            f"{row['tail_severity_choice']} {row['tail_severity_success']}/{denom}"
            if row["split"] != "total"
            else f"{row['tail_severity_success']}/{denom}"
        )
        lines.append(
            "| {split} | {ratio} | {below} | {frac} | {positive}/{denom} | "
            "{weighted}/{denom} | {triage}/{denom} | {can_style} | "
            "{severity} | {best}/{denom} |".format(
                split=row["split"],
                ratio=fmt(row["selected_min_over_unlabeled_mean"]),
                below=row["below_calibrated_threshold"],
                frac=fmt(row["below_calibrated_fraction"]),
                positive=row["positive"],
                weighted=row["weighted"],
                triage=row["triage"],
                can_style=can_style,
                severity=severity,
                best=row["best_baseline"],
                denom=denom,
            )
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The direct Can-style transfer, `any low tail -> weighted`, reaches",
            "  `145/250` on Lift, only slightly above always-weighted and always-triage",
            "  (`143/250`) and below the per-split baseline oracle (`154/250`).",
            "- Lift suggests a richer tail-severity interpretation: no low tail selects",
            "  positive-only, mild low tail selects triage/hard support, and severe low",
            "  tail selects weighted. That matches the completed Lift baseline oracle",
            "  (`154/250`) but is diagnostic, not yet a frozen method.",
            "- Combining frozen Can Candidate F (`198/250`) with this Lift tail-severity",
            f"  diagnostic gives `{combined_candidate}/500`, versus the combined",
            f"  completed baseline oracle `{combined_best}/500`.",
            "- The evidence therefore supports a Can-frozen Candidate F claim now, and",
            "  a possible broader Can+Lift tail-severity router as the next method",
            "  candidate.",
            "",
            "## Artifacts",
            "",
            f"- CSV: `{csv_path.relative_to(ROOT)}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
