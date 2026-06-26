# v0.2 Fresh Lift MG Endpoint Summary

Fresh-split endpoint rows for the frozen `METHOD_FREEZE_V02.md` Lift branch.
The frozen router selects weighted BC on Lift-like broad-coverage rows.

| split_seed | method_id | method_role | success_count | eval_episodes | endpoint_success | train_demo_count | selected_unlabeled |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | weighted_bc | v02_selected | 31 | 50 | 0.620 | 1430 | 1420 |
| 101 | positive_only_nn | strong_baseline | 28 | 50 | 0.560 | 170 | 160 |
| 101 | triage_bc | v01_method | 36 | 50 | 0.720 | 301 | 291 |
| 202 | weighted_bc | v02_selected | 30 | 50 | 0.600 | 1430 | 1420 |
| 202 | positive_only_nn | strong_baseline | 25 | 50 | 0.500 | 170 | 160 |
| 202 | triage_bc | v01_method | 34 | 50 | 0.680 | 231 | 221 |
| 303 | weighted_bc | v02_selected | 19 | 50 | 0.380 | 1430 | 1420 |
| 303 | positive_only_nn | strong_baseline | 21 | 50 | 0.420 | 170 | 160 |
| 303 | triage_bc | v01_method | 20 | 50 | 0.400 | 385 | 375 |
| 404 | weighted_bc | v02_selected | 30 | 50 | 0.600 | 1430 | 1420 |
| 404 | positive_only_nn | strong_baseline | 25 | 50 | 0.500 | 170 | 160 |
| 404 | triage_bc | v01_method | 29 | 50 | 0.580 | 219 | 209 |
| 505 | weighted_bc | v02_selected | 33 | 50 | 0.660 | 1430 | 1420 |
| 505 | positive_only_nn | strong_baseline | 26 | 50 | 0.520 | 170 | 160 |
| 505 | triage_bc | v01_method | 24 | 50 | 0.480 | 215 | 205 |

## Aggregate Read

- Completed v0.2 selected Lift rows: 143/250.
- Best completed non-oracle baseline per split: 146/250 (margin -0.012).

## Per-Split Read

- Split 101: selected `weighted_bc` is 31/50 versus best completed non-oracle baseline `triage_bc` at 36/50 (margin -0.100).
- Split 202: selected `weighted_bc` is 30/50 versus best completed non-oracle baseline `triage_bc` at 34/50 (margin -0.080).
- Split 303: selected `weighted_bc` is 19/50 versus best completed non-oracle baseline `positive_only_nn` at 21/50 (margin -0.040).
- Split 404: selected `weighted_bc` is 30/50 versus best completed non-oracle baseline `triage_bc` at 29/50 (margin +0.020).
- Split 505: selected `weighted_bc` is 33/50 versus best completed non-oracle baseline `positive_only_nn` at 26/50 (margin +0.140).
