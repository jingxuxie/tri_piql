# CAU-BC Negative-Action Preflight

This preflight reuses the Candidate C sequence mask but changes the counterfactual bad-action target.
The goal is to avoid repeating the rejected nearest-state Candidate D/X hinge unchanged.

## Retrieval Summary

| retrieval | neg mass | hidden-pos mass | hidden-bad mass | obs dist | action dist | state-action dist |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nearest_state | 5511 | 5115 | 396 | 3.498549 | 2.749362 | 4.612810 |
| nearest_state_action | 5511 | 5115 | 396 | 3.653695 | 2.016981 | 4.299046 |
| action_conflict | 5511 | 5115 | 396 | 3.810515 | 3.727614 | 5.490323 |

## Selected Recipe

- Retrieval mode: `action_conflict`.
- Negative-loss scope: `selected`.
- Top-k local negative states for action-conflict retrieval: `16`.
- Negative-loss mass: `5511`.
- Mean selected negative-action distance: `3.727614`.

## Read

- `action_conflict` chooses among local negative states but picks the negative action most different from the demonstrated action.
- This is a different bad-action target from Candidate D/X's nearest-observation negative action. It still needs a bounded endpoint screen before any claim.

## Outputs

- Weight HDF5: `results/sota_candidate/cau_action_conflict_can303_preflight/cau_negative_action_weights.hdf5`.
- Retrieval summary CSV: `results/sota_candidate/cau_action_conflict_can303_preflight/cau_retrieval_summary.csv`.
- Selected per-demo CSV: `results/sota_candidate/cau_action_conflict_can303_preflight/cau_selected_demo_summary.csv`.
- Recipe JSON: `results/sota_candidate/cau_action_conflict_can303_preflight/cau_recipe.json`.
