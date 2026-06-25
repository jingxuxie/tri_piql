# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split202_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s202_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s202_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `231`.
Selected unlabeled demos: `221`.
Selected hidden-positive demos: `186`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8534078001976013, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8534078001976013, 'labeled_positive_score_p10': 0.8838635325431824, 'labeled_positive_score_mean': 0.9415299654006958, 'labeled_negative_score_max': 0.18194518983364105, 'labeled_negative_score_mean': 0.06213191319257021, 'selected_score_mean': 0.9508465436788706, 'selected_score_min': 0.8540734648704529, 'selected_score_max': 0.9927799701690674, 'selected_demo_count': 221, 'selected_hidden_positive_demos': 186, 'selected_hidden_bad_demos': 35, 'selected_hidden_positive_purity': 0.8416289592760181}`.
Demo weights: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split202_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split202_triage_bc_policy0/setup/config.json
```
