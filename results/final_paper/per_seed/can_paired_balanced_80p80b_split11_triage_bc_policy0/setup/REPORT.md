# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/can_paired_balanced_80p80b_split11_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_balanced_80p80b_s11_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `final_can_paired_balanced_80p80b_s11_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `60`.
Selected unlabeled demos: `50`.
Selected hidden-positive demos: `43`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_coverage_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 87.7194498717448, 'mass_cap_limit': 110, 'coverage_gap_selected_demo_count': 50, 'labeled_positive_demo_count': 10, 'score_gap': 0.022741198539733887, 'selected_score_mean': 0.8287491059303284, 'selected_score_min': 0.6969635486602783, 'selected_score_max': 0.9979547262191772, 'selected_demo_count': 50, 'selected_hidden_positive_demos': 43, 'selected_hidden_bad_demos': 7, 'selected_hidden_positive_purity': 0.86}`.
Demo weights: `results/final_paper/per_seed/can_paired_balanced_80p80b_split11_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/can_paired_balanced_80p80b_split11_triage_bc_policy0/setup/config.json
```
