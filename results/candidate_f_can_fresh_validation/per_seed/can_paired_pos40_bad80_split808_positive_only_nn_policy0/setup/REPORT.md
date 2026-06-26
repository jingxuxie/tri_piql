# Official Robomimic BC-RNN Setup

Config: `results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_positive_only_nn_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s808_positive_plus_positive_nn_top_unlabeled_demos_top40_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s808_positive_plus_positive_nn_top_unlabeled_demos_top40_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden-positive demos: `37`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 40, 'selected_demo_count': 40, 'selected_hidden_positive_demos': 37, 'selected_hidden_bad_demos': 3, 'selected_hidden_positive_purity': 0.925, 'selected_score_mean': -0.19558237176388502, 'selected_score_min': -0.2615777254104614, 'selected_score_max': -0.11303400993347168}`.
Demo weights: `results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_positive_only_nn_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_f_can_fresh_validation/per_seed/can_paired_pos40_bad80_split808_positive_only_nn_policy0/setup/config.json
```
