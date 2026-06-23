# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train`.
Validation-positive filter key: `tri_lift_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive`.
Source: `positive_plus_classifier_weighted_unlabeled_demos`.
Train demos: `1430`.
Selected unlabeled demos: `1420`.
Selected hidden-positive demos: `276`.
Selection diagnostics: `{'selection_rule': 'demo_probability_weighting', 'selected_score_mean': 0.2696311329620969, 'selected_score_min': 0.001510328846052289, 'selected_score_max': 0.990500271320343, 'selected_demo_count': 1420, 'selected_hidden_positive_demos': 276, 'selected_hidden_bad_demos': 1144, 'selected_hidden_positive_purity': 0.19436619718309858, 'weighted_unlabeled_floor': 0.05, 'demo_weight_min': 0.05, 'demo_weight_mean': 0.2831439866719546, 'demo_weight_max': 1.0, 'hidden_positive_demo_weight_mean': 0.7551109811237109, 'hidden_bad_demo_weight_mean': 0.16301159978212487}`.
Demo weights: `results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed0_setup/config.json --demo-weights results/robomimic_lift_mg_official_bc_rnn_weighted_prob_seed0_setup/demo_weights.json
```
