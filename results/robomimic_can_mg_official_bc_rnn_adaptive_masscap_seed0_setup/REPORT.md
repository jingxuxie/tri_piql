# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_official_bc_rnn_adaptive_masscap_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_positive_plus_classifier_adaptive_masscap_unlabeled_demos_min4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `tri_can_mg_positive_plus_classifier_adaptive_masscap_unlabeled_demos_min4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `16`.
Selected unlabeled demos: `6`.
Selected hidden-positive demos: `3`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_coverage_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 0.0, 'gap_select_effective_min_unlabeled_demos': 4, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 1955.9040771456066, 'mass_cap_limit': 2445, 'coverage_gap_selected_demo_count': 6, 'labeled_positive_demo_count': 10, 'score_gap': 0.00012022256851196289, 'selected_score_mean': 0.9991680979728699, 'selected_score_min': 0.9991466999053955, 'selected_score_max': 0.9992043972015381, 'selected_demo_count': 6, 'selected_hidden_positive_demos': 3, 'selected_hidden_bad_demos': 3, 'selected_hidden_positive_purity': 0.5}`.
Demo weights: `results/robomimic_can_mg_official_bc_rnn_adaptive_masscap_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_can_mg_official_bc_rnn_adaptive_masscap_seed0_setup/config.json
```
