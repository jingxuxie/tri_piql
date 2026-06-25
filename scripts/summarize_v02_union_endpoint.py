from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(".")
DEFAULT_ROOT = ROOT / "results" / "final_paper" / "ablations" / "v02_union_endpoint_200ep_can40" / "split22"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--eval-subdir", default="eval_50ep")
    parser.add_argument("--summary-name", default="endpoint_200ep_summary.csv")
    parser.add_argument("--per-initial-name", default="endpoint_200ep_per_initial.csv")
    parser.add_argument("--report-name", default="REPORT.md")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def success_count(success_rate: str, eval_episodes: str) -> int:
    return int(round(float(success_rate) * int(float(eval_episodes))))


def candidate_metrics(root: Path, eval_subdir: str) -> list[dict[str, object]]:
    setup_rows = {row["candidate_tag"]: row for row in read_csv(root / "endpoint_setup_summary.csv")}
    rows = []
    for tag, setup in setup_rows.items():
        metrics_path = root / tag / eval_subdir / "metrics.csv"
        if not metrics_path.exists():
            continue
        metrics = read_csv(metrics_path)[0]
        diagnostics = json.loads((root / tag / "setup" / "diagnostics.json").read_text(encoding="utf-8"))
        eval_episodes = int(float(metrics["eval_episodes"]))
        endpoint_success = float(metrics["success_rate"])
        train_positive = int(setup["selected_hidden_positive"]) + len(
            json.loads(Path(diagnostics["split_path"]).read_text(encoding="utf-8"))["labeled_positive_ids"]
        )
        train_bad = int(setup["selected_hidden_bad"])
        rows.append(
            {
                "split_seed": setup["split_seed"],
                "method_id": setup["candidate_id"],
                "method_role": "union_candidate",
                "endpoint_success": endpoint_success,
                "success_count": int(round(endpoint_success * eval_episodes)),
                "eval_episodes": eval_episodes,
                "train_demo_count": setup["train_demo_count"],
                "train_positive_count": train_positive,
                "train_bad_count": train_bad,
                "selected_unlabeled": setup["selected_unlabeled"],
                "selected_hidden_positive": setup["selected_hidden_positive"],
                "selected_hidden_bad": setup["selected_hidden_bad"],
                "support_purity": setup["support_purity"],
                "hidden_positive_recall": setup["hidden_positive_recall"],
                "hidden_bad_admission": setup["hidden_bad_admission"],
                "checkpoint": metrics["checkpoint"],
                "metrics_path": str(metrics_path),
                "episode_metrics_path": str(root / tag / eval_subdir / "episode_metrics.csv"),
            }
        )
    return rows


def infer_train_counts(diagnostics_path: Path) -> tuple[int, int, int]:
    diagnostics = json.loads(diagnostics_path.read_text(encoding="utf-8"))
    split = json.loads(Path(diagnostics["split_path"]).read_text(encoding="utf-8"))
    positives = set(split["all_positive_ids"])
    train_ids = diagnostics["train_demo_ids"]
    train_positive = sum(demo_id in positives for demo_id in train_ids)
    train_bad = len(train_ids) - train_positive
    return len(train_ids), train_positive, train_bad


def baseline_specs(split_seed: str) -> list[tuple[str, str, Path, Path]]:
    per_seed = ROOT / "results" / "final_paper" / "per_seed"
    specs = [
        (
            "all_train_positive_oracle",
            "oracle_control",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_all_train_positive_oracle_policy0",
            per_seed
            / f"can_paired_pos40_bad80_split{split_seed}_all_train_positive_oracle_policy0"
            / "setup"
            / "diagnostics.json",
        ),
        (
            "positive_only_nn",
            "strong_baseline",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_positive_only_nn_policy0",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_positive_only_nn_policy0" / "setup" / "diagnostics.json",
        ),
        (
            "triage_bc",
            "v01_method",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_triage_bc_policy0",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_triage_bc_policy0" / "setup" / "diagnostics.json",
        ),
        (
            "weighted_bc",
            "strong_baseline",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_weighted_bc_policy0",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_weighted_bc_policy0" / "setup" / "diagnostics.json",
        ),
        (
            "bc_all_mixed",
            "mixed_log_baseline",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_bc_all_mixed_policy0",
            per_seed / f"can_paired_pos40_bad80_split{split_seed}_bc_all_mixed_policy0" / "setup" / "diagnostics.json",
        ),
    ]
    risk_root = ROOT / "results" / "final_paper" / "ablations" / "v02_action_risk_endpoint_200ep_can40" / f"split{split_seed}" / "pnrf40"
    if (risk_root / "eval" / "metrics.csv").exists():
        specs.append(
            (
                "positive_nn_risk_fusion_top40",
                "failed_v02_gate",
                risk_root,
                risk_root / "setup" / "diagnostics.json",
            )
        )
    return specs


def baseline_rows(split_seed: str) -> list[dict[str, object]]:
    rows = []
    for method_id, role, result_root, diagnostics_path in baseline_specs(split_seed):
        eval_dir = "eval" if (result_root / "eval" / "metrics.csv").exists() else "eval_50ep"
        metrics_path = result_root / eval_dir / "metrics.csv"
        if not metrics_path.exists() or not diagnostics_path.exists():
            continue
        metric = read_csv(metrics_path)[0]
        eval_episodes = int(float(metric["eval_episodes"]))
        endpoint_success = float(metric["success_rate"])
        train_demo_count, train_positive_count, train_bad_count = infer_train_counts(diagnostics_path)
        rows.append(
            {
                "split_seed": split_seed,
                "method_id": method_id,
                "method_role": role,
                "endpoint_success": endpoint_success,
                "success_count": int(round(endpoint_success * eval_episodes)),
                "eval_episodes": eval_episodes,
                "train_demo_count": train_demo_count,
                "train_positive_count": train_positive_count,
                "train_bad_count": train_bad_count,
                "selected_unlabeled": "",
                "selected_hidden_positive": "",
                "selected_hidden_bad": "",
                "support_purity": "",
                "hidden_positive_recall": "",
                "hidden_bad_admission": "",
                "checkpoint": metric["checkpoint"],
                "metrics_path": str(metrics_path),
                "episode_metrics_path": str(result_root / eval_dir / "episode_metrics.csv"),
            }
        )
    return rows


def per_initial(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    selected_methods = {"positive_nn_risk_union_top40", "positive_only_nn", "positive_nn_risk_fusion_top40"}
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    present_methods = {str(row["method_id"]) for row in rows}
    for row in rows:
        method_id = str(row["method_id"])
        if method_id not in selected_methods or not row["episode_metrics_path"]:
            continue
        path = Path(str(row["episode_metrics_path"]))
        if not path.exists():
            continue
        for episode in read_csv(path):
            grouped[(method_id, episode["initial_demo_id"])].append(float(episode["success"]))

    initial_ids = sorted({initial for _method, initial in grouped})
    out = []
    for initial_id in initial_ids:
        union_values = grouped[("positive_nn_risk_union_top40", initial_id)]
        positive_values = grouped[("positive_only_nn", initial_id)]
        risk_values = grouped[("positive_nn_risk_fusion_top40", initial_id)]
        if not union_values or not positive_values:
            continue
        union = sum(union_values) / len(union_values)
        positive = sum(positive_values) / len(positive_values)
        risk = sum(risk_values) / len(risk_values) if "positive_nn_risk_fusion_top40" in present_methods and risk_values else None
        out.append(
            {
                "initial_demo_id": initial_id,
                "union_success": f"{union:.3f}",
                "positive_only_success": f"{positive:.3f}",
                "risk_fusion_success": f"{risk:.3f}" if risk is not None else "",
                "union_minus_positive_only": f"{union - positive:.3f}",
                "union_minus_risk_fusion": f"{union - risk:.3f}" if risk is not None else "",
            }
        )
    return out


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def report(root: Path, rows: list[dict[str, object]], per_initial_rows: list[dict[str, object]]) -> str:
    by_method = {str(row["method_id"]): row for row in rows}
    union = by_method["positive_nn_risk_union_top40"]
    positive = by_method["positive_only_nn"]
    risk = by_method.get("positive_nn_risk_fusion_top40")
    best_baseline = max(
        [
            row
            for row in rows
            if row["method_role"] != "oracle_control"
            and row["method_id"] != "positive_nn_risk_union_top40"
        ],
        key=lambda row: float(row["endpoint_success"]),
    )
    delta_positive = float(union["endpoint_success"]) - float(positive["endpoint_success"])
    delta_best = float(union["endpoint_success"]) - float(best_baseline["endpoint_success"])
    delta_risk = (
        float(union["endpoint_success"]) - float(risk["endpoint_success"])
        if risk is not None
        else None
    )
    mean_initial_delta = (
        sum(float(row["union_minus_positive_only"]) for row in per_initial_rows) / len(per_initial_rows)
        if per_initial_rows
        else 0.0
    )
    lines = [
        "# v0.2 Union Candidate Endpoint Gate",
        "",
        "This is a single-split endpoint gate for a union candidate that keeps positive-only NN support and adds risk-fusion demos.",
        "It is not a frozen v0.2 result; it decides whether the union family deserves more endpoint budget.",
        "",
        "## Endpoint Summary",
        "",
        *markdown_table(
            rows,
            [
                "method_id",
                "method_role",
                "endpoint_success",
                "success_count",
                "eval_episodes",
                "train_positive_count",
                "train_bad_count",
            ],
        ),
        "",
        "## Read",
        "",
        (
            f"- Union reaches `{float(union['endpoint_success']):.3f}` "
            f"({union['success_count']}/{union['eval_episodes']}) on split {union['split_seed']}."
        ),
        (
            f"- This is `{delta_positive:+.3f}` versus positive-only NN "
            f"({positive['endpoint_success']}) and `{delta_best:+.3f}` versus the best existing non-oracle row "
            f"({best_baseline['method_id']} at {best_baseline['endpoint_success']})."
        ),
        (
            f"- Versus risk fusion, the delta is `{delta_risk:+.3f}`."
            if delta_risk is not None
            else "- No risk-fusion endpoint row is available for this split."
        ),
        (
            f"- Per-initial mean delta versus positive-only is `{mean_initial_delta:+.3f}` over "
            f"{len(per_initial_rows)} validation starts."
        ),
        (
            "- Interpretation: positive split gate, but this still needs aggregate and cross-task validation."
            if delta_best > 0.0
            else "- Interpretation: negative split gate against the strongest existing non-oracle baseline."
        ),
        "- Next gate: aggregate all completed Can 40p/80b union split checks before spending additional GPU budget.",
        "",
        "## Outputs",
        "",
        f"- `{root / 'endpoint_200ep_summary.csv'}`",
        f"- `{root / 'endpoint_200ep_per_initial.csv'}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    split_seed = args.root.name.removeprefix("split")
    rows = candidate_metrics(args.root, args.eval_subdir)
    rows.extend(baseline_rows(split_seed))
    rows.sort(key=lambda row: float(row["endpoint_success"]), reverse=True)
    per_initial_rows = per_initial(rows)

    summary_fields = [
        "split_seed",
        "method_id",
        "method_role",
        "endpoint_success",
        "success_count",
        "eval_episodes",
        "train_demo_count",
        "train_positive_count",
        "train_bad_count",
        "selected_unlabeled",
        "selected_hidden_positive",
        "selected_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "checkpoint",
        "metrics_path",
        "episode_metrics_path",
    ]
    per_initial_fields = [
        "initial_demo_id",
        "union_success",
        "positive_only_success",
        "risk_fusion_success",
        "union_minus_positive_only",
        "union_minus_risk_fusion",
    ]
    write_csv(args.root / args.summary_name, rows, summary_fields)
    write_csv(args.root / args.per_initial_name, per_initial_rows, per_initial_fields)
    (args.root / args.report_name).write_text(report(args.root, rows, per_initial_rows), encoding="utf-8")
    print(f"wrote {args.root / args.summary_name}")
    print(f"wrote {args.root / args.per_initial_name}")
    print(f"wrote {args.root / args.report_name}")


if __name__ == "__main__":
    main()
