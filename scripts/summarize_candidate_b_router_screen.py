from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path("results/final_paper_v02")
OUT_DIR = Path("results/candidate_breakthrough")


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    label: str
    episode_metrics: Path
    kind: str


METHODS = (
    MethodSpec(
        method_id="positive_only_nn_top40",
        label="Positive-only NN top40",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        kind="baseline",
    ),
    MethodSpec(
        method_id="weighted_bc_full_pool",
        label="Weighted BC full pool",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        kind="baseline",
    ),
    MethodSpec(
        method_id="triage_v01_adaptive_masscap",
        label="TRIAGE-BC v0.1 hard support",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_triage_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        kind="baseline",
    ),
    MethodSpec(
        method_id="v02_positive_nn_risk_union_top40",
        label="v0.2 positive-NN/risk union top40",
        episode_metrics=ROOT
        / "ablations"
        / "v02_fresh_endpoint_200ep_can40"
        / "split404"
        / "positive_nn_risk_union_top40"
        / "eval_50ep"
        / "episode_metrics.csv",
        kind="baseline",
    ),
    MethodSpec(
        method_id="candidate_a_transition_weighted_e200",
        label="Candidate A transition-weighted e200",
        episode_metrics=OUT_DIR / "candidate_a_tw_can404_e200_eval20" / "episode_metrics.csv",
        kind="candidate_a",
    ),
    MethodSpec(
        method_id="router_labeled_positive_bias",
        label="Router labeled support, positive bias 0.25",
        episode_metrics=OUT_DIR / "candidate_b_router_pos_weighted_margin_eval20" / "episode_metrics.csv",
        kind="candidate_b_router",
    ),
    MethodSpec(
        method_id="router_labeled_no_bias",
        label="Router labeled support, no bias",
        episode_metrics=OUT_DIR / "candidate_b_router_pos_weighted_margin_nobias_eval20" / "episode_metrics.csv",
        kind="candidate_b_router",
    ),
    MethodSpec(
        method_id="router_anchor_support_no_bias",
        label="Router positive-anchor support, no bias",
        episode_metrics=OUT_DIR / "candidate_b_router_pos_weighted_anchor_support_eval20" / "episode_metrics.csv",
        kind="candidate_b_router",
    ),
    MethodSpec(
        method_id="router_labeled_thr0p10",
        label="Router labeled support, switch threshold 0.10",
        episode_metrics=OUT_DIR / "candidate_b_router_pos_weighted_margin_thr0p10_eval20" / "episode_metrics.csv",
        kind="candidate_b_router",
    ),
    MethodSpec(
        method_id="router_labeled_thr0p05",
        label="Router labeled support, switch threshold 0.05",
        episode_metrics=OUT_DIR / "candidate_b_router_pos_weighted_margin_thr0p05_eval20" / "episode_metrics.csv",
        kind="candidate_b_router",
    ),
)

SUMMARY_OUT = OUT_DIR / "candidate_b_router_screen_summary.csv"
PER_INITIAL_OUT = OUT_DIR / "candidate_b_router_screen_per_initial.csv"
REPORT_OUT = OUT_DIR / "candidate_b_router_screen_REPORT.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def rows_for_spec(spec: MethodSpec, eval_episodes: int = 20) -> list[dict[str, str]]:
    rows = read_csv(spec.episode_metrics)
    if spec.method_id == "candidate_a_transition_weighted_e200":
        rows = [row for row in rows if Path(row["checkpoint"]).stem == "model_epoch_200"]
    rows = rows[:eval_episodes]
    if len(rows) != eval_episodes:
        raise ValueError(f"{spec.method_id}: expected {eval_episodes} rows, found {len(rows)}")
    return rows


def summarize(spec: MethodSpec) -> dict[str, object]:
    rows = rows_for_spec(spec)
    successes = [float(row["success"]) for row in rows]
    lengths = [float(row["length"]) for row in rows]
    out = {
        "method_id": spec.method_id,
        "label": spec.label,
        "kind": spec.kind,
        "eval_episodes": len(rows),
        "success_count": int(sum(successes)),
        "success_rate": f"{sum(successes) / len(rows):.3f}",
        "avg_len": f"{sum(lengths) / len(lengths):.1f}",
    }
    for key in ("choices_positive", "choices_weighted"):
        if key in rows[0]:
            out[key] = sum(int(row[key]) for row in rows)
        else:
            out[key] = ""
    return out


def per_initial_rows() -> list[dict[str, object]]:
    buckets: dict[str, dict[str, object]] = defaultdict(dict)
    for spec in METHODS:
        method_rows = rows_for_spec(spec)
        counts: dict[str, int] = defaultdict(int)
        totals: dict[str, int] = defaultdict(int)
        positive_choices: dict[str, int] = defaultdict(int)
        weighted_choices: dict[str, int] = defaultdict(int)
        for row in method_rows:
            demo_id = row["initial_demo_id"]
            counts[demo_id] += int(float(row["success"]))
            totals[demo_id] += 1
            if "choices_positive" in row:
                positive_choices[demo_id] += int(row["choices_positive"])
                weighted_choices[demo_id] += int(row["choices_weighted"])
        for demo_id in totals:
            bucket = buckets[demo_id]
            bucket["initial_demo_id"] = demo_id
            bucket[spec.method_id] = counts[demo_id]
            if spec.kind == "candidate_b_router":
                bucket[f"{spec.method_id}_positive_choices"] = positive_choices[demo_id]
                bucket[f"{spec.method_id}_weighted_choices"] = weighted_choices[demo_id]
    rows = [buckets[key] for key in sorted(buckets, key=lambda value: int(value.split("_")[-1]))]
    for row in rows:
        row["oracle_best_count"] = max(int(row.get(spec.method_id, 0)) for spec in METHODS)
    return rows


def write_report(summary_rows: list[dict[str, object]], initial_rows: list[dict[str, object]]) -> None:
    by_method = {row["method_id"]: row for row in summary_rows}
    positive = by_method["positive_only_nn_top40"]
    best_router = max(
        [row for row in summary_rows if row["kind"] == "candidate_b_router"],
        key=lambda row: int(row["success_count"]),
    )
    oracle = sum(int(row["oracle_best_count"]) for row in initial_rows)
    lines = [
        "# Candidate B Router Screen",
        "",
        "This screen evaluates deployable action-level routers over existing split-404 policies.",
        "All loaded RNN policies are called at every timestep, and the router selects one action",
        "using labeled-support state-action margins.",
        "",
        "## First-20 Summary",
        "",
        "| method | kind | success | rate | avg len | positive choices | weighted choices |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['label']} | {row['kind']} | {row['success_count']}/20 | {row['success_rate']} | "
            f"{row['avg_len']} | {row['choices_positive']} | {row['choices_weighted']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                f"- Best deployable router is `{best_router['label']}` at "
                f"`{best_router['success_count']}/20`, versus positive-only "
                f"`{positive['success_count']}/20`."
            ),
            f"- Non-deployable per-initial oracle over these rows is `{oracle}/20`, so routing has headroom.",
            "- The current margin gate is not enough to beat the positive-only anchor: it tends to recover `demo_99` and sometimes `demo_39`, but loses `demo_189`.",
            "- Small switch-threshold variants do not solve the tradeoff: threshold `0.10` stays at `16/20`, while threshold `0.05` drops to `14/20`.",
            "- Do not scale this router unchanged. A better Candidate B needs an initial-state or confidence rule that preserves `demo_189` while identifying true coverage gaps.",
            "",
            "## Per-Initial Counts",
            "",
            "| initial | positive | weighted | v0.1 | union | cand A | router bias | router no-bias | router anchor-support | thr0.10 | thr0.05 | oracle |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in initial_rows:
        lines.append(
            "| {initial_demo_id} | {positive_only_nn_top40} | {weighted_bc_full_pool} | "
            "{triage_v01_adaptive_masscap} | {v02_positive_nn_risk_union_top40} | "
            "{candidate_a_transition_weighted_e200} | {router_labeled_positive_bias} | "
            "{router_labeled_no_bias} | {router_anchor_support_no_bias} | {router_labeled_thr0p10} | "
            "{router_labeled_thr0p05} | {oracle_best_count} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{SUMMARY_OUT}`.",
            f"- Per-initial CSV: `{PER_INITIAL_OUT}`.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary_rows = [summarize(spec) for spec in METHODS]
    initial_rows = per_initial_rows()
    write_csv(
        SUMMARY_OUT,
        summary_rows,
        [
            "method_id",
            "label",
            "kind",
            "eval_episodes",
            "success_count",
            "success_rate",
            "avg_len",
            "choices_positive",
            "choices_weighted",
        ],
    )
    write_csv(
        PER_INITIAL_OUT,
        initial_rows,
        [
            "initial_demo_id",
            "positive_only_nn_top40",
            "weighted_bc_full_pool",
            "triage_v01_adaptive_masscap",
            "v02_positive_nn_risk_union_top40",
            "candidate_a_transition_weighted_e200",
            "router_labeled_positive_bias",
            "router_labeled_no_bias",
            "router_anchor_support_no_bias",
            "router_labeled_thr0p10",
            "router_labeled_thr0p05",
            "oracle_best_count",
            "router_labeled_positive_bias_positive_choices",
            "router_labeled_positive_bias_weighted_choices",
            "router_labeled_no_bias_positive_choices",
            "router_labeled_no_bias_weighted_choices",
            "router_anchor_support_no_bias_positive_choices",
            "router_anchor_support_no_bias_weighted_choices",
            "router_labeled_thr0p10_positive_choices",
            "router_labeled_thr0p10_weighted_choices",
            "router_labeled_thr0p05_positive_choices",
            "router_labeled_thr0p05_weighted_choices",
        ],
    )
    write_report(summary_rows, initial_rows)
    expected = {
        "positive_only_nn_top40": 17,
        "weighted_bc_full_pool": 13,
        "triage_v01_adaptive_masscap": 14,
        "v02_positive_nn_risk_union_top40": 7,
        "candidate_a_transition_weighted_e200": 12,
        "router_labeled_positive_bias": 15,
        "router_labeled_no_bias": 16,
        "router_anchor_support_no_bias": 16,
        "router_labeled_thr0p10": 16,
        "router_labeled_thr0p05": 14,
    }
    got = {row["method_id"]: int(row["success_count"]) for row in summary_rows}
    if got != expected:
        raise AssertionError(f"unexpected router screen totals: {got}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
