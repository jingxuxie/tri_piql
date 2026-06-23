# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_official_bc_rnn_posp10_seed2_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed2_train`.
Validation-positive filter key: `tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed2_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `836`.
Selected unlabeled demos: `826`.
Selected hidden-positive demos: `446`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_p10', 'demo_threshold': 0.8912435054779053, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.7727122902870178, 'labeled_positive_score_p10': 0.8912435054779053, 'labeled_positive_score_mean': 0.940526157617569, 'labeled_negative_score_max': 0.13116246461868286, 'labeled_negative_score_mean': 0.054361495736520736, 'selected_score_mean': 0.9552426257375943, 'selected_score_min': 0.8914711475372314, 'selected_score_max': 0.9978895783424377, 'selected_demo_count': 826, 'selected_hidden_positive_demos': 446, 'selected_hidden_bad_demos': 380, 'selected_hidden_positive_purity': 0.5399515738498789}`.
Demo weights: `results/robomimic_can_mg_official_bc_rnn_posp10_seed2_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_can_mg_official_bc_rnn_posp10_seed2_setup/config.json
```
