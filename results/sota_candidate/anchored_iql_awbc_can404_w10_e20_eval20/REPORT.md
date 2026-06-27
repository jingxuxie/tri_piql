# Official Robomimic Policy Evaluation

Split path: `results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `20`.
Eval horizon: `400`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_5 | 0.500 | 0.500 | 248.2 | 20 |
| model_epoch_10 | 0.650 | 0.650 | 207.4 | 20 |
| model_epoch_15 | 0.550 | 0.550 | 235.0 | 20 |
| model_epoch_20 | 0.600 | 0.600 | 229.8 | 20 |
