# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_posx4_pos40_bad80_seed1_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_pos40_bad80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed1_train`.
Validation-positive filter key: `tri_pos40_bad80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed1_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `87`.
Selected unlabeled demos: `77`.
Selected hidden-positive demos: `40`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'labeled_positive_demo_count': 10, 'score_gap': 0.023947060108184814, 'selected_score_mean': 0.5910140829426902, 'selected_score_min': 0.36289897561073303, 'selected_score_max': 0.8971351385116577, 'selected_demo_count': 77, 'selected_hidden_positive_demos': 40, 'selected_hidden_bad_demos': 37, 'selected_hidden_positive_purity': 0.5194805194805194}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_posx4_pos40_bad80_seed1_mlphead_setup/config.json
```
