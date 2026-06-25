# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_positive_only_nn_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos20_bad80_s22_positive_plus_positive_nn_top_unlabeled_demos_top20_seed0_train`.
Validation-positive filter key: `final_can_paired_pos20_bad80_s22_positive_plus_positive_nn_top_unlabeled_demos_top20_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `30`.
Selected unlabeled demos: `20`.
Selected hidden-positive demos: `17`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 20, 'selected_demo_count': 20, 'selected_hidden_positive_demos': 17, 'selected_hidden_bad_demos': 3, 'selected_hidden_positive_purity': 0.85, 'selected_score_mean': -0.21902682147920133, 'selected_score_min': -0.3224070966243744, 'selected_score_max': -0.11109568923711777}`.
Demo weights: `results/final_paper/per_seed/can_paired_pos20_bad80_split22_positive_only_nn_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/can_paired_pos20_bad80_split22_positive_only_nn_policy0/setup/config.json
```
