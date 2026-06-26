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
| pos_to_anchor_union_p20_alpha_0p05 | 0.550 | 0.550 | 86.5 | 20 |
| pos_to_anchor_union_p20_alpha_0p10 | 0.500 | 0.500 | 89.3 | 20 |
| pos_to_anchor_union_p20_alpha_0p20 | 0.500 | 0.500 | 92.5 | 20 |
| pos_to_anchor_union_p20_alpha_0p35 | 0.500 | 0.500 | 93.8 | 20 |
