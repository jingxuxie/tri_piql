# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed1_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed1_train`.
Validation-positive filter key: `tri_lift_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed1_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `254`.
Selected unlabeled demos: `244`.
Selected hidden-positive demos: `206`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.6600571274757385, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.6600571274757385, 'labeled_positive_score_p10': 0.8898032426834106, 'labeled_positive_score_mean': 0.9295315384864807, 'labeled_negative_score_max': 0.3265579342842102, 'labeled_negative_score_mean': 0.07370750773698091, 'selected_score_mean': 0.8726215516446066, 'selected_score_min': 0.6659716963768005, 'selected_score_max': 0.9947450757026672, 'selected_demo_count': 244, 'selected_hidden_positive_demos': 206, 'selected_hidden_bad_demos': 38, 'selected_hidden_positive_purity': 0.8442622950819673}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_posmin_seed1_setup/config.json
```
