#!/usr/bin/env python3
"""Post-hoc anchor-preserving feature-gate audit for Can404 near misses.

This is an upper-bound diagnostic, not a deployable method. It asks whether a
tiny family of hidden-label-free initial-state features could have routed from
positive-only to a near-miss candidate without losing positive-only successes on
the same first-20 Can404 screen.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"
FEATURE_CSV = ROOT / "results" / "candidate_breakthrough" / "candidate_v_failure_analysis_per_initial.csv"


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    label: str
    episode_metrics: Path
    checkpoint_name: str


POSITIVE = MethodSpec(
    "positive_only_nn_top40",
    "Positive-only NN top40",
    ROOT
    / "results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/eval/episode_metrics.csv",
    "model_epoch_200",
)

CANDIDATES = [
    MethodSpec(
        "cau_action_conflict",
        "CAU action-conflict",
        ROOT / "results/sota_candidate/cau_action_conflict_can404_b005_m05_eval20/episode_metrics.csv",
        "model_epoch_200",
    ),
    MethodSpec(
        "demo_dpo_refcenter",
        "Demo-DPO ref-centered",
        ROOT / "results/sota_candidate/demo_pref_refcenter_can404_w1_e20_eval20/episode_metrics.csv",
        "model_epoch_5",
    ),
    MethodSpec(
        "candidate_c_sequence_mask",
        "Candidate C sequence mask",
        ROOT / "results/candidate_breakthrough/candidate_c_mask_can404_e200_eval20_epoch200/episode_metrics.csv",
        "model_epoch_200",
    ),
]

FEATURES = {
    "initial_anchor_pos_dist_mean": "initial_anchor_pos_dist_mean",
    "initial_anchor_margin_mean": "initial_anchor_margin_mean",
    "candidate_e_gate_opens": "candidate_e_gate_opens",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def read_episode_successes(spec: MethodSpec, max_episodes: int = 20) -> dict[tuple[int, str], int]:
    rows: dict[tuple[int, str], int] = {}
    with spec.episode_metrics.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            episode = int(row["episode"])
            if episode >= max_episodes:
                continue
            if Path(row["checkpoint"]).stem != spec.checkpoint_name:
                continue
            rows[(episode, row["initial_demo_id"])] = int(float(row["success"]))
    if len(rows) != max_episodes:
        raise AssertionError(f"{spec.method_id} has {len(rows)} rows, expected {max_episodes}")
    return rows


def read_features() -> dict[str, dict[str, float]]:
    features: dict[str, dict[str, float]] = {}
    with FEATURE_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["split"] != "404":
                continue
            features[row["initial_demo_id"]] = {
                out_name: float(row[source_name])
                for out_name, source_name in FEATURES.items()
            }
    if not features:
        raise AssertionError(f"no split-404 features in {FEATURE_CSV}")
    return features


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def candidate_thresholds(values: list[float]) -> list[float]:
    uniq = sorted(set(values))
    if len(uniq) == 1:
        return [uniq[0]]
    return [uniq[0] - 1e-6, *[(a + b) / 2.0 for a, b in zip(uniq, uniq[1:])], uniq[-1] + 1e-6]


def main() -> None:
    args = parse_args()
    positive = read_episode_successes(POSITIVE)
    candidates = {spec.method_id: read_episode_successes(spec) for spec in CANDIDATES}
    features = read_features()
    positive_successes = sum(positive.values())

    rows: list[dict[str, object]] = []
    keys = sorted(positive)
    for spec in CANDIDATES:
        candidate = candidates[spec.method_id]
        candidate_successes = sum(candidate.values())
        for feature_name in FEATURES:
            values = [features[demo_id][feature_name] for _episode, demo_id in keys]
            for threshold in candidate_thresholds(values):
                for direction in ("le", "gt"):
                    routed_successes: dict[tuple[int, str], int] = {}
                    open_count = 0
                    opened_demo_ids: set[str] = set()
                    for key in keys:
                        _episode, demo_id = key
                        value = features[demo_id][feature_name]
                        gate_open = value <= threshold if direction == "le" else value > threshold
                        if gate_open:
                            open_count += 1
                            opened_demo_ids.add(demo_id)
                        routed_successes[key] = candidate[key] if gate_open else positive[key]
                    routed_total = sum(routed_successes.values())
                    gains = sum(routed_successes[key] == 1 and positive[key] == 0 for key in keys)
                    losses = sum(routed_successes[key] == 0 and positive[key] == 1 for key in keys)
                    rows.append(
                        {
                            "method_id": spec.method_id,
                            "label": spec.label,
                            "candidate_successes": candidate_successes,
                            "positive_successes": positive_successes,
                            "feature": feature_name,
                            "direction": direction,
                            "threshold": f"{threshold:.6f}",
                            "opened_episodes": open_count,
                            "opened_initials": len(opened_demo_ids),
                            "opened_initial_demo_ids": " ".join(sorted(opened_demo_ids)),
                            "routed_successes": routed_total,
                            "gains_vs_positive": gains,
                            "losses_vs_positive": losses,
                            "delta_vs_positive": routed_total - positive_successes,
                            "posthoc_upper_bound": "yes",
                        }
                    )

    fieldnames = [
        "method_id",
        "label",
        "candidate_successes",
        "positive_successes",
        "feature",
        "direction",
        "threshold",
        "opened_episodes",
        "opened_initials",
        "opened_initial_demo_ids",
        "routed_successes",
        "gains_vs_positive",
        "losses_vs_positive",
        "delta_vs_positive",
        "posthoc_upper_bound",
    ]
    summary_csv = args.out_dir / "can404_anchor_feature_gate_preflight.csv"
    report_path = args.out_dir / "CAN404_ANCHOR_FEATURE_GATE_PREFLIGHT_REPORT.md"
    write_csv(summary_csv, rows, fieldnames)

    best_by_method: dict[str, dict[str, object]] = {}
    zero_loss_gain_by_method: dict[str, dict[str, object] | None] = {}
    for spec in CANDIDATES:
        method_rows = [row for row in rows if row["method_id"] == spec.method_id]
        best_by_method[spec.method_id] = max(
            method_rows,
            key=lambda row: (
                int(row["routed_successes"]),
                -int(row["losses_vs_positive"]),
                int(row["gains_vs_positive"]),
                -int(row["opened_episodes"]),
            ),
        )
        zero_loss_gain_rows = [
            row
            for row in method_rows
            if int(row["losses_vs_positive"]) == 0 and int(row["gains_vs_positive"]) > 0
        ]
        zero_loss_gain_by_method[spec.method_id] = (
            max(
                zero_loss_gain_rows,
                key=lambda row: (
                    int(row["routed_successes"]),
                    int(row["gains_vs_positive"]),
                    -int(row["opened_episodes"]),
                ),
            )
            if zero_loss_gain_rows
            else None
        )

    cau_zero = zero_loss_gain_by_method["cau_action_conflict"]
    lines = [
        "# Can404 Anchor Feature-Gate Preflight",
        "",
        "This is a post-hoc upper-bound audit over existing first-20 Can404 endpoint screens.",
        "It tests whether simple hidden-label-free initial-state features from the prior Candidate E/V audit could route from positive-only to a near-miss candidate while preserving positive-only successes.",
        "",
        "Important caveat: thresholds are selected on the same Can404 endpoint outcomes. This is not a deployable method or a validation result.",
        "",
        "## Summary",
        "",
        f"- Positive-only anchor: `{positive_successes}/20`.",
    ]
    if cau_zero is not None:
        lines.append(
            "- CAU has a same-screen post-hoc zero-loss gate: `{routed_successes}/20`, gains `{gains_vs_positive}`, losses `{losses_vs_positive}`, feature `{feature}` `{direction}` `{threshold}`, opened initials `{opened_initial_demo_ids}`.".format(
                **cau_zero
            )
        )
    lines.extend(
        [
            "- Demo-DPO and Candidate C have no zero-loss gain gate in this small feature family.",
            "- This is enough to define a future validation hypothesis, but not enough to justify a paper-facing methods claim.",
            "",
            "## Best Same-Screen Gates",
            "",
            "| method | candidate alone | best routed | feature gate | opened initials | gains | losses | status |",
            "| --- | ---: | ---: | --- | --- | ---: | ---: | --- |",
        ]
    )
    for spec in CANDIDATES:
        best = best_by_method[spec.method_id]
        zero = zero_loss_gain_by_method[spec.method_id]
        status = "posthoc_hypothesis_only" if zero is not None else "no_anchor_preserving_gate_found"
        lines.append(
            "| {label} | {candidate_successes}/20 | {routed_successes}/20 | {feature} {direction} {threshold} | {opened_initial_demo_ids} | {gains_vs_positive} | {losses_vs_positive} | {status} |".format(
                status=status,
                **best,
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "- Do not run a full endpoint matrix from this same-screen result.",
            "- The only defensible follow-up would be a predeclared fresh validation: freeze the CAU-plus-positive fallback feature rule from this audit, then test it on a fresh split after training the corresponding candidate policy.",
            "- If that fresh split shows any positive-only anchor loss, stop immediately.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{summary_csv}`.",
            f"- Report: `{report_path}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected_cau = ("18", "1", "0")
    if cau_zero is None:
        raise AssertionError("expected a CAU zero-loss same-screen gate")
    actual_cau = (
        str(cau_zero["routed_successes"]),
        str(cau_zero["gains_vs_positive"]),
        str(cau_zero["losses_vs_positive"]),
    )
    if actual_cau != expected_cau:
        raise AssertionError(f"unexpected CAU gate result: {actual_cau}")
    for method_id in ("demo_dpo_refcenter", "candidate_c_sequence_mask"):
        if zero_loss_gain_by_method[method_id] is not None:
            raise AssertionError(f"unexpected zero-loss gain gate for {method_id}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
