from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(".")
DEFAULT_ROOT = ROOT / "results" / "final_paper" / "ablations" / "v02_union_endpoint_200ep_can40"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--summary-name", default="endpoint_200ep_3split_summary.csv")
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


def split_sort_key(path: Path) -> tuple[int, str]:
    suffix = path.name.removeprefix("split")
    return (int(suffix), path.name) if suffix.isdigit() else (10**9, path.name)


def load_split_rows(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for split_root in sorted(root.glob("split*"), key=split_sort_key):
        summary = split_root / "endpoint_200ep_summary.csv"
        if not summary.exists():
            continue
        for row in read_csv(summary):
            rows.append(
                {
                    "split_seed": row["split_seed"],
                    "method_id": row["method_id"],
                    "method_role": row["method_role"],
                    "endpoint_success": float(row["endpoint_success"]),
                    "success_count": int(row["success_count"]),
                    "eval_episodes": int(row["eval_episodes"]),
                }
            )
    if not rows:
        raise FileNotFoundError(f"no split endpoint summaries found under {root}")
    return rows


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["method_id"])].append(row)
    out = []
    for method_id, group in grouped.items():
        success = sum(int(row["success_count"]) for row in group)
        episodes = sum(int(row["eval_episodes"]) for row in group)
        out.append(
            {
                "method_id": method_id,
                "method_role": group[0]["method_role"],
                "split_count": len(group),
                "success_count": success,
                "eval_episodes": episodes,
                "endpoint_success": f"{success / episodes:.3f}",
                "split_successes": ";".join(
                    f"{row['split_seed']}:{float(row['endpoint_success']):.3f}" for row in sorted(group, key=lambda r: int(r["split_seed"]))
                ),
            }
        )
    out.sort(key=lambda row: float(row["endpoint_success"]), reverse=True)
    return out


def split_winners(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_split: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["method_role"] == "oracle_control":
            continue
        by_split[str(row["split_seed"])].append(row)
    out = []
    for split_seed, group in sorted(by_split.items(), key=lambda item: int(item[0])):
        winner = max(group, key=lambda row: float(row["endpoint_success"]))
        union = next(row for row in group if row["method_id"] == "positive_nn_risk_union_top40")
        best_baseline = max(
            [row for row in group if row["method_id"] != "positive_nn_risk_union_top40"],
            key=lambda row: float(row["endpoint_success"]),
        )
        out.append(
            {
                "split_seed": split_seed,
                "winner": winner["method_id"],
                "winner_success": f"{float(winner['endpoint_success']):.3f}",
                "union_success": f"{float(union['endpoint_success']):.3f}",
                "best_existing_baseline": best_baseline["method_id"],
                "best_existing_success": f"{float(best_baseline['endpoint_success']):.3f}",
                "union_minus_best_existing": f"{float(union['endpoint_success']) - float(best_baseline['endpoint_success']):+.3f}",
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


def report(root: Path, summary_rows: list[dict[str, object]], winner_rows: list[dict[str, object]]) -> str:
    union = next(row for row in summary_rows if row["method_id"] == "positive_nn_risk_union_top40")
    positive = next(row for row in summary_rows if row["method_id"] == "positive_only_nn")
    triage = next(row for row in summary_rows if row["method_id"] == "triage_bc")
    weighted = next(row for row in summary_rows if row["method_id"] == "weighted_bc")
    union_wins = sum(row["winner"] == "positive_nn_risk_union_top40" for row in winner_rows)
    lines = [
        "# v0.2 Union Candidate Can 40p/80b Endpoint Summary",
        "",
        "This aggregates the bounded three-split endpoint gate for the union candidate.",
        "The candidate keeps positive-only NN support and adds risk-fusion demos; it was developed after the action-risk replacement candidate failed endpoint checks.",
        "",
        "## Aggregate Endpoint Rows",
        "",
        *markdown_table(
            summary_rows,
            [
                "method_id",
                "method_role",
                "split_count",
                "success_count",
                "eval_episodes",
                "endpoint_success",
                "split_successes",
            ],
        ),
        "",
        "## Split Winners",
        "",
        *markdown_table(
            winner_rows,
            [
                "split_seed",
                "winner",
                "winner_success",
                "best_existing_baseline",
                "best_existing_success",
                "union_minus_best_existing",
            ],
        ),
        "",
        "## Read",
        "",
        (
            f"- Union reaches `{union['success_count']}/{union['eval_episodes']}` "
            f"(`{union['endpoint_success']}`), versus positive-only NN `{positive['endpoint_success']}`, "
            f"TRIAGE-BC v0.1 `{triage['endpoint_success']}`, and weighted BC `{weighted['endpoint_success']}`."
        ),
        f"- Union is the best non-oracle row on `{union_wins}/3` split seeds and pooled best over 150 rollouts.",
        "- This is the first Can 40p/80b candidate that beats the strong positive-only row in the pooled frozen endpoint matrix.",
        "- It is still not a full high-impact v0.2 result: Lift MG and Can MG remain unresolved, and the candidate loses split 11 to positive-only NN.",
        "",
        "## Outputs",
        "",
        f"- `{root / 'endpoint_200ep_3split_summary.csv'}`",
        f"- split reports under `{root}/split*/REPORT.md`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    split_rows = load_split_rows(args.root)
    summary_rows = aggregate(split_rows)
    winner_rows = split_winners(split_rows)
    write_csv(
        args.root / args.summary_name,
        summary_rows,
        [
            "method_id",
            "method_role",
            "split_count",
            "success_count",
            "eval_episodes",
            "endpoint_success",
            "split_successes",
        ],
    )
    (args.root / args.report_name).write_text(report(args.root, summary_rows, winner_rows), encoding="utf-8")
    print(f"wrote {args.root / args.summary_name}")
    print(f"wrote {args.root / args.report_name}")


if __name__ == "__main__":
    main()
