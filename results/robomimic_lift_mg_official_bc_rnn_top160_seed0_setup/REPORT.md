# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_top160_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_positive_plus_classifier_top_unlabeled_demos_top160_seed0_train`.
Validation-positive filter key: `tri_lift_mg_positive_plus_classifier_top_unlabeled_demos_top160_seed0_valid_positive`.
Source: `positive_plus_classifier_top_unlabeled_demos`.
Train demos: `170`.
Selected unlabeled demos: `160`.
Selected hidden-positive demos: `154`.
Selection diagnostics: `{'selection_rule': 'fixed_top', 'requested_demos': 160, 'selected_demo_count': 160, 'selected_hidden_positive_demos': 154, 'selected_hidden_bad_demos': 6, 'selected_hidden_positive_purity': 0.9625}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_top160_seed0_setup/config.json
```
