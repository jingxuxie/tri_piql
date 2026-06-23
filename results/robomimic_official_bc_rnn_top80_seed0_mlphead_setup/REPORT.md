# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_top80_seed0_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_positive_plus_classifier_top_unlabeled_demos_seed0_train`.
Validation-positive filter key: `tri_positive_plus_classifier_top_unlabeled_demos_seed0_valid_positive`.
Source: `positive_plus_classifier_top_unlabeled_demos`.
Train demos: `90`.
Selected unlabeled demos: `80`.
Selected hidden-positive demos: `72`.
Selection diagnostics: `{'selection_rule': 'fixed_top', 'requested_demos': 80, 'selected_demo_count': 80, 'selected_hidden_positive_demos': 72, 'selected_hidden_bad_demos': 8, 'selected_hidden_positive_purity': 0.9}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_top80_seed0_mlphead_setup/config.json
```
