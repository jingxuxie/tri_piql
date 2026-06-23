# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_top20_pos40_bad80_seed1_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_pos40_bad80_positive_plus_classifier_top_unlabeled_demos_top20_seed1_train`.
Validation-positive filter key: `tri_pos40_bad80_positive_plus_classifier_top_unlabeled_demos_top20_seed1_valid_positive`.
Source: `positive_plus_classifier_top_unlabeled_demos`.
Train demos: `30`.
Selected unlabeled demos: `20`.
Selected hidden-positive demos: `20`.
Selection diagnostics: `{'selection_rule': 'fixed_top', 'requested_demos': 20, 'selected_demo_count': 20, 'selected_hidden_positive_demos': 20, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_top20_pos40_bad80_seed1_mlphead_setup/config.json
```
