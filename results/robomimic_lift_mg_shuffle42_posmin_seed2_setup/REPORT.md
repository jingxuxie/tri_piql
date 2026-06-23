# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_shuffle42_posmin_seed2_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_shuffle42_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed2_train`.
Validation-positive filter key: `tri_lift_mg_shuffle42_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed2_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `211`.
Selected unlabeled demos: `201`.
Selected hidden-positive demos: `188`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8792799711227417, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8792799711227417, 'labeled_positive_score_p10': 0.8883804380893707, 'labeled_positive_score_mean': 0.9617653727531433, 'labeled_negative_score_max': 0.0691322535276413, 'labeled_negative_score_mean': 0.03721309350803494, 'selected_score_mean': 0.9639327534988745, 'selected_score_min': 0.8822791576385498, 'selected_score_max': 0.9950882792472839, 'selected_demo_count': 201, 'selected_hidden_positive_demos': 188, 'selected_hidden_bad_demos': 13, 'selected_hidden_positive_purity': 0.9353233830845771}`.
Demo weights: `results/robomimic_lift_mg_shuffle42_posmin_seed2_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_shuffle42_posmin_seed2_setup/config.json
```
