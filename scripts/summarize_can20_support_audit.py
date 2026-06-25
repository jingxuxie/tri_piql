from __future__ import annotations

import csv
from pathlib import Path


SPLIT_SEEDS = [11, 22, 33]
HIDDEN_POS_PER_SPLIT = 20
HIDDEN_BAD_PER_SPLIT = 80


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


def read_single_audit(path: Path) -> dict[str, str]:
    rows = read_rows(path)
    if len(rows) != 1:
        raise ValueError(f"expected one audit row in {path}, got {len(rows)}")
    return rows[0]


def audit_item(split_seed: int, method: str, support_rule: str, source: str) -> dict[str, str | int | float]:
    path = (
        Path("results/final_paper/per_seed")
        / f"can_paired_pos20_bad80_split{split_seed}_{method}_policy0"
        / "hidden_label_audit.csv"
    )
    row = read_single_audit(path)
    return {
        "split_seed": split_seed,
        "support_rule": support_rule,
        "selected": int(row["selected_unlabeled"]),
        "hidden_positive": int(row["hidden_positive"]),
        "hidden_bad": int(row["hidden_bad"]),
        "train_demos": int(row["train_demo_count"]),
        "source": source,
    }


def classifier_top20_item(split_seed: int) -> dict[str, str | int | float]:
    path = (
        Path("results/final_paper/score_diagnostics")
        / f"can_paired_pos20_bad80_split{split_seed}_policy0"
        / "precision_at_k.csv"
    )
    row = next(r for r in read_rows(path) if int(r["k"]) == 20)
    selected = int(row["selected_demo_count"])
    hidden_positive = int(row["selected_hidden_positive_demos"])
    hidden_bad = int(row["selected_hidden_bad_demos"])
    return {
        "split_seed": split_seed,
        "support_rule": "classifier_top20",
        "selected": selected,
        "hidden_positive": hidden_positive,
        "hidden_bad": hidden_bad,
        "train_demos": selected + 10,
        "source": "classifier_score_precision_at_k",
    }


def parse_endpoint_report(path: Path) -> tuple[str, str, str]:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| model_epoch_200 |"):
            parts = [part.strip() for part in line.strip("|").split("|")]
            success = parts[1]
            episodes = parts[4]
            successes = str(round(float(success) * int(episodes)))
            return success, successes, episodes
    raise ValueError(f"could not find model_epoch_200 row in {path}")


def endpoint_map() -> dict[tuple[str, int], tuple[str, str, str]]:
    path = Path("results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic.csv")
    mapping = {
        "positive_only_nn_top20": "positive_only_nn_top20",
        "triage_adaptive_masscap": "triage_bc_adaptive_masscap",
        "weighted_full_pool": "weighted_bc_sampler",
    }
    rows = {row["method"]: row for row in read_rows(path)}
    out: dict[tuple[str, int], tuple[str, str, str]] = {}
    for support_rule, method in mapping.items():
        row = rows[method]
        out[(support_rule, 11)] = (row["success"], row["successes"], row["eval_episodes"])
    split22_reports = {
        "positive_only_nn_top20": Path(
            "results/final_paper/per_seed/"
            "can_paired_pos20_bad80_split22_positive_only_nn_policy0/"
            "eval_endpoint_200/REPORT.md"
        ),
        "triage_adaptive_masscap": Path(
            "results/final_paper/per_seed/"
            "can_paired_pos20_bad80_split22_triage_bc_policy0/"
            "eval_endpoint_200/REPORT.md"
        ),
    }
    for support_rule, report_path in split22_reports.items():
        if report_path.exists():
            out[(support_rule, 22)] = parse_endpoint_report(report_path)
    return out


def per_split_row(item: dict[str, str | int | float], endpoints: dict[tuple[str, int], tuple[str, str, str]]) -> dict[str, str]:
    selected = int(item["selected"])
    hidden_positive = int(item["hidden_positive"])
    hidden_bad = int(item["hidden_bad"])
    support_rule = str(item["support_rule"])
    split_seed = int(item["split_seed"])
    endpoint = endpoints.get((support_rule, split_seed))
    return {
        "split_seed": str(split_seed),
        "support_rule": support_rule,
        "train_demos": str(item["train_demos"]),
        "selected_unlabeled": str(selected),
        "hidden_positive": str(hidden_positive),
        "hidden_bad": str(hidden_bad),
        "purity": fmt(hidden_positive / selected if selected else 0.0),
        "hidden_positive_recall": fmt(hidden_positive / HIDDEN_POS_PER_SPLIT),
        "hidden_bad_admission": fmt(hidden_bad / HIDDEN_BAD_PER_SPLIT),
        "endpoint_success": endpoint[0] if endpoint else "",
        "endpoint_successes": endpoint[1] if endpoint else "",
        "endpoint_episodes": endpoint[2] if endpoint else "",
        "source": str(item["source"]),
    }


def aggregate_row(items: list[dict[str, str | int | float]], endpoints: dict[tuple[str, int], tuple[str, str, str]]) -> dict[str, str]:
    selected = sum(int(item["selected"]) for item in items)
    hidden_positive = sum(int(item["hidden_positive"]) for item in items)
    hidden_bad = sum(int(item["hidden_bad"]) for item in items)
    support_rule = str(items[0]["support_rule"])
    endpoint_items = [
        endpoints[(support_rule, int(item["split_seed"]))]
        for item in items
        if (support_rule, int(item["split_seed"])) in endpoints
    ]
    endpoint_successes = sum(int(endpoint[1]) for endpoint in endpoint_items)
    endpoint_episodes = sum(int(endpoint[2]) for endpoint in endpoint_items)
    return {
        "support_rule": support_rule,
        "num_splits": str(len(items)),
        "mean_train_demos": fmt(sum(int(item["train_demos"]) for item in items) / len(items)),
        "mean_selected_unlabeled": fmt(selected / len(items)),
        "total_hidden_positive": str(hidden_positive),
        "total_hidden_bad": str(hidden_bad),
        "purity": fmt(hidden_positive / selected if selected else 0.0),
        "hidden_positive_recall": fmt(hidden_positive / (HIDDEN_POS_PER_SPLIT * len(items))),
        "hidden_bad_admission": fmt(hidden_bad / (HIDDEN_BAD_PER_SPLIT * len(items))),
        "selected_contamination": fmt(hidden_bad / selected if selected else 0.0),
        "endpoint_num_splits": str(len(endpoint_items)),
        "endpoint_success": fmt(endpoint_successes / endpoint_episodes) if endpoint_episodes else "",
        "endpoint_successes": str(endpoint_successes) if endpoint_episodes else "",
        "endpoint_episodes": str(endpoint_episodes) if endpoint_episodes else "",
        "source": str(items[0]["source"]),
    }


def table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[col] for col in columns) + " |")
    return lines


def main() -> None:
    out_dir = Path("results/final_paper/ablations")
    endpoints = endpoint_map()
    items: list[dict[str, str | int | float]] = []
    for split_seed in SPLIT_SEEDS:
        items.extend(
            [
                audit_item(
                    split_seed,
                    "triage_bc",
                    "triage_adaptive_masscap",
                    "router_v2_adaptive_masscap",
                ),
                audit_item(
                    split_seed,
                    "positive_only_nn",
                    "positive_only_nn_top20",
                    "positive_only_nearest_neighbor",
                ),
                audit_item(
                    split_seed,
                    "weighted_bc",
                    "weighted_full_pool",
                    "weighted_bc_sampler",
                ),
                classifier_top20_item(split_seed),
            ]
        )

    per_split_rows = [per_split_row(item, endpoints) for item in items]
    aggregate_rows = [
        aggregate_row([item for item in items if item["support_rule"] == support_rule], endpoints)
        for support_rule in [
            "classifier_top20",
            "triage_adaptive_masscap",
            "positive_only_nn_top20",
            "weighted_full_pool",
        ]
    ]

    out_csv = out_dir / "can_paired_pos20_bad80_support_audit_3split.csv"
    out_per_split = out_dir / "can_paired_pos20_bad80_support_audit_3split_per_split.csv"
    out_report = out_dir / "can_paired_pos20_bad80_support_audit_3split_REPORT.md"
    write_csv(out_csv, aggregate_rows)
    write_csv(out_per_split, per_split_rows)

    support_table = table(
        aggregate_rows,
        [
            "support_rule",
            "mean_selected_unlabeled",
            "purity",
            "hidden_positive_recall",
            "hidden_bad_admission",
            "endpoint_success",
        ],
    )
    split_table = table(
        [
            row
            for row in per_split_rows
            if row["support_rule"] in {"triage_adaptive_masscap", "positive_only_nn_top20"}
        ],
        [
            "split_seed",
            "support_rule",
            "selected_unlabeled",
            "hidden_positive",
            "hidden_bad",
            "purity",
            "hidden_positive_recall",
            "endpoint_success",
        ],
    )
    report = [
        "# Can 20p/80b Three-Split Support Audit",
        "",
        "This diagnostic extends the frozen Can Paired 20 hidden-positive / 80 hidden-bad split-11 endpoint row with split-seed 22 and 33 support/setup audits.",
        "It also includes a bounded split-22 endpoint comparison for TRIAGE-BC and positive-only NN top20.",
        "",
        "## Aggregate Support",
        "",
        *support_table,
        "",
        "## TRIAGE Versus Positive-Only By Split",
        "",
        *split_table,
        "",
        "## Interpretation",
        "",
        "- TRIAGE-BC / adaptive masscap recovers more hidden positives than positive-only NN top20 across the three splits (`54/60` versus `49/60`), but admits far more hidden-bad demos (`69/240` versus `11/240`).",
        "- The split behavior is unstable: TRIAGE uses broad contaminated support on splits 11 and 22, then falls back to a cleaner top20-style support on split 33.",
        "- Positive-only NN top20 is cleaner on aggregate and on splits 11/22; split 33 is the case where TRIAGE also becomes clean, but with lower hidden-positive coverage.",
        "- Positive-only NN top20 beats TRIAGE-BC on both completed endpoint splits: `54/100` pooled versus `46/100` pooled.",
        "- Weighted BC has full hidden-positive recall but also full hidden-bad admission, matching the split-11 endpoint failure mode (`18/50`). Weighted split-22 endpoint training was not run.",
        "- The useful paper claim remains a precision/coverage claim, not a bad-label policy-benefit claim: bad labels help calibrate a score, but the current Can 20/80 converter is not clearly better than strong no-bad retrieval.",
        "",
        "## Artifacts",
        "",
        f"- Aggregate CSV: `{out_csv}`",
        f"- Per-split CSV: `{out_per_split}`",
        "- Split-11 endpoint diagnostic: `results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic_REPORT.md`",
        "- Split-22 endpoint reports: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_{positive_only_nn,triage_bc}_policy0/eval_endpoint_200/REPORT.md`",
        "- Source runs: `results/final_paper/per_seed/can_paired_pos20_bad80_split{11,22,33}_*_policy0/`",
        "- Source score diagnostics: `results/final_paper/score_diagnostics/can_paired_pos20_bad80_split{11,22,33}_policy0/`",
    ]
    out_report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {out_report}")


if __name__ == "__main__":
    main()
