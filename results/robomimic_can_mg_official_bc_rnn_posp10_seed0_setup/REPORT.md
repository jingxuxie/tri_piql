# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_official_bc_rnn_posp10_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed0_train`.
Validation-positive filter key: `tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `724`.
Selected unlabeled demos: `714`.
Selected hidden-positive demos: `378`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_p10', 'demo_threshold': 0.9452162265777588, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8744948506355286, 'labeled_positive_score_p10': 0.9452162265777588, 'labeled_positive_score_mean': 0.9661575794219971, 'labeled_negative_score_max': 0.06898250430822372, 'labeled_negative_score_mean': 0.030370819049130658, 'selected_score_mean': 0.9800791815549386, 'selected_score_min': 0.9452356100082397, 'selected_score_max': 0.9992043972015381, 'selected_demo_count': 714, 'selected_hidden_positive_demos': 378, 'selected_hidden_bad_demos': 336, 'selected_hidden_positive_purity': 0.5294117647058824}`.
Demo weights: `results/robomimic_can_mg_official_bc_rnn_posp10_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_can_mg_official_bc_rnn_posp10_seed0_setup/config.json
```
