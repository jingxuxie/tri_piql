# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_min40_seed1_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed1_train`.
Validation-positive filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed1_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `55`.
Selected unlabeled demos: `45`.
Selected hidden-positive demos: `45`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 40, 'score_gap': 0.02066558599472046, 'selected_score_mean': 0.7971914635764228, 'selected_score_min': 0.6903260350227356, 'selected_score_max': 0.9403827786445618, 'selected_demo_count': 45, 'selected_hidden_positive_demos': 45, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_min40_seed1_mlphead_setup/config.json
```
