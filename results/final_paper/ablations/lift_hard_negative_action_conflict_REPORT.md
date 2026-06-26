# Lift Hard-Negative Action-Conflict Support Audit

This is the first non-Can generated support diagnostic for the paper plan's Priority C1.
It reuses the Lift MG low-dimensional sparse dataset and constructs compact-positive, hard-negative splits without policy training.
Hidden success/failure labels are used only for construction and support audits, not for any deployable selection rule.

## Construction Check

| split_seed | hidden_positive_state_gap_mean | unlabeled_bad_state_distance_mean | unlabeled_bad_action_conflict_mean | unlabeled_bad_hard_score_mean |
| --- | --- | --- | --- | --- |
| 101 | 27.566 | 23.883 | 8.680 | 1.828 |
| 202 | 25.852 | 17.962 | 9.598 | 1.447 |
| 303 | 27.477 | 23.203 | 10.498 | 1.837 |

## Support Gate

Rows aggregate over the three generated Lift split seeds.

| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |
|---|---|---:|---:|---:|---:|
| state_action_positive_nn_top40 | positive-only | 120 | 0.100 | 0.450 | 0.100 |
| state_positive_nn_top40 | positive-only | 120 | 0.067 | 0.467 | 0.067 |
| bad_aware_proxy_top40 | bad-aware proxy | 120 | 0.683 | 0.158 | 0.683 |
| hybrid_pos40_filter_badaware80_refill40 | hybrid | 120 | 0.567 | 0.217 | 0.567 |
| hybrid_rank_fusion_badaware_heavy_top40 | hybrid | 120 | 0.517 | 0.242 | 0.517 |
| hybrid_rank_fusion_equal_top40 | hybrid | 120 | 0.342 | 0.329 | 0.342 |
| all_unlabeled_soft_reference | soft-reference | 360 | 1.000 | 1.000 | 0.333 |

## Read

- State-action positive-NN top40 selects `12/120` hidden positives and `108/240` hidden bad demos.
- Bad-aware proxy top40 selects `82/120` hidden positives and `38/240` hidden bad demos.
- The Lift support gate is cleared by bad_aware_proxy_top20, bad_aware_proxy_top40, bad_aware_proxy_top60, hybrid_pos40_filter_badaware80_refill40, hybrid_rank_fusion_badaware_heavy_top40, hybrid_rank_fusion_equal_top40: these rows match or exceed state-action positive-NN recall while reducing hidden-bad admission.
- This is support-only evidence. It is useful C1 evidence that the generated bad-label mechanism transfers beyond Can, but it is not a policy endpoint claim.

## Outputs

- `results/final_paper/ablations/lift_hard_negative_action_conflict_construction.csv`
- `results/final_paper/ablations/lift_hard_negative_action_conflict_support_per_split.csv`
- `results/final_paper/ablations/lift_hard_negative_action_conflict_summary.csv`
- `results/final_paper/ablations/lift_hard_negative_action_conflict_REPORT.md`
- `results/final_paper/ablations/lift_hard_negative_action_conflict_splits`
