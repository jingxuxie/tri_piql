# Official Robomimic BC-RNN Setup

Config: `results/robomimic_square_quality_adaptive_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/square/mh/low_dim_v15.hdf5`.
Train filter key: `tri_square_quality_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `tri_square_quality_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `69`.
Selected unlabeled demos: `59`.
Selected hidden-positive demos: `42`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_coverage_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 71.85162728470814, 'mass_cap_limit': 90, 'coverage_gap_selected_demo_count': 59, 'labeled_positive_demo_count': 10, 'score_gap': 0.03466236591339111, 'selected_score_mean': 0.7802173353857913, 'selected_score_min': 0.5865707397460938, 'selected_score_max': 0.996790885925293, 'selected_demo_count': 59, 'selected_hidden_positive_demos': 42, 'selected_hidden_bad_demos': 17, 'selected_hidden_positive_purity': 0.711864406779661}`.
Demo weights: `results/robomimic_square_quality_adaptive_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_square_quality_adaptive_seed0_setup/config.json
```
