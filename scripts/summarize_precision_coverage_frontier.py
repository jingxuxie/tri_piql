from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from pathlib import Path


os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-tri-piql")

import matplotlib.pyplot as plt


DEFAULT_TABLE_DIR = Path("results/final_paper/tables")
DEFAULT_FIG_DIR = Path("results/final_paper/figures")

CAN40 = Path("results/final_paper/ablations/can40_score_support_tradeoff.csv")
CAN20 = Path("results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split.csv")
CAN80 = Path("results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint.csv")
LIFT_ENDPOINT = Path("results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary.csv")
LIFT_CLASSIFIER = Path("results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary.csv")
PER_SEED = Path("results/final_paper/per_seed")
HARD_NEGATIVE = Path("results/final_paper/ablations/hard_negative_can_action_conflict_summary.csv")
HARD_NEGATIVE_ENDPOINT = Path(
    "results/final_paper/ablations/hard_negative_can_endpoint_200ep/endpoint_200ep_3split_summary.csv"
)
COVERAGE_SHIFT = Path("results/final_paper/ablations/can_coverage_shift_summary.csv")
COVERAGE_SHIFT_ENDPOINT = Path(
    "results/final_paper/ablations/can_coverage_shift_endpoint_200ep/endpoint_200ep_3split_summary.csv"
)
PREFIX_POSITIVE = Path("results/final_paper/ablations/can_prefix_positive_summary.csv")
PREFIX_POSITIVE_ENDPOINT = Path(
    "results/final_paper/ablations/can_prefix_positive_endpoint_200ep/endpoint_200ep_aggregate_summary.csv"
)

OUT_CSV = "precision_coverage_frontier.csv"
OUT_REPORT = "precision_coverage_frontier_REPORT.md"
OUT_FIG = "precision_coverage_frontier"

SPLIT_SEEDS = (11, 22, 33)
ROBOMIMIC_PRIMARY_DENOMS = {
    "can40": (120, 240),
    "can20": (60, 240),
    "can80": (240, 240),
    "lift_mg": (828, 3432),
}

METHOD_LABELS = {
    "triage_adaptive_masscap": "TRIAGE adaptive masscap",
    "triage_bc": "TRIAGE-BC",
    "triage_bc_adaptive_masscap": "TRIAGE adaptive masscap",
    "TRIAGE-BC / pos-min": "TRIAGE-BC pos-min",
    "positive_only_nn_top20": "positive-only NN top20",
    "positive_only_nn_top40": "positive-only NN top40",
    "positive_only_nn_top80": "positive-only NN top80",
    "positive-only NN top160": "positive-only NN top160",
    "weighted_full_pool": "weighted full pool",
    "weighted BC": "weighted BC",
    "classifier-score top160": "classifier top160",
    "classifier_top10": "classifier top10",
    "classifier_top20": "classifier top20",
    "classifier_top40": "classifier top40",
    "classifier_top60": "classifier top60",
    "classifier_top80": "classifier top80",
    "classifier_score_top80": "classifier top80",
    "hybrid_rank_fusion_badaware_heavy_top40": "bad-aware hybrid top40",
    "state_action_positive_nn_top40": "positive-NN state-action top40",
    "prefix_bad_aware_state_top80": "prefix bad-aware state top80",
    "prefix_state_action_nn_top80": "prefix positive-NN state-action top80",
}

FAMILY_MARKERS = {
    "bad-aware": "o",
    "bad-aware proxy": "P",
    "classifier": "X",
    "hybrid": "p",
    "positive-only": "^",
    "soft-reference": "s",
    "weighted": "s",
    "TRIAGE": "D",
}

REGIME_COLORS = {
    "can40": "#2563eb",
    "can20": "#0891b2",
    "can80": "#0f766e",
    "lift_mg": "#7c3aed",
    "hard_negative_can": "#dc2626",
    "coverage_shift_can": "#16a34a",
    "prefix_positive_can": "#f97316",
}

REGIME_LABELS = {
    "can40": "Can 40p/80b",
    "can20": "Can 20p/80b",
    "can80": "Can 80p/80b",
    "lift_mg": "Lift MG",
    "hard_negative_can": "Can hard-negative/action-conflict",
    "coverage_shift_can": "Can scarce-positive coverage shift",
    "prefix_positive_can": "Can prefix-positive",
}

REGIME_ORDER = {
    "can40": 0,
    "can20": 1,
    "can80": 2,
    "lift_mg": 3,
    "hard_negative_can": 4,
    "coverage_shift_can": 5,
    "prefix_positive_can": 6,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--table-dir", type=Path, default=DEFAULT_TABLE_DIR)
    parser.add_argument("--fig-dir", type=Path, default=DEFAULT_FIG_DIR)
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_int(value: object) -> int:
    if value in ("", None):
        return 0
    return int(float(str(value)))


def as_float(value: object) -> float:
    if value in ("", None):
        return 0.0
    return float(str(value))


def fmt_float(value: float | str | None) -> str:
    if value in ("", None):
        return ""
    return f"{float(value):.3f}"


def fmt_int(value: int | str | None) -> str:
    if value in ("", None):
        return ""
    return str(int(float(str(value))))


def fmt_endpoint(successes: str, episodes: str) -> str:
    if not successes or not episodes:
        return ""
    return f"{successes}/{episodes}"


def infer_family(method_id: str, source_family: str = "") -> str:
    if source_family:
        if source_family == "bad-aware proxy":
            return "bad-aware proxy"
        return source_family
    lower = method_id.lower()
    if "weighted" in lower or "soft" in lower:
        return "weighted"
    if "positive_only" in lower or "positive-nn" in lower or "positive_nn" in lower:
        return "positive-only"
    if "classifier" in lower:
        return "classifier"
    if "hybrid" in lower or "fusion" in lower or "triage" in lower:
        return "TRIAGE" if "triage" in lower else "hybrid"
    if "bad_aware" in lower:
        return "bad-aware"
    return "other"


def row(
    *,
    regime_id: str,
    regime_label: str,
    row_role: str,
    method_id: str,
    method_label: str = "",
    method_family: str = "",
    support_split_count: int,
    endpoint_split_count: int = 0,
    support_split_seeds: str,
    endpoint_split_seeds: str = "",
    selected_unlabeled: int,
    hidden_positive_selected: int,
    hidden_bad_selected: int,
    total_hidden_positive: int,
    total_hidden_bad: int,
    support_purity: float,
    hidden_positive_recall: float,
    hidden_bad_admission: float,
    endpoint_successes: int | None = None,
    endpoint_episodes: int | None = None,
    endpoint_status: str = "support_only",
    support_source: str,
    endpoint_source: str = "",
    note: str = "",
) -> dict[str, str]:
    endpoint_success_rate = ""
    if endpoint_successes is not None and endpoint_episodes:
        endpoint_success_rate = fmt_float(endpoint_successes / endpoint_episodes)
    label = method_label or METHOD_LABELS.get(method_id, method_id)
    family = infer_family(method_id, method_family)
    return {
        "regime_id": regime_id,
        "regime_label": regime_label,
        "row_role": row_role,
        "method_id": method_id,
        "method_label": label,
        "method_family": family,
        "support_split_count": str(support_split_count),
        "endpoint_split_count": str(endpoint_split_count),
        "support_split_seeds": support_split_seeds,
        "endpoint_split_seeds": endpoint_split_seeds,
        "selected_unlabeled": str(selected_unlabeled),
        "hidden_positive_selected": str(hidden_positive_selected),
        "hidden_bad_selected": str(hidden_bad_selected),
        "total_hidden_positive": str(total_hidden_positive),
        "total_hidden_bad": str(total_hidden_bad),
        "support_purity": fmt_float(support_purity),
        "hidden_positive_recall": fmt_float(hidden_positive_recall),
        "hidden_bad_admission": fmt_float(hidden_bad_admission),
        "endpoint_successes": "" if endpoint_successes is None else str(endpoint_successes),
        "endpoint_episodes": "" if endpoint_episodes is None else str(endpoint_episodes),
        "endpoint_success_rate": endpoint_success_rate,
        "endpoint_status": endpoint_status,
        "support_source": support_source,
        "endpoint_source": endpoint_source,
        "note": note,
    }


def aggregate_endpoint(rows: list[dict[str, str]], candidate_key: str) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for item in rows:
        key = item[candidate_key]
        entry = grouped.setdefault(
            key,
            {
                "successes": 0,
                "episodes": 0,
                "split_seeds": set(),
            },
        )
        entry["successes"] = int(entry["successes"]) + as_int(item["success_count"])
        entry["episodes"] = int(entry["episodes"]) + as_int(item["eval_episodes"])
        if "split_seed" in item and item["split_seed"]:
            entry["split_seeds"].add(item["split_seed"])
        elif "num_splits" in item and item["num_splits"] == "3":
            entry["split_seeds"].update({"101", "202", "303"})
    return grouped


def add_can40(rows: list[dict[str, str]]) -> None:
    for item in read_rows(CAN40):
        method_id = item["support_rule"]
        selected = round(as_float(item["mean_selected"]) * as_int(item["num_splits"]))
        endpoint_successes = as_int(item["endpoint_successes"]) if item["endpoint_successes"] else None
        endpoint_episodes = as_int(item["endpoint_episodes"]) if item["endpoint_episodes"] else None
        rows.append(
            row(
                regime_id="can40",
                regime_label="Can 40p/80b",
                row_role="primary",
                method_id=method_id,
                support_split_count=as_int(item["num_splits"]),
                endpoint_split_count=3 if endpoint_episodes else 0,
                support_split_seeds="11/22/33",
                endpoint_split_seeds="11/22/33" if endpoint_episodes else "",
                selected_unlabeled=selected,
                hidden_positive_selected=as_int(item["total_hidden_positive"]),
                hidden_bad_selected=as_int(item["total_hidden_bad"]),
                total_hidden_positive=ROBOMIMIC_PRIMARY_DENOMS["can40"][0],
                total_hidden_bad=ROBOMIMIC_PRIMARY_DENOMS["can40"][1],
                support_purity=as_float(item["purity"]),
                hidden_positive_recall=as_float(item["hidden_positive_recall"]),
                hidden_bad_admission=as_float(item["hidden_bad_admission"]),
                endpoint_successes=endpoint_successes,
                endpoint_episodes=endpoint_episodes,
                endpoint_status="complete_3split_endpoint" if endpoint_episodes else "support_only",
                support_source=str(CAN40),
                endpoint_source=str(CAN40) if endpoint_episodes else "",
                note="Frozen primary Can score/support sweep.",
            )
        )


def add_can20(rows: list[dict[str, str]]) -> None:
    for item in read_rows(CAN20):
        method_id = item["support_rule"]
        endpoint_successes = as_int(item["endpoint_successes"]) if item["endpoint_successes"] else None
        endpoint_episodes = as_int(item["endpoint_episodes"]) if item["endpoint_episodes"] else None
        endpoint_splits = as_int(item["endpoint_num_splits"])
        rows.append(
            row(
                regime_id="can20",
                regime_label="Can 20p/80b",
                row_role="diagnostic",
                method_id=method_id,
                support_split_count=as_int(item["num_splits"]),
                endpoint_split_count=endpoint_splits,
                support_split_seeds="11/22/33",
                endpoint_split_seeds="11/22" if endpoint_splits == 2 else ("11" if endpoint_splits == 1 else ""),
                selected_unlabeled=round(as_float(item["mean_selected_unlabeled"]) * as_int(item["num_splits"])),
                hidden_positive_selected=as_int(item["total_hidden_positive"]),
                hidden_bad_selected=as_int(item["total_hidden_bad"]),
                total_hidden_positive=ROBOMIMIC_PRIMARY_DENOMS["can20"][0],
                total_hidden_bad=ROBOMIMIC_PRIMARY_DENOMS["can20"][1],
                support_purity=as_float(item["purity"]),
                hidden_positive_recall=as_float(item["hidden_positive_recall"]),
                hidden_bad_admission=as_float(item["hidden_bad_admission"]),
                endpoint_successes=endpoint_successes,
                endpoint_episodes=endpoint_episodes,
                endpoint_status="partial_endpoint" if endpoint_episodes else "support_only",
                support_source=str(CAN20),
                endpoint_source=str(CAN20) if endpoint_episodes else "",
                note="Appendix-only heavy-contamination diagnostic with partial endpoint coverage.",
            )
        )


def add_can80(rows: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in read_rows(CAN80):
        grouped[item["method"]].append(item)
    for method_id, items in grouped.items():
        split_seeds = sorted({item["split"] for item in items}, key=int)
        endpoint_items = [item for item in items if item["endpoint_successes"]]
        selected = sum(as_int(item["selected_unlabeled"]) for item in items)
        hidden_pos = sum(as_int(item["hidden_positive"]) for item in items)
        hidden_bad = sum(as_int(item["hidden_bad"]) for item in items)
        total_pos = 80 * len(split_seeds)
        total_bad = 80 * len(split_seeds)
        successes = sum(as_int(item["endpoint_successes"]) for item in endpoint_items) if endpoint_items else None
        episodes = sum(as_int(item["eval_episodes"]) for item in endpoint_items) if endpoint_items else None
        rows.append(
            row(
                regime_id="can80",
                regime_label="Can 80p/80b",
                row_role="diagnostic",
                method_id=method_id,
                support_split_count=len(split_seeds),
                endpoint_split_count=len(endpoint_items),
                support_split_seeds="/".join(split_seeds),
                endpoint_split_seeds="/".join(item["split"] for item in endpoint_items),
                selected_unlabeled=selected,
                hidden_positive_selected=hidden_pos,
                hidden_bad_selected=hidden_bad,
                total_hidden_positive=total_pos,
                total_hidden_bad=total_bad,
                support_purity=hidden_pos / selected if selected else 0.0,
                hidden_positive_recall=hidden_pos / total_pos if total_pos else 0.0,
                hidden_bad_admission=hidden_bad / total_bad if total_bad else 0.0,
                endpoint_successes=successes,
                endpoint_episodes=episodes,
                endpoint_status="partial_endpoint" if episodes else "support_only",
                support_source=str(CAN80),
                endpoint_source=str(CAN80) if episodes else "",
                note="Appendix-only balanced diagnostic; endpoint is split-33 only where present.",
            )
        )


def lift_method_rows() -> list[dict[str, object]]:
    endpoint = {item["method"]: item for item in read_rows(LIFT_ENDPOINT)}
    classifier = read_rows(LIFT_CLASSIFIER)[0]
    method_specs = [
        ("weighted_bc", "weighted BC", "weighted", endpoint["weighted BC"]),
        ("positive_only_nn", "positive-only NN top160", "positive-only", endpoint["positive-only NN top160"]),
        ("triage_bc", "TRIAGE-BC / pos-min", "TRIAGE", endpoint["TRIAGE-BC / pos-min"]),
        ("classifier_topk", "classifier-score top160", "classifier", None),
    ]
    out: list[dict[str, object]] = []
    for method_slug, method_label, family, endpoint_row in method_specs:
        selected = 0
        hidden_pos = 0
        hidden_bad = 0
        for split_seed in SPLIT_SEEDS:
            if method_slug == "classifier_topk":
                selected += as_int(classifier[f"split{split_seed}_selected_unlabeled"])
                hidden_pos += as_int(classifier[f"split{split_seed}_hidden_positive"])
                hidden_bad += as_int(classifier[f"split{split_seed}_hidden_bad"])
                continue
            audit_path = (
                PER_SEED
                / f"lift_mg_mg_sparse_split{split_seed}_{method_slug}_policy0"
                / "hidden_label_audit.csv"
            )
            audit = read_rows(audit_path)[0]
            selected += as_int(audit["selected_unlabeled"])
            hidden_pos += as_int(audit["hidden_positive"])
            hidden_bad += as_int(audit["hidden_bad"])
        if method_slug == "classifier_topk":
            successes = as_int(classifier["pooled_successes"])
            episodes = as_int(classifier["pooled_episodes"])
        else:
            successes = as_int(endpoint_row["pooled_successes"])
            episodes = as_int(endpoint_row["pooled_episodes"])
        out.append(
            {
                "method_id": method_slug,
                "method_label": method_label,
                "family": family,
                "selected": selected,
                "hidden_positive": hidden_pos,
                "hidden_bad": hidden_bad,
                "successes": successes,
                "episodes": episodes,
            }
        )
    return out


def add_lift(rows: list[dict[str, str]]) -> None:
    total_pos, total_bad = ROBOMIMIC_PRIMARY_DENOMS["lift_mg"]
    for item in lift_method_rows():
        selected = int(item["selected"])
        hidden_pos = int(item["hidden_positive"])
        hidden_bad = int(item["hidden_bad"])
        rows.append(
            row(
                regime_id="lift_mg",
                regime_label="Lift MG",
                row_role="primary",
                method_id=str(item["method_id"]),
                method_label=str(item["method_label"]),
                method_family=str(item["family"]),
                support_split_count=3,
                endpoint_split_count=3,
                support_split_seeds="11/22/33",
                endpoint_split_seeds="11/22/33",
                selected_unlabeled=selected,
                hidden_positive_selected=hidden_pos,
                hidden_bad_selected=hidden_bad,
                total_hidden_positive=total_pos,
                total_hidden_bad=total_bad,
                support_purity=hidden_pos / selected if selected else 0.0,
                hidden_positive_recall=hidden_pos / total_pos,
                hidden_bad_admission=hidden_bad / total_bad,
                endpoint_successes=int(item["successes"]),
                endpoint_episodes=int(item["episodes"]),
                endpoint_status="complete_3split_endpoint",
                support_source="results/final_paper/per_seed/*/hidden_label_audit.csv",
                endpoint_source=str(LIFT_ENDPOINT) if item["method_id"] != "classifier_topk" else str(LIFT_CLASSIFIER),
                note="Frozen primary Lift support/endpoint rows.",
            )
        )


def add_generated_support(
    rows: list[dict[str, str]],
    *,
    regime_id: str,
    support_path: Path,
    endpoint_path: Path | None,
    endpoint_candidate_key: str,
    endpoint_status_when_present: str,
    note: str,
) -> None:
    endpoint_map: dict[str, dict[str, object]] = {}
    if endpoint_path is not None:
        endpoint_map = aggregate_endpoint(read_rows(endpoint_path), endpoint_candidate_key)
    for item in read_rows(support_path):
        method_id = item["candidate_id"]
        endpoint = endpoint_map.get(method_id)
        split_seeds = ""
        endpoint_successes = None
        endpoint_episodes = None
        endpoint_splits = ""
        if endpoint:
            endpoint_successes = int(endpoint["successes"])
            endpoint_episodes = int(endpoint["episodes"])
            endpoint_splits = "/".join(sorted(endpoint["split_seeds"], key=int))
        rows.append(
            row(
                regime_id=regime_id,
                regime_label=item.get("setting_label") or REGIME_LABELS.get(regime_id, regime_id),
                row_role="generated_diagnostic",
                method_id=method_id,
                method_family=item.get("candidate_family", ""),
                support_split_count=as_int(item["split_count"] if "split_count" in item else item["splits"]),
                endpoint_split_count=len(endpoint["split_seeds"]) if endpoint else 0,
                support_split_seeds=split_seeds or "101/202/303",
                endpoint_split_seeds=endpoint_splits,
                selected_unlabeled=as_int(item["selected_unlabeled"]),
                hidden_positive_selected=as_int(item["hidden_positive_selected"]),
                hidden_bad_selected=as_int(item["hidden_bad_selected"]),
                total_hidden_positive=as_int(item["total_hidden_positive"]),
                total_hidden_bad=as_int(item["total_hidden_bad"]),
                support_purity=as_float(item["support_purity"]),
                hidden_positive_recall=as_float(item["hidden_positive_recall"]),
                hidden_bad_admission=as_float(item["hidden_bad_admission"]),
                endpoint_successes=endpoint_successes,
                endpoint_episodes=endpoint_episodes,
                endpoint_status=endpoint_status_when_present if endpoint else "support_only",
                support_source=str(support_path),
                endpoint_source=str(endpoint_path) if endpoint else "",
                note=note,
            )
        )


def all_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    add_can40(rows)
    add_can20(rows)
    add_can80(rows)
    add_lift(rows)
    add_generated_support(
        rows,
        regime_id="hard_negative_can",
        support_path=HARD_NEGATIVE,
        endpoint_path=HARD_NEGATIVE_ENDPOINT,
        endpoint_candidate_key="candidate_id",
        endpoint_status_when_present="complete_3split_endpoint",
        note="Generated hard-negative/action-conflict Can regime probe.",
    )
    add_generated_support(
        rows,
        regime_id="coverage_shift_can",
        support_path=COVERAGE_SHIFT,
        endpoint_path=COVERAGE_SHIFT_ENDPOINT,
        endpoint_candidate_key="candidate_id",
        endpoint_status_when_present="complete_3split_endpoint",
        note="Generated scarce-positive coverage-shift Can regime probe.",
    )
    add_generated_support(
        rows,
        regime_id="prefix_positive_can",
        support_path=PREFIX_POSITIVE,
        endpoint_path=PREFIX_POSITIVE_ENDPOINT,
        endpoint_candidate_key="candidate_id",
        endpoint_status_when_present="complete_3split_endpoint",
        note="Generated prefix-positive Can regime probe.",
    )
    rows.sort(
        key=lambda item: (
            REGIME_ORDER.get(item["regime_id"], 99),
            item["method_family"],
            item["method_id"],
        )
    )
    return rows


def endpoint_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [item for item in rows if item["endpoint_episodes"]]


def key_comparison_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    row_map = {(item["regime_id"], item["method_id"]): item for item in rows}
    pairs = [
        ("Can 40p/80b", "can40", "triage_adaptive_masscap", "positive_only_nn_top40"),
        ("Can 40p/80b", "can40", "triage_adaptive_masscap", "weighted_full_pool"),
        ("Can 20p/80b", "can20", "triage_adaptive_masscap", "positive_only_nn_top20"),
        ("Can 80p/80b", "can80", "triage_bc_adaptive_masscap", "positive_only_nn_top80"),
        (
            "Hard-negative Can",
            "hard_negative_can",
            "hybrid_rank_fusion_badaware_heavy_top40",
            "state_action_positive_nn_top40",
        ),
        (
            "Coverage-shift Can",
            "coverage_shift_can",
            "hybrid_rank_fusion_badaware_heavy_top40",
            "state_action_positive_nn_top40",
        ),
        (
            "Prefix-positive Can",
            "prefix_positive_can",
            "prefix_bad_aware_state_top80",
            "prefix_state_action_nn_top80",
        ),
        ("Lift MG", "lift_mg", "triage_bc", "weighted_bc"),
        ("Lift MG", "lift_mg", "triage_bc", "positive_only_nn"),
    ]
    out: list[dict[str, str]] = []
    for label, regime_id, a_id, b_id in pairs:
        a = row_map.get((regime_id, a_id))
        b = row_map.get((regime_id, b_id))
        if not a or not b:
            continue
        a_success = as_int(a["endpoint_successes"])
        b_success = as_int(b["endpoint_successes"])
        a_episodes = as_int(a["endpoint_episodes"])
        b_episodes = as_int(b["endpoint_episodes"])
        out.append(
            {
                "regime": label,
                "bad_aware_or_triage": a["method_label"],
                "baseline": b["method_label"],
                "recall_delta": fmt_float(as_float(a["hidden_positive_recall"]) - as_float(b["hidden_positive_recall"])),
                "bad_admission_delta": fmt_float(as_float(a["hidden_bad_admission"]) - as_float(b["hidden_bad_admission"])),
                "endpoint_delta": fmt_float((a_success / a_episodes) - (b_success / b_episodes))
                if a_episodes and b_episodes
                else "",
                "endpoint": f"{fmt_endpoint(a['endpoint_successes'], a['endpoint_episodes'])} vs {fmt_endpoint(b['endpoint_successes'], b['endpoint_episodes'])}",
                "status": a["endpoint_status"],
            }
        )
    return out


def markdown_table(rows: list[dict[str, str]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for item in rows:
        lines.append("| " + " | ".join(item.get(column, "") for column in columns) + " |")
    return lines


def write_report(path: Path, rows: list[dict[str, str]]) -> None:
    endpoints = endpoint_rows(rows)
    complete_endpoints = [item for item in endpoints if item["endpoint_status"] == "complete_3split_endpoint"]
    comparisons = key_comparison_rows(rows)
    best_endpoint = max(endpoints, key=lambda item: as_float(item["endpoint_success_rate"]))
    lines: list[str] = [
        "# Precision/Coverage Frontier Across Regimes",
        "",
        "This artifact puts all current support-selection regimes in the same audit space: "
        "hidden-positive recall on the x-axis and hidden-bad admission on the y-axis. "
        "Endpoint-backed points are larger in the figure; support-only points remain in the table as mechanism evidence.",
        "",
        "## Endpoint-Backed Highlights",
        "",
        "| regime | method | family | recall | bad admission | purity | endpoint | status |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for item in sorted(
        endpoints,
        key=lambda row: (
            REGIME_ORDER.get(row["regime_id"], 99),
            -as_float(row["endpoint_success_rate"]),
            row["method_id"],
        ),
    ):
        lines.append(
            f"| {item['regime_label']} | {item['method_label']} | {item['method_family']} | "
            f"{item['hidden_positive_recall']} | {item['hidden_bad_admission']} | {item['support_purity']} | "
            f"{fmt_endpoint(item['endpoint_successes'], item['endpoint_episodes'])} ({item['endpoint_success_rate']}) | "
            f"{item['endpoint_status']} |"
        )
    lines.extend(
        [
            "",
            "## Matched Comparisons",
            "",
            *markdown_table(
                comparisons,
                [
                    "regime",
                    "bad_aware_or_triage",
                    "baseline",
                    "recall_delta",
                    "bad_admission_delta",
                    "endpoint_delta",
                    "endpoint",
                    "status",
                ],
            ),
            "",
            "## Interpretation",
            "",
            "- Default Can 40p/80b is a precision/coverage caveat: TRIAGE-BC recovers slightly more hidden-positive support than positive-only NN, but admits far more hidden-bad support and loses the endpoint.",
            "- Generated hard-negative, coverage-shift, and prefix-positive Can probes are the clearest robotics mechanism evidence where bad-aware or hybrid support improves both support quality and endpoint success over matched positive-only retrieval.",
            "- Lift MG shows that support purity alone is insufficient: TRIAGE-BC is much purer, but weighted BC has broad coverage and wins the frozen three-split endpoint.",
            "- Can 20p/80b and Can 80p/80b remain appendix diagnostics because endpoint coverage is partial.",
            "",
            "## Evidence Boundary",
            "",
            f"- Rows in the CSV: `{len(rows)}`.",
            f"- Endpoint-backed rows: `{len(endpoints)}`; complete three-split endpoint rows: `{len(complete_endpoints)}`.",
            f"- Best endpoint-backed row in this frontier: `{best_endpoint['regime_label']} / {best_endpoint['method_label']}` with `{fmt_endpoint(best_endpoint['endpoint_successes'], best_endpoint['endpoint_episodes'])}` successes.",
            "- Hidden labels are audit-only in this artifact; they are used to place supports on the precision/coverage plane and to construct generated split diagnostics, not as inputs to the deployed selection rules.",
            "",
            "## Outputs",
            "",
            "- `results/final_paper/tables/precision_coverage_frontier.csv`",
            "- `results/final_paper/tables/precision_coverage_frontier_REPORT.md`",
            "- `results/final_paper/figures/precision_coverage_frontier.png`",
            "- `results/final_paper/figures/precision_coverage_frontier.pdf`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(rows: list[dict[str, str]], fig_dir: Path) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.6, 6.2))

    endpoints = endpoint_rows(rows)
    endpoint_lookup = {(item["regime_id"], item["method_id"]) for item in endpoints}

    for item in rows:
        regime_id = item["regime_id"]
        family = item["method_family"]
        is_endpoint = (regime_id, item["method_id"]) in endpoint_lookup
        success_rate = as_float(item["endpoint_success_rate"])
        size = 34 if not is_endpoint else 95 + 230 * success_rate
        alpha = 0.35 if not is_endpoint else 0.88
        linewidth = 0.5 if not is_endpoint else 0.9
        ax.scatter(
            as_float(item["hidden_positive_recall"]),
            as_float(item["hidden_bad_admission"]),
            s=size,
            marker=FAMILY_MARKERS.get(family, "o"),
            color=REGIME_COLORS.get(regime_id, "#6b7280"),
            alpha=alpha,
            edgecolors="#111827" if is_endpoint else "none",
            linewidths=linewidth,
        )

    ax.set_xlim(-0.03, 1.05)
    ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel("Hidden-positive recall")
    ax.set_ylabel("Hidden-bad admission")
    ax.set_title("Precision/Coverage Frontier Across Regimes")
    ax.grid(True, color="#e5e7eb", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    regime_handles = []
    for regime_id in sorted(REGIME_COLORS, key=lambda key: REGIME_ORDER[key]):
        regime_handles.append(
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=REGIME_COLORS[regime_id],
                markersize=7,
                label=regime_id.replace("_", " "),
            )
        )
    family_handles = []
    for family in ["TRIAGE", "hybrid", "bad-aware", "positive-only", "weighted", "classifier"]:
        family_handles.append(
            plt.Line2D(
                [0],
                [0],
                marker=FAMILY_MARKERS.get(family, "o"),
                color="#111827",
                linestyle="None",
                markersize=7,
                label=family,
            )
        )
    size_handles = [
        plt.scatter([], [], s=95 + 230 * rate, color="#9ca3af", edgecolors="#111827", linewidths=0.8)
        for rate in (0.4, 0.7, 1.0)
    ]
    first_legend = ax.legend(
        handles=regime_handles,
        title="Regime",
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        frameon=False,
        fontsize=8,
        title_fontsize=8.5,
    )
    ax.add_artist(first_legend)
    second_legend = ax.legend(
        handles=family_handles,
        title="Method family",
        loc="center left",
        bbox_to_anchor=(1.01, 0.35),
        frameon=False,
        fontsize=8,
        title_fontsize=8.5,
    )
    ax.add_artist(second_legend)
    ax.legend(
        size_handles,
        ["0.4", "0.7", "1.0"],
        title="Endpoint rate",
        loc="lower left",
        bbox_to_anchor=(1.01, 0.0),
        frameon=False,
        fontsize=8,
        title_fontsize=8.5,
    )
    fig.text(
        0.5,
        0.01,
        "Large, outlined points have endpoint rollouts and size encodes endpoint success rate; smaller translucent points are support-only audits.",
        ha="center",
        va="bottom",
        fontsize=8,
        color="#4b5563",
    )
    fig.tight_layout(rect=(0, 0.04, 0.78, 1))

    for suffix in ("png", "pdf"):
        fig.savefig(fig_dir / f"{OUT_FIG}.{suffix}", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    rows = all_rows()
    fieldnames = [
        "regime_id",
        "regime_label",
        "row_role",
        "method_id",
        "method_label",
        "method_family",
        "support_split_count",
        "endpoint_split_count",
        "support_split_seeds",
        "endpoint_split_seeds",
        "selected_unlabeled",
        "hidden_positive_selected",
        "hidden_bad_selected",
        "total_hidden_positive",
        "total_hidden_bad",
        "support_purity",
        "hidden_positive_recall",
        "hidden_bad_admission",
        "endpoint_successes",
        "endpoint_episodes",
        "endpoint_success_rate",
        "endpoint_status",
        "support_source",
        "endpoint_source",
        "note",
    ]
    write_csv(args.table_dir / OUT_CSV, rows, fieldnames)
    write_report(args.table_dir / OUT_REPORT, rows)
    plot(rows, args.fig_dir)

    print(f"wrote {args.table_dir / OUT_CSV}")
    print(f"wrote {args.table_dir / OUT_REPORT}")
    print(f"wrote {args.fig_dir / (OUT_FIG + '.png')}")
    print(f"wrote {args.fig_dir / (OUT_FIG + '.pdf')}")


if __name__ == "__main__":
    main()
