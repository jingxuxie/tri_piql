from __future__ import annotations

import csv
from pathlib import Path


OUT_DIR = Path("results/final_paper/tables")

CAN40 = OUT_DIR / "can_paired_pos40_bad80_final_endpoint_summary.csv"
CAN20 = Path("results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split.csv")
CAN80 = Path("results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint.csv")
LIFT = OUT_DIR / "lift_mg_mg_sparse_final_endpoint_summary.csv"
POINTNAV_BAD_COUNT = Path("results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5.csv")
PER_SEED = Path("results/final_paper/per_seed")

SPLIT_SEEDS = [11, 22, 33]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt_float(value: float) -> str:
    return f"{value:.3f}"


def fmt_count(successes: int | None, episodes: int | None) -> str:
    if successes is None or episodes is None:
        return ""
    return f"{successes}/{episodes}"


def fmt_support(hidden_positive: int | None, hidden_bad: int | None, selected: int | None) -> str:
    if hidden_positive is None or hidden_bad is None or selected is None:
        return ""
    purity = hidden_positive / selected if selected else 0.0
    return f"{hidden_positive} pos, {hidden_bad} bad / {selected} selected (purity {purity:.3f})"


def row(
    *,
    setting: str,
    bad_aware_method: str,
    comparison_baseline: str,
    bad_aware_endpoint: str,
    baseline_endpoint: str,
    bad_aware_support: str,
    baseline_support: str,
    endpoint_delta_bad_aware_minus_baseline: str,
    interpretation: str,
    source: str,
) -> dict[str, str]:
    return {
        "setting": setting,
        "bad_aware_method": bad_aware_method,
        "comparison_baseline": comparison_baseline,
        "bad_aware_endpoint": bad_aware_endpoint,
        "baseline_endpoint": baseline_endpoint,
        "bad_aware_support": bad_aware_support,
        "baseline_support": baseline_support,
        "endpoint_delta_bad_aware_minus_baseline": endpoint_delta_bad_aware_minus_baseline,
        "interpretation": interpretation,
        "source": source,
    }


def can40_row() -> dict[str, str]:
    aggregate = next(item for item in read_rows(CAN40) if item["split_seed"] == "aggregate")
    triage_successes = int(aggregate["triage_successes"])
    posonly_successes = int(aggregate["positive_only_nn_successes"])
    episodes = int(aggregate["eval_episodes"])
    return row(
        setting="Can 40p/80b primary frozen 3-split",
        bad_aware_method="TRIAGE-BC adaptive masscap",
        comparison_baseline="positive-only NN top40",
        bad_aware_endpoint=fmt_count(triage_successes, episodes),
        baseline_endpoint=fmt_count(posonly_successes, episodes),
        bad_aware_support=fmt_support(
            int(aggregate["triage_hidden_positive"]),
            int(aggregate["triage_hidden_bad"]),
            int(aggregate["triage_selected_unlabeled"]),
        ),
        baseline_support=fmt_support(
            int(aggregate["positive_only_nn_hidden_positive"]),
            int(aggregate["positive_only_nn_hidden_bad"]),
            int(aggregate["positive_only_nn_selected_unlabeled"]),
        ),
        endpoint_delta_bad_aware_minus_baseline=fmt_float((triage_successes - posonly_successes) / episodes),
        interpretation=(
            "Bad-aware scoring recovers slightly more hidden-positive demos, but the converter admits much more hidden-bad support; positive-only retrieval is the stronger endpoint baseline."
        ),
        source="results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md",
    )


def can20_row() -> dict[str, str]:
    rows = {item["support_rule"]: item for item in read_rows(CAN20)}
    triage = rows["triage_adaptive_masscap"]
    posonly = rows["positive_only_nn_top20"]
    triage_successes = int(triage["endpoint_successes"])
    posonly_successes = int(posonly["endpoint_successes"])
    episodes = int(triage["endpoint_episodes"])
    return row(
        setting="Can 20p/80b diagnostic support audit + two endpoints",
        bad_aware_method="TRIAGE-BC adaptive masscap",
        comparison_baseline="positive-only NN top20",
        bad_aware_endpoint=fmt_count(triage_successes, episodes),
        baseline_endpoint=fmt_count(posonly_successes, int(posonly["endpoint_episodes"])),
        bad_aware_support=fmt_support(
            int(triage["total_hidden_positive"]),
            int(triage["total_hidden_bad"]),
            int(float(triage["mean_selected_unlabeled"]) * int(triage["num_splits"])),
        ),
        baseline_support=fmt_support(
            int(posonly["total_hidden_positive"]),
            int(posonly["total_hidden_bad"]),
            int(float(posonly["mean_selected_unlabeled"]) * int(posonly["num_splits"])),
        ),
        endpoint_delta_bad_aware_minus_baseline=fmt_float((triage_successes - posonly_successes) / episodes),
        interpretation=(
            "TRIAGE-BC recovers more hidden positives under heavier contamination, but positive-only retrieval admits far fewer bad demos and wins the completed endpoints."
        ),
        source="results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md",
    )


def can80_row() -> dict[str, str]:
    rows = read_rows(CAN80)
    triage_rows = [item for item in rows if item["method"] == "triage_bc_adaptive_masscap"]
    posonly_rows = [item for item in rows if item["method"] == "positive_only_nn_top80"]
    triage_endpoint = next(item for item in triage_rows if item["status"] == "endpoint")
    posonly_endpoint = next(item for item in posonly_rows if item["status"] == "endpoint")
    triage_successes = int(triage_endpoint["endpoint_successes"])
    posonly_successes = int(posonly_endpoint["endpoint_successes"])
    episodes = int(triage_endpoint["eval_episodes"])
    return row(
        setting="Can 80p/80b balanced diagnostic",
        bad_aware_method="TRIAGE-BC adaptive masscap",
        comparison_baseline="positive-only NN top80",
        bad_aware_endpoint=fmt_count(triage_successes, episodes),
        baseline_endpoint=fmt_count(posonly_successes, int(posonly_endpoint["eval_episodes"])),
        bad_aware_support=fmt_support(
            sum(int(item["hidden_positive"]) for item in triage_rows),
            sum(int(item["hidden_bad"]) for item in triage_rows),
            sum(int(item["selected_unlabeled"]) for item in triage_rows),
        ),
        baseline_support=fmt_support(
            sum(int(item["hidden_positive"]) for item in posonly_rows),
            sum(int(item["hidden_bad"]) for item in posonly_rows),
            sum(int(item["selected_unlabeled"]) for item in posonly_rows),
        ),
        endpoint_delta_bad_aware_minus_baseline=fmt_float((triage_successes - posonly_successes) / episodes),
        interpretation=(
            "The balanced diagnostic also favors positive-only retrieval; even the split where TRIAGE-BC has purer support has lower endpoint success."
        ),
        source="results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md",
    )


def lift_support(method_slug: str) -> tuple[int, int, int]:
    selected = 0
    hidden_positive = 0
    hidden_bad = 0
    for split_seed in SPLIT_SEEDS:
        path = (
            PER_SEED
            / f"lift_mg_mg_sparse_split{split_seed}_{method_slug}_policy0"
            / "hidden_label_audit.csv"
        )
        audit = read_rows(path)[0]
        selected += int(audit["selected_unlabeled"])
        hidden_positive += int(audit["hidden_positive"])
        hidden_bad += int(audit["hidden_bad"])
    return selected, hidden_positive, hidden_bad


def lift_row() -> dict[str, str]:
    rows = {item["method"]: item for item in read_rows(LIFT)}
    triage = rows["TRIAGE-BC / pos-min"]
    posonly = rows["positive-only NN top160"]
    triage_successes = int(triage["pooled_successes"])
    posonly_successes = int(posonly["pooled_successes"])
    episodes = int(triage["pooled_episodes"])
    triage_selected, triage_pos, triage_bad = lift_support("triage_bc")
    posonly_selected, posonly_pos, posonly_bad = lift_support("positive_only_nn")
    return row(
        setting="Lift MG primary frozen 3-split",
        bad_aware_method="TRIAGE-BC pos-min",
        comparison_baseline="positive-only NN top160",
        bad_aware_endpoint=fmt_count(triage_successes, episodes),
        baseline_endpoint=fmt_count(posonly_successes, int(posonly["pooled_episodes"])),
        bad_aware_support=fmt_support(triage_pos, triage_bad, triage_selected),
        baseline_support=fmt_support(posonly_pos, posonly_bad, posonly_selected),
        endpoint_delta_bad_aware_minus_baseline=fmt_float((triage_successes - posonly_successes) / episodes),
        interpretation=(
            "Bad-aware pos-min support is much purer and recovers more hidden positives, but the fixed endpoint still trails the broader positive-only baseline."
        ),
        source="results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md",
    )


def pointnav_row() -> dict[str, str]:
    rows = read_rows(POINTNAV_BAD_COUNT)
    triage_successes = [float(item["triage_gap_demo_bc"]) for item in rows]
    bc_all_successes = [float(item["bc_all"]) for item in rows]
    local_weighted_successes = [float(item["local_weighted_bc"]) for item in rows]
    hidden_bad = [float(item["hidden_bad_demos"]) for item in rows]
    purity = [float(item["selected_demo_purity"]) for item in rows]
    return row(
        setting="Controlled PointNav n+=5, n- in {1,2,5}",
        bad_aware_method="score-gap support with explicit bad labels",
        comparison_baseline="mixed-log / local weighted BC",
        bad_aware_endpoint=f"min {min(triage_successes):.3f}, mean {sum(triage_successes) / len(triage_successes):.3f}",
        baseline_endpoint=(
            f"BC-all mean {sum(bc_all_successes) / len(bc_all_successes):.3f}; "
            f"local weighted mean {sum(local_weighted_successes) / len(local_weighted_successes):.3f}"
        ),
        bad_aware_support=f"min purity {min(purity):.3f}; max hidden-bad demos {max(hidden_bad):.1f}",
        baseline_support="",
        endpoint_delta_bad_aware_minus_baseline="",
        interpretation=(
            "In the controlled mechanism, even one labeled bad shortcut is enough for pure hidden-good support; this supports label-efficient calibration, not Can bad-label necessity."
        ),
        source="results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md",
    )


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for item in rows:
        lines.append("| " + " | ".join(item[column] for column in columns) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    columns = [
        "setting",
        "bad_aware_method",
        "comparison_baseline",
        "bad_aware_endpoint",
        "baseline_endpoint",
        "endpoint_delta_bad_aware_minus_baseline",
    ]
    support_columns = [
        "setting",
        "bad_aware_support",
        "baseline_support",
        "interpretation",
    ]
    lines = [
        "# Bad-Label Control Summary",
        "",
        "This report consolidates the paper-facing bad-label evidence from staged final-paper artifacts.",
        "It is a claim guardrail: explicit bad labels can help score calibration and support purity, but the current bad-aware converter is not uniformly better than strong no-bad-label retrieval.",
        "",
        "## Endpoint Comparisons",
        "",
        *markdown_table(rows, columns),
        "",
        "## Support And Interpretation",
        "",
        *markdown_table(rows, support_columns),
        "",
        "## Paper Wording",
        "",
        "- Use this table to support: bad labels improve calibration and sometimes recover hidden support.",
        "- Do not use this table to claim: bad labels are necessary, TRIAGE-BC uniformly beats positive-only retrieval, or hard support always wins.",
        "- The strongest current wording is that explicit failures are calibration signal whose value depends on score-to-support conversion and task coverage.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = [pointnav_row(), can40_row(), can20_row(), can80_row(), lift_row()]
    csv_path = OUT_DIR / "bad_label_control_summary.csv"
    report_path = OUT_DIR / "bad_label_control_summary_REPORT.md"
    write_csv(csv_path, rows)
    write_report(report_path, rows)
    print(f"wrote {csv_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
