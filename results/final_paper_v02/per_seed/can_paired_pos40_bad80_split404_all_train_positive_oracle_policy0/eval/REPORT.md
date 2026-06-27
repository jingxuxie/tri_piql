# Official Robomimic Policy Evaluation

Split path: `results/final_paper_v02/splits/can_paired_pos40_bad80_split404/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `400`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_50 | 0.180 | 0.180 | 350.1 | 50 |
| model_epoch_100 | 0.840 | 0.840 | 158.3 | 50 |
| model_epoch_150 | 0.960 | 0.960 | 122.6 | 50 |
| model_epoch_200 | 0.980 | 0.980 | 113.3 | 50 |
