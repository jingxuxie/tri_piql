# Lift MG Classifier-Score Top160 Ablation

This ablation tests whether the frozen Lift coverage failure can be fixed by replacing the current `pos_min` threshold with a broader fixed classifier-score top160 support rule.

Protocol:

- Task/split: Robomimic Lift MG sparse low-dimensional data.
- Split seeds: `11`, `22`, and `33`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Support rule: labeled positives plus the top 160 unlabeled demos by classifier trajectory score.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts per split, horizon 150, CPU fallback.
- Status: ablation only; this is not part of the frozen main five-method table.

## Endpoint Results

| method | split 11 | split 22 | split 33 | pooled successes | pooled success |
|---|---:|---:|---:|---:|---:|
| classifier-score top160 | 0.320 | 0.380 | 0.660 | 68/150 | 0.453 |
| TRIAGE-BC / pos-min | 0.540 | 0.500 | 0.440 | 74/150 | 0.493 |
| positive-only NN top160 | 0.460 | 0.680 | 0.500 | 82/150 | 0.547 |
| weighted BC | 0.480 | 0.660 | 0.720 | 93/150 | 0.620 |

## Support Audit

| split | selected unlabeled | hidden-positive | hidden-bad | purity |
|---:|---:|---:|---:|---:|
| 11 | 160 | 154 | 6 | 0.963 |
| 22 | 160 | 150 | 10 | 0.938 |
| 33 | 160 | 158 | 2 | 0.988 |

## Interpretation

- The ablation partially fixes split 33: classifier-score top160 reaches 33/50, compared with 22/50 for TRIAGE-BC / pos-min and 25/50 for positive-only NN top160.
- It fails as a general Lift converter: split 11 drops to 16/50 and split 22 drops to 19/50, despite high support purity on both splits.
- Pooled over the three splits, classifier-score top160 reaches 68/150, below TRIAGE-BC / pos-min at 74/150, positive-only NN top160 at 82/150, and weighted BC at 93/150.
- The result rules out a simple fixed classifier top-k rescue. Lift needs a policy-quality or distribution-shape converter, not just a broader high-purity support set.

## Artifacts

- Split 11 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_classifier_topk_policy0/REPORT.md`
- Split 22 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_classifier_topk_policy0/REPORT.md`
- Split 33 run: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_classifier_topk_policy0/REPORT.md`
