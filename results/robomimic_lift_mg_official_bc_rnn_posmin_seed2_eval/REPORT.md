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
| model_epoch_50 | 0.000 | 0.000 | 150.0 | 10 |
| model_epoch_100 | 0.200 | 0.200 | 127.8 | 10 |
| model_epoch_150 | 0.500 | 0.500 | 93.5 | 10 |
| model_epoch_200 | 0.800 | 0.800 | 61.4 | 10 |
