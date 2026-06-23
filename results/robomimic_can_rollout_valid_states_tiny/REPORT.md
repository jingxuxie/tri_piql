# Robomimic Can Rollout Smoke

Split path: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Environment: `PickPlaceCan` version `1.5.1`.
Observation keys: `['object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_eef_quat_site', 'robot0_gripper_qpos', 'robot0_gripper_qvel', 'robot0_joint_pos', 'robot0_joint_pos_cos', 'robot0_joint_pos_sin', 'robot0_joint_vel']`.
BC steps: `50`.
State-action classifier steps: `50`.
Evaluation episodes: `1`.
Evaluation horizon: `20`.
Evaluation init mode: `valid_positive_states`.
Candidate count: `8`.

## Rollout Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_labeled_positive | 0.000 | 0.000 | 20.0 |
| bc_pos_unlabeled | 0.000 | 0.000 | 20.0 |
| bc_all | 0.000 | 0.000 | 20.0 |
| weighted_bc_state_action | 0.000 | 0.000 | 20.0 |
| bc_positive_sa_rerank_noise0.1_penalty0.05 | 0.000 | 0.000 | 20.0 |

## State-Action Classifier

- Train labeled accuracy: `0.682`.
- Held-out validation accuracy: `0.687`.
- Validation positive/negative logit mean: `0.249` / `-0.247`.
- Unlabeled positive probability mean: `0.508`.

## Interpretation

- This is a short simulator smoke, not a final Robomimic benchmark.
- It tests whether the scarce-label policies trained from low-dimensional paired data can produce nonzero Can task success under the recovered robosuite environment.
- If all policies are near zero, the immediate issue is rollout-capable imitation strength, not the tri-signal objective.
