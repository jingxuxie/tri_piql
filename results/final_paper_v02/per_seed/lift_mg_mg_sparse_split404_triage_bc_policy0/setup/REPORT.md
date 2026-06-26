# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s404_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s404_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `219`.
Selected unlabeled demos: `209`.
Selected hidden-positive demos: `177`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.958652675151825, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.958652675151825, 'labeled_positive_score_p10': 0.9621277451515198, 'labeled_positive_score_mean': 0.9819824814796447, 'labeled_negative_score_max': 0.09083239734172821, 'labeled_negative_score_mean': 0.01826809422345832, 'selected_score_mean': 0.986631897077606, 'selected_score_min': 0.95917147397995, 'selected_score_max': 0.9995840191841125, 'selected_demo_count': 209, 'selected_hidden_positive_demos': 177, 'selected_hidden_bad_demos': 32, 'selected_hidden_positive_purity': 0.84688995215311}`.
Demo weights: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_triage_bc_policy0/setup/config.json
```
