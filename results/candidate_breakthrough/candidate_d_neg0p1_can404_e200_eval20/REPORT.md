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
| model_epoch_100 | 0.700 | 0.700 | 198.8 | 20 |
| model_epoch_200 | 0.650 | 0.650 | 205.4 | 20 |
