# Official Robomimic Policy Evaluation

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `10`.
Eval horizon: `400`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_50 | 0.000 | 0.000 | 400.0 | 10 |
| model_epoch_100 | 0.000 | 0.000 | 400.0 | 10 |
| model_epoch_150 | 0.100 | 0.100 | 372.0 | 10 |
| model_epoch_200 | 0.000 | 0.000 | 400.0 | 10 |
