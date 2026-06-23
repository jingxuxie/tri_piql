# Official Robomimic BC-RNN Setup

Config: `results/robomimic_square_quality_mixed_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/square/mh/low_dim_v15.hdf5`.
Train filter key: `tri_square_quality_all_train_demos_seed0_train`.
Validation-positive filter key: `tri_square_quality_all_train_demos_seed0_valid_positive`.
Source: `all_train_demos`.
Train demos: `180`.
Selected unlabeled demos: `0`.
Selected hidden-positive demos: `0`.
Selection diagnostics: `{}`.
Demo weights: `results/robomimic_square_quality_mixed_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_square_quality_mixed_seed0_setup/config.json
```
