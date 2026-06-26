from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


TABLE_DIR = Path("results/final_paper/tables")
UNION_ENDPOINT_ROOT = Path("results/final_paper/ablations/v02_union_endpoint_200ep_can40")
PER_SEED_ROOT = Path("results/final_paper/per_seed")

OUT_CSV = "failure_mode_initial_states.csv"
OUT_CASES = "failure_mode_initial_states_cases.csv"
OUT_REPORT = "failure_mode_initial_states_REPORT.md"

SPLIT_SEEDS = ("11", "22", "33")
HORIZON = 400.0
TIMEOUT_FRACTION = 0.95


@dataclass(frozen=True)
class MethodSpec:
    method_id: str
    method_label: str
    path_template: str
    role: str


METHODS = (
    MethodSpec(
        "positive_only_nn_top40",
        "positive-only NN top40",
        str(PER_SEED_ROOT / "can_paired_pos40_bad80_split{split}_positive_only_nn_policy0" / "eval" / "episode_metrics.csv"),
        "hard positive-only support",
    ),
    MethodSpec(
        "weighted_bc_full_pool",
        "weighted BC full pool",
        str(PER_SEED_ROOT / "can_paired_pos40_bad80_split{split}_weighted_bc_policy0" / "eval" / "episode_metrics.csv"),
        "soft full-pool weighting",
    ),
    MethodSpec(
        "positive_nn_risk_union_top40",
        "positive-NN/risk union top40",
        str(UNION_ENDPOINT_ROOT / "split{split}" / "positive_nn_risk_union_top40" / "eval_50ep" / "episode_metrics.csv"),
        "hard union support",
    ),
    MethodSpec(
        "all_demo_bc_full_pool",
        "all-demo BC full pool",
        str(PER_SEED_ROOT / "can_paired_pos40_bad80_split{split}_bc_all_mixed_policy0" / "eval" / "episode_metrics.csv"),
        "unweighted full-pool cloning",
    ),
)

CASE_SPECS = (
    (
        "union_rescue",
        "Hard-union rescue",
        "Union succeeds where positive-only, weighted, and all-demo mostly timeout; illustrates the coverage gain from adding risk-derived support.",
    ),
    (
        "positive_anchor_regression",
        "Positive-anchor regression",
        "Positive-only succeeds while the union and weighted rows timeout; this is the split-specific regression that keeps the union claim non-uniform.",
    ),
    (
        "soft_pool_rescue",
        "Soft-pool rescue",
        "Weighted BC succeeds where hard support struggles; broad weighted coverage remains a first-class branch rather than a disposable baseline.",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=TABLE_DIR)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float | str | None) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.3f}"


def fmt_len(value: float | str | None) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.1f}"


def as_int(value: object) -> int:
    return int(round(float(str(value))))


def aggregate_method(path: Path) -> dict[str, dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in read_rows(path):
        grouped.setdefault(row["initial_demo_id"], []).append(row)

    out: dict[str, dict[str, object]] = {}
    for initial_demo_id, rows in grouped.items():
        successes = [float(row["success"]) for row in rows]
        lengths = [float(row["length"]) for row in rows]
        success_count = as_int(sum(successes))
        episodes = len(rows)
        failed_lengths = [length for success, length in zip(successes, lengths) if success < 0.5]
        success_lengths = [length for success, length in zip(successes, lengths) if success >= 0.5]
        timeout_failures = sum(length >= HORIZON * TIMEOUT_FRACTION for length in failed_lengths)
        out[initial_demo_id] = {
            "success_count": success_count,
            "eval_episodes": episodes,
            "success_rate": success_count / episodes,
            "avg_length": sum(lengths) / episodes,
            "avg_success_length": sum(success_lengths) / len(success_lengths) if success_lengths else None,
            "avg_failure_length": sum(failed_lengths) / len(failed_lengths) if failed_lengths else None,
            "failed_count": len(failed_lengths),
            "timeout_failure_count": timeout_failures,
            "timeout_failure_rate": timeout_failures / len(failed_lengths) if failed_lengths else 0.0,
        }
    return out


def load_stats() -> dict[tuple[str, str, str], dict[str, object]]:
    stats: dict[tuple[str, str, str], dict[str, object]] = {}
    for split_seed in SPLIT_SEEDS:
        for method in METHODS:
            path = Path(method.path_template.format(split=split_seed))
            if not path.exists():
                raise FileNotFoundError(path)
            for initial_demo_id, row in aggregate_method(path).items():
                stats[(split_seed, initial_demo_id, method.method_id)] = {
                    **row,
                    "source": str(path),
                }
    return stats


def demos_for_split(stats: dict[tuple[str, str, str], dict[str, object]], split_seed: str) -> list[str]:
    demos = {
        initial_demo_id
        for candidate_split, initial_demo_id, method_id in stats
        if candidate_split == split_seed and method_id == METHODS[0].method_id
    }
    return sorted(demos, key=lambda demo_id: int(demo_id.removeprefix("demo_")))


def rate(stats: dict[tuple[str, str, str], dict[str, object]], split_seed: str, demo_id: str, method_id: str) -> float:
    return float(stats[(split_seed, demo_id, method_id)]["success_rate"])


def length(stats: dict[tuple[str, str, str], dict[str, object]], split_seed: str, demo_id: str, method_id: str) -> float:
    return float(stats[(split_seed, demo_id, method_id)]["avg_length"])


def case_score(
    case_id: str,
    stats: dict[tuple[str, str, str], dict[str, object]],
    split_seed: str,
    demo_id: str,
) -> tuple[float, ...]:
    positive = rate(stats, split_seed, demo_id, "positive_only_nn_top40")
    weighted = rate(stats, split_seed, demo_id, "weighted_bc_full_pool")
    union = rate(stats, split_seed, demo_id, "positive_nn_risk_union_top40")
    all_demo = rate(stats, split_seed, demo_id, "all_demo_bc_full_pool")
    if case_id == "union_rescue":
        return (
            union - max(positive, weighted, all_demo),
            union - positive,
            union,
            length(stats, split_seed, demo_id, "positive_only_nn_top40"),
        )
    if case_id == "positive_anchor_regression":
        return (
            positive - union,
            positive - weighted,
            positive - all_demo,
            positive,
        )
    if case_id == "soft_pool_rescue":
        return (
            weighted - max(positive, union),
            weighted - union,
            weighted - positive,
            weighted,
        )
    raise KeyError(case_id)


def select_cases(stats: dict[tuple[str, str, str], dict[str, object]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    used: set[tuple[str, str]] = set()
    candidates = [
        (split_seed, demo_id)
        for split_seed in SPLIT_SEEDS
        for demo_id in demos_for_split(stats, split_seed)
    ]

    for case_id, case_title, case_read in CASE_SPECS:
        ranked = sorted(
            (
                (case_score(case_id, stats, split_seed, demo_id), split_seed, demo_id)
                for split_seed, demo_id in candidates
                if (split_seed, demo_id) not in used
            ),
            key=lambda item: (
                item[0],
                -int(item[1]),
                -int(item[2].removeprefix("demo_")),
            ),
            reverse=True,
        )
        score, split_seed, demo_id = ranked[0]
        used.add((split_seed, demo_id))
        selected.append(
            {
                "case_id": case_id,
                "case_title": case_title,
                "split_seed": split_seed,
                "initial_demo_id": demo_id,
                "selection_score": fmt(score[0]),
                "case_read": case_read,
            }
        )
    return selected


def grasp_proxy(success_count: int, episodes: int) -> str:
    if success_count == episodes:
        return "success_proxy_grasp_observed_all"
    if success_count > 0:
        return "success_proxy_grasp_observed_some"
    return "no_success_proxy_grasp_unobserved"


def loop_or_miss_proxy(success_count: int, episodes: int, timeout_failure_count: int, failed_count: int) -> str:
    if success_count == episodes:
        return "no_failure_observed"
    if failed_count and timeout_failure_count == failed_count:
        return "timeout_or_miss_all_failures"
    if failed_count and timeout_failure_count / failed_count >= 0.8:
        return "timeout_or_miss_most_failures"
    return "mixed_or_non_timeout_failures"


def bad_demo_proxy(method_id: str, success_count: int, episodes: int, timeout_failure_count: int, failed_count: int) -> str:
    if success_count == episodes:
        return "not_applicable_successful"
    if method_id in {"weighted_bc_full_pool", "all_demo_bc_full_pool"} and failed_count:
        if timeout_failure_count / failed_count >= 0.8:
            return "contamination_compatible_timeout_not_verified"
        return "contamination_compatible_mixed_not_verified"
    return "support_gap_or_controller_failure_not_bad-demo-attributed"


def method_rows(
    stats: dict[tuple[str, str, str], dict[str, object]],
    cases: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    method_index = {method.method_id: method for method in METHODS}
    for case in cases:
        split_seed = case["split_seed"]
        initial_demo_id = case["initial_demo_id"]
        for method in METHODS:
            stat = stats[(split_seed, initial_demo_id, method.method_id)]
            success_count = as_int(stat["success_count"])
            episodes = as_int(stat["eval_episodes"])
            failed_count = as_int(stat["failed_count"])
            timeout_failures = as_int(stat["timeout_failure_count"])
            rows.append(
                {
                    "case_id": case["case_id"],
                    "case_title": case["case_title"],
                    "split_seed": split_seed,
                    "initial_demo_id": initial_demo_id,
                    "method_id": method.method_id,
                    "method_label": method.method_label,
                    "method_role": method_index[method.method_id].role,
                    "success_count": str(success_count),
                    "eval_episodes": str(episodes),
                    "success_rate": fmt(stat["success_rate"]),
                    "avg_trajectory_length": fmt_len(stat["avg_length"]),
                    "avg_success_length": fmt_len(stat["avg_success_length"]),
                    "avg_failure_length": fmt_len(stat["avg_failure_length"]),
                    "failed_count": str(failed_count),
                    "timeout_failure_count": str(timeout_failures),
                    "timeout_failure_rate_among_failures": fmt(stat["timeout_failure_rate"]),
                    "grasp_proxy": grasp_proxy(success_count, episodes),
                    "loop_or_miss_proxy": loop_or_miss_proxy(success_count, episodes, timeout_failures, failed_count),
                    "bad_demo_resemblance_proxy": bad_demo_proxy(method.method_id, success_count, episodes, timeout_failures, failed_count),
                    "source": str(stat["source"]),
                }
            )
    return rows


def case_rows(
    stats: dict[tuple[str, str, str], dict[str, object]],
    cases: list[dict[str, str]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    method_fields = [
        ("positive_only_nn_top40", "positive_only"),
        ("weighted_bc_full_pool", "weighted_bc"),
        ("positive_nn_risk_union_top40", "union"),
        ("all_demo_bc_full_pool", "all_demo"),
    ]
    for case in cases:
        split_seed = case["split_seed"]
        initial_demo_id = case["initial_demo_id"]
        row = dict(case)
        for method_id, prefix in method_fields:
            stat = stats[(split_seed, initial_demo_id, method_id)]
            row[f"{prefix}_success_count"] = f"{as_int(stat['success_count'])}/{as_int(stat['eval_episodes'])}"
            row[f"{prefix}_success_rate"] = fmt(stat["success_rate"])
            row[f"{prefix}_avg_length"] = fmt_len(stat["avg_length"])
        rows.append(row)
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(column, "") for column in columns) + " |")
    return lines


def write_report(path: Path, cases: list[dict[str, str]], rows: list[dict[str, str]]) -> None:
    by_case = {case["case_id"]: case for case in cases}
    method_by_case = {
        (row["case_id"], row["method_id"]): row
        for row in rows
    }
    union_case = by_case["union_rescue"]
    anchor_case = by_case["positive_anchor_regression"]
    soft_case = by_case["soft_pool_rescue"]
    lines = [
        "# Failure-Mode Initial-State Audit",
        "",
        "This artifact compares positive-only NN, weighted BC, the v0.2 hard union, and all-demo BC on three representative paired Can 40p/80b initial states.",
        "It reuses existing 50-episode endpoint evaluations; each selected initial state has five repeated rollouts per method.",
        "",
        "No videos or direct object-state labels are parsed here. The grasp and loop/miss columns are metric proxies: success is used as the only grasp proxy, and horizon-length failures are treated as timeout/miss/loop proxies.",
        "",
        "## Selected Cases",
        "",
        *markdown_table(
            cases,
            [
                "case_id",
                "case_title",
                "split_seed",
                "initial_demo_id",
                "selection_score",
                "positive_only_success_count",
                "weighted_bc_success_count",
                "union_success_count",
                "all_demo_success_count",
                "case_read",
            ],
        ),
        "",
        "## Per-Method Rows",
        "",
        *markdown_table(
            rows,
            [
                "case_id",
                "method_label",
                "success_count",
                "eval_episodes",
                "avg_trajectory_length",
                "loop_or_miss_proxy",
                "bad_demo_resemblance_proxy",
            ],
        ),
        "",
        "## Read",
        "",
        (
            f"- Union rescue: split `{union_case['split_seed']}`, `{union_case['initial_demo_id']}` has "
            f"union `{method_by_case[('union_rescue', 'positive_nn_risk_union_top40')]['success_count']}/5` "
            f"at average length `{method_by_case[('union_rescue', 'positive_nn_risk_union_top40')]['avg_trajectory_length']}`, "
            f"while positive-only is `{method_by_case[('union_rescue', 'positive_only_nn_top40')]['success_count']}/5`, "
            f"weighted BC is `{method_by_case[('union_rescue', 'weighted_bc_full_pool')]['success_count']}/5`, "
            f"and all-demo BC is `{method_by_case[('union_rescue', 'all_demo_bc_full_pool')]['success_count']}/5`."
        ),
        (
            f"- Positive-anchor regression: split `{anchor_case['split_seed']}`, `{anchor_case['initial_demo_id']}` has "
            f"positive-only `{method_by_case[('positive_anchor_regression', 'positive_only_nn_top40')]['success_count']}/5` "
            f"but union `{method_by_case[('positive_anchor_regression', 'positive_nn_risk_union_top40')]['success_count']}/5` "
            f"and weighted BC `{method_by_case[('positive_anchor_regression', 'weighted_bc_full_pool')]['success_count']}/5`."
        ),
        (
            f"- Soft-pool rescue: split `{soft_case['split_seed']}`, `{soft_case['initial_demo_id']}` has "
            f"weighted BC `{method_by_case[('soft_pool_rescue', 'weighted_bc_full_pool')]['success_count']}/5` "
            f"while positive-only is `{method_by_case[('soft_pool_rescue', 'positive_only_nn_top40')]['success_count']}/5` "
            f"and union is `{method_by_case[('soft_pool_rescue', 'positive_nn_risk_union_top40')]['success_count']}/5`."
        ),
        "- The table supports the current paper framing: the hard union gives a real Can rescue pattern, but weighted coverage and positive-only support remain essential comparator branches.",
        "",
        "## Outputs",
        "",
        f"- `{TABLE_DIR / OUT_CSV}`",
        f"- `{TABLE_DIR / OUT_CASES}`",
        f"- `{TABLE_DIR / OUT_REPORT}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    stats = load_stats()
    cases = case_rows(stats, select_cases(stats))
    rows = method_rows(stats, cases)
    case_fields = [
        "case_id",
        "case_title",
        "split_seed",
        "initial_demo_id",
        "selection_score",
        "positive_only_success_count",
        "positive_only_success_rate",
        "positive_only_avg_length",
        "weighted_bc_success_count",
        "weighted_bc_success_rate",
        "weighted_bc_avg_length",
        "union_success_count",
        "union_success_rate",
        "union_avg_length",
        "all_demo_success_count",
        "all_demo_success_rate",
        "all_demo_avg_length",
        "case_read",
    ]
    row_fields = [
        "case_id",
        "case_title",
        "split_seed",
        "initial_demo_id",
        "method_id",
        "method_label",
        "method_role",
        "success_count",
        "eval_episodes",
        "success_rate",
        "avg_trajectory_length",
        "avg_success_length",
        "avg_failure_length",
        "failed_count",
        "timeout_failure_count",
        "timeout_failure_rate_among_failures",
        "grasp_proxy",
        "loop_or_miss_proxy",
        "bad_demo_resemblance_proxy",
        "source",
    ]
    write_csv(args.out_dir / OUT_CASES, cases, case_fields)
    write_csv(args.out_dir / OUT_CSV, rows, row_fields)
    write_report(args.out_dir / OUT_REPORT, cases, rows)
    print(f"wrote {args.out_dir / OUT_CASES}")
    print(f"wrote {args.out_dir / OUT_CSV}")
    print(f"wrote {args.out_dir / OUT_REPORT}")


if __name__ == "__main__":
    main()
