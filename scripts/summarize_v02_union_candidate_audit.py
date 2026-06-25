from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(".")
TABLE_DIR = ROOT / "results" / "final_paper" / "tables"
SOURCE_CSV = TABLE_DIR / "v02_action_risk_candidate_support_per_split.csv"
PER_SPLIT_OUT = TABLE_DIR / "v02_union_candidate_support_per_split.csv"
SUMMARY_OUT = TABLE_DIR / "v02_union_candidate_support_summary.csv"
REPORT_OUT = TABLE_DIR / "v02_union_candidate_support_REPORT.md"

UNION_SPECS = {
    "can20": ("positive_nn_top20", "positive_nn_risk_fusion_top20", "positive_nn_risk_union_top20"),
    "can40": ("positive_nn_top40", "positive_nn_risk_fusion_top40", "positive_nn_risk_union_top40"),
    "can80": ("positive_nn_top80", "positive_nn_risk_fusion_top80", "positive_nn_risk_union_top80"),
    "lift_mg": ("positive_nn_top160", "positive_nn_risk_fusion_top160", "positive_nn_risk_union_top160"),
}

SETTING_ORDER = {
    "can20": 0,
    "can40": 1,
    "can80": 2,
    "lift_mg": 3,
}


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


def demo_sort_key(demo_id: str) -> int:
    return int(demo_id.split("_")[-1])


def selected_ids(row: dict[str, str]) -> list[str]:
    return [item for item in row["selected_demo_ids"].split(";") if item]


def ordered_union(*groups: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for demo_id in group:
            if demo_id not in seen:
                seen.add(demo_id)
                out.append(demo_id)
    return out


def fmt(value: float | None) -> str:
    if value is None or math.isnan(value):
        return ""
    return f"{value:.3f}"


def intish(row: dict[str, str], field: str) -> int:
    return int(round(float(row[field])))


def floatish(row: dict[str, str], field: str) -> float:
    return float(row[field]) if row[field] else float("nan")


def summarize_ids(
    *,
    template: dict[str, str],
    candidate_id: str,
    candidate_family: str,
    demo_ids: list[str],
    source_rows: list[dict[str, str]],
) -> dict[str, object]:
    split = json.loads(Path(template["source"]).read_text(encoding="utf-8"))
    positives = set(split["all_positive_ids"])
    unlabeled = set(split["unlabeled_ids"])
    hidden_positive = sum(demo_id in positives for demo_id in demo_ids)
    hidden_bad = len(demo_ids) - hidden_positive
    total_positive = sum(demo_id in positives for demo_id in unlabeled)
    total_bad = len(unlabeled) - total_positive

    def weighted_mean(field: str) -> float:
        values = []
        for row in source_rows:
            value = floatish(row, field)
            weight = intish(row, "selected_unlabeled")
            if not math.isnan(value) and weight > 0:
                values.append((value, weight))
        if not values:
            return float("nan")
        weight_sum = sum(weight for _value, weight in values)
        return sum(value * weight for value, weight in values) / weight_sum

    selected = len(demo_ids)
    return {
        "setting_id": template["setting_id"],
        "setting_label": template["setting_label"],
        "row_role": template["row_role"],
        "split_seed": template["split_seed"],
        "candidate_id": candidate_id,
        "candidate_family": candidate_family,
        "selected_unlabeled": selected,
        "hidden_positive_selected": hidden_positive,
        "hidden_bad_selected": hidden_bad,
        "total_hidden_positive": total_positive,
        "total_hidden_bad": total_bad,
        "support_purity": hidden_positive / selected if selected else 0.0,
        "hidden_positive_recall": hidden_positive / total_positive if total_positive else 0.0,
        "hidden_bad_admission": hidden_bad / total_bad if total_bad else 0.0,
        "selected_contamination": hidden_bad / selected if selected else 0.0,
        "classifier_score_mean": weighted_mean("classifier_score_mean"),
        "action_conflict_risk_mean": weighted_mean("action_conflict_risk_mean"),
        "bad_neighbor_risk_mean": weighted_mean("bad_neighbor_risk_mean"),
        "combined_risk_mean": weighted_mean("combined_risk_mean"),
        "safe_margin_score_mean": weighted_mean("safe_margin_score_mean"),
        "selected_demo_ids": ";".join(demo_ids),
        "source": template["source"],
    }


def copy_compact(row: dict[str, str]) -> dict[str, object]:
    out: dict[str, object] = dict(row)
    for field in [
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
    ]:
        out[field] = intish(row, field)
    for field in [
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "classifier_score_mean",
        "action_conflict_risk_mean",
        "bad_neighbor_risk_mean",
        "combined_risk_mean",
        "safe_margin_score_mean",
    ]:
        out[field] = floatish(row, field)
    return out


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["setting_id"]), str(row["candidate_id"]))].append(row)

    out = []
    for (_setting, _candidate), group in grouped.items():
        first = group[0]
        selected = sum(int(row["selected_unlabeled"]) for row in group)
        hidden_positive = sum(int(row["hidden_positive_selected"]) for row in group)
        hidden_bad = sum(int(row["hidden_bad_selected"]) for row in group)
        total_positive = sum(int(row["total_hidden_positive"]) for row in group)
        total_bad = sum(int(row["total_hidden_bad"]) for row in group)

        def weighted(field: str) -> float:
            values = []
            for row in group:
                value = float(row[field])
                weight = int(row["selected_unlabeled"])
                if not math.isnan(value) and weight > 0:
                    values.append((value, weight))
            if not values:
                return float("nan")
            weight_sum = sum(weight for _value, weight in values)
            return sum(value * weight for value, weight in values) / weight_sum

        recall = hidden_positive / total_positive if total_positive else 0.0
        bad_admission = hidden_bad / total_bad if total_bad else 0.0
        out.append(
            {
                "setting_id": first["setting_id"],
                "setting_label": first["setting_label"],
                "row_role": first["row_role"],
                "candidate_id": first["candidate_id"],
                "candidate_family": first["candidate_family"],
                "split_count": len(group),
                "selected_unlabeled": selected,
                "hidden_positive_selected": hidden_positive,
                "hidden_bad_selected": hidden_bad,
                "total_hidden_positive": total_positive,
                "total_hidden_bad": total_bad,
                "support_purity": hidden_positive / selected if selected else 0.0,
                "hidden_positive_recall": recall,
                "hidden_bad_admission": bad_admission,
                "selected_contamination": hidden_bad / selected if selected else 0.0,
                "classifier_score_mean": weighted("classifier_score_mean"),
                "action_conflict_risk_mean": weighted("action_conflict_risk_mean"),
                "bad_neighbor_risk_mean": weighted("bad_neighbor_risk_mean"),
                "combined_risk_mean": weighted("combined_risk_mean"),
                "safe_margin_score_mean": weighted("safe_margin_score_mean"),
                "audit_oracle_score": recall - bad_admission,
            }
        )
    return sorted(
        out,
        key=lambda row: (
            SETTING_ORDER.get(str(row["setting_id"]), 99),
            str(row["candidate_family"]),
            str(row["candidate_id"]),
        ),
    )


def format_rows(rows: list[dict[str, object]], *, split: bool) -> list[dict[str, str]]:
    fields = [
        "setting_id",
        "setting_label",
        "row_role",
        "candidate_id",
        "candidate_family",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
    ]
    if split:
        fields.insert(3, "split_seed")
    else:
        fields.insert(3, "split_count")
    numeric = [
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "classifier_score_mean",
        "action_conflict_risk_mean",
        "bad_neighbor_risk_mean",
        "combined_risk_mean",
        "safe_margin_score_mean",
    ]
    if not split:
        numeric.append("audit_oracle_score")
    out = []
    for row in rows:
        formatted = {field: str(row[field]) for field in fields}
        for field in numeric:
            formatted[field] = fmt(float(row[field]))
        if split:
            formatted["selected_demo_ids"] = str(row["selected_demo_ids"])
            formatted["source"] = str(row["source"])
        out.append(formatted)
    return out


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row[column] for column in columns) + " |")
    return lines


def report(summary_rows: list[dict[str, object]], split_rows: list[dict[str, object]]) -> str:
    formatted_summary = format_rows(summary_rows, split=False)
    can40_rows = [
        row
        for row in formatted_summary
        if row["setting_id"] == "can40"
        and row["candidate_id"]
        in {
            "positive_nn_top40",
            "positive_nn_risk_fusion_top40",
            "positive_nn_risk_union_top40",
        }
    ]
    promising_splits = [
        row
        for row in format_rows(split_rows, split=True)
        if row["setting_id"] == "can40" and row["candidate_id"] == "positive_nn_risk_union_top40"
    ]
    split22 = next(row for row in promising_splits if row["split_seed"] == "22")
    lines = [
        "# v0.2 Union Candidate Support Audit",
        "",
        "Generated from the staged action-risk candidate support audit without policy training.",
        "The union candidate keeps the positive-only NN support and adds demos from the risk-fusion support.",
        "It tests whether the risk branch should complement, not replace, the strong positive-only baseline.",
        "",
        "## Can 40p/80b Summary",
        "",
        *markdown_table(
            can40_rows,
            [
                "candidate_id",
                "selected_unlabeled",
                "hidden_positive_selected",
                "hidden_bad_selected",
                "support_purity",
                "hidden_positive_recall",
                "hidden_bad_admission",
                "audit_oracle_score",
            ],
        ),
        "",
        "## Can 40p/80b Union Per Split",
        "",
        *markdown_table(
            promising_splits,
            [
                "split_seed",
                "selected_unlabeled",
                "hidden_positive_selected",
                "hidden_bad_selected",
                "support_purity",
                "hidden_positive_recall",
                "hidden_bad_admission",
            ],
        ),
        "",
        "## Endpoint Gate Recommendation",
        "",
        (
            "- The split-22 union is the cleanest first endpoint gate: it recovers "
            f"{split22['hidden_positive_selected']}/{split22['total_hidden_positive']} hidden positives "
            f"while keeping {split22['hidden_bad_selected']} hidden bad demos, matching positive-only NN's bad count."
        ),
        "- This is still only a support gate. Endpoint training must decide whether the added hidden-positive coverage helps or whether positive-only's exact distribution remains better.",
        "- If split 22 fails, do not spend a full three-split endpoint budget on this union family without a new reason.",
        "",
        "## Outputs",
        "",
        f"- `{PER_SPLIT_OUT}`",
        f"- `{SUMMARY_OUT}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    source_rows = read_csv(SOURCE_CSV)
    by_key = {
        (row["setting_id"], int(row["split_seed"]), row["candidate_id"]): row
        for row in source_rows
    }
    out_rows: list[dict[str, object]] = []
    for setting_id, (pos_id, risk_id, union_id) in UNION_SPECS.items():
        seeds = sorted(
            {
                int(row["split_seed"])
                for row in source_rows
                if row["setting_id"] == setting_id and row["candidate_id"] == pos_id
            }
        )
        for seed in seeds:
            pos = by_key[(setting_id, seed, pos_id)]
            risk = by_key[(setting_id, seed, risk_id)]
            out_rows.append(copy_compact(pos))
            out_rows.append(copy_compact(risk))
            union_ids = sorted(
                ordered_union(selected_ids(pos), selected_ids(risk)),
                key=demo_sort_key,
            )
            out_rows.append(
                summarize_ids(
                    template=pos,
                    candidate_id=union_id,
                    candidate_family="union-hybrid",
                    demo_ids=union_ids,
                    source_rows=[pos, risk],
                )
            )

    split_fieldnames = [
        "setting_id",
        "setting_label",
        "row_role",
        "split_seed",
        "candidate_id",
        "candidate_family",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "classifier_score_mean",
        "action_conflict_risk_mean",
        "bad_neighbor_risk_mean",
        "combined_risk_mean",
        "safe_margin_score_mean",
        "selected_demo_ids",
        "source",
    ]
    summary_fieldnames = [
        "setting_id",
        "setting_label",
        "row_role",
        "split_count",
        "candidate_id",
        "candidate_family",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "selected_contamination",
        "classifier_score_mean",
        "action_conflict_risk_mean",
        "bad_neighbor_risk_mean",
        "combined_risk_mean",
        "safe_margin_score_mean",
        "audit_oracle_score",
    ]
    formatted_split = format_rows(out_rows, split=True)
    summary_rows = aggregate(out_rows)
    formatted_summary = format_rows(summary_rows, split=False)
    write_csv(PER_SPLIT_OUT, formatted_split, split_fieldnames)
    write_csv(SUMMARY_OUT, formatted_summary, summary_fieldnames)
    REPORT_OUT.write_text(report(summary_rows, out_rows), encoding="utf-8")
    print(f"wrote {PER_SPLIT_OUT}")
    print(f"wrote {SUMMARY_OUT}")
    print(f"wrote {REPORT_OUT}")


if __name__ == "__main__":
    main()
