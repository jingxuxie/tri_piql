# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `0`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Source transitions: `3470`.
Selected unlabeled transitions: `2272`.
Selected unlabeled demos: `23`.
Selected hidden-positive demos: `23`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.0378037691116333, 'selected_score_mean': 0.9071355306583903, 'selected_score_min': 0.8311644792556763, 'selected_score_max': 0.9692974090576172, 'selected_demo_count': 23, 'selected_hidden_positive_demos': 23, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.
Candidate unlabeled demos: `120`.
Diversity weight: `0.35`.
Gap max/min demos: `80` / `4`.
Unlabeled threshold: `0.9`.
GMM support validation: `{'enabled': True, 'unit': 'demo', 'requested_frac': 0.2, 'train_transitions': 2753, 'validation_transitions': 717, 'train_demos': 26, 'validation_demos': 7, 'validation_demo_ids': ['demo_1', 'demo_17', 'demo_23', 'demo_157', 'demo_159', 'demo_171', 'demo_199']}`.
GMM checkpoint selection metric: `support_val_mode_mse`.
GMM selected checkpoint: `2500`.
Retrain selected checkpoint on full support: `True`.
Components: `5`.
Feature mode: `obs`.
Policy modes: `['mode']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `10`.
Evaluation horizon: `400`.
Evaluated checkpoints: `[2500, 5000, 10000, 20000]`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train_step2500 | 0.000 | 0.000 | 400.0 |
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train_step5000 | 0.100 | 0.100 | 370.2 |
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train_step10000 | 0.300 | 0.300 | 310.4 |
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train_step20000 | 0.000 | 0.000 | 400.0 |
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_support_val_mode_mse_selected_full_step2500 | 0.000 | 0.000 | 400.0 |

## Checkpoint Selection

| checkpoint_step | support_train_nll | support_val_nll | support_val_mode_mse | support_val_mean_mse |
|---:|---:|---:|---:|---:|
| 2500 | -17.422 | 41.458 | 0.035938 | 0.032864 |
| 5000 | -18.794 | 55.160 | 0.039345 | 0.033596 |
| 10000 | -19.877 | 80.991 | 0.040724 | 0.035513 |
| 20000 | -20.714 | 138.568 | 0.045370 | 0.039984 |

## Classifier

- Labeled accuracy: `0.981`.
- Positive/negative logit mean: `12.396` / `-15.081`.
- Unlabeled probability mean: `0.526`.
- Selected unlabeled transitions: `2272`.
- Selected unlabeled probability mean: `0.907`.
- Selected hidden-positive demos: `23` / `23`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
