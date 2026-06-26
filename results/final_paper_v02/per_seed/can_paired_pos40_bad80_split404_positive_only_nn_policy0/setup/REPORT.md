# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s404_positive_plus_positive_nn_top_unlabeled_demos_top40_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s404_positive_plus_positive_nn_top_unlabeled_demos_top40_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden-positive demos: `35`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 40, 'selected_demo_count': 40, 'selected_hidden_positive_demos': 35, 'selected_hidden_bad_demos': 5, 'selected_hidden_positive_purity': 0.875, 'selected_score_mean': -0.20239456407725812, 'selected_score_min': -0.28704774379730225, 'selected_score_max': -0.08415908366441727}`.
Demo weights: `results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/can_paired_pos40_bad80_split404_positive_only_nn_policy0/setup/config.json
```
