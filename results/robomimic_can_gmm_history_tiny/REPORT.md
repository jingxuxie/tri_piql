# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Source: `positive_plus_classifier_unlabeled`.
Source transitions: `1199`.
Selected unlabeled transitions: `1`.
Unlabeled threshold: `0.9`.
Components: `3`.
Feature mode: `obs_prev_action_time`.
Policy modes: `['mode', 'mean', 'classifier_rerank']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `1`.
Evaluation horizon: `20`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_positive_plus_classifier_unlabeled | 0.000 | 0.000 | 20.0 |
| gmm_mean_positive_plus_classifier_unlabeled | 0.000 | 0.000 | 20.0 |
| gmm_classifier_rerank_positive_plus_classifier_unlabeled | 0.000 | 0.000 | 20.0 |

## Classifier

- Labeled accuracy: `0.697`.
- Positive/negative logit mean: `0.083` / `-0.370`.
- Unlabeled probability mean: `0.485`.
- Selected unlabeled transitions: `1`.
- Selected unlabeled probability mean: `0.747`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
