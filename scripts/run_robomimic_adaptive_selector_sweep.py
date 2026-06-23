from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
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
from run_robomimic_gmm_smoke import demo_sort_key, effective_gap_min_count, select_gap_demos, source_batches  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_adaptive_selector_sweep_pos_count"))
    parser.add_argument("--positive-counts", type=int, nargs="+", default=[5, 10, 20, 30, 40, 50, 60, 70, 80])
    parser.add_argument("--negative-count", type=int, default=80)
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
    parser.add_argument("--eval-horizon", type=int, default=400)
    return parser.parse_args()


def make_split(base_split: dict, positive_count: int, negative_count: int) -> dict:
    positives = set(base_split["all_positive_ids"])
    negatives = set(base_split["all_negative_ids"])
    labeled = set(base_split["labeled_positive_ids"] + base_split["labeled_negative_ids"])
    train_pos_pool = [
        demo_id
        for demo_id in base_split["train_ids"]
        if demo_id in positives and demo_id not in labeled
    ]
    train_neg_pool = [
        demo_id
        for demo_id in base_split["train_ids"]
        if demo_id in negatives and demo_id not in labeled
    ]
    if positive_count > len(train_pos_pool):
        raise ValueError(f"requested {positive_count} positives, only {len(train_pos_pool)} available")
    if negative_count > len(train_neg_pool):
        raise ValueError(f"requested {negative_count} negatives, only {len(train_neg_pool)} available")
    unlabeled = sorted(
        [*train_pos_pool[:positive_count], *train_neg_pool[:negative_count]],
        key=demo_sort_key,
    )
    split = dict(base_split)
    split["unlabeled_positive_count"] = int(positive_count)
    split["unlabeled_negative_count"] = int(negative_count)
    split["unlabeled_ids"] = unlabeled
    return split


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


def summarize_selection(selected: list[dict[str, float | int | str]], positive_count: int) -> dict[str, float | int]:
    hidden_positive = sum(1 for row in selected if row["hidden_label"] == "positive")
    hidden_bad = len(selected) - hidden_positive
    return {
        "selected_demo_count": int(len(selected)),
        "selected_hidden_positive_demos": int(hidden_positive),
        "selected_hidden_bad_demos": int(hidden_bad),
        "selected_hidden_positive_purity": float(hidden_positive / max(1, len(selected))),
        "selected_hidden_positive_recall": float(hidden_positive / max(1, positive_count)),
        "selected_score_min": float(min((float(row["score"]) for row in selected), default=float("nan"))),
        "selected_score_mean": float(np.mean([float(row["score"]) for row in selected])) if selected else float("nan"),
        "selected_score_max": float(max((float(row["score"]) for row in selected), default=float("nan"))),
    }


def mean(values: list[float]) -> float:
    return float(np.mean(np.asarray(values, dtype=np.float64)))


def std(values: list[float]) -> float:
    return float(np.std(np.asarray(values, dtype=np.float64)))


def format_float(value: float) -> str:
    if math.isnan(value):
        return "nan"
    return f"{value:.3f}"


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    base_split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = base_split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    hidden_positive_ids = set(base_split["all_positive_ids"])

    per_seed_rows: list[dict[str, float | int | str]] = []
    adaptive_rows: list[dict[str, float | int | str]] = []

    for positive_count in args.positive_counts:
        split = make_split(base_split, positive_count, args.negative_count)
        for seed in args.seeds:
            selector_args = SimpleNamespace(
                source="positive_plus_classifier_gap_unlabeled_demos",
                feature_mode="obs",
                eval_horizon=args.eval_horizon,
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

            labeled_pos_mean = float(np.mean([float(row["score"]) for row in pos_scores]))
            labeled_neg_mean = float(np.mean([float(row["score"]) for row in neg_scores]))
            score_denom = max(1.0e-8, labeled_pos_mean - labeled_neg_mean)
            estimated_positive_mass = float(
                np.sum(
                    [
                        np.clip((float(row["score"]) - labeled_neg_mean) / score_denom, 0.0, 1.0)
                        for row in ranked
                    ]
                )
            )
            effective_min = effective_gap_min_count(selector_args, split)
            demo_scores = [(int(row["demo_index"]), float(row["score"])) for row in ranked]
            selected_order, score_gap = select_gap_demos(
                demo_scores,
                max_count=args.gap_select_max_unlabeled_demos,
                min_count=effective_min,
            )
            selected_set = {f"demo_{demo_index}" for demo_index in selected_order}
            coverage_selected = [row for row in ranked if row["demo_id"] in selected_set]

            top20_selected = ranked[: min(20, len(ranked))]
            top40_selected = ranked[: min(40, len(ranked))]
            top80_selected = ranked[: min(80, len(ranked))]
            if estimated_positive_mass >= effective_min:
                adaptive_mode = "coverage_gap"
                adaptive_selected = coverage_selected
            else:
                adaptive_mode = "precision_top20"
                adaptive_selected = top20_selected
            mass_cap_limit = int(np.ceil(args.adaptive_mass_cap_ratio * estimated_positive_mass))
            if estimated_positive_mass < effective_min:
                masscap_mode = "precision_top20"
                masscap_selected = top20_selected
            elif len(coverage_selected) > mass_cap_limit:
                masscap_mode = "top_estimated_mass"
                masscap_count = int(np.ceil(estimated_positive_mass))
                masscap_count = min(len(ranked), max(effective_min, masscap_count))
                masscap_selected = ranked[:masscap_count]
            else:
                masscap_mode = "coverage_gap"
                masscap_selected = coverage_selected

            base_row = {
                "unlabeled_positive_count": int(positive_count),
                "unlabeled_negative_count": int(args.negative_count),
                "unlabeled_bad_fraction": float(args.negative_count / max(1, positive_count + args.negative_count)),
                "seed": int(seed),
                "estimated_positive_mass": float(estimated_positive_mass),
                "effective_min": int(effective_min),
                "labeled_positive_score_mean": float(labeled_pos_mean),
                "labeled_negative_score_mean": float(labeled_neg_mean),
                "score_gap": float(score_gap),
                "adaptive_mode": adaptive_mode,
                "masscap_mode": masscap_mode,
            }
            methods = {
                "adaptive_posmass": adaptive_selected,
                "adaptive_masscap": masscap_selected,
                "coverage_gap": coverage_selected,
                "top20": top20_selected,
                "top40": top40_selected,
                "top80": top80_selected,
            }
            method_modes = {
                "adaptive_posmass": adaptive_mode,
                "adaptive_masscap": masscap_mode,
                "coverage_gap": "coverage_gap",
                "top20": "top20",
                "top40": "top40",
                "top80": "top80",
            }
            for method, selected in methods.items():
                row = {
                    "method": method,
                    "selector_mode": method_modes[method],
                    **base_row,
                    **summarize_selection(selected, positive_count),
                }
                per_seed_rows.append(row)
                if method == "adaptive_masscap":
                    adaptive_rows.append(row)

    groups: dict[tuple[int, int, str], list[dict[str, float | int | str]]] = defaultdict(list)
    for row in per_seed_rows:
        groups[(int(row["unlabeled_positive_count"]), int(row["unlabeled_negative_count"]), str(row["method"]))].append(row)
    aggregate_rows = []
    for (positive_count, negative_count, method), rows in sorted(groups.items()):
        modes = sorted({str(row["selector_mode"]) for row in rows})
        posmass_modes = sorted({str(row["adaptive_mode"]) for row in rows})
        masscap_modes = sorted({str(row["masscap_mode"]) for row in rows})
        aggregate_rows.append(
            {
                "unlabeled_positive_count": positive_count,
                "unlabeled_negative_count": negative_count,
                "unlabeled_bad_fraction": float(negative_count / max(1, positive_count + negative_count)),
                "method": method,
                "seeds": len(rows),
                "selector_modes": ",".join(modes),
                "posmass_modes": ",".join(posmass_modes),
                "masscap_modes": ",".join(masscap_modes),
                "estimated_positive_mass_mean": mean([float(row["estimated_positive_mass"]) for row in rows]),
                "estimated_positive_mass_std": std([float(row["estimated_positive_mass"]) for row in rows]),
                "selected_demo_count_mean": mean([float(row["selected_demo_count"]) for row in rows]),
                "selected_hidden_positive_demos_mean": mean([float(row["selected_hidden_positive_demos"]) for row in rows]),
                "selected_hidden_bad_demos_mean": mean([float(row["selected_hidden_bad_demos"]) for row in rows]),
                "selected_hidden_positive_purity_mean": mean([float(row["selected_hidden_positive_purity"]) for row in rows]),
                "selected_hidden_positive_recall_mean": mean([float(row["selected_hidden_positive_recall"]) for row in rows]),
            }
        )

    write_csv(args.out_dir / "per_seed_selection.csv", per_seed_rows)
    write_csv(args.out_dir / "aggregate_selection.csv", aggregate_rows)

    adaptive_aggregate = [row for row in aggregate_rows if row["method"] == "adaptive_masscap"]
    report_table = [
        "| hidden pos | hidden bad | bad frac | mass mean | adaptive mode | selected | hidden pos | hidden bad | purity | recall |",
        "|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in adaptive_aggregate:
        report_table.append(
            "| "
            f"{row['unlabeled_positive_count']} | "
            f"{row['unlabeled_negative_count']} | "
            f"{format_float(float(row['unlabeled_bad_fraction']))} | "
            f"{format_float(float(row['estimated_positive_mass_mean']))} | "
            f"{row['selector_modes']} | "
            f"{format_float(float(row['selected_demo_count_mean']))} | "
            f"{format_float(float(row['selected_hidden_positive_demos_mean']))} | "
            f"{format_float(float(row['selected_hidden_bad_demos_mean']))} | "
            f"{format_float(float(row['selected_hidden_positive_purity_mean']))} | "
            f"{format_float(float(row['selected_hidden_positive_recall_mean']))} |"
        )

    control_rows = [
        row
        for row in aggregate_rows
        if row["method"] in {"adaptive_masscap", "adaptive_posmass", "coverage_gap", "top20", "top80"}
        and int(row["unlabeled_positive_count"]) in {20, 40, 80}
    ]
    control_table = [
        "| hidden pos | method | mode | selected | hidden pos | hidden bad | purity | recall |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in control_rows:
        control_table.append(
            "| "
            f"{row['unlabeled_positive_count']} | "
            f"{row['method']} | "
            f"{row['selector_modes']} | "
            f"{format_float(float(row['selected_demo_count_mean']))} | "
            f"{format_float(float(row['selected_hidden_positive_demos_mean']))} | "
            f"{format_float(float(row['selected_hidden_bad_demos_mean']))} | "
            f"{format_float(float(row['selected_hidden_positive_purity_mean']))} | "
            f"{format_float(float(row['selected_hidden_positive_recall_mean']))} |"
        )

    args_json = {
        "split_path": str(args.split_path),
        "positive_counts": args.positive_counts,
        "negative_count": args.negative_count,
        "seeds": args.seeds,
        "classifier_steps": args.classifier_steps,
        "gap_select_min_labeled_positive_multiplier": args.gap_select_min_labeled_positive_multiplier,
        "adaptive_mass_cap_ratio": args.adaptive_mass_cap_ratio,
    }
    (args.out_dir / "config.json").write_text(json.dumps(args_json, indent=2), encoding="utf-8")

    report = [
        "# Robomimic Adaptive Selector Positive-Mass Sweep",
        "",
        "This support-only sweep fixes the Robomimic Can scarce labels and keeps 80 hidden-bad unlabeled demos, then varies how many hidden-positive demos are present in the unlabeled pool. The adaptive rules are fixed before the sweep and use no hidden labels for their decisions.",
        "",
        "Main rule: estimate unlabeled positive-demo mass from classifier scores calibrated by labeled positive and negative demo-score means. If the estimated mass is below the `4 x labeled-positive` coverage floor, use top20 precision mode. Otherwise use coverage-gap unless the gap cut selects more than the configured multiple of estimated positive mass; in that case use the top estimated-positive-mass demos.",
        "",
        "## Files",
        "",
        "- `per_seed_selection.csv`: every seed, mixture, and selector.",
        "- `aggregate_selection.csv`: mean support statistics by mixture and selector.",
        "- `config.json`: sweep arguments.",
        "",
        "## Mass-Capped Adaptive Decisions",
        "",
        "\n".join(report_table),
        "",
        "## Controls at Representative Mixtures",
        "",
        "\n".join(control_table),
        "",
        "## Interpretation",
        "",
        "The sweep tests the selector decision rule itself rather than policy performance at every mixture. The already-trained endpoint policies anchor two modes that the mass-capped rule preserves: balanced 80p/80b uses coverage-gap and reaches 0.900 mean success at 20k, while heavy contamination 20p/80b uses precision top20 and reaches 0.667 mean success at 20k.",
        "",
        "The mass cap is important in the intermediate 30-40 hidden-positive regime: the original positive-mass switch would move to coverage, but the score-gap cut can select substantially more demos than the calibrated positive-mass estimate. The capped rule keeps the decision hidden-label-free while avoiding an oversized gap cut.",
        "",
        "A paper claim should describe this as mechanism evidence for an adaptive purity/coverage rule. Intermediate mixtures still need policy rollouts before claiming end-to-end performance there.",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
