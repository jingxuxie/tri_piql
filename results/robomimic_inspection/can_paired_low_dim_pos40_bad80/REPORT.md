# Robomimic Inspection: Can Paired Low-Dim

HDF5 path: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.

## Dataset

- Demos: `200`.
- Positive demos: `100`.
- Negative demos: `100`.
- Return p10/p50/p90: `0.000` / `2.500` / `5.000`.
- Length p10/p50/p90: `73.9` / `97.5` / `127.1`.
- Masks: `{'train': 180, 'tri_labeled_positive_seed0_train': 10, 'tri_labeled_positive_seed0_valid_positive': 10, 'tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_train': 83, 'tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_valid_positive': 10, 'tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed1_train': 55, 'tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed1_valid_positive': 10, 'tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed2_train': 76, 'tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed2_valid_positive': 10, 'tri_positive_plus_classifier_gap_unlabeled_demos_seed0_train': 83, 'tri_positive_plus_classifier_gap_unlabeled_demos_seed0_valid_positive': 10, 'tri_positive_plus_classifier_gap_unlabeled_demos_seed1_train': 55, 'tri_positive_plus_classifier_gap_unlabeled_demos_seed1_valid_positive': 10, 'tri_positive_plus_classifier_gap_unlabeled_demos_seed2_train': 76, 'tri_positive_plus_classifier_gap_unlabeled_demos_seed2_valid_positive': 10, 'tri_positive_plus_classifier_top_unlabeled_demos_seed0_train': 90, 'tri_positive_plus_classifier_top_unlabeled_demos_seed0_valid_positive': 10, 'tri_positive_plus_classifier_top_unlabeled_demos_seed1_train': 90, 'tri_positive_plus_classifier_top_unlabeled_demos_seed1_valid_positive': 10, 'tri_positive_plus_classifier_top_unlabeled_demos_seed2_train': 90, 'tri_positive_plus_classifier_top_unlabeled_demos_seed2_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_train': 58, 'tri_stress_p20_b80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed1_train': 66, 'tri_stress_p20_b80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed1_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed2_train': 63, 'tri_stress_p20_b80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed2_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top20_seed0_train': 30, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top20_seed0_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top20_seed1_train': 30, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top20_seed1_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top20_seed2_train': 30, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top20_seed2_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top80_seed0_train': 90, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top80_seed0_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top80_seed1_train': 90, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top80_seed1_valid_positive': 10, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top80_seed2_train': 90, 'tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top80_seed2_valid_positive': 10, 'valid': 20}`.
- Observation keys: `['object', 'robot0_eef_pos', 'robot0_eef_quat', 'robot0_eef_quat_site', 'robot0_gripper_qpos', 'robot0_gripper_qvel', 'robot0_joint_pos', 'robot0_joint_pos_cos', 'robot0_joint_pos_sin', 'robot0_joint_vel']`.
- Action shape: `[7]`.

## Default Tri-Signal Split

- Labeled positives: `10`.
- Labeled negatives: `10`.
- Unlabeled train demos: `120`.
- Hidden-positive unlabeled demos: `40`.
- Hidden-negative unlabeled demos: `80`.
- Validation positives: `10`.
- Validation negatives: `10`.

## Interpretation

- The paired dataset is exactly balanced: even demo ids are failures, odd demo ids are paired successes.
- This is a strong target for testing scarce good/bad labels plus a large unlabeled mixed pool.
