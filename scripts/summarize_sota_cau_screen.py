from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(".")
DEFAULT_EVAL_METRICS = ROOT / "results" / "sota_candidate" / "cau_action_conflict_can404_b005_m05_eval20" / "metrics.csv"
DEFAULT_PREFLIGHT_REPORT = (
    ROOT
    / "results"
    / "sota_candidate"
    / "cau_action_conflict_can404_preflight"
    / "cau_preflight_REPORT.md"
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


def add_reference_row(
    rows: list[dict[str, object]],
    row: dict[str, str],
    kind: str,
    positive_success: int,
) -> None:
    success_count = int(row["success_count"])
    rows.append(
        {
            "method_id": row["method_id"],
            "label": row["label"],
            "kind": kind,
            "train_epochs": row["train_epochs"],
            "eval_episodes": row["eval_episodes"],
            "success_count": success_count,
            "success_rate": row["success_rate"],
            "avg_len": row["avg_len"],
            "delta_vs_positive": success_count - positive_success,
        }
    )


def main() -> None:
    args = parse_args()
    eval_rows = read_csv(args.eval_metrics)
    c_rows = read_csv(args.candidate_c_summary)
    d_rows = read_csv(args.candidate_d_summary)

    positive = row_by_method(c_rows, "positive_only_nn_top40")
    weighted = row_by_method(c_rows, "weighted_bc_full_pool")
    candidate_c = row_by_method(c_rows, "candidate_c_sequence_mask_e200")
    candidate_d100 = row_by_method(d_rows, "candidate_d_negative_action_e100")
    candidate_d200 = row_by_method(d_rows, "candidate_d_negative_action_e200")
    candidate_x100 = row_by_method(d_rows, "candidate_x_extra_negative_action_e100")
    candidate_x200 = row_by_method(d_rows, "candidate_x_extra_negative_action_e200")

    positive_success = int(positive["success_count"])
    rows: list[dict[str, object]] = []
    add_reference_row(rows, positive, "baseline", positive_success)
    add_reference_row(rows, weighted, "baseline", positive_success)
    add_reference_row(rows, candidate_c, "previous_candidate", positive_success)
    add_reference_row(rows, candidate_d100, "previous_negative_action", positive_success)
    add_reference_row(rows, candidate_d200, "previous_negative_action", positive_success)
    add_reference_row(rows, candidate_x100, "previous_negative_action", positive_success)
    add_reference_row(rows, candidate_x200, "previous_negative_action", positive_success)

    for eval_row in eval_rows:
        success_count = success_count_from_rate(eval_row)
        epoch = eval_row["checkpoint_name"].removeprefix("model_epoch_")
        rows.append(
            {
                "method_id": f"cau_action_conflict_b005_m05_e{epoch}",
                "label": f"CAU action-conflict beta0.05 margin0.5 e{epoch}",
                "kind": "sota_candidate_2",
                "train_epochs": epoch,
                "eval_episodes": eval_row["eval_episodes"],
                "success_count": success_count,
                "success_rate": f"{float(eval_row['success_rate']):.3f}",
                "avg_len": f"{float(eval_row['avg_len']):.1f}",
                "delta_vs_positive": success_count - positive_success,
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = args.out_dir / "cau_action_conflict_can404_screen_summary.csv"
    report_path = args.out_dir / "cau_action_conflict_can404_screen_REPORT.md"
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

    cau_rows = [row for row in rows if row["kind"] == "sota_candidate_2"]
    best_cau = max(cau_rows, key=lambda row: int(row["success_count"]))
    candidate_c_success = int(candidate_c["success_count"])
    decision = "reject" if int(best_cau["success_count"]) < positive_success else "needs_followup"
    lines = [
        "# CAU-BC Can404 Screen",
        "",
        "This is the first SOTA Candidate 2 screen from `triage_bc_sota_candidate_plan.md`.",
        "It reuses the Candidate C sequence mask but swaps the rejected nearest-state negative action for an action-conflict target.",
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
            f"- Best CAU checkpoint: `{best_cau['success_count']}/20`.",
            f"- Positive-only NN matched screen: `{positive_success}/20`.",
            f"- Previous Candidate C sequence mask: `{candidate_c_success}/20`.",
            f"- Previous best nearest-negative hinge screen: `{candidate_x200['success_count']}/20`.",
            f"- Decision: `{decision}` for this action-conflict `beta=0.05`, `margin=0.5`, selected-scope recipe.",
            "",
            "Read: action-conflict retrieval fixes the worst nearest-negative hinge regression and ties Candidate C, but it still does not beat the positive-only anchor on split 404. Do not promote or scale this recipe unchanged.",
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
        "weighted_bc_full_pool": 13,
        "candidate_c_sequence_mask_e200": 16,
        "candidate_d_negative_action_e100": 14,
        "candidate_d_negative_action_e200": 13,
        "candidate_x_extra_negative_action_e100": 10,
        "candidate_x_extra_negative_action_e200": 14,
        "cau_action_conflict_b005_m05_e100": 6,
        "cau_action_conflict_b005_m05_e200": 16,
    }
    actual = {row["method_id"]: int(row["success_count"]) for row in rows}
    for key, value in expected.items():
        if actual.get(key) != value:
            raise AssertionError(f"{key}: expected {value}, got {actual.get(key)}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
