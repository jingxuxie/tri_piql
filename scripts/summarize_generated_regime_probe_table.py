from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


OUT_DIR = Path("results/final_paper/tables")

HARD_NEGATIVE_SOURCE = Path(
    "results/final_paper/ablations/hard_negative_can_endpoint_200ep/endpoint_200ep_3split_summary.csv"
)
COVERAGE_SHIFT_SOURCE = Path(
    "results/final_paper/ablations/can_coverage_shift_endpoint_200ep/endpoint_200ep_3split_summary.csv"
)
PREFIX_POSITIVE_SOURCE = Path(
    "results/final_paper/ablations/can_prefix_positive_endpoint_200ep/endpoint_200ep_aggregate_summary.csv"
)

OUT_CSV = "generated_regime_probe_summary.csv"
OUT_REPORT = "generated_regime_probe_summary_REPORT.md"

BAD_AWARE_HYBRID = "hybrid_rank_fusion_badaware_heavy_top40"
POSITIVE_NN_TOP40 = "state_action_positive_nn_top40"
PREFIX_BAD_AWARE = "prefix_bad_aware_state_top80"
PREFIX_POSITIVE_NN = "prefix_state_action_nn_top80"


@dataclass(frozen=True)
class ProbeSpec:
    probe_id: str
    probe_label: str
    hypothesis: str
    source: Path
    bad_aware_method: str
    positive_method: str
    row_format: str
    split_seeds: str = "101/202/303"


PROBES = (
    ProbeSpec(
        probe_id="hard_negative_can",
        probe_label="Hard-negative Can",
        hypothesis="Action-conflicting near-neighbor failures",
        source=HARD_NEGATIVE_SOURCE,
        bad_aware_method=BAD_AWARE_HYBRID,
        positive_method=POSITIVE_NN_TOP40,
        row_format="per_split",
    ),
    ProbeSpec(
        probe_id="coverage_shift_can",
        probe_label="Coverage-shift Can",
        hypothesis="Trusted positives under-cover initial conditions",
        source=COVERAGE_SHIFT_SOURCE,
        bad_aware_method=BAD_AWARE_HYBRID,
        positive_method=POSITIVE_NN_TOP40,
        row_format="per_split",
    ),
    ProbeSpec(
        probe_id="prefix_positive_can",
        probe_label="Prefix-positive Can",
        hypothesis="Trusted positives are successful-demo prefixes",
        source=PREFIX_POSITIVE_SOURCE,
        bad_aware_method=PREFIX_BAD_AWARE,
        positive_method=PREFIX_POSITIVE_NN,
        row_format="aggregate",
    ),
)

FIELDNAMES = [
    "probe_id",
    "probe_label",
    "hypothesis",
    "split_seeds",
    "bad_aware_method",
    "positive_method",
    "bad_aware_endpoint",
    "positive_endpoint",
    "endpoint_delta",
    "bad_aware_success_count",
    "bad_aware_eval_episodes",
    "positive_success_count",
    "positive_eval_episodes",
    "bad_aware_hidden_positive",
    "bad_aware_hidden_bad",
    "positive_hidden_positive",
    "positive_hidden_bad",
    "bad_aware_support_pos_bad",
    "positive_support_pos_bad",
    "bad_aware_avg_len",
    "positive_avg_len",
    "source_artifact",
    "claim_scope",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def as_int(value: str) -> int:
    return int(round(float(value)))


def fmt_one(value: float) -> str:
    return f"{value:.1f}"


def endpoint(successes: int, episodes: int) -> str:
    return f"{successes}/{episodes}"


def delta_string(bad_aware_success: int, positive_success: int, episodes: int) -> str:
    delta = bad_aware_success - positive_success
    return f"{delta:+d}/{episodes}"


def average(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot average empty values")
    return sum(values) / len(values)


def summarize_per_split(spec: ProbeSpec, rows: list[dict[str, str]], method: str) -> dict[str, int | float]:
    selected = [row for row in rows if row["candidate_id"] == method]
    if not selected:
        raise ValueError(f"{spec.probe_id}: no rows for {method}")
    return {
        "success_count": sum(as_int(row["success_count"]) for row in selected),
        "eval_episodes": sum(as_int(row["eval_episodes"]) for row in selected),
        "hidden_positive": sum(as_int(row["selected_hidden_positive"]) for row in selected),
        "hidden_bad": sum(as_int(row["selected_hidden_bad"]) for row in selected),
        "avg_len": average([float(row["avg_len"]) for row in selected]),
    }


def summarize_aggregate(spec: ProbeSpec, rows: list[dict[str, str]], method: str) -> dict[str, int | float]:
    matches = [row for row in rows if row["candidate_id"] == method]
    if len(matches) != 1:
        raise ValueError(f"{spec.probe_id}: expected one row for {method}, found {len(matches)}")
    row = matches[0]
    return {
        "success_count": as_int(row["success_count"]),
        "eval_episodes": as_int(row["eval_episodes"]),
        "hidden_positive": as_int(row["selected_hidden_positive"]),
        "hidden_bad": as_int(row["selected_hidden_bad"]),
        "avg_len": float(row["avg_len"]),
    }


def summarize_method(spec: ProbeSpec, rows: list[dict[str, str]], method: str) -> dict[str, int | float]:
    if spec.row_format == "per_split":
        return summarize_per_split(spec, rows, method)
    if spec.row_format == "aggregate":
        return summarize_aggregate(spec, rows, method)
    raise ValueError(f"unknown row format {spec.row_format!r}")


def summarize_probe(spec: ProbeSpec) -> dict[str, str]:
    rows = read_csv(spec.source)
    bad_aware = summarize_method(spec, rows, spec.bad_aware_method)
    positive = summarize_method(spec, rows, spec.positive_method)
    bad_success = int(bad_aware["success_count"])
    bad_episodes = int(bad_aware["eval_episodes"])
    pos_success = int(positive["success_count"])
    pos_episodes = int(positive["eval_episodes"])
    if bad_episodes != pos_episodes:
        raise ValueError(f"{spec.probe_id}: mismatched eval episode counts")
    bad_hidden_pos = int(bad_aware["hidden_positive"])
    bad_hidden_bad = int(bad_aware["hidden_bad"])
    pos_hidden_pos = int(positive["hidden_positive"])
    pos_hidden_bad = int(positive["hidden_bad"])
    return {
        "probe_id": spec.probe_id,
        "probe_label": spec.probe_label,
        "hypothesis": spec.hypothesis,
        "split_seeds": spec.split_seeds,
        "bad_aware_method": spec.bad_aware_method,
        "positive_method": spec.positive_method,
        "bad_aware_endpoint": endpoint(bad_success, bad_episodes),
        "positive_endpoint": endpoint(pos_success, pos_episodes),
        "endpoint_delta": delta_string(bad_success, pos_success, bad_episodes),
        "bad_aware_success_count": str(bad_success),
        "bad_aware_eval_episodes": str(bad_episodes),
        "positive_success_count": str(pos_success),
        "positive_eval_episodes": str(pos_episodes),
        "bad_aware_hidden_positive": str(bad_hidden_pos),
        "bad_aware_hidden_bad": str(bad_hidden_bad),
        "positive_hidden_positive": str(pos_hidden_pos),
        "positive_hidden_bad": str(pos_hidden_bad),
        "bad_aware_support_pos_bad": f"{bad_hidden_pos}/{bad_hidden_bad}",
        "positive_support_pos_bad": f"{pos_hidden_pos}/{pos_hidden_bad}",
        "bad_aware_avg_len": fmt_one(float(bad_aware["avg_len"])),
        "positive_avg_len": fmt_one(float(positive["avg_len"])),
        "source_artifact": str(spec.source),
        "claim_scope": "generated diagnostic, not primary benchmark row",
    }


def markdown_table(rows: list[dict[str, str]], columns: list[tuple[str, str]]) -> list[str]:
    lines = [
        "| " + " | ".join(label for label, _key in columns) + " |",
        "| " + " | ".join("---" for _label, _key in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[key] for _label, key in columns) + " |")
    return lines


def report(rows: list[dict[str, str]], out_dir: Path) -> str:
    lines = [
        "# Generated Regime-Probe Summary",
        "",
        "This is the concise generated-regime probe summary requested by the top-tier plan.",
        "It combines the endpoint-backed hard-negative, coverage-shift, and prefix-positive Can probes into one paper-facing artifact.",
        "",
        "## Summary",
        "",
        *markdown_table(
            rows,
            [
                ("Probe", "probe_label"),
                ("Bad-aware endpoint", "bad_aware_endpoint"),
                ("Positive-only endpoint", "positive_endpoint"),
                ("Delta", "endpoint_delta"),
                ("Bad-aware support pos/bad", "bad_aware_support_pos_bad"),
                ("Positive-only support pos/bad", "positive_support_pos_bad"),
            ],
        ),
        "",
        "## Interpretation",
        "",
        "- All rows are generated split constructions, not default Robomimic benchmark rows.",
        "- They isolate settings where explicit bad labels help beyond matched positive-only retrieval.",
        "- Hidden labels are used to construct and audit the splits; the support rules themselves use only trusted positive labels, trusted bad labels, and unlabeled observations/actions.",
        "- The default benchmark rows remain the primary Can/Lift endpoint matrix and the fresh v0.2 Can+Lift gate.",
        "",
        "## Source Artifacts",
        "",
    ]
    for row in rows:
        lines.append(f"- `{row['probe_label']}`: `{row['source_artifact']}`")
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{out_dir / OUT_CSV}`",
            f"- `{out_dir / OUT_REPORT}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    rows = [summarize_probe(spec) for spec in PROBES]
    write_csv(args.out_dir / OUT_CSV, rows, FIELDNAMES)
    (args.out_dir / OUT_REPORT).write_text(report(rows, args.out_dir), encoding="utf-8")
    print(f"wrote {args.out_dir / OUT_CSV}")
    print(f"wrote {args.out_dir / OUT_REPORT}")


if __name__ == "__main__":
    main()
