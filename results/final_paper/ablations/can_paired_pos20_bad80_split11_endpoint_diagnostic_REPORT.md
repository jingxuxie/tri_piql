# Can Paired 20p/80b Split-11 Endpoint Diagnostic

This diagnostic tests whether the heavier Can Paired contamination setting rescues the bad-label policy-benefit claim under the frozen runner. It is a single fresh split row, not a main table result.

Protocol:

- Task/split: Robomimic Can Paired low-dimensional data, 20 labeled positives and 80 labeled bad demos.
- Split seed: `11`.
- Policy/classifier seed: `0`.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts, horizon 400, CPU fallback.
- Status: diagnostic only; more split seeds would be needed before using this as a primary Can 20p/80b result.

## Endpoint Results

| method | success | successes | train demos | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|---:|---:|---:|
| positive-only NN top20 | 0.680 | 34/50 | 30 | 20 | 17 | 3 | 0.850 |
| TRIAGE-BC / adaptive masscap | 0.660 | 33/50 | 60 | 50 | 20 | 30 | 0.400 |
| weighted BC sampler | 0.360 | 18/50 | 110 | 100 weighted | 20 | 80 | 0.200 |

## Setup-Only Audit

The classifier-score top20 hard-support ablation was prepared but not trained or evaluated because its support audit was already weaker than positive-only NN on this split.

| setup branch | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| classifier-score top20 | 20 | 11 | 9 | 0.550 |

## Interpretation

- This split does not support a bad-label policy-benefit claim. Positive-only NN top20 is the best completed endpoint row, with 34/50 successes versus 33/50 for TRIAGE-BC.
- TRIAGE-BC recovers all 20 hidden-positive unlabeled demos, but the adaptive masscap branch also admits 30 hidden-bad demos. That extra coverage is not enough to beat the cleaner positive-only support.
- Weighted BC is the clear loser here: it samples from the full 100-demo contaminated pool and reaches only 18/50 successes.
- The result is still useful for the paper because it strengthens the support-conversion story: soft weighting can fail badly under heavy action-conflicting contamination, while positive-only retrieval remains a hard baseline that must be treated as first-class.

## Artifacts

- CSV: `results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic.csv`
- Positive-only NN run: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_positive_only_nn_policy0/REPORT.md`
- TRIAGE-BC run: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_triage_bc_policy0/REPORT.md`
- Weighted BC run: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_weighted_bc_policy0/REPORT.md`
- Classifier-score top20 setup: `results/final_paper/per_seed/can_paired_pos20_bad80_split11_classifier_topk_policy0/REPORT.md`
