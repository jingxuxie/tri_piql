# v0.2 Fresh Lift MG Endpoint Summary

Fresh-split endpoint rows for the frozen `METHOD_FREEZE_V02.md` Lift branch.
The frozen router selects weighted BC on Lift-like broad-coverage rows.

| split_seed | method_id | method_role | success_count | eval_episodes | endpoint_success | train_demo_count | selected_unlabeled |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | weighted_bc | v02_selected | 31 | 50 | 0.620 | 1430 | 1420 |
| 101 | positive_only_nn | strong_baseline | 28 | 50 | 0.560 | 170 | 160 |
| 202 | weighted_bc | v02_selected | 30 | 50 | 0.600 | 1430 | 1420 |
| 202 | positive_only_nn | strong_baseline | 25 | 50 | 0.500 | 170 | 160 |
| 303 | weighted_bc | v02_selected | 19 | 50 | 0.380 | 1430 | 1420 |
| 303 | positive_only_nn | strong_baseline | 21 | 50 | 0.420 | 170 | 160 |

## Aggregate Read

- Completed v0.2 selected Lift rows: 80/150.
- Best completed non-oracle baseline per split: 74/150 (margin +0.040).

## Per-Split Read

- Split 101: selected `weighted_bc` is 31/50 versus best completed non-oracle baseline `positive_only_nn` at 28/50 (margin +0.060).
- Split 202: selected `weighted_bc` is 30/50 versus best completed non-oracle baseline `positive_only_nn` at 25/50 (margin +0.100).
- Split 303: selected `weighted_bc` is 19/50 versus best completed non-oracle baseline `positive_only_nn` at 21/50 (margin -0.040).
