from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


ROOT = Path("results/final_paper_v02")
OUT_DIR = Path("results/candidate_breakthrough")
SPLIT_SEED = 404
TOTAL_HIDDEN_POSITIVE = 40
TOTAL_HIDDEN_BAD = 80


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    label: str
    role: str
    episode_metrics: Path
    support_audit: Path | None = None
    setup_summary: Path | None = None
    setup_candidate_id: str | None = None


METHODS = (
    MethodSpec(
        method_id="positive_only_nn_top40",
        label="Positive-only NN top40",
        role="strong no-bad-label anchor",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        support_audit=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_positive_only_nn_policy0"
        / "support_audit.csv",
    ),
    MethodSpec(
        method_id="weighted_bc_full_pool",
        label="Weighted BC full pool",
        role="soft broad-coverage baseline",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        support_audit=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_weighted_bc_policy0"
        / "support_audit.csv",
    ),
    MethodSpec(
        method_id="triage_v01_adaptive_masscap",
        label="TRIAGE-BC v0.1 hard support",
        role="v0.1 hard-support baseline",
        episode_metrics=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_triage_bc_policy0"
        / "eval"
        / "episode_metrics.csv",
        support_audit=ROOT
        / "per_seed"
        / "can_paired_pos40_bad80_split404_triage_bc_policy0"
        / "support_audit.csv",
    ),
    MethodSpec(
        method_id="v02_positive_nn_risk_union_top40",
        label="v0.2 positive-NN/risk union top40",
        role="v0.2 selected hard-union branch",
        episode_metrics=ROOT
        / "ablations"
        / "v02_fresh_endpoint_200ep_can40"
        / "split404"
        / "positive_nn_risk_union_top40"
        / "eval_50ep"
        / "episode_metrics.csv",
        setup_summary=ROOT
        / "ablations"
        / "v02_fresh_endpoint_200ep_can40"
        / "split404"
        / "endpoint_setup_summary.csv",
        setup_candidate_id="positive_nn_risk_union_top40",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt_float(value: float) -> str:
    return f"{value:.3f}"


def fmt_len(value: float) -> str:
    return f"{value:.1f}"


def read_support_summary(method: MethodSpec) -> dict[str, object]:
    if method.support_audit is not None:
        rows = read_csv(method.support_audit)
        hidden_positive = sum(row["hidden_label"] == "positive" for row in rows)
        hidden_bad = sum(row["hidden_label"] == "bad" for row in rows)
        selected = len(rows)
    elif method.setup_summary is not None and method.setup_candidate_id is not None:
        matches = [
            row
            for row in read_csv(method.setup_summary)
            if row["candidate_id"] == method.setup_candidate_id
        ]
        if len(matches) != 1:
            raise ValueError(
                f"expected one setup row for {method.setup_candidate_id}, found {len(matches)}"
            )
        row = matches[0]
        selected = int(row["selected_unlabeled"])
        hidden_positive = int(row["selected_hidden_positive"])
        hidden_bad = int(row["selected_hidden_bad"])
    else:
        raise ValueError(f"no support source for {method.method_id}")

    return {
        "selected_unlabeled": selected,
        "selected_hidden_positive": hidden_positive,
        "selected_hidden_bad": hidden_bad,
        "support_purity": hidden_positive / selected if selected else 0.0,
        "hidden_positive_recall": hidden_positive / TOTAL_HIDDEN_POSITIVE,
        "hidden_bad_admission": hidden_bad / TOTAL_HIDDEN_BAD,
    }


def aggregate_episodes(path: Path) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(path):
        grouped.setdefault(row["initial_demo_id"], []).append(row)

    by_initial: dict[str, dict[str, object]] = {}
    total_success = 0
    total_episodes = 0
    total_length = 0.0
    timeout_failures = 0
    failures = 0
    for initial_demo_id, rows in grouped.items():
        successes = [int(round(float(row["success"]))) for row in rows]
        lengths = [float(row["length"]) for row in rows]
        success_count = sum(successes)
        failed_lengths = [
            length for success, length in zip(successes, lengths) if success == 0
        ]
        timeout_count = sum(length >= 380.0 for length in failed_lengths)
        by_initial[initial_demo_id] = {
            "success_count": success_count,
            "eval_episodes": len(rows),
            "success_rate": success_count / len(rows),
            "avg_length": sum(lengths) / len(rows),
            "failure_count": len(failed_lengths),
            "timeout_failure_count": timeout_count,
        }
        total_success += success_count
        total_episodes += len(rows)
        total_length += sum(lengths)
        timeout_failures += timeout_count
        failures += len(failed_lengths)

    summary = {
        "success_count": total_success,
        "eval_episodes": total_episodes,
        "success_rate": total_success / total_episodes,
        "avg_length": total_length / total_episodes,
        "failure_count": failures,
        "timeout_failure_count": timeout_failures,
    }
    return by_initial, summary


def classify_row(row: dict[str, object]) -> str:
    pos = int(row["positive_only_success_count"])
    weighted = int(row["weighted_success_count"])
    v01 = int(row["v01_success_count"])
    union = int(row["union_success_count"])
    best = max(pos, weighted, v01, union)
    if pos - union >= 3:
        return "positive_anchor_regression"
    if weighted - union >= 3 and weighted >= pos:
        return "weighted_coverage_rescue"
    if union == best and union > pos:
        return "union_rescue"
    if union == best:
        return "union_tied_best"
    if union < best:
        return "union_under_best"
    return "mixed"


def initial_rows(stats: dict[str, dict[str, dict[str, object]]]) -> list[dict[str, object]]:
    demos = sorted(
        stats["positive_only_nn_top40"],
        key=lambda demo_id: int(demo_id.removeprefix("demo_")),
    )
    rows: list[dict[str, object]] = []
    for demo_id in demos:
        pos = stats["positive_only_nn_top40"][demo_id]
        weighted = stats["weighted_bc_full_pool"][demo_id]
        v01 = stats["triage_v01_adaptive_masscap"][demo_id]
        union = stats["v02_positive_nn_risk_union_top40"][demo_id]
        row: dict[str, object] = {
            "split_seed": SPLIT_SEED,
            "initial_demo_id": demo_id,
            "positive_only_success_count": pos["success_count"],
            "weighted_success_count": weighted["success_count"],
            "v01_success_count": v01["success_count"],
            "union_success_count": union["success_count"],
            "eval_episodes": pos["eval_episodes"],
            "positive_only_avg_length": fmt_len(float(pos["avg_length"])),
            "weighted_avg_length": fmt_len(float(weighted["avg_length"])),
            "v01_avg_length": fmt_len(float(v01["avg_length"])),
            "union_avg_length": fmt_len(float(union["avg_length"])),
            "union_minus_positive_successes": int(union["success_count"])
            - int(pos["success_count"]),
            "union_minus_best_successes": int(union["success_count"])
            - max(
                int(pos["success_count"]),
                int(weighted["success_count"]),
                int(v01["success_count"]),
            ),
        }
        row["case_type"] = classify_row(row)
        rows.append(row)
    return rows


def pairwise_rows(initials: list[dict[str, object]]) -> list[dict[str, object]]:
    specs = [
        ("positive_only_nn_top40", "v02_positive_nn_risk_union_top40", "positive_only", "union"),
        ("weighted_bc_full_pool", "v02_positive_nn_risk_union_top40", "weighted", "union"),
        ("triage_v01_adaptive_masscap", "v02_positive_nn_risk_union_top40", "v01", "union"),
        ("positive_only_nn_top40", "weighted_bc_full_pool", "positive_only", "weighted"),
    ]
    rows: list[dict[str, object]] = []
    for left_id, right_id, left_prefix, right_prefix in specs:
        left_key = f"{left_prefix}_success_count"
        right_key = f"{right_prefix}_success_count"
        left_total = sum(int(row[left_key]) for row in initials)
        right_total = sum(int(row[right_key]) for row in initials)
        left_better_starts = sum(int(row[left_key]) > int(row[right_key]) for row in initials)
        right_better_starts = sum(int(row[right_key]) > int(row[left_key]) for row in initials)
        tied_starts = len(initials) - left_better_starts - right_better_starts
        left_adv_episode_count = sum(
            max(0, int(row[left_key]) - int(row[right_key])) for row in initials
        )
        right_adv_episode_count = sum(
            max(0, int(row[right_key]) - int(row[left_key])) for row in initials
        )
        rows.append(
            {
                "left_method": left_id,
                "right_method": right_id,
                "left_success_count": left_total,
                "right_success_count": right_total,
                "left_minus_right_successes": left_total - right_total,
                "left_better_initials": left_better_starts,
                "right_better_initials": right_better_starts,
                "tied_initials": tied_starts,
                "left_advantage_episode_count": left_adv_episode_count,
                "right_advantage_episode_count": right_adv_episode_count,
            }
        )
    return rows


def method_rows(stats: dict[str, dict[str, dict[str, object]]], summaries: dict[str, dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for method in METHODS:
        support = read_support_summary(method)
        summary = summaries[method.method_id]
        rows.append(
            {
                "split_seed": SPLIT_SEED,
                "method_id": method.method_id,
                "method_label": method.label,
                "role": method.role,
                "success_count": summary["success_count"],
                "eval_episodes": summary["eval_episodes"],
                "success_rate": fmt_float(float(summary["success_rate"])),
                "avg_length": fmt_len(float(summary["avg_length"])),
                "selected_unlabeled": support["selected_unlabeled"],
                "selected_hidden_positive": support["selected_hidden_positive"],
                "selected_hidden_bad": support["selected_hidden_bad"],
                "support_purity": fmt_float(float(support["support_purity"])),
                "hidden_positive_recall": fmt_float(float(support["hidden_positive_recall"])),
                "hidden_bad_admission": fmt_float(float(support["hidden_bad_admission"])),
            }
        )
    return rows


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def build_report(
    method_summary: list[dict[str, object]],
    initial_summary: list[dict[str, object]],
    pairwise_summary: list[dict[str, object]],
) -> str:
    method_by_id = {row["method_id"]: row for row in method_summary}
    pos = method_by_id["positive_only_nn_top40"]
    union = method_by_id["v02_positive_nn_risk_union_top40"]
    weighted = method_by_id["weighted_bc_full_pool"]
    v01 = method_by_id["triage_v01_adaptive_masscap"]
    pos_vs_union = next(
        row
        for row in pairwise_summary
        if row["left_method"] == "positive_only_nn_top40"
        and row["right_method"] == "v02_positive_nn_risk_union_top40"
    )
    weighted_vs_union = next(
        row
        for row in pairwise_summary
        if row["left_method"] == "weighted_bc_full_pool"
        and row["right_method"] == "v02_positive_nn_risk_union_top40"
    )
    regression_rows = [
        row for row in initial_summary if row["case_type"] == "positive_anchor_regression"
    ]
    coverage_rows = [
        row for row in initial_summary if row["case_type"] == "weighted_coverage_rescue"
    ]
    union_rescue_rows = [
        row for row in initial_summary if row["case_type"] == "union_rescue"
    ]

    lines = [
        "# Candidate-Breakthrough Split-404 Audit",
        "",
        "This is a failure-focused preflight audit for `triage_bc_candidate_breakthrough_plan.md`.",
        "It reuses completed fresh Can 40p/80b split-404 endpoint rollouts and does not run a new policy.",
        "",
        "## Summary",
        "",
        f"- Positive-only NN is the split-404 endpoint winner at `{pos['success_count']}/{pos['eval_episodes']}`.",
        f"- The v0.2 hard union reaches `{union['success_count']}/{union['eval_episodes']}`, "
        f"which is `{int(union['success_count']) - int(pos['success_count'])}` successes below positive-only.",
        f"- Weighted BC reaches `{weighted['success_count']}/{weighted['eval_episodes']}` and v0.1 hard support reaches `{v01['success_count']}/{v01['eval_episodes']}`.",
        f"- The support audit does not explain the reversal by hidden-label counts: union selects "
        f"`{union['selected_hidden_positive']}/{TOTAL_HIDDEN_POSITIVE}` hidden positives and "
        f"`{union['selected_hidden_bad']}/{TOTAL_HIDDEN_BAD}` hidden bad demos, versus positive-only "
        f"`{pos['selected_hidden_positive']}/{TOTAL_HIDDEN_POSITIVE}` and "
        f"`{pos['selected_hidden_bad']}/{TOTAL_HIDDEN_BAD}`.",
        f"- Per-initial-state accounting shows positive-only beats union on "
        f"`{pos_vs_union['left_better_initials']}/10` starts, union beats positive-only on "
        f"`{pos_vs_union['right_better_initials']}/10`, and they tie on "
        f"`{pos_vs_union['tied_initials']}/10`.",
        f"- Weighted BC beats union on `{weighted_vs_union['left_better_initials']}/10` starts, "
        f"showing that broad coverage is still useful on some split-404 states.",
        "",
        "Interpretation: split 404 is not mainly a global support-purity failure. The hard union has higher hidden-positive recall than positive-only with the same hidden-bad count, yet it loses many endpoint successes. This points to sequence/action-distribution effects and state-specific branch choice, matching the motivation for transition-risk weighting, sequence masking, or state-level gating.",
        "",
        "## Method Summary",
        "",
    ]
    lines.extend(
        markdown_table(
            method_summary,
            [
                "method_id",
                "success_count",
                "eval_episodes",
                "avg_length",
                "selected_hidden_positive",
                "selected_hidden_bad",
                "hidden_positive_recall",
                "hidden_bad_admission",
            ],
        )
    )
    lines.extend(["", "## Pairwise Endpoint Accounting", ""])
    lines.extend(
        markdown_table(
            pairwise_summary,
            [
                "left_method",
                "right_method",
                "left_minus_right_successes",
                "left_better_initials",
                "right_better_initials",
                "tied_initials",
            ],
        )
    )
    lines.extend(["", "## Representative Failure Modes", ""])
    if regression_rows:
        lines.append(
            "- Positive-anchor regressions: "
            + ", ".join(
                f"{row['initial_demo_id']} "
                f"(positive {row['positive_only_success_count']}/5, union {row['union_success_count']}/5)"
                for row in regression_rows
            )
            + "."
        )
    if coverage_rows:
        lines.append(
            "- Weighted-coverage rescues: "
            + ", ".join(
                f"{row['initial_demo_id']} "
                f"(weighted {row['weighted_success_count']}/5, union {row['union_success_count']}/5)"
                for row in coverage_rows
            )
            + "."
        )
    if union_rescue_rows:
        lines.append(
            "- Union rescues: "
            + ", ".join(
                f"{row['initial_demo_id']} "
                f"(union {row['union_success_count']}/5, positive {row['positive_only_success_count']}/5)"
                for row in union_rescue_rows
            )
            + "."
        )
    lines.extend(["", "## Per-Initial-State Table", ""])
    lines.extend(
        markdown_table(
            initial_summary,
            [
                "initial_demo_id",
                "case_type",
                "positive_only_success_count",
                "weighted_success_count",
                "v01_success_count",
                "union_success_count",
                "union_minus_best_successes",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## Candidate Implications",
            "",
            "- Candidate A/C should keep the positive-only anchor at the transition or timestep level instead of replacing it with a globally unioned support set.",
            "- Candidate B should use state-level fallback: starts such as `demo_89` and `demo_99` need positive-anchor protection, while starts such as `demo_39` need broader weighted coverage.",
            "- More global threshold tuning is unlikely to fix this split because the hard-union support labels are already strong; the failure appears after support is converted into a sequence policy.",
            "",
            "## Outputs",
            "",
            "- `results/candidate_breakthrough/can40_split404_method_summary.csv`",
            "- `results/candidate_breakthrough/can40_split404_initial_state_audit.csv`",
            "- `results/candidate_breakthrough/can40_split404_pairwise_summary.csv`",
            "- `results/candidate_breakthrough/can40_split404_failure_audit_REPORT.md`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    stats: dict[str, dict[str, dict[str, object]]] = {}
    summaries: dict[str, dict[str, object]] = {}
    for method in METHODS:
        by_initial, summary = aggregate_episodes(method.episode_metrics)
        stats[method.method_id] = by_initial
        summaries[method.method_id] = summary

    method_summary = method_rows(stats, summaries)
    initial_summary = initial_rows(stats)
    pairwise_summary = pairwise_rows(initial_summary)

    expected_totals = {
        "positive_only_nn_top40": 39,
        "weighted_bc_full_pool": 33,
        "triage_v01_adaptive_masscap": 36,
        "v02_positive_nn_risk_union_top40": 27,
    }
    for row in method_summary:
        expected = expected_totals[row["method_id"]]
        if int(row["success_count"]) != expected:
            raise AssertionError(
                f"{row['method_id']} expected {expected} successes, got {row['success_count']}"
            )

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        out_dir / "can40_split404_method_summary.csv",
        method_summary,
        [
            "split_seed",
            "method_id",
            "method_label",
            "role",
            "success_count",
            "eval_episodes",
            "success_rate",
            "avg_length",
            "selected_unlabeled",
            "selected_hidden_positive",
            "selected_hidden_bad",
            "support_purity",
            "hidden_positive_recall",
            "hidden_bad_admission",
        ],
    )
    write_csv(
        out_dir / "can40_split404_initial_state_audit.csv",
        initial_summary,
        [
            "split_seed",
            "initial_demo_id",
            "case_type",
            "positive_only_success_count",
            "weighted_success_count",
            "v01_success_count",
            "union_success_count",
            "eval_episodes",
            "positive_only_avg_length",
            "weighted_avg_length",
            "v01_avg_length",
            "union_avg_length",
            "union_minus_positive_successes",
            "union_minus_best_successes",
        ],
    )
    write_csv(
        out_dir / "can40_split404_pairwise_summary.csv",
        pairwise_summary,
        [
            "left_method",
            "right_method",
            "left_success_count",
            "right_success_count",
            "left_minus_right_successes",
            "left_better_initials",
            "right_better_initials",
            "tied_initials",
            "left_advantage_episode_count",
            "right_advantage_episode_count",
        ],
    )
    report = build_report(method_summary, initial_summary, pairwise_summary)
    (out_dir / "can40_split404_failure_audit_REPORT.md").write_text(
        report, encoding="utf-8"
    )
    print(f"wrote {out_dir / 'can40_split404_failure_audit_REPORT.md'}")


if __name__ == "__main__":
    main()
