# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `0`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Source transitions: `3056`.
Selected unlabeled transitions: `1858`.
Selected unlabeled demos: `19`.
Selected hidden-positive demos: `19`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.030059635639190674, 'selected_score_mean': 0.9000322693272641, 'selected_score_min': 0.8483670353889465, 'selected_score_max': 0.9626666903495789, 'selected_demo_count': 19, 'selected_hidden_positive_demos': 19, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.
Candidate unlabeled demos: `120`.
Diversity weight: `0.35`.
Gap max/min demos: `80` / `4`.
Unlabeled threshold: `0.9`.
GMM support validation: `{'enabled': False}`.
GMM checkpoint selection metric: `support_val_nll`.
GMM selected checkpoint: `None`.
Retrain selected checkpoint on full support: `False`.
Components: `5`.
Feature mode: `obs_prev_action_time`.
Policy modes: `['mode']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `10`.
Evaluation horizon: `400`.
Evaluated checkpoints: `[5000, 10000]`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_step5000 | 0.100 | 0.100 | 396.9 |
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_step10000 | 0.000 | 0.000 | 400.0 |

## Checkpoint Selection

- Not used.

## Classifier

- Labeled accuracy: `0.983`.
- Positive/negative logit mean: `12.925` / `-18.032`.
- Unlabeled probability mean: `0.475`.
- Selected unlabeled transitions: `1858`.
- Selected unlabeled probability mean: `0.900`.
- Selected hidden-positive demos: `19` / `19`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
