from __future__ import annotations

import csv
from pathlib import Path


SPLIT_SEEDS = [11, 22, 33]
HIDDEN_POS_PER_SPLIT = 40
HIDDEN_BAD_PER_SPLIT = 80
TOP_KS = [10, 20, 40, 60, 80]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def aggregate_support(rows: list[dict[str, float | str]]) -> dict[str, str]:
    selected = sum(float(row["selected"]) for row in rows)
    hidden_pos = sum(float(row["hidden_positive"]) for row in rows)
    hidden_bad = sum(float(row["hidden_bad"]) for row in rows)
    hidden_pos_total = HIDDEN_POS_PER_SPLIT * len(rows)
    hidden_bad_total = HIDDEN_BAD_PER_SPLIT * len(rows)
    purity = hidden_pos / selected if selected else 0.0
    recall = hidden_pos / hidden_pos_total if hidden_pos_total else 0.0
    bad_admission = hidden_bad / hidden_bad_total if hidden_bad_total else 0.0
    contamination = hidden_bad / selected if selected else 0.0
    return {
        "support_rule": str(rows[0]["support_rule"]),
        "num_splits": str(len(rows)),
        "mean_selected": fmt(selected / len(rows)),
        "total_hidden_positive": str(int(hidden_pos)),
        "total_hidden_bad": str(int(hidden_bad)),
        "purity": fmt(purity),
        "hidden_positive_recall": fmt(recall),
        "hidden_bad_admission": fmt(bad_admission),
        "selected_contamination": fmt(contamination),
        "endpoint_success": "",
        "endpoint_successes": "",
        "endpoint_episodes": "",
        "source": str(rows[0]["source"]),
    }


def main() -> None:
    out_dir = Path("results/final_paper/ablations")
    score_root = Path("results/final_paper/score_diagnostics")
    endpoint_path = Path("results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv")
    endpoint_rows = read_rows(endpoint_path)
    endpoint_by_split = {
        int(row["split_seed"]): row
        for row in endpoint_rows
        if row["split_seed"] != "aggregate"
    }
    endpoint_aggregate = next(row for row in endpoint_rows if row["split_seed"] == "aggregate")

    support_items: list[dict[str, float | str]] = []
    for split_seed in SPLIT_SEEDS:
        diag_dir = score_root / f"can_paired_pos40_bad80_split{split_seed}_policy0"
        for row in read_rows(diag_dir / "precision_at_k.csv"):
            k = int(row["k"])
            if k not in TOP_KS:
                continue
            support_items.append(
                {
                    "support_rule": f"classifier_top{k}",
                    "split_seed": split_seed,
                    "selected": float(row["selected_demo_count"]),
                    "hidden_positive": float(row["selected_hidden_positive_demos"]),
                    "hidden_bad": float(row["selected_hidden_bad_demos"]),
                    "source": "classifier_score_precision_at_k",
                }
            )
        selection = read_rows(diag_dir / "selection_rules.csv")
        adaptive = next(row for row in selection if row["threshold_name"] == "adaptive_masscap")
        support_items.append(
            {
                "support_rule": "triage_adaptive_masscap",
                "split_seed": split_seed,
                "selected": float(adaptive["selected_demo_count"]),
                "hidden_positive": float(adaptive["selected_hidden_positive_demos"]),
                "hidden_bad": float(adaptive["selected_hidden_bad_demos"]),
                "source": "router_v2_adaptive_masscap",
            }
        )
        endpoint = endpoint_by_split[split_seed]
        support_items.extend(
            [
                {
                    "support_rule": "weighted_full_pool",
                    "split_seed": split_seed,
                    "selected": float(endpoint["weighted_selected_unlabeled"]),
                    "hidden_positive": float(endpoint["weighted_hidden_positive"]),
                    "hidden_bad": float(endpoint["weighted_hidden_bad"]),
                    "source": "weighted_bc_sampler",
                },
                {
                    "support_rule": "positive_only_nn_top40",
                    "split_seed": split_seed,
                    "selected": float(endpoint["positive_only_nn_selected_unlabeled"]),
                    "hidden_positive": float(endpoint["positive_only_nn_hidden_positive"]),
                    "hidden_bad": float(endpoint["positive_only_nn_hidden_bad"]),
                    "source": "positive_only_nearest_neighbor",
                },
            ]
        )

    per_split_rows = []
    for item in support_items:
        selected = float(item["selected"])
        hidden_pos = float(item["hidden_positive"])
        hidden_bad = float(item["hidden_bad"])
        per_split_rows.append(
            {
                "split_seed": str(item["split_seed"]),
                "support_rule": str(item["support_rule"]),
                "selected": str(int(selected)),
                "hidden_positive": str(int(hidden_pos)),
                "hidden_bad": str(int(hidden_bad)),
                "purity": fmt(hidden_pos / selected if selected else 0.0),
                "hidden_positive_recall": fmt(hidden_pos / HIDDEN_POS_PER_SPLIT),
                "hidden_bad_admission": fmt(hidden_bad / HIDDEN_BAD_PER_SPLIT),
                "source": str(item["source"]),
            }
        )

    aggregate_rows = []
    for support_rule in [
        *(f"classifier_top{k}" for k in TOP_KS),
        "triage_adaptive_masscap",
        "weighted_full_pool",
        "positive_only_nn_top40",
    ]:
        selected = [row for row in support_items if row["support_rule"] == support_rule]
        aggregate_rows.append(aggregate_support(selected))

    endpoint_map = {
        "triage_adaptive_masscap": (
            endpoint_aggregate["triage_success_rate"],
            endpoint_aggregate["triage_successes"],
            endpoint_aggregate["eval_episodes"],
        ),
        "weighted_full_pool": (
            endpoint_aggregate["weighted_success_rate"],
            endpoint_aggregate["weighted_successes"],
            endpoint_aggregate["eval_episodes"],
        ),
        "positive_only_nn_top40": (
            endpoint_aggregate["positive_only_nn_success_rate"],
            endpoint_aggregate["positive_only_nn_successes"],
            endpoint_aggregate["eval_episodes"],
        ),
    }
    for row in aggregate_rows:
        if row["support_rule"] in endpoint_map:
            success, successes, episodes = endpoint_map[row["support_rule"]]
            row["endpoint_success"] = success
            row["endpoint_successes"] = successes
            row["endpoint_episodes"] = episodes

    out_csv = out_dir / "can40_score_support_tradeoff.csv"
    out_per_split = out_dir / "can40_score_support_tradeoff_per_split.csv"
    out_report = out_dir / "can40_score_support_tradeoff_REPORT.md"
    write_csv(out_csv, aggregate_rows)
    write_csv(out_per_split, per_split_rows)

    def table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
        lines = [
            "| " + " | ".join(columns) + " |",
            "| " + " | ".join(["---"] * len(columns)) + " |",
        ]
        for row in rows:
            lines.append("| " + " | ".join(row[col] for col in columns) + " |")
        return lines

    support_table = table(
        aggregate_rows,
        [
            "support_rule",
            "mean_selected",
            "purity",
            "hidden_positive_recall",
            "hidden_bad_admission",
            "endpoint_success",
        ],
    )
    report = [
        "# Can 40p/80b Score-Support Tradeoff",
        "",
        "This analysis aggregates the frozen Can Paired 40 hidden-positive / 80 hidden-bad split seeds 11, 22, and 33.",
        "It reuses existing score diagnostics and endpoint evaluations; no new policy training is included.",
        "",
        "## Aggregate Support Sweep",
        "",
        *support_table,
        "",
        "## Interpretation",
        "",
        "- Classifier-score top-k support traces the precision/coverage curve: small top-k rules are purer but under-cover hidden positives, while broader top-k rules recover more positives and admit more hidden bad demos.",
        "- TRIAGE-BC adaptive masscap recovers `110/120` hidden-positive demos across the three splits, but it also admits `80/240` hidden-bad demos. Its endpoint success is `99/150`.",
        "- Positive-only NN top40 recovers slightly fewer hidden positives (`106/120`) but admits far fewer hidden-bad demos (`14/240`), and it has the best non-oracle endpoint success on this matrix (`108/150`).",
        "- Weighted BC has full hidden-positive recall but also full hidden-bad admission, reaching `90/150` endpoint successes.",
        "- This supports the paper's precision/coverage framing but not a bad-label benefit claim on Can 40p/80b: the bad-aware converter improves over weighted and all-demo cloning, yet the no-bad positive-only support point sits on a better precision/coverage frontier.",
        "",
        "## Artifacts",
        "",
        f"- Aggregate CSV: `{out_csv}`",
        f"- Per-split CSV: `{out_per_split}`",
        "- Source endpoint table: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary.csv`",
        "- Source score diagnostics: `results/final_paper/score_diagnostics/can_paired_pos40_bad80_split{11,22,33}_policy0/`",
    ]
    out_report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {out_report}")


if __name__ == "__main__":
    main()
