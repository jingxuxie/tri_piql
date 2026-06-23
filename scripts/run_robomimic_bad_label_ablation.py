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
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_bad_label_ablation"))
    parser.add_argument("--positive-counts", type=int, nargs="+", default=[5, 10, 20, 30, 40, 50, 60, 70, 80])
    parser.add_argument("--negative-count", type=int, default=80)
    parser.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--classifier-steps", type=int, default=500)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1.0e-4)
    parser.add_argument("--gap-select-max-unlabeled-demos", type=int, default=80)
    parser.add_argument("--gap-select-min-unlabeled-demos", type=int, default=4)
    parser.add_argument("--gap-select-min-labeled-positive-multiplier", type=float, default=4.0)
    parser.add_argument("--adaptive-mass-cap-ratio", type=float, default=1.25)
    parser.add_argument("--top-k", type=int, nargs="+", default=[20, 40, 80])
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
    split = dict(base_split)
    split["unlabeled_positive_count"] = int(positive_count)
    split["unlabeled_negative_count"] = int(negative_count)
    split["unlabeled_ids"] = sorted(
        [*train_pos_pool[:positive_count], *train_neg_pool[:negative_count]],
        key=demo_sort_key,
    )
    return split


def demo_score_rows(batch, scores: np.ndarray, hidden_positive_ids: set[str]) -> list[dict[str, float | int | str]]:
    rows = []
    for demo_index in np.unique(batch.demo_ids):
        mask = batch.demo_ids == demo_index
        demo_id = f"demo_{int(demo_index)}"
        rows.append(
            {
                "demo_id": demo_id,
                "demo_index": int(demo_index),
                "score": float(scores[mask].mean()),
                "hidden_label": "positive" if demo_id in hidden_positive_ids else "bad",
            }
        )
    return rows


def summarize_selection(
    selected: list[dict[str, float | int | str]],
    positive_count: int,
) -> dict[str, float | int]:
    hidden_positive = sum(1 for row in selected if row["hidden_label"] == "positive")
    hidden_bad = len(selected) - hidden_positive
    scores = [float(row["score"]) for row in selected]
    return {
        "selected_demo_count": int(len(selected)),
        "selected_hidden_positive_demos": int(hidden_positive),
        "selected_hidden_bad_demos": int(hidden_bad),
        "selected_hidden_positive_purity": float(hidden_positive / max(1, len(selected))),
        "selected_hidden_positive_recall": float(hidden_positive / max(1, positive_count)),
        "selected_score_min": float(min(scores, default=float("nan"))),
        "selected_score_mean": float(np.mean(scores)) if scores else float("nan"),
        "selected_score_max": float(max(scores, default=float("nan"))),
    }


def ranked_from_scores(batch, scores: np.ndarray, hidden_positive_ids: set[str]) -> list[dict[str, float | int | str]]:
    ranked = demo_score_rows(batch, scores, hidden_positive_ids)
    ranked.sort(key=lambda row: float(row["score"]), reverse=True)
    return ranked


def positive_nn_transition_scores(pos_obs: np.ndarray, pos_actions: np.ndarray, unl_obs: np.ndarray, unl_actions: np.ndarray) -> np.ndarray:
    pos_x = state_action_features(pos_obs, pos_actions).astype(np.float32, copy=False)
    unl_x = state_action_features(unl_obs, unl_actions).astype(np.float32, copy=False)
    mean = np.mean(np.concatenate([pos_x, unl_x], axis=0), axis=0, keepdims=True)
    std = np.std(np.concatenate([pos_x, unl_x], axis=0), axis=0, keepdims=True) + 1.0e-6
    pos_x = (pos_x - mean) / std
    unl_x = (unl_x - mean) / std
    min_dist = np.full((unl_x.shape[0],), np.inf, dtype=np.float32)
    chunk = 2048
    for start in range(0, unl_x.shape[0], chunk):
        part = unl_x[start : start + chunk]
        distances = np.mean((part[:, None, :] - pos_x[None, :, :]) ** 2, axis=2)
        min_dist[start : start + chunk] = distances.min(axis=1)
    return -min_dist


def add_selection_row(
    rows: list[dict[str, float | int | str]],
    *,
    positive_count: int,
    negative_count: int,
    seed: int,
    score_family: str,
    selector: str,
    selected: list[dict[str, float | int | str]],
    extra: dict[str, float | int | str] | None = None,
) -> None:
    row: dict[str, float | int | str] = {
        "unlabeled_positive_count": int(positive_count),
        "unlabeled_negative_count": int(negative_count),
        "unlabeled_bad_fraction": float(negative_count / max(1, positive_count + negative_count)),
        "seed": int(seed),
        "score_family": score_family,
        "selector": selector,
        **summarize_selection(selected, positive_count),
    }
    if extra:
        row.update(extra)
    rows.append(row)


def mean(values: list[float]) -> float:
    return float(np.mean(np.asarray(values, dtype=np.float64)))


def std(values: list[float]) -> float:
    return float(np.std(np.asarray(values, dtype=np.float64)))


def fmt(value: float) -> str:
    if math.isnan(value):
        return "nan"
    return f"{value:.3f}"


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    fieldnames: list[str] = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def aggregate_rows(rows: list[dict[str, float | int | str]]) -> list[dict[str, float | int | str]]:
    grouped: dict[tuple[int, str, str], list[dict[str, float | int | str]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["unlabeled_positive_count"]), str(row["score_family"]), str(row["selector"]))].append(row)
    out = []
    metric_keys = [
        "selected_demo_count",
        "selected_hidden_positive_demos",
        "selected_hidden_bad_demos",
        "selected_hidden_positive_purity",
        "selected_hidden_positive_recall",
    ]
    for (positive_count, score_family, selector), group in sorted(grouped.items()):
        row: dict[str, float | int | str] = {
            "unlabeled_positive_count": int(positive_count),
            "unlabeled_negative_count": int(group[0]["unlabeled_negative_count"]),
            "unlabeled_bad_fraction": float(group[0]["unlabeled_bad_fraction"]),
            "score_family": score_family,
            "selector": selector,
            "seed_count": len(group),
        }
        for key in metric_keys:
            values = [float(item[key]) for item in group]
            row[f"{key}_mean"] = mean(values)
            row[f"{key}_std"] = std(values)
        out.append(row)
    return out


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    aligns = ["---"] + ["---:" for _ in headers[1:]]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(aligns) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    base_split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = base_split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    hidden_positive_ids = set(base_split["all_positive_ids"])
    per_seed_rows: list[dict[str, float | int | str]] = []

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

            bad_classifier, _bad_history = train_state_action_classifier(
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
            pos_prob = sigmoid(predict(bad_classifier, state_action_features(pos.observations, pos.actions)).reshape(-1))
            neg_prob = sigmoid(predict(bad_classifier, state_action_features(neg.observations, neg.actions)).reshape(-1))
            bad_unl_prob = sigmoid(predict(bad_classifier, state_action_features(unl.observations, unl.actions)).reshape(-1))
            bad_ranked = ranked_from_scores(unl, bad_unl_prob, hidden_positive_ids)

            labeled_pos_scores = demo_score_rows(pos, pos_prob, hidden_positive_ids)
            labeled_neg_scores = demo_score_rows(neg, neg_prob, hidden_positive_ids)
            labeled_pos_mean = float(np.mean([float(row["score"]) for row in labeled_pos_scores]))
            labeled_neg_mean = float(np.mean([float(row["score"]) for row in labeled_neg_scores]))
            score_denom = max(1.0e-8, labeled_pos_mean - labeled_neg_mean)
            estimated_positive_mass = float(
                np.sum(
                    [
                        np.clip((float(row["score"]) - labeled_neg_mean) / score_denom, 0.0, 1.0)
                        for row in bad_ranked
                    ]
                )
            )
            effective_min = effective_gap_min_count(selector_args, split)
            demo_scores = [(int(row["demo_index"]), float(row["score"])) for row in bad_ranked]
            coverage_order, score_gap = select_gap_demos(
                demo_scores,
                max_count=args.gap_select_max_unlabeled_demos,
                min_count=effective_min,
            )
            coverage_set = {f"demo_{demo_index}" for demo_index in coverage_order}
            coverage_selected = [row for row in bad_ranked if row["demo_id"] in coverage_set]
            top20_selected = bad_ranked[: min(20, len(bad_ranked))]
            mass_cap_limit = int(np.ceil(args.adaptive_mass_cap_ratio * estimated_positive_mass))
            if estimated_positive_mass < effective_min:
                masscap_rule = "precision_top20"
                masscap_selected = top20_selected
            elif len(coverage_selected) > mass_cap_limit:
                masscap_rule = "top_estimated_mass"
                masscap_count = int(np.ceil(estimated_positive_mass))
                masscap_count = min(len(bad_ranked), max(effective_min, masscap_count))
                masscap_selected = bad_ranked[:masscap_count]
            else:
                masscap_rule = "coverage_gap"
                masscap_selected = coverage_selected

            common_extra = {
                "estimated_positive_mass": float(estimated_positive_mass),
                "effective_min": int(effective_min),
                "score_gap": float(score_gap),
                "labeled_positive_score_mean": float(labeled_pos_mean),
                "labeled_negative_score_mean": float(labeled_neg_mean),
            }
            add_selection_row(
                per_seed_rows,
                positive_count=positive_count,
                negative_count=args.negative_count,
                seed=seed,
                score_family="bad_aware_pos_vs_neg",
                selector="adaptive_masscap",
                selected=masscap_selected,
                extra={**common_extra, "adaptive_masscap_mode": masscap_rule},
            )
            add_selection_row(
                per_seed_rows,
                positive_count=positive_count,
                negative_count=args.negative_count,
                seed=seed,
                score_family="bad_aware_pos_vs_neg",
                selector="coverage_gap",
                selected=coverage_selected,
                extra=common_extra,
            )
            for k in args.top_k:
                add_selection_row(
                    per_seed_rows,
                    positive_count=positive_count,
                    negative_count=args.negative_count,
                    seed=seed,
                    score_family="bad_aware_pos_vs_neg",
                    selector=f"top{k}",
                    selected=bad_ranked[: min(k, len(bad_ranked))],
                    extra=common_extra,
                )

            nn_scores = positive_nn_transition_scores(pos.observations, pos.actions, unl.observations, unl.actions)
            nn_ranked = ranked_from_scores(unl, nn_scores, hidden_positive_ids)
            for k in args.top_k:
                add_selection_row(
                    per_seed_rows,
                    positive_count=positive_count,
                    negative_count=args.negative_count,
                    seed=seed,
                    score_family="positive_only_nn",
                    selector=f"top{k}",
                    selected=nn_ranked[: min(k, len(nn_ranked))],
                )

            pu_classifier, _pu_history = train_state_action_classifier(
                pos.observations,
                pos.actions,
                unl.observations,
                unl.actions,
                seed=seed + 177,
                steps=args.classifier_steps,
                batch_size=args.batch_size,
                hidden_dim=args.hidden_dim,
                depth=args.depth,
                lr=args.lr,
            )
            pu_scores = sigmoid(predict(pu_classifier, state_action_features(unl.observations, unl.actions)).reshape(-1))
            pu_ranked = ranked_from_scores(unl, pu_scores, hidden_positive_ids)
            for k in args.top_k:
                add_selection_row(
                    per_seed_rows,
                    positive_count=positive_count,
                    negative_count=args.negative_count,
                    seed=seed,
                    score_family="positive_vs_unlabeled",
                    selector=f"top{k}",
                    selected=pu_ranked[: min(k, len(pu_ranked))],
                )

            print(
                f"pos={positive_count} seed={seed}: "
                f"masscap={len(masscap_selected)} demos, "
                f"nn_top20={summarize_selection(nn_ranked[:20], positive_count)['selected_hidden_positive_demos']} hp, "
                f"pu_top20={summarize_selection(pu_ranked[:20], positive_count)['selected_hidden_positive_demos']} hp"
            )

    aggregate = aggregate_rows(per_seed_rows)
    write_csv(args.out_dir / "per_seed_selection.csv", per_seed_rows)
    write_csv(args.out_dir / "aggregate_selection.csv", aggregate)
    config = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "positive_counts": args.positive_counts,
        "negative_count": args.negative_count,
        "seeds": args.seeds,
        "classifier_steps": args.classifier_steps,
        "top_k": args.top_k,
        "gap_select_max_unlabeled_demos": args.gap_select_max_unlabeled_demos,
        "gap_select_min_unlabeled_demos": args.gap_select_min_unlabeled_demos,
        "gap_select_min_labeled_positive_multiplier": args.gap_select_min_labeled_positive_multiplier,
        "adaptive_mass_cap_ratio": args.adaptive_mass_cap_ratio,
    }
    (args.out_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    by_key = {
        (int(row["unlabeled_positive_count"]), str(row["score_family"]), str(row["selector"])): row
        for row in aggregate
    }

    def format_cell(item: dict[str, float | int | str] | None) -> str:
        if item is None:
            return ""
        return (
            f"{float(item['selected_hidden_positive_demos_mean']):.1f} / "
            f"{float(item['selected_hidden_bad_demos_mean']):.1f} / "
            f"{float(item['selected_hidden_positive_purity_mean']):.3f}"
        )

    report_lines = [
        "# Robomimic Bad-Label Support Ablation",
        "",
        "This support-only diagnostic asks whether explicit bad labels are doing real work in the Robomimic selector. It compares the current positive-vs-negative state-action classifier against controls that do not use labeled bad demos.",
        "",
        "Protocol:",
        "",
        f"- Base split: `{args.split_path}`",
        f"- Labeled positives / negatives: `{len(base_split['labeled_positive_ids'])}` / `{len(base_split['labeled_negative_ids'])}`",
        f"- Hidden-bad unlabeled demos fixed at `{args.negative_count}`.",
        f"- Hidden-positive unlabeled demos swept over `{', '.join(str(x) for x in args.positive_counts)}`.",
        f"- Seeds: `{', '.join(str(x) for x in args.seeds)}`.",
        f"- Classifier steps: `{args.classifier_steps}`.",
        "",
        "Selector families:",
        "",
        "- `bad_aware_pos_vs_neg`: current tri-signal scoring, trained on labeled positive versus labeled bad transitions.",
        "- `positive_only_nn`: no-bad-label nearest-neighbor similarity to labeled positive state-action support.",
        "- `positive_vs_unlabeled`: no-bad-label classifier trained to separate labeled positives from the unlabeled pool treated as background.",
        "",
        "## Key Support Results",
        "",
        "Each cell shows mean selected hidden-positive demos / mean hidden-bad demos / mean purity over the requested seeds.",
        "",
    ]
    headers = ["hidden pos", "bad-aware adaptive", "bad-aware top20", "pos-only NN top20", "pos-only NN top40", "pos-vs-unl top20", "pos-vs-unl top40"]
    table_rows = []
    for positive_count in args.positive_counts:
        table_rows.append(
            [
                str(positive_count),
                format_cell(by_key.get((positive_count, "bad_aware_pos_vs_neg", "adaptive_masscap"))),
                format_cell(by_key.get((positive_count, "bad_aware_pos_vs_neg", "top20"))),
                format_cell(by_key.get((positive_count, "positive_only_nn", "top20"))),
                format_cell(by_key.get((positive_count, "positive_only_nn", "top40"))),
                format_cell(by_key.get((positive_count, "positive_vs_unlabeled", "top20"))),
                format_cell(by_key.get((positive_count, "positive_vs_unlabeled", "top40"))),
            ]
        )
    report_lines.append(markdown_table(headers, table_rows))
    report_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The no-bad-label controls are ranking controls, not policy results. They test whether scarce positives alone are enough to identify hidden-good Robomimic demos under contamination.",
            "",
            "Use this report to decide whether a no-bad-label official BC-RNN policy control is worth running. If a no-bad support rule is close to the bad-aware adaptive selector in the target regime, the paper claim should emphasize adaptive support selection rather than bad-label necessity. If it is substantially worse, the next GPU run should train official BC-RNN on the strongest no-bad support control for an end-to-end policy ablation.",
            "",
            "Artifacts:",
            "",
            f"- Per-seed CSV: `{args.out_dir / 'per_seed_selection.csv'}`",
            f"- Aggregate CSV: `{args.out_dir / 'aggregate_selection.csv'}`",
            f"- Config: `{args.out_dir / 'config.json'}`",
        ]
    )
    (args.out_dir / "REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"wrote {args.out_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
