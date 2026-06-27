# Official Robomimic Policy Evaluation

Split path: `results/final_paper_v02/splits/lift_mg_mg_sparse_split505/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Environment: `Lift` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `150`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_50 | 0.140 | 0.140 | 138.1 | 50 |
| model_epoch_100 | 0.660 | 0.660 | 78.6 | 50 |
| model_epoch_150 | 0.740 | 0.740 | 68.9 | 50 |
| model_epoch_200 | 0.780 | 0.780 | 60.1 | 50 |
