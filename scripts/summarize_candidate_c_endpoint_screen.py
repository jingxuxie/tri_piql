from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path("results/final_paper_v02")
OUT_DIR = Path("results/candidate_breakthrough")
PREFLIGHT_RECIPE = OUT_DIR / "candidate_c_sequence_mask_preflight" / "candidate_c_sequence_mask_recipe.json"


@dataclass(frozen=True)
class EvalSpec:
    method_id: str
    label: str
    episode_metrics: Path
    kind: str
    train_epochs: int


METHODS = (
    EvalSpec(
        method_id="positive_only_nn_top40",
        label="Positive-only NN top40",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        kind="baseline",
        train_epochs=200,
    ),
    EvalSpec(
        method_id="weighted_bc_full_pool",
        label="Weighted BC full pool",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        kind="baseline",
        train_epochs=200,
    ),
    EvalSpec(
        method_id="triage_v01_adaptive_masscap",
        label="TRIAGE-BC v0.1 hard support",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_triage_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        kind="baseline",
        train_epochs=200,
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
        kind="baseline",
        train_epochs=200,
    ),
    EvalSpec(
        method_id="candidate_a_transition_weighted_e200",
        label="Candidate A transition-weighted e200",
        episode_metrics=OUT_DIR / "candidate_a_tw_can404_e200_eval20" / "episode_metrics.csv",
        kind="candidate_a",
        train_epochs=200,
    ),
    EvalSpec(
        method_id="router_labeled_no_bias",
        label="Candidate B router labeled support, no bias",
        episode_metrics=OUT_DIR / "candidate_b_router_pos_weighted_margin_nobias_eval20" / "episode_metrics.csv",
        kind="candidate_b",
        train_epochs=200,
    ),
    EvalSpec(
        method_id="router_anchor_support_no_bias",
        label="Candidate B router positive-anchor support, no bias",
        episode_metrics=OUT_DIR / "candidate_b_router_pos_weighted_anchor_support_eval20" / "episode_metrics.csv",
        kind="candidate_b",
        train_epochs=200,
    ),
    EvalSpec(
        method_id="candidate_c_sequence_mask_e100",
        label="Candidate C sequence-mask e100",
        episode_metrics=OUT_DIR / "candidate_c_mask_can404_e200_eval20_epoch100" / "episode_metrics.csv",
        kind="candidate_c",
        train_epochs=100,
    ),
    EvalSpec(
        method_id="candidate_c_sequence_mask_e200",
        label="Candidate C sequence-mask e200",
        episode_metrics=OUT_DIR / "candidate_c_mask_can404_e200_eval20_epoch200" / "episode_metrics.csv",
        kind="candidate_c",
        train_epochs=200,
    ),
)

SUMMARY_OUT = OUT_DIR / "candidate_c_endpoint_screen_summary.csv"
PER_INITIAL_OUT = OUT_DIR / "candidate_c_endpoint_screen_per_initial.csv"
REPORT_OUT = OUT_DIR / "candidate_c_endpoint_screen_REPORT.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def rows_for_spec(spec: EvalSpec, eval_episodes: int = 20) -> list[dict[str, str]]:
    rows = read_csv(spec.episode_metrics)
    if spec.method_id == "candidate_a_transition_weighted_e200":
        rows = [row for row in rows if Path(row["checkpoint"]).stem == "model_epoch_200"]
    rows = rows[:eval_episodes]
    if len(rows) != eval_episodes:
        raise ValueError(f"{spec.method_id}: expected {eval_episodes} rows, found {len(rows)}")
    return rows


def summarize(spec: EvalSpec) -> dict[str, object]:
    rows = rows_for_spec(spec)
    successes = [float(row["success"]) for row in rows]
    lengths = [float(row["length"]) for row in rows]
    return {
        "method_id": spec.method_id,
        "label": spec.label,
        "kind": spec.kind,
        "train_epochs": spec.train_epochs,
        "eval_episodes": len(rows),
        "success_count": int(sum(successes)),
        "success_rate": f"{sum(successes) / len(rows):.3f}",
        "avg_len": f"{sum(lengths) / len(lengths):.1f}",
    }


def per_initial_rows() -> list[dict[str, object]]:
    buckets: dict[str, dict[str, object]] = defaultdict(dict)
    for spec in METHODS:
        counts: dict[str, int] = defaultdict(int)
        totals: dict[str, int] = defaultdict(int)
        for row in rows_for_spec(spec):
            demo_id = row["initial_demo_id"]
            counts[demo_id] += int(float(row["success"]))
            totals[demo_id] += 1
        for demo_id in totals:
            bucket = buckets[demo_id]
            bucket["initial_demo_id"] = demo_id
            bucket[spec.method_id] = counts[demo_id]
    return [buckets[key] for key in sorted(buckets, key=lambda value: int(value.split("_")[-1]))]


def write_report(summary_rows: list[dict[str, object]], initial_rows: list[dict[str, object]]) -> None:
    recipe = json.loads(PREFLIGHT_RECIPE.read_text(encoding="utf-8"))
    by_method = {row["method_id"]: row for row in summary_rows}
    positive = by_method["positive_only_nn_top40"]
    weighted = by_method["weighted_bc_full_pool"]
    candidate_100 = by_method["candidate_c_sequence_mask_e100"]
    candidate_200 = by_method["candidate_c_sequence_mask_e200"]
    best_candidate = max((candidate_100, candidate_200), key=lambda row: int(row["success_count"]))
    best_non_c = max(
        [row for row in summary_rows if row["kind"] != "candidate_c"],
        key=lambda row: int(row["success_count"]),
    )

    def success(row: dict[str, object]) -> int:
        return int(row["success_count"])

    lines = [
        "# Candidate C Sequence-Mask Endpoint Screen",
        "",
        "This screen evaluates the conservative sequence-mask recipe on the Can 40p/80b split-404 failure case.",
        "The implementation keeps the full weighted training pool for recurrent context, gives positive-anchor demos full loss mass,",
        "and admits only high-score, positive-margin timesteps from extra weighted-pool demos.",
        "",
        "## Preflight Mask Audit",
        "",
        "| field | value |",
        "| --- | ---: |",
        f"| train demos | {recipe['train_demo_count']} |",
        f"| full-weight anchor demos | {recipe['anchor_demo_count']} |",
        f"| extra demos in weighted pool | {recipe['extra_demo_count']} |",
        f"| extra positive demos with selected mass | {recipe['extra_positive_demo_count']} |",
        f"| extra bad demos with selected mass | {recipe['extra_bad_demo_count']} |",
        f"| extra positive selected mass | {recipe['extra_positive_mass']} |",
        f"| extra bad selected mass | {recipe['extra_bad_mass']} |",
        f"| extra bad masked fraction | {recipe['extra_bad_masked_fraction']:.3f} |",
        f"| extra selected mass fraction of all transitions | {recipe['extra_mass_fraction_total']:.3f} |",
        "",
        "## First-20 Endpoint Summary",
        "",
        "| method | kind | epochs | success | rate | avg len |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['label']} | {row['kind']} | {row['train_epochs']} | "
            f"{row['success_count']}/20 | {row['success_rate']} | {row['avg_len']} |"
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                f"- Best Candidate C checkpoint is `{best_candidate['label']}` at "
                f"`{success(best_candidate)}/20`, versus positive-only `{success(positive)}/20` "
                f"and weighted BC `{success(weighted)}/20`."
            ),
            (
                f"- The best non-C row in this first-20 table is `{best_non_c['label']}` at "
                f"`{success(best_non_c)}/20`."
            ),
            "- The conservative mask preserves broad context but does not beat the positive-only anchor on this split.",
            "- Do not scale this Candidate C recipe unchanged. The remaining headroom is more likely in explicit action-negative regularization or a better confidence-preserving router than in this mask alone.",
            "",
            "## Per-Initial Counts",
            "",
            "| initial | positive | weighted | v0.1 | union | cand A | router no-bias | router anchor | cand C e100 | cand C e200 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in initial_rows:
        lines.append(
            "| {initial_demo_id} | {positive_only_nn_top40} | {weighted_bc_full_pool} | "
            "{triage_v01_adaptive_masscap} | {v02_positive_nn_risk_union_top40} | "
            "{candidate_a_transition_weighted_e200} | {router_labeled_no_bias} | "
            "{router_anchor_support_no_bias} | {candidate_c_sequence_mask_e100} | "
            "{candidate_c_sequence_mask_e200} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{SUMMARY_OUT}`.",
            f"- Per-initial CSV: `{PER_INITIAL_OUT}`.",
            "- Epoch-100 eval report: `results/candidate_breakthrough/candidate_c_mask_can404_e200_eval20_epoch100/REPORT.md`.",
            "- Epoch-200 eval report: `results/candidate_breakthrough/candidate_c_mask_can404_e200_eval20_epoch200/REPORT.md`.",
            "- Preflight report: `results/candidate_breakthrough/candidate_c_sequence_mask_preflight/candidate_c_sequence_mask_preflight_REPORT.md`.",
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
            "train_epochs",
            "eval_episodes",
            "success_count",
            "success_rate",
            "avg_len",
        ],
    )
    write_csv(PER_INITIAL_OUT, initial_rows, list(initial_rows[0]))
    write_report(summary_rows, initial_rows)
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
