# Official Robomimic Policy Evaluation

Split path: `results/candidate_g_fresh_preflight/splits/can_paired_pos40_bad80_split707/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `400`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_200 | 0.750 | 0.750 | 181.9 | 20 |
