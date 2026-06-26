# Official Robomimic BC-RNN Setup

Config: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s707_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s707_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `57`.
Selected unlabeled demos: `47`.
Selected hidden-positive demos: `29`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_top_estimated_mass', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 46.86414093624916, 'mass_cap_limit': 59, 'coverage_gap_selected_demo_count': 73, 'labeled_positive_demo_count': 10, 'score_gap': 0.050914496183395386, 'selected_score_mean': 0.6870117073363446, 'selected_score_min': 0.5249602198600769, 'selected_score_max': 0.9868795871734619, 'selected_demo_count': 47, 'selected_hidden_positive_demos': 29, 'selected_hidden_bad_demos': 18, 'selected_hidden_positive_purity': 0.6170212765957447}`.
Demo weights: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_triage_bc_policy0/setup/config.json
```
