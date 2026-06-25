# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_classifier_topk_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s33_positive_plus_classifier_top_unlabeled_demos_top160_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s33_positive_plus_classifier_top_unlabeled_demos_top160_seed0_valid_positive`.
Source: `positive_plus_classifier_top_unlabeled_demos`.
Train demos: `170`.
Selected unlabeled demos: `160`.
Selected hidden-positive demos: `158`.
Selection diagnostics: `{'selection_rule': 'fixed_top', 'requested_demos': 160, 'selected_demo_count': 160, 'selected_hidden_positive_demos': 158, 'selected_hidden_bad_demos': 2, 'selected_hidden_positive_purity': 0.9875}`.
Demo weights: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_classifier_topk_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/lift_mg_mg_sparse_split33_classifier_topk_policy0/setup/config.json
```
