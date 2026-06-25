# Official Robomimic BC-RNN Setup

Config: `results/final_paper/per_seed/can_paired_pos40_bad80_split22_bc_all_mixed_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `final_can_paired_pos40_bad80_s22_all_train_demos_seed0_train`.
Validation-positive filter key: `final_can_paired_pos40_bad80_s22_all_train_demos_seed0_valid_positive`.
Source: `all_train_demos`.
Train demos: `180`.
Selected unlabeled demos: `0`.
Selected hidden-positive demos: `0`.
Selection diagnostics: `{}`.
Demo weights: `results/final_paper/per_seed/can_paired_pos40_bad80_split22_bc_all_mixed_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper/per_seed/can_paired_pos40_bad80_split22_bc_all_mixed_policy0/setup/config.json
```
