# Official Robomimic BC-RNN Setup

Config: `results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split909_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s909_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s909_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `89`.
Selected unlabeled demos: `79`.
Selected hidden-positive demos: `39`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_coverage_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 64.6886250054251, 'mass_cap_limit': 81, 'coverage_gap_selected_demo_count': 79, 'labeled_positive_demo_count': 10, 'score_gap': 0.030198991298675537, 'selected_score_mean': 0.7101259925697423, 'selected_score_min': 0.4423215687274933, 'selected_score_max': 0.9881289005279541, 'selected_demo_count': 79, 'selected_hidden_positive_demos': 39, 'selected_hidden_bad_demos': 40, 'selected_hidden_positive_purity': 0.4936708860759494}`.
Demo weights: `results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split909_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split909_triage_bc_policy0/setup/config.json
```
