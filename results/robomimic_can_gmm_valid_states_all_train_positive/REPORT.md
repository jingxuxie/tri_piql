# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim_budget80/split_indices.json`.
Source: `all_train_positive`.
Source transitions: `9826`.
Selected unlabeled transitions: `0`.
Unlabeled threshold: `0.9`.
Components: `5`.
Policy modes: `['mode', 'mean', 'sample']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `5`.
Evaluation horizon: `400`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_all_train_positive | 0.200 | 0.200 | 339.6 |
| gmm_mean_all_train_positive | 0.400 | 0.400 | 281.0 |
| gmm_sample_all_train_positive | 0.400 | 0.400 | 292.2 |

## Classifier

- Not used for this source.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
