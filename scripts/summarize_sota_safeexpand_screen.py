from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(".")
DEFAULT_EVAL_METRICS = ROOT / "results" / "sota_candidate" / "safeexpand_can404_demo103_eval20" / "metrics.csv"
DEFAULT_PREFLIGHT_DIAGNOSTICS = (
    ROOT / "results" / "sota_candidate" / "safeexpand_can404_demo103_preflight" / "diagnostics.json"
)
DEFAULT_CAU_SUMMARY = ROOT / "results" / "sota_candidate" / "cau_action_conflict_can404_screen_summary.csv"
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-metrics", type=Path, default=DEFAULT_EVAL_METRICS)
    parser.add_argument("--preflight-diagnostics", type=Path, default=DEFAULT_PREFLIGHT_DIAGNOSTICS)
    parser.add_argument("--cau-summary", type=Path, default=DEFAULT_CAU_SUMMARY)
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


def copy_reference(
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
    cau_rows = read_csv(args.cau_summary)
    diagnostics = json.loads(args.preflight_diagnostics.read_text(encoding="utf-8"))

    positive = row_by_method(cau_rows, "positive_only_nn_top40")
    weighted = row_by_method(cau_rows, "weighted_bc_full_pool")
    candidate_c = row_by_method(cau_rows, "candidate_c_sequence_mask_e200")
    cau_best = row_by_method(cau_rows, "cau_action_conflict_b005_m05_e200")
    positive_success = int(positive["success_count"])

    rows: list[dict[str, object]] = []
    copy_reference(rows, positive, "baseline", positive_success)
    copy_reference(rows, weighted, "baseline", positive_success)
    copy_reference(rows, candidate_c, "previous_candidate", positive_success)
    copy_reference(rows, cau_best, "previous_sota_candidate", positive_success)
    for eval_row in eval_rows:
        success_count = success_count_from_rate(eval_row)
        epoch = eval_row["checkpoint_name"].removeprefix("model_epoch_")
        rows.append(
            {
                "method_id": f"safeexpand_demo103_e{epoch}",
                "label": f"SafeExpand demo103 e{epoch}",
                "kind": "sota_candidate_4",
                "train_epochs": epoch,
                "eval_episodes": eval_row["eval_episodes"],
                "success_count": success_count,
                "success_rate": f"{float(eval_row['success_rate']):.3f}",
                "avg_len": f"{float(eval_row['avg_len']):.1f}",
                "delta_vs_positive": success_count - positive_success,
            }
        )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_csv = args.out_dir / "safeexpand_can404_screen_summary.csv"
    report_path = args.out_dir / "safeexpand_can404_screen_REPORT.md"
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

    candidate_rows = [row for row in rows if row["kind"] == "sota_candidate_4"]
    best_candidate = max(candidate_rows, key=lambda row: int(row["success_count"]))
    decision = "reject" if int(best_candidate["success_count"]) < positive_success else "needs_followup"
    lines = [
        "# SafeExpand-BC Can404 Screen",
        "",
        "This is the first SOTA Candidate 4 screen from `triage_bc_sota_candidate_plan.md`.",
        "It tests a conservative one-demo expansion of the positive-only NN support.",
        "",
        "## Support Change",
        "",
        f"- Added demos: `{', '.join(diagnostics['added_demo_ids'])}`.",
        f"- Added hidden-positive / hidden-bad diagnostic: `{diagnostics['added_hidden_positive']}` / `{diagnostics['added_hidden_bad']}`.",
        f"- Final selected unlabeled support: `{diagnostics['selected_hidden_positive']}` hidden-positive, `{diagnostics['selected_hidden_bad']}` hidden-bad out of `{diagnostics['selected_unlabeled_count']}`.",
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
            f"- Best SafeExpand checkpoint: `{best_candidate['success_count']}/20`.",
            f"- Positive-only NN matched screen: `{positive_success}/20`.",
            f"- Candidate C and CAU matched screen: `{candidate_c['success_count']}/20` and `{cau_best['success_count']}/20`.",
            f"- Decision: `{decision}` for this one-demo SafeExpand recipe.",
            "",
            "Read: adding the single certified-safe hidden-positive demo does not preserve the anchor. Endpoint performance drops below weighted BC, so this recipe should not be scaled.",
            "",
            "## Artifacts",
            "",
            f"- Preflight diagnostics: `{args.preflight_diagnostics}`.",
            f"- Eval report: `{args.eval_metrics.parent / 'REPORT.md'}`.",
            f"- Summary CSV: `{summary_csv}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    expected = {
        "positive_only_nn_top40": 17,
        "weighted_bc_full_pool": 13,
        "candidate_c_sequence_mask_e200": 16,
        "cau_action_conflict_b005_m05_e200": 16,
        "safeexpand_demo103_e100": 10,
        "safeexpand_demo103_e200": 12,
    }
    actual = {row["method_id"]: int(row["success_count"]) for row in rows}
    for key, value in expected.items():
        if actual.get(key) != value:
            raise AssertionError(f"{key}: expected {value}, got {actual.get(key)}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
