# Official Robomimic BC-RNN Setup

Config: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_all_train_positive_oracle_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s505_all_train_positive_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s505_all_train_positive_seed0_valid_positive`.
Source: `all_train_positive`.
Train demos: `286`.
Selected unlabeled demos: `0`.
Selected hidden-positive demos: `0`.
Selection diagnostics: `{}`.
Demo weights: `results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_all_train_positive_oracle_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/final_paper_v02/per_seed/lift_mg_mg_sparse_split505_all_train_positive_oracle_policy0/setup/config.json
```
