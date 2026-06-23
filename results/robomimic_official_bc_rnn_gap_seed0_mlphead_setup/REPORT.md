# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_seed0_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed0_train`.
Validation-positive filter key: `tri_positive_plus_classifier_gap_unlabeled_demos_seed0_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `43`.
Selected unlabeled demos: `33`.
Selected hidden-positive demos: `33`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'score_gap': 0.024093031883239746, 'selected_score_mean': 0.8117915698976228, 'selected_score_min': 0.7474926710128784, 'selected_score_max': 0.9103220701217651, 'selected_demo_count': 33, 'selected_hidden_positive_demos': 33, 'selected_hidden_bad_demos': 0, 'selected_hidden_positive_purity': 1.0}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_seed0_mlphead_setup/config.json
```
