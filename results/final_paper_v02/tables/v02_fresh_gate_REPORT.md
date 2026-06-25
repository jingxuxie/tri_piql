# v0.2 Fresh Can+Lift Endpoint Gate

Combined endpoint read for the frozen `METHOD_FREEZE_V02.md` fresh-split gate.
Rows use official Robomimic BC-RNN-GMM, epoch-200 checkpoints, and 50 valid-positive-start rollouts per split.

## Aggregate Read

| setting_label | selected_method | selected_success | selected_episodes | selected_rate | best_baseline_success | best_baseline_episodes | best_baseline_rate | margin | winning_splits | losing_splits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive_nn_risk_union_top40 | 129 | 150 | 0.860 | 113 | 150 | 0.753 | +0.107 | 3 | 0 |
| Lift MG | weighted_bc | 80 | 150 | 0.533 | 74 | 150 | 0.493 | +0.040 | 2 | 1 |

- Combined selected rows: 209/300.
- Combined best per-split non-oracle baselines: 187/300 (margin +0.073).

## Per-Split Read

| setting_label | split_seed | selected_method | selected_success | selected_episodes | best_baseline_method | best_baseline_success | best_baseline_episodes | margin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 101 | positive_nn_risk_union_top40 | 45 | 50 | weighted_bc | 37 | 50 | +0.160 |
| Can 40p/80b | 202 | positive_nn_risk_union_top40 | 45 | 50 | positive_only_nn | 40 | 50 | +0.100 |
| Can 40p/80b | 303 | positive_nn_risk_union_top40 | 39 | 50 | positive_only_nn | 36 | 50 | +0.060 |
| Lift MG | 101 | weighted_bc | 31 | 50 | positive_only_nn | 28 | 50 | +0.060 |
| Lift MG | 202 | weighted_bc | 30 | 50 | positive_only_nn | 25 | 50 | +0.100 |
| Lift MG | 303 | weighted_bc | 19 | 50 | positive_only_nn | 21 | 50 | -0.040 |

## Interpretation

- Can 40p/80b is the cleaner v0.2 improvement: the selected hard-union branch wins all three fresh splits.
- Lift MG supports the router's soft-coverage branch only cautiously: selected weighted BC wins two splits but loses split `303`.
- Treat the completed fresh gate as evidence for hidden-label-free branch selection, not as a claim that hard bad-aware support dominates weighted BC.
