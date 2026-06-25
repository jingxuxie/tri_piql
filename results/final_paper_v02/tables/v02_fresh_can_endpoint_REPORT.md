# v0.2 Fresh Can 40 Endpoint Summary

Fresh-split endpoint rows for the frozen `METHOD_FREEZE_V02.md` Can branch.
This report covers the Can branch; see the v0.2 README and Lift report for the cross-task gate.

| split_seed | method_id | method_role | success_count | eval_episodes | endpoint_success | train_demo_count | selected_unlabeled |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | positive_nn_risk_union_top40 | v02_selected | 45 | 50 | 0.900 | 59 | 49 |
| 101 | positive_only_nn | strong_baseline | 19 | 50 | 0.380 | 50 | 40 |
| 101 | weighted_bc | strong_baseline | 37 | 50 | 0.740 | 130 | 120 |
| 202 | positive_nn_risk_union_top40 | v02_selected | 45 | 50 | 0.900 | 54 | 44 |
| 202 | positive_only_nn | strong_baseline | 40 | 50 | 0.800 | 50 | 40 |
| 202 | weighted_bc | strong_baseline | 33 | 50 | 0.660 | 130 | 120 |
| 303 | positive_nn_risk_union_top40 | v02_selected | 39 | 50 | 0.780 | 55 | 45 |
| 303 | positive_only_nn | strong_baseline | 36 | 50 | 0.720 | 50 | 40 |
| 303 | weighted_bc | strong_baseline | 25 | 50 | 0.500 | 130 | 120 |

## Aggregate Read

- Completed v0.2 selected Can rows: 129/150.
- Best completed non-oracle baseline per split: 113/150 (margin +0.107).

## Per-Split Read

- Split 101: v0.2 selected `positive_nn_risk_union_top40` is 45/50 versus best completed non-oracle baseline `weighted_bc` at 37/50 (margin +0.160).
- Split 202: v0.2 selected `positive_nn_risk_union_top40` is 45/50 versus best completed non-oracle baseline `positive_only_nn` at 40/50 (margin +0.100).
- Split 303: v0.2 selected `positive_nn_risk_union_top40` is 39/50 versus best completed non-oracle baseline `positive_only_nn` at 36/50 (margin +0.060).
