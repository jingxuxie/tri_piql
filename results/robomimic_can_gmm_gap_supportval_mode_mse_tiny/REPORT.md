# Robomimic Can GMM Policy Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
Seed: `0`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Source transitions: `1552`.
Selected unlabeled transitions: `354`.
Selected unlabeled demos: `4`.
Selected hidden-positive demos: `4`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 20, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.0005297064781188965, 'selected_score_mean': 0.5104244202375412, 'selected_score_min': 0.5093724131584167, 'selected_score_max': 0.5118085145950317, 'selected_demo_count': 4, 'selected_hidden_positive_demos': 4, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.
Candidate unlabeled demos: `120`.
Diversity weight: `0.35`.
Gap max/min demos: `20` / `4`.
Unlabeled threshold: `0.9`.
GMM support validation: `{'enabled': True, 'unit': 'demo', 'requested_frac': 0.2, 'train_transitions': 1256, 'validation_transitions': 296, 'train_demos': 11, 'validation_demos': 3, 'validation_demo_ids': ['demo_15', 'demo_139', 'demo_143']}`.
GMM checkpoint selection metric: `support_val_mode_mse`.
GMM selected checkpoint: `10`.
Retrain selected checkpoint on full support: `True`.
Components: `5`.
Feature mode: `obs`.
Policy modes: `['mode']`.
Evaluation init mode: `valid_positive_states`.
Evaluation episodes: `1`.
Evaluation horizon: `1`.
Evaluated checkpoints: `[5, 10]`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train_step5 | 0.000 | 0.000 | 1.0 |
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train_step10 | 0.000 | 0.000 | 1.0 |
| gmm_mode_positive_plus_classifier_gap_unlabeled_demos_support_val_mode_mse_selected_full_step10 | 0.000 | 0.000 | 1.0 |

## Checkpoint Selection

| checkpoint_step | support_train_nll | support_val_nll | support_val_mode_mse | support_val_mean_mse |
|---:|---:|---:|---:|---:|
| 5 | 7.095 | 7.096 | 0.242100 | 0.246974 |
| 10 | 6.783 | 6.764 | 0.232598 | 0.235216 |

## Classifier

- Labeled accuracy: `0.609`.
- Positive/negative logit mean: `0.010` / `-0.042`.
- Unlabeled probability mean: `0.497`.
- Selected unlabeled transitions: `354`.
- Selected unlabeled probability mean: `0.510`.
- Selected hidden-positive demos: `4` / `4`.

## Interpretation

- This is a compact learned action-distribution extractor for the Robomimic support signal.
- It tests whether a diagonal GMM policy can replace nonparametric KNN while using scarce good/bad labels to select unlabeled transitions.
- A useful result should beat scarce-positive-only KNN and the deterministic MLP BC smoke on the same held-out initial states.
