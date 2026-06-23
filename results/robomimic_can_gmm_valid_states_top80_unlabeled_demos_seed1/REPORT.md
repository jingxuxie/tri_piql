# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `1`.
Source: `positive_plus_classifier_top_unlabeled_demos`.
Source transitions: `9015`.
Selected unlabeled transitions: `7817`.
Selected unlabeled demos: `80`.
Selected hidden-positive demos: `59`.
Unlabeled threshold: `0.9`.
Components: `5`.
Feature mode: `obs`.
Policy modes: `['mode', 'mean', 'classifier_rerank']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `5`.
Evaluation horizon: `400`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_positive_plus_classifier_top_unlabeled_demos | 0.000 | 0.000 | 400.0 |
| gmm_mean_positive_plus_classifier_top_unlabeled_demos | 0.000 | 0.000 | 400.0 |
| gmm_classifier_rerank_positive_plus_classifier_top_unlabeled_demos | 0.000 | 0.000 | 400.0 |

## Classifier

- Labeled accuracy: `0.982`.
- Positive/negative logit mean: `11.887` / `-14.596`.
- Unlabeled probability mean: `0.539`.
- Selected unlabeled transitions: `7817`.
- Selected unlabeled probability mean: `0.758`.
- Selected hidden-positive demos: `59` / `80`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
