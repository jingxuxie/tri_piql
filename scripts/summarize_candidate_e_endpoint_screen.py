from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path("results/final_paper_v02")
OUT_DIR = Path("results/candidate_breakthrough")

SUMMARY_OUT = OUT_DIR / "candidate_e_endpoint_screen_summary.csv"
PER_INITIAL_50_OUT = OUT_DIR / "candidate_e_endpoint_screen_per_initial_50.csv"
REPORT_OUT = OUT_DIR / "candidate_e_endpoint_screen_REPORT.md"


@dataclass(frozen=True)
class EvalSpec:
    method_id: str
    label: str
    episode_metrics: Path
    eval_episodes: int
    kind: str


BASELINE_50 = (
    EvalSpec(
        method_id="positive_only_nn_top40",
        label="Positive-only NN top40",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        eval_episodes=50,
        kind="baseline",
    ),
    EvalSpec(
        method_id="weighted_bc_full_pool",
        label="Weighted BC full pool",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        eval_episodes=50,
        kind="baseline",
    ),
    EvalSpec(
        method_id="triage_v01_adaptive_masscap",
        label="TRIAGE-BC v0.1 hard support",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_triage_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        eval_episodes=50,
        kind="baseline",
    ),
    EvalSpec(
        method_id="v02_positive_nn_risk_union_top40",
        label="v0.2 positive-NN/risk union top40",
        episode_metrics=ROOT
        / "ablations"
        / "v02_fresh_endpoint_200ep_can40"
        / "split404"
        / "positive_nn_risk_union_top40"
        / "eval_50ep"
        / "episode_metrics.csv",
        eval_episodes=50,
        kind="baseline",
    ),
    EvalSpec(
        method_id="candidate_a_transition_weighted_e200",
        label="Candidate A transition-weighted",
        episode_metrics=OUT_DIR / "candidate_a_tw_can404_e200_eval50" / "episode_metrics.csv",
        eval_episodes=50,
        kind="candidate_a",
    ),
    EvalSpec(
        method_id="candidate_e_initial_gate_weighted_e200",
        label="Candidate E initial support-distance gate (isolated RNG)",
        episode_metrics=OUT_DIR / "candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng" / "episode_metrics.csv",
        eval_episodes=50,
        kind="candidate_e",
    ),
)

FIRST20 = (
    EvalSpec(
        method_id="positive_only_nn_top40_first20",
        label="Positive-only NN top40",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        eval_episodes=20,
        kind="baseline",
    ),
    EvalSpec(
        method_id="candidate_b_router_no_bias_first20",
        label="Candidate B router labeled support, no bias",
        episode_metrics=OUT_DIR / "candidate_b_router_pos_weighted_margin_nobias_eval20" / "episode_metrics.csv",
        eval_episodes=20,
        kind="candidate_b",
    ),
    EvalSpec(
        method_id="candidate_c_sequence_mask_e200_first20",
        label="Candidate C sequence-mask e200",
        episode_metrics=OUT_DIR / "candidate_c_mask_can404_e200_eval20_epoch200" / "episode_metrics.csv",
        eval_episodes=20,
        kind="candidate_c",
    ),
    EvalSpec(
        method_id="candidate_d_negative_action_e100_first20",
        label="Candidate D negative-action e100",
        episode_metrics=OUT_DIR / "candidate_d_neg0p1_can404_e200_eval20" / "episode_metrics.csv",
        eval_episodes=20,
        kind="candidate_d",
    ),
    EvalSpec(
        method_id="candidate_e_initial_gate_weighted_first20",
        label="Candidate E initial support-distance gate (isolated RNG)",
        episode_metrics=OUT_DIR / "candidate_e_initial_posdist_gate_weighted_split404_eval20_isolated_rng" / "episode_metrics.csv",
        eval_episodes=20,
        kind="candidate_e",
    ),
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


def rows_for_spec(spec: EvalSpec) -> list[dict[str, str]]:
    rows = read_csv(spec.episode_metrics)[: spec.eval_episodes]
    if len(rows) != spec.eval_episodes:
        raise ValueError(f"{spec.method_id}: expected {spec.eval_episodes} rows, found {len(rows)}")
    return rows


def summarize(spec: EvalSpec) -> dict[str, object]:
    rows = rows_for_spec(spec)
    successes = [float(row["success"]) for row in rows]
    lengths = [float(row["length"]) for row in rows]
    out = {
        "method_id": spec.method_id,
        "label": spec.label,
        "kind": spec.kind,
        "eval_episodes": spec.eval_episodes,
        "success_count": int(sum(successes)),
        "success_rate": f"{sum(successes) / len(rows):.3f}",
        "avg_len": f"{sum(lengths) / len(lengths):.1f}",
    }
    if "initial_gate_open" in rows[0]:
        out["gate_open_count"] = sum(int(row["initial_gate_open"]) for row in rows)
        out["choices_positive"] = sum(int(row["choices_positive"]) for row in rows)
        out["choices_weighted"] = sum(int(row["choices_weighted"]) for row in rows)
    else:
        out["gate_open_count"] = ""
        out["choices_positive"] = ""
        out["choices_weighted"] = ""
    return out


def per_initial_rows(specs: tuple[EvalSpec, ...]) -> list[dict[str, object]]:
    buckets: dict[str, dict[str, object]] = defaultdict(dict)
    for spec in specs:
        counts: dict[str, int] = defaultdict(int)
        totals: dict[str, int] = defaultdict(int)
        gate_opens: dict[str, int] = defaultdict(int)
        for row in rows_for_spec(spec):
            demo_id = row["initial_demo_id"]
            counts[demo_id] += int(float(row["success"]))
            totals[demo_id] += 1
            if "initial_gate_open" in row:
                gate_opens[demo_id] += int(row["initial_gate_open"])
        for demo_id in totals:
            bucket = buckets[demo_id]
            bucket["initial_demo_id"] = demo_id
            bucket[spec.method_id] = counts[demo_id]
            if spec.kind == "candidate_e":
                bucket["candidate_e_gate_open_count"] = gate_opens[demo_id]
    return [buckets[key] for key in sorted(buckets, key=lambda value: int(value.split("_")[-1]))]


def write_report(summary_rows: list[dict[str, object]], first20_rows: list[dict[str, object]], initial_rows: list[dict[str, object]]) -> None:
    by_method = {row["method_id"]: row for row in summary_rows}
    positive = by_method["positive_only_nn_top40"]
    candidate = by_method["candidate_e_initial_gate_weighted_e200"]
    lines = [
        "# Candidate E Initial-Gate Endpoint Screen",
        "",
        "Candidate E is a confidence-preserving router: use positive-only by default,",
        "but if the positive policy's initial action is far from labeled positive support",
        "(`initial_anchor_pos_dist > 3.0`), force the weighted policy for that episode.",
        "The router evaluator uses isolated per-policy RNG streams for this report.",
        "",
        "## 50-Episode Split-404 Summary",
        "",
        "| method | kind | success | rate | avg len | gate opens |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['label']} | {row['kind']} | {row['success_count']}/50 | "
            f"{row['success_rate']} | {row['avg_len']} | {row['gate_open_count']} |"
        )
    lines.extend(
        [
            "",
            "## First-20 Screen",
            "",
            "| method | kind | success | rate | gate opens |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in first20_rows:
        lines.append(
            f"| {row['label']} | {row['kind']} | {row['success_count']}/20 | "
            f"{row['success_rate']} | {row['gate_open_count']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                f"- Candidate E reaches `{candidate['success_count']}/50`, "
                f"`{int(candidate['success_count']) - int(positive['success_count']):+d}/50` versus positive-only."
            ),
            "- The gate opens only on the high initial positive-support-distance state `demo_39`, where positive-only fails and weighted BC has coverage.",
            "- This is the strongest split-404 candidate in this branch, but it is still a hand-thresholded one-split result.",
            "- Multi-split promotion requires the Candidate F anchor calibration rather than this fixed positive-anchor gate alone.",
            "",
            "## Per-Initial 50-Episode Counts",
            "",
            "| initial | positive | weighted | v0.1 | union | cand A | cand E | gate opens |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in initial_rows:
        lines.append(
            "| {initial_demo_id} | {positive_only_nn_top40} | {weighted_bc_full_pool} | "
            "{triage_v01_adaptive_masscap} | {v02_positive_nn_risk_union_top40} | "
            "{candidate_a_transition_weighted_e200} | {candidate_e_initial_gate_weighted_e200} | "
            "{candidate_e_gate_open_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{SUMMARY_OUT}`.",
            f"- Per-initial CSV: `{PER_INITIAL_50_OUT}`.",
            "- Initial feature audit: `results/candidate_breakthrough/candidate_e_initial_gate_audit_REPORT.md`.",
            "- 50-episode eval: `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng/REPORT.md`.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary_rows = [summarize(spec) for spec in BASELINE_50]
    first20_rows = [summarize(spec) for spec in FIRST20]
    initial_rows = per_initial_rows(BASELINE_50)
    write_csv(
        SUMMARY_OUT,
        [*summary_rows, *first20_rows],
        [
            "method_id",
            "label",
            "kind",
            "eval_episodes",
            "success_count",
            "success_rate",
            "avg_len",
            "gate_open_count",
            "choices_positive",
            "choices_weighted",
        ],
    )
    write_csv(PER_INITIAL_50_OUT, initial_rows, list(initial_rows[0]))
    write_report(summary_rows, first20_rows, initial_rows)
    expected = {
        "positive_only_nn_top40": 39,
        "weighted_bc_full_pool": 33,
        "triage_v01_adaptive_masscap": 36,
        "v02_positive_nn_risk_union_top40": 27,
        "candidate_a_transition_weighted_e200": 30,
        "candidate_e_initial_gate_weighted_e200": 46,
        "candidate_e_initial_gate_weighted_first20": 19,
    }
    got = {row["method_id"]: int(row["success_count"]) for row in [*summary_rows, *first20_rows]}
    for key, value in expected.items():
        if got.get(key) != value:
            raise AssertionError(f"{key}: expected {value}, got {got.get(key)}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
