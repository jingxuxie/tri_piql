#!/usr/bin/env python3
"""Summarize the Candidate J Lift606 router screen."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_g_fresh_preflight"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def metric_row(path: Path) -> dict[str, str]:
    rows = read_csv(path)
    if len(rows) != 1:
        raise ValueError(f"{path}: expected one row")
    return rows[0]


def count_successes(path: Path, limit: int | None = None) -> tuple[int, int, float]:
    rows = read_csv(path)
    if limit is not None:
        rows = rows[:limit]
    successes = sum(int(float(row["success"])) for row in rows)
    avg_len = sum(float(row["length"]) for row in rows) / len(rows)
    return successes, len(rows), avg_len


def metric_success(path: Path) -> tuple[int, int, float]:
    row = metric_row(path)
    episodes = int(row["eval_episodes"])
    successes = int(round(float(row["success_rate"]) * episodes))
    return successes, episodes, float(row["avg_len"])


def first20_baselines() -> list[dict[str, object]]:
    specs = [
        (
            "positive_only_nn",
            OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv",
            OUT / "lift606_positive_epoch200_eval50" / "episode_metrics.csv",
        ),
        (
            "triage_bc",
            OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv",
            OUT / "lift606_triage_epoch200_eval50" / "episode_metrics.csv",
        ),
        (
            "weighted_bc",
            OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv",
            OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv",
        ),
    ]
    rows = []
    for method, first20_path, eval50_path in specs:
        s20, n20, l20 = count_successes(first20_path, limit=20)
        s50, n50, l50 = count_successes(eval50_path)
        rows.append(
            {
                "method": method,
                "first20_successes": s20,
                "first20_episodes": n20,
                "first20_avg_len": round(l20, 3),
                "eval50_successes": s50,
                "eval50_episodes": n50,
                "eval50_avg_len": round(l50, 3),
            }
        )
    return rows


def router_rows() -> list[dict[str, object]]:
    specs = [
        (
            "margin_labeled",
            OUT / "lift606_router_pos_triage_weighted_margin_eval20" / "metrics.csv",
            "Unrestricted per-step support-margin router over positive, triage, weighted.",
        ),
        (
            "positive_anchor_labeled",
            OUT / "lift606_router_pos_triage_weighted_anchor_eval20" / "metrics.csv",
            "Per-step margin router that keeps positive unless another branch is better.",
        ),
        (
            "positive_anchor_anchor_support",
            OUT / "lift606_router_pos_triage_weighted_anchor_support_eval20" / "metrics.csv",
            "Same anchor router, but positive support includes Lift606 positive-NN selected demos.",
        ),
        (
            "init_posdist3_pos_to_triage",
            OUT / "lift606_router_pos_to_triage_initdist3_eval20" / "metrics.csv",
            "Episode-level gate: switch positive to triage if initial positive action is far from positive support.",
        ),
    ]
    rows = []
    for method, path, note in specs:
        s, n, avg_len = metric_success(path)
        row = metric_row(path)
        rows.append(
            {
                "method": method,
                "successes": s,
                "episodes": n,
                "avg_len": round(avg_len, 3),
                "choices_positive": int(row.get("choices_positive", 0)),
                "choices_triage": int(row.get("choices_triage", 0)),
                "choices_weighted": int(row.get("choices_weighted", 0)),
                "note": note,
            }
        )
    return rows


def outcome_by_demo(path: Path, limit: int = 20) -> dict[str, int]:
    rows = read_csv(path)[:limit]
    return {row["initial_demo_id"]: int(float(row["success"])) for row in rows}


def initial_distance_threshold_audit() -> list[dict[str, object]]:
    feature_rows = read_csv(OUT / "lift606_router_pos_to_triage_initdist3_eval20" / "episode_metrics.csv")
    pos = outcome_by_demo(OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv")
    tri = outcome_by_demo(OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv")
    distances = sorted({float(row["initial_anchor_pos_dist"]) for row in feature_rows})
    thresholds = [0.0, *[(a + b) / 2.0 for a, b in zip(distances, distances[1:])], max(distances) + 1.0]
    rows = []
    for threshold in thresholds:
        successes = 0
        switches = 0
        for row in feature_rows:
            demo = row["initial_demo_id"]
            use_triage = float(row["initial_anchor_pos_dist"]) > threshold
            switches += int(use_triage)
            successes += tri[demo] if use_triage else pos[demo]
        rows.append(
            {
                "threshold": round(threshold, 6),
                "successes": successes,
                "episodes": len(feature_rows),
                "switches": switches,
            }
        )
    best = max(row["successes"] for row in rows)
    return [row for row in rows if row["successes"] == best]


def per_initial_rows() -> list[dict[str, object]]:
    pos = outcome_by_demo(OUT / "lift606_positive_epoch200_eval20" / "episode_metrics.csv")
    tri = outcome_by_demo(OUT / "lift606_triage_epoch200_eval20" / "episode_metrics.csv")
    weighted = outcome_by_demo(OUT / "lift606_weighted_epoch200_eval50" / "episode_metrics.csv")
    init_rows = read_csv(OUT / "lift606_router_pos_to_triage_initdist3_eval20" / "episode_metrics.csv")
    router_sources = {
        "margin_labeled": OUT / "lift606_router_pos_triage_weighted_margin_eval20" / "episode_metrics.csv",
        "anchor_labeled": OUT / "lift606_router_pos_triage_weighted_anchor_eval20" / "episode_metrics.csv",
        "anchor_support": OUT / "lift606_router_pos_triage_weighted_anchor_support_eval20" / "episode_metrics.csv",
        "init_posdist3": OUT / "lift606_router_pos_to_triage_initdist3_eval20" / "episode_metrics.csv",
    }
    router_outcomes = {
        name: outcome_by_demo(path)
        for name, path in router_sources.items()
    }
    rows = []
    for row in init_rows:
        demo = row["initial_demo_id"]
        rows.append(
            {
                "initial_demo_id": demo,
                "initial_positive_pos_dist": round(float(row["initial_anchor_pos_dist"]), 6),
                "positive": pos[demo],
                "triage": tri[demo],
                "weighted": weighted[demo],
                "margin_labeled": router_outcomes["margin_labeled"][demo],
                "anchor_labeled": router_outcomes["anchor_labeled"][demo],
                "anchor_support": router_outcomes["anchor_support"][demo],
                "init_posdist3": router_outcomes["init_posdist3"][demo],
                "oracle_pos_triage_weighted": max(pos[demo], tri[demo], weighted[demo]),
            }
        )
    return rows


def format_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def main() -> None:
    baseline_rows = first20_baselines()
    routers = router_rows()
    best_thresholds = initial_distance_threshold_audit()
    initial_rows = per_initial_rows()

    baseline_csv = OUT / "candidate_j_lift_router_baselines.csv"
    router_csv = OUT / "candidate_j_lift_router_summary.csv"
    threshold_csv = OUT / "candidate_j_lift_router_initdist_threshold_audit.csv"
    per_initial_csv = OUT / "candidate_j_lift_router_per_initial.csv"
    write_csv(
        baseline_csv,
        baseline_rows,
        [
            "method",
            "first20_successes",
            "first20_episodes",
            "first20_avg_len",
            "eval50_successes",
            "eval50_episodes",
            "eval50_avg_len",
        ],
    )
    write_csv(
        router_csv,
        routers,
        [
            "method",
            "successes",
            "episodes",
            "avg_len",
            "choices_positive",
            "choices_triage",
            "choices_weighted",
            "note",
        ],
    )
    write_csv(threshold_csv, best_thresholds, ["threshold", "successes", "episodes", "switches"])
    write_csv(
        per_initial_csv,
        initial_rows,
        [
            "initial_demo_id",
            "initial_positive_pos_dist",
            "positive",
            "triage",
            "weighted",
            "margin_labeled",
            "anchor_labeled",
            "anchor_support",
            "init_posdist3",
            "oracle_pos_triage_weighted",
        ],
    )

    first20_pos = next(row for row in baseline_rows if row["method"] == "positive_only_nn")
    first20_oracle = sum(int(row["oracle_pos_triage_weighted"]) for row in initial_rows)
    report_path = OUT / "candidate_j_lift_router_screen_REPORT.md"
    lines = [
        "# Candidate J Lift606 Router Screen",
        "",
        "**Status: failed screen.** Candidate J tests whether a deployable",
        "support-distance gate can repair Candidate I's Lift mild-tail failure by",
        "routing among existing positive-only, triage, and weighted policies.",
        "",
        "## Baselines",
        "",
        *format_table(
            baseline_rows,
            [
                "method",
                "first20_successes",
                "first20_episodes",
                "eval50_successes",
                "eval50_episodes",
            ],
        ),
        "",
        "## Router Screens",
        "",
        *format_table(
            routers,
            [
                "method",
                "successes",
                "episodes",
                "choices_positive",
                "choices_triage",
                "choices_weighted",
            ],
        ),
        "",
        "## Initial-Distance Audit",
        "",
        *format_table(best_thresholds, ["threshold", "successes", "episodes", "switches"]),
        "",
        "The initial-distance audit is post-hoc and only checks whether any",
        "threshold over the logged first-step positive-action distance could beat",
        "positive-only on the first 20 starts. It cannot: the best threshold ties",
        f"positive-only at `{first20_pos['first20_successes']}/{first20_pos['first20_episodes']}`.",
        "",
        "## Read",
        "",
        f"- The non-deployable oracle over positive, triage, and weighted is `{first20_oracle}/20`,",
        "  so the policy set has headroom, but the tested support-distance gates do",
        "  not expose it.",
        "- Per-step labeled-support margin routing is worse than the positive-only",
        "  anchor (`11/20` versus `14/20`).",
        "- Adding the Lift606 positive-NN anchor demos to the support scorer makes",
        "  the margin router worse (`10/20`).",
        "- The simple initial positive-distance gate with threshold `3.0` never opens",
        "  and exactly reproduces positive-only first-20 behavior.",
        "- Next router work needs richer deployable features, likely temporal",
        "  confidence or policy self-likelihood features, not just nearest labeled",
        "  state-action margin.",
        "",
        "## Artifacts",
        "",
        f"- Baseline CSV: `{baseline_csv.relative_to(ROOT)}`.",
        f"- Router summary CSV: `{router_csv.relative_to(ROOT)}`.",
        f"- Threshold audit CSV: `{threshold_csv.relative_to(ROOT)}`.",
        f"- Per-initial CSV: `{per_initial_csv.relative_to(ROOT)}`.",
        "- Evaluator: `scripts/evaluate_robomimic_router_policy.py` now accepts",
        "  `--positive-anchor-diagnostics` for non-Can anchor-support routing.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
