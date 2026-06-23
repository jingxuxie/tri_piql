# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_adaptive_masscap_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max320_seed0_train`.
Validation-positive filter key: `tri_lift_mg_positive_plus_classifier_adaptive_masscap_unlabeled_demos_posx4_cap1p25_max320_seed0_valid_positive`.
Source: `positive_plus_classifier_adaptive_masscap_unlabeled_demos`.
Train demos: `289`.
Selected unlabeled demos: `279`.
Selected hidden-positive demos: `223`.
Selection diagnostics: `{'selection_rule': 'adaptive_masscap_coverage_gap', 'gap_select_max_unlabeled_demos': 320, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'adaptive_mass_cap_ratio': 1.25, 'estimated_positive_mass': 344.6088456096082, 'mass_cap_limit': 431, 'coverage_gap_selected_demo_count': 279, 'labeled_positive_demo_count': 10, 'score_gap': 0.012195110321044922, 'selected_score_mean': 0.8267217312662405, 'selected_score_min': 0.5434873700141907, 'selected_score_max': 0.994234025478363, 'selected_demo_count': 279, 'selected_hidden_positive_demos': 223, 'selected_hidden_bad_demos': 56, 'selected_hidden_positive_purity': 0.7992831541218638}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_adaptive_masscap_seed0_setup/config.json
```
