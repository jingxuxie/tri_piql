# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed2_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top80_seed2_train`.
Validation-positive filter key: `tri_stress_p20_b80_positive_plus_classifier_top_unlabeled_demos_top80_seed2_valid_positive`.
Source: `positive_plus_classifier_top_unlabeled_demos`.
Train demos: `90`.
Selected unlabeled demos: `80`.
Selected hidden-positive demos: `20`.
Selection diagnostics: `{'selection_rule': 'fixed_top', 'requested_demos': 80, 'selected_demo_count': 80, 'selected_hidden_positive_demos': 20, 'selected_hidden_bad_demos': 60, 'selected_hidden_positive_purity': 0.25}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed2_mlphead_setup/config.json
```
