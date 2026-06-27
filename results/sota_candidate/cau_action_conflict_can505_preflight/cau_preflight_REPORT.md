# CAU-BC Negative-Action Preflight

This preflight reuses the Candidate C sequence mask but changes the counterfactual bad-action target.
The goal is to avoid repeating the rejected nearest-state Candidate D/X hinge unchanged.

## Retrieval Summary

| retrieval | neg mass | hidden-pos mass | hidden-bad mass | obs dist | action dist | state-action dist |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| nearest_state | 5382 | 5091 | 291 | 3.466070 | 2.719609 | 4.595084 |
| nearest_state_action | 5382 | 5091 | 291 | 3.646456 | 2.002505 | 4.298201 |
| action_conflict | 5382 | 5091 | 291 | 3.818120 | 3.721178 | 5.508957 |

## Selected Recipe

- Retrieval mode: `action_conflict`.
- Negative-loss scope: `selected`.
- Top-k local negative states for action-conflict retrieval: `16`.
- Negative-loss mass: `5382`.
- Mean selected negative-action distance: `3.721178`.

## Read

- `action_conflict` chooses among local negative states but picks the negative action most different from the demonstrated action.
- This is a different bad-action target from Candidate D/X's nearest-observation negative action. It still needs a bounded endpoint screen before any claim.

## Outputs

- Weight HDF5: `results/sota_candidate/cau_action_conflict_can505_preflight/cau_negative_action_weights.hdf5`.
- Retrieval summary CSV: `results/sota_candidate/cau_action_conflict_can505_preflight/cau_retrieval_summary.csv`.
- Selected per-demo CSV: `results/sota_candidate/cau_action_conflict_can505_preflight/cau_selected_demo_summary.csv`.
- Recipe JSON: `results/sota_candidate/cau_action_conflict_can505_preflight/cau_recipe.json`.
