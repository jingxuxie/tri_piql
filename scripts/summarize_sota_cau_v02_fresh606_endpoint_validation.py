#!/usr/bin/env python3
"""Summarize fresh split-606 endpoint validation for the CAU+v0.2 hypothesis."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"
SPLIT_SEED = 606


METRIC_SOURCES = [
    {
        "method_id": "positive_only_nn",
        "method_role": "existing_baseline",
        "path": ROOT / "results/candidate_g_fresh_preflight/can606_positive_epoch200_eval20/metrics.csv",
    },
    {
        "method_id": "weighted_bc",
        "method_role": "existing_baseline",
        "path": ROOT / "results/candidate_g_fresh_preflight/can606_weighted_epoch200_eval20/metrics.csv",
    },
    {
        "method_id": "candidate_e_gate",
        "method_role": "existing_router",
        "path": ROOT / "results/candidate_g_fresh_preflight/can606_candidate_e_gate_eval20/metrics.csv",
    },
    {
        "method_id": "cau_action_conflict",
        "method_role": "posthoc_portfolio_selected_branch",
        "path": DEFAULT_OUT_DIR / "cau_action_conflict_can606_b005_m05_eval20/metrics.csv",
    },
    {
        "method_id": "positive_nn_risk_union_top40",
        "method_role": "frozen_v02_can_branch",
        "path": DEFAULT_OUT_DIR
        / "fresh606_v02_endpoint_200ep_can40/split606/positive_nn_risk_union_top40/eval20/metrics.csv",
    },
    {
        "method_id": "positive_nn_risk_fusion_top40",
        "method_role": "cleaner_support_diagnostic",
        "path": DEFAULT_OUT_DIR / "fresh606_v02_endpoint_200ep_can40/split606/pnrf40/eval20/metrics.csv",
    },
    {
        "method_id": "cau_action_conflict_expanded_mask",
        "method_role": "expanded_mask_diagnostic",
        "path": DEFAULT_OUT_DIR / "cau_action_conflict_can606_expanded_mask_b005_m05_eval20/metrics.csv",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
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


def success_count(row: dict[str, str]) -> int:
    return int(round(float(row["success_rate"]) * int(float(row["eval_episodes"]))))


def score(successes: int, episodes: int) -> str:
    return f"{successes}/{episodes}"


def checkpoint_name(row: dict[str, str], method_id: str) -> str:
    name = row.get("checkpoint_name", "")
    if name:
        return name
    if method_id == "candidate_e_gate":
        return "router"
    return "endpoint"


def metric_rows(out_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in METRIC_SOURCES:
        path = Path(source["path"])
        if not path.exists():
            raise FileNotFoundError(path)
        for metric in read_csv(path):
            episodes = int(float(metric["eval_episodes"]))
            successes = success_count(metric)
            rows.append(
                {
                    "split_seed": SPLIT_SEED,
                    "method_id": source["method_id"],
                    "method_role": source["method_role"],
                    "checkpoint_name": checkpoint_name(metric, source["method_id"]),
                    "success_count": successes,
                    "eval_episodes": episodes,
                    "endpoint_success": f"{float(metric['success_rate']):.3f}",
                    "avg_len": f"{float(metric['avg_len']):.1f}",
                    "checkpoint": metric.get("checkpoint", ""),
                    "metrics_path": str(path),
                }
            )
    setup_path = (
        out_dir
        / "fresh606_v02_endpoint_200ep_can40"
        / "split606"
        / "endpoint_setup_summary.csv"
    )
    if setup_path.exists():
        setup_rows = {row["candidate_id"]: row for row in read_csv(setup_path)}
        for row in rows:
            setup = setup_rows.get(str(row["method_id"]))
            if setup is None:
                continue
            for key in [
                "train_demo_count",
                "selected_unlabeled",
                "selected_hidden_positive",
                "selected_hidden_bad",
                "support_purity",
                "hidden_positive_recall",
                "hidden_bad_admission",
            ]:
                row[key] = setup.get(key, "")
    expanded_setup = out_dir / "cau_action_conflict_can606_expanded_mask_b005_m05_e200" / "setup" / "diagnostics.json"
    if expanded_setup.exists():
        setup = json.loads(expanded_setup.read_text(encoding="utf-8"))
        for row in rows:
            if row["method_id"] != "cau_action_conflict_expanded_mask":
                continue
            row["train_demo_count"] = setup.get("train_demo_count", "")
    for row in rows:
        for key in [
            "train_demo_count",
            "selected_unlabeled",
            "selected_hidden_positive",
            "selected_hidden_bad",
            "support_purity",
            "hidden_positive_recall",
            "hidden_bad_admission",
        ]:
            row.setdefault(key, "")
    return rows


def row_for(rows: list[dict[str, object]], method_id: str, checkpoint: str = "model_epoch_200") -> dict[str, object]:
    for row in rows:
        if row["method_id"] == method_id and row["checkpoint_name"] == checkpoint:
            return row
    raise KeyError((method_id, checkpoint))


def best_new_branch(rows: list[dict[str, object]]) -> dict[str, object]:
    candidates = [
        row
        for row in rows
        if row["method_id"]
        in {
            "cau_action_conflict",
            "positive_nn_risk_union_top40",
            "positive_nn_risk_fusion_top40",
            "cau_action_conflict_expanded_mask",
        }
    ]
    return max(candidates, key=lambda row: int(row["success_count"]))


def support_row(out_dir: Path, candidate_id: str) -> dict[str, str]:
    path = out_dir / "cau_v02_fresh606707_support_preflight" / "v02_fresh_router_support_per_split.csv"
    for row in read_csv(path):
        if int(row["split_seed"]) == SPLIT_SEED and row["candidate_id"] == candidate_id:
            return row
    raise KeyError(candidate_id)


def gate_row(out_dir: Path) -> dict[str, str]:
    path = out_dir / "cau_v02_portfolio_preflight_gate_scan.csv"
    return read_csv(path)[0]


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def write_report(out_dir: Path, rows: list[dict[str, object]]) -> None:
    report_path = out_dir / "CAU_V02_FRESH606_ENDPOINT_VALIDATION_REPORT.md"
    summary_csv = out_dir / "cau_v02_fresh606_endpoint_validation_summary.csv"
    positive = row_for(rows, "positive_only_nn")
    weighted = row_for(rows, "weighted_bc")
    candidate_e = row_for(rows, "candidate_e_gate", "router")
    cau = row_for(rows, "cau_action_conflict")
    union = row_for(rows, "positive_nn_risk_union_top40")
    fusion = row_for(rows, "positive_nn_risk_fusion_top40")
    expanded = row_for(rows, "cau_action_conflict_expanded_mask")
    best_candidate = best_new_branch(rows)
    support_union = support_row(out_dir, "positive_nn_risk_union_top40")
    support_fusion = support_row(out_dir, "positive_nn_risk_fusion_top40")
    gate = gate_row(out_dir)
    threshold = float(gate["threshold"])
    estimated_mass = float(support_union["estimated_positive_mass"])
    selected_branch = "CAU" if estimated_mass > threshold else "v0.2"

    columns = [
        "method_id",
        "method_role",
        "checkpoint_name",
        "success_count",
        "eval_episodes",
        "endpoint_success",
        "avg_len",
        "train_demo_count",
        "selected_unlabeled",
        "selected_hidden_bad",
    ]
    lines = [
        "# CAU+v0.2 Fresh606 Endpoint Validation",
        "",
        "This is the first fresh endpoint check for the post-hoc CAU+v0.2 portfolio hypothesis.",
        "It uses Can 40p/80b split 606, which was not part of the five-split gate fit.",
        "",
        "## Decision",
        "",
        (
            f"- The post-hoc gate `{gate['gate_id']}` would select `{selected_branch}` on split 606 "
            f"because estimated positive mass is `{estimated_mass:.3f}` versus threshold `{threshold:.3f}`."
        ),
        (
            f"- The selected CAU branch reaches {score(int(cau['success_count']), int(cau['eval_episodes']))}, "
            f"below positive-only at {score(int(positive['success_count']), int(positive['eval_episodes']))}."
        ),
        (
            f"- Frozen v0.2 union reaches {score(int(union['success_count']), int(union['eval_episodes']))}; "
            f"the cleaner risk-fusion diagnostic reaches {score(int(fusion['success_count']), int(fusion['eval_episodes']))}."
        ),
        (
            f"- Proper expanded-mask CAU, which trains with the full 130-demo transition-weight filter, reaches "
            f"{score(int(expanded['success_count']), int(expanded['eval_episodes']))}."
        ),
        (
            f"- Best new branch on this fresh split is `{best_candidate['method_id']}` at "
            f"{score(int(best_candidate['success_count']), int(best_candidate['eval_episodes']))}, "
            f"which is {int(best_candidate['success_count']) - int(positive['success_count']):+d} versus positive-only."
        ),
        "- This rejects promoting the CAU+v0.2 portfolio as a fresh-validated SOTA method in its current form.",
        "",
        "## Endpoint Rows",
        "",
        *markdown_table(rows, columns),
        "",
        "## Support Read",
        "",
        (
            f"- Frozen v0.2 union support selected {support_union['selected_unlabeled']} unlabeled demos: "
            f"{support_union['hidden_positive_selected']} hidden positives and "
            f"{support_union['hidden_bad_selected']} hidden bad demos "
            f"(purity {support_union['support_purity']})."
        ),
        (
            f"- Risk-fusion support selected {support_fusion['selected_unlabeled']} unlabeled demos: "
            f"{support_fusion['hidden_positive_selected']} hidden positives and "
            f"{support_fusion['hidden_bad_selected']} hidden bad demos "
            f"(purity {support_fusion['support_purity']})."
        ),
        "- Cleaner support alone did not recover the positive-only anchor on this split.",
        "- Expanding CAU to the full conservative transition-weight mask made the endpoint worse, so the split606 CAU failure is not only a filter/config mismatch.",
        "",
        "## References",
        "",
        f"- Summary CSV: `{summary_csv}`.",
        f"- CAU eval report: `{out_dir / 'cau_action_conflict_can606_b005_m05_eval20/REPORT.md'}`.",
        f"- Expanded-mask CAU eval report: `{out_dir / 'cau_action_conflict_can606_expanded_mask_b005_m05_eval20/REPORT.md'}`.",
        f"- v0.2 union eval report: `{out_dir / 'fresh606_v02_endpoint_200ep_can40/split606/positive_nn_risk_union_top40/eval20/REPORT.md'}`.",
        f"- Risk-fusion eval report: `{out_dir / 'fresh606_v02_endpoint_200ep_can40/split606/pnrf40/eval20/REPORT.md'}`.",
        f"- Support preflight: `{out_dir / 'cau_v02_fresh606707_support_preflight/v02_fresh_router_support_REPORT.md'}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows = metric_rows(args.out_dir)
    fieldnames = [
        "split_seed",
        "method_id",
        "method_role",
        "checkpoint_name",
        "success_count",
        "eval_episodes",
        "endpoint_success",
        "avg_len",
        "train_demo_count",
        "selected_unlabeled",
        "selected_hidden_positive",
        "selected_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "checkpoint",
        "metrics_path",
    ]
    summary_csv = args.out_dir / "cau_v02_fresh606_endpoint_validation_summary.csv"
    write_csv(summary_csv, rows, fieldnames)
    write_report(args.out_dir, rows)
    print(f"wrote {summary_csv}")
    print(f"wrote {args.out_dir / 'CAU_V02_FRESH606_ENDPOINT_VALIDATION_REPORT.md'}")


if __name__ == "__main__":
    main()
