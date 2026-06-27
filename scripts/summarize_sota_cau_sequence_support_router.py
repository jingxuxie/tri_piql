#!/usr/bin/env python3
"""Summarize the CAU per-step support-margin router screens."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(".")
OUT_DIR = ROOT / "results" / "sota_candidate"

SCREENS = [
    {
        "screen_id": "split909_thr0",
        "split": "909",
        "threshold": "0.0",
        "positive_path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "per_seed"
        / "can_paired_pos40_bad80_split909_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "cau_action_conflict_can909_b005_m05_eval20" / "episode_metrics.csv",
        "cau_substr": "cau_action_conflict",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can909_eval20_thr0" / "episode_metrics.csv",
    },
    {
        "screen_id": "split101_thr005_eval50",
        "split": "101",
        "threshold": "0.05",
        "positive_path": ROOT
        / "results"
        / "final_paper_v02"
        / "per_seed"
        / "can_paired_pos40_bad80_split101_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "positive_substr": "model_epoch_200",
        "cau_path": OUT_DIR / "cau_action_conflict_can101_b005_m05_eval50" / "episode_metrics.csv",
        "cau_substr": "model_epoch_200",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can101_eval50_thr005" / "episode_metrics.csv",
    },
    {
        "screen_id": "split101_persistent_thr005_k10_eval50",
        "split": "101",
        "threshold": "0.05_persistent_k10",
        "positive_path": ROOT
        / "results"
        / "final_paper_v02"
        / "per_seed"
        / "can_paired_pos40_bad80_split101_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "positive_substr": "model_epoch_200",
        "cau_path": OUT_DIR / "cau_action_conflict_can101_b005_m05_eval50" / "episode_metrics.csv",
        "cau_substr": "model_epoch_200",
        "router_path": OUT_DIR
        / "cau_sequence_support_margin_persistent_can101_eval50_thr005_k10"
        / "episode_metrics.csv",
    },
    {
        "screen_id": "split909_thr005",
        "split": "909",
        "threshold": "0.05",
        "positive_path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "per_seed"
        / "can_paired_pos40_bad80_split909_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "cau_action_conflict_can909_b005_m05_eval20" / "episode_metrics.csv",
        "cau_substr": "cau_action_conflict",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can909_eval20_thr005" / "episode_metrics.csv",
    },
    {
        "screen_id": "split909_thr025",
        "split": "909",
        "threshold": "0.25",
        "positive_path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "per_seed"
        / "can_paired_pos40_bad80_split909_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "cau_action_conflict_can909_b005_m05_eval20" / "episode_metrics.csv",
        "cau_substr": "cau_action_conflict",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can909_eval20_thr025" / "episode_metrics.csv",
    },
    {
        "screen_id": "split606_thr005_heldout",
        "split": "606",
        "threshold": "0.05",
        "positive_path": ROOT
        / "results"
        / "candidate_g_fresh_preflight"
        / "can606_positive_epoch200_eval20"
        / "episode_metrics.csv",
        "positive_substr": "model_epoch_200",
        "cau_path": OUT_DIR / "cau_action_conflict_can606_b005_m05_eval20" / "episode_metrics.csv",
        "cau_substr": "model_epoch_200",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can606_eval20_thr005" / "episode_metrics.csv",
    },
    {
        "screen_id": "split606_thr005_eval50",
        "split": "606",
        "threshold": "0.05",
        "positive_path": OUT_DIR / "can606_positive_cau_eval50" / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "can606_positive_cau_eval50" / "episode_metrics.csv",
        "cau_substr": "cau_action_conflict",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can606_eval50_thr005" / "episode_metrics.csv",
    },
    {
        "screen_id": "split808_thr005",
        "split": "808",
        "threshold": "0.05",
        "positive_path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "per_seed"
        / "can_paired_pos40_bad80_split808_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "cau_action_conflict_can808_b005_m05_eval50" / "episode_metrics.csv",
        "cau_substr": "model_epoch_200",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can808_eval20_thr005" / "episode_metrics.csv",
    },
    {
        "screen_id": "split808_thr025",
        "split": "808",
        "threshold": "0.25",
        "positive_path": ROOT
        / "results"
        / "candidate_f_can_fresh_validation"
        / "per_seed"
        / "can_paired_pos40_bad80_split808_positive_only_nn_policy0"
        / "eval"
        / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "cau_action_conflict_can808_b005_m05_eval50" / "episode_metrics.csv",
        "cau_substr": "model_epoch_200",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can808_eval20_thr025" / "episode_metrics.csv",
    },
    {
        "screen_id": "split707_thr025",
        "split": "707",
        "threshold": "0.25",
        "positive_path": OUT_DIR / "can707_positive_weighted_cau_eval50" / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "can707_positive_weighted_cau_eval50" / "episode_metrics.csv",
        "cau_substr": "cau_action_conflict",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can707_eval20_thr025" / "episode_metrics.csv",
    },
    {
        "screen_id": "split707_thr010",
        "split": "707",
        "threshold": "0.10",
        "positive_path": OUT_DIR / "can707_positive_weighted_cau_eval50" / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "can707_positive_weighted_cau_eval50" / "episode_metrics.csv",
        "cau_substr": "cau_action_conflict",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can707_eval20_thr010" / "episode_metrics.csv",
    },
    {
        "screen_id": "split707_thr005",
        "split": "707",
        "threshold": "0.05",
        "positive_path": OUT_DIR / "can707_positive_weighted_cau_eval50" / "episode_metrics.csv",
        "positive_substr": "positive_only",
        "cau_path": OUT_DIR / "can707_positive_weighted_cau_eval50" / "episode_metrics.csv",
        "cau_substr": "cau_action_conflict",
        "router_path": OUT_DIR / "cau_sequence_support_margin_can707_eval20_thr005" / "episode_metrics.csv",
    },
]


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


def checkpoint_matches(row: dict[str, str], substring: str) -> bool:
    checkpoint = row.get("checkpoint", "")
    checkpoint_name = row.get("checkpoint_name", "")
    if substring == "model_epoch_200":
        return Path(checkpoint).stem == "model_epoch_200" or checkpoint_name == "model_epoch_200"
    return substring in checkpoint or checkpoint_name == substring


def keyed_successes(path: Path, substring: str, limit: int) -> dict[tuple[int, str], int]:
    out: dict[tuple[int, str], int] = {}
    for row in read_csv(path):
        if "checkpoint" in row and not checkpoint_matches(row, substring):
            continue
        episode = int(row["episode"])
        if episode >= limit:
            continue
        out[(episode, row["initial_demo_id"])] = int(float(row["success"]) > 0.5)
    if len(out) != limit:
        raise ValueError(f"{path} {substring}: expected {limit} rows, got {len(out)}")
    return out


def keyed_router_rows(path: Path) -> dict[tuple[int, str], dict[str, str]]:
    rows = read_csv(path)
    out: dict[tuple[int, str], dict[str, str]] = {}
    for row in rows:
        out[(int(row["episode"]), row["initial_demo_id"])] = row
    return out


def score(count: int, episodes: int) -> str:
    return f"{count}/{episodes}"


def plural(count: object, singular: str, plural_word: str | None = None) -> str:
    value = int(count)
    return singular if value == 1 else (plural_word or f"{singular}s")


def summarize_screen(spec: dict[str, object]) -> dict[str, object]:
    router_rows = keyed_router_rows(spec["router_path"])
    limit = len(router_rows)
    positive = keyed_successes(spec["positive_path"], spec["positive_substr"], limit)
    cau = keyed_successes(spec["cau_path"], spec["cau_substr"], limit)
    if set(positive) != set(router_rows) or set(cau) != set(router_rows):
        raise ValueError(f"{spec['screen_id']}: mismatched episode/start keys")
    router = {
        key: int(float(row["success"]) > 0.5)
        for key, row in router_rows.items()
    }
    positive_successes = sum(positive.values())
    cau_successes = sum(cau.values())
    router_successes = sum(router.values())
    gains = sum(1 for key, value in router.items() if value == 1 and positive[key] == 0)
    losses = sum(1 for key, value in router.items() if value == 0 and positive[key] == 1)
    choices_positive = sum(int(float(row.get("choices_positive", 0) or 0)) for row in router_rows.values())
    choices_cau = sum(int(float(row.get("choices_cau", 0) or 0)) for row in router_rows.values())
    return {
        "screen_id": spec["screen_id"],
        "split": spec["split"],
        "threshold": spec["threshold"],
        "episodes": limit,
        "positive_successes": positive_successes,
        "cau_successes": cau_successes,
        "router_successes": router_successes,
        "positive_score": score(positive_successes, limit),
        "cau_score": score(cau_successes, limit),
        "router_score": score(router_successes, limit),
        "delta_vs_positive": router_successes - positive_successes,
        "delta_vs_cau": router_successes - cau_successes,
        "gains_vs_positive": gains,
        "losses_vs_positive": losses,
        "choices_positive": choices_positive,
        "choices_cau": choices_cau,
        "router_report": spec["router_path"].parent / "REPORT.md",
    }


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
    rows = [summarize_screen(spec) for spec in SCREENS]
    summary_path = args.out_dir / "cau_sequence_support_router_summary.csv"
    report_path = args.out_dir / "CAU_SEQUENCE_SUPPORT_ROUTER_REPORT.md"
    fieldnames = [
        "screen_id",
        "split",
        "threshold",
        "episodes",
        "positive_successes",
        "cau_successes",
        "router_successes",
        "positive_score",
        "cau_score",
        "router_score",
        "delta_vs_positive",
        "delta_vs_cau",
        "gains_vs_positive",
        "losses_vs_positive",
        "choices_positive",
        "choices_cau",
        "router_report",
    ]
    write_csv(summary_path, rows, fieldnames)

    split909_thr0 = next(row for row in rows if row["screen_id"] == "split909_thr0")
    split909_thr005 = next(row for row in rows if row["screen_id"] == "split909_thr005")
    split909_thr025 = next(row for row in rows if row["screen_id"] == "split909_thr025")
    split101_thr005_eval50 = next(row for row in rows if row["screen_id"] == "split101_thr005_eval50")
    split101_persistent = next(row for row in rows if row["screen_id"] == "split101_persistent_thr005_k10_eval50")
    split606_thr005 = next(row for row in rows if row["screen_id"] == "split606_thr005_heldout")
    split606_thr005_eval50 = next(row for row in rows if row["screen_id"] == "split606_thr005_eval50")
    split808_thr005 = next(row for row in rows if row["screen_id"] == "split808_thr005")
    split808_thr025 = next(row for row in rows if row["screen_id"] == "split808_thr025")
    split707_thr005 = next(row for row in rows if row["screen_id"] == "split707_thr005")
    split707_thr010 = next(row for row in rows if row["screen_id"] == "split707_thr010")
    split707_thr025 = next(row for row in rows if row["screen_id"] == "split707_thr025")
    fixed005_rows = [split909_thr005, split808_thr005, split707_thr005]
    fixed005_episodes = sum(int(row["episodes"]) for row in fixed005_rows)
    fixed005_router = sum(int(row["router_successes"]) for row in fixed005_rows)
    fixed005_positive = sum(int(row["positive_successes"]) for row in fixed005_rows)
    fixed005_cau = sum(int(row["cau_successes"]) for row in fixed005_rows)
    fixed005_gains = sum(int(row["gains_vs_positive"]) for row in fixed005_rows)
    fixed005_losses = sum(int(row["losses_vs_positive"]) for row in fixed005_rows)
    fixed005_with_heldout_rows = fixed005_rows + [split606_thr005]
    fixed005_with_heldout_episodes = sum(int(row["episodes"]) for row in fixed005_with_heldout_rows)
    fixed005_with_heldout_router = sum(int(row["router_successes"]) for row in fixed005_with_heldout_rows)
    fixed005_with_heldout_positive = sum(int(row["positive_successes"]) for row in fixed005_with_heldout_rows)
    fixed005_with_heldout_cau = sum(int(row["cau_successes"]) for row in fixed005_with_heldout_rows)
    fixed005_with_heldout_gains = sum(int(row["gains_vs_positive"]) for row in fixed005_with_heldout_rows)
    fixed005_with_heldout_losses = sum(int(row["losses_vs_positive"]) for row in fixed005_with_heldout_rows)
    eval50_rows = [split606_thr005_eval50, split101_thr005_eval50]
    eval50_episodes = sum(int(row["episodes"]) for row in eval50_rows)
    eval50_router = sum(int(row["router_successes"]) for row in eval50_rows)
    eval50_positive = sum(int(row["positive_successes"]) for row in eval50_rows)
    eval50_cau = sum(int(row["cau_successes"]) for row in eval50_rows)
    eval50_gains = sum(int(row["gains_vs_positive"]) for row in eval50_rows)
    eval50_losses = sum(int(row["losses_vs_positive"]) for row in eval50_rows)
    report_lines = [
        "# CAU Sequence Support-Margin Router",
        "",
        "This short screen evaluates a per-step support-margin router between positive-only and CAU.",
        "The router starts from positive-only and chooses CAU only when CAU's labeled state-action support margin exceeds the positive anchor by `--switch-threshold`.",
        "",
        "## Decision",
        "",
        f"- On split909, threshold `0.0` is too aggressive: router `{split909_thr0['router_score']}` versus positive-only `{split909_thr0['positive_score']}` and CAU `{split909_thr0['cau_score']}`.",
        f"- On split909, threshold `0.25` reaches `{split909_thr025['router_score']}` versus positive-only `{split909_thr025['positive_score']}`, with `{split909_thr025['gains_vs_positive']}` {plural(split909_thr025['gains_vs_positive'], 'gain')} and `{split909_thr025['losses_vs_positive']}` {plural(split909_thr025['losses_vs_positive'], 'loss', 'losses')}.",
        f"- The same threshold preserves split808: router `{split808_thr025['router_score']}` versus positive-only `{split808_thr025['positive_score']}` and CAU `{split808_thr025['cau_score']}`, with `{split808_thr025['losses_vs_positive']}` losses.",
        f"- The same threshold misses split707 CAU upside: router `{split707_thr025['router_score']}` versus positive-only `{split707_thr025['positive_score']}` and CAU `{split707_thr025['cau_score']}`.",
        f"- Relaxing split707 to threshold `0.10` is not enough: router `{split707_thr010['router_score']}` with `{split707_thr010['gains_vs_positive']}` gain and `{split707_thr010['losses_vs_positive']}` loss versus positive-only.",
        f"- Fixed threshold `0.05` is the best short-screen setting so far: aggregate router `{score(fixed005_router, fixed005_episodes)}` versus positive-only `{score(fixed005_positive, fixed005_episodes)}` and CAU `{score(fixed005_cau, fixed005_episodes)}`, with `{fixed005_gains}` gains and `{fixed005_losses}` loss versus positive-only.",
        f"- Threshold `0.05` reaches split909 `{split909_thr005['router_score']}`, split808 `{split808_thr005['router_score']}`, and split707 `{split707_thr005['router_score']}`; this is promising short-screen evidence, but the 50-episode validations below are mixed.",
        f"- The first no-retune held-out guardrail on split606 is neutral: threshold `0.05` reaches `{split606_thr005['router_score']}` versus positive-only `{split606_thr005['positive_score']}` and CAU `{split606_thr005['cau_score']}`, with `{split606_thr005['gains_vs_positive']}` gains and `{split606_thr005['losses_vs_positive']}` losses.",
        f"- Including split606, threshold `0.05` is `{score(fixed005_with_heldout_router, fixed005_with_heldout_episodes)}` versus positive-only `{score(fixed005_with_heldout_positive, fixed005_with_heldout_episodes)}` and CAU `{score(fixed005_with_heldout_cau, fixed005_with_heldout_episodes)}`, with `{fixed005_with_heldout_gains}` gains and `{fixed005_with_heldout_losses}` losses.",
        f"- The 50-episode split606 no-retune validation is positive: threshold `0.05` reaches `{split606_thr005_eval50['router_score']}` versus positive-only `{split606_thr005_eval50['positive_score']}` and CAU `{split606_thr005_eval50['cau_score']}`, with `{split606_thr005_eval50['gains_vs_positive']}` gains and `{split606_thr005_eval50['losses_vs_positive']}` losses versus positive-only.",
        f"- The 50-episode split101 no-retune validation is mixed-negative: threshold `0.05` reaches `{split101_thr005_eval50['router_score']}` versus positive-only `{split101_thr005_eval50['positive_score']}` but remains below CAU `{split101_thr005_eval50['cau_score']}`.",
        f"- Across the two 50-episode no-retune validations, the router is `{score(eval50_router, eval50_episodes)}` versus positive-only `{score(eval50_positive, eval50_episodes)}` and CAU `{score(eval50_cau, eval50_episodes)}`, with `{eval50_gains}` gains and `{eval50_losses}` losses versus positive-only.",
        f"- A persistent support-margin variant does not fix split101: k=10 reaches `{split101_persistent['router_score']}` versus non-persistent `{split101_thr005_eval50['router_score']}` and CAU `{split101_persistent['cau_score']}`.",
        "",
        "## Screen Rows",
        "",
        *markdown_table(
            rows,
            [
                "screen_id",
                "router_score",
                "positive_score",
                "cau_score",
                "delta_vs_positive",
                "gains_vs_positive",
                "losses_vs_positive",
                "choices_positive",
                "choices_cau",
            ],
        ),
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{summary_path}`.",
        *[f"- {row['screen_id']} report: `{row['router_report']}`." for row in rows],
    ]
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path}")
    print(f"wrote {summary_path}")


if __name__ == "__main__":
    main()
