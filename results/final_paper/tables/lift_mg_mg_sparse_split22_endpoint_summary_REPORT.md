# Lift MG Sparse Split-22 Endpoint Summary

This is the second frozen final-paper Lift MG sparse row under `METHOD_FREEZE.md`.

Protocol:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seed: `22`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts, horizon 150.
- Evaluation device: CPU fallback; checkpoint, seed, init-state mode, episode count, and horizon are shared across methods.

## Endpoint Results

| method | success | successes | train demos | selected unlabeled | support purity |
|---|---:|---:|---:|---:|---:|
| positive-only NN top160 | 0.680 | 34/50 | 170 | 160 | 0.700 |
| all-positive oracle | 0.680 | 34/50 | 286 | 0 | n/a |
| weighted BC | 0.660 | 33/50 | 1430 | 1420 weighted | 0.194 |
| TRIAGE-BC / pos-min | 0.500 | 25/50 | 171 | 161 | 0.932 |
| all-demo BC | 0.200 | 10/50 | 1440 | all train demos | 0.194 |

## Support Audit

| method | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| TRIAGE-BC / pos-min | 161 | 150 | 11 | 0.932 |
| weighted BC | 1420 | 276 | 1144 | 0.194 |
| positive-only NN top160 | 160 | 112 | 48 | 0.700 |

## Interpretation

- This split reverses the split-11 Lift ordering: positive-only NN top160 and all-positive oracle tie at 0.680, weighted BC reaches 0.660, and TRIAGE-BC / pos-min reaches 0.500.
- Bad labels still improve support purity on this split: TRIAGE-BC selects 150 hidden-positive and 11 hidden-bad demos, while positive-only NN selects 112 hidden-positive and 48 hidden-bad demos.
- The policy result shows that higher selected-support purity is not sufficient by itself. Coverage, support diversity, and optimization noise still matter for the fixed endpoint.
- All-demo mixed cloning remains weak at 0.200, reinforcing that contaminated Lift logs hurt naive BC even when TRIAGE-BC is not the best filtered method.
- This row should be treated as a split-sensitivity result, not as evidence that weighted BC is weak or that bad labels are universally beneficial.

## Artifacts

- TRIAGE-BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_weighted_bc_policy0/REPORT.md`
- Positive-only NN run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_positive_only_nn_policy0/REPORT.md`
- All-demo BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_bc_all_mixed_policy0/REPORT.md`
- All-positive oracle run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_all_train_positive_oracle_policy0/REPORT.md`
