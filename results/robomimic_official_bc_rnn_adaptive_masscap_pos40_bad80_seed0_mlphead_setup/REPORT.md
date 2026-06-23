# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed0_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_pos40_bad80_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `tri_pos40_bad80_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `60`.
Selected unlabeled demos: `50`.
Selected hidden-positive demos: `36`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_top_estimated_mass', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 49.47595354787238, 'mass_cap_limit': 62, 'coverage_gap_selected_demo_count': 73, 'labeled_positive_demo_count': 10, 'score_gap': 0.0238192081451416, 'selected_score_mean': 0.6628337442874909, 'selected_score_min': 0.5008993148803711, 'selected_score_max': 0.8895639777183533, 'selected_demo_count': 50, 'selected_hidden_positive_demos': 36, 'selected_hidden_bad_demos': 14, 'selected_hidden_positive_purity': 0.72}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed0_mlphead_setup/config.json
```
