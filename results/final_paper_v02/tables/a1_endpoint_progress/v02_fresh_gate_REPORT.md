# v0.2 Fresh Can+Lift Endpoint Gate

Combined endpoint read for the frozen `METHOD_FREEZE_V02.md` fresh-split gate.
Rows use official Robomimic BC-RNN-GMM, epoch-200 checkpoints, and 50 valid-positive-start rollouts per split.

## Aggregate Read

| setting_label | selected_method | selected_success | selected_episodes | selected_rate | best_baseline_success | best_baseline_episodes | best_baseline_rate | margin | winning_splits | losing_splits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | positive_nn_risk_union_top40 | 197 | 250 | 0.788 | 192 | 250 | 0.768 | +0.020 | 4 | 1 |
| Lift MG | weighted_bc | 143 | 250 | 0.572 | 125 | 250 | 0.500 | +0.072 | 4 | 1 |

- Combined selected rows: 340/500.
- Combined best per-split non-oracle baselines: 317/500 (margin +0.046).

## Per-Split Read

| setting_label | split_seed | selected_method | selected_success | selected_episodes | best_baseline_method | best_baseline_success | best_baseline_episodes | margin |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Can 40p/80b | 101 | positive_nn_risk_union_top40 | 45 | 50 | weighted_bc | 37 | 50 | +0.160 |
| Can 40p/80b | 202 | positive_nn_risk_union_top40 | 45 | 50 | positive_only_nn | 40 | 50 | +0.100 |
| Can 40p/80b | 303 | positive_nn_risk_union_top40 | 39 | 50 | positive_only_nn | 36 | 50 | +0.060 |
| Can 40p/80b | 404 | positive_nn_risk_union_top40 | 27 | 50 | positive_only_nn | 39 | 50 | -0.240 |
| Can 40p/80b | 505 | positive_nn_risk_union_top40 | 41 | 50 | positive_only_nn | 40 | 50 | +0.020 |
| Lift MG | 101 | weighted_bc | 31 | 50 | positive_only_nn | 28 | 50 | +0.060 |
| Lift MG | 202 | weighted_bc | 30 | 50 | positive_only_nn | 25 | 50 | +0.100 |
| Lift MG | 303 | weighted_bc | 19 | 50 | positive_only_nn | 21 | 50 | -0.040 |
| Lift MG | 404 | weighted_bc | 30 | 50 | positive_only_nn | 25 | 50 | +0.100 |
| Lift MG | 505 | weighted_bc | 33 | 50 | positive_only_nn | 26 | 50 | +0.140 |

## Interpretation

- Can 40p/80b: selected branch margin +0.020 over the best per-split non-oracle baseline, with 4/5 winning splits, 0 ties, and 1 loss.
- Lift MG: selected branch margin +0.072 over the best per-split non-oracle baseline, with 4/5 winning splits, 0 ties, and 1 loss.
- Treat the completed fresh gate as evidence for hidden-label-free branch selection, not as a claim that hard bad-aware support dominates weighted BC.
