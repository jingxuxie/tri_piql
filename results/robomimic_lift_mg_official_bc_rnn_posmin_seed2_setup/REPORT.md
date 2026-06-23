# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed2_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed2_train`.
Validation-positive filter key: `tri_lift_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed2_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `248`.
Selected unlabeled demos: `238`.
Selected hidden-positive demos: `206`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.6581892967224121, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.6581892967224121, 'labeled_positive_score_p10': 0.8826429843902588, 'labeled_positive_score_mean': 0.9279293060302735, 'labeled_negative_score_max': 0.3259013891220093, 'labeled_negative_score_mean': 0.07144113928079605, 'selected_score_mean': 0.8665521310157135, 'selected_score_min': 0.6612117290496826, 'selected_score_max': 0.9944073557853699, 'selected_demo_count': 238, 'selected_hidden_positive_demos': 206, 'selected_hidden_bad_demos': 32, 'selected_hidden_positive_purity': 0.865546218487395}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_posmin_seed2_setup/config.json
```
