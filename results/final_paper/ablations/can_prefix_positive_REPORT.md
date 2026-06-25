# Can Prefix-Positive Support Diagnostic

This controlled Robomimic diagnostic uses only early prefixes of successful Can demos
as positive labels for scoring. Full successful and failed trajectories are hidden in
the unlabeled pool, and failed demos provide explicit bad labels.

Artifacts:

- Construction CSV: `results/final_paper/ablations/can_prefix_positive_construction.csv`
- Per-split support CSV: `results/final_paper/ablations/can_prefix_positive_support_per_split.csv`
- Summary CSV: `results/final_paper/ablations/can_prefix_positive_summary.csv`
- Split files: `results/final_paper/ablations/can_prefix_positive_splits/split*/split_indices.json`

## Support Gate

The support gate is cleared by 15 candidate(s): `prefix_bad_aware_state_action_top120, prefix_bad_aware_state_action_top20, prefix_bad_aware_state_action_top40, prefix_bad_aware_state_action_top80, prefix_bad_aware_state_top120, prefix_bad_aware_state_top20, prefix_bad_aware_state_top40, prefix_bad_aware_state_top80, prefix_rank_fusion_badaware_heavy_top40, prefix_rank_fusion_badaware_heavy_top80, prefix_rank_fusion_equal_top40, prefix_rank_fusion_equal_top80, prefix_state_action_nn_top20, prefix_state_nn_top20, prefix_state_nn_top80`.

## Baselines

| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |
|---|---|---:|---:|---:|---:|
| prefix_state_action_nn_top40 | positive-only | 120 | 0.000 | 0.500 | 0.000 |
| prefix_state_action_nn_top80 | positive-only | 240 | 0.154 | 0.846 | 0.154 |

## Best Support Rows

| candidate | family | selected | hidden-positive recall | hidden-bad admission | purity |
|---|---|---:|---:|---:|---:|
| all_unlabeled_soft_reference | soft-reference | 480 | 1.000 | 1.000 | 0.500 |
| prefix_bad_aware_state_action_top120 | bad-aware | 360 | 0.983 | 0.517 | 0.656 |
| prefix_bad_aware_state_top120 | bad-aware | 360 | 0.983 | 0.517 | 0.656 |
| prefix_bad_aware_state_top80 | bad-aware | 240 | 0.812 | 0.188 | 0.812 |
| prefix_bad_aware_state_action_top80 | bad-aware | 240 | 0.804 | 0.196 | 0.804 |
| prefix_rank_fusion_badaware_heavy_top80 | hybrid | 240 | 0.629 | 0.371 | 0.629 |
| prefix_state_action_nn_top120 | positive-only | 360 | 0.550 | 0.950 | 0.367 |
| prefix_state_nn_top120 | positive-only | 360 | 0.550 | 0.950 | 0.367 |

## Decision

- This is support-only evidence. Endpoint training is justified only if a hidden-label-free
  bad-aware or hybrid rule strictly improves over prefix positive-NN at comparable selected count.
- If the gate clears, train the best top80 candidate against prefix state-action positive-NN top80
  on one split before expanding.
