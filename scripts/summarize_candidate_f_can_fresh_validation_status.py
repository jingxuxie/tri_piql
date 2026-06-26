#!/usr/bin/env python3
"""Summarize the Candidate F fresh Can-only validation status."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "candidate_f_can_fresh_validation"
PILOT = ROOT / "results" / "candidate_g_fresh_preflight"
TABLE_DIR = OUT / "tables"

VALIDATION_SEEDS = [808, 909, 1001, 1112, 1213]
PILOT_SEEDS = [606, 707]
EXCLUDED_DISCOVERY_SEEDS = [101, 202, 303, 404, 505]
REQUIRED_METHODS = ["positive_only_nn", "weighted_bc", "triage_bc"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def table(rows: list[dict[str, object]], columns: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return lines


def split_path(root: Path, seed: int) -> Path:
    return root / "splits" / f"can_paired_pos40_bad80_split{seed}" / "split_indices.json"


def method_dir(root: Path, seed: int, method: str) -> Path:
    return root / "per_seed" / f"can_paired_pos40_bad80_split{seed}_{method}_policy0"


def latest_epoch200_checkpoint(run_dir: Path) -> Path | None:
    train_dir = run_dir / "train"
    matches = sorted(train_dir.glob("**/models/model_epoch_200.pth"))
    return matches[-1] if matches else None


def eval_dir(root: Path, seed: int, method: str, episodes: int) -> Path:
    return root / f"can{seed}_{method}_epoch200_eval{episodes}"


def success_cell(run_dir: Path) -> str:
    metrics_path = run_dir / "metrics.csv"
    if not metrics_path.exists():
        return ""
    row = read_csv(metrics_path)[0]
    episodes = int(float(row["eval_episodes"]))
    successes = int(round(float(row["success_rate"]) * episodes))
    return f"{successes}/{episodes}"


def parse_success_cell(cell: str) -> tuple[int, int] | None:
    if not cell or "/" not in cell:
        return None
    successes, episodes = cell.split("/", 1)
    return int(successes), int(episodes)


def tail_decision(root: Path, seed: int) -> dict[str, object]:
    pos_dir = method_dir(root, seed, "positive_only_nn")
    weighted_dir = method_dir(root, seed, "weighted_bc")
    pos_diag_path = pos_dir / "setup" / "diagnostics.json"
    weights_path = weighted_dir / "setup" / "demo_weights.json"
    weighted_diag_path = weighted_dir / "setup" / "diagnostics.json"
    if not (pos_diag_path.exists() and weights_path.exists() and weighted_diag_path.exists()):
        return {
            "tail_status": "missing_setup",
            "below_count": "",
            "below_fraction": "",
            "candidate_f_branch": "",
        }
    pos_diag = json.loads(pos_diag_path.read_text(encoding="utf-8"))
    weights = json.loads(weights_path.read_text(encoding="utf-8"))
    weighted_diag = json.loads(weighted_diag_path.read_text(encoding="utf-8"))
    selected = list(pos_diag["selected_unlabeled_demos"])
    unlabeled_prob_mean = float(weighted_diag["classifier"]["unlabeled_prob_mean"])
    threshold = 0.5 * unlabeled_prob_mean
    below_count = sum(float(weights[demo_id]) < threshold for demo_id in selected)
    below_fraction = below_count / max(1, len(selected))
    return {
        "tail_status": "ready",
        "below_count": int(below_count),
        "below_fraction": f"{below_fraction:.3f}",
        "candidate_f_branch": "weighted_bc" if below_count > 0 else "candidate_e_gate",
    }


def validation_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed in VALIDATION_SEEDS:
        split_exists = split_path(OUT, seed).exists()
        tail = tail_decision(OUT, seed)
        method_status = {}
        eval_status = {}
        for method in REQUIRED_METHODS:
            run_dir = method_dir(OUT, seed, method)
            method_status[f"{method}_setup"] = int((run_dir / "setup" / "diagnostics.json").exists())
            method_status[f"{method}_ckpt200"] = int(latest_epoch200_checkpoint(run_dir) is not None)
            # Baseline evals are expected at 50 episodes for validation.
            direct_eval = run_dir / "eval" / "metrics.csv"
            eval_status[f"{method}_eval50"] = int(direct_eval.exists())
            eval_status[f"{method}_success50"] = success_cell(run_dir / "eval")
        candidate_e = OUT / "candidate_e_eval" / f"can{seed}_candidate_e_gate_eval50"
        branch = tail["candidate_f_branch"]
        if branch == "candidate_e_gate":
            candidate_f_eval50 = int((candidate_e / "metrics.csv").exists())
            candidate_f_success50 = success_cell(candidate_e)
        elif branch == "weighted_bc":
            weighted_eval_dir = method_dir(OUT, seed, "weighted_bc") / "eval"
            candidate_f_eval50 = int((weighted_eval_dir / "metrics.csv").exists())
            candidate_f_success50 = success_cell(weighted_eval_dir)
        else:
            candidate_f_eval50 = 0
            candidate_f_success50 = ""
        baseline_counts = {}
        for method in REQUIRED_METHODS:
            parsed = parse_success_cell(eval_status[f"{method}_success50"])
            if parsed is not None:
                baseline_counts[method] = parsed[0]
        candidate_parsed = parse_success_cell(candidate_f_success50)
        if baseline_counts:
            best_baseline_method, best_baseline_successes = max(
                baseline_counts.items(),
                key=lambda item: (item[1], -REQUIRED_METHODS.index(item[0])),
            )
            # All validation evals use the frozen 50-episode endpoint protocol.
            best_baseline_success50 = f"{best_baseline_successes}/50"
        else:
            best_baseline_method = ""
            best_baseline_success50 = ""
        if baseline_counts and candidate_parsed is not None:
            delta_vs_best = candidate_parsed[0] - best_baseline_successes
            no_worse_best = int(delta_vs_best >= 0)
        else:
            delta_vs_best = ""
            no_worse_best = ""
        rows.append(
            {
                "seed": seed,
                "split_exists": int(split_exists),
                **tail,
                **method_status,
                **eval_status,
                "candidate_e_eval50": int((candidate_e / "metrics.csv").exists()),
                "candidate_e_success50": success_cell(candidate_e),
                "candidate_f_eval50": candidate_f_eval50,
                "candidate_f_success50": candidate_f_success50,
                "best_baseline_method": best_baseline_method,
                "best_baseline_success50": best_baseline_success50,
                "candidate_f_delta_vs_best50": delta_vs_best,
                "candidate_f_no_worse_best50": no_worse_best,
                "claim_use": "fresh_validation",
            }
        )
    return rows


def pilot_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed in PILOT_SEEDS:
        root = PILOT
        tail = tail_decision(root, seed)
        row = {
            "seed": seed,
            "claim_use": "pilot_only_excluded",
            **tail,
            "candidate_f_first20": "",
            "positive_first20": success_cell(eval_dir(root, seed, "positive", 20)),
            "weighted_first20": success_cell(eval_dir(root, seed, "weighted", 20)),
            "triage_first20": success_cell(eval_dir(root, seed, "triage", 20)),
            "candidate_e_first20": success_cell(root / f"can{seed}_candidate_e_gate_eval20"),
        }
        if seed == 606:
            row["candidate_f_first20"] = row["candidate_e_first20"]
        elif seed == 707:
            row["candidate_f_first20"] = row["weighted_first20"]
        rows.append(row)
    return rows


def main() -> None:
    validation = validation_rows()
    pilots = pilot_rows()
    validation_csv = TABLE_DIR / "candidate_f_can_fresh_validation_status.csv"
    pilot_csv = TABLE_DIR / "candidate_f_can_fresh_pilot_rows.csv"
    report_path = TABLE_DIR / "candidate_f_can_fresh_validation_STATUS.md"

    validation_fields = [
        "seed",
        "split_exists",
        "tail_status",
        "below_count",
        "below_fraction",
        "candidate_f_branch",
        "positive_only_nn_setup",
        "positive_only_nn_ckpt200",
        "positive_only_nn_eval50",
        "positive_only_nn_success50",
        "weighted_bc_setup",
        "weighted_bc_ckpt200",
        "weighted_bc_eval50",
        "weighted_bc_success50",
        "triage_bc_setup",
        "triage_bc_ckpt200",
        "triage_bc_eval50",
        "triage_bc_success50",
        "candidate_e_eval50",
        "candidate_e_success50",
        "candidate_f_eval50",
        "candidate_f_success50",
        "best_baseline_method",
        "best_baseline_success50",
        "candidate_f_delta_vs_best50",
        "candidate_f_no_worse_best50",
        "claim_use",
    ]
    pilot_fields = [
        "seed",
        "claim_use",
        "tail_status",
        "below_count",
        "below_fraction",
        "candidate_f_branch",
        "candidate_f_first20",
        "positive_first20",
        "weighted_first20",
        "triage_first20",
        "candidate_e_first20",
    ]
    write_csv(validation_csv, validation, validation_fields)
    write_csv(pilot_csv, pilots, pilot_fields)

    ready_splits = sum(
        row["split_exists"]
        and row["positive_only_nn_ckpt200"]
        and row["weighted_bc_ckpt200"]
        and row["triage_bc_ckpt200"]
        for row in validation
    )
    setup_splits = sum(
        row["split_exists"]
        and row["positive_only_nn_setup"]
        and row["weighted_bc_setup"]
        and row["triage_bc_setup"]
        for row in validation
    )
    claim_ready_splits = sum(
        row["split_exists"]
        and row["positive_only_nn_ckpt200"]
        and row["weighted_bc_ckpt200"]
        and row["triage_bc_ckpt200"]
        and row["positive_only_nn_eval50"]
        and row["weighted_bc_eval50"]
        and row["triage_bc_eval50"]
        and row["candidate_f_eval50"]
        for row in validation
    )
    worse_than_best = sum(row["candidate_f_no_worse_best50"] == 0 for row in validation)
    max_allowed_worse = len(VALIDATION_SEEDS) - 4
    gate_failed_early = worse_than_best > max_allowed_worse
    if gate_failed_early:
        status_line = "**Status: validation gate failed early.**"
    elif claim_ready_splits == len(VALIDATION_SEEDS):
        status_line = "**Status: validation endpoints complete.**"
    elif claim_ready_splits:
        status_line = "**Status: validation endpoints in progress.**"
    elif ready_splits:
        status_line = "**Status: trained baselines ready, no validation endpoints yet.**"
    elif setup_splits:
        status_line = "**Status: setup started, no validation endpoints yet.**"
    else:
        status_line = "**Status: frozen but not launched.**"
    validation_display = [{key: row[key] for key in validation_fields} for row in validation]
    pilot_display = [{key: row[key] for key in pilot_fields} for row in pilots]
    lines = [
        "# Candidate F Fresh Can-Only Validation Status",
        "",
        f"{status_line} The validation split seeds are",
        "`808/909/1001/1112/1213`; pilot seeds `606/707` are excluded from",
        "claim-bearing validation because they were already used to decide whether",
        "Candidate F should continue.",
        "",
        f"Setup-complete validation splits: `{setup_splits}/5`.",
        f"Ready trained validation splits: `{ready_splits}/5`.",
        f"Claim-ready validation splits: `{claim_ready_splits}/5`.",
        "",
        "## Frozen Validation Rows",
        "",
        *table(
            validation_display,
            [
                "seed",
                "split_exists",
                "tail_status",
                "below_count",
                "below_fraction",
                "candidate_f_branch",
                "positive_only_nn_ckpt200",
                "positive_only_nn_success50",
                "weighted_bc_ckpt200",
                "weighted_bc_success50",
                "triage_bc_ckpt200",
                "triage_bc_success50",
                "candidate_e_eval50",
                "candidate_e_success50",
                "candidate_f_success50",
                "best_baseline_method",
                "best_baseline_success50",
                "candidate_f_delta_vs_best50",
                "candidate_f_no_worse_best50",
                "claim_use",
            ],
        ),
        "",
        "## Pilot Rows Excluded From Claims",
        "",
        *table(
            pilot_display,
            [
                "seed",
                "claim_use",
                "candidate_f_branch",
                "candidate_f_first20",
                "positive_first20",
                "weighted_first20",
                "triage_first20",
                "candidate_e_first20",
            ],
        ),
        "",
        "## Read",
        "",
        f"- Claim-ready validation rows: `{claim_ready_splits}/5`.",
        (
            f"- Frozen gate failed early: Candidate F is worse than the best "
            f"completed non-oracle baseline on `{worse_than_best}` validation "
            f"rows, while the 4/5 no-worse gate allows at most `{max_allowed_worse}`."
            if gate_failed_early
            else "- Treat this as live validation progress, not a promotable claim until the frozen gate is satisfied."
        ),
        (
            "- Stop Candidate F scaling for a methods-dominance claim and return to the cautious precision/coverage paper framing or a new candidate."
            if gate_failed_early
            else "- Next compute should continue the remaining frozen validation seeds unless the current rows already falsify the candidate strongly enough to stop."
        ),
        "- The pilot rows remain neutral: Candidate F ties positive-only across",
        "  `606/707` at `31/40`, so they are useful context but not validation",
        "  evidence.",
        "- Claim promotion requires the gate in",
        "  `METHOD_FREEZE_CANDIDATE_F_CAN_FRESH.md`.",
        "",
        "## Artifacts",
        "",
        f"- Validation CSV: `{validation_csv.relative_to(ROOT)}`.",
        f"- Pilot CSV: `{pilot_csv.relative_to(ROOT)}`.",
        "- Freeze: `METHOD_FREEZE_CANDIDATE_F_CAN_FRESH.md`.",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
