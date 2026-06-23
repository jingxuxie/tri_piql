# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top240_seed2_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_posonly_nn_top240_positive_plus_positive_nn_top_unlabeled_demos_top240_seed2_train`.
Validation-positive filter key: `tri_lift_mg_posonly_nn_top240_positive_plus_positive_nn_top_unlabeled_demos_top240_seed2_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `250`.
Selected unlabeled demos: `240`.
Selected hidden-positive demos: `143`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 240, 'selected_demo_count': 240, 'selected_hidden_positive_demos': 143, 'selected_hidden_bad_demos': 97, 'selected_hidden_positive_purity': 0.5958333333333333, 'selected_score_mean': -0.2422002732908974, 'selected_score_min': -0.3481019139289856, 'selected_score_max': -0.05556052550673485}`.
Demo weights: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top240_seed2_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top240_seed2_setup/config.json
```
