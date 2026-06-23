# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_seed0_tiny_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed0_train`.
Validation-positive filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed0_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `25`.
Selected unlabeled demos: `15`.
Selected hidden-positive demos: `10`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 20, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.00037914514541625977, 'selected_score_mean': 0.5082314809163412, 'selected_score_min': 0.5070261359214783, 'selected_score_max': 0.5113239288330078, 'selected_demo_count': 15, 'selected_hidden_positive_demos': 10, 'selected_hidden_bad_demos': 5, 'selected_hidden_positive_purity': 0.6666666666666666}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_seed0_tiny_setup/config.json
```
