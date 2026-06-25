# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s303_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s303_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `385`.
Selected unlabeled demos: `375`.
Selected hidden-positive demos: `172`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.9633781909942627, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.9633781909942627, 'labeled_positive_score_p10': 0.9862179517745971, 'labeled_positive_score_mean': 0.99000004529953, 'labeled_negative_score_max': 0.01884549856185913, 'labeled_negative_score_mean': 0.008839241781970486, 'selected_score_mean': 0.9852984744707743, 'selected_score_min': 0.9634515643119812, 'selected_score_max': 0.9984009861946106, 'selected_demo_count': 375, 'selected_hidden_positive_demos': 172, 'selected_hidden_bad_demos': 203, 'selected_hidden_positive_purity': 0.45866666666666667}`.
Demo weights: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split303_triage_bc_policy0/setup/config.json
```
