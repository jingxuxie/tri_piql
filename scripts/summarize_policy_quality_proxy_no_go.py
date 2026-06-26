from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


TABLE_DIR = Path("results/final_paper/tables")
ABLATION_DIR = Path("results/final_paper/ablations")

PROXY_VALIDATION = TABLE_DIR / "proxy_endpoint_validation.csv"
PROXY_WINNERS = TABLE_DIR / "proxy_endpoint_validation_winners.csv"
PROXY_CORRELATIONS = TABLE_DIR / "proxy_endpoint_validation_correlations.csv"
CANDIDATE_AUDIT = TABLE_DIR / "candidate_family_audit.csv"
CAN_MG_PROXY_WINNERS = ABLATION_DIR / "can_mg_branch_proxy_summary" / "proxy_winners.csv"
CAN_MG_PROXY_SCORES = ABLATION_DIR / "can_mg_branch_proxy_summary" / "method_proxy_scores.csv"
ACTION_RISK_ROOT = ABLATION_DIR / "v02_action_risk_endpoint_200ep_can40"
POLICY_COVERAGE_SPLIT11 = TABLE_DIR / "v02_policy_coverage_diagnostic.csv"
POLICY_COVERAGE_SPLIT22 = TABLE_DIR / "v02_policy_coverage_diagnostic_split22.csv"
LIFT_CLASSIFIER = ABLATION_DIR / "lift_mg_classifier_top160_endpoint_summary.csv"

DEFAULT_OUT_DIR = TABLE_DIR

OUT_CSV = "policy_quality_proxy_no_go.csv"
OUT_REPORT = "policy_quality_proxy_no_go_REPORT.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
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


def fmt(value: float | str | None, digits: int = 3) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}f}"


def fmt_endpoint(successes: int | str | None, episodes: int | str | None) -> str:
    if successes in ("", None) or episodes in ("", None):
        return ""
    return f"{as_int(successes)}/{as_int(episodes)}"


def endpoint_from_rate(rate: str, episodes: str) -> str:
    eval_episodes = as_int(episodes)
    return fmt_endpoint(round(as_float(rate) * eval_episodes), eval_episodes)


def audit_index() -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row["setting_id"], row["candidate_label"]): row
        for row in read_rows(CANDIDATE_AUDIT)
    }


def row(
    *,
    evidence_id: str,
    setting: str,
    proxy_family: str,
    proxy_signal: str,
    proxy_selected_method: str,
    proxy_selected_endpoint: str,
    endpoint_winner: str,
    endpoint_winner_endpoint: str,
    proxy_matches_endpoint: bool,
    deployable_proxy: bool = True,
    audit_only: bool = False,
    support_purity: str = "",
    hidden_positive_recall: str = "",
    hidden_bad_admission: str = "",
    coverage_proxy_score: str = "",
    source: str,
    interpretation: str,
) -> dict[str, str]:
    return {
        "evidence_id": evidence_id,
        "setting": setting,
        "proxy_family": proxy_family,
        "proxy_signal": proxy_signal,
        "proxy_selected_method": proxy_selected_method,
        "proxy_selected_endpoint": proxy_selected_endpoint,
        "endpoint_winner": endpoint_winner,
        "endpoint_winner_endpoint": endpoint_winner_endpoint,
        "proxy_matches_endpoint": str(proxy_matches_endpoint).lower(),
        "deployable_proxy": str(deployable_proxy).lower(),
        "audit_only": str(audit_only).lower(),
        "support_purity": support_purity,
        "hidden_positive_recall": hidden_positive_recall,
        "hidden_bad_admission": hidden_bad_admission,
        "coverage_proxy_score": coverage_proxy_score,
        "source": source,
        "interpretation": interpretation,
    }


def coverage_proxy_rows() -> list[dict[str, str]]:
    audit = audit_index()
    out: list[dict[str, str]] = []
    for item in read_rows(PROXY_WINNERS):
        setting_id = item["setting_id"]
        proxy_label = item["coverage_proxy_winner"]
        audit_row = audit.get((setting_id, proxy_label), {})
        out.append(
            row(
                evidence_id=f"coverage_proxy_{setting_id}",
                setting=item["setting_label"],
                proxy_family="coverage proxy",
                proxy_signal="selects the largest hidden-label-free support coverage score",
                proxy_selected_method=proxy_label,
                proxy_selected_endpoint=item["coverage_proxy_winner_success"],
                endpoint_winner=item["endpoint_winner"],
                endpoint_winner_endpoint=item["endpoint_winner_success"],
                proxy_matches_endpoint=item["coverage_proxy_matches_endpoint"] == "true",
                support_purity=audit_row.get("support_purity", ""),
                hidden_positive_recall=audit_row.get("hidden_positive_recall", ""),
                hidden_bad_admission=audit_row.get("hidden_bad_admission", ""),
                coverage_proxy_score=audit_row.get("coverage_proxy_score", ""),
                source=f"{PROXY_WINNERS}; {CANDIDATE_AUDIT}",
                interpretation=(
                    "Coverage is useful on some broad-coverage settings, but it over-selects weighted support on contaminated Can when precision matters."
                ),
            )
        )
    return out


def audit_score_rows() -> list[dict[str, str]]:
    audit = audit_index()
    out: list[dict[str, str]] = []
    for item in read_rows(PROXY_WINNERS):
        setting_id = item["setting_id"]
        proxy_label = item["audit_score_winner"]
        if not proxy_label:
            continue
        audit_row = audit.get((setting_id, proxy_label), {})
        out.append(
            row(
                evidence_id=f"audit_score_{setting_id}",
                setting=item["setting_label"],
                proxy_family="audit-only support score",
                proxy_signal="maximizes hidden-positive recall minus hidden-bad admission; not deployable",
                proxy_selected_method=proxy_label,
                proxy_selected_endpoint=item["audit_score_winner_success"],
                endpoint_winner=item["endpoint_winner"],
                endpoint_winner_endpoint=item["endpoint_winner_success"],
                proxy_matches_endpoint=item["audit_score_matches_endpoint"] == "true",
                deployable_proxy=False,
                audit_only=True,
                support_purity=audit_row.get("support_purity", ""),
                hidden_positive_recall=audit_row.get("hidden_positive_recall", ""),
                hidden_bad_admission=audit_row.get("hidden_bad_admission", ""),
                coverage_proxy_score=audit_row.get("coverage_proxy_score", ""),
                source=f"{PROXY_WINNERS}; {CANDIDATE_AUDIT}",
                interpretation=(
                    "Even an audit-only support score fails on Lift MG, showing that label purity and hidden-positive recall do not by themselves predict policy quality."
                ),
            )
        )
    return out


def can_mg_likelihood_rows() -> list[dict[str, str]]:
    labels = {
        "valid_positive_ll": "positive likelihood",
        "labeled_positive_ll": "positive likelihood",
        "valid_contrastive_gap": "positive-minus-negative likelihood",
        "labeled_contrastive_gap": "positive-minus-negative likelihood",
        "valid_negative_rejection": "negative rejection",
        "labeled_negative_rejection": "negative rejection",
    }
    out: list[dict[str, str]] = []
    for item in read_rows(CAN_MG_PROXY_WINNERS):
        if item["split"] != "can_mg_original":
            continue
        proxy_name = item["proxy"]
        out.append(
            row(
                evidence_id=f"can_mg_{proxy_name}",
                setting="Can MG original",
                proxy_family=labels.get(proxy_name, proxy_name),
                proxy_signal=proxy_name,
                proxy_selected_method=item["proxy_winner"],
                proxy_selected_endpoint=fmt(float(item["proxy_winner_rollout_20k"]), 3),
                endpoint_winner=item["rollout_best_method"],
                endpoint_winner_endpoint=fmt(float(item["rollout_best_20k"]), 3),
                proxy_matches_endpoint=item["proxy_matches_rollout_best_method"] == "true",
                source=f"{CAN_MG_PROXY_WINNERS}; {CAN_MG_PROXY_SCORES}",
                interpretation=(
                    "Likelihood-style branch scoring selects all-positive hard support on original Can MG, but weighted BC is rollout-best."
                ),
            )
        )
    return out


def action_risk_row() -> dict[str, str]:
    setup11 = {
        item["candidate_id"]: item
        for item in read_rows(ACTION_RISK_ROOT / "split11" / "endpoint_setup_summary.csv")
    }
    setup22 = {
        item["candidate_id"]: item
        for item in read_rows(ACTION_RISK_ROOT / "split22" / "endpoint_setup_summary.csv")
    }
    pnrf11 = setup11["positive_nn_risk_fusion_top40"]
    pnrf22 = setup22["positive_nn_risk_fusion_top40"]
    selected = as_int(pnrf11["selected_unlabeled"]) + as_int(pnrf22["selected_unlabeled"])
    hidden_pos = as_int(pnrf11["selected_hidden_positive"]) + as_int(pnrf22["selected_hidden_positive"])
    hidden_bad = as_int(pnrf11["selected_hidden_bad"]) + as_int(pnrf22["selected_hidden_bad"])
    total_pos = 80
    total_bad = 160

    pnrf_successes = 0
    pos_successes = 0
    episodes = 0
    for split in ("11", "22"):
        pnrf_metrics = read_rows(
            ACTION_RISK_ROOT / f"split{split}" / "pnrf40" / "eval" / "metrics.csv"
        )[0]
        pos_metrics = read_rows(
            Path(f"results/final_paper/per_seed/can_paired_pos40_bad80_split{split}_positive_only_nn_policy0/eval/metrics.csv")
        )[0]
        split_episodes = as_int(pnrf_metrics["eval_episodes"])
        pnrf_successes += round(as_float(pnrf_metrics["success_rate"]) * split_episodes)
        pos_successes += round(as_float(pos_metrics["success_rate"]) * split_episodes)
        episodes += split_episodes

    return row(
        evidence_id="action_risk_high_purity_can40",
        setting="Can 40p/80b split 11+22",
        proxy_family="support purity plus action-risk",
        proxy_signal="positive-NN/risk fusion improves hidden-label support audit",
        proxy_selected_method="positive-NN/risk fusion top40",
        proxy_selected_endpoint=fmt_endpoint(pnrf_successes, episodes),
        endpoint_winner="positive-only NN top40",
        endpoint_winner_endpoint=fmt_endpoint(pos_successes, episodes),
        proxy_matches_endpoint=False,
        deployable_proxy=False,
        audit_only=True,
        support_purity=fmt(hidden_pos / selected),
        hidden_positive_recall=fmt(hidden_pos / total_pos),
        hidden_bad_admission=fmt(hidden_bad / total_bad),
        source=f"{ACTION_RISK_ROOT}/REPORT.md; split*/endpoint_setup_summary.csv",
        interpretation=(
            "The risk-fusion support is nearly pure and recovers almost all hidden positives, but it still loses the two-split endpoint check."
        ),
    )


def lift_topk_row() -> dict[str, str]:
    item = read_rows(LIFT_CLASSIFIER)[0]
    selected = sum(as_int(item[f"split{split}_selected_unlabeled"]) for split in ("11", "22", "33"))
    hidden_pos = sum(as_int(item[f"split{split}_hidden_positive"]) for split in ("11", "22", "33"))
    hidden_bad = sum(as_int(item[f"split{split}_hidden_bad"]) for split in ("11", "22", "33"))
    total_pos = 828
    total_bad = 3432
    return row(
        evidence_id="lift_classifier_top160_purity",
        setting="Lift MG",
        proxy_family="support purity plus hidden-positive recall",
        proxy_signal="classifier top160 has high purity on every split",
        proxy_selected_method="classifier-score top160",
        proxy_selected_endpoint=fmt_endpoint(item["pooled_successes"], item["pooled_episodes"]),
        endpoint_winner="weighted BC",
        endpoint_winner_endpoint="93/150",
        proxy_matches_endpoint=False,
        deployable_proxy=False,
        audit_only=True,
        support_purity=fmt(hidden_pos / selected),
        hidden_positive_recall=fmt(hidden_pos / total_pos),
        hidden_bad_admission=fmt(hidden_bad / total_bad),
        source=str(LIFT_CLASSIFIER),
        interpretation=(
            "A broader high-purity hard support rule still underperforms weighted BC, so purity and recall do not solve Lift policy quality."
        ),
    )


def policy_coverage_row() -> dict[str, str]:
    split22 = {item["method_id"]: item for item in read_rows(POLICY_COVERAGE_SPLIT22)}
    risk = split22["positive_nn_risk_fusion_top40"]
    pos = split22["positive_only_nn"]
    return row(
        evidence_id="initial_transition_coverage_split22",
        setting="Can 40p/80b split 22",
        proxy_family="initial-state and transition coverage",
        proxy_signal=(
            "risk fusion has no selected bad support and slightly lower transition positive-NN distance "
            f"({fmt(risk['valid_transition_nn_positive_mean'])} vs {fmt(pos['valid_transition_nn_positive_mean'])})"
        ),
        proxy_selected_method="positive-NN/risk fusion top40",
        proxy_selected_endpoint=endpoint_from_rate(risk["endpoint_success"], "50"),
        endpoint_winner="positive-only NN top40",
        endpoint_winner_endpoint=endpoint_from_rate(pos["endpoint_success"], "50"),
        proxy_matches_endpoint=False,
        support_purity="1.000",
        hidden_positive_recall="1.000",
        hidden_bad_admission="0.000",
        source=f"{POLICY_COVERAGE_SPLIT22}; {TABLE_DIR / 'v02_policy_coverage_diagnostic_split22_REPORT.md'}",
        interpretation=(
            "Nearest-neighbor reset/transition coverage does not explain the split-22 endpoint reversal."
        ),
    )


def all_rows() -> list[dict[str, str]]:
    rows = []
    rows.extend(coverage_proxy_rows())
    rows.extend(audit_score_rows())
    rows.extend(can_mg_likelihood_rows())
    rows.append(action_risk_row())
    rows.append(lift_topk_row())
    rows.append(policy_coverage_row())
    return rows


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for item in rows:
        lines.append("| " + " | ".join(item.get(column, "") for column in columns) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    coverage = [row for row in rows if row["proxy_family"] == "coverage proxy"]
    can_mg = [row for row in rows if row["setting"] == "Can MG original"]
    deployable = [row for row in rows if row["deployable_proxy"] == "true"]
    audit_only = [row for row in rows if row["audit_only"] == "true"]
    mismatches = [row for row in rows if row["proxy_matches_endpoint"] == "false"]
    match_counts = Counter(row["proxy_family"] for row in rows if row["proxy_matches_endpoint"] == "true")
    total_counts = Counter(row["proxy_family"] for row in rows)
    corr_rows = read_rows(PROXY_CORRELATIONS)
    all_corr = next(item for item in corr_rows if item["analysis_set"] == "all endpoint-evaluated support rows")
    primary_corr = next(item for item in corr_rows if item["analysis_set"] == "primary complete rows")

    lines: list[str] = [
        "# Policy-Quality Proxy No-Go Table",
        "",
        "This artifact consolidates the current negative evidence for simple hidden-label-free policy-quality proxies. "
        "The table is not a new endpoint experiment; it normalizes existing staged reports into the proxy categories needed for the paper appendix.",
        "",
        "## Summary",
        "",
        f"- Coverage-only winner matches endpoint winner in `{sum(row['proxy_matches_endpoint'] == 'true' for row in coverage)}/{len(coverage)}` evaluated settings.",
        f"- On all endpoint-evaluated support rows, coverage-proxy Pearson/Spearman correlations with endpoint success are `{all_corr['coverage_proxy_pearson']}`/`{all_corr['coverage_proxy_spearman']}`.",
        f"- On primary complete rows, coverage-proxy Pearson/Spearman correlations are `{primary_corr['coverage_proxy_pearson']}`/`{primary_corr['coverage_proxy_spearman']}`.",
        f"- Original Can MG likelihood-style proxies match the rollout-best method in `{sum(row['proxy_matches_endpoint'] == 'true' for row in can_mg)}/{len(can_mg)}` checks.",
        f"- Deployable proxy attempts match endpoint winners in `{sum(row['proxy_matches_endpoint'] == 'true' for row in deployable)}/{len(deployable)}` rows.",
        f"- Audit-only support rows match endpoint winners in `{sum(row['proxy_matches_endpoint'] == 'true' for row in audit_only)}/{len(audit_only)}` rows.",
        f"- Total mismatching proxy rows in this consolidated table: `{len(mismatches)}/{len(rows)}`.",
        "",
        "## Proxy Family Match Counts",
        "",
        "| proxy family | matches | total |",
        "|---|---:|---:|",
    ]
    for proxy_family in sorted(total_counts):
        lines.append(f"| {proxy_family} | {match_counts[proxy_family]} | {total_counts[proxy_family]} |")
    lines.extend(
        [
            "",
            "## Consolidated Evidence",
            "",
            *markdown_table(
                rows,
                [
                    "setting",
                    "proxy_family",
                    "proxy_selected_method",
                    "proxy_selected_endpoint",
                    "endpoint_winner",
                    "endpoint_winner_endpoint",
                    "proxy_matches_endpoint",
                    "deployable_proxy",
                    "audit_only",
                    "support_purity",
                    "hidden_positive_recall",
                    "hidden_bad_admission",
                ],
            ),
            "",
            "## Interpretation",
            "",
            "- Positive likelihood, positive-minus-negative likelihood, and negative rejection fail on original Can MG: all select all-positive hard support, while weighted BC is rollout-best.",
            "- Coverage-only selection is useful for Lift but over-selects broad weighted support in contaminated Can settings.",
            "- Support purity and hidden-positive recall are not sufficient: action-risk Can support and Lift classifier top-k look strong in audit space but lose endpoint comparisons.",
            "- Initial-state and transition nearest-neighbor coverage is descriptive but not enough to decide between high-purity support candidates.",
            "",
            "## Paper Claim",
            "",
            "> Policy-quality prediction remains an open problem: a score that separates positives and negatives, a pure selected support set, or a simple coverage proxy is not enough to choose the best policy-training branch.",
            "",
            "## Outputs",
            "",
            "- `results/final_paper/tables/policy_quality_proxy_no_go.csv`",
            "- `results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = all_rows()
    fieldnames = [
        "evidence_id",
        "setting",
        "proxy_family",
        "proxy_signal",
        "proxy_selected_method",
        "proxy_selected_endpoint",
        "endpoint_winner",
        "endpoint_winner_endpoint",
        "proxy_matches_endpoint",
        "deployable_proxy",
        "audit_only",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "coverage_proxy_score",
        "source",
        "interpretation",
    ]
    write_csv(args.out_dir / OUT_CSV, rows, fieldnames)
    write_report(args.out_dir / OUT_REPORT, rows)
    print(f"wrote {args.out_dir / OUT_CSV}")
    print(f"wrote {args.out_dir / OUT_REPORT}")


if __name__ == "__main__":
    main()
