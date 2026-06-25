# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_weighted_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s22_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s22_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive`.
Source: `positive_plus_classifier_weighted_unlabeled_demos`.
Train demos: `1430`.
Selected unlabeled demos: `1420`.
Selected hidden-positive demos: `276`.
Selection diagnostics: `{'selection_rule': 'demo_probability_weighting', 'selected_score_mean': 0.28173127978610557, 'selected_score_min': 0.0011459364322945476, 'selected_score_max': 0.9965934157371521, 'selected_demo_count': 1420, 'selected_hidden_positive_demos': 276, 'selected_hidden_bad_demos': 1144, 'selected_hidden_positive_purity': 0.19436619718309858, 'weighted_unlabeled_floor': 0.05, 'demo_weight_min': 0.05, 'demo_weight_mean': 0.2963186010916333, 'demo_weight_max': 1.0, 'hidden_positive_demo_weight_mean': 0.7927015717748714, 'hidden_bad_demo_weight_mean': 0.17041080922305168}`.
Demo weights: `results/final_paper/per_seed/lift_mg_mg_sparse_split22_weighted_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/final_paper/per_seed/lift_mg_mg_sparse_split22_weighted_bc_policy0/setup/config.json --demo-weights results/final_paper/per_seed/lift_mg_mg_sparse_split22_weighted_bc_policy0/setup/demo_weights.json
```
