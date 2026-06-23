# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_seed2_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_pos40_bad80_shuffle42_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed2_train`.
Validation-positive filter key: `tri_pos40_bad80_shuffle42_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed2_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `76`.
Selected unlabeled demos: `66`.
Selected hidden-positive demos: `40`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_coverage_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 58.85634821188336, 'mass_cap_limit': 74, 'coverage_gap_selected_demo_count': 66, 'labeled_positive_demo_count': 10, 'score_gap': 0.043101876974105835, 'selected_score_mean': 0.6859127030228124, 'selected_score_min': 0.45705077052116394, 'selected_score_max': 0.9486134648323059, 'selected_demo_count': 66, 'selected_hidden_positive_demos': 40, 'selected_hidden_bad_demos': 26, 'selected_hidden_positive_purity': 0.6060606060606061}`.
Demo weights: `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_seed2_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_seed2_setup/config.json
```
