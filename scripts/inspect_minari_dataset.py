from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tri_piql.datasets import inspect_minari_dataset, sanitize_dataset_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_id", help="Minari dataset id, for example D4RL/pointmaze/large-v2")
    parser.add_argument("--download", action="store_true", help="Download the dataset if it is not local")
    parser.add_argument("--out-dir", type=Path, default=Path("results/minari_inspection"))
    parser.add_argument("--top-frac", type=float, default=0.10)
    parser.add_argument("--bottom-frac", type=float, default=0.20)
    parser.add_argument(
        "--score-mode",
        choices=["return", "shortest", "return_length", "final_goal_distance"],
        default="return",
        help="Trajectory score used for positive/negative split ranking",
    )
    parser.add_argument("--episode-sample", type=int, default=None)
    parser.add_argument("--seed", type=int, default=0)
    return parser.parse_args()


def write_episodes_csv(path: Path, inspection) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "episode_id",
                "split",
                "length",
                "trajectory_return",
                "label_score",
                "return_percentile",
                "terminated",
                "truncated",
            ],
        )
        writer.writeheader()
        for episode in inspection.episodes:
            writer.writerow(
                {
                    "episode_id": episode.episode_id,
                    "split": episode.split,
                    "length": episode.length,
                    "trajectory_return": episode.trajectory_return,
                    "label_score": episode.label_score,
                    "return_percentile": episode.return_percentile,
                    "terminated": int(episode.terminated),
                    "truncated": int(episode.truncated),
                }
            )


def write_report(path: Path, inspection, command: list[str]) -> None:
    rs = inspection.return_stats
    ss = inspection.score_stats
    ls = inspection.length_stats
    ties = inspection.tie_diagnostics
    score_ties = inspection.score_tie_diagnostics
    split = inspection.split_sizes
    report = [
        f"# Minari Inspection: `{inspection.dataset_id}`",
        "",
        "## Command",
        "",
        "```bash",
        " ".join(command),
        "```",
        "",
        "## Dataset",
        "",
        f"- Total episodes: `{inspection.total_episodes}`.",
        f"- Total steps: `{inspection.total_steps}`.",
        f"- Inspected episodes: `{inspection.inspected_episodes}`.",
        f"- Observation space: `{inspection.observation_space}`.",
        f"- Action space: `{inspection.action_space}`.",
        "",
        "## Return And Length",
        "",
        f"- Return mean/std: `{rs.get('mean'):.6g}` / `{rs.get('std'):.6g}`.",
        f"- Return p10/p50/p90: `{rs.get('p10'):.6g}` / `{rs.get('p50'):.6g}` / `{rs.get('p90'):.6g}`.",
        f"- Length mean/std: `{ls.get('mean'):.6g}` / `{ls.get('std'):.6g}`.",
        f"- Length min/p50/max: `{ls.get('min'):.6g}` / `{ls.get('p50'):.6g}` / `{ls.get('max'):.6g}`.",
        "",
        "## Score-Based Split",
        "",
        f"- Score mode: `{inspection.score_mode}`.",
        f"- Score mean/std: `{ss.get('mean'):.6g}` / `{ss.get('std'):.6g}`.",
        f"- Score p10/p50/p90: `{ss.get('p10'):.6g}` / `{ss.get('p50'):.6g}` / `{ss.get('p90'):.6g}`.",
        f"- Positive trajectories: `{split['positive']}`.",
        f"- Negative trajectories: `{split['negative']}`.",
        f"- Unlabeled trajectories: `{split['unlabeled']}`.",
        f"- Unique label scores: `{score_ties['unique_return_count']}`.",
        f"- Largest exact score tie: `{score_ties['largest_tie_count']}` trajectories.",
        f"- Positive score cutoff: `{score_ties['positive_cutoff']}` with tie count `{score_ties['positive_cutoff_tie_count']}`.",
        f"- Negative score cutoff: `{score_ties['negative_cutoff']}` with tie count `{score_ties['negative_cutoff_tie_count']}`.",
        f"- Unique trajectory returns: `{ties['unique_return_count']}`.",
        f"- Largest exact return tie: `{ties['largest_tie_count']}` trajectories.",
        "",
        "## Terminal Flags",
        "",
        f"- Terminated: `{inspection.terminal_stats['terminated']}`.",
        f"- Truncated: `{inspection.terminal_stats['truncated']}`.",
        f"- Neither: `{inspection.terminal_stats['neither']}`.",
        "",
        "## Immediate Use",
        "",
        "- Use `episodes.csv` for trajectory-level labels and held-out split debugging.",
        "- Use `split_indices.json` when loading the same Minari dataset for BC, weighted BC, and Tri-PIQL.",
        "- True rewards are used only here to define labels and diagnostics; reward learning should hide them.",
    ]
    path.write_text("\n".join(report) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    inspection = inspect_minari_dataset(
        args.dataset_id,
        download=args.download,
        top_frac=args.top_frac,
        bottom_frac=args.bottom_frac,
        score_mode=args.score_mode,
        episode_sample=args.episode_sample,
        seed=args.seed,
    )
    run_dir = args.out_dir / sanitize_dataset_id(args.dataset_id)
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_dir / "summary.json"
    episodes_path = run_dir / "episodes.csv"
    split_path = run_dir / "split_indices.json"
    report_path = run_dir / "REPORT.md"

    summary_path.write_text(json.dumps(inspection.to_json_dict(), indent=2), encoding="utf-8")
    write_episodes_csv(episodes_path, inspection)
    split_path.write_text(
        json.dumps(
            {
                "dataset_id": inspection.dataset_id,
                "split_config": inspection.split_config,
                "positive_ids": inspection.positive_ids,
                "negative_ids": inspection.negative_ids,
                "unlabeled_ids": inspection.unlabeled_ids,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_report(report_path, inspection, sys.argv)

    print(f"dataset={inspection.dataset_id}")
    print(f"episodes={inspection.inspected_episodes} steps={inspection.total_steps}")
    print(
        "split="
        f"+{inspection.split_sizes['positive']} "
        f"-{inspection.split_sizes['negative']} "
        f"u{inspection.split_sizes['unlabeled']}"
    )
    print(
        "returns="
        f"p10={inspection.return_stats.get('p10'):.6g} "
        f"p50={inspection.return_stats.get('p50'):.6g} "
        f"p90={inspection.return_stats.get('p90'):.6g}"
    )
    print(
        "scores="
        f"mode={inspection.score_mode} "
        f"p10={inspection.score_stats.get('p10'):.6g} "
        f"p50={inspection.score_stats.get('p50'):.6g} "
        f"p90={inspection.score_stats.get('p90'):.6g}"
    )
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
