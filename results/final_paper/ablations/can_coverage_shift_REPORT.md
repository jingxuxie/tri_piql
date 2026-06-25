# Can Scarce-Positive Coverage-Shift Support Audit

Generated from the paired low-dimensional Can dataset without policy training.
Each split labels successes from one compact initial-object-pose cluster, hides successes from other clusters, and spreads bad demos across all clusters.
Hidden labels are used only for audit summaries.

## Construction Check

| split seed | label cluster | positive clusters | negative clusters | hidden-positive clusters | labeled-negative clusters | labeled-positive shift | hidden-positive shift | unlabeled-negative shift |
|---:|---:|---|---|---:|---:|---:|---:|---:|
| 101 | 1 | 0:24;1:34;2:29;3:13 | 0:24;1:34;2:29;3:13 | 3 | 4 | 1.522 | 4.526 | 3.254 |
| 202 | 0 | 0:26;1:12;2:35;3:27 | 0:26;1:12;2:35;3:27 | 3 | 4 | 1.248 | 4.723 | 3.312 |
| 303 | 1 | 0:25;1:25;2:23;3:27 | 0:25;1:25;2:23;3:27 | 3 | 4 | 1.726 | 4.846 | 3.748 |

## Support Gate

Rows aggregate over the three generated split seeds.

| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |
|---|---|---:|---:|---:|---:|
| state_action_positive_nn_top40 | positive-only | 120 | 0.875 | 0.062 | 0.875 |
| state_positive_nn_top40 | positive-only | 120 | 0.875 | 0.062 | 0.875 |
| bad_aware_proxy_top40 | bad-aware proxy | 120 | 1.000 | 0.000 | 1.000 |
| hybrid_pos20_filter_badaware80_refill40 | hybrid | 120 | 0.992 | 0.004 | 0.992 |
| hybrid_pos40_filter_badaware80_refill40 | hybrid | 120 | 0.883 | 0.058 | 0.883 |
| hybrid_rank_fusion_badaware_heavy_top40 | hybrid | 120 | 0.983 | 0.008 | 0.983 |
| hybrid_rank_fusion_equal_top40 | hybrid | 120 | 0.975 | 0.013 | 0.975 |
| all_unlabeled_soft_reference | soft-reference | 360 | 1.000 | 1.000 | 0.333 |

## Decision

The support gate is cleared by bad_aware_proxy_top40, hybrid_intersection_pos40_badaware40, hybrid_pos20_filter_badaware80_refill40, hybrid_pos40_filter_badaware80, hybrid_pos40_filter_badaware80_refill40, hybrid_rank_fusion_badaware_heavy_top40, hybrid_rank_fusion_equal_top40: it improves the state-action positive-NN top40 recall/bad-admission tradeoff under coverage shift.

Use this audit as Experiment Group C2 support evidence. A cleared support rule is a candidate for endpoint BC on these generated split files, not a rollout-performance claim.

## Outputs

- `results/final_paper/ablations/can_coverage_shift_construction.csv`
- `results/final_paper/ablations/can_coverage_shift_support_per_split.csv`
- `results/final_paper/ablations/can_coverage_shift_summary.csv`
- `results/final_paper/ablations/can_coverage_shift_REPORT.md`
- `results/final_paper/ablations/can_coverage_shift_splits`

Summary rows: `19`. Per-split rows: `57`.
