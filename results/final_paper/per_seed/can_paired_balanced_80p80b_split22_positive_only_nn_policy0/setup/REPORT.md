# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/can_paired_balanced_80p80b_split22_positive_only_nn_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_balanced_80p80b_s22_positive_plus_positive_nn_top_unlabeled_demos_top80_seed0_train`.
Validation-positive filter key: `final_can_paired_balanced_80p80b_s22_positive_plus_positive_nn_top_unlabeled_demos_top80_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `90`.
Selected unlabeled demos: `80`.
Selected hidden-positive demos: `76`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 80, 'selected_demo_count': 80, 'selected_hidden_positive_demos': 76, 'selected_hidden_bad_demos': 4, 'selected_hidden_positive_purity': 0.95, 'selected_score_mean': -0.20328632136806846, 'selected_score_min': -0.3393157124519348, 'selected_score_max': -0.06522747129201889}`.
Demo weights: `results/final_paper/per_seed/can_paired_balanced_80p80b_split22_positive_only_nn_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/can_paired_balanced_80p80b_split22_positive_only_nn_policy0/setup/config.json
```
