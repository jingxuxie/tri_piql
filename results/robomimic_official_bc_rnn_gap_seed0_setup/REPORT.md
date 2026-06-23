# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed0_train`.
Validation-positive filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed0_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `69`.
Selected unlabeled demos: `59`.
Selected hidden-positive demos: `59`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.021726667881011963, 'selected_score_mean': 0.7492691702761892, 'selected_score_min': 0.6465744376182556, 'selected_score_max': 0.8745578527450562, 'selected_demo_count': 59, 'selected_hidden_positive_demos': 59, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_seed0_setup/config.json
```
