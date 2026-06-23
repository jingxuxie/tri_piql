# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top320_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_posonly_nn_top320_positive_plus_positive_nn_top_unlabeled_demos_top320_seed0_train`.
Validation-positive filter key: `tri_lift_mg_posonly_nn_top320_positive_plus_positive_nn_top_unlabeled_demos_top320_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `330`.
Selected unlabeled demos: `320`.
Selected hidden-positive demos: `164`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 320, 'selected_demo_count': 320, 'selected_hidden_positive_demos': 164, 'selected_hidden_bad_demos': 156, 'selected_hidden_positive_purity': 0.5125, 'selected_score_mean': -0.2727841471438296, 'selected_score_min': -0.38223668932914734, 'selected_score_max': -0.05556052550673485}`.
Demo weights: `results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top320_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_posonly_nn_top320_seed0_setup/config.json
```
