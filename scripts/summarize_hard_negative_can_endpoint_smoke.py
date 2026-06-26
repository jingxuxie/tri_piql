from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(".")
DEFAULT_RESULT_ROOT = ROOT / "results" / "final_paper" / "ablations" / "hard_negative_can_endpoint_smoke" / "split101"
DEFAULT_FOLLOWUP_PATH = (
    ROOT / "results" / "final_paper" / "ablations" / "hard_negative_can_endpoint_200ep" / "split101" / "REPORT.md"
)

RESULT_ROOT = DEFAULT_RESULT_ROOT
SETUP_SUMMARY = RESULT_ROOT / "endpoint_setup_summary.csv"
EVAL_METRICS = RESULT_ROOT / "eval_smoke_all" / "metrics.csv"
EVAL_EPISODES = RESULT_ROOT / "eval_smoke_all" / "episode_metrics.csv"
SUMMARY_OUT = RESULT_ROOT / "endpoint_smoke_summary.csv"
REPORT_OUT = RESULT_ROOT / "REPORT.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_RESULT_ROOT)
    parser.add_argument("--eval-subdir", default="eval_smoke_all")
    parser.add_argument("--summary-name", default="endpoint_smoke_summary.csv")
    parser.add_argument("--report-name", default="REPORT.md")
    parser.add_argument("--diagnostic-name", default="Hard-Negative Can")
    parser.add_argument("--diagnostic-description", default="generated hard-negative Can diagnostic")
    parser.add_argument(
        "--mechanism-sentence",
        default=(
            "The endpoint effect aligns with the support diagnostic: the hybrid keeps near-positive coverage while "
            "strongly reducing action-conflict bad-demo admission."
        ),
    )
    parser.add_argument(
        "--claim-scope-sentence",
        default=(
            "This result is suitable as targeted hard-negative evidence; keep the primary benchmark claims separate "
            "from the generated diagnostic."
        ),
    )
    parser.add_argument("--followup-path", type=Path, default=DEFAULT_FOLLOWUP_PATH)
    parser.add_argument(
        "--aggregate-splits",
        action="store_true",
        help="Treat --root as a parent directory containing split*/ endpoint runs.",
    )
    return parser.parse_args()


def configure_paths(args: argparse.Namespace) -> None:
    global RESULT_ROOT, SETUP_SUMMARY, EVAL_METRICS, EVAL_EPISODES, SUMMARY_OUT, REPORT_OUT
    RESULT_ROOT = args.root
    SETUP_SUMMARY = RESULT_ROOT / "endpoint_setup_summary.csv"
    EVAL_METRICS = RESULT_ROOT / args.eval_subdir / "metrics.csv"
    EVAL_EPISODES = RESULT_ROOT / args.eval_subdir / "episode_metrics.csv"
    SUMMARY_OUT = RESULT_ROOT / args.summary_name
    REPORT_OUT = RESULT_ROOT / args.report_name


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def candidate_tag_from_checkpoint(checkpoint: str) -> str:
    parts = Path(checkpoint).parts
    try:
        split_index = next(i for i, part in enumerate(parts) if part.startswith("split"))
        return parts[split_index + 1]
    except (ValueError, IndexError) as exc:
        raise ValueError(f"could not infer candidate tag from checkpoint path: {checkpoint}") from exc


def load_setup_rows(result_root: Path) -> dict[str, dict[str, str]]:
    rows = read_csv(result_root / "endpoint_setup_summary.csv")
    return {row["candidate_tag"]: row for row in rows}


def load_diagnostics(result_root: Path, tag: str) -> dict:
    return json.loads((result_root / tag / "setup" / "diagnostics.json").read_text(encoding="utf-8"))


def summarize_rows_for_root(result_root: Path, eval_subdir: str) -> list[dict[str, object]]:
    setup_by_tag = load_setup_rows(result_root)
    rows = []
    for metric in read_csv(result_root / eval_subdir / "metrics.csv"):
        tag = candidate_tag_from_checkpoint(metric["checkpoint"])
        setup = setup_by_tag[tag]
        diagnostics = load_diagnostics(result_root, tag)
        rows.append(
            {
                "split_seed": setup["split_seed"],
                "candidate_id": setup["candidate_id"],
                "candidate_tag": tag,
                "train_epochs": diagnostics["num_epochs"],
                "epoch_steps": diagnostics["epoch_steps"],
                "train_demo_count": setup["train_demo_count"],
                "selected_unlabeled": setup["selected_unlabeled"],
                "selected_hidden_positive": setup["selected_hidden_positive"],
                "selected_hidden_bad": setup["selected_hidden_bad"],
                "support_purity": setup["support_purity"],
                "hidden_positive_recall": setup["hidden_positive_recall"],
                "hidden_bad_admission": setup["hidden_bad_admission"],
                "success_rate": metric["success_rate"],
                "success_count": int(round(float(metric["success_rate"]) * int(metric["eval_episodes"]))),
                "eval_episodes": metric["eval_episodes"],
                "avg_len": metric["avg_len"],
                "checkpoint": metric["checkpoint"],
            }
        )
    rows.sort(key=lambda row: float(row["success_rate"]), reverse=True)
    return rows


def split_sort_key(path: Path) -> tuple[int, str]:
    if path.name.startswith("split"):
        suffix = path.name.removeprefix("split")
        if suffix.isdigit():
            return (int(suffix), path.name)
    return (10**9, path.name)


def summarize_aggregate_rows(result_root: Path, eval_subdir: str) -> list[dict[str, object]]:
    split_roots = [
        path
        for path in result_root.glob("split*")
        if (path / "endpoint_setup_summary.csv").exists()
        and (path / eval_subdir / "metrics.csv").exists()
    ]
    if not split_roots:
        raise FileNotFoundError(f"no split*/ endpoint summaries found under {result_root}")
    rows = []
    for split_root in sorted(split_roots, key=split_sort_key):
        rows.extend(summarize_rows_for_root(split_root, eval_subdir))
    rows.sort(key=lambda row: (int(row["split_seed"]), row["candidate_id"]))
    return rows


def summarize_rows(eval_subdir: str) -> list[dict[str, object]]:
    return summarize_rows_for_root(RESULT_ROOT, eval_subdir)


def aggregate_by_candidate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_candidate: dict[str, dict[str, object]] = {}
    for row in rows:
        candidate_id = str(row["candidate_id"])
        entry = by_candidate.setdefault(
            candidate_id,
            {
                "candidate_id": candidate_id,
                "success_count": 0,
                "eval_episodes": 0,
                "selected_hidden_positive": 0,
                "selected_hidden_bad": 0,
                "support_purity_sum": 0.0,
                "hidden_positive_recall_sum": 0.0,
                "hidden_bad_admission_sum": 0.0,
                "avg_len_weighted_sum": 0.0,
                "num_splits": 0,
            },
        )
        success_count = int(row["success_count"])
        eval_episodes = int(row["eval_episodes"])
        entry["success_count"] = int(entry["success_count"]) + success_count
        entry["eval_episodes"] = int(entry["eval_episodes"]) + eval_episodes
        entry["selected_hidden_positive"] = int(entry["selected_hidden_positive"]) + int(
            row["selected_hidden_positive"]
        )
        entry["selected_hidden_bad"] = int(entry["selected_hidden_bad"]) + int(row["selected_hidden_bad"])
        entry["support_purity_sum"] = float(entry["support_purity_sum"]) + float(row["support_purity"])
        entry["hidden_positive_recall_sum"] = float(entry["hidden_positive_recall_sum"]) + float(
            row["hidden_positive_recall"]
        )
        entry["hidden_bad_admission_sum"] = float(entry["hidden_bad_admission_sum"]) + float(
            row["hidden_bad_admission"]
        )
        entry["avg_len_weighted_sum"] = float(entry["avg_len_weighted_sum"]) + (
            float(row["avg_len"]) * eval_episodes
        )
        entry["num_splits"] = int(entry["num_splits"]) + 1

    summary = []
    for entry in by_candidate.values():
        num_splits = int(entry["num_splits"])
        eval_episodes = int(entry["eval_episodes"])
        success_count = int(entry["success_count"])
        summary.append(
            {
                "candidate_id": entry["candidate_id"],
                "success_count": success_count,
                "eval_episodes": eval_episodes,
                "success_rate": success_count / eval_episodes,
                "mean_support_purity": float(entry["support_purity_sum"]) / num_splits,
                "mean_hidden_positive_recall": float(entry["hidden_positive_recall_sum"]) / num_splits,
                "mean_hidden_bad_admission": float(entry["hidden_bad_admission_sum"]) / num_splits,
                "selected_hidden_positive": int(entry["selected_hidden_positive"]),
                "selected_hidden_bad": int(entry["selected_hidden_bad"]),
                "avg_len": float(entry["avg_len_weighted_sum"]) / eval_episodes,
                "num_splits": num_splits,
            }
        )
    summary.sort(key=lambda row: (float(row["success_rate"]), int(row["success_count"])), reverse=True)
    return summary


def aggregate_report(rows: list[dict[str, object]], args: argparse.Namespace) -> str:
    candidate_rows = aggregate_by_candidate(rows)
    best = candidate_rows[0]
    positive = next(
        (row for row in candidate_rows if row["candidate_id"] == "state_action_positive_nn_top40"),
        None,
    )
    split_seeds = sorted({int(row["split_seed"]) for row in rows})
    train_epochs = sorted({int(row["train_epochs"]) for row in rows})
    eval_episodes = sorted({int(row["eval_episodes"]) for row in rows})
    split_count = len(split_seeds)
    aggregate_label = "Three-Split" if split_count == 3 else f"{split_count}-Split"
    lines = [
        f"# {args.diagnostic_name} {aggregate_label} Endpoint Check",
        "",
        f"This is a {args.diagnostic_description} over split seeds "
        f"{', '.join(str(seed) for seed in split_seeds)}. It is stronger than a single-split development check, "
        "but it should be framed as targeted diagnostic evidence rather than as a primary Robomimic benchmark row.",
        f"All policies use official Robomimic BC-RNN-GMM with {train_epochs[0]} epochs, 100 gradient steps per epoch, and {eval_episodes[0]} valid-positive evaluation starts per split.",
        "",
        "## Aggregate Result",
        "",
        "| candidate | success | success rate | mean support purity | hidden-positive selected | hidden-bad selected | avg len |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in candidate_rows:
        lines.append(
            f"| {row['candidate_id']} | {row['success_count']}/{row['eval_episodes']} | "
            f"{float(row['success_rate']):.3f} | {float(row['mean_support_purity']):.3f} | "
            f"{row['selected_hidden_positive']} | {row['selected_hidden_bad']} | {float(row['avg_len']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Per-Split Result",
            "",
            "| split | candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    candidate_order = {str(row["candidate_id"]): index for index, row in enumerate(candidate_rows)}
    for row in sorted(rows, key=lambda item: (int(item["split_seed"]), candidate_order[str(item["candidate_id"])])):
        lines.append(
            f"| {row['split_seed']} | {row['candidate_id']} | {row['support_purity']} | "
            f"{row['hidden_positive_recall']} | {row['hidden_bad_admission']} | "
            f"{row['success_count']}/{row['eval_episodes']} | {float(row['avg_len']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Best aggregate row: `{best['candidate_id']}` with `{best['success_count']}/{best['eval_episodes']}` successes.",
        ]
    )
    if positive is not None and best["candidate_id"] != positive["candidate_id"]:
        delta = int(best["success_count"]) - int(positive["success_count"])
        lines.append(
            f"- The best row is ahead of state-action positive-NN top40 by `{delta}` successes over `{best['eval_episodes']}` paired-budget rollouts."
        )
    lines.extend(
        [
            f"- {args.mechanism_sentence}",
            f"- {args.claim_scope_sentence}",
            "",
            "## Outputs",
            "",
            f"- `{SUMMARY_OUT}`",
            f"- `{REPORT_OUT}`",
        ]
    )
    return "\n".join(lines) + "\n"


def report(rows: list[dict[str, object]], args: argparse.Namespace) -> str:
    if len({int(row["split_seed"]) for row in rows}) > 1:
        return aggregate_report(rows, args)
    best = rows[0]
    positive = next((row for row in rows if row["candidate_id"] == "state_action_positive_nn_top40"), None)
    split_seed = rows[0]["split_seed"]
    train_epochs = sorted({int(row["train_epochs"]) for row in rows})
    eval_episodes = sorted({int(row["eval_episodes"]) for row in rows})
    title = f"{args.diagnostic_name} Endpoint Smoke"
    scope = f"This is a bounded endpoint smoke on generated split seed {split_seed}, not a final paper endpoint row."
    if max(train_epochs) >= 200 and max(eval_episodes) >= 50:
        title = f"{args.diagnostic_name} Split-{split_seed} Endpoint Check"
        scope = (
            f"This is a single-split endpoint check on generated split seed {split_seed}, "
            "not a primary Robomimic benchmark row."
        )
    lines = [
        f"# {title}",
        "",
        scope,
        f"All policies use official Robomimic BC-RNN-GMM with {train_epochs[0]} epochs, 100 gradient steps per epoch, and {eval_episodes[0]} valid-positive evaluation starts.",
        "",
        "## Result",
        "",
        "| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['candidate_id']} | {row['support_purity']} | {row['hidden_positive_recall']} | "
            f"{row['hidden_bad_admission']} | {row['success_count']}/{row['eval_episodes']} | {float(row['avg_len']):.1f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            f"- Best row: `{best['candidate_id']}` with `{best['success_count']}/{best['eval_episodes']}` successes.",
        ]
    )
    if positive is not None:
        delta = int(best["success_count"]) - int(positive["success_count"])
        lines.append(
            f"- Positive-NN top40 is the support baseline and gets `{positive['success_count']}/{positive['eval_episodes']}` successes after selecting `{positive['selected_hidden_bad']}` hidden-bad demos on this split."
        )
        if best is not positive:
            lines.append(
                f"- The best row is ahead of positive-NN by `{delta}` successes in this bounded check."
            )
    if any(row["candidate_id"] == "bad_aware_proxy_top40" for row in rows):
        if best["candidate_id"] == "bad_aware_proxy_top40":
            if max(train_epochs) >= 200 and max(eval_episodes) >= 50:
                aggregate_path = RESULT_ROOT.parent / "REPORT.md"
                if aggregate_path.exists():
                    lines.append(
                        "- The bad-aware candidate is best on this split; use the aggregate report for claim scope."
                    )
                else:
                    lines.append(
                        "- The bad-aware candidate is best on this split; keep it exploratory until multi-split confirmation."
                    )
            else:
                lines.append(
                    "- The pure bad-aware candidate is best in this smoke; verify at the frozen endpoint budget before treating the cleaner support as a policy-quality claim."
                )
        else:
            lines.append(
                "- The pure bad-aware support is cleaner but not best in the smoke; the best endpoint candidate should be prioritized for the next run."
            )
    lines.append(f"- {args.mechanism_sentence}")
    if max(train_epochs) >= 200 and max(eval_episodes) >= 50:
        aggregate_path = RESULT_ROOT.parent / "REPORT.md"
        if aggregate_path.exists():
            lines.append(f"- The three-split aggregate is recorded in `{aggregate_path}`.")
        else:
            lines.append(
                f"- Next decision: aggregate this split with the remaining completed {args.diagnostic_name} split checks before using it as evidence."
            )
    else:
        if args.followup_path.exists():
            lines.append(
                f"- The 200-epoch / 50-episode split-{split_seed} follow-up is recorded in `{args.followup_path}`."
            )
        else:
            lines.append(
                f"- Next decision: rerun the best candidate and positive-NN baseline at the frozen 200-epoch / 50-episode endpoint budget on split {split_seed}, then decide whether to expand to split seeds 202 and 303."
            )
    lines.extend(
        [
            "",
            "## Outputs",
            "",
            f"- `{SUMMARY_OUT}`",
            f"- `{EVAL_METRICS}`",
            f"- `{EVAL_EPISODES}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    args = parse_args()
    configure_paths(args)
    if args.aggregate_splits:
        rows = summarize_aggregate_rows(RESULT_ROOT, args.eval_subdir)
    else:
        rows = summarize_rows(args.eval_subdir)
    write_csv(
        SUMMARY_OUT,
        rows,
        fieldnames=[
            "split_seed",
            "candidate_id",
            "candidate_tag",
            "train_epochs",
            "epoch_steps",
            "train_demo_count",
            "selected_unlabeled",
            "selected_hidden_positive",
            "selected_hidden_bad",
            "support_purity",
            "hidden_positive_recall",
            "hidden_bad_admission",
            "success_rate",
            "success_count",
            "eval_episodes",
            "avg_len",
            "checkpoint",
        ],
    )
    REPORT_OUT.write_text(report(rows, args), encoding="utf-8")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
