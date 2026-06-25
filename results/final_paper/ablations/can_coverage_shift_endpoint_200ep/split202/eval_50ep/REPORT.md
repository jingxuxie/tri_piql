# Official Robomimic Policy Evaluation

Split path: `results/final_paper/ablations/can_coverage_shift_splits/split202/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `400`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_200 | 0.820 | 0.820 | 174.5 | 50 |
| model_epoch_200 | 0.580 | 0.580 | 238.5 | 50 |
