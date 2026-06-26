# Official Robomimic BC-RNN Setup

Config: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split606_positive_only_nn_policy0/setup/config.json`.
Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.
Train filter key: `final_lift_mg_mg_sparse_s606_positive_plus_positive_nn_top_unlabeled_demos_top160_seed0_train`.
Validation-positive filter key: `final_lift_mg_mg_sparse_s606_positive_plus_positive_nn_top_unlabeled_demos_top160_seed0_valid_positive`.
Source: `positive_plus_positive_nn_top_unlabeled_demos`.
Train demos: `170`.
Selected unlabeled demos: `160`.
Selected hidden-positive demos: `141`.
Selection diagnostics: `{'selection_rule': 'positive_nn_top', 'requested_demos': 160, 'selected_demo_count': 160, 'selected_hidden_positive_demos': 141, 'selected_hidden_bad_demos': 19, 'selected_hidden_positive_purity': 0.88125, 'selected_score_mean': -0.19522711131721734, 'selected_score_min': -0.3309280276298523, 'selected_score_max': -0.04407736286520958}`.
Demo weights: `results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split606_positive_only_nn_policy0/setup/demo_weights.json`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/candidate_g_fresh_preflight/per_seed/lift_mg_mg_sparse_split606_positive_only_nn_policy0/setup/config.json
```
