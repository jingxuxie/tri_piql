# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_posonly_nn_top160_positive_plus_positive_nn_top_unlabeled_demos_top160_seed0_train`.
Validation-positive filter key: `tri_lift_mg_posonly_nn_top160_positive_plus_positive_nn_top_unlabeled_demos_top160_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `170`.
Selected unlabeled demos: `160`.
Selected hidden-positive demos: `126`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 160, 'selected_demo_count': 160, 'selected_hidden_positive_demos': 126, 'selected_hidden_bad_demos': 34, 'selected_hidden_positive_purity': 0.7875, 'selected_score_mean': -0.19752838818822055, 'selected_score_min': -0.3093196153640747, 'selected_score_max': -0.05556052550673485}`.
Demo weights: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top160_seed0_setup/config.json
```
