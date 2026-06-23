# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_shuffle42_posmin_seed1_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_shuffle42_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed1_train`.
Validation-positive filter key: `tri_lift_mg_shuffle42_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed1_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `205`.
Selected unlabeled demos: `195`.
Selected hidden-positive demos: `180`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8818244338035583, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8818244338035583, 'labeled_positive_score_p10': 0.8905690789222718, 'labeled_positive_score_mean': 0.9602940857410431, 'labeled_negative_score_max': 0.06958817690610886, 'labeled_negative_score_mean': 0.03391636461019516, 'selected_score_mean': 0.9618964513142904, 'selected_score_min': 0.8838181495666504, 'selected_score_max': 0.9931061863899231, 'selected_demo_count': 195, 'selected_hidden_positive_demos': 180, 'selected_hidden_bad_demos': 15, 'selected_hidden_positive_purity': 0.9230769230769231}`.
Demo weights: `results/robomimic_lift_mg_shuffle42_posmin_seed1_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_shuffle42_posmin_seed1_setup/config.json
```
