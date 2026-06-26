# Official Robomimic BC-RNN Setup

Config: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split606_triage_bc_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s606_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s606_positive_plus_classifier_demo_threshold_unlabeled_demos_pos_min_seed0_valid_positive`.
Source: `positive_plus_classifier_demo_threshold_unlabeled_demos`.
Train demos: `186`.
Selected unlabeled demos: `176`.
Selected hidden-positive demos: `144`.
Selection diagnostics: `{'selection_rule': 'demo_threshold', 'demo_threshold_rule': 'pos_min', 'demo_threshold': 0.8928115963935852, 'labeled_positive_demo_count': 10, 'labeled_negative_demo_count': 10, 'labeled_positive_score_min': 0.8928115963935852, 'labeled_positive_score_p10': 0.9173221588134766, 'labeled_positive_score_mean': 0.963483190536499, 'labeled_negative_score_max': 0.14429707825183868, 'labeled_negative_score_mean': 0.035855061700567604, 'selected_score_mean': 0.9625752656297251, 'selected_score_min': 0.8944297432899475, 'selected_score_max': 0.9973039031028748, 'selected_demo_count': 176, 'selected_hidden_positive_demos': 144, 'selected_hidden_bad_demos': 32, 'selected_hidden_positive_purity': 0.8181818181818182}`.
Demo weights: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split606_triage_bc_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split606_triage_bc_policy0/setup/config.json
```
