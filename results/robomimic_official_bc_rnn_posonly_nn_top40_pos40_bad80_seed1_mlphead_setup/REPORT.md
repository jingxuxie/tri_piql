# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_seed1_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_pos40_bad80_positive_plus_positive_nn_top_unlabeled_demos_top40_seed1_train`.
Validation-positive filter key: `tri_pos40_bad80_positive_plus_positive_nn_top_unlabeled_demos_top40_seed1_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden-positive demos: `31`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 40, 'selected_demo_count': 40, 'selected_hidden_positive_demos': 31, 'selected_hidden_bad_demos': 9, 'selected_hidden_positive_purity': 0.775, 'selected_score_mean': -0.2168174970895052, 'selected_score_min': -0.3367440700531006, 'selected_score_max': -0.08061140030622482}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_seed1_mlphead_setup/config.json
```
