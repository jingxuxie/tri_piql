# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_official_bc_rnn_gap_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_positive_plus_classifier_gap_unlabeled_demos_posx4_max800_seed0_train`.
Validation-positive filter key: `tri_can_mg_positive_plus_classifier_gap_unlabeled_demos_posx4_max800_seed0_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `809`.
Selected unlabeled demos: `799`.
Selected hidden-positive demos: `403`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 800, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'labeled_positive_demo_count': 10, 'score_gap': 0.000861823558807373, 'selected_score_mean': 0.975655989220205, 'selected_score_min': 0.9319158792495728, 'selected_score_max': 0.9992043972015381, 'selected_demo_count': 799, 'selected_hidden_positive_demos': 403, 'selected_hidden_bad_demos': 396, 'selected_hidden_positive_purity': 0.5043804755944932}`.
Demo weights: `results/robomimic_can_mg_official_bc_rnn_gap_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_can_mg_official_bc_rnn_gap_seed0_setup/config.json
```
