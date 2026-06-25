# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/can_paired_pos40_bad80_split33_positive_only_nn_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s33_positive_plus_positive_nn_top_unlabeled_demos_top40_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s33_positive_plus_positive_nn_top_unlabeled_demos_top40_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden-positive demos: `33`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 40, 'selected_demo_count': 40, 'selected_hidden_positive_demos': 33, 'selected_hidden_bad_demos': 7, 'selected_hidden_positive_purity': 0.825, 'selected_score_mean': -0.22105792742222546, 'selected_score_min': -0.32978373765945435, 'selected_score_max': -0.08956818282604218}`.
Demo weights: `results/final_paper/per_seed/can_paired_pos40_bad80_split33_positive_only_nn_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/can_paired_pos40_bad80_split33_positive_only_nn_policy0/setup/config.json
```
