from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tri_piql.algos.neural_gridworld import NeuralConfig, train_neural_gridworld_tri_piql
from tri_piql.algos.tabular import (
    fit_desirability_classifier,
    fit_tabular_bc,
    fit_transition_weighted_bc,
    greedy_policy_from_probs,
    q_policy_from_reward,
)
from tri_piql.envs.gridworld import (
    GridSpec,
    ascii_state_map,
    evaluate_policy,
    make_loop_mixed_dataset,
    pad_trajectories,
    truncate_trajectory,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=Path("results/neural_gridworld_loop_mixed"))
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0])
    parser.add_argument("--bad-fracs", type=float, nargs="+", default=[0.25, 0.75])
    parser.add_argument("--n-pos", type=int, default=12)
    parser.add_argument("--n-neg", type=int, default=12)
    parser.add_argument("--n-unlabeled", type=int, default=180)
    parser.add_argument("--positive-prefix-len", type=int, default=6)
    parser.add_argument("--hidden-dim", type=int, default=64)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=3.0e-3)
    parser.add_argument("--feature-mode", choices=["coords", "onehot"], default="coords")
    parser.add_argument("--negative-shortcut-frac", type=float, default=0.0)
    parser.add_argument("--width", type=int, default=7)
    parser.add_argument("--height", type=int, default=7)
    parser.add_argument("--max-steps", type=int, default=18)
    parser.add_argument("--trap-x", type=int, default=5)
    parser.add_argument("--trap-y", type=int, default=2)
    return parser.parse_args()


def hidden_good_flags(unlabeled) -> np.ndarray:
    return np.asarray([traj.latent_kind.startswith("hidden_good") for traj in unlabeled], dtype=np.float32)


def row_with_metrics(seed: int, bad_frac: float, method: str, metrics: dict[str, float]) -> dict[str, float | str | int]:
    row: dict[str, float | str | int] = {"seed": seed, "bad_frac": bad_frac, "method": method}
    row.update(metrics)
    return row


def summarize(rows: list[dict[str, float | str | int]]) -> list[dict[str, float | str]]:
    keys = ["success_rate", "trap_rate", "avg_return", "avg_len"]
    grouped: dict[tuple[float, str], list[dict[str, float | str | int]]] = {}
    for row in rows:
        grouped.setdefault((float(row["bad_frac"]), str(row["method"])), []).append(row)
    summary = []
    for (bad_frac, method), items in sorted(grouped.items()):
        out: dict[str, float | str] = {"bad_frac": bad_frac, "method": method}
        for key in keys:
            vals = np.asarray([float(item[key]) for item in items], dtype=np.float64)
            out[f"{key}_mean"] = float(vals.mean())
            out[f"{key}_std"] = float(vals.std(ddof=0))
        summary.append(out)
    return summary


def markdown_table(summary: list[dict[str, float | str]]) -> str:
    lines = ["| bad_frac | method | success | trap | return |", "|---|---|---:|---:|---:|"]
    for row in summary:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{float(row['bad_frac']):.2f}",
                    str(row["method"]),
                    f"{float(row['success_rate_mean']):.3f} +/- {float(row['success_rate_std']):.3f}",
                    f"{float(row['trap_rate_mean']):.3f} +/- {float(row['trap_rate_std']):.3f}",
                    f"{float(row['avg_return_mean']):.3f} +/- {float(row['avg_return_std']):.3f}",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def run_one(args: argparse.Namespace, seed: int, bad_frac: float):
    spec = GridSpec(
        width=args.width,
        height=args.height,
        start=(0, args.height - 1),
        goal=(args.width - 1, 0),
        trap=(args.trap_x, args.trap_y),
        max_steps=args.max_steps,
    )
    data = make_loop_mixed_dataset(
        spec,
        seed=seed,
        n_pos=args.n_pos,
        n_neg=args.n_neg,
        n_unlabeled=args.n_unlabeled,
        unlabeled_bad_frac=bad_frac,
        negative_shortcut_frac=args.negative_shortcut_frac,
    )
    positives = [truncate_trajectory(traj, args.positive_prefix_len, label="+") for traj in data["pos"]]
    negatives = data["neg"]
    unlabeled = data["unlabeled"]
    all_trajs = positives + negatives + unlabeled

    bc_pos_probs = fit_tabular_bc(spec, positives)
    bc_pos_unlabeled_probs = fit_tabular_bc(spec, positives + unlabeled)
    bc_all_probs = fit_tabular_bc(spec, all_trajs)

    classifier = fit_desirability_classifier(spec, positives, negatives, unlabeled)
    wbc_trajs = positives + negatives + unlabeled
    wbc_weights = np.concatenate(
        [
            np.ones(len(positives), dtype=np.float64),
            np.zeros(len(negatives), dtype=np.float64),
            classifier.q_unlabeled,
        ]
    )
    wbc_probs = fit_tabular_bc(spec, wbc_trajs, wbc_weights)

    max_len = max(t.length for t in all_trajs)
    latent_good = hidden_good_flags(unlabeled)
    config = NeuralConfig(
        hidden_dim=args.hidden_dim,
        depth=args.depth,
        lr=args.lr,
        feature_mode=args.feature_mode,
    )
    tri = train_neural_gridworld_tri_piql(
        spec=spec,
        pos_batch=pad_trajectories(positives, max_len=max_len),
        neg_batch=pad_trajectories(negatives, max_len=max_len),
        unlabeled_batch=pad_trajectories(unlabeled, max_len=max_len),
        unlabeled_latent_good=latent_good,
        seed=seed,
        steps=args.steps,
        config=config,
    )
    tri_policy, tri_q = q_policy_from_reward(spec, tri.reward)
    tri_adv = tri_q - tri_q.mean(axis=1, keepdims=True)

    awbc_trajs = positives + negatives + unlabeled
    awbc_transition_weights = []
    for traj in positives:
        adv = tri_adv[traj.states, traj.actions]
        awbc_transition_weights.append(np.exp(np.clip(adv, -2.0, 2.0)))
    for traj in negatives:
        awbc_transition_weights.append(np.zeros((traj.length,), dtype=np.float64))
    for traj, q_value in zip(unlabeled, tri.q_unlabeled, strict=True):
        adv = tri_adv[traj.states, traj.actions]
        awbc_transition_weights.append(float(q_value) * np.exp(np.clip(adv, -2.0, 2.0)))
    tri_awbc_probs = fit_transition_weighted_bc(spec, awbc_trajs, awbc_transition_weights)

    evals = {
        "bc_positive": evaluate_policy(spec, greedy_policy_from_probs(bc_pos_probs)),
        "bc_pos_unlabeled": evaluate_policy(spec, greedy_policy_from_probs(bc_pos_unlabeled_probs)),
        "bc_all": evaluate_policy(spec, greedy_policy_from_probs(bc_all_probs)),
        "weighted_bc": evaluate_policy(spec, greedy_policy_from_probs(wbc_probs)),
        "neural_tri_piql_awbc": evaluate_policy(spec, greedy_policy_from_probs(tri_awbc_probs)),
        "neural_tri_piql_greedy_q_diagnostic": evaluate_policy(spec, tri_policy),
    }
    diagnostics = {
        "seed": seed,
        "bad_frac": bad_frac,
        "feature_mode": args.feature_mode,
        "classifier": {
            "labeled_accuracy": classifier.labeled_accuracy,
            "pos_prob_mean": classifier.pos_prob_mean,
            "neg_prob_mean": classifier.neg_prob_mean,
            "unlabeled_prob_mean": classifier.unlabeled_prob_mean,
        },
        "neural_tri_piql": {
            "q_pos_mean": tri.q_pos_mean,
            "q_neg_mean": tri.q_neg_mean,
            "q_unlabeled_mean": tri.q_unlabeled_mean,
            "q_unlabeled_hidden_good_mean": tri.q_unlabeled_hidden_good_mean,
            "q_unlabeled_hidden_bad_mean": tri.q_unlabeled_hidden_bad_mean,
            "q_unlabeled_auc": tri.q_unlabeled_auc,
            "pos_return_mean": tri.pos_return_mean,
            "neg_return_mean": tri.neg_return_mean,
            "rank_gap": tri.rank_gap,
            "good_adv_mean": tri.good_adv_mean,
            "bad_adv_mean": tri.bad_adv_mean,
            "pos_transition_reward_mean": tri.pos_transition_reward_mean,
            "neg_transition_reward_mean": tri.neg_transition_reward_mean,
            "goal_transition_reward_mean": tri.goal_transition_reward_mean,
            "trap_transition_reward_mean": tri.trap_transition_reward_mean,
            "loss_history": tri.loss_history,
        },
        "learned_reward_max_heatmap": ascii_state_map(spec, tri.reward.max(axis=1)),
        "learned_q_max_heatmap": ascii_state_map(spec, tri_q.max(axis=1)),
    }
    return evals, diagnostics


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    metric_rows = []
    diagnostic_items = []
    for bad_frac in args.bad_fracs:
        for seed in args.seeds:
            evals, diagnostics = run_one(args, seed, bad_frac)
            diagnostic_items.append(diagnostics)
            for method, metrics in evals.items():
                metric_rows.append(row_with_metrics(seed, bad_frac, method, metrics))
            print(
                f"finished seed={seed} bad_frac={bad_frac:.2f}: "
                f"neural Tri success={evals['neural_tri_piql_awbc']['success_rate']:.3f}, "
                f"weighted success={evals['weighted_bc']['success_rate']:.3f}, "
                f"q_auc={diagnostics['neural_tri_piql']['q_unlabeled_auc']:.3f}"
            )

    metrics_path = args.out_dir / "metrics.csv"
    with metrics_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["seed", "bad_frac", "method", "success_rate", "trap_rate", "avg_return", "avg_len"],
        )
        writer.writeheader()
        writer.writerows(metric_rows)

    diagnostics_path = args.out_dir / "diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostic_items, indent=2), encoding="utf-8")

    summary = summarize(metric_rows)
    summary_path = args.out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    latest = diagnostic_items[-1]
    tri = latest["neural_tri_piql"]
    report = [
        "# Neural GridWorld Loop-Mixed Report",
        "",
        f"Training steps per run: `{args.steps}`.",
        f"Seeds: `{args.seeds}`.",
        f"Unlabeled bad fractions: `{args.bad_fracs}`.",
        f"Grid: `{args.width}x{args.height}`, trap `({args.trap_x}, {args.trap_y})`, max steps `{args.max_steps}`.",
        f"Labeled positive prefix length: `{args.positive_prefix_len}`.",
        f"Feature mode: `{args.feature_mode}`.",
        f"Negative shortcut fraction in labeled bad set: `{args.negative_shortcut_frac}`.",
        f"MLP: depth `{args.depth}`, hidden dim `{args.hidden_dim}`, lr `{args.lr}`.",
        "",
        "## Policy Metrics",
        "",
        markdown_table(summary),
        "",
        "## Latest Run Diagnostics",
        "",
        f"- Neural Tri-PIQL q AUC on hidden unlabeled tags: `{tri['q_unlabeled_auc']:.3f}`.",
        f"- Learned return gap R(pos)-R(neg): `{tri['rank_gap']:.3f}`.",
        f"- Good transition advantage mean: `{tri['good_adv_mean']:.3f}`.",
        f"- Bad transition advantage mean: `{tri['bad_adv_mean']:.3f}`.",
        f"- Positive-demo transition reward mean: `{tri['pos_transition_reward_mean']:.3f}`.",
        f"- Negative-demo transition reward mean: `{tri['neg_transition_reward_mean']:.3f}`.",
        "",
        "### Learned Reward Max Heatmap",
        "",
        "```text",
        latest["learned_reward_max_heatmap"],
        "```",
        "",
        "### Learned Q Max Heatmap",
        "",
        "```text",
        latest["learned_q_max_heatmap"],
        "```",
        "",
        "## Immediate Interpretation",
        "",
        "- This run tests whether the loop-mixed tabular mechanism survives a neural reward parameterization.",
        "- A useful result requires neural Tri-PIQL AWBC to beat weighted BC while preserving positive good/bad advantage separation.",
    ]
    report_path = args.out_dir / "REPORT.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {metrics_path}")
    print(f"wrote {diagnostics_path}")
    print(f"wrote {report_path}")


if __name__ == "__main__":
    main()
