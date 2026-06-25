# Hard-Negative Can Action-Conflict Support Audit

Generated from the paired low-dimensional Can dataset without policy training.
The diagnostic constructs compact-positive splits, places hidden positives far from the labeled-positive cluster, and ranks bad demos by near-positive state distance plus action conflict.
Hidden labels are used only for audit summaries.

## Construction Check

| split seed | hidden-positive state gap mean | unlabeled-bad state distance mean | valid-bad state distance mean | unlabeled-bad action conflict mean | valid-bad action conflict mean | unlabeled-bad hard score mean | valid-bad hard score mean |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 101 | 14.878 | 19.986 | 23.773 | 7.140 | 7.671 | 0.032 | -1.744 |
| 202 | 14.093 | 20.143 | 23.219 | 7.640 | 7.761 | 0.026 | -1.806 |
| 303 | 13.183 | 20.223 | 23.215 | 7.725 | 8.047 | 0.002 | -1.843 |

## Support Gate

Rows aggregate over the three generated split seeds.

| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |
|---|---|---:|---:|---:|---:|
| state_action_positive_nn_top40 | positive-only | 120 | 0.583 | 0.208 | 0.583 |
| state_positive_nn_top40 | positive-only | 120 | 0.542 | 0.229 | 0.542 |
| bad_aware_proxy_top40 | bad-aware proxy | 120 | 1.000 | 0.000 | 1.000 |
| hybrid_pos40_filter_badaware80_refill40 | hybrid | 120 | 0.867 | 0.067 | 0.867 |
| hybrid_rank_fusion_equal_top40 | hybrid | 120 | 0.875 | 0.062 | 0.875 |
| all_unlabeled_soft_reference | soft-reference | 360 | 1.000 | 1.000 | 0.333 |

## Decision

The support gate is cleared by bad_aware_proxy_top40, hybrid_intersection_pos40_badaware40, hybrid_pos40_filter_badaware80, hybrid_pos40_filter_badaware80_refill40, hybrid_rank_fusion_badaware_heavy_top40, hybrid_rank_fusion_equal_top40: it matches or exceeds state-action positive-NN recall while reducing hidden-bad admission.

Use this audit as Experiment Group C1 support evidence. A cleared support rule is a candidate for endpoint BC on these generated split files, not a rollout-performance claim.

## Outputs

- `results/final_paper/ablations/hard_negative_can_action_conflict_construction.csv`
- `results/final_paper/ablations/hard_negative_can_action_conflict_support_per_split.csv`
- `results/final_paper/ablations/hard_negative_can_action_conflict_summary.csv`
- `results/final_paper/ablations/hard_negative_can_action_conflict_REPORT.md`
- `results/final_paper/ablations/hard_negative_can_action_conflict_splits`

Summary rows: `18`. Per-split rows: `54`.
