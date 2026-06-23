# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Source: `positive_plus_classifier_top_unlabeled_demos`.
Source transitions: `5124`.
Selected unlabeled transitions: `3926`.
Selected unlabeled demos: `40`.
Selected hidden-positive demos: `40`.
Unlabeled threshold: `0.9`.
Components: `3`.
Feature mode: `obs`.
Policy modes: `['mode', 'mean', 'classifier_rerank']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `1`.
Evaluation horizon: `20`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_positive_plus_classifier_top_unlabeled_demos | 0.000 | 0.000 | 20.0 |
| gmm_mean_positive_plus_classifier_top_unlabeled_demos | 0.000 | 0.000 | 20.0 |
| gmm_classifier_rerank_positive_plus_classifier_top_unlabeled_demos | 0.000 | 0.000 | 20.0 |

## Classifier

- Labeled accuracy: `0.696`.
- Positive/negative logit mean: `0.079` / `-0.359`.
- Unlabeled probability mean: `0.488`.
- Selected unlabeled transitions: `3926`.
- Selected unlabeled probability mean: `0.537`.
- Selected hidden-positive demos: `40` / `40`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
