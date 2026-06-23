# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `0`.
Source: `positive_plus_classifier_diverse_unlabeled_demos`.
Source transitions: `9005`.
Selected unlabeled transitions: `7807`.
Selected unlabeled demos: `80`.
Selected hidden-positive demos: `58`.
Candidate unlabeled demos: `120`.
Diversity weight: `0.35`.
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
| gmm_mode_positive_plus_classifier_diverse_unlabeled_demos | 0.000 | 0.000 | 400.0 |
| gmm_mean_positive_plus_classifier_diverse_unlabeled_demos | 0.000 | 0.000 | 400.0 |
| gmm_classifier_rerank_positive_plus_classifier_diverse_unlabeled_demos | 0.000 | 0.000 | 400.0 |

## Classifier

- Labeled accuracy: `0.981`.
- Positive/negative logit mean: `12.396` / `-15.081`.
- Unlabeled probability mean: `0.526`.
- Selected unlabeled transitions: `7807`.
- Selected unlabeled probability mean: `0.740`.
- Selected hidden-positive demos: `58` / `80`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
