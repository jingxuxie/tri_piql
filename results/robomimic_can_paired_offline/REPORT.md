# Robomimic Can Paired Offline Diagnostic

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Labeled demos: `10` positive, `10` negative.
Unlabeled demos: `160`.
Validation demos: `10` positive, `10` negative.

## Policy Offline Metrics

| method | valid positive MSE | valid negative MSE | neg-pos MSE gap |
|---|---:|---:|---:|
| bc_labeled_positive | 0.04986 | 0.14027 | 0.09041 |
| bc_pos_unlabeled | 0.02390 | 0.02713 | 0.00323 |
| bc_all | 0.02484 | 0.02712 | 0.00228 |
| weighted_bc_state_action | 0.02435 | 0.06093 | 0.03657 |

## State-Action Classifier

- Train labeled accuracy: `0.985`.
- Valid labeled accuracy: `0.747`.
- Valid positive-vs-negative AUC: `0.854`.
- Valid positive/negative logit mean: `11.517` / `-8.385`.
- Unlabeled positive probability mean: `0.501`.

## Interpretation

- This is an offline-only viability check before installing/evaluating full robosuite rollouts.
- A useful signal is high held-out positive-vs-negative classifier AUC and lower action MSE on held-out positive demonstrations than held-out negative demonstrations.
