#!/usr/bin/env python3
"""Summarize the frozen Candidate F Can 40p/80b matrix."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_breakthrough"
FINAL = ROOT / "results" / "final_paper_v02"
SPLITS = [101, 202, 303, 404, 505]
N_EPISODES = 50


FROZEN_COMPONENTS = {
    101: (
        "weighted_anchor",
        OUT / "candidate_f_frozen_split101_weighted_sampler_anchor_eval50" / "episode_metrics.csv",
    ),
    202: (
        "candidate_e_gate",
        OUT / "candidate_f_frozen_split202_candidate_e_gate_eval50" / "episode_metrics.csv",
    ),
    303: (
        "candidate_e_gate",
        OUT / "candidate_f_frozen_split303_candidate_e_gate_eval50" / "episode_metrics.csv",
    ),
    404: (
        "candidate_e_gate",
        OUT / "candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng" / "episode_metrics.csv",
    ),
    505: (
        "candidate_e_gate",
        OUT / "candidate_e_initial_posdist_gate_weighted_split505_eval50_isolated_rng" / "episode_metrics.csv",
    ),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def endpoint_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if rows and "checkpoint" in rows[0]:
        checkpoints = {row["checkpoint"] for row in rows}
        if len(checkpoints) > 1:
            filtered = [row for row in rows if "model_epoch_200" in row["checkpoint"]]
            if filtered:
                return filtered
    return rows


def success_count(path: Path, n: int = N_EPISODES) -> int:
    rows = endpoint_rows(read_csv(path))[:n]
    if len(rows) != n:
        raise ValueError(f"{path}: expected {n} rows, found {len(rows)}")
    return sum(int(float(row["success"])) for row in rows)


def gate_count(path: Path) -> int | str:
    rows = read_csv(path)
    if not rows or "initial_gate_open" not in rows[0]:
        return ""
    return sum(int(row.get("initial_gate_open", "0")) for row in rows[:N_EPISODES])


def baseline_csv(split: int, method: str) -> Path:
    return (
        FINAL
        / "per_seed"
        / f"can_paired_pos40_bad80_split{split}_{method}_policy0"
        / "eval"
        / "episode_metrics.csv"
    )


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows: list[dict[str, object]] = []
    for split in SPLITS:
        source, path = FROZEN_COMPONENTS[split]
        positive = success_count(baseline_csv(split, "positive_only_nn"))
        weighted = success_count(baseline_csv(split, "weighted_bc"))
        triage = success_count(baseline_csv(split, "triage_bc"))
        candidate_f = success_count(path)
        best_baseline = max(positive, weighted, triage)
        rows.append(
            {
                "split": split,
                "candidate_f_source": source,
                "positive": positive,
                "weighted": weighted,
                "triage": triage,
                "best_baseline": best_baseline,
                "candidate_f": candidate_f,
                "delta_vs_best_baseline": candidate_f - best_baseline,
                "gate_opens": gate_count(path),
                "artifact": str(path.parent.relative_to(ROOT)),
            }
        )

    total = {
        "split": "total",
        "candidate_f_source": "",
        "positive": sum(int(row["positive"]) for row in rows),
        "weighted": sum(int(row["weighted"]) for row in rows),
        "triage": sum(int(row["triage"]) for row in rows),
        "best_baseline": sum(int(row["best_baseline"]) for row in rows),
        "candidate_f": sum(int(row["candidate_f"]) for row in rows),
        "delta_vs_best_baseline": sum(int(row["candidate_f"]) for row in rows)
        - sum(int(row["best_baseline"]) for row in rows),
        "gate_opens": sum(int(row["gate_opens"]) for row in rows if row["gate_opens"] != ""),
        "artifact": "",
    }
    rows_with_total = [*rows, total]

    csv_path = OUT / "candidate_f_frozen_matrix_summary.csv"
    fieldnames = [
        "split",
        "candidate_f_source",
        "positive",
        "weighted",
        "triage",
        "best_baseline",
        "candidate_f",
        "delta_vs_best_baseline",
        "gate_opens",
        "artifact",
    ]
    write_csv(csv_path, rows_with_total, fieldnames)

    report_path = OUT / "candidate_f_frozen_matrix_REPORT.md"
    lines = [
        "# Candidate F Frozen Matrix",
        "",
        "Candidate F uses the endpoint-free calibrated anchor rule from",
        "`candidate_f_anchor_calibration_screen_REPORT.md`: if the positive-NN",
        "selected support has a classifier-probability tail below",
        "`0.5 * unlabeled_prob_mean`, use weighted BC as the split-level anchor;",
        "otherwise use the isolated-RNG Candidate E initial-distance gate.",
        "",
        "| split | source | positive | weighted | triage | best base | cand F | delta | gate opens | artifact |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows_with_total:
        denom = 250 if row["split"] == "total" else 50
        lines.append(
            "| {split} | {candidate_f_source} | {positive}/{denom} | "
            "{weighted}/{denom} | {triage}/{denom} | {best_baseline}/{denom} | "
            "{candidate_f}/{denom} | {delta:+d} | {gate_opens} | {artifact} |".format(
                split=row["split"],
                candidate_f_source=row["candidate_f_source"],
                positive=row["positive"],
                weighted=row["weighted"],
                triage=row["triage"],
                best_baseline=row["best_baseline"],
                candidate_f=row["candidate_f"],
                denom=denom,
                delta=int(row["delta_vs_best_baseline"]),
                gate_opens=row["gate_opens"],
                artifact=row["artifact"],
            )
        )

    lines.extend(
        [
            "",
            "## Read",
            "",
            "- Frozen Candidate F reaches `198/250`, versus positive-only `174/250`,",
            "  weighted `158/250`, triage `171/250`, and the per-split baseline",
            "  oracle `192/250`.",
            "- It improves over the best completed baseline on split 404 by `+7/50`,",
            "  loses split 505 by `-1/50`, and ties the best baseline on splits",
            "  101/202/303.",
            "- The incorrect root `last.pth` split-101 diagnostic is intentionally",
            "  excluded; the frozen split-101 row uses the weighted-sampler",
            "  `model_epoch_200.pth` checkpoint that produced the paper baseline.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{csv_path.relative_to(ROOT)}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
