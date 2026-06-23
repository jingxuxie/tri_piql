# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_scarce_seed0_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_labeled_positive_seed0_train`.
Validation-positive filter key: `tri_labeled_positive_seed0_valid_positive`.
Source: `labeled_positive`.
Train demos: `10`.
Selected unlabeled demos: `0`.
Selected hidden-positive demos: `0`.
Selection diagnostics: `{}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_scarce_seed0_mlphead_setup/config.json
```
