# Lift MG Sparse Frozen Endpoint Summary

This summarizes the completed frozen Lift MG sparse split rows currently staged under `METHOD_FREEZE.md`.

Protocol shared by all rows:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seeds: `11`, `22`, and `33`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts per split, horizon 150.

## Endpoint Results

| method | split 11 | split 22 | split 33 | pooled successes | pooled success |
|---|---:|---:|---:|---:|---:|
| all-positive oracle | 0.660 | 0.680 | 0.760 | 105/150 | 0.700 |
| weighted BC | 0.480 | 0.660 | 0.720 | 93/150 | 0.620 |
| positive-only NN top160 | 0.460 | 0.680 | 0.500 | 82/150 | 0.547 |
| TRIAGE-BC / pos-min | 0.540 | 0.500 | 0.440 | 74/150 | 0.493 |
| all-demo BC | 0.260 | 0.200 | 0.160 | 31/150 | 0.207 |

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

- The full frozen Lift matrix favors weighted BC among non-oracle methods: 93/150 for weighted BC, 82/150 for positive-only NN top160, and 74/150 for TRIAGE-BC / pos-min.
- Bad labels consistently improve selected-support purity, but that support-side advantage does not reliably translate into the best fixed-endpoint policy. Split 33 is the sharpest example: TRIAGE-BC selects 102/102 hidden positives, yet weighted BC reaches 36/50 successes.
- All-demo mixed cloning is consistently weak across all three splits, reaching only 31/150 pooled endpoint successes. This preserves the contaminated-log negative control.
- The all-positive oracle reaches 105/150 pooled successes. Lift is learnable with broad true-positive support, but it is not near-saturated in the way the frozen Can oracle is.
- The paper-facing Lift claim should emphasize split-sensitive score-to-support conversion, strong weighted and positive-only baselines, and the unresolved precision/coverage tradeoff rather than a bad-label policy benefit.

## Artifacts

- Split 11 report: `results/final_paper/tables/lift_mg_mg_sparse_split11_endpoint_summary_REPORT.md`
- Split 22 report: `results/final_paper/tables/lift_mg_mg_sparse_split22_endpoint_summary_REPORT.md`
- Split 33 report: `results/final_paper/tables/lift_mg_mg_sparse_split33_endpoint_summary_REPORT.md`
