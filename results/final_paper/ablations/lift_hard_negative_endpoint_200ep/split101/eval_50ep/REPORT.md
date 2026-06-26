# Official Robomimic Policy Evaluation

Split path: `results/final_paper/ablations/lift_hard_negative_action_conflict_splits/split101/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Environment: `Lift` version `1.5.1`.
Eval init mode: `valid_positive_states`.
Eval episodes: `50`.
Eval horizon: `150`.
Device: `cuda`.

## Rollout Metrics

| checkpoint | success_rate | avg_return | avg_len | eval_episodes |
|---|---:|---:|---:|---:|
| model_epoch_200 | 0.140 | 0.140 | 137.3 | 50 |
| model_epoch_200 | 0.060 | 0.060 | 143.6 | 50 |
