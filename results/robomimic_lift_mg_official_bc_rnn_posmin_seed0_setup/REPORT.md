# Official Robomimic BC-RNN Setup

Config: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_lift_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `tri_lift_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `240`.
Selected unlabeled demos: `230`.
Selected hidden-positive demos: `203`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.6558923125267029, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.6558923125267029, 'labeled_positive_score_p10': 0.8887903988361359, 'labeled_positive_score_mean': 0.930619740486145, 'labeled_negative_score_max': 0.3178037405014038, 'labeled_negative_score_mean': 0.07066999324597419, 'selected_score_mean': 0.876285668818847, 'selected_score_min': 0.6559332013130188, 'selected_score_max': 0.994234025478363, 'selected_demo_count': 230, 'selected_hidden_positive_demos': 203, 'selected_hidden_bad_demos': 27, 'selected_hidden_positive_purity': 0.8826086956521739}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_lift_mg_official_bc_rnn_posmin_seed0_setup/config.json
```
