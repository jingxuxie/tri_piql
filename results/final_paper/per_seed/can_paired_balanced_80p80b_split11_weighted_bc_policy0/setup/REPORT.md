# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/can_paired_balanced_80p80b_split11_weighted_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_balanced_80p80b_s11_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_train`.
Validation-positive filter key: `final_can_paired_balanced_80p80b_s11_positive_plus_classifier_weighted_unlabeled_demos_floor0p05_seed0_valid_positive`.
Source: `positive_plus_classifier_weighted_unlabeled_demos`.
Train demos: `170`.
Selected unlabeled demos: `160`.
Selected hidden-positive demos: `80`.
Selection diagnostics: `{'selection_rule': 'demo_probability_weighting', 'selected_score_mean': 0.539812741917558, 'selected_score_min': 0.016758758574724197, 'selected_score_max': 0.997957170009613, 'selected_demo_count': 160, 'selected_hidden_positive_demos': 80, 'selected_hidden_bad_demos': 80, 'selected_hidden_positive_purity': 0.5, 'weighted_unlabeled_floor': 0.05, 'demo_weight_min': 0.05, 'demo_weight_mean': 0.567104525982457, 'demo_weight_max': 1.0, 'hidden_positive_demo_weight_mean': 0.7178782280534506, 'hidden_bad_demo_weight_mean': 0.3622188896592706}`.
Demo weights: `results/final_paper/per_seed/can_paired_balanced_80p80b_split11_weighted_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py --config results/final_paper/per_seed/can_paired_balanced_80p80b_split11_weighted_bc_policy0/setup/config.json --demo-weights results/final_paper/per_seed/can_paired_balanced_80p80b_split11_weighted_bc_policy0/setup/demo_weights.json
```
