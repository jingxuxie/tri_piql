# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_shuffle42_posmin_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_shuffle42_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `tri_lift_mg_shuffle42_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `212`.
Selected unlabeled demos: `202`.
Selected hidden-positive demos: `187`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8744307160377502, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8744307160377502, 'labeled_positive_score_p10': 0.8914384961128234, 'labeled_positive_score_mean': 0.96145578622818, 'labeled_negative_score_max': 0.07773955166339874, 'labeled_negative_score_mean': 0.04126857714727521, 'selected_score_mean': 0.9633941340564501, 'selected_score_min': 0.8766883611679077, 'selected_score_max': 0.9930689334869385, 'selected_demo_count': 202, 'selected_hidden_positive_demos': 187, 'selected_hidden_bad_demos': 15, 'selected_hidden_positive_purity': 0.9257425742574258}`.
Demo weights: `results/robomimic_lift_mg_shuffle42_posmin_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_shuffle42_posmin_seed0_setup/config.json
```
