# Robomimic Official Checkpoint Selection Analysis

Split path: `results/robomimic_inspection/lift_mg_low_dim_sparse/split_indices.json`.
Device: `cuda`.
Batch size: `100`.
Max validation batches: `120`.
Max train-support batches: `50`.

Offline score is Robomimic validation log-likelihood; higher is better.

## Selected Checkpoints

| run | filter | selected_epoch | selected_log_likelihood | selected_rollout_success | rollout_best_epoch | rollout_best_success |
| --- | --- | --- | --- | --- | --- | --- |
| posmin_seed0 | train_support | 200 | -27611629.040 | 0.800 | 200 | 0.800 |
| posmin_seed0 | valid_all | 50 | -83791372.422 | 0.200 | 200 | 0.800 |
| posmin_seed0 | valid_positive | 200 | -53737007.067 | 0.800 | 200 | 0.800 |
| posmin_seed0 | labeled_positive | 200 | -20633985.633 | 0.800 | 200 | 0.800 |
| posmin_seed1 | train_support | 200 | -32177133.070 | 0.400 | 150 | 0.500 |
| posmin_seed1 | valid_all | 50 | -84538714.044 | 0.200 | 150 | 0.500 |
| posmin_seed1 | valid_positive | 100 | -54595036.533 | 0.200 | 150 | 0.500 |
| posmin_seed1 | labeled_positive | 200 | -21376940.533 | 0.400 | 150 | 0.500 |
| posmin_seed2 | train_support | 200 | -34290548.340 | 0.800 | 200 | 0.800 |
| posmin_seed2 | valid_all | 100 | -82716457.611 | 0.200 | 200 | 0.800 |
| posmin_seed2 | valid_positive | 200 | -50759466.489 | 0.800 | 200 | 0.800 |
| posmin_seed2 | labeled_positive | 200 | -20836018.600 | 0.800 | 200 | 0.800 |
| allpositive_seed0 | train_support | 200 | -29483114.700 | 0.800 | 200 | 0.800 |
| allpositive_seed0 | valid_all | 50 | -81736481.122 | 0.200 | 200 | 0.800 |
| allpositive_seed0 | valid_positive | 100 | -50270183.089 | 0.300 | 200 | 0.800 |
| allpositive_seed0 | labeled_positive | 200 | -21096087.533 | 0.800 | 200 | 0.800 |
| allpositive_seed1 | train_support | 200 | -29775315.840 | 0.500 | 150 | 0.700 |
| allpositive_seed1 | valid_all | 50 | -80501002.678 | 0.100 | 150 | 0.700 |
| allpositive_seed1 | valid_positive | 200 | -46309531.067 | 0.500 | 150 | 0.700 |
| allpositive_seed1 | labeled_positive | 200 | -21096962.400 | 0.500 | 150 | 0.700 |
| allpositive_seed2 | train_support | 200 | -28981301.860 | 0.600 | 150 | 0.700 |
| allpositive_seed2 | valid_all | 50 | -80219929.111 | 0.200 | 150 | 0.700 |
| allpositive_seed2 | valid_positive | 100 | -49153283.533 | 0.600 | 150 | 0.700 |
| allpositive_seed2 | labeled_positive | 200 | -20663830.733 | 0.600 | 150 | 0.700 |
| alltrain_seed0 | train_support | 50 | -107227298.240 | 0.100 | 150 | 0.300 |
| alltrain_seed0 | valid_all | 200 | -51301101.800 | 0.100 | 150 | 0.300 |
| alltrain_seed0 | valid_positive | 200 | -41956758.467 | 0.100 | 150 | 0.300 |
| alltrain_seed0 | labeled_positive | 200 | -27728817.533 | 0.100 | 150 | 0.300 |
| alltrain_seed1 | train_support | 200 | -109482903.040 | 0.300 | 200 | 0.300 |
| alltrain_seed1 | valid_all | 200 | -51831723.111 | 0.300 | 200 | 0.300 |
| alltrain_seed1 | valid_positive | 200 | -41949603.311 | 0.300 | 200 | 0.300 |
| alltrain_seed1 | labeled_positive | 200 | -28034183.533 | 0.300 | 200 | 0.300 |
| alltrain_seed2 | train_support | 200 | -107129306.880 | 0.200 | 200 | 0.200 |
| alltrain_seed2 | valid_all | 200 | -51605531.933 | 0.200 | 200 | 0.200 |
| alltrain_seed2 | valid_positive | 200 | -42293932.200 | 0.200 | 200 | 0.200 |
| alltrain_seed2 | labeled_positive | 200 | -28170880.067 | 0.200 | 200 | 0.200 |

## Aggregate Selection Outcome

| filter | method | mean selected success | mean rollout-best success |
| --- | --- | ---: | ---: |
| train_support | allpositive | 0.633 | 0.733 |
| train_support | alltrain | 0.200 | 0.267 |
| train_support | posmin | 0.667 | 0.700 |
| valid_all | allpositive | 0.167 | 0.733 |
| valid_all | alltrain | 0.200 | 0.267 |
| valid_all | posmin | 0.200 | 0.700 |
| valid_positive | allpositive | 0.467 | 0.733 |
| valid_positive | alltrain | 0.200 | 0.267 |
| valid_positive | posmin | 0.600 | 0.700 |
| labeled_positive | allpositive | 0.633 | 0.733 |
| labeled_positive | alltrain | 0.200 | 0.267 |
| labeled_positive | posmin | 0.667 | 0.700 |

## Interpretation

Offline likelihood is not a general hidden-label-free checkpoint selector on this Lift split. The random `valid_all` filter is especially misleading: because the validation set is half failed demos, it selects early checkpoints for the selected-support runs and collapses pos-min mean selected success from `0.700` rollout-best to `0.200`.

The labeled-positive and train-support filters mostly select the final checkpoint. That preserves the three-seed fixed-20k story already in the controls report: pos-min remains far above all-demo cloning and close to the all-positive oracle, but the seed-1 15k peak is not recovered by a simple likelihood selector.

This should be treated as a diagnostic negative result. It argues against claiming best-checkpoint numbers unless a stronger, predeclared checkpoint rule is added. It also explains why naive mixed-log BC is weak: likelihood on the bad-dominated data can improve while rollout success stays poor.

## Files

- `checkpoint_scores.csv`: per-checkpoint offline scores and rollout metrics.
- `selected_checkpoints.csv`: best checkpoint per offline filter.
