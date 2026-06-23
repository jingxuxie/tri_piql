# Robomimic Inspection

HDF5 path: `data/robomimic/v1.5/square/mh/low_dim_v15.hdf5`.
Environment: `NutAssemblySquare`.

## Dataset

- Demos: `300`.
- Positive demos: `300`.
- Negative demos: `0`.
- Return p10/p50/p90: `5.000` / `5.000` / `5.000`.
- Length p10/p50/p90: `154.9` / `239.5` / `396.9`.
- Masks: `{'20_percent': 60, '20_percent_train': 54, '20_percent_valid': 6, '50_percent': 144, '50_percent_train': 132, '50_percent_valid': 12, 'better': 100, 'better_operator_1': 50, 'better_operator_1_train': 45, 'better_operator_1_valid': 5, 'better_operator_2': 50, 'better_operator_2_train': 45, 'better_operator_2_valid': 5, 'better_train': 90, 'better_valid': 10, 'okay': 100, 'okay_better': 200, 'okay_better_train': 180, 'okay_better_valid': 20, 'okay_operator_1': 50, 'okay_operator_1_train': 45, 'okay_operator_1_valid': 5, 'okay_operator_2': 50, 'okay_operator_2_train': 45, 'okay_operator_2_valid': 5, 'okay_train': 90, 'okay_valid': 10, 'train': 270, 'valid': 30, 'worse': 100, 'worse_better': 200, 'worse_better_train': 180, 'worse_better_valid': 20, 'worse_okay': 200, 'worse_okay_train': 180, 'worse_okay_valid': 20, 'worse_operator_1': 50, 'worse_operator_1_train': 45, 'worse_operator_1_valid': 5, 'worse_operator_2': 50, 'worse_operator_2_train': 45, 'worse_operator_2_valid': 5, 'worse_train': 90, 'worse_valid': 10}`.
- Fallback split used: `False`.
- Observation keys: `['object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_eef_quat_site', 'robot0_gripper_qpos', 'robot0_gripper_qvel', 'robot0_joint_pos', 'robot0_joint_pos_cos', 'robot0_joint_pos_sin', 'robot0_joint_vel']`.
- Action shape: `[7]`.

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
