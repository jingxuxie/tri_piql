# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/can_paired_pos20_bad80_split33_weighted_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos20_bad80_s33_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train`.
Validation-positive filter key: `final_can_paired_pos20_bad80_s33_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive`.
Source: `positive_plus_classifier_weighted_unlabeled_demos`.
Train demos: `110`.
Selected unlabeled demos: `100`.
Selected hidden-positive demos: `20`.
Selection diagnostics: `{'selection_rule': 'demo_probability_weighting', 'selected_score_mean': 0.3609439489804208, 'selected_score_min': 0.01776551641523838, 'selected_score_max': 0.9174340963363647, 'selected_demo_count': 100, 'selected_hidden_positive_demos': 20, 'selected_hidden_bad_demos': 80, 'selected_hidden_positive_purity': 0.2, 'weighted_unlabeled_floor': 0.05, 'demo_weight_min': 0.05, 'demo_weight_mean': 0.4201141903955827, 'demo_weight_max': 1.0, 'hidden_positive_demo_weight_mean': 0.6758986234664917, 'hidden_bad_demo_weight_mean': 0.2836823559273034}`.
Demo weights: `results/final_paper/per_seed/can_paired_pos20_bad80_split33_weighted_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/final_paper/per_seed/can_paired_pos20_bad80_split33_weighted_bc_policy0/setup/config.json --demo-weights results/final_paper/per_seed/can_paired_pos20_bad80_split33_weighted_bc_policy0/setup/demo_weights.json
```
