# Lift MG Sparse Split-33 Endpoint Summary

This is the third frozen final-paper Lift MG sparse row under `METHOD_FREEZE.md`, now including the all-demo BC and all-positive oracle controls.

Protocol:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seed: `33`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts, horizon 150.
- Evaluation device: CPU fallback; checkpoint, seed, init-state mode, episode count, and horizon are shared across methods.

## Endpoint Results

| method | success | successes | train demos | selected unlabeled | support purity |
|---|---:|---:|---:|---:|---:|
| all-positive oracle | 0.760 | 38/50 | 286 | 0 | n/a |
| weighted BC | 0.720 | 36/50 | 1430 | 1420 weighted | 0.194 |
| positive-only NN top160 | 0.500 | 25/50 | 170 | 160 | 0.906 |
| TRIAGE-BC / pos-min | 0.440 | 22/50 | 112 | 102 | 1.000 |
| all-demo BC | 0.160 | 8/50 | 1440 | all train demos | 0.194 |

## Support Audit

| method | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| TRIAGE-BC / pos-min | 102 | 102 | 0 | 1.000 |
| weighted BC | 1420 | 276 | 1144 | 0.194 |
| positive-only NN top160 | 160 | 145 | 15 | 0.906 |

## Interpretation

- Split 33 is the clearest Lift coverage failure for TRIAGE-BC / pos-min: it has perfect selected-support purity, but selects only 102 hidden positives and reaches 0.440 endpoint success.
- Weighted BC is close to the all-positive oracle on this split, 36/50 versus 38/50, despite the low hidden-positive fraction in the weighted train pool.
- Positive-only NN top160 also beats TRIAGE-BC on the fixed endpoint while keeping high support purity.
- All-demo mixed cloning is weak at 8/50, completing the contaminated-log negative control for all three frozen Lift splits.
- This row strengthens the paper caveat: bad labels improve support purity, but the current hard threshold does not convert that purity into the best Lift policy.

## Artifacts

- TRIAGE-BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_weighted_bc_policy0/REPORT.md`
- Positive-only NN run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_positive_only_nn_policy0/REPORT.md`
- All-demo BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_bc_all_mixed_policy0/REPORT.md`
- All-positive oracle run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_all_train_positive_oracle_policy0/REPORT.md`
