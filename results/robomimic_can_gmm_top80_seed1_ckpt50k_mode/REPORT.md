# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `1`.
Source: `positive_plus_classifier_top_unlabeled_demos`.
Source transitions: `9133`.
Selected unlabeled transitions: `7935`.
Selected unlabeled demos: `80`.
Selected hidden-positive demos: `63`.
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
| gmm_mode_positive_plus_classifier_top_unlabeled_demos_step20000 | 0.200 | 0.200 | 340.0 |
| gmm_mode_positive_plus_classifier_top_unlabeled_demos_step50000 | 0.200 | 0.200 | 344.3 |

## Classifier

- Labeled accuracy: `0.994`.
- Positive/negative logit mean: `25.913` / `-27.843`.
- Unlabeled probability mean: `0.513`.
- Selected unlabeled transitions: `7935`.
- Selected unlabeled probability mean: `0.731`.
- Selected hidden-positive demos: `63` / `80`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
