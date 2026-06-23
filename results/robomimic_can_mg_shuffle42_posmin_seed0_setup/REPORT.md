# Official Robomimic BC-RNN Setup

Config: `results/robomimic_can_mg_shuffle42_posmin_seed0_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `tri_can_mg_shuffle42_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `tri_can_mg_shuffle42_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `659`.
Selected unlabeled demos: `649`.
Selected hidden-positive demos: `414`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8729662895202637, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8729662895202637, 'labeled_positive_score_p10': 0.9469458520412445, 'labeled_positive_score_mean': 0.9582354664802551, 'labeled_negative_score_max': 0.11485430598258972, 'labeled_negative_score_mean': 0.04698629630729556, 'selected_score_mean': 0.9413320383599433, 'selected_score_min': 0.8736979365348816, 'selected_score_max': 0.992424726486206, 'selected_demo_count': 649, 'selected_hidden_positive_demos': 414, 'selected_hidden_bad_demos': 235, 'selected_hidden_positive_purity': 0.637904468412943}`.
Demo weights: `results/robomimic_can_mg_shuffle42_posmin_seed0_setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_can_mg_shuffle42_posmin_seed0_setup/config.json
```
