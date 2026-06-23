# Robomimic Inspection

HDF5 path: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Environment: `Lift`.

## Dataset

- Demos: `1500`.
- Positive demos: `316`.
- Negative demos: `1184`.
- Return p10/p50/p90: `0.000` / `0.000` / `103.100`.
- Length p10/p50/p90: `150.0` / `150.0` / `150.0`.
- Masks: `{}`.
- Fallback split used: `True`.
- Observation keys: `['object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_eef_quat_site', 'robot0_gripper_qpos', 'robot0_gripper_qvel', 'robot0_joint_pos', 'robot0_joint_pos_cos', 'robot0_joint_pos_sin', 'robot0_joint_vel']`.
- Action shape: `[7]`.

## Default Tri-Signal Split

- Labeled positives: `10`.
- Labeled negatives: `10`.
- Unlabeled train demos: `1420`.
- Hidden-positive unlabeled demos: `276`.
- Hidden-negative unlabeled demos: `1144`.
- Validation positives: `30`.
- Validation negatives: `30`.

## Interpretation

- Positive and negative labels are derived from total sparse reward, not from paired same-initial-state demonstrations.
- This is useful for cross-task mixed-quality validation, but it is a weaker bad-demo setting than Can Paired.
