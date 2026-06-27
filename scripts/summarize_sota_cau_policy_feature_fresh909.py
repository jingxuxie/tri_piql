#!/usr/bin/env python3
"""Summarize the fresh split909 CAU policy-feature gate screen."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"
DEFAULT_LIMIT = 20

METHODS = [
    {
        "method_id": "positive_only_nn",
        "label": "Positive-only NN",
        "path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "per_seed"
        / "can_paired_pos40_bad80_split909_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
    },
    {
        "method_id": "weighted_bc",
        "label": "Weighted BC",
        "path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "per_seed"
        / "can_paired_pos40_bad80_split909_weighted_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
    },
    {
        "method_id": "triage_bc_v01",
        "label": "TRIAGE-BC v0.1",
        "path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "per_seed"
        / "can_paired_pos40_bad80_split909_triage_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
    },
    {
        "method_id": "candidate_e_gate",
        "label": "Candidate E gate",
        "path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "candidate_e_eval"
        / "can909_candidate_e_gate_eval50"
        / "episode_metrics.csv",
    },
    {
        "method_id": "cau_action_conflict",
        "label": "CAU action-conflict",
        "path": DEFAULT_OUT_DIR
        / "cau_action_conflict_can909_b005_m05_eval20"
        / "episode_metrics.csv",
    },
    {
        "method_id": "cau_policy_feature_gate",
        "label": "CAU policy-feature gate",
        "path": DEFAULT_OUT_DIR
        / "cau_policy_feature_gate_can909_eval20"
        / "episode_metrics.csv",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--episode-limit", type=int, default=DEFAULT_LIMIT)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda row: int(row["episode"]))
    return rows


def limited_rows(rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    selected = [row for row in rows if int(row["episode"]) < limit]
    if len(selected) != limit:
        raise ValueError(f"expected {limit} rows, found {len(selected)}")
    return selected


def success(row: dict[str, str]) -> int:
    return int(float(row["success"]) > 0.5)


def row_key(row: dict[str, str]) -> tuple[int, str]:
    return int(row["episode"]), row["initial_demo_id"]


def score(count: int, episodes: int) -> str:
    return f"{count}/{episodes}"


def mean(rows: list[dict[str, str]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def gate_open_count(rows: list[dict[str, str]]) -> str:
    if "initial_gate_open" not in rows[0]:
        return ""
    return str(sum(int(float(row["initial_gate_open"])) for row in rows))


def choice_count(rows: list[dict[str, str]], key: str) -> str:
    if key not in rows[0]:
        return ""
    return str(sum(int(float(row[key])) for row in rows))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def main() -> None:
    args = parse_args()

    all_rows = {method["method_id"]: read_rows(method["path"]) for method in METHODS}
    screen_rows = {
        method_id: limited_rows(rows, args.episode_limit)
        for method_id, rows in all_rows.items()
    }
    positive_by_key = {
        row_key(row): success(row) for row in screen_rows["positive_only_nn"]
    }

    summary_rows: list[dict[str, object]] = []
    for method in METHODS:
        method_id = method["method_id"]
        rows = screen_rows[method_id]
        by_key = {row_key(row): success(row) for row in rows}
        if set(by_key) != set(positive_by_key):
            missing = sorted(set(positive_by_key) - set(by_key))
            extra = sorted(set(by_key) - set(positive_by_key))
            raise ValueError(
                f"{method_id} does not match positive-only starts; "
                f"missing={missing[:3]} extra={extra[:3]}"
            )
        successes = sum(by_key.values())
        gains = sum(
            1
            for key, value in by_key.items()
            if value == 1 and positive_by_key[key] == 0
        )
        losses = sum(
            1
            for key, value in by_key.items()
            if value == 0 and positive_by_key[key] == 1
        )
        full_successes = sum(success(row) for row in all_rows[method_id])
        summary_rows.append(
            {
                "method_id": method_id,
                "label": method["label"],
                "screen_episodes": len(rows),
                "screen_successes": successes,
                "screen_score": score(successes, len(rows)),
                "screen_success_rate": f"{successes / len(rows):.3f}",
                "delta_vs_positive": successes - sum(positive_by_key.values()),
                "gains_vs_positive": gains,
                "losses_vs_positive": losses,
                "mean_return": f"{mean(rows, 'return'):.3f}",
                "mean_length": f"{mean(rows, 'length'):.1f}",
                "gate_open_episodes": gate_open_count(rows),
                "choices_positive": choice_count(rows, "choices_positive"),
                "choices_weighted": choice_count(rows, "choices_weighted"),
                "choices_cau": choice_count(rows, "choices_cau"),
                "all_available_episodes": len(all_rows[method_id]),
                "all_available_score": score(full_successes, len(all_rows[method_id])),
                "source": method["path"],
            }
        )

    out_dir = args.out_dir
    summary_path = out_dir / "cau_policy_feature_fresh909_summary.csv"
    report_path = out_dir / "CAU_POLICY_FEATURE_FRESH909_REPORT.md"
    fields = [
        "method_id",
        "label",
        "screen_episodes",
        "screen_successes",
        "screen_score",
        "screen_success_rate",
        "delta_vs_positive",
        "gains_vs_positive",
        "losses_vs_positive",
        "mean_return",
        "mean_length",
        "gate_open_episodes",
        "choices_positive",
        "choices_weighted",
        "choices_cau",
        "all_available_episodes",
        "all_available_score",
        "source",
    ]
    write_csv(summary_path, summary_rows, fields)

    positive = next(row for row in summary_rows if row["method_id"] == "positive_only_nn")
    gate = next(row for row in summary_rows if row["method_id"] == "cau_policy_feature_gate")
    cau = next(row for row in summary_rows if row["method_id"] == "cau_action_conflict")
    non_gate_references = [
        row for row in summary_rows if row["method_id"] != "cau_policy_feature_gate"
    ]
    best_reference_successes = max(
        int(row["screen_successes"]) for row in non_gate_references
    )
    best_reference_labels = [
        row["label"]
        for row in non_gate_references
        if int(row["screen_successes"]) == best_reference_successes
    ]
    gate_delta = int(gate["delta_vs_positive"])
    gate_opens = int(gate["gate_open_episodes"] or 0)
    if gate_delta > 0:
        decision_note = (
            "This is a promising fresh method-seed result, not yet a paper-ready "
            "dominance claim: it needs 50-episode confirmation and at least one "
            "more fresh split because the rule was selected after completed "
            "development splits and still allows anchor losses in LOO audit."
        )
    elif gate_opens == 0:
        decision_note = (
            "This is neutral transfer, not a promotable method result: the fixed "
            "rule defers entirely to positive-only on this screen, so it preserves "
            "the anchor but does not capture any CAU-helped starts."
        )
    elif gate_delta == 0:
        decision_note = (
            "This is neutral transfer, not a promotable method result: the fixed "
            "rule changes some starts but does not improve over positive-only."
        )
    else:
        decision_note = (
            "This is a negative transfer result: the fixed rule loses to the "
            "positive-only anchor on the matched first-20 screen."
        )

    report_lines = [
        "# CAU Policy-Feature Fresh Split909 Screen",
        "",
        "This report evaluates a predeclared policy-feature gate on fresh split909.",
        "The gate uses the pooled development rule from the completed CAU policy-feature audit:",
        "",
        "- route from positive-only to CAU when `alt_logp_margin_vs_anchor > 0.757864` or `alt_support_margin > 0.837440`.",
        "- `anchor` is positive-only NN and `alt` is CAU action-conflict.",
        "- comparisons below use the first 20 matched valid-positive starts for every method.",
        "",
        "## Decision",
        "",
        f"- Positive-only NN reaches `{positive['screen_score']}` on the matched first-20 screen.",
        f"- CAU action-conflict alone reaches `{cau['screen_score']}`.",
        f"- The fixed policy-feature gate reaches `{gate['screen_score']}` with `{gate['gains_vs_positive']}` gains and `{gate['losses_vs_positive']}` losses versus positive-only.",
        f"- The best non-gate reference on this first-20 screen is `{' / '.join(best_reference_labels)}` at `{score(best_reference_successes, args.episode_limit)}`.",
        f"- {decision_note}",
        "",
        "## First-20 Matched Starts",
        "",
        *markdown_table(
            summary_rows,
            [
                "label",
                "screen_score",
                "delta_vs_positive",
                "gains_vs_positive",
                "losses_vs_positive",
                "gate_open_episodes",
                "all_available_score",
            ],
        ),
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_path}`.",
        "- Policy-feature gate eval: `results/sota_candidate/cau_policy_feature_gate_can909_eval20/REPORT.md`.",
        "- CAU action-conflict eval: `results/sota_candidate/cau_action_conflict_can909_b005_m05_eval20/REPORT.md`.",
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
