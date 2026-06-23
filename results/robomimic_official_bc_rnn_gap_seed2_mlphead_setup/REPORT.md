# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_seed2_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed2_train`.
Validation-positive filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed2_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `19`.
Selected unlabeled demos: `9`.
Selected hidden-positive demos: `9`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.017369985580444336, 'selected_score_mean': 0.8528398076693217, 'selected_score_min': 0.8171380162239075, 'selected_score_max': 0.8913596272468567, 'selected_demo_count': 9, 'selected_hidden_positive_demos': 9, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_seed2_mlphead_setup/config.json
```
