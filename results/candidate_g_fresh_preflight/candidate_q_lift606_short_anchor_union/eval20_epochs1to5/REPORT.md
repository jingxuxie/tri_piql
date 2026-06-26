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
| model_epoch_1 | 0.500 | 0.500 | 90.4 | 20 |
| model_epoch_2 | 0.500 | 0.500 | 89.8 | 20 |
| model_epoch_3 | 0.450 | 0.450 | 96.3 | 20 |
| model_epoch_4 | 0.550 | 0.550 | 84.4 | 20 |
| model_epoch_5 | 0.500 | 0.500 | 91.7 | 20 |
