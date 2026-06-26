#!/usr/bin/env python3
"""Summarize Candidate K confidence-router screens."""

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
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def metric_success(path: Path) -> tuple[int, int, float]:
    rows = read_csv(path)
    if len(rows) != 1:
        raise ValueError(f"{path}: expected one metric row")
    row = rows[0]
    episodes = int(row["eval_episodes"])
    successes = int(round(float(row["success_rate"]) * episodes))
    return successes, episodes, float(row["avg_len"])


def first_n_successes(path: Path, n: int) -> tuple[int, int, float]:
    rows = read_csv(path)[:n]
    successes = sum(int(float(row["success"])) for row in rows)
    avg_len = sum(float(row["length"]) for row in rows) / len(rows)
    return successes, len(rows), avg_len


def row(
    *,
    split: str,
    method: str,
    report_dir: str,
    protocol: str,
    source: str = "metrics",
) -> dict[str, object]:
    if source == "metrics":
        successes, episodes, avg_len = metric_success(OUT / report_dir / "metrics.csv")
    elif source == "episode_first20":
        successes, episodes, avg_len = first_n_successes(OUT / report_dir / "episode_metrics.csv", 20)
    else:
        raise ValueError(source)
    return {
        "split": split,
        "method": method,
        "successes": successes,
        "episodes": episodes,
        "avg_len": round(avg_len, 3),
        "protocol": protocol,
        "report": f"results/candidate_g_fresh_preflight/{report_dir}/REPORT.md",
    }


def candidate_rows() -> list[dict[str, object]]:
    return [
        row(
            split="lift606",
            method="positive_only_nn",
            report_dir="lift606_positive_epoch200_eval20",
            protocol="20 valid-positive starts",
            source="episode_first20",
        ),
        row(
            split="lift606",
            method="triage_bc",
            report_dir="lift606_triage_epoch200_eval20",
            protocol="20 valid-positive starts",
            source="episode_first20",
        ),
        row(
            split="lift606",
            method="weighted_bc",
            report_dir="lift606_weighted_epoch200_eval50",
            protocol="20 valid-positive starts",
            source="episode_first20",
        ),
        row(
            split="lift606",
            method="confidence_router_thr5p93",
            report_dir="lift606_router_confidence_poslogp_triage_eval20",
            protocol="20 valid-positive starts",
        ),
        row(
            split="lift606",
            method="confidence_router_thr6p27",
            report_dir="lift606_router_confidence_poslogp_triage_thr6p27_eval20",
            protocol="20 valid-positive starts",
        ),
        row(
            split="lift606",
            method="positive_only_nn",
            report_dir="lift606_positive_epoch200_eval50",
            protocol="50 valid-positive starts",
        ),
        row(
            split="lift606",
            method="triage_bc",
            report_dir="lift606_triage_epoch200_eval50",
            protocol="50 valid-positive starts",
        ),
        row(
            split="lift606",
            method="weighted_bc",
            report_dir="lift606_weighted_epoch200_eval50",
            protocol="50 valid-positive starts",
        ),
        row(
            split="lift606",
            method="confidence_router_thr6p27",
            report_dir="lift606_router_confidence_poslogp_triage_thr6p27_eval50",
            protocol="50 valid-positive starts",
        ),
        row(
            split="lift707",
            method="positive_only_nn",
            report_dir="lift707_positive_epoch200_eval20",
            protocol="20 valid-positive starts",
        ),
        row(
            split="lift707",
            method="triage_bc",
            report_dir="lift707_triage_epoch200_eval20",
            protocol="20 valid-positive starts",
        ),
        row(
            split="lift707",
            method="confidence_router_thr6p27",
            report_dir="lift707_router_confidence_poslogp_triage_thr6p27_eval20",
            protocol="20 valid-positive starts",
        ),
    ]


def table(rows: list[dict[str, object]], split: str, protocol: str) -> list[str]:
    selected = [row for row in rows if row["split"] == split and row["protocol"] == protocol]
    lines = [
        "| method | successes | avg len |",
        "| --- | ---: | ---: |",
    ]
    for row in selected:
        lines.append(f"| {row['method']} | {row['successes']}/{row['episodes']} | {row['avg_len']} |")
    return lines


def main() -> None:
    rows = candidate_rows()
    csv_path = OUT / "candidate_k_confidence_router_summary.csv"
    write_csv(
        csv_path,
        rows,
        ["split", "method", "successes", "episodes", "avg_len", "protocol", "report"],
    )

    audit_report = OUT / "candidate_k_lift_confidence_audit_REPORT.md"
    report_path = OUT / "candidate_k_confidence_router_screen_REPORT.md"
    lines = [
        "# Candidate K Confidence Router Screen",
        "",
        "**Status: rejected as a frozen candidate.** Candidate K routes from",
        "positive-only to triage when the positive top-mode action has low learned",
        "GMM log-likelihood under the triage policy. Threshold `6.269868` was",
        "selected from the Lift606 exploratory audit and then tested unchanged on",
        "Lift707.",
        "",
        "## Lift606 Development Screen",
        "",
        *table(rows, "lift606", "20 valid-positive starts"),
        "",
        "On the tuned Lift606 first-20 screen, the confidence router reaches",
        "`18/20`, above positive-only `14/20` and triage `13/20`.",
        "",
        "## Lift606 Broader Endpoint",
        "",
        *table(rows, "lift606", "50 valid-positive starts"),
        "",
        "The same threshold reaches `32/50`, above positive-only `28/50`, triage",
        "`23/50`, and weighted `16/50` on Lift606.",
        "",
        "## Lift707 Fresh Screen",
        "",
        *table(rows, "lift707", "20 valid-positive starts"),
        "",
        "The fixed threshold does not transfer to Lift707: the router reaches",
        "`10/20`, below positive-only `12/20` and only above triage `9/20`.",
        "",
        "## Read",
        "",
        "- Learned GMM confidence has real local signal on Lift606, unlike nearest",
        "  support-margin routing.",
        "- The fixed threshold is not stable enough for a method claim. Candidate K",
        "  should not be scaled as-is.",
        "- The next useful direction is either threshold calibration from labeled",
        "  validation features, or a temporal confidence gate that adapts within an",
        "  episode, not another globally fixed Lift threshold.",
        "",
        "## Artifacts",
        "",
        f"- Summary CSV: `{csv_path.relative_to(ROOT)}`.",
        f"- Feature audit report: `{audit_report.relative_to(ROOT)}`.",
        "- Lift606 router 50-episode eval: `results/candidate_g_fresh_preflight/lift606_router_confidence_poslogp_triage_thr6p27_eval50/REPORT.md`.",
        "- Lift707 router eval: `results/candidate_g_fresh_preflight/lift707_router_confidence_poslogp_triage_thr6p27_eval20/REPORT.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
