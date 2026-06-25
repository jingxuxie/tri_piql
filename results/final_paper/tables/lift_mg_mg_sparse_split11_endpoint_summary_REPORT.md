# Lift MG Sparse Split-11 Endpoint Summary

This is the first frozen final-paper Lift MG sparse row under `METHOD_FREEZE.md`.

Protocol:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seed: `11`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts, horizon 150.
- Evaluation device: CPU fallback; checkpoint, seed, init-state mode, episode count, and horizon are shared across methods.

## Endpoint Results

| method | success | successes | train demos | selected unlabeled | support purity |
|---|---:|---:|---:|---:|---:|
| all-positive oracle | 0.660 | 33/50 | 286 | 0 | n/a |
| TRIAGE-BC / pos-min | 0.540 | 27/50 | 188 | 178 | 0.949 |
| weighted BC | 0.480 | 24/50 | 1430 | 1420 weighted | 0.194 |
| positive-only NN top160 | 0.460 | 23/50 | 170 | 160 | 0.531 |
| all-demo BC | 0.260 | 13/50 | 1440 | all train demos | 0.194 |

## Support Audit

| method | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| TRIAGE-BC / pos-min | 178 | 169 | 9 | 0.949 |
| weighted BC | 1420 | 276 | 1144 | 0.194 |
| positive-only NN top160 | 160 | 85 | 75 | 0.531 |

## Interpretation

- TRIAGE-BC keeps a same-split edge over weighted BC, positive-only NN, and all-demo cloning on this fresh Lift split.
- The positive-only NN support is much noisier on this split than in the previous original-split diagnostic, selecting only 85 hidden positives and 75 hidden bad demos. This is useful evidence for a bad-label calibration benefit on Lift.
- The edge over weighted BC is only 3 successes out of 50, so this is a directionally useful split row, not a standalone statistical claim.
- The all-positive oracle reaches only 0.660, so this split is harder than the near-saturated frozen Can oracle diagnostic and leaves modest support-conversion headroom.
- All-demo mixed cloning remains weak at 0.260, reinforcing that contaminated Lift logs hurt naive BC even with the official BC-RNN-GMM backbone.

## Artifacts

- TRIAGE-BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_weighted_bc_policy0/REPORT.md`
- Positive-only NN run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_positive_only_nn_policy0/REPORT.md`
- All-demo BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_bc_all_mixed_policy0/REPORT.md`
- All-positive oracle run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_all_train_positive_oracle_policy0/REPORT.md`
