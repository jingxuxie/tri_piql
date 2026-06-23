from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


METHODS = [
    {
        "method": "better_only",
        "label": "better-only BC",
        "setup_dir": Path("results/robomimic_square_quality_better_seed0_setup"),
        "eval_dir": Path("results/robomimic_square_quality_better_seed0_eval"),
    },
    {
        "method": "mixed_better_worse",
        "label": "mixed better+worse BC",
        "setup_dir": Path("results/robomimic_square_quality_mixed_seed0_setup"),
        "eval_dir": Path("results/robomimic_square_quality_mixed_seed0_eval"),
    },
    {
        "method": "adaptive_masscap",
        "label": "adaptive-masscap support BC",
        "setup_dir": Path("results/robomimic_square_quality_adaptive_seed0_setup"),
        "eval_dir": Path("results/robomimic_square_quality_adaptive_seed0_eval"),
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("results/robomimic_square_quality_policy_smoke_summary"),
    )
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fmt(value: str | float, digits: int = 3) -> str:
    return f"{float(value):.{digits}f}"


def rel(path: str | Path) -> str:
    path = Path(path)
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def checkpoint_epoch(row: dict[str, str]) -> int:
    name = row["checkpoint_name"]
    if name.startswith("model_epoch_"):
        return int(name.removeprefix("model_epoch_"))
    return -1


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str | int | float]] = []
    setup_rows: list[dict[str, str | int | float]] = []
    eval_horizon = None
    eval_episodes = None
    eval_init_mode = None
    split_path = None

    for method in METHODS:
        setup = json.loads((method["setup_dir"] / "diagnostics.json").read_text(encoding="utf-8"))
        eval_diag = json.loads((method["eval_dir"] / "diagnostics.json").read_text(encoding="utf-8"))
        metrics = read_csv(method["eval_dir"] / "metrics.csv")
        eval_horizon = eval_diag["eval_horizon"]
        eval_episodes = eval_diag["eval_episodes"]
        eval_init_mode = eval_diag["eval_init_mode"]
        split_path = eval_diag["split_path"]
        selected = int(setup.get("selection_diagnostics", {}).get("selected_demo_count", 0))
        hidden_pos = int(setup.get("selection_diagnostics", {}).get("selected_hidden_positive_demos", 0))
        hidden_bad = int(setup.get("selection_diagnostics", {}).get("selected_hidden_bad_demos", 0))
        purity = setup.get("selection_diagnostics", {}).get("selected_hidden_positive_purity", "")
        setup_rows.append(
            {
                "method": method["method"],
                "label": method["label"],
                "source": setup["source"],
                "train_demo_count": setup["train_demo_count"],
                "selected_unlabeled_demos": selected,
                "selected_hidden_positive_demos": hidden_pos,
                "selected_hidden_bad_demos": hidden_bad,
                "selected_hidden_positive_purity": purity,
            }
        )
        for metric in sorted(metrics, key=checkpoint_epoch):
            rows.append(
                {
                    "method": method["method"],
                    "label": method["label"],
                    "epoch": checkpoint_epoch(metric),
                    "success_rate": float(metric["success_rate"]),
                    "avg_return": float(metric["avg_return"]),
                    "avg_len": float(metric["avg_len"]),
                    "eval_episodes": int(metric["eval_episodes"]),
                    "checkpoint": rel(metric["checkpoint"]),
                }
            )

    with (args.out_dir / "policy_metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    with (args.out_dir / "training_support.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(setup_rows[0].keys()))
        writer.writeheader()
        writer.writerows(setup_rows)

    all_zero = all(float(row["success_rate"]) == 0.0 for row in rows)
    report = [
        "# Robomimic Square Quality Policy Smoke",
        "",
        "This is a bounded one-seed policy smoke for the Square MH relative-quality split.",
        "It tests whether the support-side Square score diagnostic can already produce a usable policy comparison with the same official Robomimic BC-RNN-GMM backbone used in the Can/Lift results.",
        "",
        "## Protocol",
        "",
        f"- Split: `{split_path}`.",
        f"- Evaluation initial states: `{eval_init_mode}`.",
        f"- Checkpoints: epoch 50 and epoch 100, corresponding to 5k and 10k optimizer steps under this config.",
        f"- Evaluation: `{eval_episodes}` episodes per checkpoint, horizon `{eval_horizon}`.",
        "- Seed: `0`.",
        "",
        "## Training Support",
        "",
        "| method | source | train demos | selected unlabeled | hidden positive | hidden bad | selected purity |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in setup_rows:
        purity = "n/a" if row["selected_hidden_positive_purity"] == "" else fmt(row["selected_hidden_positive_purity"])
        report.append(
            f"| {row['label']} | `{row['source']}` | {row['train_demo_count']} | "
            f"{row['selected_unlabeled_demos']} | {row['selected_hidden_positive_demos']} | "
            f"{row['selected_hidden_bad_demos']} | {purity} |"
        )
    report.extend(
        [
            "",
            "## Policy Results",
            "",
            "| method | epoch | success | return | avg len | episodes |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        report.append(
            f"| {row['label']} | {row['epoch']} | {fmt(row['success_rate'])} | "
            f"{fmt(row['avg_return'])} | {fmt(row['avg_len'], 1)} | {row['eval_episodes']} |"
        )
    report.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if all_zero:
        report.extend(
            [
                "- All evaluated Square policies failed all held-out `better_valid` initial-state rollouts at both checkpoints.",
                "- The failures run to the full 500-step horizon, so the smoke does not reveal a quality-sensitive policy ordering.",
                "- This should be treated as a negative/inconclusive policy result, not evidence against the score-calibration diagnostic.",
                "- Square MH should remain support-side transfer evidence unless a stronger Square policy setup or a direct quality-sensitive evaluator is added.",
            ]
        )
    else:
        report.extend(
            [
                "- At least one policy has nonzero success, so this diagnostic may be worth expanding beyond the one-seed smoke.",
                "- Because Square MH has relative-quality masks rather than reward failures, any future claim still needs a quality-sensitive evaluation beyond sparse success.",
            ]
        )
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
