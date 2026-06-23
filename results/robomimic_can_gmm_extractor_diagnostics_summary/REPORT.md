# Robomimic GMM Run Summary

Run directories: `4`.

## Aggregate

| source | method | selector | ckpt metric | features | max steps | ckpt | train transitions | selected demos | eval eps | runs | seeds | success mean | success values | hidden-positive demos |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | score_gap |  | obs | 20000 | 5000 | 3470 | 23.0 | 10 | 1 | 0 | 0.400 | 0.400 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | score_gap |  | obs_prev_action_time | 10000 | 5000 | 3056 | 19.0 | 10 | 1 | 0 | 0.100 | 0.100 | 19.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | score_gap |  | obs | 20000 | 10000 | 3470 | 23.0 | 10 | 1 | 0 | 0.200 | 0.200 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | score_gap |  | obs_prev_action_time | 10000 | 10000 | 3056 | 19.0 | 10 | 1 | 0 | 0.000 | 0.000 | 19.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos | score_gap |  | obs | 20000 | 20000 | 3470 | 23.0 | 10 | 1 | 0 | 0.100 | 0.100 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_support_val_mode_mse_selected_full | score_gap | support_val_mode_mse | obs | 20000 | 2500 | 3470 | 23.0 | 10 | 1 | 0 | 0.000 | 0.000 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportnll_selected_full | score_gap |  | obs | 20000 | 2500 | 3470 | 23.0 | 10 | 1 | 0 | 0.000 | 0.000 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train | score_gap |  | obs | 20000 | 2500 | 3470 | 23.0 | 10 | 1 | 0 | 0.000 | 0.000 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train | score_gap | support_val_mode_mse | obs | 20000 | 2500 | 3470 | 23.0 | 10 | 1 | 0 | 0.000 | 0.000 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train | score_gap |  | obs | 20000 | 5000 | 3470 | 23.0 | 10 | 1 | 0 | 0.100 | 0.100 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train | score_gap | support_val_mode_mse | obs | 20000 | 5000 | 3470 | 23.0 | 10 | 1 | 0 | 0.100 | 0.100 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train | score_gap |  | obs | 20000 | 10000 | 3470 | 23.0 | 10 | 1 | 0 | 0.300 | 0.300 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train | score_gap | support_val_mode_mse | obs | 20000 | 10000 | 3470 | 23.0 | 10 | 1 | 0 | 0.300 | 0.300 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train | score_gap |  | obs | 20000 | 20000 | 3470 | 23.0 | 10 | 1 | 0 | 0.000 | 0.000 | 23.0 |
| positive_plus_classifier_gap_unlabeled_demos | gmm_mode_positive_plus_classifier_gap_unlabeled_demos_supportval_train | score_gap | support_val_mode_mse | obs | 20000 | 20000 | 3470 | 23.0 | 10 | 1 | 0 | 0.000 | 0.000 | 23.0 |

## Interpretation

- This summary aggregates completed smoke runs only; it does not rerun experiments.
- Treat low-episode or single-seed rows as triage evidence rather than final benchmark numbers.
