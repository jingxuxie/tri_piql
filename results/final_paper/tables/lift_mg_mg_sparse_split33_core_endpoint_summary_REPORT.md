# Lift MG Sparse Split-33 Core Endpoint Summary

This is the third frozen final-paper Lift MG sparse row for the core TRIAGE / weighted / positive-only comparison under `METHOD_FREEZE.md`.

The full split-33 row with all-demo BC and all-positive oracle controls is now staged in `results/final_paper/tables/lift_mg_mg_sparse_split33_endpoint_summary_REPORT.md`. This report is kept as the matched core comparison artifact.

Protocol:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seed: `33`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts, horizon 150.
- Evaluation device: CPU fallback; checkpoint, seed, init-state mode, episode count, and horizon are shared across methods.

This report intentionally summarizes only the three matched non-oracle core methods.

## Endpoint Results

| method | success | successes | train demos | selected unlabeled | support purity |
|---|---:|---:|---:|---:|---:|
| weighted BC | 0.720 | 36/50 | 1430 | 1420 weighted | 0.194 |
| positive-only NN top160 | 0.500 | 25/50 | 170 | 160 | 0.906 |
| TRIAGE-BC / pos-min | 0.440 | 22/50 | 112 | 102 | 1.000 |

## Support Audit

| method | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| TRIAGE-BC / pos-min | 102 | 102 | 0 | 1.000 |
| weighted BC | 1420 | 276 | 1144 | 0.194 |
| positive-only NN top160 | 160 | 145 | 15 | 0.906 |

## Interpretation

- Split 33 strengthens the coverage caveat: TRIAGE-BC has perfect selected-support purity, but selects only 102 hidden positives and reaches 0.440.
- Positive-only NN keeps high support purity while selecting broader hidden-positive support, and reaches 0.500.
- Weighted BC is the clear fixed-endpoint winner on this split at 0.720, despite low raw hidden-positive support fraction in the weighted train mask.
- Together with split 22, this argues against presenting Lift as a bad-label policy win. The stronger Lift claim is that bad labels can improve support purity, while the policy-level converter still needs a better precision/coverage rule.

## Artifacts

- TRIAGE-BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_weighted_bc_policy0/REPORT.md`
- Positive-only NN run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_positive_only_nn_policy0/REPORT.md`
- Full split-33 report: `results/final_paper/tables/lift_mg_mg_sparse_split33_endpoint_summary_REPORT.md`
