# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed0_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_pos40_bad80_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train`.
Validation-positive filter key: `tri_pos40_bad80_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive`.
Source: `positive_plus_classifier_weighted_unlabeled_demos`.
Train demos: `130`.
Selected unlabeled demos: `120`.
Selected hidden-positive demos: `40`.
Selection diagnostics: `{'selection_rule': 'demo_probability_weighting', 'selected_score_mean': 0.4477917493010561, 'selected_score_min': 0.0910591334104538, 'selected_score_max': 0.8535712361335754, 'selected_demo_count': 120, 'selected_hidden_positive_demos': 40, 'selected_hidden_bad_demos': 80, 'selected_hidden_positive_purity': 0.3333333333333333, 'weighted_unlabeled_floor': 0.05, 'demo_weight_min': 0.0910591334104538, 'demo_weight_mean': 0.4902693070471287, 'demo_weight_max': 1.0, 'hidden_positive_demo_weight_mean': 0.676599920541048, 'hidden_bad_demo_weight_mean': 0.3333876636810601}`.
Demo weights: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed0_mlphead_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed0_mlphead_setup/config.json --demo-weights results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed0_mlphead_setup/demo_weights.json
```
