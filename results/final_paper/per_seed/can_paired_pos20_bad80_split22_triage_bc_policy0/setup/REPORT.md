# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos20_bad80_s22_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_train`.
Validation-positive filter key: `final_can_paired_pos20_bad80_s22_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `63`.
Selected unlabeled demos: `53`.
Selected hidden-positive demos: `18`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_top_estimated_mass', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 52.54555173976604, 'mass_cap_limit': 66, 'coverage_gap_selected_demo_count': 74, 'labeled_positive_demo_count': 10, 'score_gap': 0.050289809703826904, 'selected_score_mean': 0.7624047983367488, 'selected_score_min': 0.5284693837165833, 'selected_score_max': 0.9984932541847229, 'selected_demo_count': 53, 'selected_hidden_positive_demos': 18, 'selected_hidden_bad_demos': 35, 'selected_hidden_positive_purity': 0.33962264150943394}`.
Demo weights: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/can_paired_pos20_bad80_split22_triage_bc_policy0/setup/config.json
```
