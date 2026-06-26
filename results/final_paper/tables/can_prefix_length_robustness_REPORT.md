# Can Prefix-Length Robustness Support Sweep

This is the B5 support-only robustness check for the generated Can prefix-positive probe.
It varies the labeled-positive prefix length while holding split seeds, label budget, and the top80 support size fixed.
No new policy endpoint is trained here; the endpoint-backed default-prefix row remains the main generated prefix-positive result.

## Key Rows

| config_id | candidate_id | hidden_positive_selected | hidden_bad_selected | hidden_positive_recall | hidden_bad_admission | support_purity | delta_recall_vs_prefix_state_action_nn_top80 | delta_bad_admission_vs_prefix_state_action_nn_top80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short_prefix | prefix_state_action_nn_top80 | 61 | 179 | 0.254 | 0.746 | 0.254 | 0.000 | 0.000 |
| short_prefix | prefix_bad_aware_state_action_top80 | 158 | 82 | 0.658 | 0.342 | 0.658 | 0.404 | -0.404 |
| short_prefix | prefix_bad_aware_state_top80 | 157 | 83 | 0.654 | 0.346 | 0.654 | 0.400 | -0.400 |
| short_prefix | prefix_rank_fusion_badaware_heavy_top80 | 132 | 108 | 0.550 | 0.450 | 0.550 | 0.296 | -0.296 |
| short_prefix | all_unlabeled_soft_reference | 240 | 240 | 1.000 | 1.000 | 0.500 | 0.746 | 0.254 |
| default_prefix | prefix_state_action_nn_top80 | 37 | 203 | 0.154 | 0.846 | 0.154 | 0.000 | 0.000 |
| default_prefix | prefix_bad_aware_state_action_top80 | 193 | 47 | 0.804 | 0.196 | 0.804 | 0.650 | -0.650 |
| default_prefix | prefix_bad_aware_state_top80 | 195 | 45 | 0.812 | 0.188 | 0.812 | 0.658 | -0.658 |
| default_prefix | prefix_rank_fusion_badaware_heavy_top80 | 151 | 89 | 0.629 | 0.371 | 0.629 | 0.475 | -0.475 |
| default_prefix | all_unlabeled_soft_reference | 240 | 240 | 1.000 | 1.000 | 0.500 | 0.846 | 0.154 |
| long_prefix | prefix_state_action_nn_top80 | 22 | 218 | 0.092 | 0.908 | 0.092 | 0.000 | 0.000 |
| long_prefix | prefix_bad_aware_state_action_top80 | 198 | 42 | 0.825 | 0.175 | 0.825 | 0.733 | -0.733 |
| long_prefix | prefix_bad_aware_state_top80 | 199 | 41 | 0.829 | 0.171 | 0.829 | 0.737 | -0.737 |
| long_prefix | prefix_rank_fusion_badaware_heavy_top80 | 154 | 86 | 0.642 | 0.358 | 0.642 | 0.550 | -0.550 |
| long_prefix | all_unlabeled_soft_reference | 240 | 240 | 1.000 | 1.000 | 0.500 | 0.908 | 0.092 |

## Read

- `short_prefix`: bad-aware state top80 selects `157` hidden positives and `83` hidden bad demos, versus prefix positive-NN top80 `61` and `179`. The recall delta is `0.400` and the bad-admission delta is `-0.400`.
- `default_prefix`: bad-aware state top80 selects `195` hidden positives and `45` hidden bad demos, versus prefix positive-NN top80 `37` and `203`. The recall delta is `0.658` and the bad-admission delta is `-0.658`.
- `long_prefix`: bad-aware state top80 selects `199` hidden positives and `41` hidden bad demos, versus prefix positive-NN top80 `22` and `218`. The recall delta is `0.737` and the bad-admission delta is `-0.737`.

## Answer

The prefix-positive generated probe is not a one-point artifact of the default prefix length. Across short, default, and long prefix settings, the bad-aware state top80 row clears the matched prefix positive-NN top80 support row by increasing hidden-positive recall and decreasing hidden-bad admission at the same selected support size.

This is support-only robustness. It justifies the generated-probe mechanism story, but it should not be promoted as a new endpoint result unless one of the non-default settings is trained and evaluated.

## Outputs

- `results/final_paper/tables/can_prefix_length_robustness.csv`
- `results/final_paper/tables/can_prefix_length_robustness_all_candidates.csv`
- `results/final_paper/tables/can_prefix_length_robustness_REPORT.md`
- generated split files under `results/final_paper/ablations/can_prefix_length_robustness_splits`
