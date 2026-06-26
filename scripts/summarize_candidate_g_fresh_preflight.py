#!/usr/bin/env python3
"""Summarize Candidate G branch decisions on prepared fresh splits."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAIL_FRACTION_OF_UNLABELED_MEAN = 0.5
MILD_TAIL_FRACTION_MAX = 0.03
TASKS = {
    "can_paired": {
        "split_type": "pos40_bad80",
        "task_label": "Can 40p/80b",
        "no_tail_choice": "candidate_e_gate",
    },
    "lift_mg": {
        "split_type": "mg_sparse",
        "task_label": "Lift MG",
        "no_tail_choice": "positive_only_nn",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/candidate_g_fresh_preflight"))
    parser.add_argument("--split-seeds", type=int, nargs="+", default=[606, 707])
    parser.add_argument("--policy-seed", type=int, default=0)
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_id(task: str, split_type: str, split_seed: int, method: str, policy_seed: int) -> str:
    return f"{task}_{split_type}_split{split_seed}_{method}_policy{policy_seed}"


def setup_dir(out_dir: Path, task: str, split_type: str, split_seed: int, method: str, policy_seed: int) -> Path:
    return out_dir / "per_seed" / run_id(task, split_type, split_seed, method, policy_seed) / "setup"


def run_dir(out_dir: Path, task: str, split_type: str, split_seed: int, method: str, policy_seed: int) -> Path:
    return out_dir / "per_seed" / run_id(task, split_type, split_seed, method, policy_seed)


def branch_choice(below_count: int, below_fraction: float, no_tail_choice: str) -> str:
    if below_count == 0:
        return no_tail_choice
    if below_fraction < MILD_TAIL_FRACTION_MAX:
        return "triage_bc"
    return "weighted_bc"


def support_counts(run_path: Path) -> dict[str, object]:
    audit_path = run_path / "hidden_label_audit.csv"
    if not audit_path.exists():
        return {
            "branch_selected_unlabeled": "",
            "branch_hidden_positive": "",
            "branch_hidden_bad": "",
            "branch_purity": "",
        }
    rows = read_csv(audit_path)
    if len(rows) != 1:
        raise ValueError(f"{audit_path}: expected exactly one row")
    row = rows[0]
    return {
        "branch_selected_unlabeled": int(row["selected_unlabeled"]),
        "branch_hidden_positive": int(row["hidden_positive"]),
        "branch_hidden_bad": int(row["hidden_bad"]),
        "branch_purity": float(row["purity"]),
    }


def required_paths(out_dir: Path, task: str, split_type: str, split_seed: int, policy_seed: int) -> list[Path]:
    paths = []
    for method in ["positive_only_nn", "weighted_bc", "triage_bc"]:
        paths.append(setup_dir(out_dir, task, split_type, split_seed, method, policy_seed) / "diagnostics.json")
    paths.append(setup_dir(out_dir, task, split_type, split_seed, "weighted_bc", policy_seed) / "demo_weights.json")
    return paths


def candidate_row(out_dir: Path, task: str, split_seed: int, policy_seed: int) -> dict[str, object]:
    spec = TASKS[task]
    split_type = str(spec["split_type"])
    missing = [path for path in required_paths(out_dir, task, split_type, split_seed, policy_seed) if not path.exists()]
    if missing:
        raise FileNotFoundError("missing prepared artifacts:\n" + "\n".join(str(path) for path in missing))

    positive_diag = read_json(setup_dir(out_dir, task, split_type, split_seed, "positive_only_nn", policy_seed) / "diagnostics.json")
    weighted_setup = setup_dir(out_dir, task, split_type, split_seed, "weighted_bc", policy_seed)
    weighted_diag = read_json(weighted_setup / "diagnostics.json")
    demo_weights = read_json(weighted_setup / "demo_weights.json")

    selected = list(positive_diag["selected_unlabeled_demos"])
    selected_probs = sorted(float(demo_weights[demo_id]) for demo_id in selected)
    unlabeled_prob_mean = float(weighted_diag["classifier"]["unlabeled_prob_mean"])
    tail_threshold = TAIL_FRACTION_OF_UNLABELED_MEAN * unlabeled_prob_mean
    below_count = sum(prob < tail_threshold for prob in selected_probs)
    below_fraction = below_count / len(selected_probs)
    choice = branch_choice(below_count, below_fraction, str(spec["no_tail_choice"]))

    if choice == "candidate_e_gate":
        support_method = "positive_only_nn"
    elif choice == "positive_only_nn":
        support_method = "positive_only_nn"
    else:
        support_method = choice
    branch_support = support_counts(run_dir(out_dir, task, split_type, split_seed, support_method, policy_seed))

    return {
        "task": task,
        "task_label": spec["task_label"],
        "split_type": split_type,
        "split_seed": split_seed,
        "policy_seed": policy_seed,
        "selected_count": len(selected),
        "selected_prob_min": selected_probs[0],
        "selected_prob_p10": selected_probs[max(0, int(0.10 * (len(selected_probs) - 1)))],
        "selected_prob_mean": sum(selected_probs) / len(selected_probs),
        "unlabeled_prob_mean": unlabeled_prob_mean,
        "tail_threshold": tail_threshold,
        "selected_min_over_unlabeled_mean": selected_probs[0] / unlabeled_prob_mean,
        "below_count": below_count,
        "below_fraction": below_fraction,
        "candidate_g_choice": choice,
        "support_method_for_audit": support_method,
        **branch_support,
    }


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(path)


def markdown_table(rows: list[dict[str, object]]) -> list[str]:
    lines = [
        "| task | split | min/mean | #<thr | frac<thr | choice | support hp/bad | purity |",
        "| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for row in rows:
        hp_bad = (
            f"{row['branch_hidden_positive']}/{row['branch_hidden_bad']}"
            if row["branch_hidden_positive"] != ""
            else ""
        )
        lines.append(
            "| {task} | {split} | {ratio} | {below} | {frac} | {choice} | {hp_bad} | {purity} |".format(
                task=row["task"],
                split=row["split_seed"],
                ratio=fmt(row["selected_min_over_unlabeled_mean"]),
                below=row["below_count"],
                frac=fmt(row["below_fraction"]),
                choice=row["candidate_g_choice"],
                hp_bad=hp_bad,
                purity=fmt(row["branch_purity"]),
            )
        )
    return lines


def main() -> None:
    args = parse_args()
    rows = []
    for task in TASKS:
        for split_seed in args.split_seeds:
            rows.append(candidate_row(args.out_dir, task, split_seed, args.policy_seed))

    csv_path = args.out_dir / "candidate_g_fresh_preflight_summary.csv"
    fieldnames = [
        "task",
        "task_label",
        "split_type",
        "split_seed",
        "policy_seed",
        "selected_count",
        "selected_prob_min",
        "selected_prob_p10",
        "selected_prob_mean",
        "unlabeled_prob_mean",
        "tail_threshold",
        "selected_min_over_unlabeled_mean",
        "below_count",
        "below_fraction",
        "candidate_g_choice",
        "support_method_for_audit",
        "branch_selected_unlabeled",
        "branch_hidden_positive",
        "branch_hidden_bad",
        "branch_purity",
    ]
    write_csv(csv_path, rows, fieldnames)

    report_path = args.out_dir / "candidate_g_fresh_preflight_REPORT.md"
    lines = [
        "# Candidate G Fresh-Split Preflight",
        "",
        "This report applies the frozen Candidate G branch rule to prepared split",
        "artifacts only. It does not use endpoint outcomes.",
        "",
        *markdown_table(rows),
        "",
        "## Read",
        "",
    ]
    task_choices: dict[str, list[str]] = {}
    for row in rows:
        task_choices.setdefault(str(row["task"]), []).append(str(row["candidate_g_choice"]))
    for task, choices in task_choices.items():
        counts = {choice: choices.count(choice) for choice in sorted(set(choices))}
        lines.append(f"- `{task}` choices: `{counts}`.")
    lines.extend(
        [
            "- This preflight only says which frozen branch would be evaluated on",
            "  unseen split seeds and what hidden-label support audit that branch has.",
            "- Endpoint rollouts are still required before Candidate G can support a",
            "  methods claim.",
            "",
            "## Artifacts",
            "",
            f"- Summary CSV: `{display_path(csv_path)}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {display_path(report_path)}")


if __name__ == "__main__":
    main()
