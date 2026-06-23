# Robomimic Inspection: Can Paired Low-Dim

HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.

## Dataset

- Demos: `200`.
- Positive demos: `100`.
- Negative demos: `100`.
- Return p10/p50/p90: `0.000` / `2.500` / `5.000`.
- Length p10/p50/p90: `73.9` / `97.5` / `127.1`.
- Masks: `{'train': 180, 'valid': 20}`.
- Observation keys: `['object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_eef_quat_site', 'robot0_gripper_qpos', 'robot0_gripper_qvel', 'robot0_joint_pos', 'robot0_joint_pos_cos', 'robot0_joint_pos_sin', 'robot0_joint_vel']`.
- Action shape: `[7]`.

## Default Tri-Signal Split

- Labeled positives: `10`.
- Labeled negatives: `10`.
- Unlabeled train demos: `160`.
- Validation positives: `10`.
- Validation negatives: `10`.

## Interpretation

- The paired dataset is exactly balanced: even demo ids are failures, odd demo ids are paired successes.
- This is a strong target for testing scarce good/bad labels plus a large unlabeled mixed pool.
