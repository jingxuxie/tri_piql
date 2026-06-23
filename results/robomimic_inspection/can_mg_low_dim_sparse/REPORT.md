# Robomimic Inspection

HDF5 path: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Environment: `PickPlaceCan`.

## Dataset

- Demos: `3900`.
- Positive demos: `718`.
- Negative demos: `3182`.
- Return p10/p50/p90: `0.000` / `0.000` / `72.000`.
- Length p10/p50/p90: `150.0` / `150.0` / `150.0`.
- Masks: `{}`.
- Fallback split used: `True`.
- Observation keys: `['object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_eef_quat_site', 'robot0_gripper_qpos', 'robot0_gripper_qvel', 'robot0_joint_pos', 'robot0_joint_pos_cos', 'robot0_joint_pos_sin', 'robot0_joint_vel']`.
- Action shape: `[7]`.

## Default Tri-Signal Split

- Labeled positives: `10`.
- Labeled negatives: `10`.
- Unlabeled train demos: `3840`.
- Hidden-positive unlabeled demos: `688`.
- Hidden-negative unlabeled demos: `3152`.
- Validation positives: `20`.
- Validation negatives: `20`.

## Interpretation

- Positive and negative labels are derived from total sparse reward, not from paired same-initial-state demonstrations.
- This is useful for cross-task mixed-quality validation, but it is a weaker bad-demo setting than Can Paired.
