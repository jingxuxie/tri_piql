# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_posx4_seed0_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_train`.
Validation-positive filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `83`.
Selected unlabeled demos: `73`.
Selected hidden-positive demos: `67`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'labeled_positive_demo_count': 10, 'score_gap': 0.01969534158706665, 'selected_score_mean': 0.7241660078910932, 'selected_score_min': 0.5699806213378906, 'selected_score_max': 0.9103220701217651, 'selected_demo_count': 73, 'selected_hidden_positive_demos': 67, 'selected_hidden_bad_demos': 6, 'selected_hidden_positive_purity': 0.9178082191780822}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_posx4_seed0_mlphead_setup/config.json
```
