# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_official_bc_rnn_posp10_seed1_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed1_train`.
Validation-positive filter key: `tri_can_mg_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_p10_seed1_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `789`.
Selected unlabeled demos: `779`.
Selected hidden-positive demos: `424`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_p10', 'demo_threshold': 0.8998070299625397, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.7797244787216187, 'labeled_positive_score_p10': 0.8998070299625397, 'labeled_positive_score_mean': 0.9415450096130371, 'labeled_negative_score_max': 0.11986842006444931, 'labeled_negative_score_mean': 0.048582259006798266, 'selected_score_mean': 0.9575279349693132, 'selected_score_min': 0.8999678492546082, 'selected_score_max': 0.9972501397132874, 'selected_demo_count': 779, 'selected_hidden_positive_demos': 424, 'selected_hidden_bad_demos': 355, 'selected_hidden_positive_purity': 0.5442875481386393}`.
Demo weights: `results/robomimic_can_mg_official_bc_rnn_posp10_seed1_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_can_mg_official_bc_rnn_posp10_seed1_setup/config.json
```
