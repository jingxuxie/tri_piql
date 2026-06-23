# Official Robomimic Policy Evaluation

Split path: `results/robomimic_inspection/lift_mg_low_dim_sparse/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Environment: `Lift` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `10`.
Eval horizon: `150`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_50 | 0.100 | 0.100 | 138.5 | 10 |
| model_epoch_100 | 0.400 | 0.400 | 105.1 | 10 |
| model_epoch_150 | 0.600 | 0.600 | 84.2 | 10 |
| model_epoch_200 | 0.600 | 0.600 | 85.3 | 10 |
