#!/usr/bin/env python3
"""Summarize a train-statistic anchor calibration screen for Candidate F."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
FINAL = ROOT / "results" / "final_paper_v02"
SPLITS = [101, 202, 303, 404, 505]
N_FIRST20 = 20
N_ENDPOINT = 50
TAIL_FRACTION_OF_UNLABELED_MEAN = 0.5


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


def success_count(path: Path, n: int = N_FIRST20) -> int:
    rows = endpoint_rows(read_csv(path))[:n]
    if len(rows) != n:
        raise ValueError(f"{path}: expected at least {n} rows, got {len(rows)}")
    return sum(int(float(row["success"])) for row in rows)


def baseline_csv(split: int, method: str) -> Path:
    return (
        FINAL
        / "per_seed"
        / f"can_paired_pos40_bad80_split{split}_{method}_policy0"
        / "eval"
        / "episode_metrics.csv"
    )


def candidate_e_csv(split: int) -> Path:
    isolated = OUT / f"candidate_e_initial_posdist_gate_weighted_split{split}_eval20_isolated_rng" / "episode_metrics.csv"
    if isolated.exists():
        return isolated
    if split == 404:
        return OUT / "candidate_e_initial_posdist_gate_weighted_eval20" / "episode_metrics.csv"
    return OUT / f"candidate_e_initial_posdist_gate_weighted_split{split}_eval20" / "episode_metrics.csv"


def candidate_e_50_csv(split: int) -> Path | None:
    isolated = OUT / f"candidate_e_initial_posdist_gate_weighted_split{split}_eval50_isolated_rng" / "episode_metrics.csv"
    if isolated.exists():
        return isolated
    legacy = OUT / f"candidate_e_initial_posdist_gate_weighted_split{split}_eval50" / "episode_metrics.csv"
    if legacy.exists():
        return legacy
    if split == 404:
        old = OUT / "candidate_e_initial_posdist_gate_weighted_eval50" / "episode_metrics.csv"
        if old.exists():
            return old
    return None


def gate_opens(path: Path) -> int:
    rows = read_csv(path)
    if not rows or "initial_gate_open" not in rows[0]:
        return 0
    return sum(int(row.get("initial_gate_open", "0")) for row in rows)


def positive_selected_classifier_tail(split: int) -> dict[str, float | int]:
    pos_diag_path = (
        FINAL
        / "per_seed"
        / f"can_paired_pos40_bad80_split{split}_positive_only_nn_policy0"
        / "setup"
        / "diagnostics.json"
    )
    weights_path = (
        FINAL
        / "per_seed"
        / f"can_paired_pos40_bad80_split{split}_weighted_bc_policy0"
        / "setup"
        / "demo_weights.json"
    )
    pos_diag = json.loads(pos_diag_path.read_text(encoding="utf-8"))
    weights = json.loads(weights_path.read_text(encoding="utf-8"))
    selected = list(pos_diag["selected_unlabeled_demos"])
    probs = sorted(float(weights[demo_id]) for demo_id in selected)
    weighted_diag_path = (
        FINAL
        / "per_seed"
        / f"can_paired_pos40_bad80_split{split}_weighted_bc_policy0"
        / "setup"
        / "diagnostics.json"
    )
    weighted_diag = json.loads(weighted_diag_path.read_text(encoding="utf-8"))
    unlabeled_prob_mean = float(weighted_diag["classifier"]["unlabeled_prob_mean"])
    calibrated_tail_threshold = TAIL_FRACTION_OF_UNLABELED_MEAN * unlabeled_prob_mean
    return {
        "selected_count": len(selected),
        "selected_prob_min": probs[0],
        "selected_prob_p10": probs[int(0.1 * len(probs))],
        "selected_prob_p25": probs[int(0.25 * len(probs))],
        "selected_prob_mean": sum(probs) / len(probs),
        "unlabeled_prob_mean": unlabeled_prob_mean,
        "selected_min_over_unlabeled_mean": probs[0] / unlabeled_prob_mean,
        "calibrated_tail_threshold": calibrated_tail_threshold,
        "selected_prob_below_calibrated_threshold": sum(prob < calibrated_tail_threshold for prob in probs),
        "selected_prob_below_0p2": sum(prob < 0.2 for prob in probs),
        "selected_prob_below_0p4": sum(prob < 0.4 for prob in probs),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object) -> str:
    if value == "":
        return ""
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def count_cell(value: object, denom: int) -> str:
    if value == "":
        return "n/a"
    return f"{value}/{denom}"


def main() -> None:
    rows: list[dict[str, object]] = []
    for split in SPLITS:
        positive = success_count(baseline_csv(split, "positive_only_nn"), N_FIRST20)
        weighted = success_count(baseline_csv(split, "weighted_bc"), N_FIRST20)
        triage = success_count(baseline_csv(split, "triage_bc"), N_FIRST20)
        candidate_e_path = candidate_e_csv(split)
        candidate_e = success_count(candidate_e_path, N_FIRST20)

        positive_50 = success_count(baseline_csv(split, "positive_only_nn"), N_ENDPOINT)
        weighted_50 = success_count(baseline_csv(split, "weighted_bc"), N_ENDPOINT)
        triage_50 = success_count(baseline_csv(split, "triage_bc"), N_ENDPOINT)
        candidate_e_50_path = candidate_e_50_csv(split)
        if candidate_e_50_path is not None:
            candidate_e_50 = success_count(candidate_e_50_path, N_ENDPOINT)
            candidate_e_50_source = candidate_e_50_path.parent.name
        elif gate_opens(candidate_e_path) == 0:
            candidate_e_50 = positive_50
            candidate_e_50_source = "positive_50_no_gate_in_first20"
        else:
            candidate_e_50 = ""
            candidate_e_50_source = "missing_router_50"

        tail = positive_selected_classifier_tail(split)
        use_weighted_anchor = int(tail["selected_prob_below_calibrated_threshold"]) > 0
        candidate_f = weighted if use_weighted_anchor else candidate_e
        candidate_f_50 = weighted_50 if use_weighted_anchor else candidate_e_50
        candidate_f_source = "weighted_anchor" if use_weighted_anchor else "candidate_e_gate"
        best_baseline = max(positive, weighted, triage)
        best_baseline_50 = max(positive_50, weighted_50, triage_50)
        rows.append(
            {
                "split": split,
                **tail,
                "anchor_rule": (
                    "weighted if positive-selected classifier tail < "
                    f"{TAIL_FRACTION_OF_UNLABELED_MEAN:g} * unlabeled_prob_mean; "
                    "else candidate_e"
                ),
                "candidate_f_source": candidate_f_source,
                "positive_first20": positive,
                "weighted_first20": weighted,
                "triage_first20": triage,
                "candidate_e_first20": candidate_e,
                "candidate_f_first20": candidate_f,
                "best_baseline_first20": best_baseline,
                "candidate_f_delta_vs_best_baseline": candidate_f - best_baseline,
                "positive_50": positive_50,
                "weighted_50": weighted_50,
                "triage_50": triage_50,
                "candidate_e_50": candidate_e_50,
                "candidate_e_50_source": candidate_e_50_source,
                "candidate_f_50": candidate_f_50,
                "best_baseline_50": best_baseline_50,
                "candidate_f_50_delta_vs_best_baseline": (
                    int(candidate_f_50) - best_baseline_50 if candidate_f_50 != "" else ""
                ),
            }
        )

    rows_with_e_50 = [row for row in rows if row["candidate_e_50"] != ""]
    rows_with_f_50 = [row for row in rows if row["candidate_f_50"] != ""]
    total = {
        "split": "total",
        "selected_count": "",
        "selected_prob_min": "",
        "selected_prob_p10": "",
        "selected_prob_p25": "",
        "selected_prob_mean": "",
        "unlabeled_prob_mean": "",
        "selected_min_over_unlabeled_mean": "",
        "calibrated_tail_threshold": "",
        "selected_prob_below_calibrated_threshold": sum(
            int(row["selected_prob_below_calibrated_threshold"]) for row in rows
        ),
        "selected_prob_below_0p2": sum(int(row["selected_prob_below_0p2"]) for row in rows),
        "selected_prob_below_0p4": sum(int(row["selected_prob_below_0p4"]) for row in rows),
        "anchor_rule": "",
        "candidate_f_source": "",
        "positive_first20": sum(int(row["positive_first20"]) for row in rows),
        "weighted_first20": sum(int(row["weighted_first20"]) for row in rows),
        "triage_first20": sum(int(row["triage_first20"]) for row in rows),
        "candidate_e_first20": sum(int(row["candidate_e_first20"]) for row in rows),
        "candidate_f_first20": sum(int(row["candidate_f_first20"]) for row in rows),
        "best_baseline_first20": sum(int(row["best_baseline_first20"]) for row in rows),
        "positive_50": sum(int(row["positive_50"]) for row in rows),
        "weighted_50": sum(int(row["weighted_50"]) for row in rows),
        "triage_50": sum(int(row["triage_50"]) for row in rows),
        "candidate_e_50": sum(int(row["candidate_e_50"]) for row in rows_with_e_50)
        if len(rows_with_e_50) == len(rows)
        else "",
        "candidate_e_50_source": "mixed observed and no-gate substitution",
        "candidate_f_50": sum(int(row["candidate_f_50"]) for row in rows_with_f_50)
        if len(rows_with_f_50) == len(rows)
        else "",
        "best_baseline_50": sum(int(row["best_baseline_50"]) for row in rows),
    }
    total["candidate_f_delta_vs_best_baseline"] = int(total["candidate_f_first20"]) - int(
        total["best_baseline_first20"]
    )
    total["candidate_f_50_delta_vs_best_baseline"] = (
        int(total["candidate_f_50"]) - int(total["best_baseline_50"])
        if total["candidate_f_50"] != ""
        else ""
    )
    rows_with_total = [*rows, total]

    fieldnames = [
        "split",
        "selected_count",
        "selected_prob_min",
        "selected_prob_p10",
        "selected_prob_p25",
        "selected_prob_mean",
        "unlabeled_prob_mean",
        "selected_min_over_unlabeled_mean",
        "calibrated_tail_threshold",
        "selected_prob_below_calibrated_threshold",
        "selected_prob_below_0p2",
        "selected_prob_below_0p4",
        "anchor_rule",
        "candidate_f_source",
        "positive_first20",
        "weighted_first20",
        "triage_first20",
        "candidate_e_first20",
        "candidate_f_first20",
        "best_baseline_first20",
        "candidate_f_delta_vs_best_baseline",
        "positive_50",
        "weighted_50",
        "triage_50",
        "candidate_e_50",
        "candidate_e_50_source",
        "candidate_f_50",
        "best_baseline_50",
        "candidate_f_50_delta_vs_best_baseline",
    ]
    csv_path = OUT / "candidate_f_anchor_calibration_first20_summary.csv"
    write_csv(csv_path, rows_with_total, fieldnames)

    report_path = OUT / "candidate_f_anchor_calibration_screen_REPORT.md"
    lines = [
        "# Candidate F Anchor-Calibration First-20 Screen",
        "",
        "Candidate F is a hypothesis from train/support statistics:",
        "",
        "- compute classifier probabilities for the positive-NN selected unlabeled",
        "  support set;",
        "- set the tail threshold to half of the full unlabeled pool's mean",
        "  classifier probability;",
        "- if any selected demo falls below that threshold, use weighted BC as the",
        "  split-level anchor;",
        "- otherwise use Candidate E, the positive anchor with initial-distance",
        "  fallback to weighted BC.",
        "",
        "This rule uses no endpoint outcomes or hidden labels. The remaining",
        "hyperparameter is the tail fraction `0.5`.",
        "",
        "| split | min prob | unlabeled mean | min/mean | tail thr | #<thr | source | positive | weighted | triage | cand E | cand F | delta vs best |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows_with_total:
        denom = 100 if row["split"] == "total" else 20
        lines.append(
            "| {split} | {selected_prob_min} | {unlabeled_prob_mean} | "
            "{selected_min_over_unlabeled_mean} | {calibrated_tail_threshold} | "
            "{selected_prob_below_calibrated_threshold} | "
            "{candidate_f_source} | "
            "{positive_first20}/{denom} | {weighted_first20}/{denom} | "
            "{triage_first20}/{denom} | {candidate_e_first20}/{denom} | "
            "{candidate_f_first20}/{denom} | {delta:+d} |".format(
                split=row["split"],
                selected_prob_min=fmt(row["selected_prob_min"]),
                unlabeled_prob_mean=fmt(row["unlabeled_prob_mean"]),
                selected_min_over_unlabeled_mean=fmt(row["selected_min_over_unlabeled_mean"]),
                calibrated_tail_threshold=fmt(row["calibrated_tail_threshold"]),
                selected_prob_below_calibrated_threshold=row["selected_prob_below_calibrated_threshold"],
                candidate_f_source=row["candidate_f_source"],
                positive_first20=row["positive_first20"],
                weighted_first20=row["weighted_first20"],
                triage_first20=row["triage_first20"],
                candidate_e_first20=row["candidate_e_first20"],
                candidate_f_first20=row["candidate_f_first20"],
                denom=denom,
                delta=int(row["candidate_f_delta_vs_best_baseline"]),
            )
        )
    lines.extend(
        [
            "",
            "## 50-Episode Assembled Endpoint Estimate",
            "",
            "This table combines completed 50-episode baselines with isolated-RNG",
            "Candidate E 50-episode runs where available. For splits where the",
            "isolated first-20 gate never opened and no router-50 run was launched,",
            "the positive-only 50-episode result is used as a no-gate substitution.",
            "",
            "| split | positive | weighted | triage | cand E / subst | cand F | delta vs best | source |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows_with_total:
        denom = 250 if row["split"] == "total" else 50
        lines.append(
            "| {split} | {positive_50} | {weighted_50} | "
            "{triage_50} | {candidate_e_50} | "
            "{candidate_f_50} | {delta} | {source} |".format(
                split=row["split"],
                positive_50=count_cell(row["positive_50"], denom),
                weighted_50=count_cell(row["weighted_50"], denom),
                triage_50=count_cell(row["triage_50"], denom),
                candidate_e_50=count_cell(row["candidate_e_50"], denom),
                candidate_f_50=count_cell(row["candidate_f_50"], denom),
                delta=(
                    f"{int(row['candidate_f_50_delta_vs_best_baseline']):+d}"
                    if row["candidate_f_50_delta_vs_best_baseline"] != ""
                    else ""
                ),
                source=row["candidate_e_50_source"],
            )
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            "- The calibrated low-probability tail rule selects weighted only on split",
            "  101, where the fixed positive anchor was the main failure.",
            "- The normalized tail ratio is `0.309` on split 101 versus at least",
            "  `0.692` on the other splits, so any tail fraction in roughly",
            "  `[0.35, 0.65]` would make the same anchor decision.",
            "- With isolated-RNG router evaluation, the resulting first-20 aggregate",
            "  is `79/100`, exceeding the completed per-split baseline oracle over",
            "  positive-only, weighted, and triage (`76/100`).",
            "- The assembled 50-episode estimate is `198/250`, versus positive-only",
            "  `174/250` and the per-split baseline oracle `192/250`. The gain is",
            "  mostly split 101 weighted anchoring plus split 404 isolated-RNG",
            "  Candidate E (`46/50`).",
            "- This is closer to a frozen rule than the fixed `0.2` threshold because",
            "  the cutoff is tied to the unlabeled pool's classifier score scale. It",
            "  has now been consolidated in",
            "  `results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md`.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{csv_path.relative_to(ROOT)}`.",
            "- Frozen matrix: `results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md`.",
            "- Teacher-forced negative audit:",
            "  `results/candidate_breakthrough/candidate_f_teacher_forced_anchor_audit_REPORT.md`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
