# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_official_bc_rnn_alltrain_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_all_train_demos_seed0_train`.
Validation-positive filter key: `tri_can_mg_all_train_demos_seed0_valid_positive`.
Source: `all_train_demos`.
Train demos: `3860`.
Selected unlabeled demos: `0`.
Selected hidden-positive demos: `0`.
Selection diagnostics: `{}`.
Demo weights: `results/robomimic_can_mg_official_bc_rnn_alltrain_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_can_mg_official_bc_rnn_alltrain_seed0_setup/config.json
```
