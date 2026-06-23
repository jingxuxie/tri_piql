# Official Robomimic Policy Evaluation

Split path: `results/robomimic_inspection/can_paired_low_dim_pos40_bad80/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `10`.
Eval horizon: `400`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_50 | 0.200 | 0.200 | 354.1 | 10 |
| model_epoch_100 | 0.600 | 0.600 | 235.7 | 10 |
| model_epoch_150 | 0.700 | 0.700 | 200.3 | 10 |
| model_epoch_200 | 0.600 | 0.600 | 225.3 | 10 |
