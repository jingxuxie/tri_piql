# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_weighted_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s33_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s33_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive`.
Source: `positive_plus_classifier_weighted_unlabeled_demos`.
Train demos: `1430`.
Selected unlabeled demos: `1420`.
Selected hidden-positive demos: `276`.
Selection diagnostics: `{'selection_rule': 'demo_probability_weighting', 'selected_score_mean': 0.2048355721791921, 'selected_score_min': 0.0007617786759510636, 'selected_score_max': 0.9984444379806519, 'selected_demo_count': 1420, 'selected_hidden_positive_demos': 276, 'selected_hidden_bad_demos': 1144, 'selected_hidden_positive_purity': 0.19436619718309858, 'weighted_unlabeled_floor': 0.05, 'demo_weight_min': 0.05, 'demo_weight_mean': 0.2279799477219373, 'demo_weight_max': 1.0, 'hidden_positive_demo_weight_mean': 0.7377372388633482, 'hidden_bad_demo_weight_mean': 0.09824811828329222}`.
Demo weights: `results/final_paper/per_seed/lift_mg_mg_sparse_split33_weighted_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/final_paper/per_seed/lift_mg_mg_sparse_split33_weighted_bc_policy0/setup/config.json --demo-weights results/final_paper/per_seed/lift_mg_mg_sparse_split33_weighted_bc_policy0/setup/demo_weights.json
```
