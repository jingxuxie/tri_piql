from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_minari_action_rerank_smoke import state_action_features, train_state_action_classifier  # noqa: E402
from run_minari_bc_baselines import predict  # noqa: E402
from run_robomimic_can_rollout_smoke import dataset_obs_keys, sigmoid  # noqa: E402
from run_robomimic_gmm_smoke import effective_gap_min_count, select_gap_demos, source_batches  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1.0e-4)
    parser.add_argument("--gap-select-max-unlabeled-demos", type=int, default=80)
    parser.add_argument("--gap-select-min-unlabeled-demos", type=int, default=4)
    parser.add_argument("--gap-select-min-labeled-positive-multiplier", type=float, default=4.0)
    parser.add_argument("--adaptive-mass-cap-ratio", type=float, default=1.25)
    parser.add_argument("--precision-at", type=int, nargs="+", default=[10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 80])
    return parser.parse_args()


def demo_score_rows(batch, probs: np.ndarray, hidden_positive_ids: set[str]) -> list[dict[str, float | int | str]]:
    rows = []
    for demo_index in np.unique(batch.demo_ids):
        mask = batch.demo_ids == demo_index
        demo_id = f"demo_{int(demo_index)}"
        rows.append(
            {
                "demo_id": demo_id,
                "demo_index": int(demo_index),
                "score": float(probs[mask].mean()),
                "hidden_label": "positive" if demo_id in hidden_positive_ids else "bad",
            }
        )
    return rows


def score_stats(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(arr.mean()),
        "min": float(arr.min()),
        "p10": float(np.quantile(arr, 0.10)),
        "p50": float(np.quantile(arr, 0.50)),
        "p90": float(np.quantile(arr, 0.90)),
        "max": float(arr.max()),
    }


def summarize_selection(name: str, selected: list[dict[str, float | int | str]]) -> dict[str, float | int | str]:
    hidden_positive = sum(1 for row in selected if row["hidden_label"] == "positive")
    hidden_bad = len(selected) - hidden_positive
    return {
        "rule": name,
        "selected_demo_count": int(len(selected)),
        "selected_hidden_positive_demos": int(hidden_positive),
        "selected_hidden_bad_demos": int(hidden_bad),
        "selected_hidden_positive_purity": float(hidden_positive / max(1, len(selected))),
        "selected_score_min": float(min((float(row["score"]) for row in selected), default=float("nan"))),
        "selected_score_mean": float(np.mean([float(row["score"]) for row in selected])) if selected else float("nan"),
        "selected_score_max": float(max((float(row["score"]) for row in selected), default=float("nan"))),
    }


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    hidden_positive_ids = set(split["all_positive_ids"])

    all_rank_rows = []
    summary_rows = []
    threshold_rows = []
    p_at_k_rows = []

    for seed in args.seeds:
        selector_args = SimpleNamespace(
            source="positive_plus_classifier_gap_unlabeled_demos",
            feature_mode="obs",
            eval_horizon=400,
            seed=seed,
            classifier_steps=args.classifier_steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
            unlabeled_threshold=0.9,
            top_unlabeled_demos=80,
            candidate_unlabeled_demos=120,
            diversity_weight=0.35,
            gap_select_max_unlabeled_demos=args.gap_select_max_unlabeled_demos,
            gap_select_min_unlabeled_demos=args.gap_select_min_unlabeled_demos,
            gap_select_min_labeled_positive_multiplier=args.gap_select_min_labeled_positive_multiplier,
            unlabeled_weight_mode="prob",
        )
        _obs_mean, _obs_std, pos, neg, unl, _all_pos = source_batches(selector_args, split, hdf5_path, obs_keys)
        classifier, _history = train_state_action_classifier(
            pos.observations,
            pos.actions,
            neg.observations,
            neg.actions,
            seed=seed + 77,
            steps=args.classifier_steps,
            batch_size=args.batch_size,
            hidden_dim=args.hidden_dim,
            depth=args.depth,
            lr=args.lr,
        )
        pos_prob = sigmoid(predict(classifier, state_action_features(pos.observations, pos.actions)).reshape(-1))
        neg_prob = sigmoid(predict(classifier, state_action_features(neg.observations, neg.actions)).reshape(-1))
        unl_prob = sigmoid(predict(classifier, state_action_features(unl.observations, unl.actions)).reshape(-1))

        pos_scores = demo_score_rows(pos, pos_prob, hidden_positive_ids)
        neg_scores = demo_score_rows(neg, neg_prob, hidden_positive_ids)
        ranked = demo_score_rows(unl, unl_prob, hidden_positive_ids)
        ranked.sort(key=lambda row: float(row["score"]), reverse=True)
        for rank, row in enumerate(ranked, start=1):
            all_rank_rows.append({"seed": seed, "rank": rank, **row})

        labeled_pos_scores = [float(row["score"]) for row in pos_scores]
        labeled_neg_scores = [float(row["score"]) for row in neg_scores]
        summary_rows.append(
            {
                "seed": seed,
                "labeled_positive_demo_count": len(pos_scores),
                "labeled_negative_demo_count": len(neg_scores),
                **{f"labeled_positive_{k}": v for k, v in score_stats(labeled_pos_scores).items()},
                **{f"labeled_negative_{k}": v for k, v in score_stats(labeled_neg_scores).items()},
            }
        )

        for k in args.precision_at:
            selected = ranked[: min(k, len(ranked))]
            p_at_k_rows.append({"seed": seed, "k": k, **summarize_selection(f"top_{k}", selected)})

        demo_scores = [(int(row["demo_index"]), float(row["score"])) for row in ranked]
        current_min_count = effective_gap_min_count(selector_args, split)
        selected_order, score_gap = select_gap_demos(
            demo_scores,
            max_count=args.gap_select_max_unlabeled_demos,
            min_count=current_min_count,
        )
        selected_set = {f"demo_{demo_index}" for demo_index in selected_order}
        selected = [row for row in ranked if row["demo_id"] in selected_set]
        threshold_rows.append(
            {
                "seed": seed,
                "threshold_name": "score_gap_posx",
                "threshold": "",
                "score_gap": float(score_gap),
                "effective_min": int(current_min_count),
                **summarize_selection("score_gap_posx", selected),
            }
        )

        score_denom = max(1.0e-8, float(np.mean(labeled_pos_scores)) - float(np.mean(labeled_neg_scores)))
        estimated_positive_mass = float(
            np.sum(
                [
                    np.clip((float(row["score"]) - float(np.mean(labeled_neg_scores))) / score_denom, 0.0, 1.0)
                    for row in ranked
                ]
            )
        )
        adaptive_count = int(np.ceil(2.0 * len(split["labeled_positive_ids"])))
        if estimated_positive_mass >= current_min_count:
            adaptive_rule = "adaptive_posmass_coverage_gap"
            adaptive_selected = selected
        else:
            adaptive_rule = "adaptive_posmass_precision_top_posx2"
            adaptive_selected = ranked[: min(adaptive_count, len(ranked))]
        threshold_rows.append(
            {
                "seed": seed,
                "threshold_name": "adaptive_posmass",
                "threshold": estimated_positive_mass,
                "score_gap": float(score_gap),
                "effective_min": int(current_min_count),
                **summarize_selection(adaptive_rule, adaptive_selected),
            }
        )
        coverage_count = len(selected)
        mass_cap_limit = int(np.ceil(args.adaptive_mass_cap_ratio * estimated_positive_mass))
        if estimated_positive_mass < current_min_count:
            masscap_rule = "adaptive_masscap_precision_top_posx2"
            masscap_selected = ranked[: min(adaptive_count, len(ranked))]
        elif coverage_count > mass_cap_limit:
            masscap_rule = "adaptive_masscap_top_estimated_mass"
            masscap_count = int(np.ceil(estimated_positive_mass))
            masscap_count = min(len(ranked), max(current_min_count, masscap_count))
            masscap_selected = ranked[:masscap_count]
        else:
            masscap_rule = "adaptive_masscap_coverage_gap"
            masscap_selected = selected
        threshold_rows.append(
            {
                "seed": seed,
                "threshold_name": "adaptive_masscap",
                "threshold": estimated_positive_mass,
                "score_gap": float(score_gap),
                "effective_min": int(current_min_count),
                **summarize_selection(masscap_rule, masscap_selected),
            }
        )

        for multiplier in [2.0, 3.0, 4.0]:
            k = int(np.ceil(multiplier * len(split["labeled_positive_ids"])))
            selected = ranked[: min(k, len(ranked))]
            threshold_rows.append(
                {
                    "seed": seed,
                    "threshold_name": f"top_posx{multiplier:g}",
                    "threshold": "",
                    "score_gap": "",
                    "effective_min": k,
                    **summarize_selection(f"top_posx{multiplier:g}", selected),
                }
            )

        thresholds = {
            "neg_max": max(labeled_neg_scores),
            "mid_mean": 0.5 * (float(np.mean(labeled_pos_scores)) + float(np.mean(labeled_neg_scores))),
            "mid_minpos_maxneg": 0.5 * (min(labeled_pos_scores) + max(labeled_neg_scores)),
            "pos_p10": float(np.quantile(labeled_pos_scores, 0.10)),
            "pos_min": min(labeled_pos_scores),
        }
        for name, threshold in thresholds.items():
            selected = [row for row in ranked if float(row["score"]) >= threshold]
            threshold_rows.append(
                {
                    "seed": seed,
                    "threshold_name": name,
                    "threshold": float(threshold),
                    "score_gap": "",
                    "effective_min": "",
                    **summarize_selection(name, selected),
                }
            )

    for path, rows in [
        (args.out_dir / "demo_rankings.csv", all_rank_rows),
        (args.out_dir / "score_summary.csv", summary_rows),
        (args.out_dir / "precision_at_k.csv", p_at_k_rows),
        (args.out_dir / "selection_rules.csv", threshold_rows),
    ]:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    report = [
        "# Robomimic Selector Score Analysis",
        "",
        f"Split path: `{args.split_path}`.",
        f"Seeds: `{args.seeds}`.",
        f"Gap max demos: `{args.gap_select_max_unlabeled_demos}`.",
        f"Gap min demos: `{args.gap_select_min_unlabeled_demos}`.",
        f"Gap min labeled-positive multiplier: `{args.gap_select_min_labeled_positive_multiplier}`.",
        f"Adaptive mass-cap ratio: `{args.adaptive_mass_cap_ratio}`.",
        "",
        "## Files",
        "",
        "- `demo_rankings.csv`: full unlabeled demo score rankings by seed.",
        "- `score_summary.csv`: labeled positive / negative score calibration summary.",
        "- `precision_at_k.csv`: hidden support composition for fixed top-k prefixes.",
        "- `selection_rules.csv`: hidden support composition for score-gap, calibrated candidate rules, `adaptive_posmass`, and `adaptive_masscap`.",
        "",
        "## Adaptive Rule",
        "",
        "`adaptive_posmass` estimates unlabeled positive-demo mass from classifier scores calibrated by labeled positive and negative demo means. If the estimated mass is at least the effective score-gap coverage floor, it uses coverage-aware score-gap. Otherwise, it switches to precision mode with top `2 x labeled-positive demo count` unlabeled demos.",
        "",
        "`adaptive_masscap` uses the same precision/coverage decision, but caps coverage when the score-gap cut selects more than the configured multiple of estimated positive mass. In that case it takes the top estimated-positive-mass demos rather than trusting an oversized gap cut.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
