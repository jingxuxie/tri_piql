# Official Robomimic Policy Evaluation

Split path: `results/final_paper/splits/lift_mg_mg_sparse_split33/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Environment: `Lift` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `150`.
Device: `cpu`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_200 | 0.500 | 0.500 | 96.2 | 50 |
