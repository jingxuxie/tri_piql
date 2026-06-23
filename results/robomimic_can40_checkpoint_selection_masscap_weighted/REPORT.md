# Robomimic Official Checkpoint Selection Analysis

Split path: `results/robomimic_inspection/can_paired_low_dim_pos40_bad80/split_indices.json`.
Device: `cuda`.
Batch size: `100`.
Max validation batches: `80`.
Max train-support batches: `50`.

Offline score is Robomimic validation log-likelihood; higher is better.

## Selected Checkpoints

| run | filter | selected_epoch | selected_log_likelihood | selected_rollout_success | rollout_best_epoch | rollout_best_success |
| --- | --- | --- | --- | --- | --- | --- |
| masscap_seed0 | train_support | 200 | -2781356.065 | 0.800 | 150 | 0.800 |
| masscap_seed0 | valid_positive | 100 | -6225075.521 | 0.500 | 150 | 0.800 |
| masscap_seed0 | valid_negative | 200 | -9486484.583 | 0.800 | 150 | 0.800 |
| masscap_seed0 | labeled_positive | 200 | -3133318.594 | 0.800 | 150 | 0.800 |
| masscap_seed0 | labeled_negative | 100 | -13979726.182 | 0.500 | 150 | 0.800 |
| masscap_seed1 | train_support | 200 | -2914998.535 | 0.600 | 150 | 0.700 |
| masscap_seed1 | valid_positive | 50 | -6546329.000 | 0.200 | 150 | 0.700 |
| masscap_seed1 | valid_negative | 100 | -11095918.389 | 0.600 | 150 | 0.700 |
| masscap_seed1 | labeled_positive | 200 | -3064617.177 | 0.600 | 150 | 0.700 |
| masscap_seed1 | labeled_negative | 100 | -13926241.818 | 0.600 | 150 | 0.700 |
| masscap_seed2 | train_support | 200 | -2361822.455 | 0.800 | 200 | 0.800 |
| masscap_seed2 | valid_positive | 150 | -5624387.031 | 0.700 | 200 | 0.800 |
| masscap_seed2 | valid_negative | 200 | -10706969.833 | 0.800 | 200 | 0.800 |
| masscap_seed2 | labeled_positive | 200 | -2520193.979 | 0.800 | 200 | 0.800 |
| masscap_seed2 | labeled_negative | 200 | -12498144.773 | 0.800 | 200 | 0.800 |
| weighted_seed0 | train_support | 200 | -3120627.550 | 0.500 | 100 | 0.800 |
| weighted_seed0 | valid_positive | 100 | -5920410.062 | 0.800 | 100 | 0.800 |
| weighted_seed0 | valid_negative | 200 | -5999714.750 | 0.500 | 100 | 0.800 |
| weighted_seed0 | labeled_positive | 200 | -2796133.125 | 0.500 | 100 | 0.800 |
| weighted_seed0 | labeled_negative | 200 | -7298580.750 | 0.500 | 100 | 0.800 |
| weighted_seed1 | train_support | 200 | -3144470.993 | 0.600 | 100 | 0.600 |
| weighted_seed1 | valid_positive | 150 | -5725468.000 | 0.600 | 100 | 0.600 |
| weighted_seed1 | valid_negative | 200 | -6067816.611 | 0.600 | 100 | 0.600 |
| weighted_seed1 | labeled_positive | 200 | -2714221.000 | 0.600 | 100 | 0.600 |
| weighted_seed1 | labeled_negative | 200 | -7739084.750 | 0.600 | 100 | 0.600 |
| weighted_seed2 | train_support | 200 | -2958933.312 | 0.600 | 150 | 0.700 |
| weighted_seed2 | valid_positive | 200 | -5638195.604 | 0.600 | 150 | 0.700 |
| weighted_seed2 | valid_negative | 200 | -5343778.333 | 0.600 | 150 | 0.700 |
| weighted_seed2 | labeled_positive | 200 | -2629271.667 | 0.600 | 150 | 0.700 |
| weighted_seed2 | labeled_negative | 200 | -6878567.545 | 0.600 | 150 | 0.700 |

## Aggregate Selection Outcome

| filter | method | mean_selected_success | mean_rollout_best_success |
| --- | --- | --- | --- |
| train_support | masscap | 0.733 | 0.767 |
| train_support | weighted | 0.567 | 0.700 |
| valid_positive | masscap | 0.467 | 0.767 |
| valid_positive | weighted | 0.667 | 0.700 |
| valid_negative | masscap | 0.733 | 0.767 |
| valid_negative | weighted | 0.567 | 0.700 |
| labeled_positive | masscap | 0.733 | 0.767 |
| labeled_positive | weighted | 0.567 | 0.700 |
| labeled_negative | masscap | 0.633 | 0.767 |
| labeled_negative | weighted | 0.567 | 0.700 |

## Files

- `checkpoint_scores.csv`: per-checkpoint offline scores and rollout metrics.
- `selected_checkpoints.csv`: best checkpoint per offline filter.
