from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(".")
DEFAULT_EVAL_METRICS = ROOT / "results" / "sota_candidate" / "sm_rwbc_can404_m003_lam2_combined_eval20" / "metrics.csv"
DEFAULT_PREFLIGHT_REPORT = (
    ROOT
    / "results"
    / "sota_candidate"
    / "sm_rwbc_can404_m003_lam2_combined_preflight"
    / "sm_rwbc_preflight_REPORT.md"
)
DEFAULT_CANDIDATE_C_SUMMARY = ROOT / "results" / "candidate_breakthrough" / "candidate_c_endpoint_screen_summary.csv"
DEFAULT_CANDIDATE_D_SUMMARY = ROOT / "results" / "candidate_breakthrough" / "candidate_d_endpoint_screen_summary.csv"
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-metrics", type=Path, default=DEFAULT_EVAL_METRICS)
    parser.add_argument("--preflight-report", type=Path, default=DEFAULT_PREFLIGHT_REPORT)
    parser.add_argument("--candidate-c-summary", type=Path, default=DEFAULT_CANDIDATE_C_SUMMARY)
    parser.add_argument("--candidate-d-summary", type=Path, default=DEFAULT_CANDIDATE_D_SUMMARY)
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


def success_count_from_rate(row: dict[str, str]) -> int:
    return int(round(float(row["success_rate"]) * int(row["eval_episodes"])))


def row_by_method(rows: list[dict[str, str]], method_id: str) -> dict[str, str]:
    for row in rows:
        if row["method_id"] == method_id:
            return row
    raise KeyError(method_id)


def main() -> None:
    args = parse_args()
    eval_rows = read_csv(args.eval_metrics)
    c_rows = read_csv(args.candidate_c_summary)
    d_rows = read_csv(args.candidate_d_summary)
    positive = row_by_method(c_rows, "positive_only_nn_top40")
    weighted = row_by_method(c_rows, "weighted_bc_full_pool")
    candidate_c = row_by_method(c_rows, "candidate_c_sequence_mask_e200")
    candidate_x = row_by_method(d_rows, "candidate_x_extra_negative_action_e200")

    rows: list[dict[str, object]] = [
        {
            "method_id": "positive_only_nn_top40",
            "label": positive["label"],
            "kind": "baseline",
            "train_epochs": positive["train_epochs"],
            "eval_episodes": positive["eval_episodes"],
            "success_count": positive["success_count"],
            "success_rate": positive["success_rate"],
            "avg_len": positive["avg_len"],
            "delta_vs_positive": 0,
        },
        {
            "method_id": "weighted_bc_full_pool",
            "label": weighted["label"],
            "kind": "baseline",
            "train_epochs": weighted["train_epochs"],
            "eval_episodes": weighted["eval_episodes"],
            "success_count": weighted["success_count"],
            "success_rate": weighted["success_rate"],
            "avg_len": weighted["avg_len"],
            "delta_vs_positive": int(weighted["success_count"]) - int(positive["success_count"]),
        },
        {
            "method_id": "candidate_c_sequence_mask_e200",
            "label": candidate_c["label"],
            "kind": "previous_candidate",
            "train_epochs": candidate_c["train_epochs"],
            "eval_episodes": candidate_c["eval_episodes"],
            "success_count": candidate_c["success_count"],
            "success_rate": candidate_c["success_rate"],
            "avg_len": candidate_c["avg_len"],
            "delta_vs_positive": int(candidate_c["success_count"]) - int(positive["success_count"]),
        },
        {
            "method_id": "candidate_x_extra_negative_action_e200",
            "label": candidate_x["label"],
            "kind": "previous_candidate",
            "train_epochs": candidate_x["train_epochs"],
            "eval_episodes": candidate_x["eval_episodes"],
            "success_count": candidate_x["success_count"],
            "success_rate": candidate_x["success_rate"],
            "avg_len": candidate_x["avg_len"],
            "delta_vs_positive": int(candidate_x["success_count"]) - int(positive["success_count"]),
        },
    ]
    for eval_row in eval_rows:
        success_count = success_count_from_rate(eval_row)
        epoch = eval_row["checkpoint_name"].removeprefix("model_epoch_")
        rows.append(
            {
                "method_id": f"sm_rwbc_m003_lam2_combined_e{epoch}",
                "label": f"SM-RWBC m0.03 lambda2 combined e{epoch}",
                "kind": "sota_candidate_1",
                "train_epochs": epoch,
                "eval_episodes": eval_row["eval_episodes"],
                "success_count": success_count,
                "success_rate": f"{float(eval_row['success_rate']):.3f}",
                "avg_len": f"{float(eval_row['avg_len']):.1f}",
                "delta_vs_positive": success_count - int(positive["success_count"]),
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = args.out_dir / "sm_rwbc_can404_screen_summary.csv"
    report_path = args.out_dir / "sm_rwbc_can404_screen_REPORT.md"
    fieldnames = [
        "method_id",
        "label",
        "kind",
        "train_epochs",
        "eval_episodes",
        "success_count",
        "success_rate",
        "avg_len",
        "delta_vs_positive",
    ]
    write_csv(summary_csv, rows, fieldnames)

    best_sm = max((row for row in rows if row["kind"] == "sota_candidate_1"), key=lambda row: int(row["success_count"]))
    positive_success = int(positive["success_count"])
    decision = (
        "reject"
        if int(best_sm["success_count"]) < positive_success
        else "needs_followup"
    )
    lines = [
        "# SM-RWBC Can404 Screen",
        "",
        "This is the first SOTA Candidate 1 screen from `triage_bc_sota_candidate_plan.md`.",
        "It tests broad-pool sequence-masked risk-weighted BC on the severe Can split-404 regression case.",
        "",
        "## Result",
        "",
        "| method | successes | success rate | avg len | delta vs positive |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {label} | {success_count}/{eval_episodes} | {success_rate} | {avg_len} | {delta_vs_positive} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"- Best SM-RWBC checkpoint: `{best_sm['success_count']}/20`.",
            f"- Positive-only NN matched screen: `{positive_success}/20`.",
            f"- Previous Candidate C sequence mask: `{candidate_c['success_count']}/20`.",
            f"- Decision: `{decision}` for this broad-pool `m_min=0.03`, `lambda=2`, `combined` recipe.",
            "",
            "Read: the preflight reduced hidden-bad transition mass in the broad pool, but the endpoint policy still collapses below the positive-only anchor. Do not scale this recipe unchanged to Can505 or Lift.",
            "",
            "## Artifacts",
            "",
            f"- Preflight report: `{args.preflight_report}`.",
            f"- Eval report: `{args.eval_metrics.parent / 'REPORT.md'}`.",
            f"- Summary CSV: `{summary_csv}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = {
        "positive_only_nn_top40": 17,
        "candidate_c_sequence_mask_e200": 16,
        "candidate_x_extra_negative_action_e200": 14,
        "sm_rwbc_m003_lam2_combined_e100": 10,
        "sm_rwbc_m003_lam2_combined_e200": 10,
    }
    actual = {row["method_id"]: int(row["success_count"]) for row in rows}
    for key, value in expected.items():
        if actual.get(key) != value:
            raise AssertionError(f"{key}: expected {value}, got {actual.get(key)}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
