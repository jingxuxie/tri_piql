# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s22_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s22_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `171`.
Selected unlabeled demos: `161`.
Selected hidden-positive demos: `150`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8712196946144104, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8712196946144104, 'labeled_positive_score_p10': 0.9068349778652192, 'labeled_positive_score_mean': 0.9584247708320618, 'labeled_negative_score_max': 0.11494369804859161, 'labeled_negative_score_mean': 0.044899206375703216, 'selected_score_mean': 0.957823926247425, 'selected_score_min': 0.8727981448173523, 'selected_score_max': 0.996583878993988, 'selected_demo_count': 161, 'selected_hidden_positive_demos': 150, 'selected_hidden_bad_demos': 11, 'selected_hidden_positive_purity': 0.9316770186335404}`.
Demo weights: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/lift_mg_mg_sparse_split22_triage_bc_policy0/setup/config.json
```
