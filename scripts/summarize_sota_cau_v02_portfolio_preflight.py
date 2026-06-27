#!/usr/bin/env python3
"""Post-hoc preflight for a CAU-plus-v0.2 Can portfolio rule."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(".")
OUT_DIR = ROOT / "results" / "sota_candidate"
V02_CAN_SUMMARY = ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_can_endpoint_summary.csv"
V02_SUPPORT = ROOT / "results" / "final_paper_v02" / "tables" / "v02_fresh_router_support_per_split.csv"
CAU_SUMMARY = OUT_DIR / "cau_action_conflict_can_five_split_endpoint.csv"
UNION_METHOD = "positive_nn_risk_union_top40"
SPLITS = (101, 202, 303, 404, 505)

BASE_FEATURES = (
    "estimated_positive_mass",
    "count_ge_pos_min",
    "labeled_positive_p10",
    "selected_unlabeled",
    "classifier_score_mean",
    "labeled_positive_min",
    "labeled_positive_mean",
    "labeled_negative_mean",
)
DERIVED_FEATURES = (
    "estimated_mass_ratio",
    "estimated_mass_minus_selected",
    "score_gap_labeled_pos_neg",
    "count_ge_pos_min_ratio",
)
FEATURES = BASE_FEATURES + DERIVED_FEATURES


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def score(successes: int, episodes: int) -> str:
    return f"{successes}/{episodes}"


def fnum(row: dict[str, str], key: str) -> float:
    value = row[key]
    if value == "":
        raise ValueError(f"missing numeric value for {key}")
    return float(value)


def endpoint_by_split_method(rows: list[dict[str, str]]) -> dict[tuple[int, str], dict[str, str]]:
    return {(int(row["split_seed"]), row["method_id"]): row for row in rows}


def cau_by_split(rows: list[dict[str, str]]) -> dict[int, dict[str, str]]:
    return {int(row["split_seed"]): row for row in rows}


def support_by_split(rows: list[dict[str, str]]) -> dict[int, dict[str, str]]:
    out = {}
    for row in rows:
        if row["setting_id"] == "can40" and row["candidate_id"] == UNION_METHOD:
            out[int(row["split_seed"])] = row
    return out


def build_feature_row(row: dict[str, str]) -> dict[str, float]:
    values = {feature: fnum(row, feature) for feature in BASE_FEATURES}
    selected = values["selected_unlabeled"]
    values["estimated_mass_ratio"] = values["estimated_positive_mass"] / selected
    values["estimated_mass_minus_selected"] = values["estimated_positive_mass"] - selected
    values["score_gap_labeled_pos_neg"] = (
        values["labeled_positive_mean"] - values["labeled_negative_mean"]
    )
    values["count_ge_pos_min_ratio"] = values["count_ge_pos_min"] / selected
    return values


def midpoint_thresholds(values: list[float]) -> list[float]:
    unique = sorted(set(values))
    return [(left + right) / 2.0 for left, right in zip(unique, unique[1:])]


def split_label(splits: list[int]) -> str:
    return ";".join(str(split) for split in splits)


def selected_score(
    split_rows: dict[int, dict[str, object]],
    selected_cau_splits: set[int],
) -> int:
    total = 0
    for split in SPLITS:
        row = split_rows[split]
        if split in selected_cau_splits:
            total += int(row["cau_successes"])
        else:
            total += int(row["v02_selected_successes"])
    return total


def gate_row(
    *,
    gate_id: str,
    feature: str,
    direction: str,
    threshold: str,
    selected_cau_splits: set[int],
    split_rows: dict[int, dict[str, object]],
    totals: dict[str, int],
) -> dict[str, object]:
    cau_splits = sorted(selected_cau_splits)
    v02_splits = [split for split in SPLITS if split not in selected_cau_splits]
    successes = selected_score(split_rows, selected_cau_splits)
    episodes = totals["episodes"]
    return {
        "gate_id": gate_id,
        "feature": feature,
        "direction": direction,
        "threshold": threshold,
        "selected_successes": successes,
        "eval_episodes": episodes,
        "selected_score": score(successes, episodes),
        "selected_cau_splits": split_label(cau_splits),
        "selected_v02_splits": split_label(v02_splits),
        "delta_vs_always_v02": successes - totals["always_v02"],
        "delta_vs_always_cau": successes - totals["always_cau"],
        "delta_vs_best_old_baseline_per_split": successes - totals["best_old"],
        "regret_to_cau_v02_oracle": totals["best_cau_v02"] - successes,
        "regret_to_all_non_oracle_oracle": totals["best_all"] - successes,
    }


def score_gate_sort_key(row: dict[str, object]) -> tuple[int, int, int, int, str]:
    feature_priority = {feature: idx for idx, feature in enumerate(FEATURES)}
    feature = str(row["feature"])
    return (
        -int(row["selected_successes"]),
        int(row["regret_to_cau_v02_oracle"]),
        feature_priority.get(feature, 999),
        len(str(row["selected_cau_splits"]).split(";")) if row["selected_cau_splits"] else 0,
        str(row["gate_id"]),
    )


def main() -> None:
    endpoint_rows = endpoint_by_split_method(read_csv(V02_CAN_SUMMARY))
    cau_rows = cau_by_split(read_csv(CAU_SUMMARY))
    support_rows = support_by_split(read_csv(V02_SUPPORT))
    if sorted(support_rows) != list(SPLITS):
        raise AssertionError(f"missing support rows for splits: {sorted(support_rows)}")

    feature_rows = {split: build_feature_row(support_rows[split]) for split in SPLITS}
    split_rows: dict[int, dict[str, object]] = {}
    for split in SPLITS:
        positive = int(endpoint_rows[(split, "positive_only_nn")]["success_count"])
        weighted = int(endpoint_rows[(split, "weighted_bc")]["success_count"])
        triage = int(endpoint_rows[(split, "triage_bc")]["success_count"])
        v02_selected = int(endpoint_rows[(split, UNION_METHOD)]["success_count"])
        cau = int(cau_rows[split]["cau_successes"])
        episodes = int(cau_rows[split]["eval_episodes"])
        best_old = max(positive, weighted, triage)
        row: dict[str, object] = {
            "split_seed": split,
            "eval_episodes": episodes,
            "positive_only_successes": positive,
            "weighted_bc_successes": weighted,
            "triage_bc_successes": triage,
            "v02_selected_successes": v02_selected,
            "cau_successes": cau,
            "best_old_baseline_successes": best_old,
            "best_cau_v02_successes": max(cau, v02_selected),
            "best_all_non_oracle_successes": max(cau, v02_selected, best_old),
        }
        for feature in FEATURES:
            row[feature] = f"{feature_rows[split][feature]:.6f}"
        split_rows[split] = row

    totals = {
        "episodes": sum(int(row["eval_episodes"]) for row in split_rows.values()),
        "always_v02": sum(int(row["v02_selected_successes"]) for row in split_rows.values()),
        "always_cau": sum(int(row["cau_successes"]) for row in split_rows.values()),
        "best_old": sum(int(row["best_old_baseline_successes"]) for row in split_rows.values()),
        "best_cau_v02": sum(int(row["best_cau_v02_successes"]) for row in split_rows.values()),
        "best_all": sum(int(row["best_all_non_oracle_successes"]) for row in split_rows.values()),
    }

    gate_rows: list[dict[str, object]] = [
        gate_row(
            gate_id="always_v02",
            feature="",
            direction="always_v02",
            threshold="",
            selected_cau_splits=set(),
            split_rows=split_rows,
            totals=totals,
        ),
        gate_row(
            gate_id="always_cau",
            feature="",
            direction="always_cau",
            threshold="",
            selected_cau_splits=set(SPLITS),
            split_rows=split_rows,
            totals=totals,
        ),
    ]
    for feature in FEATURES:
        values = [feature_rows[split][feature] for split in SPLITS]
        for threshold in midpoint_thresholds(values):
            for direction in ("gt", "le"):
                if direction == "gt":
                    selected_cau = {
                        split for split in SPLITS if feature_rows[split][feature] > threshold
                    }
                    label = f"{feature}_gt_{threshold:.6f}"
                else:
                    selected_cau = {
                        split for split in SPLITS if feature_rows[split][feature] <= threshold
                    }
                    label = f"{feature}_le_{threshold:.6f}"
                gate_rows.append(
                    gate_row(
                        gate_id=label,
                        feature=feature,
                        direction=direction,
                        threshold=f"{threshold:.6f}",
                        selected_cau_splits=selected_cau,
                        split_rows=split_rows,
                        totals=totals,
                    )
                )

    scan_rows = sorted(gate_rows, key=score_gate_sort_key)
    best_gate = scan_rows[0]
    best_cau_splits = {
        int(split) for split in str(best_gate["selected_cau_splits"]).split(";") if split
    }
    per_split_rows = []
    for split in SPLITS:
        row = dict(split_rows[split])
        selected_method = "cau_action_conflict" if split in best_cau_splits else UNION_METHOD
        selected_successes = (
            int(row["cau_successes"])
            if selected_method == "cau_action_conflict"
            else int(row["v02_selected_successes"])
        )
        row["best_gate_selected_method"] = selected_method
        row["best_gate_selected_successes"] = selected_successes
        row["best_gate_delta_vs_v02"] = selected_successes - int(row["v02_selected_successes"])
        row["best_gate_delta_vs_cau"] = selected_successes - int(row["cau_successes"])
        row["best_gate_delta_vs_best_old"] = selected_successes - int(row["best_old_baseline_successes"])
        per_split_rows.append(row)

    per_split_csv = OUT_DIR / "cau_v02_portfolio_preflight.csv"
    gate_scan_csv = OUT_DIR / "cau_v02_portfolio_preflight_gate_scan.csv"
    report_path = OUT_DIR / "CAU_V02_PORTFOLIO_PREFLIGHT_REPORT.md"
    write_csv(
        per_split_csv,
        per_split_rows,
        [
            "split_seed",
            "eval_episodes",
            "positive_only_successes",
            "weighted_bc_successes",
            "triage_bc_successes",
            "v02_selected_successes",
            "cau_successes",
            "best_old_baseline_successes",
            "best_cau_v02_successes",
            "best_all_non_oracle_successes",
            *FEATURES,
            "best_gate_selected_method",
            "best_gate_selected_successes",
            "best_gate_delta_vs_v02",
            "best_gate_delta_vs_cau",
            "best_gate_delta_vs_best_old",
        ],
    )
    write_csv(
        gate_scan_csv,
        scan_rows,
        [
            "gate_id",
            "feature",
            "direction",
            "threshold",
            "selected_successes",
            "eval_episodes",
            "selected_score",
            "selected_cau_splits",
            "selected_v02_splits",
            "delta_vs_always_v02",
            "delta_vs_always_cau",
            "delta_vs_best_old_baseline_per_split",
            "regret_to_cau_v02_oracle",
            "regret_to_all_non_oracle_oracle",
        ],
    )

    lines = [
        "# CAU plus v0.2 Portfolio Preflight",
        "",
        "This is a post-hoc preflight over the same five completed Can endpoint splits.",
        "It does not add fresh evidence and must not be promoted as a frozen paper result.",
        "The gate scan uses only hidden-label-free setup diagnostics from the v0.2 support audit.",
        "",
        "## Aggregate Read",
        "",
        f"- Always v0.2 selected union: `{score(totals['always_v02'], totals['episodes'])}`.",
        f"- Always CAU action-conflict: `{score(totals['always_cau'], totals['episodes'])}`.",
        f"- Best old baseline per split: `{score(totals['best_old'], totals['episodes'])}`.",
        f"- Best CAU/v0.2 per split: `{score(totals['best_cau_v02'], totals['episodes'])}`.",
        f"- Best non-oracle per split including old baselines, v0.2, and CAU: `{score(totals['best_all'], totals['episodes'])}`.",
        (
            f"- Best one-feature deployable preflight gate: `{best_gate['gate_id']}` selects "
            f"`{best_gate['selected_successes']}/{best_gate['eval_episodes']}`, "
            f"{int(best_gate['delta_vs_always_v02']):+d} versus always-v0.2 and "
            f"{int(best_gate['delta_vs_always_cau']):+d} versus always-CAU."
        ),
        "",
        "## Best Gate Per Split",
        "",
        "| split | selected | selected score | v0.2 | CAU | best old | estimated positive mass |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in per_split_rows:
        selected = str(row["best_gate_selected_method"]).replace("positive_nn_risk_union_top40", "v0.2")
        lines.append(
            "| {split_seed} | {selected} | {best_gate_selected_successes}/{eval_episodes} | "
            "{v02_selected_successes}/{eval_episodes} | {cau_successes}/{eval_episodes} | "
            "{best_old_baseline_successes}/{eval_episodes} | {estimated_positive_mass} |".format(
                selected=selected,
                **row,
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "- The strongest simple rule is an estimated-positive-mass split gate: choose CAU on "
                "`303`, `404`, and `505`, and choose v0.2 on `101` and `202`."
            ),
            "- This recovers the CAU/v0.2 per-split oracle on these five splits, but only post-hoc.",
            "- It still does not solve the split404 positive-only anchor loss: the all-method non-oracle oracle remains `4/250` higher because positive-only beats CAU on split404.",
            "- Treat this as the next fresh-validation hypothesis, not as a claim-bearing method.",
            "",
            "## Artifacts",
            "",
            f"- Per-split portfolio CSV: `{per_split_csv}`.",
            f"- Gate scan CSV: `{gate_scan_csv}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    target_gate = next(
        row
        for row in scan_rows
        if row["feature"] == "estimated_positive_mass"
        and row["direction"] == "gt"
        and row["selected_successes"] == 208
    )
    expected = {
        "always_v02": 197,
        "always_cau": 193,
        "best_old": 192,
        "best_cau_v02": 208,
        "best_all": 212,
        "best_gate": 208,
        "estimated_mass_gate": 208,
    }
    actual = {
        "always_v02": totals["always_v02"],
        "always_cau": totals["always_cau"],
        "best_old": totals["best_old"],
        "best_cau_v02": totals["best_cau_v02"],
        "best_all": totals["best_all"],
        "best_gate": int(best_gate["selected_successes"]),
        "estimated_mass_gate": int(target_gate["selected_successes"]),
    }
    if actual != expected:
        raise AssertionError(f"unexpected CAU/v0.2 portfolio aggregate: {actual}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
