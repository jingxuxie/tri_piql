#!/usr/bin/env python3
"""Summarize CAU/GMM-router and fixed-CAU follow-up on fresh Can splits."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(".")
OUT_DIR = ROOT / "results" / "sota_candidate"


PATHS = {
    "can606_gmm_summary": OUT_DIR / "can606_gmm_confidence_cau_router_summary.csv",
    "can606_gmm_scan": OUT_DIR / "can606_gmm_confidence_cau_router_threshold_scan.csv",
    "can707_positive_eval20": ROOT / "results/candidate_g_fresh_preflight/can707_positive_epoch200_eval20/metrics.csv",
    "can707_weighted_eval20": ROOT / "results/candidate_g_fresh_preflight/can707_weighted_epoch200_eval20/metrics.csv",
    "can707_cau_eval20": OUT_DIR / "cau_action_conflict_can707_b005_m05_eval20/metrics.csv",
    "can707_gmm_router_eval20": OUT_DIR / "can707_gmm_confidence_cau_router_thr15p545_eval20/metrics.csv",
    "can707_eval50": OUT_DIR / "can707_positive_weighted_cau_eval50/metrics.csv",
    "can808_positive_eval50": ROOT
    / "results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_positive_only_nn_policy0/eval/metrics.csv",
    "can808_weighted_eval50": ROOT
    / "results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_weighted_bc_policy0/eval/metrics.csv",
    "can808_triage_eval50": ROOT
    / "results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_triage_bc_policy0/eval/metrics.csv",
    "can808_candidate_e_eval50": ROOT
    / "results/candidate_f_can_fresh_validation/candidate_e_eval/can808_candidate_e_gate_eval50/metrics.csv",
    "can808_cau_eval50": OUT_DIR / "cau_action_conflict_can808_b005_m05_eval50/metrics.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
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


def successes(row: dict[str, str]) -> int:
    return int(round(float(row["success_rate"]) * int(float(row["eval_episodes"]))))


def metric_row(path: Path, *, checkpoint_name: str = "model_epoch_200") -> dict[str, str]:
    for row in read_csv(path):
        if row.get("checkpoint_name") == checkpoint_name:
            return row
    raise KeyError((path, checkpoint_name))


def metric_row_by_checkpoint_substr(path: Path, substring: str) -> dict[str, str]:
    for row in read_csv(path):
        if substring in row.get("checkpoint", ""):
            return row
    raise KeyError((path, substring))


def score(success_count: object, episodes: object) -> str:
    return f"{int(success_count)}/{int(episodes)}"


def add_metric(
    rows: list[dict[str, object]],
    *,
    artifact_id: str,
    split: int,
    screen: str,
    method_id: str,
    method_role: str,
    row: dict[str, str],
    source_path: Path,
) -> None:
    episodes = int(float(row["eval_episodes"]))
    rows.append(
        {
            "artifact_id": artifact_id,
            "split": split,
            "screen": screen,
            "method_id": method_id,
            "method_role": method_role,
            "successes": successes(row),
            "eval_episodes": episodes,
            "score": score(successes(row), episodes),
            "success_rate": f"{float(row['success_rate']):.3f}",
            "avg_len": f"{float(row['avg_len']):.1f}",
            "source_path": str(source_path),
        }
    )


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []

    can606_q25 = read_csv(PATHS["can606_gmm_summary"])[0]
    can606_best = max(
        read_csv(PATHS["can606_gmm_scan"]),
        key=lambda row: (
            int(row["routed_successes"]),
            -int(row["losses_vs_positive"]),
            int(row["gains_vs_positive"]),
        ),
    )
    rows.append(
        {
            "artifact_id": "can606_gmm_q25",
            "split": 606,
            "screen": "eval20",
            "method_id": "gmm_confidence_router_q25",
            "method_role": "labeled_calibrated_router",
            "successes": int(can606_q25["routed_successes"]),
            "eval_episodes": int(can606_q25["episodes"]),
            "score": score(can606_q25["routed_successes"], can606_q25["episodes"]),
            "success_rate": f"{int(can606_q25['routed_successes']) / int(can606_q25['episodes']):.3f}",
            "avg_len": "",
            "source_path": str(PATHS["can606_gmm_summary"]),
        }
    )
    rows.append(
        {
            "artifact_id": "can606_gmm_posthoc_best",
            "split": 606,
            "screen": "eval20",
            "method_id": "gmm_confidence_router_posthoc",
            "method_role": "same_screen_hypothesis",
            "successes": int(can606_best["routed_successes"]),
            "eval_episodes": int(can606_best["episodes"]),
            "score": score(can606_best["routed_successes"], can606_best["episodes"]),
            "success_rate": f"{int(can606_best['routed_successes']) / int(can606_best['episodes']):.3f}",
            "avg_len": "",
            "source_path": str(PATHS["can606_gmm_scan"]),
        }
    )

    add_metric(
        rows,
        artifact_id="can707_positive_eval20",
        split=707,
        screen="eval20",
        method_id="positive_only_nn",
        method_role="fresh_baseline",
        row=metric_row(PATHS["can707_positive_eval20"]),
        source_path=PATHS["can707_positive_eval20"],
    )
    add_metric(
        rows,
        artifact_id="can707_weighted_eval20",
        split=707,
        screen="eval20",
        method_id="weighted_bc",
        method_role="fresh_baseline",
        row=metric_row(PATHS["can707_weighted_eval20"]),
        source_path=PATHS["can707_weighted_eval20"],
    )
    add_metric(
        rows,
        artifact_id="can707_cau_eval20",
        split=707,
        screen="eval20",
        method_id="cau_action_conflict",
        method_role="fresh_cau_followup",
        row=metric_row(PATHS["can707_cau_eval20"]),
        source_path=PATHS["can707_cau_eval20"],
    )
    add_metric(
        rows,
        artifact_id="can707_gmm_router_eval20",
        split=707,
        screen="eval20",
        method_id="gmm_confidence_router_thr15p545",
        method_role="fresh_router_transfer",
        row=read_csv(PATHS["can707_gmm_router_eval20"])[0],
        source_path=PATHS["can707_gmm_router_eval20"],
    )

    for artifact_id, method_id, role, substring in [
        ("can707_positive_eval50", "positive_only_nn", "fresh_baseline_confirmation", "positive_only"),
        ("can707_weighted_eval50", "weighted_bc", "fresh_baseline_confirmation", "weighted_bc"),
        ("can707_cau_eval50", "cau_action_conflict", "fresh_cau_confirmation", "cau_action_conflict"),
    ]:
        add_metric(
            rows,
            artifact_id=artifact_id,
            split=707,
            screen="eval50",
            method_id=method_id,
            method_role=role,
            row=metric_row_by_checkpoint_substr(PATHS["can707_eval50"], substring),
            source_path=PATHS["can707_eval50"],
        )

    for artifact_id, method_id, role, path in [
        ("can808_positive_eval50", "positive_only_nn", "fresh_validation_baseline", PATHS["can808_positive_eval50"]),
        ("can808_weighted_eval50", "weighted_bc", "fresh_validation_baseline", PATHS["can808_weighted_eval50"]),
        ("can808_triage_eval50", "triage_bc_v01", "fresh_validation_baseline", PATHS["can808_triage_eval50"]),
    ]:
        add_metric(
            rows,
            artifact_id=artifact_id,
            split=808,
            screen="eval50",
            method_id=method_id,
            method_role=role,
            row=metric_row(path),
            source_path=path,
        )
    add_metric(
        rows,
        artifact_id="can808_candidate_e_eval50",
        split=808,
        screen="eval50",
        method_id="candidate_e_gate",
        method_role="fresh_validation_router_reference",
        row=read_csv(PATHS["can808_candidate_e_eval50"])[0],
        source_path=PATHS["can808_candidate_e_eval50"],
    )
    for checkpoint_name in ("model_epoch_100", "model_epoch_200"):
        suffix = checkpoint_name.rsplit("_", maxsplit=1)[-1]
        add_metric(
            rows,
            artifact_id=f"can808_cau_e{suffix}_eval50",
            split=808,
            screen="eval50",
            method_id=f"cau_action_conflict_{checkpoint_name}",
            method_role="fresh_fixed_cau_validation",
            row=metric_row(PATHS["can808_cau_eval50"], checkpoint_name=checkpoint_name),
            source_path=PATHS["can808_cau_eval50"],
        )
    return rows, can606_best


def row_by_id(rows: list[dict[str, object]], artifact_id: str) -> dict[str, object]:
    for row in rows:
        if row["artifact_id"] == artifact_id:
            return row
    raise KeyError(artifact_id)


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def write_report(out_dir: Path, rows: list[dict[str, object]], can606_best: dict[str, str]) -> None:
    summary_path = out_dir / "cau_gmm_router_followup_summary.csv"
    report_path = out_dir / "CAU_GMM_ROUTER_FOLLOWUP_REPORT.md"
    can606_q25 = row_by_id(rows, "can606_gmm_q25")
    can707_cau20 = row_by_id(rows, "can707_cau_eval20")
    can707_router = row_by_id(rows, "can707_gmm_router_eval20")
    can707_pos50 = row_by_id(rows, "can707_positive_eval50")
    can707_weighted50 = row_by_id(rows, "can707_weighted_eval50")
    can707_cau50 = row_by_id(rows, "can707_cau_eval50")
    can808_pos50 = row_by_id(rows, "can808_positive_eval50")
    can808_weighted50 = row_by_id(rows, "can808_weighted_eval50")
    can808_triage50 = row_by_id(rows, "can808_triage_eval50")
    can808_candidate_e50 = row_by_id(rows, "can808_candidate_e_eval50")
    can808_cau200 = row_by_id(rows, "can808_cau_e200_eval50")

    columns = ["artifact_id", "split", "screen", "method_id", "score", "avg_len"]
    lines = [
        "# CAU/GMM Router Follow-up",
        "",
        "This report follows the fresh split606 CAU failure with one deployable GMM-confidence router screen and fixed-CAU checks on unused validation splits.",
        "",
        "## Decision",
        "",
        (
            f"- Split606 labeled-positive q25 GMM calibration is neutral: "
            f"`{can606_q25['score']}` versus positive-only `16/20` and CAU `15/20`."
        ),
        (
            f"- A same-screen split606 GMM threshold can reach "
            f"`{score(can606_best['routed_successes'], can606_best['episodes'])}` with "
            f"`{can606_best['losses_vs_positive']}` losses, but this is post-hoc."
        ),
        (
            f"- That frozen threshold does not transfer to split707: the router reaches "
            f"`{can707_router['score']}` and opens no CAU episodes, while CAU alone reaches "
            f"`{can707_cau20['score']}`."
        ),
        (
            f"- CAU-alone split707 confirmation is strong: `{can707_cau50['score']}` versus "
            f"positive-only `{can707_pos50['score']}` and weighted BC `{can707_weighted50['score']}`."
        ),
        (
            f"- Split808 rejects a consistent fixed-CAU dominance claim: CAU epoch 200 reaches "
            f"`{can808_cau200['score']}` versus positive-only `{can808_pos50['score']}`, "
            f"weighted BC `{can808_weighted50['score']}`, TRIAGE-BC v0.1 `{can808_triage50['score']}`, "
            f"and the older Candidate E gate `{can808_candidate_e50['score']}`."
        ),
        "- The GMM router is a no-go in this form, and CAU-alone remains a useful but inconsistent method seed rather than a promotable SOTA result.",
        "",
        "## Rows",
        "",
        *markdown_table(rows, columns),
        "",
        "## References",
        "",
        f"- Split606 GMM report: `{out_dir / 'CAN606_GMM_CONFIDENCE_CAU_ROUTER_REPORT.md'}`.",
        f"- Split707 CAU eval20: `{out_dir / 'cau_action_conflict_can707_b005_m05_eval20/REPORT.md'}`.",
        f"- Split707 GMM router eval20: `{out_dir / 'can707_gmm_confidence_cau_router_thr15p545_eval20/REPORT.md'}`.",
        f"- Split707 50-episode confirmation: `{out_dir / 'can707_positive_weighted_cau_eval50/REPORT.md'}`.",
        f"- Split808 CAU 50-episode validation: `{out_dir / 'cau_action_conflict_can808_b005_m05_eval50/REPORT.md'}`.",
        "- Split808 baseline evaluations: `results/candidate_f_can_fresh_validation/per_seed/`.",
        f"- Summary CSV: `{summary_path}`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    rows, can606_best = build_rows()
    fieldnames = [
        "artifact_id",
        "split",
        "screen",
        "method_id",
        "method_role",
        "successes",
        "eval_episodes",
        "score",
        "success_rate",
        "avg_len",
        "source_path",
    ]
    write_csv(args.out_dir / "cau_gmm_router_followup_summary.csv", rows, fieldnames)
    write_report(args.out_dir, rows, can606_best)
    print(f"wrote {args.out_dir / 'CAU_GMM_ROUTER_FOLLOWUP_REPORT.md'}")


if __name__ == "__main__":
    main()
