# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_alltrain_seed1_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_all_train_demos_seed1_train`.
Validation-positive filter key: `tri_lift_mg_all_train_demos_seed1_valid_positive`.
Source: `all_train_demos`.
Train demos: `1440`.
Selected unlabeled demos: `0`.
Selected hidden-positive demos: `0`.
Selection diagnostics: `{}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_alltrain_seed1_setup/config.json
```
