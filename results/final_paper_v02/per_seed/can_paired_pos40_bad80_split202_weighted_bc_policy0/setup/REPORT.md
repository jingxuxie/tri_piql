# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_weighted_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s202_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s202_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive`.
Source: `positive_plus_classifier_weighted_unlabeled_demos`.
Train demos: `130`.
Selected unlabeled demos: `120`.
Selected hidden-positive demos: `40`.
Selection diagnostics: `{'selection_rule': 'demo_probability_weighting', 'selected_score_mean': 0.38891162001527846, 'selected_score_min': 0.008301638066768646, 'selected_score_max': 0.9101269841194153, 'selected_demo_count': 120, 'selected_hidden_positive_demos': 40, 'selected_hidden_bad_demos': 80, 'selected_hidden_positive_purity': 0.3333333333333333, 'weighted_unlabeled_floor': 0.05, 'demo_weight_min': 0.05, 'demo_weight_mean': 0.4376496884857233, 'demo_weight_max': 1.0, 'hidden_positive_demo_weight_mean': 0.6433442264795304, 'hidden_bad_demo_weight_mean': 0.2645086305495351}`.
Demo weights: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_weighted_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_weighted_bc_policy0/setup/config.json --demo-weights results/final_paper_v02/per_seed/can_paired_pos40_bad80_split202_weighted_bc_policy0/setup/demo_weights.json
```
