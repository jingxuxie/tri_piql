# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `1`.
Source: `labeled_positive`.
Source transitions: `1198`.
Selected unlabeled transitions: `0`.
Selected unlabeled demos: `0`.
Selected hidden-positive demos: `0`.
Candidate unlabeled demos: `120`.
Diversity weight: `0.35`.
Unlabeled threshold: `0.9`.
Components: `5`.
Feature mode: `obs`.
Policy modes: `['mode']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `10`.
Evaluation horizon: `400`.
Evaluated checkpoints: `[20000, 50000]`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_labeled_positive_step20000 | 0.100 | 0.100 | 371.8 |
| gmm_mode_labeled_positive_step50000 | 0.200 | 0.200 | 343.3 |

## Classifier

- Not used for this source.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
