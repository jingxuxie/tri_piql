# Lift MG Sparse Three-Split Core Endpoint Summary

This summarizes the three frozen Lift MG sparse rows currently available for the core non-oracle comparison.

Protocol shared by all rows:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seeds: `11`, `22`, and `33`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts per split, horizon 150.

All three splits also include all-demo BC and all-positive oracle controls in the full Lift final summary. This report intentionally summarizes only the matched non-oracle core methods.

## Endpoint Results

| method | split 11 | split 22 | split 33 | pooled successes | pooled success |
|---|---:|---:|---:|---:|---:|
| weighted BC | 0.480 | 0.660 | 0.720 | 93/150 | 0.620 |
| positive-only NN top160 | 0.460 | 0.680 | 0.500 | 82/150 | 0.547 |
| TRIAGE-BC / pos-min | 0.540 | 0.500 | 0.440 | 74/150 | 0.493 |

## Support Audit

| split | method | selected unlabeled | hidden-positive | hidden-bad | purity |
|---:|---|---:|---:|---:|---:|
| 11 | TRIAGE-BC / pos-min | 178 | 169 | 9 | 0.949 |
| 11 | positive-only NN top160 | 160 | 85 | 75 | 0.531 |
| 11 | weighted BC | 1420 | 276 | 1144 | 0.194 |
| 22 | TRIAGE-BC / pos-min | 161 | 150 | 11 | 0.932 |
| 22 | positive-only NN top160 | 160 | 112 | 48 | 0.700 |
| 22 | weighted BC | 1420 | 276 | 1144 | 0.194 |
| 33 | TRIAGE-BC / pos-min | 102 | 102 | 0 | 1.000 |
| 33 | positive-only NN top160 | 160 | 145 | 15 | 0.906 |
| 33 | weighted BC | 1420 | 276 | 1144 | 0.194 |

## Interpretation

- The three-split core Lift result now favors weighted BC: 93/150 for weighted BC, 82/150 for positive-only NN, and 74/150 for TRIAGE-BC.
- TRIAGE-BC consistently improves support purity over positive-only NN, but the policy result does not track purity alone. Split 33 is the clearest example: TRIAGE selects 102/102 hidden positives, yet weighted BC reaches the best endpoint success.
- The current Lift evidence should not be framed as a bad-label policy benefit. It is better evidence for the unresolved precision/coverage conversion problem.
- Positive-only NN remains a strong no-bad-label baseline and beats TRIAGE-BC on two of three fresh frozen Lift splits.
- The all-demo negative control is now complete in the full Lift final summary, where all-demo BC reaches 31/150.

## Artifacts

- Split 11 full report: `results/final_paper/tables/lift_mg_mg_sparse_split11_endpoint_summary_REPORT.md`
- Split 22 full report: `results/final_paper/tables/lift_mg_mg_sparse_split22_endpoint_summary_REPORT.md`
- Split 33 full report: `results/final_paper/tables/lift_mg_mg_sparse_split33_endpoint_summary_REPORT.md`
- Full five-method aggregate: `results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md`
