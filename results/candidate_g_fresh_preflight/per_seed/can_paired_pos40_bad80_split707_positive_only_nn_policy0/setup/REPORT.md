# Official Robomimic BC-RNN Setup

Config: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_positive_only_nn_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s707_positive_plus_positive_nn_top_unlabeled_demos_top40_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s707_positive_plus_positive_nn_top_unlabeled_demos_top40_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `50`.
Selected unlabeled demos: `40`.
Selected hidden-positive demos: `32`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 40, 'selected_demo_count': 40, 'selected_hidden_positive_demos': 32, 'selected_hidden_bad_demos': 8, 'selected_hidden_positive_purity': 0.8, 'selected_score_mean': -0.21234777923673392, 'selected_score_min': -0.29165560007095337, 'selected_score_max': -0.10881243646144867}`.
Demo weights: `results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_positive_only_nn_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_g_fresh_preflight/per_seed/can_paired_pos40_bad80_split707_positive_only_nn_policy0/setup/config.json
```
