# Robomimic Official Checkpoint Selection Analysis

Split path: `results/robomimic_inspection/can_mg_low_dim_sparse_shuffle42/split_indices.json`.
Device: `cuda`.
Batch size: `100`.
Max validation batches: `80`.
Max train-support batches: `20`.

Offline score is Robomimic validation log-likelihood; higher is better.

## Selected Checkpoints

| run | filter | selected_epoch | selected_log_likelihood | selected_rollout_success | rollout_best_epoch | rollout_best_success |
| --- | --- | --- | --- | --- | --- | --- |
| hard_posmin_seed0 | labeled_positive | 200 | -22915293.000 | 0.100 | 200 | 0.100 |
| hard_posmin_seed0 | labeled_negative | 200 | -193200925.867 | 0.100 | 200 | 0.100 |
| hard_posmin_seed0 | valid_positive | 200 | -42532609.667 | 0.100 | 200 | 0.100 |
| hard_posmin_seed0 | valid_negative | 200 | -141598784.400 | 0.100 | 200 | 0.100 |
| soft_weighted_seed0 | labeled_positive | 200 | -27205224.467 | 0.100 | 200 | 0.100 |
| soft_weighted_seed0 | labeled_negative | 200 | -92123728.267 | 0.100 | 200 | 0.100 |
| soft_weighted_seed0 | valid_positive | 200 | -38082416.600 | 0.100 | 200 | 0.100 |
| soft_weighted_seed0 | valid_negative | 200 | -73233349.200 | 0.100 | 200 | 0.100 |

## Aggregate Selection Outcome

| filter | method | mean_selected_success | mean_rollout_best_success |
| --- | --- | --- | --- |
| labeled_positive | hard_posmin | 0.100 | 0.100 |
| labeled_positive | soft_weighted | 0.100 | 0.100 |
| labeled_negative | hard_posmin | 0.100 | 0.100 |
| labeled_negative | soft_weighted | 0.100 | 0.100 |
| valid_positive | hard_posmin | 0.100 | 0.100 |
| valid_positive | soft_weighted | 0.100 | 0.100 |
| valid_negative | hard_posmin | 0.100 | 0.100 |
| valid_negative | soft_weighted | 0.100 | 0.100 |

## Files

- `checkpoint_scores.csv`: per-checkpoint offline scores and rollout metrics.
- `selected_checkpoints.csv`: best checkpoint per offline filter.
