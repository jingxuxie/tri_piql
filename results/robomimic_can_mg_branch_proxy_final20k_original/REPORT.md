# Robomimic Official Checkpoint Selection Analysis

Split path: `results/robomimic_inspection/can_mg_low_dim_sparse/split_indices.json`.
Device: `cuda`.
Batch size: `100`.
Max validation batches: `80`.
Max train-support batches: `20`.

Offline score is Robomimic validation log-likelihood; higher is better.

## Selected Checkpoints

| run | filter | selected_epoch | selected_log_likelihood | selected_rollout_success | rollout_best_epoch | rollout_best_success |
| --- | --- | --- | --- | --- | --- | --- |
| weighted_seed0 | labeled_positive | 200 | -29419890.933 | 0.400 | 200 | 0.400 |
| weighted_seed0 | labeled_negative | 200 | -87436491.600 | 0.400 | 200 | 0.400 |
| weighted_seed0 | valid_positive | 200 | -39870417.800 | 0.400 | 200 | 0.400 |
| weighted_seed0 | valid_negative | 200 | -80141795.000 | 0.400 | 200 | 0.400 |
| weighted_seed1 | labeled_positive | 200 | -29541007.067 | 0.300 | 200 | 0.300 |
| weighted_seed1 | labeled_negative | 200 | -85718425.867 | 0.300 | 200 | 0.300 |
| weighted_seed1 | valid_positive | 200 | -39980764.000 | 0.300 | 200 | 0.300 |
| weighted_seed1 | valid_negative | 200 | -79626079.333 | 0.300 | 200 | 0.300 |
| weighted_seed2 | labeled_positive | 200 | -29525201.600 | 0.300 | 200 | 0.300 |
| weighted_seed2 | labeled_negative | 200 | -88076448.267 | 0.300 | 200 | 0.300 |
| weighted_seed2 | valid_positive | 200 | -40311210.800 | 0.300 | 200 | 0.300 |
| weighted_seed2 | valid_negative | 200 | -80199297.000 | 0.300 | 200 | 0.300 |
| posp10_seed0 | labeled_positive | 200 | -26326348.800 | 0.300 | 200 | 0.300 |
| posp10_seed0 | labeled_negative | 200 | -165217646.400 | 0.300 | 200 | 0.300 |
| posp10_seed0 | valid_positive | 200 | -46693059.600 | 0.300 | 200 | 0.300 |
| posp10_seed0 | valid_negative | 200 | -141431403.600 | 0.300 | 200 | 0.300 |
| posp10_seed1 | labeled_positive | 200 | -26521478.333 | 0.100 | 200 | 0.100 |
| posp10_seed1 | labeled_negative | 200 | -163151288.533 | 0.100 | 200 | 0.100 |
| posp10_seed1 | valid_positive | 200 | -45558678.533 | 0.100 | 200 | 0.100 |
| posp10_seed1 | valid_negative | 200 | -151576663.067 | 0.100 | 200 | 0.100 |
| posp10_seed2 | labeled_positive | 200 | -26445611.333 | 0.100 | 200 | 0.100 |
| posp10_seed2 | labeled_negative | 200 | -152148109.200 | 0.100 | 200 | 0.100 |
| posp10_seed2 | valid_positive | 200 | -44421914.400 | 0.100 | 200 | 0.100 |
| posp10_seed2 | valid_negative | 200 | -148155059.067 | 0.100 | 200 | 0.100 |
| allpositive_seed0 | labeled_positive | 200 | -24442544.333 | 0.400 | 200 | 0.400 |
| allpositive_seed0 | labeled_negative | 200 | -170995850.667 | 0.400 | 200 | 0.400 |
| allpositive_seed0 | valid_positive | 200 | -40449161.533 | 0.400 | 200 | 0.400 |
| allpositive_seed0 | valid_negative | 200 | -188305894.400 | 0.400 | 200 | 0.400 |
| allpositive_seed1 | labeled_positive | 200 | -24600052.600 | 0.000 | 200 | 0.000 |
| allpositive_seed1 | labeled_negative | 200 | -176116308.267 | 0.000 | 200 | 0.000 |
| allpositive_seed1 | valid_positive | 200 | -39571856.467 | 0.000 | 200 | 0.000 |
| allpositive_seed1 | valid_negative | 200 | -184597415.600 | 0.000 | 200 | 0.000 |
| allpositive_seed2 | labeled_positive | 200 | -23806442.200 | 0.200 | 200 | 0.200 |
| allpositive_seed2 | labeled_negative | 200 | -171775127.200 | 0.200 | 200 | 0.200 |
| allpositive_seed2 | valid_positive | 200 | -39964746.000 | 0.200 | 200 | 0.200 |
| allpositive_seed2 | valid_negative | 200 | -188177534.800 | 0.200 | 200 | 0.200 |
| alltrain_seed0 | labeled_positive | 200 | -33468480.133 | 0.200 | 200 | 0.200 |
| alltrain_seed0 | labeled_negative | 200 | -67658378.400 | 0.200 | 200 | 0.200 |
| alltrain_seed0 | valid_positive | 200 | -41383477.333 | 0.200 | 200 | 0.200 |
| alltrain_seed0 | valid_negative | 200 | -74121181.867 | 0.200 | 200 | 0.200 |
| alltrain_seed1 | labeled_positive | 200 | -35012513.733 | 0.100 | 200 | 0.100 |
| alltrain_seed1 | labeled_negative | 200 | -67593703.467 | 0.100 | 200 | 0.100 |
| alltrain_seed1 | valid_positive | 200 | -41510471.333 | 0.100 | 200 | 0.100 |
| alltrain_seed1 | valid_negative | 200 | -73606213.467 | 0.100 | 200 | 0.100 |
| alltrain_seed2 | labeled_positive | 200 | -34657440.667 | 0.000 | 200 | 0.000 |
| alltrain_seed2 | labeled_negative | 200 | -68179350.000 | 0.000 | 200 | 0.000 |
| alltrain_seed2 | valid_positive | 200 | -41103927.933 | 0.000 | 200 | 0.000 |
| alltrain_seed2 | valid_negative | 200 | -76951864.667 | 0.000 | 200 | 0.000 |

## Aggregate Selection Outcome

| filter | method | mean_selected_success | mean_rollout_best_success |
| --- | --- | --- | --- |
| labeled_positive | allpositive | 0.200 | 0.200 |
| labeled_positive | alltrain | 0.100 | 0.100 |
| labeled_positive | posp10 | 0.167 | 0.167 |
| labeled_positive | weighted | 0.333 | 0.333 |
| labeled_negative | allpositive | 0.200 | 0.200 |
| labeled_negative | alltrain | 0.100 | 0.100 |
| labeled_negative | posp10 | 0.167 | 0.167 |
| labeled_negative | weighted | 0.333 | 0.333 |
| valid_positive | allpositive | 0.200 | 0.200 |
| valid_positive | alltrain | 0.100 | 0.100 |
| valid_positive | posp10 | 0.167 | 0.167 |
| valid_positive | weighted | 0.333 | 0.333 |
| valid_negative | allpositive | 0.200 | 0.200 |
| valid_negative | alltrain | 0.100 | 0.100 |
| valid_negative | posp10 | 0.167 | 0.167 |
| valid_negative | weighted | 0.333 | 0.333 |

## Files

- `checkpoint_scores.csv`: per-checkpoint offline scores and rollout metrics.
- `selected_checkpoints.csv`: best checkpoint per offline filter.
