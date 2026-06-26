# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s404_positive_plus_positive_nn_top_unlabeled_demos_top160_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s404_positive_plus_positive_nn_top_unlabeled_demos_top160_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `170`.
Selected unlabeled demos: `160`.
Selected hidden-positive demos: `115`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 160, 'selected_demo_count': 160, 'selected_hidden_positive_demos': 115, 'selected_hidden_bad_demos': 45, 'selected_hidden_positive_purity': 0.71875, 'selected_score_mean': -0.1926568710245192, 'selected_score_min': -0.2883921265602112, 'selected_score_max': -0.04449332505464554}`.
Demo weights: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split404_positive_only_nn_policy0/setup/config.json
```
