# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train`.
Validation-positive filter key: `tri_can_mg_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive`.
Source: `positive_plus_classifier_weighted_unlabeled_demos`.
Train demos: `3850`.
Selected unlabeled demos: `3840`.
Selected hidden-positive demos: `688`.
Selection diagnostics: `{'selection_rule': 'demo_probability_weighting', 'selected_score_mean': 0.5068527655437767, 'selected_score_min': 6.03537519054953e-05, 'selected_score_max': 0.9992043972015381, 'selected_demo_count': 3840, 'selected_hidden_positive_demos': 688, 'selected_hidden_bad_demos': 3152, 'selected_hidden_positive_purity': 0.17916666666666667, 'weighted_unlabeled_floor': 0.05, 'demo_weight_min': 0.05, 'demo_weight_mean': 0.5147567128126884, 'demo_weight_max': 1.0, 'hidden_positive_demo_weight_mean': 0.8853604679624009, 'hidden_bad_demo_weight_mean': 0.43232402993994884}`.
Demo weights: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed0_setup/config.json --demo-weights results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed0_setup/demo_weights.json
```
