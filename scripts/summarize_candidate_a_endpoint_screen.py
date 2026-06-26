from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path("results/final_paper_v02")
OUT_DIR = Path("results/candidate_breakthrough")
PREFLIGHT_RECIPE = OUT_DIR / "candidate_a_transition_weight_preflight" / "candidate_a_transition_weight_recipe.json"


@dataclass(frozen=True)
class EvalSpec:
    method_id: str
    label: str
    episode_metrics: Path
    train_epochs: int
    selected_hidden_positive: int | None = None
    selected_hidden_bad: int | None = None


BASELINE_50 = (
    EvalSpec(
        method_id="positive_only_nn_top40",
        label="Positive-only NN top40",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
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
        train_epochs=200,
        selected_hidden_positive=39,
        selected_hidden_bad=5,
    ),
)

CANDIDATE_50 = EvalSpec(
    method_id="candidate_a_transition_weighted_e200",
    label="Candidate A transition-weighted",
    episode_metrics=OUT_DIR / "candidate_a_tw_can404_e200_eval50" / "episode_metrics.csv",
    train_epochs=200,
)

FIRST20_SCREENS = (
    EvalSpec(
        method_id="candidate_a_transition_weighted_e50",
        label="Candidate A transition-weighted e50",
        episode_metrics=OUT_DIR / "candidate_a_tw_can404_e50_eval20" / "episode_metrics.csv",
        train_epochs=50,
    ),
    EvalSpec(
        method_id="candidate_a_transition_weighted_e100",
        label="Candidate A transition-weighted e100",
        episode_metrics=OUT_DIR / "candidate_a_tw_can404_e200_eval20" / "episode_metrics.csv",
        train_epochs=100,
    ),
    EvalSpec(
        method_id="candidate_a_transition_weighted_e200",
        label="Candidate A transition-weighted e200",
        episode_metrics=OUT_DIR / "candidate_a_tw_can404_e200_eval20" / "episode_metrics.csv",
        train_epochs=200,
    ),
)

SUMMARY_OUT = OUT_DIR / "candidate_a_endpoint_screen_summary.csv"
FIRST20_OUT = OUT_DIR / "candidate_a_endpoint_screen_first20.csv"
PER_INITIAL_OUT = OUT_DIR / "candidate_a_endpoint_screen_per_initial.csv"
REPORT_OUT = OUT_DIR / "candidate_a_endpoint_screen_REPORT.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_candidate_support() -> tuple[int, int]:
    metadata = json.loads(PREFLIGHT_RECIPE.read_text(encoding="utf-8"))
    summary = metadata["summary"]
    return int(summary["hidden_positive_selected"]), int(summary["hidden_bad_selected"])


def support_from_audit(path: Path) -> tuple[int, int]:
    rows = read_csv(path)
    return (
        sum(row["hidden_label"] == "positive" for row in rows),
        sum(row["hidden_label"] == "bad" for row in rows),
    )


def support_counts(spec: EvalSpec) -> tuple[int | None, int | None]:
    if spec.selected_hidden_positive is not None and spec.selected_hidden_bad is not None:
        return spec.selected_hidden_positive, spec.selected_hidden_bad
    if spec.method_id == "candidate_a_transition_weighted_e200":
        return load_candidate_support()
    audit_paths = {
        "positive_only_nn_top40": ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "support_audit.csv",
        "weighted_bc_full_pool": ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
        / "support_audit.csv",
        "triage_v01_adaptive_masscap": ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_triage_bc_policy0"
        / "support_audit.csv",
    }
    path = audit_paths.get(spec.method_id)
    if path is None or not path.exists():
        return None, None
    return support_from_audit(path)


def rows_for_checkpoint(spec: EvalSpec) -> list[dict[str, str]]:
    rows = read_csv(spec.episode_metrics)
    if spec.method_id == "candidate_a_transition_weighted_e100":
        return [row for row in rows if Path(row["checkpoint"]).stem == "model_epoch_100"]
    if spec.method_id == "candidate_a_transition_weighted_e200" and "eval20" in str(spec.episode_metrics):
        return [row for row in rows if Path(row["checkpoint"]).stem == "model_epoch_200"]
    return rows


def summarize(spec: EvalSpec, eval_episodes: int) -> dict[str, object]:
    rows = rows_for_checkpoint(spec)[:eval_episodes]
    if len(rows) != eval_episodes:
        raise ValueError(f"{spec.method_id}: expected {eval_episodes} rows, found {len(rows)}")
    successes = [float(row["success"]) for row in rows]
    lengths = [float(row["length"]) for row in rows]
    hidden_pos, hidden_bad = support_counts(spec)
    return {
        "method_id": spec.method_id,
        "label": spec.label,
        "train_epochs": spec.train_epochs,
        "eval_episodes": eval_episodes,
        "success_count": int(sum(successes)),
        "success_rate": f"{sum(successes) / eval_episodes:.3f}",
        "avg_len": f"{sum(lengths) / len(lengths):.1f}",
        "selected_hidden_positive": "" if hidden_pos is None else hidden_pos,
        "selected_hidden_bad": "" if hidden_bad is None else hidden_bad,
    }


def per_initial(specs: tuple[EvalSpec, ...], eval_episodes: int) -> list[dict[str, object]]:
    grouped: dict[str, dict[str, int]] = {}
    for spec in specs:
        rows = rows_for_checkpoint(spec)[:eval_episodes]
        for row in rows:
            demo_id = row["initial_demo_id"]
            if demo_id not in grouped:
                grouped[demo_id] = {"initial_demo_id": demo_id}
            grouped[demo_id][spec.method_id] = grouped[demo_id].get(spec.method_id, 0) + int(float(row["success"]))
    return [grouped[key] for key in sorted(grouped, key=lambda value: int(value.split("_")[-1]))]


def write_report(summary_rows: list[dict[str, object]], first20_rows: list[dict[str, object]], per_initial_rows: list[dict[str, object]]) -> None:
    by_method = {row["method_id"]: row for row in summary_rows}
    candidate = by_method["candidate_a_transition_weighted_e200"]
    union = by_method["v02_positive_nn_risk_union_top40"]
    weighted = by_method["weighted_bc_full_pool"]
    positive = by_method["positive_only_nn_top40"]
    v01 = by_method["triage_v01_adaptive_masscap"]

    def success(row: dict[str, object]) -> int:
        return int(row["success_count"])

    lines = [
        "# Candidate A Endpoint Screen",
        "",
        "This report summarizes the transition-weighted Candidate A screen on the Can 40p/80b split-404 failure case.",
        "",
        "## 50-Episode Comparison",
        "",
        "| method | support hidden pos/bad | success | rate | avg len |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summary_rows:
        support = f"{row['selected_hidden_positive']}/{row['selected_hidden_bad']}"
        lines.append(
            f"| {row['label']} | {support} | {row['success_count']}/50 | {row['success_rate']} | {row['avg_len']} |"
        )
    lines.extend(
        [
            "",
            "## Read",
            "",
            (
                f"- Candidate A reaches `{success(candidate)}/50`, which is "
                f"`{success(candidate) - success(union):+d}` versus the v0.2 hard union "
                f"but `{success(candidate) - success(weighted):+d}` versus weighted BC, "
                f"`{success(candidate) - success(v01):+d}` versus v0.1, and "
                f"`{success(candidate) - success(positive):+d}` versus positive-only NN."
            ),
            "- The current transition-weight recipe is therefore an improvement over hard union, not a breakthrough.",
            "- The result argues against scaling this Candidate A recipe unchanged; the next attempt should change the recipe or move to Candidate C/B.",
            "",
            "## First-20 Training-Length Screen",
            "",
            "| method | epochs | success | rate |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in first20_rows:
        lines.append(f"| {row['label']} | {row['train_epochs']} | {row['success_count']}/20 | {row['success_rate']} |")
    lines.extend(
        [
            "",
            "## Per-Initial 50-Episode Counts",
            "",
            "| initial | positive-only | weighted | v0.1 | union | candidate A |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in per_initial_rows:
        lines.append(
            "| {initial_demo_id} | {positive_only_nn_top40} | {weighted_bc_full_pool} | "
            "{triage_v01_adaptive_masscap} | {v02_positive_nn_risk_union_top40} | "
            "{candidate_a_transition_weighted_e200} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- 50-episode summary CSV: `{SUMMARY_OUT}`.",
            f"- First-20 screen CSV: `{FIRST20_OUT}`.",
            f"- Per-initial CSV: `{PER_INITIAL_OUT}`.",
            f"- Candidate A 50-episode eval report: `results/candidate_breakthrough/candidate_a_tw_can404_e200_eval50/REPORT.md`.",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    summary_specs = (*BASELINE_50, CANDIDATE_50)
    summary_rows = [summarize(spec, 50) for spec in summary_specs]
    first20_rows = [
        *[summarize(spec, 20) for spec in BASELINE_50],
        *[summarize(spec, 20) for spec in FIRST20_SCREENS],
    ]
    per_initial_rows = per_initial(summary_specs, 50)

    write_csv(
        SUMMARY_OUT,
        summary_rows,
        [
            "method_id",
            "label",
            "train_epochs",
            "eval_episodes",
            "success_count",
            "success_rate",
            "avg_len",
            "selected_hidden_positive",
            "selected_hidden_bad",
        ],
    )
    write_csv(
        FIRST20_OUT,
        first20_rows,
        [
            "method_id",
            "label",
            "train_epochs",
            "eval_episodes",
            "success_count",
            "success_rate",
            "avg_len",
            "selected_hidden_positive",
            "selected_hidden_bad",
        ],
    )
    write_csv(
        PER_INITIAL_OUT,
        per_initial_rows,
        [
            "initial_demo_id",
            "positive_only_nn_top40",
            "weighted_bc_full_pool",
            "triage_v01_adaptive_masscap",
            "v02_positive_nn_risk_union_top40",
            "candidate_a_transition_weighted_e200",
        ],
    )
    write_report(summary_rows, first20_rows, per_initial_rows)
    expected = {
        "positive_only_nn_top40": 39,
        "weighted_bc_full_pool": 33,
        "triage_v01_adaptive_masscap": 36,
        "v02_positive_nn_risk_union_top40": 27,
        "candidate_a_transition_weighted_e200": 30,
    }
    got = {row["method_id"]: int(row["success_count"]) for row in summary_rows}
    if got != expected:
        raise AssertionError(f"unexpected 50-episode summary: {got}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
