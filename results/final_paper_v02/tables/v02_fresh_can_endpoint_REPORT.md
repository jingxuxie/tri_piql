# v0.2 Fresh Can 40 Endpoint Summary

Fresh-split endpoint rows for the frozen `METHOD_FREEZE_V02.md` Can branch.
This report covers the Can branch; see the v0.2 README and Lift report for the cross-task gate.

| split_seed | method_id | method_role | success_count | eval_episodes | endpoint_success | train_demo_count | selected_unlabeled |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | positive_nn_risk_union_top40 | v02_selected | 45 | 50 | 0.900 | 59 | 49 |
| 101 | positive_only_nn | strong_baseline | 19 | 50 | 0.380 | 50 | 40 |
| 101 | weighted_bc | strong_baseline | 37 | 50 | 0.740 | 130 | 120 |
| 101 | triage_bc | v01_method | 28 | 50 | 0.560 | 56 | 46 |
| 202 | positive_nn_risk_union_top40 | v02_selected | 45 | 50 | 0.900 | 54 | 44 |
| 202 | positive_only_nn | strong_baseline | 40 | 50 | 0.800 | 50 | 40 |
| 202 | weighted_bc | strong_baseline | 33 | 50 | 0.660 | 130 | 120 |
| 202 | triage_bc | v01_method | 36 | 50 | 0.720 | 54 | 44 |
| 303 | positive_nn_risk_union_top40 | v02_selected | 39 | 50 | 0.780 | 55 | 45 |
| 303 | positive_only_nn | strong_baseline | 36 | 50 | 0.720 | 50 | 40 |
| 303 | weighted_bc | strong_baseline | 25 | 50 | 0.500 | 130 | 120 |
| 303 | triage_bc | v01_method | 35 | 50 | 0.700 | 50 | 40 |
| 404 | positive_nn_risk_union_top40 | v02_selected | 27 | 50 | 0.540 | 54 | 44 |
| 404 | positive_only_nn | strong_baseline | 39 | 50 | 0.780 | 50 | 40 |
| 404 | weighted_bc | strong_baseline | 33 | 50 | 0.660 | 130 | 120 |
| 404 | triage_bc | v01_method | 36 | 50 | 0.720 | 69 | 59 |
| 404 | bc_all_mixed | mixed_log_baseline | 27 | 50 | 0.540 | 180 | 0 |
| 404 | all_train_positive_oracle | oracle_control | 49 | 50 | 0.980 | 90 | 0 |
| 505 | positive_nn_risk_union_top40 | v02_selected | 41 | 50 | 0.820 | 54 | 44 |
| 505 | positive_only_nn | strong_baseline | 40 | 50 | 0.800 | 50 | 40 |
| 505 | weighted_bc | strong_baseline | 30 | 50 | 0.600 | 130 | 120 |
| 505 | triage_bc | v01_method | 36 | 50 | 0.720 | 55 | 45 |

## Aggregate Read

- Completed v0.2 selected Can rows: 197/250.
- Comparable splits with completed non-oracle baselines: 5.
- On comparable splits, v0.2 selected Can rows: 197/250.
- On comparable splits, best completed non-oracle baseline per split: 192/250 (margin +0.020).

## Per-Split Read

- Split 101: v0.2 selected `positive_nn_risk_union_top40` is 45/50 versus best completed non-oracle baseline `weighted_bc` at 37/50 (margin +0.160).
- Split 202: v0.2 selected `positive_nn_risk_union_top40` is 45/50 versus best completed non-oracle baseline `positive_only_nn` at 40/50 (margin +0.100).
- Split 303: v0.2 selected `positive_nn_risk_union_top40` is 39/50 versus best completed non-oracle baseline `positive_only_nn` at 36/50 (margin +0.060).
- Split 404: v0.2 selected `positive_nn_risk_union_top40` is 27/50 versus best completed non-oracle baseline `positive_only_nn` at 39/50 (margin -0.240).
- Split 505: v0.2 selected `positive_nn_risk_union_top40` is 41/50 versus best completed non-oracle baseline `positive_only_nn` at 40/50 (margin +0.020).
