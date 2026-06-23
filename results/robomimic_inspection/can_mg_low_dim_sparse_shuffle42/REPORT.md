# Robomimic Inspection

HDF5 path: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Environment: `PickPlaceCan`.

## Dataset

- Demos: `3900`.
- Positive demos: `718`.
- Negative demos: `3182`.
- Return p10/p50/p90: `0.000` / `0.000` / `72.000`.
- Length p10/p50/p90: `150.0` / `150.0` / `150.0`.
- Masks: `{'tri_can_mg_all_train_demos_seed0_train': 3860, 'tri_can_mg_all_train_demos_seed0_valid_positive': 20, 'tri_can_mg_all_train_demos_seed1_train': 3860, 'tri_can_mg_all_train_demos_seed1_valid_positive': 20, 'tri_can_mg_all_train_demos_seed2_train': 3860, 'tri_can_mg_all_train_demos_seed2_valid_positive': 20, 'tri_can_mg_all_train_positive_seed0_train': 698, 'tri_can_mg_all_train_positive_seed0_valid_positive': 20, 'tri_can_mg_all_train_positive_seed1_train': 698, 'tri_can_mg_all_train_positive_seed1_valid_positive': 20, 'tri_can_mg_all_train_positive_seed2_train': 698, 'tri_can_mg_all_train_positive_seed2_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_adaptive_masscap_unlabeled_demos_min4_cap1p25_max80_seed0_train': 16, 'tri_can_mg_positive_plus_classifier_adaptive_masscap_unlabeled_demos_min4_cap1p25_max80_seed0_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train': 1049, 'tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed0_train': 724, 'tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed0_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed1_train': 789, 'tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed1_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed2_train': 836, 'tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed2_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_gap_unlabeled_demos_posx4_max800_seed0_train': 809, 'tri_can_mg_positive_plus_classifier_gap_unlabeled_demos_posx4_max800_seed0_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_top_unlabeled_demos_top160_seed0_train': 170, 'tri_can_mg_positive_plus_classifier_top_unlabeled_demos_top160_seed0_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train': 3850, 'tri_can_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed1_train': 3850, 'tri_can_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed1_valid_positive': 20, 'tri_can_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed2_train': 3850, 'tri_can_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed2_valid_positive': 20}`.
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
