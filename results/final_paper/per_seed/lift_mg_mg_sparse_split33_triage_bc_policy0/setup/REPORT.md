# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s33_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s33_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `112`.
Selected unlabeled demos: `102`.
Selected hidden-positive demos: `102`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.9400264620780945, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.9400264620780945, 'labeled_positive_score_p10': 0.968686830997467, 'labeled_positive_score_mean': 0.9804597198963165, 'labeled_negative_score_max': 0.053399182856082916, 'labeled_negative_score_mean': 0.020480460254475474, 'selected_score_mean': 0.9829617586790347, 'selected_score_min': 0.9454105496406555, 'selected_score_max': 0.9984444379806519, 'selected_demo_count': 102, 'selected_hidden_positive_demos': 102, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.
Demo weights: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/lift_mg_mg_sparse_split33_triage_bc_policy0/setup/config.json
```
