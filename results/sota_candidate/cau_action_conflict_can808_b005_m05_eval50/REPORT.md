# Official Robomimic Policy Evaluation

Split path: `results/candidate_f_can_fresh_validation/splits/can_paired_pos40_bad80_split808/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `400`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_100 | 0.500 | 0.500 | 256.7 | 50 |
| model_epoch_200 | 0.760 | 0.760 | 178.9 | 50 |
