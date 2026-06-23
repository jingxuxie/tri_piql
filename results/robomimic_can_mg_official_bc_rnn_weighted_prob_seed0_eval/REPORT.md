# Official Robomimic Policy Evaluation

Split path: `results/robomimic_inspection/can_mg_low_dim_sparse/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `10`.
Eval horizon: `400`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_50 | 0.000 | 0.000 | 400.0 | 10 |
| model_epoch_100 | 0.300 | 0.300 | 340.2 | 10 |
| model_epoch_150 | 0.200 | 0.200 | 371.8 | 10 |
| model_epoch_200 | 0.400 | 0.400 | 293.7 | 10 |
