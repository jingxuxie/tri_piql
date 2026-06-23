# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top80_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_posonly_nn_top80_positive_plus_positive_nn_top_unlabeled_demos_top80_seed0_train`.
Validation-positive filter key: `tri_lift_mg_posonly_nn_top80_positive_plus_positive_nn_top_unlabeled_demos_top80_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `90`.
Selected unlabeled demos: `80`.
Selected hidden-positive demos: `78`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 80, 'selected_demo_count': 80, 'selected_hidden_positive_demos': 78, 'selected_hidden_bad_demos': 2, 'selected_hidden_positive_purity': 0.975, 'selected_score_mean': -0.13422661651857198, 'selected_score_min': -0.19780050218105316, 'selected_score_max': -0.05556052550673485}`.
Demo weights: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top80_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top80_seed0_setup/config.json
```
