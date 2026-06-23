# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_posx4_seed2_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed2_train`.
Validation-positive filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed2_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `76`.
Selected unlabeled demos: `66`.
Selected hidden-positive demos: `65`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'labeled_positive_demo_count': 10, 'score_gap': 0.016429603099822998, 'selected_score_mean': 0.7294957240422567, 'selected_score_min': 0.589424192905426, 'selected_score_max': 0.8913596272468567, 'selected_demo_count': 66, 'selected_hidden_positive_demos': 65, 'selected_hidden_bad_demos': 1, 'selected_hidden_positive_purity': 0.9848484848484849}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_posx4_seed2_mlphead_setup/config.json
```
