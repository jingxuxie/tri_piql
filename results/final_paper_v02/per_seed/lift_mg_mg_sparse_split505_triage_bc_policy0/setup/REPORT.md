# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s505_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s505_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `215`.
Selected unlabeled demos: `205`.
Selected hidden-positive demos: `187`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.859283983707428, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.859283983707428, 'labeled_positive_score_p10': 0.9110668182373047, 'labeled_positive_score_mean': 0.9549706757068634, 'labeled_negative_score_max': 0.12219002097845078, 'labeled_negative_score_mean': 0.044860271038487554, 'selected_score_mean': 0.9616928871085004, 'selected_score_min': 0.8595808148384094, 'selected_score_max': 0.992784321308136, 'selected_demo_count': 205, 'selected_hidden_positive_demos': 187, 'selected_hidden_bad_demos': 18, 'selected_hidden_positive_purity': 0.9121951219512195}`.
Demo weights: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_triage_bc_policy0/setup/config.json
```
