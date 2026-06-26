from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path("results/final_paper_v02")
OUT_DIR = Path("results/candidate_breakthrough")
PREFLIGHT_RECIPE = OUT_DIR / "candidate_d_negative_action_preflight" / "candidate_d_negative_action_recipe.json"
EXTRA_PREFLIGHT_RECIPE = (
    OUT_DIR / "candidate_x_extra_negative_action_preflight" / "candidate_d_negative_action_recipe.json"
)


@dataclass(frozen=True)
class EvalSpec:
    method_id: str
    label: str
    episode_metrics: Path
    kind: str
    train_epochs: int
    checkpoint_stem: str | None = None


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
        method_id="candidate_c_sequence_mask_e200",
        label="Candidate C sequence-mask e200",
        episode_metrics=OUT_DIR / "candidate_c_mask_can404_e200_eval20_epoch200" / "episode_metrics.csv",
        kind="candidate_c",
        train_epochs=200,
    ),
    EvalSpec(
        method_id="candidate_d_negative_action_e100",
        label="Candidate D negative-action e100",
        episode_metrics=OUT_DIR / "candidate_d_neg0p1_can404_e200_eval20" / "episode_metrics.csv",
        kind="candidate_d",
        train_epochs=100,
        checkpoint_stem="model_epoch_100",
    ),
    EvalSpec(
        method_id="candidate_d_negative_action_e200",
        label="Candidate D negative-action e200",
        episode_metrics=OUT_DIR / "candidate_d_neg0p1_can404_e200_eval20" / "episode_metrics.csv",
        kind="candidate_d",
        train_epochs=200,
        checkpoint_stem="model_epoch_200",
    ),
    EvalSpec(
        method_id="candidate_x_extra_negative_action_e100",
        label="Candidate X extra-only negative-action e100",
        episode_metrics=OUT_DIR / "candidate_x_extra_neg0p1_can404_e200_eval20" / "episode_metrics.csv",
        kind="candidate_x",
        train_epochs=100,
        checkpoint_stem="model_epoch_100",
    ),
    EvalSpec(
        method_id="candidate_x_extra_negative_action_e200",
        label="Candidate X extra-only negative-action e200",
        episode_metrics=OUT_DIR / "candidate_x_extra_neg0p1_can404_e200_eval20" / "episode_metrics.csv",
        kind="candidate_x",
        train_epochs=200,
        checkpoint_stem="model_epoch_200",
    ),
)

SUMMARY_OUT = OUT_DIR / "candidate_d_endpoint_screen_summary.csv"
PER_INITIAL_OUT = OUT_DIR / "candidate_d_endpoint_screen_per_initial.csv"
REPORT_OUT = OUT_DIR / "candidate_d_endpoint_screen_REPORT.md"


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
    if spec.checkpoint_stem is not None:
        rows = [row for row in rows if Path(row["checkpoint"]).stem == spec.checkpoint_stem]
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
    extra_recipe = json.loads(EXTRA_PREFLIGHT_RECIPE.read_text(encoding="utf-8"))
    by_method = {row["method_id"]: row for row in summary_rows}
    positive = by_method["positive_only_nn_top40"]
    candidate_c = by_method["candidate_c_sequence_mask_e200"]
    candidate_rows = [row for row in summary_rows if row["kind"] in {"candidate_d", "candidate_x"}]
    best_candidate = max(candidate_rows, key=lambda row: int(row["success_count"]))

    def success(row: dict[str, object]) -> int:
        return int(row["success_count"])

    lines = [
        "# Candidate D Negative-Action Endpoint Screen",
        "",
        "This screen evaluates a conservative action-negative regularizer on the Can 40p/80b split-404 failure case.",
        "The BC loss uses the Candidate C sequence mask, and the hinge penalizes likelihood of the nearest labeled-negative action.",
        "",
        "## Preflight Audit",
        "",
        "| field | value |",
        "| --- | ---: |",
        f"| train demos | {recipe['train_demo_count']} |",
        f"| full-weight anchor demos | {recipe['anchor_demo_count']} |",
        f"| full-anchor negative-loss scope | {recipe.get('negative_loss_scope', 'selected')} |",
        f"| full-anchor negative-loss mass | {recipe['negative_loss_mass']} |",
        f"| extra-only negative-loss scope | {extra_recipe['negative_loss_scope']} |",
        f"| extra-only negative-loss mass | {extra_recipe['negative_loss_mass']} |",
        f"| extra positive selected mass | {recipe['extra_positive_mass']} |",
        f"| extra bad selected mass | {recipe['extra_bad_mass']} |",
        f"| mean selected nearest-negative obs distance | {recipe['selected_nearest_negative_obs_distance_mean']:.3f} |",
        f"| hinge weight | 0.1 |",
        f"| hinge margin | 0.5 |",
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
                f"- Best Candidate D checkpoint is `{best_candidate['label']}` at "
                f"`{success(best_candidate)}/20`, versus Candidate C `{success(candidate_c)}/20` "
                f"and positive-only `{success(positive)}/20`."
            ),
            "- Moving the hinge off the full-weight positive-anchor demos does not rescue the objective: the extra-only variant reaches only `14/20` at epoch 200.",
            "- Per-initial counts show neither hinge scope recovers `demo_39`; both remain below the Candidate C mask and positive-only anchor.",
            "- Do not scale negative-action hinge variants unchanged. The remaining transition-level route needs a different bad-action target or an explicit anchor-preserving objective.",
            "",
            "## Per-Initial Counts",
            "",
            "| initial | positive | weighted | v0.1 | cand C e200 | cand D e100 | cand D e200 | cand X e100 | cand X e200 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in initial_rows:
        lines.append(
            "| {initial_demo_id} | {positive_only_nn_top40} | {weighted_bc_full_pool} | "
            "{triage_v01_adaptive_masscap} | {candidate_c_sequence_mask_e200} | "
            "{candidate_d_negative_action_e100} | {candidate_d_negative_action_e200} | "
            "{candidate_x_extra_negative_action_e100} | {candidate_x_extra_negative_action_e200} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{SUMMARY_OUT}`.",
            f"- Per-initial CSV: `{PER_INITIAL_OUT}`.",
            "- Preflight report: `results/candidate_breakthrough/candidate_d_negative_action_preflight/candidate_d_negative_action_preflight_REPORT.md`.",
            "- Endpoint eval report: `results/candidate_breakthrough/candidate_d_neg0p1_can404_e200_eval20/REPORT.md`.",
            "- Extra-only preflight report: `results/candidate_breakthrough/candidate_x_extra_negative_action_preflight/candidate_d_negative_action_preflight_REPORT.md`.",
            "- Extra-only endpoint eval report: `results/candidate_breakthrough/candidate_x_extra_neg0p1_can404_e200_eval20/REPORT.md`.",
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
    expected = {
        "positive_only_nn_top40": 17,
        "weighted_bc_full_pool": 13,
        "triage_v01_adaptive_masscap": 14,
        "candidate_c_sequence_mask_e200": 16,
        "candidate_d_negative_action_e100": 14,
        "candidate_d_negative_action_e200": 13,
        "candidate_x_extra_negative_action_e100": 10,
        "candidate_x_extra_negative_action_e200": 14,
    }
    got = {row["method_id"]: int(row["success_count"]) for row in summary_rows}
    if got != expected:
        raise AssertionError(f"unexpected Candidate D totals: {got}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
