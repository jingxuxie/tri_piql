# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_pos40_bad80_shuffle42_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `tri_pos40_bad80_shuffle42_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `74`.
Selected unlabeled demos: `64`.
Selected hidden-positive demos: `40`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_coverage_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 58.505374189173935, 'mass_cap_limit': 74, 'coverage_gap_selected_demo_count': 64, 'labeled_positive_demo_count': 10, 'score_gap': 0.02570521831512451, 'selected_score_mean': 0.6922503770329058, 'selected_score_min': 0.49130919575691223, 'selected_score_max': 0.9500983357429504, 'selected_demo_count': 64, 'selected_hidden_positive_demos': 40, 'selected_hidden_bad_demos': 24, 'selected_hidden_positive_purity': 0.625}`.
Demo weights: `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_seed0_setup/config.json
```
