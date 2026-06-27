from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path


DEFAULT_ROOT = Path("results/final_paper_v02")
DEFAULT_OUT_DIR = DEFAULT_ROOT / "tables"


ROW_ORDER = [
    "always_positive_only_nn",
    "always_weighted_bc",
    "always_hard_support",
    "v01_triage_bc",
    "v02_router",
    "oracle_branch_selector",
]

ROW_LABELS = {
    "always_positive_only_nn": "Always positive-only NN",
    "always_weighted_bc": "Always weighted BC",
    "always_hard_support": "Always hard support",
    "v01_triage_bc": "v0.1 TRIAGE-BC",
    "v02_router": "v0.2 router",
    "oracle_branch_selector": "Oracle branch selector",
}

REGIME_ORDER = [
    "can40_fresh",
    "lift_mg_fresh",
    "hard_negative_can",
    "coverage_shift_can",
    "prefix_positive_can",
    "can_mg_stress",
]

REGIME_LABELS = {
    "can40_fresh": "Can 40p/80b",
    "lift_mg_fresh": "Lift MG",
    "hard_negative_can": "Hard-negative Can",
    "coverage_shift_can": "Coverage-shift Can",
    "prefix_positive_can": "Prefix-positive Can",
    "can_mg_stress": "Can MG abstention/stress",
}

BRANCH_SELECTION_ROLES = {"v02_selected", "strong_baseline", "v01_method"}


@dataclass(frozen=True)
class Cell:
    row_id: str
    regime_id: str
    status: str
    successes: int | None = None
    episodes: int | None = None
    success_rate: float | None = None
    oracle_successes: int | None = None
    oracle_episodes: int | None = None
    oracle_success_rate: float | None = None
    source_method: str = ""
    note: str = ""

    @property
    def regret_successes(self) -> int | None:
        if self.successes is None or self.oracle_successes is None:
            return None
        return self.oracle_successes - self.successes

    @property
    def regret_rate(self) -> float | None:
        if self.success_rate is None or self.oracle_success_rate is None:
            return None
        return self.oracle_success_rate - self.success_rate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
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


def fmt_rate(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.3f}"


def row_by_method(rows: list[dict[str, str]], method_id: str) -> list[dict[str, str]]:
    return [row for row in rows if row["method_id"] == method_id]


def branch_selection_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["method_role"] in BRANCH_SELECTION_ROLES]


def summed_cell(
    *,
    row_id: str,
    regime_id: str,
    rows: list[dict[str, str]],
    source_method: str,
    oracle_successes: int,
    oracle_episodes: int,
    status: str = "complete",
    note: str = "",
) -> Cell:
    successes = sum(int(row["success_count"]) for row in rows)
    episodes = sum(int(row["eval_episodes"]) for row in rows)
    return Cell(
        row_id=row_id,
        regime_id=regime_id,
        status=status,
        successes=successes,
        episodes=episodes,
        success_rate=successes / episodes,
        oracle_successes=oracle_successes,
        oracle_episodes=oracle_episodes,
        oracle_success_rate=oracle_successes / oracle_episodes,
        source_method=source_method,
        note=note,
    )


def oracle_by_split(
    rows: list[dict[str, str]],
    split_key: str,
    success_key: str,
    episode_key: str,
) -> tuple[int, int]:
    successes = 0
    episodes = 0
    for split_seed in sorted({row[split_key] for row in rows}):
        split_rows = [row for row in rows if row[split_key] == split_seed]
        best = max(split_rows, key=lambda row: int(row[success_key]))
        successes += int(best[success_key])
        episodes += int(best[episode_key])
    return successes, episodes


def oracle_by_split_subset(
    rows: list[dict[str, str]],
    split_key: str,
    success_key: str,
    episode_key: str,
    split_values: set[str],
) -> tuple[int, int]:
    return oracle_by_split(
        [row for row in rows if row[split_key] in split_values],
        split_key,
        success_key,
        episode_key,
    )


def completed_split_note(rows: list[dict[str, str]], all_rows: list[dict[str, str]], split_key: str) -> str:
    completed = sorted({row[split_key] for row in rows})
    all_splits = sorted({row[split_key] for row in all_rows})
    missing = [split for split in all_splits if split not in completed]
    completed_text = ", ".join(completed)
    if missing:
        return f"Completed split seeds {completed_text}; A3 still missing {', '.join(missing)}."
    return f"Completed all current split seeds: {completed_text}."


def partial_or_complete_cell(
    *,
    row_id: str,
    regime_id: str,
    rows: list[dict[str, str]],
    all_rows: list[dict[str, str]],
    split_key: str,
    source_method: str,
    missing_note: str,
    note_prefix: str = "",
) -> Cell:
    if not rows:
        oracle_successes, oracle_episodes = oracle_by_split(all_rows, split_key, "success_count", "eval_episodes")
        return Cell(
            row_id=row_id,
            regime_id=regime_id,
            status="not_run",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            note=missing_note,
        )
    split_values = {row[split_key] for row in rows}
    oracle_successes, oracle_episodes = oracle_by_split_subset(
        all_rows,
        split_key,
        "success_count",
        "eval_episodes",
        split_values,
    )
    note = completed_split_note(rows, all_rows, split_key)
    if note_prefix:
        note = f"{note_prefix} {note}"
    status = "partial" if len(split_values) < len({row[split_key] for row in all_rows}) else "complete"
    return summed_cell(
        row_id=row_id,
        regime_id=regime_id,
        rows=rows,
        source_method=source_method,
        oracle_successes=oracle_successes,
        oracle_episodes=oracle_episodes,
        status=status,
        note=note,
    )


def endpoint_cells_from_fresh_can(root: Path) -> list[Cell]:
    rows = read_csv(root / "tables" / "v02_fresh_can_endpoint_summary.csv")
    branch_rows = branch_selection_rows(rows)
    oracle_successes, oracle_episodes = oracle_by_split(
        branch_rows, "split_seed", "success_count", "eval_episodes"
    )
    triage_rows = row_by_method(branch_rows, "triage_bc")
    cells = [
        summed_cell(
            row_id="always_positive_only_nn",
            regime_id="can40_fresh",
            rows=row_by_method(branch_rows, "positive_only_nn"),
            source_method="positive_only_nn",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
        ),
        summed_cell(
            row_id="always_weighted_bc",
            regime_id="can40_fresh",
            rows=row_by_method(branch_rows, "weighted_bc"),
            source_method="weighted_bc",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
        ),
        summed_cell(
            row_id="always_hard_support",
            regime_id="can40_fresh",
            rows=row_by_method(branch_rows, "positive_nn_risk_union_top40"),
            source_method="positive_nn_risk_union_top40",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
        ),
        partial_or_complete_cell(
            row_id="v01_triage_bc",
            regime_id="can40_fresh",
            rows=triage_rows,
            all_rows=branch_rows,
            split_key="split_seed",
            source_method="triage_bc",
            missing_note="A3 baseline completion needed for v0.1 on fresh split seeds 101/202/303/404/505.",
        ),
        summed_cell(
            row_id="v02_router",
            regime_id="can40_fresh",
            rows=[row for row in branch_rows if row["method_role"] == "v02_selected"],
            source_method="hard_risk_union",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            note="Frozen v0.2 selects hard union on all five Can 40 fresh splits.",
        ),
        Cell(
            row_id="oracle_branch_selector",
            regime_id="can40_fresh",
            status="oracle",
            successes=oracle_successes,
            episodes=oracle_episodes,
            success_rate=oracle_successes / oracle_episodes,
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            source_method="per_split_best_completed_branch",
            note="Audit-only selector over completed branch-selection rows; optional mixed-log and oracle controls are excluded.",
        ),
    ]
    return cells


def endpoint_cells_from_fresh_lift(root: Path) -> list[Cell]:
    rows = read_csv(root / "tables" / "v02_fresh_lift_endpoint_summary.csv")
    branch_rows = branch_selection_rows(rows)
    oracle_successes, oracle_episodes = oracle_by_split(
        branch_rows, "split_seed", "success_count", "eval_episodes"
    )
    triage_rows = row_by_method(branch_rows, "triage_bc")
    cells = [
        summed_cell(
            row_id="always_positive_only_nn",
            regime_id="lift_mg_fresh",
            rows=row_by_method(branch_rows, "positive_only_nn"),
            source_method="positive_only_nn",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
        ),
        summed_cell(
            row_id="always_weighted_bc",
            regime_id="lift_mg_fresh",
            rows=row_by_method(branch_rows, "weighted_bc"),
            source_method="weighted_bc",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
        ),
        partial_or_complete_cell(
            row_id="always_hard_support",
            regime_id="lift_mg_fresh",
            rows=triage_rows,
            all_rows=branch_rows,
            split_key="split_seed",
            source_method="triage_bc",
            missing_note="Hard-support branch not completed for the five fresh Lift splits; A3 should fill v0.1/hard-support baselines if needed.",
            note_prefix="Fresh hard-support proxy uses the v0.1 hard pos-min TRIAGE branch.",
        ),
        partial_or_complete_cell(
            row_id="v01_triage_bc",
            regime_id="lift_mg_fresh",
            rows=triage_rows,
            all_rows=branch_rows,
            split_key="split_seed",
            source_method="triage_bc",
            missing_note="A3 baseline completion needed for v0.1 on fresh split seeds 101/202/303/404/505.",
        ),
        summed_cell(
            row_id="v02_router",
            regime_id="lift_mg_fresh",
            rows=[row for row in branch_rows if row["method_role"] == "v02_selected"],
            source_method="soft_weighted",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            note="Frozen v0.2 selects weighted BC on all five Lift MG fresh splits.",
        ),
        Cell(
            row_id="oracle_branch_selector",
            regime_id="lift_mg_fresh",
            status="oracle",
            successes=oracle_successes,
            episodes=oracle_episodes,
            success_rate=oracle_successes / oracle_episodes,
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            source_method="per_split_best_completed_branch",
            note="Audit-only selector over completed branch-selection rows; optional mixed-log and oracle controls are excluded.",
        ),
    ]
    return cells


def generated_can_cells(
    *,
    path: Path,
    regime_id: str,
    positive_method: str,
    hard_method: str,
) -> list[Cell]:
    rows = read_csv(path)
    oracle_successes, oracle_episodes = oracle_by_split(rows, "split_seed", "success_count", "eval_episodes")
    cells = [
        summed_cell(
            row_id="always_positive_only_nn",
            regime_id=regime_id,
            rows=[row for row in rows if row["candidate_id"] == positive_method],
            source_method=positive_method,
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
        ),
        Cell(
            row_id="always_weighted_bc",
            regime_id=regime_id,
            status="not_applicable",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            note="Weighted BC was not part of this matched generated-regime endpoint probe.",
        ),
        summed_cell(
            row_id="always_hard_support",
            regime_id=regime_id,
            rows=[row for row in rows if row["candidate_id"] == hard_method],
            source_method=hard_method,
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            note="Bad-aware hard-support probe branch.",
        ),
        Cell(
            row_id="v01_triage_bc",
            regime_id=regime_id,
            status="not_applicable",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            note="v0.1 frozen router was not evaluated for this generated-regime endpoint probe.",
        ),
        Cell(
            row_id="v02_router",
            regime_id=regime_id,
            status="not_applicable",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            note="v0.2 router rule was not frozen/evaluated for this generated-regime endpoint probe.",
        ),
        Cell(
            row_id="oracle_branch_selector",
            regime_id=regime_id,
            status="oracle",
            successes=oracle_successes,
            episodes=oracle_episodes,
            success_rate=oracle_successes / oracle_episodes,
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            source_method="per_split_best_completed_probe_branch",
            note="Audit-only selector over completed positive-only and bad-aware probe branches.",
        ),
    ]
    return cells


def prefix_positive_cells(path: Path) -> list[Cell]:
    rows = read_csv(path)
    by_method = {row["candidate_id"]: row for row in rows}
    positive = by_method["prefix_state_action_nn_top80"]
    hard = by_method["prefix_bad_aware_state_top80"]
    oracle_successes = max(int(positive["success_count"]), int(hard["success_count"]))
    oracle_episodes = int(positive["eval_episodes"])
    return [
        Cell(
            row_id="always_positive_only_nn",
            regime_id="prefix_positive_can",
            status="complete",
            successes=int(positive["success_count"]),
            episodes=int(positive["eval_episodes"]),
            success_rate=float(positive["success_rate"]),
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            source_method="prefix_state_action_nn_top80",
        ),
        Cell(
            row_id="always_weighted_bc",
            regime_id="prefix_positive_can",
            status="not_applicable",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            note="Weighted BC was not part of this matched generated-regime endpoint probe.",
        ),
        Cell(
            row_id="always_hard_support",
            regime_id="prefix_positive_can",
            status="complete",
            successes=int(hard["success_count"]),
            episodes=int(hard["eval_episodes"]),
            success_rate=float(hard["success_rate"]),
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            source_method="prefix_bad_aware_state_top80",
            note="Bad-aware hard-support probe branch.",
        ),
        Cell(
            row_id="v01_triage_bc",
            regime_id="prefix_positive_can",
            status="not_applicable",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            note="v0.1 frozen router was not evaluated for this generated-regime endpoint probe.",
        ),
        Cell(
            row_id="v02_router",
            regime_id="prefix_positive_can",
            status="not_applicable",
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            note="v0.2 router rule was not frozen/evaluated for this generated-regime endpoint probe.",
        ),
        Cell(
            row_id="oracle_branch_selector",
            regime_id="prefix_positive_can",
            status="oracle",
            successes=oracle_successes,
            episodes=oracle_episodes,
            success_rate=oracle_successes / oracle_episodes,
            oracle_successes=oracle_successes,
            oracle_episodes=oracle_episodes,
            oracle_success_rate=oracle_successes / oracle_episodes,
            source_method="best_completed_probe_branch",
            note="Audit-only selector over completed positive-only and bad-aware probe branches.",
        ),
    ]


def can_mg_cells(path: Path) -> list[Cell]:
    rows = [row for row in read_csv(path) if row["split"] == "can_mg_original"]
    by_method = {row["method"]: row for row in rows}
    oracle_rate = max(float(row["rollout_success_20k"]) for row in rows)
    return [
        Cell(
            row_id="always_positive_only_nn",
            regime_id="can_mg_stress",
            status="not_run",
            oracle_success_rate=oracle_rate,
            note="No matched positive-only NN endpoint row is staged for the Can MG stress artifact.",
        ),
        Cell(
            row_id="always_weighted_bc",
            regime_id="can_mg_stress",
            status="rate_only",
            success_rate=float(by_method["weighted"]["rollout_success_20k"]),
            oracle_success_rate=oracle_rate,
            source_method="weighted",
            note="Rate-only reused final-20k Can MG stress diagnostic; episode counts are not staged in this CSV.",
        ),
        Cell(
            row_id="always_hard_support",
            regime_id="can_mg_stress",
            status="rate_only",
            success_rate=float(by_method["posp10"]["rollout_success_20k"]),
            oracle_success_rate=oracle_rate,
            source_method="posp10",
            note="Rate-only hard-support stress branch; episode counts are not staged in this CSV.",
        ),
        Cell(
            row_id="v01_triage_bc",
            regime_id="can_mg_stress",
            status="not_run",
            oracle_success_rate=oracle_rate,
            note="No directly comparable v0.1 Can MG endpoint row is staged for this regret table.",
        ),
        Cell(
            row_id="v02_router",
            regime_id="can_mg_stress",
            status="abstained",
            oracle_success_rate=oracle_rate,
            source_method="stress_abstain",
            note="Frozen v0.2 abstains on large ambiguous MG-style pools; abstention is counted separately from failure.",
        ),
        Cell(
            row_id="oracle_branch_selector",
            regime_id="can_mg_stress",
            status="oracle_rate_only",
            success_rate=oracle_rate,
            oracle_success_rate=oracle_rate,
            source_method="weighted",
            note="Audit-only best observed stress branch is weighted at fixed 20k.",
        ),
    ]


def collect_cells(root: Path) -> list[Cell]:
    final_root = Path("results/final_paper")
    cells: list[Cell] = []
    cells.extend(endpoint_cells_from_fresh_can(root))
    cells.extend(endpoint_cells_from_fresh_lift(root))
    cells.extend(
        generated_can_cells(
            path=final_root / "ablations" / "hard_negative_can_endpoint_200ep" / "endpoint_200ep_3split_summary.csv",
            regime_id="hard_negative_can",
            positive_method="state_action_positive_nn_top40",
            hard_method="hybrid_rank_fusion_badaware_heavy_top40",
        )
    )
    cells.extend(
        generated_can_cells(
            path=final_root / "ablations" / "can_coverage_shift_endpoint_200ep" / "endpoint_200ep_3split_summary.csv",
            regime_id="coverage_shift_can",
            positive_method="state_action_positive_nn_top40",
            hard_method="hybrid_rank_fusion_badaware_heavy_top40",
        )
    )
    cells.extend(
        prefix_positive_cells(
            final_root / "ablations" / "can_prefix_positive_endpoint_200ep" / "endpoint_200ep_aggregate_summary.csv"
        )
    )
    cells.extend(
        can_mg_cells(final_root / "ablations" / "can_mg_branch_proxy_summary" / "method_proxy_scores.csv")
    )
    return cells


def cell_text(cell: Cell) -> str:
    if cell.status in {"complete", "partial", "oracle"} and cell.successes is not None and cell.episodes is not None:
        regret = cell.regret_successes
        suffix = "" if regret in {None, 0} else f"; regret {regret}"
        return f"{cell.successes}/{cell.episodes}{suffix}"
    if cell.status in {"rate_only", "oracle_rate_only"}:
        regret = cell.regret_rate
        suffix = "" if regret is None or abs(regret) < 1e-12 else f"; regret {regret:.3f}"
        return f"{cell.success_rate:.3f}{suffix}"
    if cell.status == "abstained":
        return "abstain"
    if cell.status == "not_run":
        return "N/A not run"
    if cell.status == "not_applicable":
        return "N/A"
    return cell.status


def markdown_table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    out = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return out


def aggregate_completed(
    per_regime: list[dict[str, object]],
    row_label: str,
    regime_ids: set[str],
) -> tuple[int, int, int] | None:
    successes = 0
    episodes = 0
    oracle_successes = 0
    for row in per_regime:
        if row["row_label"] != row_label or row["regime_id"] not in regime_ids:
            continue
        if row["successes"] == "" or row["episodes"] == "" or row["oracle_successes"] == "":
            continue
        successes += int(row["successes"])
        episodes += int(row["episodes"])
        oracle_successes += int(row["oracle_successes"])
    if episodes == 0:
        return None
    return successes, episodes, oracle_successes - successes


def per_regime_rows(cells: list[Cell]) -> list[dict[str, object]]:
    rows = []
    for cell in sorted(cells, key=lambda c: (REGIME_ORDER.index(c.regime_id), ROW_ORDER.index(c.row_id))):
        rows.append(
            {
                "row_id": cell.row_id,
                "row_label": ROW_LABELS[cell.row_id],
                "regime_id": cell.regime_id,
                "regime_label": REGIME_LABELS[cell.regime_id],
                "status": cell.status,
                "successes": "" if cell.successes is None else cell.successes,
                "episodes": "" if cell.episodes is None else cell.episodes,
                "success_rate": fmt_rate(cell.success_rate),
                "oracle_successes": "" if cell.oracle_successes is None else cell.oracle_successes,
                "oracle_episodes": "" if cell.oracle_episodes is None else cell.oracle_episodes,
                "oracle_success_rate": fmt_rate(cell.oracle_success_rate),
                "regret_successes": "" if cell.regret_successes is None else cell.regret_successes,
                "regret_rate": fmt_rate(cell.regret_rate),
                "source_method": cell.source_method,
                "note": cell.note,
            }
        )
    return rows


def summary_rows(cells: list[Cell]) -> list[dict[str, object]]:
    rows = []
    by_key = {(cell.row_id, cell.regime_id): cell for cell in cells}
    for row_id in ROW_ORDER:
        row_cells = [cell for cell in cells if cell.row_id == row_id]
        counted = [cell for cell in row_cells if cell.successes is not None and cell.episodes is not None]
        successes = sum(cell.successes or 0 for cell in counted)
        episodes = sum(cell.episodes or 0 for cell in counted)
        oracle_successes = sum(cell.oracle_successes or 0 for cell in counted)
        oracle_episodes = sum(cell.oracle_episodes or 0 for cell in counted)
        abstentions = sum(1 for cell in row_cells if cell.status == "abstained")
        missing = sum(1 for cell in row_cells if cell.status in {"not_run", "not_applicable"})
        partial = sum(1 for cell in row_cells if cell.status == "partial")
        rate_only = sum(1 for cell in row_cells if cell.status in {"rate_only", "oracle_rate_only"})
        rows.append(
            {
                "row_id": row_id,
                "row_label": ROW_LABELS[row_id],
                **{regime_id: cell_text(by_key[(row_id, regime_id)]) for regime_id in REGIME_ORDER},
                "counted_success": "" if episodes == 0 else f"{successes}/{episodes}",
                "counted_oracle": "" if oracle_episodes == 0 else f"{oracle_successes}/{oracle_episodes}",
                "counted_regret_to_oracle": "" if oracle_episodes == 0 else oracle_successes - successes,
                "abstentions": abstentions,
                "missing_or_na_cells": missing,
                "partial_cells": partial,
                "rate_only_cells": rate_only,
            }
        )
    return rows


def build_report(summary: list[dict[str, object]], per_regime: list[dict[str, object]]) -> str:
    summary_columns = [
        "row_label",
        "can40_fresh",
        "lift_mg_fresh",
        "hard_negative_can",
        "coverage_shift_can",
        "prefix_positive_can",
        "can_mg_stress",
        "counted_success",
        "counted_regret_to_oracle",
        "abstentions",
        "missing_or_na_cells",
        "partial_cells",
    ]
    detail_columns = [
        "regime_label",
        "row_label",
        "status",
        "successes",
        "episodes",
        "success_rate",
        "oracle_successes",
        "oracle_episodes",
        "regret_successes",
        "source_method",
    ]
    can_lift_regimes = {"can40_fresh", "lift_mg_fresh"}
    v02_can_lift = aggregate_completed(per_regime, "v0.2 router", can_lift_regimes)
    positive_can_lift = aggregate_completed(per_regime, "Always positive-only NN", can_lift_regimes)
    weighted_can_lift = aggregate_completed(per_regime, "Always weighted BC", can_lift_regimes)
    v01_can_lift = aggregate_completed(per_regime, "v0.1 TRIAGE-BC", can_lift_regimes)
    v01_can_status = next(
        (
            str(row["status"])
            for row in per_regime
            if row["row_label"] == "v0.1 TRIAGE-BC" and row["regime_label"] == "Can 40p/80b"
        ),
        "",
    )

    interpretation = []
    if v02_can_lift and positive_can_lift and weighted_can_lift:
        interpretation.append(
            "- On completed Can+Lift rows, current regret to the completed oracle selector is "
            f"`{v02_can_lift[2]}/{v02_can_lift[1]}` for v0.2, versus "
            f"`{positive_can_lift[2]}/{positive_can_lift[1]}` for always positive-only and "
            f"`{weighted_can_lift[2]}/{weighted_can_lift[1]}` for always weighted BC."
        )
    if v01_can_lift:
        if v01_can_status == "complete":
            v01_audit_text = (
                "completed the fresh Lift v0.1 hard-support audit and the fresh Can v0.1 audit"
            )
            v01_can_text = "Fresh Can v0.1 now covers all current split seeds."
        else:
            v01_audit_text = (
                "completed the fresh Lift v0.1 hard-support audit and started the fresh Can v0.1 audit"
            )
            v01_can_text = (
                "Fresh Can v0.1 is partial; see the per-regime CSV for completed and missing split seeds."
            )
        interpretation.append(
            f"- A3 has {v01_audit_text}: "
            f"completed v0.1 Can/Lift cells currently total `{v01_can_lift[0]}/{v01_can_lift[1]}` "
            f"with regret `{v01_can_lift[2]}/{v01_can_lift[1]}` to the same completed-split oracle. "
            f"{v01_can_text}"
        )
    interpretation.extend(
        [
            "- The generated Can probes show the complementary regime: bad-aware hard support has zero regret on hard-negative, coverage-shift, and prefix-positive probes, while matched positive-only retrieval has large regret.",
            "- Can MG remains an abstention/stress case; forcing a branch is not yet justified by the current hidden-label-free proxies.",
            "- This is not yet a fully complete fixed-branch matrix; remaining missing or not-applicable cells are tracked in the per-regime CSV notes.",
        ]
    )

    lines = [
        "# v0.2 Router-Regret Table",
        "",
        "This table is the current A2 portfolio-regret artifact. It compares fixed branches, the frozen v0.2 router, and an audit-only oracle selector over the endpoint rows that are currently completed.",
        "",
        "Important scope notes:",
        "",
        "- `N/A` means that branch was not part of that completed endpoint probe; it is excluded from counted combined success and regret.",
        "- `N/A not run` means the branch is conceptually relevant but missing from the current completed matrix; A3 should fill these cells if the paper needs a complete leaderboard.",
        "- Can MG is a stress/abstention diagnostic with rate-only reused branch summaries, so it is shown but excluded from counted endpoint totals.",
        "- Regret is measured against the best completed branch-selection row per split or aggregate probe; optional mixed-log and all-positive oracle diagnostics are excluded from the fresh Can/Lift regret oracle.",
        "",
        "## Summary",
        "",
        *markdown_table(summary, summary_columns),
        "",
        "## Per-Regime Detail",
        "",
        *markdown_table(per_regime, detail_columns),
        "",
        "## Interpretation",
        "",
        *interpretation,
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    cells = collect_cells(args.root)
    per_regime = per_regime_rows(cells)
    summary = summary_rows(cells)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    write_csv(
        args.out_dir / "v02_router_regret_per_regime.csv",
        per_regime,
        [
            "row_id",
            "row_label",
            "regime_id",
            "regime_label",
            "status",
            "successes",
            "episodes",
            "success_rate",
            "oracle_successes",
            "oracle_episodes",
            "oracle_success_rate",
            "regret_successes",
            "regret_rate",
            "source_method",
            "note",
        ],
    )
    write_csv(
        args.out_dir / "v02_router_regret_summary.csv",
        summary,
        [
            "row_id",
            "row_label",
            *REGIME_ORDER,
            "counted_success",
            "counted_oracle",
            "counted_regret_to_oracle",
            "abstentions",
            "missing_or_na_cells",
            "partial_cells",
            "rate_only_cells",
        ],
    )
    report_path = args.out_dir / "v02_router_regret_REPORT.md"
    report_path.write_text(build_report(summary, per_regime), encoding="utf-8")
    print(f"wrote {args.out_dir / 'v02_router_regret_per_regime.csv'}")
    print(f"wrote {args.out_dir / 'v02_router_regret_summary.csv'}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
