# Robomimic Inspection

HDF5 path: `data/robomimic/v1.5/transport/mh/low_dim_v15.hdf5`.
Environment: `TwoArmTransport`.

## Dataset

- Demos: `300`.
- Positive demos: `300`.
- Negative demos: `0`.
- Return p10/p50/p90: `5.000` / `5.000` / `6.000`.
- Length p10/p50/p90: `451.8` / `630.0` / `824.1`.
- Masks: `{'20_percent': 60, '20_percent_train': 54, '20_percent_valid': 6, '50_percent': 144, '50_percent_train': 132, '50_percent_valid': 12, 'better': 50, 'better_train': 45, 'better_valid': 5, 'okay': 50, 'okay_better': 50, 'okay_better_train': 45, 'okay_better_valid': 5, 'okay_train': 45, 'okay_valid': 5, 'train': 270, 'valid': 30, 'worse': 50, 'worse_better': 50, 'worse_better_train': 45, 'worse_better_valid': 5, 'worse_okay': 50, 'worse_okay_train': 45, 'worse_okay_valid': 5, 'worse_train': 45, 'worse_valid': 5}`.
- Fallback split used: `False`.
- Observation keys: `['object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_eef_quat_site', 'robot0_gripper_qpos', 'robot0_gripper_qvel', 'robot0_joint_pos', 'robot0_joint_pos_cos', 'robot0_joint_pos_sin', 'robot0_joint_vel', 'robot1_eef_pos', 'robot1_eef_quat', 'robot1_eef_quat_site', 'robot1_gripper_qpos', 'robot1_gripper_qvel', 'robot1_joint_pos', 'robot1_joint_pos_cos', 'robot1_joint_pos_sin', 'robot1_joint_vel']`.
- Action shape: `[14]`.

## Default Tri-Signal Split

- Labeled positives: `10`.
- Labeled negatives: `0`.
- Unlabeled train demos: `260`.
- Hidden-positive unlabeled demos: `260`.
- Hidden-negative unlabeled demos: `0`.
- Validation positives: `30`.
- Validation negatives: `0`.

## Interpretation

- Positive and negative labels are derived from total sparse reward, not from paired same-initial-state demonstrations.
- This is useful for cross-task mixed-quality validation, but it is a weaker bad-demo setting than Can Paired.
