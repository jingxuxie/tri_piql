# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s505_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s505_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `55`.
Selected unlabeled demos: `45`.
Selected hidden-positive demos: `36`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_coverage_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 53.52372571132551, 'mass_cap_limit': 67, 'coverage_gap_selected_demo_count': 45, 'labeled_positive_demo_count': 10, 'score_gap': 0.016127049922943115, 'selected_score_mean': 0.7316301955117119, 'selected_score_min': 0.5591181516647339, 'selected_score_max': 0.9641896486282349, 'selected_demo_count': 45, 'selected_hidden_positive_demos': 36, 'selected_hidden_bad_demos': 9, 'selected_hidden_positive_purity': 0.8}`.
Demo weights: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/can_paired_pos40_bad80_split505_triage_bc_policy0/setup/config.json
```
