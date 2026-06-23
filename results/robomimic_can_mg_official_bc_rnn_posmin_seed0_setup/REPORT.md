# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_official_bc_rnn_posmin_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `1049`.
Selected unlabeled demos: `1039`.
Selected hidden-positive demos: `485`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8744948506355286, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8744948506355286, 'labeled_positive_score_p10': 0.9452162265777588, 'labeled_positive_score_mean': 0.9661575794219971, 'labeled_negative_score_max': 0.06898250430822372, 'labeled_negative_score_mean': 0.030370819049130658, 'selected_score_mean': 0.9594885810736399, 'selected_score_min': 0.8746287822723389, 'selected_score_max': 0.9992043972015381, 'selected_demo_count': 1039, 'selected_hidden_positive_demos': 485, 'selected_hidden_bad_demos': 554, 'selected_hidden_positive_purity': 0.4667949951876805}`.
Demo weights: `results/robomimic_can_mg_official_bc_rnn_posmin_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_can_mg_official_bc_rnn_posmin_seed0_setup/config.json
```
