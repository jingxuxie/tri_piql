# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s11_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s11_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `188`.
Selected unlabeled demos: `178`.
Selected hidden-positive demos: `169`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8976201415061951, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8976201415061951, 'labeled_positive_score_p10': 0.9272027611732483, 'labeled_positive_score_mean': 0.9544438540935516, 'labeled_negative_score_max': 0.1579708307981491, 'labeled_negative_score_mean': 0.0478479799348861, 'selected_score_mean': 0.9692671724249807, 'selected_score_min': 0.8976823091506958, 'selected_score_max': 0.9976680278778076, 'selected_demo_count': 178, 'selected_hidden_positive_demos': 169, 'selected_hidden_bad_demos': 9, 'selected_hidden_positive_purity': 0.949438202247191}`.
Demo weights: `results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/lift_mg_mg_sparse_split11_triage_bc_policy0/setup/config.json
```
