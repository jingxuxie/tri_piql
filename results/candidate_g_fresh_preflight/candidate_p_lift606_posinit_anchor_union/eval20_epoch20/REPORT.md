# Official Robomimic Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/lift_mg_mg_sparse_split606/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Environment: `Lift` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `150`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_20 | 0.550 | 0.550 | 94.2 | 20 |
