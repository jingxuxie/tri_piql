from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(".")
TABLE_DIR = ROOT / "results" / "final_paper" / "tables"
ABLATION_DIR = ROOT / "results" / "final_paper" / "ablations"

ENDPOINT_MASTER = TABLE_DIR / "endpoint_master_table.csv"
CAN40_TRADEOFF = ABLATION_DIR / "can40_score_support_tradeoff.csv"
CAN20_AUDIT = ABLATION_DIR / "can_paired_pos20_bad80_support_audit_3split.csv"
CAN80_AUDIT = ABLATION_DIR / "can_paired_balanced_80p80b_support_and_split33_endpoint.csv"
CAN_MG_PROXY = ABLATION_DIR / "can_mg_branch_proxy_summary" / "proxy_winners.csv"
UNION_SUPPORT = TABLE_DIR / "v02_union_candidate_support_summary.csv"
UNION_ENDPOINT = ABLATION_DIR / "v02_union_endpoint_200ep_can40" / "endpoint_200ep_3split_summary.csv"

AUDIT_OUT = TABLE_DIR / "candidate_family_audit.csv"
DECISION_OUT = TABLE_DIR / "candidate_family_decision_table.csv"
REPORT_OUT = TABLE_DIR / "candidate_family_oracle_proxy_REPORT.md"

SETTING_ORDER = {
    "can40": 0,
    "lift_mg": 1,
    "can20": 2,
    "can80": 3,
}

TASK_TOTALS_3SPLIT = {
    "Can 40p/80b": (120, 240),
    "Can 20p/80b": (60, 240),
    "Can 80p/80b": (240, 240),
    "Lift MG": (828, 3432),
}

FAMILY_LABELS = {
    "bad_aware_hard": "bad-aware hard",
    "diagnostic_oracle": "diagnostic oracle",
    "mixed_baseline": "mixed baseline",
    "positive_only": "positive-only",
    "soft_weighted": "soft weighted",
    "union_hybrid": "union hybrid",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: object) -> float | None:
    if value in ("", None):
        return None
    return float(value)


def as_int(value: object) -> int:
    return int(round(float(value)))


def fmt(value: object, digits: int = 3) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}f}"


def rate(successes: object, episodes: object) -> str:
    if successes in ("", None) or episodes in ("", None) or as_int(episodes) == 0:
        return ""
    return fmt(as_int(successes) / as_int(episodes))


def method_family(candidate_id: str) -> str:
    if "oracle" in candidate_id or candidate_id == "all_train_positive_oracle":
        return "diagnostic_oracle"
    if "all_demo" in candidate_id or candidate_id == "bc_all_mixed":
        return "mixed_baseline"
    if "union" in candidate_id:
        return "union_hybrid"
    if "positive_only" in candidate_id:
        return "positive_only"
    if "weighted" in candidate_id:
        return "soft_weighted"
    if "triage" in candidate_id or "classifier" in candidate_id:
        return "bad_aware_hard"
    return "bad_aware_hard"


def display_candidate(candidate_id: str, fallback: str = "") -> str:
    labels = {
        "all_train_positive_oracle": "all-positive oracle",
        "bc_all_mixed": "all-demo BC",
        "classifier_top10": "classifier top10",
        "classifier_top20": "classifier top20",
        "classifier_top40": "classifier top40",
        "classifier_top60": "classifier top60",
        "classifier_top80": "classifier top80",
        "classifier_topk": "classifier top-k",
        "classifier_score_top80": "classifier top80",
        "classifier-score top160": "classifier top160",
        "positive_only_nn": "positive-only NN",
        "positive_only_nn_top20": "positive-only NN top20",
        "positive_only_nn_top40": "positive-only NN top40",
        "positive_only_nn_top80": "positive-only NN top80",
        "positive_only_nn_top160": "positive-only NN top160",
        "positive_nn_risk_union_top40": "positive-NN/risk union top40",
        "triage_adaptive_masscap": "TRIAGE-BC adaptive masscap",
        "triage_bc": "TRIAGE-BC",
        "triage_bc_adaptive_masscap": "TRIAGE-BC adaptive masscap",
        "weighted_bc": "weighted BC",
        "weighted_full_pool": "weighted BC full pool",
    }
    return labels.get(candidate_id, fallback or candidate_id.replace("_", " "))


def endpoint_status(endpoint_splits: int, endpoint_episodes: object) -> str:
    if endpoint_episodes in ("", None) or as_int(endpoint_episodes) == 0:
        return "support_only"
    if endpoint_splits >= 3:
        return "complete_3split_endpoint"
    return "partial_endpoint"


def add_candidate(
    rows: list[dict[str, object]],
    *,
    setting_id: str,
    setting_label: str,
    row_role: str,
    candidate_id: str,
    candidate_label: str = "",
    support_splits: int,
    endpoint_splits: int,
    selected_unlabeled: object,
    hidden_positive: object,
    hidden_bad: object,
    total_hidden_positive: object,
    total_hidden_bad: object,
    endpoint_successes: object = "",
    endpoint_episodes: object = "",
    source: str,
    notes: str = "",
) -> None:
    selected = as_int(selected_unlabeled) if selected_unlabeled not in ("", None) else ""
    hidden_pos = as_int(hidden_positive) if hidden_positive not in ("", None) else ""
    hidden_bad_count = as_int(hidden_bad) if hidden_bad not in ("", None) else ""
    total_pos = as_int(total_hidden_positive) if total_hidden_positive not in ("", None) else ""
    total_bad = as_int(total_hidden_bad) if total_hidden_bad not in ("", None) else ""
    support_applicable = selected not in ("", 0)

    purity = ""
    hidden_positive_recall = ""
    hidden_bad_admission = ""
    selected_contamination = ""
    coverage_proxy_score = ""
    audit_oracle_score = ""
    if support_applicable:
        purity = fmt(hidden_pos / selected if selected else 0.0)
        selected_contamination = fmt(hidden_bad_count / selected if selected else 0.0)
        if total_pos:
            hidden_positive_recall = fmt(hidden_pos / total_pos)
        if total_bad:
            hidden_bad_admission = fmt(hidden_bad_count / total_bad)
        if total_pos and total_bad:
            coverage_proxy_score = fmt(selected / (total_pos + total_bad))
        if hidden_positive_recall != "" and hidden_bad_admission != "":
            audit_oracle_score = fmt(float(hidden_positive_recall) - float(hidden_bad_admission))

    successes = as_int(endpoint_successes) if endpoint_successes not in ("", None) else ""
    episodes = as_int(endpoint_episodes) if endpoint_episodes not in ("", None) else ""
    candidate_family = method_family(candidate_id)
    rows.append(
        {
            "setting_id": setting_id,
            "setting_label": setting_label,
            "row_role": row_role,
            "candidate_id": candidate_id,
            "candidate_label": candidate_label or display_candidate(candidate_id),
            "candidate_family": candidate_family,
            "candidate_family_label": FAMILY_LABELS[candidate_family],
            "support_split_count": support_splits,
            "endpoint_split_count": endpoint_splits,
            "selected_unlabeled": selected,
            "hidden_positive_selected": hidden_pos,
            "hidden_bad_selected": hidden_bad_count,
            "total_hidden_positive_in_audited_splits": total_pos,
            "total_hidden_bad_in_audited_splits": total_bad,
            "support_purity": purity,
            "hidden_positive_recall": hidden_positive_recall,
            "hidden_bad_admission": hidden_bad_admission,
            "selected_contamination": selected_contamination,
            "coverage_proxy_score": coverage_proxy_score,
            "audit_oracle_score": audit_oracle_score,
            "endpoint_successes": successes,
            "endpoint_episodes": episodes,
            "endpoint_success_rate": rate(successes, episodes),
            "endpoint_status": endpoint_status(endpoint_splits, episodes),
            "source": source,
            "notes": notes,
        }
    )


def add_can40(rows: list[dict[str, object]]) -> None:
    for row in read_csv(CAN40_TRADEOFF):
        support_rule = row["support_rule"]
        splits = as_int(row["num_splits"])
        selected = as_int(float(row["mean_selected"]) * splits)
        add_candidate(
            rows,
            setting_id="can40",
            setting_label="Can 40p/80b",
            row_role="primary",
            candidate_id=support_rule,
            support_splits=splits,
            endpoint_splits=splits if row["endpoint_episodes"] else 0,
            selected_unlabeled=selected,
            hidden_positive=row["total_hidden_positive"],
            hidden_bad=row["total_hidden_bad"],
            total_hidden_positive=TASK_TOTALS_3SPLIT["Can 40p/80b"][0],
            total_hidden_bad=TASK_TOTALS_3SPLIT["Can 40p/80b"][1],
            endpoint_successes=row["endpoint_successes"],
            endpoint_episodes=row["endpoint_episodes"],
            source=str(CAN40_TRADEOFF),
        )


def add_can40_union(rows: list[dict[str, object]]) -> None:
    if not UNION_SUPPORT.exists() or not UNION_ENDPOINT.exists():
        return
    support_rows = {
        row["candidate_id"]: row
        for row in read_csv(UNION_SUPPORT)
        if row["setting_id"] == "can40"
    }
    endpoint_rows = {row["method_id"]: row for row in read_csv(UNION_ENDPOINT)}
    candidate_id = "positive_nn_risk_union_top40"
    support = support_rows.get(candidate_id)
    endpoint = endpoint_rows.get(candidate_id)
    if support is None or endpoint is None:
        return
    add_candidate(
        rows,
        setting_id="can40",
        setting_label="Can 40p/80b",
        row_role="primary",
        candidate_id=candidate_id,
        candidate_label="positive-NN/risk union top40",
        support_splits=as_int(support["split_count"]),
        endpoint_splits=as_int(endpoint["split_count"]),
        selected_unlabeled=support["selected_unlabeled"],
        hidden_positive=support["hidden_positive_selected"],
        hidden_bad=support["hidden_bad_selected"],
        total_hidden_positive=support["total_hidden_positive"],
        total_hidden_bad=support["total_hidden_bad"],
        endpoint_successes=endpoint["success_count"],
        endpoint_episodes=endpoint["eval_episodes"],
        source=f"{UNION_SUPPORT}; {UNION_ENDPOINT}",
        notes="v0.2 development union candidate; not frozen cross-task method",
    )


def add_can20(rows: list[dict[str, object]]) -> None:
    for row in read_csv(CAN20_AUDIT):
        support_rule = row["support_rule"]
        splits = as_int(row["num_splits"])
        selected = as_int(float(row["mean_selected_unlabeled"]) * splits)
        endpoint_splits = as_int(row["endpoint_num_splits"]) if row["endpoint_num_splits"] else 0
        add_candidate(
            rows,
            setting_id="can20",
            setting_label="Can 20p/80b",
            row_role="diagnostic",
            candidate_id=support_rule,
            support_splits=splits,
            endpoint_splits=endpoint_splits,
            selected_unlabeled=selected,
            hidden_positive=row["total_hidden_positive"],
            hidden_bad=row["total_hidden_bad"],
            total_hidden_positive=TASK_TOTALS_3SPLIT["Can 20p/80b"][0],
            total_hidden_bad=TASK_TOTALS_3SPLIT["Can 20p/80b"][1],
            endpoint_successes=row["endpoint_successes"],
            endpoint_episodes=row["endpoint_episodes"],
            source=str(CAN20_AUDIT),
        )


def add_can80(rows: list[dict[str, object]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(CAN80_AUDIT):
        grouped[row["method"]].append(row)

    method_ids = {
        "triage_bc_adaptive_masscap": "triage_bc_adaptive_masscap",
        "positive_only_nn_top80": "positive_only_nn_top80",
        "classifier_score_top80": "classifier_score_top80",
    }
    for method, method_rows in grouped.items():
        endpoint_rows = [row for row in method_rows if row["eval_episodes"]]
        successes = sum(as_int(row["endpoint_successes"]) for row in endpoint_rows)
        episodes = sum(as_int(row["eval_episodes"]) for row in endpoint_rows)
        add_candidate(
            rows,
            setting_id="can80",
            setting_label="Can 80p/80b",
            row_role="diagnostic",
            candidate_id=method_ids.get(method, method),
            support_splits=len(method_rows),
            endpoint_splits=len(endpoint_rows),
            selected_unlabeled=sum(as_int(row["selected_unlabeled"]) for row in method_rows),
            hidden_positive=sum(as_int(row["hidden_positive"]) for row in method_rows),
            hidden_bad=sum(as_int(row["hidden_bad"]) for row in method_rows),
            total_hidden_positive=TASK_TOTALS_3SPLIT["Can 80p/80b"][0],
            total_hidden_bad=TASK_TOTALS_3SPLIT["Can 80p/80b"][1],
            endpoint_successes=successes if endpoint_rows else "",
            endpoint_episodes=episodes if endpoint_rows else "",
            source=str(CAN80_AUDIT),
        )


def add_endpoint_master_rows(rows: list[dict[str, object]]) -> None:
    for row in read_csv(ENDPOINT_MASTER):
        task_label = row["task_label"]
        method = row["method"]
        include = (
            task_label == "Lift MG"
            or (task_label == "Can 40p/80b" and method in {"all_train_positive_oracle", "bc_all_mixed"})
            or (task_label == "Can 80p/80b" and method == "weighted_bc")
        )
        if not include:
            continue
        support_splits = as_int(row["support_split_count"])
        if method in {"all_train_positive_oracle", "bc_all_mixed"}:
            total_pos = ""
            total_bad = ""
            hidden_pos = ""
            hidden_bad = ""
            selected = ""
            notes = "support audit not comparable for oracle/all-demo training row"
        else:
            total_3split = TASK_TOTALS_3SPLIT[task_label]
            total_pos = as_int(total_3split[0] * support_splits / 3)
            total_bad = as_int(total_3split[1] * support_splits / 3)
            hidden_pos = row["support_hidden_positive"]
            hidden_bad = row["support_hidden_bad"]
            selected = row["support_selected_unlabeled"]
            notes = ""
        setting_id = {
            "Can 40p/80b": "can40",
            "Can 80p/80b": "can80",
            "Lift MG": "lift_mg",
        }[task_label]
        add_candidate(
            rows,
            setting_id=setting_id,
            setting_label=task_label,
            row_role=row["row_role"],
            candidate_id=method,
            candidate_label=row["method_label"],
            support_splits=support_splits,
            endpoint_splits=as_int(row["endpoint_split_count"]),
            selected_unlabeled=selected,
            hidden_positive=hidden_pos,
            hidden_bad=hidden_bad,
            total_hidden_positive=total_pos,
            total_hidden_bad=total_bad,
            endpoint_successes=row["endpoint_successes"],
            endpoint_episodes=row["endpoint_episodes"],
            source=str(ENDPOINT_MASTER),
            notes=notes,
        )


def endpoint_value(row: dict[str, object]) -> float:
    value = as_float(row["endpoint_success_rate"])
    return value if value is not None else -1.0


def proxy_value(row: dict[str, object], key: str) -> float:
    value = as_float(row[key])
    return value if value is not None else -1.0


def best(rows: list[dict[str, object]], key: str) -> dict[str, object] | None:
    valid = [row for row in rows if row[key] not in ("", None)]
    if not valid:
        return None
    if key == "endpoint_success_rate":
        return max(valid, key=endpoint_value)
    return max(valid, key=lambda row: proxy_value(row, key))


def method_endpoint(row: dict[str, object] | None) -> str:
    if row is None or row["endpoint_success_rate"] == "":
        return ""
    return f"{row['endpoint_successes']}/{row['endpoint_episodes']} ({row['endpoint_success_rate']})"


def make_decision_rows(audit_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_setting: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in audit_rows:
        by_setting[row["setting_id"]].append(row)

    decision_rows: list[dict[str, object]] = []
    for setting_id, rows in sorted(by_setting.items(), key=lambda item: SETTING_ORDER[item[0]]):
        endpoint_candidates = [
            row for row in rows
            if row["endpoint_success_rate"] != ""
            and row["candidate_family"] not in {"diagnostic_oracle", "mixed_baseline"}
        ]
        baseline_candidates = [
            row for row in endpoint_candidates
            if row["candidate_family"] in {"positive_only", "soft_weighted"}
        ]
        bad_aware_candidates = [
            row for row in endpoint_candidates
            if row["candidate_family"] in {"bad_aware_hard", "union_hybrid"}
        ]
        oracle_candidates = [
            row for row in rows
            if row["candidate_family"] == "diagnostic_oracle" and row["endpoint_success_rate"] != ""
        ]
        endpoint_oracle = best(endpoint_candidates, "endpoint_success_rate")
        strongest_baseline = best(baseline_candidates, "endpoint_success_rate")
        bad_aware = best(bad_aware_candidates, "endpoint_success_rate")
        all_positive = best(oracle_candidates, "endpoint_success_rate")
        coverage_proxy = best(endpoint_candidates, "coverage_proxy_score")
        audit_proxy = best(rows, "audit_oracle_score")
        baseline_rate = as_float(strongest_baseline["endpoint_success_rate"]) if strongest_baseline else None
        bad_rate = as_float(bad_aware["endpoint_success_rate"]) if bad_aware else None
        bad_gap = "" if baseline_rate is None or bad_rate is None else fmt(bad_rate - baseline_rate)
        if not endpoint_candidates:
            decision = "support-only; do not use as endpoint evidence"
        elif endpoint_oracle and strongest_baseline and endpoint_oracle["candidate_id"] == strongest_baseline["candidate_id"]:
            decision = "portfolio can only match the strongest baseline by selecting that baseline"
        elif endpoint_oracle and strongest_baseline and endpoint_value(endpoint_oracle) > endpoint_value(strongest_baseline):
            decision = "portfolio contains an endpoint branch above the strongest baseline"
        else:
            decision = "portfolio endpoint evidence is incomplete or below strongest baseline"
        endpoint_statuses = sorted({str(row["endpoint_status"]) for row in rows})
        decision_rows.append(
            {
                "setting_id": setting_id,
                "setting_label": rows[0]["setting_label"],
                "row_role": rows[0]["row_role"],
                "endpoint_evidence_status": "/".join(endpoint_statuses),
                "endpoint_oracle_candidate": endpoint_oracle["candidate_label"] if endpoint_oracle else "",
                "endpoint_oracle_endpoint": method_endpoint(endpoint_oracle),
                "strongest_baseline_candidate": strongest_baseline["candidate_label"] if strongest_baseline else "",
                "strongest_baseline_endpoint": method_endpoint(strongest_baseline),
                "best_bad_aware_candidate": bad_aware["candidate_label"] if bad_aware else "",
                "best_bad_aware_endpoint": method_endpoint(bad_aware),
                "bad_aware_gap_vs_strongest_baseline": bad_gap,
                "all_positive_oracle_endpoint": method_endpoint(all_positive),
                "coverage_proxy_winner": coverage_proxy["candidate_label"] if coverage_proxy else "",
                "coverage_proxy_winner_endpoint": method_endpoint(coverage_proxy),
                "audit_oracle_winner": audit_proxy["candidate_label"] if audit_proxy else "",
                "audit_oracle_winner_endpoint": method_endpoint(audit_proxy),
                "decision": decision,
            }
        )
    return decision_rows


def can_mg_summary() -> dict[str, object]:
    rows = read_csv(CAN_MG_PROXY)
    by_split: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_split[row["split"]].append(row)
    parts = {}
    for split, split_rows in sorted(by_split.items()):
        matches = sum(row["proxy_matches_best_success"] == "true" for row in split_rows)
        total = len(split_rows)
        best_method = split_rows[0]["rollout_best_method"]
        best_success = split_rows[0]["rollout_best_20k"]
        winners = sorted({row["proxy_winner"] for row in split_rows})
        parts[split] = {
            "matches": matches,
            "total": total,
            "best_method": best_method,
            "best_success": best_success,
            "proxy_winners": "/".join(winners),
        }
    return parts


def markdown_report(
    audit_rows: list[dict[str, object]],
    decision_rows: list[dict[str, object]],
) -> str:
    lines: list[str] = []
    lines.append("# Candidate Family Oracle/Proxy Audit")
    lines.append("")
    lines.append("Generated from staged final-paper endpoint, support, and proxy artifacts.")
    lines.append("Hidden labels are audit-only; endpoint-oracle and audit-oracle rows are diagnostics, not deployable selection rules.")
    lines.append("")
    lines.append("## Decision Summary")
    lines.append("")
    lines.append("| setting | endpoint oracle | strongest baseline | best bad-aware | bad-aware gap | coverage proxy winner | audit-support winner | decision |")
    lines.append("|---|---|---|---|---:|---|---|---|")
    for row in decision_rows:
        lines.append(
            f"| {row['setting_label']} | {row['endpoint_oracle_candidate']} {row['endpoint_oracle_endpoint']} | "
            f"{row['strongest_baseline_candidate']} {row['strongest_baseline_endpoint']} | "
            f"{row['best_bad_aware_candidate']} {row['best_bad_aware_endpoint']} | "
            f"{row['bad_aware_gap_vs_strongest_baseline']} | "
            f"{row['coverage_proxy_winner']} {row['coverage_proxy_winner_endpoint']} | "
            f"{row['audit_oracle_winner']} {row['audit_oracle_winner_endpoint']} | "
            f"{row['decision']} |"
        )
    lines.append("")
    lines.append("## Primary Candidate Audit")
    lines.append("")
    primary = [
        row for row in audit_rows
        if row["setting_id"] in {"can40", "lift_mg"}
        and row["candidate_family"] != "mixed_baseline"
    ]
    primary = sorted(primary, key=lambda row: (SETTING_ORDER[row["setting_id"]], row["candidate_family"], row["candidate_label"]))
    lines.append("| setting | candidate | family | recall | bad admission | support purity | coverage proxy | audit score | endpoint |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|")
    for row in primary:
        endpoint = method_endpoint(row)
        lines.append(
            f"| {row['setting_label']} | {row['candidate_label']} | {row['candidate_family_label']} | "
            f"{row['hidden_positive_recall']} | {row['hidden_bad_admission']} | {row['support_purity']} | "
            f"{row['coverage_proxy_score']} | {row['audit_oracle_score']} | {endpoint} |"
        )
    lines.append("")
    lines.append("## Can MG Proxy Stress")
    lines.append("")
    mg = can_mg_summary()
    lines.append("| split | rollout-best branch | proxy winners | proxy-best matches |")
    lines.append("|---|---|---|---:|")
    for split, item in mg.items():
        lines.append(
            f"| {split} | {item['best_method']} ({float(item['best_success']):.3f}) | "
            f"{item['proxy_winners']} | {item['matches']}/{item['total']} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- The new Can 40p/80b union branch is the first endpoint-evaluated bad-aware candidate in this audit that exceeds the strongest positive-only/weighted baseline.")
    lines.append("- This does not solve v0.2 by itself: Lift MG is still won by the weighted branch, and Can MG remains an abstention/stress case.")
    lines.append("- The all-positive oracle remains well above non-oracle methods on Can 40p/80b and Lift MG, so there is backbone/headroom, but the current support-conversion family does not capture it.")
    lines.append("- Coverage-only selection picks broad weighted support, which explains Lift MG but fails Can-style contamination even after adding the union branch; audit-only precision/coverage scores are not deployable.")
    lines.append("- Can MG confirms that simple positive/negative likelihood proxies can pick the wrong branch or miss that all branches are weak.")
    lines.append("")
    lines.append("## v0.2 Gate")
    lines.append("")
    lines.append("- Do not promote the union branch as TRIAGE-BC v0.2 until a hidden-label-free selector is frozen and validated on fresh cross-task splits.")
    lines.append("- The next cheap v0.2 step is a portfolio-router audit: choose union-style hard support for low-mass Can-like contamination, weighted support for Lift-like coverage, and abstention for ambiguous Can MG-style pools.")
    lines.append("- Fresh GPU endpoint budget should be reserved for a frozen rule that has this complete cross-task story, not for more post-hoc Can-only tuning.")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- `{AUDIT_OUT}`")
    lines.append(f"- `{DECISION_OUT}`")
    lines.append(f"- `{REPORT_OUT}`")
    lines.append("")
    lines.append(f"Candidate rows audited: `{len(audit_rows)}`.")
    return "\n".join(lines) + "\n"


def main() -> None:
    audit_rows: list[dict[str, object]] = []
    add_can40(audit_rows)
    add_can40_union(audit_rows)
    add_can20(audit_rows)
    add_can80(audit_rows)
    add_endpoint_master_rows(audit_rows)
    audit_rows.sort(key=lambda row: (SETTING_ORDER[row["setting_id"]], row["candidate_family"], row["candidate_label"]))
    decision_rows = make_decision_rows(audit_rows)

    audit_fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "candidate_id",
        "candidate_label",
        "candidate_family",
        "candidate_family_label",
        "support_split_count",
        "endpoint_split_count",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive_in_audited_splits",
        "total_hidden_bad_in_audited_splits",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "coverage_proxy_score",
        "audit_oracle_score",
        "endpoint_successes",
        "endpoint_episodes",
        "endpoint_success_rate",
        "endpoint_status",
        "source",
        "notes",
    ]
    decision_fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "endpoint_evidence_status",
        "endpoint_oracle_candidate",
        "endpoint_oracle_endpoint",
        "strongest_baseline_candidate",
        "strongest_baseline_endpoint",
        "best_bad_aware_candidate",
        "best_bad_aware_endpoint",
        "bad_aware_gap_vs_strongest_baseline",
        "all_positive_oracle_endpoint",
        "coverage_proxy_winner",
        "coverage_proxy_winner_endpoint",
        "audit_oracle_winner",
        "audit_oracle_winner_endpoint",
        "decision",
    ]
    write_csv(AUDIT_OUT, audit_rows, audit_fields)
    write_csv(DECISION_OUT, decision_rows, decision_fields)
    REPORT_OUT.write_text(markdown_report(audit_rows, decision_rows), encoding="utf-8")
    print(f"wrote {AUDIT_OUT}")
    print(f"wrote {DECISION_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
