from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(".")
PER_SEED = ROOT / "results" / "final_paper" / "per_seed"
OUT_DIR = ROOT / "results" / "final_paper" / "tables"

ENDPOINT_OUT = OUT_DIR / "endpoint_master_table.csv"
SUPPORT_OUT = OUT_DIR / "support_master_table.csv"
REPORT_OUT = OUT_DIR / "baseline_strength_REPORT.md"

PRIMARY_TASKS = {
    ("can_paired", "pos40_bad80"),
    ("lift_mg", "mg_sparse"),
}

TASK_LABELS = {
    ("can_paired", "pos40_bad80"): "Can 40p/80b",
    ("can_paired", "pos20_bad80"): "Can 20p/80b",
    ("can_paired", "balanced_80p80b"): "Can 80p/80b",
    ("lift_mg", "mg_sparse"): "Lift MG",
}

METHOD_LABELS = {
    "all_train_positive_oracle": "all-positive oracle",
    "bc_all_mixed": "all-demo BC",
    "classifier_topk": "classifier top-k",
    "positive_only_nn": "positive-only NN",
    "triage_bc": "TRIAGE-BC",
    "weighted_bc": "weighted BC",
}

ORACLE_METHODS = {"all_train_positive_oracle"}
PRIMARY_EXPECTED_METHODS = {
    ("can_paired", "pos40_bad80"): [
        "all_train_positive_oracle",
        "bc_all_mixed",
        "positive_only_nn",
        "triage_bc",
        "weighted_bc",
    ],
    ("lift_mg", "mg_sparse"): [
        "all_train_positive_oracle",
        "bc_all_mixed",
        "positive_only_nn",
        "triage_bc",
        "weighted_bc",
    ],
}
DIAGNOSTIC_EXPECTED_METHODS = {
    ("can_paired", "pos20_bad80"): [
        "classifier_topk",
        "positive_only_nn",
        "triage_bc",
        "weighted_bc",
    ],
    ("can_paired", "balanced_80p80b"): [
        "classifier_topk",
        "positive_only_nn",
        "triage_bc",
        "weighted_bc",
    ],
    ("lift_mg", "mg_sparse"): ["classifier_topk"],
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


def fmt_float(value: object, digits: int = 3) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.{digits}f}"


def as_int(value: object) -> int:
    return int(float(value))


def evidence_status(task: str, split_type: str, method: str, has_endpoint: bool) -> str:
    key = (task, split_type)
    if method in ORACLE_METHODS:
        return "diagnostic_oracle_endpoint" if has_endpoint else "diagnostic_oracle_support_only"
    if key in PRIMARY_TASKS:
        return "primary_endpoint" if has_endpoint else "primary_support_only"
    return "diagnostic_endpoint" if has_endpoint else "diagnostic_support_only"


def load_eval(run_dir: Path) -> dict[str, object]:
    metric_candidates = [
        run_dir / "eval" / "metrics.csv",
        run_dir / "eval_endpoint_200" / "metrics.csv",
    ]
    metrics_path = next((path for path in metric_candidates if path.exists()), None)
    if metrics_path is None:
        return {
            "eval_status": "missing_eval_metrics",
            "successes": "",
            "episodes": "",
            "success_rate": "",
            "avg_return": "",
            "avg_len": "",
            "endpoint_checkpoint": "",
            "eval_metrics_path": "",
        }
    rows = read_csv(metrics_path)
    if len(rows) != 1:
        raise ValueError(f"expected one row in {metrics_path}, got {len(rows)}")
    row = rows[0]
    episodes = as_int(row["eval_episodes"])
    success_rate = float(row["success_rate"])
    successes = round(success_rate * episodes)
    return {
        "eval_status": "endpoint_evaluated",
        "successes": successes,
        "episodes": episodes,
        "success_rate": fmt_float(success_rate),
        "avg_return": fmt_float(row["avg_return"]),
        "avg_len": fmt_float(row["avg_len"]),
        "endpoint_checkpoint": row.get("checkpoint_name", ""),
        "eval_metrics_path": str(metrics_path),
    }


def row_from_manifest(manifest_path: Path) -> dict[str, object]:
    run_dir = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    hidden_path = run_dir / "hidden_label_audit.csv"
    if not hidden_path.exists():
        raise FileNotFoundError(hidden_path)
    hidden = read_csv(hidden_path)[0]
    task = manifest["task"]
    split_type = manifest["split_type"]
    method = manifest["method"]
    eval_info = load_eval(run_dir)
    has_endpoint = eval_info["eval_status"] == "endpoint_evaluated"
    selected = as_int(hidden["selected_unlabeled"])
    hidden_positive = as_int(hidden["hidden_positive"])
    hidden_bad = as_int(hidden["hidden_bad"])
    train_demo_count = as_int(hidden["train_demo_count"])
    purity = float(hidden["purity"]) if selected else 0.0
    total_hidden_positive = hidden_positive
    total_hidden_bad = hidden_bad
    split_seed = as_int(manifest["split_seed"])
    policy_seed = as_int(manifest["policy_seed"])
    router = manifest.get("router_decision") or {}
    return {
        "task": task,
        "task_label": TASK_LABELS.get((task, split_type), f"{task}/{split_type}"),
        "split_type": split_type,
        "split_seed": split_seed,
        "policy_seed": policy_seed,
        "method": method,
        "method_label": METHOD_LABELS.get(method, method),
        "evidence_status": evidence_status(task, split_type, method, has_endpoint),
        "row_role": "oracle" if method in ORACLE_METHODS else ("primary" if (task, split_type) in PRIMARY_TASKS else "diagnostic"),
        "eval_status": eval_info["eval_status"],
        "successes": eval_info["successes"],
        "episodes": eval_info["episodes"],
        "success_rate": eval_info["success_rate"],
        "avg_return": eval_info["avg_return"],
        "avg_len": eval_info["avg_len"],
        "endpoint_checkpoint": eval_info["endpoint_checkpoint"],
        "selected_unlabeled_count": selected,
        "total_train_demos": train_demo_count,
        "hidden_positive_selected": hidden_positive,
        "hidden_bad_selected": hidden_bad,
        "support_purity": fmt_float(purity),
        "hidden_positive_recall": "",
        "hidden_bad_admission": "",
        "router_branch": router.get("router_v2_branch", ""),
        "router_reason": router.get("reason", ""),
        "estimated_positive_mass": fmt_float(router.get("estimated_positive_mass", "")),
        "count_ge_pos_min": router.get("count_ge_pos_min", ""),
        "manifest_path": str(manifest_path),
        "support_audit_path": str(run_dir / "support_audit.csv"),
        "hidden_label_audit_path": str(hidden_path),
        "eval_metrics_path": eval_info["eval_metrics_path"],
        "notes": "",
    }


def summarize_group(rows: list[dict[str, object]]) -> dict[str, object]:
    endpoint_rows = [row for row in rows if row["eval_status"] == "endpoint_evaluated"]
    support_rows = rows
    successes = sum(as_int(row["successes"]) for row in endpoint_rows)
    episodes = sum(as_int(row["episodes"]) for row in endpoint_rows)
    selected = sum(as_int(row["selected_unlabeled_count"]) for row in support_rows)
    hidden_pos = sum(as_int(row["hidden_positive_selected"]) for row in support_rows)
    hidden_bad = sum(as_int(row["hidden_bad_selected"]) for row in support_rows)
    train_demos = sum(as_int(row["total_train_demos"]) for row in support_rows)
    purity = hidden_pos / selected if selected else 0.0
    split_seeds = sorted({as_int(row["split_seed"]) for row in support_rows})
    endpoint_split_seeds = sorted({as_int(row["split_seed"]) for row in endpoint_rows})
    first = rows[0]
    return {
        "task": first["task"],
        "task_label": first["task_label"],
        "split_type": first["split_type"],
        "method": first["method"],
        "method_label": first["method_label"],
        "row_role": first["row_role"],
        "support_split_count": len(split_seeds),
        "endpoint_split_count": len(endpoint_split_seeds),
        "support_split_seeds": "/".join(str(seed) for seed in split_seeds),
        "endpoint_split_seeds": "/".join(str(seed) for seed in endpoint_split_seeds),
        "support_selected_unlabeled": selected,
        "support_train_demos": train_demos,
        "support_hidden_positive": hidden_pos,
        "support_hidden_bad": hidden_bad,
        "support_purity": fmt_float(purity),
        "endpoint_successes": successes if endpoint_rows else "",
        "endpoint_episodes": episodes if endpoint_rows else "",
        "endpoint_success_rate": fmt_float(successes / episodes) if episodes else "",
        "completion_status": "complete_3split_endpoint" if len(endpoint_split_seeds) == 3 else (
            "partial_endpoint" if endpoint_rows else "support_only"
        ),
    }


def expected_missing(summary_rows: list[dict[str, object]]) -> list[str]:
    present = {
        (row["task"], row["split_type"], row["method"]): row
        for row in summary_rows
    }
    messages: list[str] = []
    for expected_map, role in [
        (PRIMARY_EXPECTED_METHODS, "primary"),
        (DIAGNOSTIC_EXPECTED_METHODS, "diagnostic"),
    ]:
        for key, methods in expected_map.items():
            task_label = TASK_LABELS.get(key, f"{key[0]}/{key[1]}")
            for method in methods:
                row = present.get((*key, method))
                method_label = METHOD_LABELS.get(method, method)
                if row is None:
                    messages.append(f"{task_label} / {method_label}: missing {role} support row")
                    continue
                if row["completion_status"] != "complete_3split_endpoint":
                    messages.append(
                        f"{task_label} / {method_label}: {row['completion_status']} "
                        f"(endpoint splits {row['endpoint_split_seeds'] or 'none'}, support splits {row['support_split_seeds']})"
                    )
    return messages


def report_markdown(summary_rows: list[dict[str, object]], support_rows: list[dict[str, object]]) -> str:
    lines: list[str] = []
    lines.append("# Baseline Strength And Completeness Report")
    lines.append("")
    lines.append("Generated from final-paper per-seed manifests, support audits, hidden-label audits, and endpoint metrics.")
    lines.append("Hidden labels are audit-only; this report is for evidence accounting and v0.2 planning.")
    lines.append("")
    lines.append("## Primary Endpoint Ranking")
    lines.append("")
    primary = [
        row for row in summary_rows
        if (row["task"], row["split_type"]) in PRIMARY_TASKS and row["row_role"] != "oracle"
    ]
    primary = sorted(primary, key=lambda row: (row["task_label"], -float(row["endpoint_success_rate"] or 0.0)))
    lines.append("| task | method | endpoint | support | status |")
    lines.append("|---|---|---:|---|---|")
    for row in primary:
        endpoint = (
            f"{row['endpoint_successes']}/{row['endpoint_episodes']} ({row['endpoint_success_rate']})"
            if row["endpoint_episodes"] else ""
        )
        support = (
            f"{row['support_hidden_positive']} pos, {row['support_hidden_bad']} bad / "
            f"{row['support_selected_unlabeled']} selected (purity {row['support_purity']})"
        )
        lines.append(
            f"| {row['task_label']} | {row['method_label']} | {endpoint} | {support} | {row['completion_status']} |"
        )
    lines.append("")
    lines.append("Interpretation: the current v0.1 primary matrix does not yet clear the high-impact methods bar. "
                 "Can 40p/80b is led by positive-only NN, and Lift MG is led by weighted BC.")
    lines.append("")
    lines.append("## Diagnostic Endpoint Coverage")
    lines.append("")
    diagnostic = [
        row for row in summary_rows
        if row["row_role"] == "diagnostic"
    ]
    diagnostic = sorted(diagnostic, key=lambda row: (row["task_label"], row["method_label"]))
    lines.append("| task | method | endpoint splits | endpoint | support splits | status |")
    lines.append("|---|---|---|---:|---|---|")
    for row in diagnostic:
        endpoint = (
            f"{row['endpoint_successes']}/{row['endpoint_episodes']} ({row['endpoint_success_rate']})"
            if row["endpoint_episodes"] else ""
        )
        lines.append(
            f"| {row['task_label']} | {row['method_label']} | {row['endpoint_split_seeds'] or 'none'} | "
            f"{endpoint} | {row['support_split_seeds']} | {row['completion_status']} |"
        )
    lines.append("")
    lines.append("## Missing Or Incomplete Rows")
    lines.append("")
    missing = expected_missing(summary_rows)
    for message in missing:
        lines.append(f"- {message}")
    lines.append("")
    lines.append("## v0.2 Decision Gate")
    lines.append("")
    lines.append("- Current candidate family is not yet enough for a top-tier methods claim: v0.1 is not best non-oracle on either primary task.")
    lines.append("- Before GPU-heavy v0.2 final runs, the next useful cheap artifact is a candidate-family oracle/proxy audit using these master tables.")
    lines.append("- Can 20p/80b and Can 80p/80b should remain diagnostic unless their endpoint rows are completed across the same split/method grid.")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- `{ENDPOINT_OUT}`")
    lines.append(f"- `{SUPPORT_OUT}`")
    lines.append(f"- `{REPORT_OUT}`")
    lines.append("")
    lines.append(f"Support rows normalized: `{len(support_rows)}`.")
    endpoint_count = sum(1 for row in support_rows if row["eval_status"] == "endpoint_evaluated")
    lines.append(f"Endpoint rows with metrics: `{endpoint_count}`.")
    return "\n".join(lines) + "\n"


def main() -> None:
    support_rows = [row_from_manifest(path) for path in sorted(PER_SEED.glob("*/manifest.json"))]
    support_rows.sort(key=lambda row: (row["task_label"], row["split_type"], as_int(row["split_seed"]), row["method"]))

    grouped: dict[tuple[object, ...], list[dict[str, object]]] = defaultdict(list)
    for row in support_rows:
        grouped[(row["task"], row["split_type"], row["method"], row["policy_seed"])].append(row)
    endpoint_rows = [summarize_group(rows) for rows in grouped.values()]
    endpoint_rows.sort(key=lambda row: (row["task_label"], row["split_type"], row["method_label"]))

    support_fieldnames = [
        "task",
        "task_label",
        "split_type",
        "split_seed",
        "policy_seed",
        "method",
        "method_label",
        "evidence_status",
        "row_role",
        "eval_status",
        "successes",
        "episodes",
        "success_rate",
        "avg_return",
        "avg_len",
        "endpoint_checkpoint",
        "selected_unlabeled_count",
        "total_train_demos",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "router_branch",
        "router_reason",
        "estimated_positive_mass",
        "count_ge_pos_min",
        "manifest_path",
        "support_audit_path",
        "hidden_label_audit_path",
        "eval_metrics_path",
        "notes",
    ]
    endpoint_fieldnames = [
        "task",
        "task_label",
        "split_type",
        "method",
        "method_label",
        "row_role",
        "support_split_count",
        "endpoint_split_count",
        "support_split_seeds",
        "endpoint_split_seeds",
        "support_selected_unlabeled",
        "support_train_demos",
        "support_hidden_positive",
        "support_hidden_bad",
        "support_purity",
        "endpoint_successes",
        "endpoint_episodes",
        "endpoint_success_rate",
        "completion_status",
    ]
    write_csv(SUPPORT_OUT, support_rows, support_fieldnames)
    write_csv(ENDPOINT_OUT, endpoint_rows, endpoint_fieldnames)
    REPORT_OUT.write_text(report_markdown(endpoint_rows, support_rows), encoding="utf-8")
    print(f"wrote {SUPPORT_OUT}")
    print(f"wrote {ENDPOINT_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
