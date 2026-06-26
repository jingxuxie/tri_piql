# Official Robomimic BC-RNN Setup

Config: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s707_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s707_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `182`.
Selected unlabeled demos: `172`.
Selected hidden-positive demos: `149`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.9298269748687744, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.9298269748687744, 'labeled_positive_score_p10': 0.965956062078476, 'labeled_positive_score_mean': 0.977165812253952, 'labeled_negative_score_max': 0.0989425778388977, 'labeled_negative_score_mean': 0.0233054056763649, 'selected_score_mean': 0.9736689530139746, 'selected_score_min': 0.9301170110702515, 'selected_score_max': 0.9982291460037231, 'selected_demo_count': 172, 'selected_hidden_positive_demos': 149, 'selected_hidden_bad_demos': 23, 'selected_hidden_positive_purity': 0.8662790697674418}`.
Demo weights: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split707_triage_bc_policy0/setup/config.json
```
