# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split101_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s101_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s101_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `301`.
Selected unlabeled demos: `291`.
Selected hidden-positive demos: `177`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8801381587982178, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8801381587982178, 'labeled_positive_score_p10': 0.916141825914383, 'labeled_positive_score_mean': 0.9542256534099579, 'labeled_negative_score_max': 0.21386297047138214, 'labeled_negative_score_mean': 0.05298184698913246, 'selected_score_mean': 0.9611384649456981, 'selected_score_min': 0.8804973363876343, 'selected_score_max': 0.9954630732536316, 'selected_demo_count': 291, 'selected_hidden_positive_demos': 177, 'selected_hidden_bad_demos': 114, 'selected_hidden_positive_purity': 0.6082474226804123}`.
Demo weights: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split101_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split101_triage_bc_policy0/setup/config.json
```
