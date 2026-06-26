from __future__ import annotations

import argparse
import csv
from pathlib import Path


TABLE_DIR = Path("results/final_paper/tables")
ABLATION_DIR = Path("results/final_paper/ablations")

TRADEOFF = ABLATION_DIR / "can40_score_support_tradeoff.csv"
TRADEOFF_PER_SPLIT = ABLATION_DIR / "can40_score_support_tradeoff_per_split.csv"
UNION_SUPPORT = TABLE_DIR / "v02_union_candidate_support_summary.csv"
UNION_SUPPORT_PER_SPLIT = TABLE_DIR / "v02_union_candidate_support_per_split.csv"
UNION_ENDPOINT_ROOT = ABLATION_DIR / "v02_union_endpoint_200ep_can40"
UNION_ENDPOINT = UNION_ENDPOINT_ROOT / "endpoint_200ep_3split_summary.csv"

OUT_CSV = "hard_union_component_ablation.csv"
OUT_PER_SPLIT = "hard_union_component_ablation_per_split.csv"
OUT_REPORT = "hard_union_component_ablation_REPORT.md"

SPLIT_SEEDS = ("11", "22", "33")


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


def as_float(value: object) -> float:
    if value in ("", None):
        return 0.0
    return float(str(value))


def as_int(value: object) -> int:
    if value in ("", None):
        return 0
    return int(round(float(str(value))))


def fmt(value: float | str | None) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.3f}"


def fmt_count(successes: object, episodes: object) -> str:
    if successes in ("", None) or episodes in ("", None):
        return ""
    return f"{as_int(successes)}/{as_int(episodes)}"


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def endpoint_summary() -> dict[str, dict[str, str]]:
    rows = by_key(read_rows(UNION_ENDPOINT), "method_id")
    return {
        "positive_only_nn_top40": rows["positive_only_nn"],
        "positive_nn_risk_fusion_top40": rows["positive_nn_risk_fusion_top40"],
        "positive_nn_risk_union_top40": rows["positive_nn_risk_union_top40"],
        "classifier_top40": {},
        "weighted_full_pool": rows["weighted_bc"],
        "triage_adaptive_masscap": rows["triage_bc"],
    }


def support_summary() -> dict[str, dict[str, str]]:
    union_rows = {
        row["candidate_id"]: row
        for row in read_rows(UNION_SUPPORT)
        if row["setting_id"] == "can40"
    }
    tradeoff_rows = by_key(read_rows(TRADEOFF), "support_rule")
    return {
        "positive_only_nn_top40": union_rows["positive_nn_top40"],
        "positive_nn_risk_fusion_top40": union_rows["positive_nn_risk_fusion_top40"],
        "positive_nn_risk_union_top40": union_rows["positive_nn_risk_union_top40"],
        "classifier_top40": tradeoff_rows["classifier_top40"],
        "weighted_full_pool": tradeoff_rows["weighted_full_pool"],
        "triage_adaptive_masscap": tradeoff_rows["triage_adaptive_masscap"],
    }


def support_value(row: dict[str, str], union_field: str, tradeoff_field: str) -> str:
    if union_field in row:
        return row[union_field]
    return row.get(tradeoff_field, "")


def selected_unlabeled(method_id: str, row: dict[str, str]) -> str:
    if "selected_unlabeled" in row:
        return row["selected_unlabeled"]
    return str(as_int(as_float(row["mean_selected"]) * as_int(row["num_splits"])))


def positive_reference_for_endpoint(endpoint: dict[str, str]) -> tuple[int, int]:
    positive = endpoint_summary()["positive_only_nn_top40"]
    positive_splits = parse_split_successes(positive["split_successes"])
    target_splits = parse_split_successes(endpoint.get("split_successes", ""))
    if not target_splits:
        return 0, 0
    successes = 0
    episodes = 0
    for split_seed in target_splits:
        successes += round(positive_splits[split_seed] * 50)
        episodes += 50
    return successes, episodes


def parse_split_successes(value: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for item in value.split(";"):
        if not item:
            continue
        split_seed, rate = item.split(":")
        out[split_seed] = float(rate)
    return out


def endpoint_delta_vs_positive(endpoint: dict[str, str]) -> str:
    if not endpoint:
        return ""
    positive_successes, positive_episodes = positive_reference_for_endpoint(endpoint)
    if positive_episodes == 0:
        return ""
    endpoint_rate = as_int(endpoint["success_count"]) / as_int(endpoint["eval_episodes"])
    positive_rate = positive_successes / positive_episodes
    return f"{endpoint_rate - positive_rate:+.3f}"


def aggregate_rows() -> list[dict[str, str]]:
    supports = support_summary()
    endpoints = endpoint_summary()
    positive = supports["positive_only_nn_top40"]
    specs = [
        (
            "positive_only_nn_top40",
            "positive-only NN top40",
            "positive-only anchor",
            "nearest-neighbor retrieval from trusted positives",
            "Strong high-precision baseline; the union must beat this, not just weighted BC.",
        ),
        (
            "positive_nn_risk_fusion_top40",
            "risk-fusion top40",
            "risk branch alone",
            "rank fusion of positive similarity and action/bad-neighbor risk",
            "Improves hidden support labels, but loses the same two-split endpoint check to positive-only.",
        ),
        (
            "positive_nn_risk_union_top40",
            "positive-NN/risk union top40",
            "union candidate",
            "positive-only support plus risk-fusion additions",
            "Best pooled Can40 endpoint; the gain comes from added coverage on splits 22 and 33, not uniform dominance.",
        ),
        (
            "classifier_top40",
            "classifier-only top40",
            "classifier-only hard support",
            "top-k by bad-aware classifier score",
            "Support-only and dominated by positive-only top40 on both hidden-positive recovery and bad admission.",
        ),
        (
            "weighted_full_pool",
            "weighted BC full pool",
            "soft coverage baseline",
            "sample all unlabeled demos with learned weights",
            "Full coverage admits all hidden bad support and trails the union endpoint.",
        ),
        (
            "triage_adaptive_masscap",
            "v0.1 adaptive masscap",
            "v0.1 hard support",
            "original TRIAGE-BC support converter",
            "Beats weighted BC but admits too many bad demos relative to positive-only and the union.",
        ),
    ]

    rows: list[dict[str, str]] = []
    for method_id, label, role, selection_rule, interpretation in specs:
        support = supports[method_id]
        endpoint = endpoints[method_id]
        hidden_pos = support_value(support, "hidden_positive_selected", "total_hidden_positive")
        hidden_bad = support_value(support, "hidden_bad_selected", "total_hidden_bad")
        recall = support_value(support, "hidden_positive_recall", "hidden_positive_recall")
        bad_admission = support_value(support, "hidden_bad_admission", "hidden_bad_admission")
        purity = support_value(support, "support_purity", "purity")
        rows.append(
            {
                "method_id": method_id,
                "method_label": label,
                "component_role": role,
                "selection_rule": selection_rule,
                "support_split_count": support.get("split_count", support.get("num_splits", "")),
                "endpoint_split_count": endpoint.get("split_count", "0"),
                "selected_unlabeled": selected_unlabeled(method_id, support),
                "hidden_positive_selected": hidden_pos,
                "hidden_bad_selected": hidden_bad,
                "support_purity": fmt(purity),
                "hidden_positive_recall": fmt(recall),
                "hidden_bad_admission": fmt(bad_admission),
                "delta_hidden_positive_vs_positive": str(as_int(hidden_pos) - as_int(positive["hidden_positive_selected"])),
                "delta_hidden_bad_vs_positive": str(as_int(hidden_bad) - as_int(positive["hidden_bad_selected"])),
                "endpoint_success": endpoint.get("endpoint_success", ""),
                "endpoint_success_count": fmt_count(endpoint.get("success_count", ""), endpoint.get("eval_episodes", "")),
                "split_successes": endpoint.get("split_successes", ""),
                "endpoint_delta_vs_positive_same_splits": endpoint_delta_vs_positive(endpoint),
                "endpoint_status": (
                    "complete_3split_endpoint"
                    if endpoint.get("split_count") == "3"
                    else "partial_2split_endpoint"
                    if endpoint.get("split_count") == "2"
                    else "support_only"
                ),
                "source": source_for(method_id),
                "interpretation": interpretation,
            }
        )
    return rows


def source_for(method_id: str) -> str:
    if method_id == "positive_nn_risk_union_top40":
        return f"{UNION_SUPPORT}; {UNION_ENDPOINT}"
    if method_id == "positive_nn_risk_fusion_top40":
        return f"{UNION_SUPPORT}; {UNION_ENDPOINT_ROOT}/split11; {UNION_ENDPOINT_ROOT}/split22"
    if method_id == "positive_only_nn_top40":
        return f"{UNION_SUPPORT}; {UNION_ENDPOINT}"
    if method_id in {"classifier_top40", "weighted_full_pool", "triage_adaptive_masscap"}:
        return str(TRADEOFF)
    raise KeyError(method_id)


def endpoint_split_index() -> dict[tuple[str, str], dict[str, str]]:
    out = {}
    for split_seed in SPLIT_SEEDS:
        for row in read_rows(UNION_ENDPOINT_ROOT / f"split{split_seed}" / "endpoint_200ep_summary.csv"):
            method_id = {
                "positive_only_nn": "positive_only_nn_top40",
                "positive_nn_risk_fusion_top40": "positive_nn_risk_fusion_top40",
                "positive_nn_risk_union_top40": "positive_nn_risk_union_top40",
                "weighted_bc": "weighted_full_pool",
                "triage_bc": "triage_adaptive_masscap",
            }.get(row["method_id"])
            if method_id:
                out[(split_seed, method_id)] = row
    return out


def support_split_index() -> dict[tuple[str, str], dict[str, str]]:
    out = {}
    for row in read_rows(UNION_SUPPORT_PER_SPLIT):
        if row["setting_id"] != "can40":
            continue
        method_id = {
            "positive_nn_top40": "positive_only_nn_top40",
            "positive_nn_risk_fusion_top40": "positive_nn_risk_fusion_top40",
            "positive_nn_risk_union_top40": "positive_nn_risk_union_top40",
        }.get(row["candidate_id"])
        if method_id:
            out[(row["split_seed"], method_id)] = row
    for row in read_rows(TRADEOFF_PER_SPLIT):
        method_id = {
            "classifier_top40": "classifier_top40",
            "weighted_full_pool": "weighted_full_pool",
            "triage_adaptive_masscap": "triage_adaptive_masscap",
            "positive_only_nn_top40": "positive_only_nn_top40",
        }.get(row["support_rule"])
        if method_id:
            out[(row["split_seed"], method_id)] = row
    return out


def per_split_rows() -> list[dict[str, str]]:
    endpoint = endpoint_split_index()
    support = support_split_index()
    methods = [
        ("positive_only_nn_top40", "positive-only NN top40"),
        ("positive_nn_risk_fusion_top40", "risk-fusion top40"),
        ("positive_nn_risk_union_top40", "positive-NN/risk union top40"),
        ("classifier_top40", "classifier-only top40"),
        ("weighted_full_pool", "weighted BC full pool"),
        ("triage_adaptive_masscap", "v0.1 adaptive masscap"),
    ]
    rows: list[dict[str, str]] = []
    for split_seed in SPLIT_SEEDS:
        positive_endpoint = endpoint[(split_seed, "positive_only_nn_top40")]
        positive_rate = as_float(positive_endpoint["endpoint_success"])
        for method_id, label in methods:
            support_row = support.get((split_seed, method_id), {})
            endpoint_row = endpoint.get((split_seed, method_id), {})
            rows.append(
                {
                    "split_seed": split_seed,
                    "method_id": method_id,
                    "method_label": label,
                    "selected_unlabeled": support_row.get("selected_unlabeled", support_row.get("selected", "")),
                    "hidden_positive_selected": support_row.get("hidden_positive_selected", support_row.get("hidden_positive", "")),
                    "hidden_bad_selected": support_row.get("hidden_bad_selected", support_row.get("hidden_bad", "")),
                    "support_purity": fmt(support_row.get("support_purity", support_row.get("purity", ""))),
                    "hidden_positive_recall": fmt(support_row.get("hidden_positive_recall", "")),
                    "hidden_bad_admission": fmt(support_row.get("hidden_bad_admission", "")),
                    "endpoint_success": fmt(endpoint_row.get("endpoint_success", "")),
                    "endpoint_success_count": fmt_count(endpoint_row.get("success_count", ""), endpoint_row.get("eval_episodes", "")),
                    "endpoint_delta_vs_positive": (
                        f"{as_float(endpoint_row['endpoint_success']) - positive_rate:+.3f}" if endpoint_row else ""
                    ),
                    "endpoint_status": "endpoint" if endpoint_row else "support_only",
                }
            )
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row.get(column, "") for column in columns) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, str]], split_rows: list[dict[str, str]]) -> None:
    by_method = {row["method_id"]: row for row in rows}
    union = by_method["positive_nn_risk_union_top40"]
    positive = by_method["positive_only_nn_top40"]
    risk = by_method["positive_nn_risk_fusion_top40"]
    classifier = by_method["classifier_top40"]
    weighted = by_method["weighted_full_pool"]
    triage = by_method["triage_adaptive_masscap"]

    endpoint_rows = [
        row
        for row in split_rows
        if row["method_id"]
        in {
            "positive_only_nn_top40",
            "positive_nn_risk_fusion_top40",
            "positive_nn_risk_union_top40",
            "weighted_full_pool",
            "triage_adaptive_masscap",
        }
    ]
    lines = [
        "# Hard-Union Component Ablation",
        "",
        "This artifact consolidates the v0.2 Can 40p/80b hard-union component evidence.",
        "It does not add new policy training; it normalizes existing support audits and endpoint gates.",
        "",
        "## Aggregate Component Table",
        "",
        *markdown_table(
            rows,
            [
                "method_label",
                "component_role",
                "selected_unlabeled",
                "hidden_positive_selected",
                "hidden_bad_selected",
                "hidden_positive_recall",
                "hidden_bad_admission",
                "endpoint_success_count",
                "endpoint_delta_vs_positive_same_splits",
                "endpoint_status",
            ],
        ),
        "",
        "## Per-Split Endpoint Table",
        "",
        *markdown_table(
            endpoint_rows,
            [
                "split_seed",
                "method_label",
                "hidden_positive_selected",
                "hidden_bad_selected",
                "endpoint_success_count",
                "endpoint_delta_vs_positive",
                "endpoint_status",
            ],
        ),
        "",
        "## Interpretation",
        "",
        (
            f"- Positive-only NN top40 is the required baseline: it selects "
            f"`{positive['hidden_positive_selected']}/120` hidden positives and "
            f"`{positive['hidden_bad_selected']}/240` hidden bad demos, then reaches "
            f"`{positive['endpoint_success_count']}`."
        ),
        (
            f"- Risk-fusion top40 improves the support audit to "
            f"`{risk['hidden_positive_selected']}/120` hidden positives and "
            f"`{risk['hidden_bad_selected']}/240` hidden bad demos, but its two-split endpoint "
            f"is `{risk['endpoint_success_count']}`, `{risk['endpoint_delta_vs_positive_same_splits']}` "
            "versus positive-only on the same split seeds."
        ),
        (
            f"- The union keeps the positive-only anchor and adds risk-fusion coverage, selecting "
            f"`{union['hidden_positive_selected']}/120` hidden positives and "
            f"`{union['hidden_bad_selected']}/240` hidden bad demos. It reaches "
            f"`{union['endpoint_success_count']}`, `{union['endpoint_delta_vs_positive_same_splits']}` "
            "versus positive-only over all three splits."
        ),
        (
            f"- Classifier-only top40 is support-only and is dominated by positive-only top40: "
            f"`{classifier['hidden_positive_selected']}/120` hidden positives and "
            f"`{classifier['hidden_bad_selected']}/240` hidden bad demos."
        ),
        (
            f"- Weighted BC has full coverage but full hidden-bad admission (`{weighted['hidden_bad_selected']}/240`) "
            f"and reaches `{weighted['endpoint_success_count']}`. v0.1 adaptive masscap reaches "
            f"`{triage['endpoint_success_count']}` while admitting `{triage['hidden_bad_selected']}/240` bad demos."
        ),
        "",
        "## Answer",
        "",
        "The union helps because it combines both mechanisms: it preserves the strong positive-only anchor while adding risk-derived coverage. Risk-fusion alone gives the cleanest hidden-label support but is not endpoint-best on its evaluated splits, and classifier-only hard support is not competitive. The pooled union gain comes mainly from split 22 and split 33; split 11 still favors positive-only NN.",
        "",
        "## Outputs",
        "",
        f"- `{TABLE_DIR / OUT_CSV}`",
        f"- `{TABLE_DIR / OUT_PER_SPLIT}`",
        f"- `{TABLE_DIR / OUT_REPORT}`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = aggregate_rows()
    split_rows = per_split_rows()
    aggregate_fields = [
        "method_id",
        "method_label",
        "component_role",
        "selection_rule",
        "support_split_count",
        "endpoint_split_count",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "delta_hidden_positive_vs_positive",
        "delta_hidden_bad_vs_positive",
        "endpoint_success",
        "endpoint_success_count",
        "split_successes",
        "endpoint_delta_vs_positive_same_splits",
        "endpoint_status",
        "source",
        "interpretation",
    ]
    split_fields = [
        "split_seed",
        "method_id",
        "method_label",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "endpoint_success",
        "endpoint_success_count",
        "endpoint_delta_vs_positive",
        "endpoint_status",
    ]
    write_csv(args.out_dir / OUT_CSV, rows, aggregate_fields)
    write_csv(args.out_dir / OUT_PER_SPLIT, split_rows, split_fields)
    write_report(args.out_dir / OUT_REPORT, rows, split_rows)
    print(f"wrote {args.out_dir / OUT_CSV}")
    print(f"wrote {args.out_dir / OUT_PER_SPLIT}")
    print(f"wrote {args.out_dir / OUT_REPORT}")


if __name__ == "__main__":
    main()
