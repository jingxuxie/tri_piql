# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `1`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Source transitions: `3512`.
Selected unlabeled transitions: `2314`.
Selected unlabeled demos: `23`.
Selected hidden-positive demos: `23`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.022979557514190674, 'selected_score_mean': 0.9372869004373965, 'selected_score_min': 0.8776872754096985, 'selected_score_max': 0.9853120446205139, 'selected_demo_count': 23, 'selected_hidden_positive_demos': 23, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.
Candidate unlabeled demos: `120`.
Diversity weight: `0.35`.
Gap max/min demos: `80` / `4`.
Unlabeled threshold: `0.9`.
Components: `5`.
Feature mode: `obs`.
Policy modes: `['mode']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `10`.
Evaluation horizon: `400`.
Evaluated checkpoints: `[5000]`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos | 0.400 | 0.400 | 285.3 |

## Classifier

- Labeled accuracy: `0.982`.
- Positive/negative logit mean: `11.887` / `-14.596`.
- Unlabeled probability mean: `0.539`.
- Selected unlabeled transitions: `2314`.
- Selected unlabeled probability mean: `0.936`.
- Selected hidden-positive demos: `23` / `23`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
