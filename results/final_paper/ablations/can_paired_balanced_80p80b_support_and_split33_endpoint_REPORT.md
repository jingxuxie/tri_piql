# Can Paired 80p/80b Support And Split-33 Endpoint Diagnostic

This diagnostic revisits the balanced Can Paired setting under the frozen runner and fresh split seeds. The goal is to test whether this easier contamination regime can provide the missing bad-label policy-benefit evidence against the strong positive-only nearest-neighbor baseline.

Protocol:

- Task/split: Robomimic Can Paired low-dimensional data, 80 hidden-positive and 80 hidden-bad unlabeled demos.
- Split seeds: `11`, `22`, and `33` support audit.
- Endpoint training/evaluation: split seed `33` only, policy/classifier seed `0`.
- Backbone: official Robomimic BC-RNN-GMM, 200 epochs, 100 steps per epoch.
- Endpoint checkpoint: `model_epoch_200.pth`.
- Evaluation: 50 validation-positive initial-state rollouts, horizon 400, CPU fallback.
- Status: diagnostic only; this is not a completed three-split endpoint table.

## Support Audit

| split | method/setup | train demos | selected unlabeled | hidden-positive | hidden-bad | purity |
|---:|---|---:|---:|---:|---:|---:|
| 11 | TRIAGE-BC / adaptive masscap | 60 | 50 | 43 | 7 | 0.860 |
| 11 | positive-only NN top80 | 90 | 80 | 72 | 8 | 0.900 |
| 11 | classifier-score top80 | 90 | 80 | 63 | 17 | 0.787 |
| 22 | TRIAGE-BC / adaptive masscap | 85 | 75 | 55 | 20 | 0.733 |
| 22 | positive-only NN top80 | 90 | 80 | 76 | 4 | 0.950 |
| 22 | classifier-score top80 | 90 | 80 | 57 | 23 | 0.713 |
| 33 | TRIAGE-BC / adaptive masscap | 50 | 40 | 39 | 1 | 0.975 |
| 33 | positive-only NN top80 | 90 | 80 | 72 | 8 | 0.900 |
| 33 | classifier-score top80 | 90 | 80 | 70 | 10 | 0.875 |

## Split-33 Endpoint Results

| method | success | successes | train demos | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|---:|---:|---:|
| positive-only NN top80 | 0.980 | 49/50 | 90 | 80 | 72 | 8 | 0.900 |
| TRIAGE-BC / adaptive masscap | 0.860 | 43/50 | 50 | 40 | 39 | 1 | 0.975 |

## Interpretation

- The fresh support audit does not support a bad-aware advantage over positive-only NN on balanced Can. Positive-only NN has higher hidden-positive coverage on all three splits and higher support purity on splits 11 and 22.
- Split 33 was the best case for TRIAGE-BC because it selected a much purer support set than positive-only NN (`0.975` versus `0.900`). Even there, the endpoint result favors positive-only NN by 6 successes out of 50.
- Classifier-score top80 is not a rescue: it is lower-purity than positive-only NN on all three support audits.
- This result does not invalidate the older development balanced-Can score-to-support result, but it does mean the final paper should not use balanced Can as evidence that explicit bad labels beat strong no-bad-label retrieval. It is better framed as evidence that score-to-support conversion matters, while positive-only retrieval remains a central baseline.

## Artifacts

- CSV: `results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint.csv`
- Split-33 TRIAGE-BC run: `results/final_paper/per_seed/can_paired_balanced_80p80b_split33_triage_bc_policy0/REPORT.md`
- Split-33 positive-only NN run: `results/final_paper/per_seed/can_paired_balanced_80p80b_split33_positive_only_nn_policy0/REPORT.md`
- Split-11/22/33 support setup runs: `results/final_paper/per_seed/can_paired_balanced_80p80b_split*_policy0/REPORT.md`
