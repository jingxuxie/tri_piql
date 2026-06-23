# Official Robomimic BC-RNN Setup

Config: `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed0_mlphead_setup/config.json`.
Dataset: `data/robomimic/v1.5/can/paired/low_dim_v15.hdf5`.
Train filter key: `tri_stress_p20_b80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_train`.
Validation-positive filter key: `tri_stress_p20_b80_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_valid_positive`.
Source: `positive_plus_classifier_gap_unlabeled_demos`.
Train demos: `58`.
Selected unlabeled demos: `48`.
Selected hidden-positive demos: `20`.
Selection diagnostics: `{'selection_rule': 'score_gap', 'gap_select_max_unlabeled_demos': 80, 'gap_select_min_unlabeled_demos': 4, 'gap_select_min_labeled_positive_multiplier': 4.0, 'gap_select_effective_min_unlabeled_demos': 40, 'labeled_positive_demo_count': 10, 'score_gap': 0.02679196000099182, 'selected_score_mean': 0.5738737713545561, 'selected_score_min': 0.39424049854278564, 'selected_score_max': 0.8730028867721558, 'selected_demo_count': 48, 'selected_hidden_positive_demos': 20, 'selected_hidden_bad_demos': 28, 'selected_hidden_positive_purity': 0.4166666666666667}`.

## Command

```bash
conda run -n tri-piql python -m robomimic.scripts.train --config results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed0_mlphead_setup/config.json
```
