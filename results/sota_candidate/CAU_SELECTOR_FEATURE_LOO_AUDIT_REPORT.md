# CAU Selector Feature LOO Audit

This development audit tests whether simple hidden-label-free initial support-distance features can select between positive-only and CAU across completed Can CAU splits.
Thresholds are chosen from a coarse quantile grid to test robust signal rather than endpoint-specific threshold mining.

## Decision

- Baselines over the audited splits: positive-only `269/370`, always-CAU `296/370`, and per-episode oracle switch `331/370`.
- Leave-one-split-out safe selector score: `263/370` with `7` gains and `13` losses versus positive-only.
- Leave-one-split-out best-delta selector score: `277/370` with `31` gains and `23` losses versus positive-only.
- The support-distance features do not provide a deployable CAU selector; preserving anchors collapses back to positive-only or fails to improve it.

## Split Baselines

| split | episodes | positive_successes | cau_successes | oracle_switch_successes | cau_delta_vs_positive | oracle_delta_vs_positive |
| --- | --- | --- | --- | --- | --- | --- |
| 101 | 50 | 19 | 33 | 40 | 14 | 21 |
| 202 | 50 | 40 | 42 | 46 | 2 | 6 |
| 303 | 50 | 36 | 40 | 46 | 4 | 10 |
| 404 | 50 | 39 | 35 | 41 | -4 | 2 |
| 505 | 50 | 40 | 43 | 46 | 3 | 6 |
| 606 | 20 | 16 | 15 | 18 | -1 | 2 |
| 707 | 50 | 36 | 50 | 50 | 14 | 14 |
| 808 | 50 | 43 | 38 | 44 | -5 | 1 |

## Leave-One-Split-Out Rows

| selector_mode | heldout_split | gate_label | feature_1 | direction_1 | threshold_1 | feature_2 | direction_2 | threshold_2 | operator | test_routed_successes | test_positive_successes | test_cau_successes | test_gains_vs_positive | test_losses_vs_positive | test_opened_episodes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| safe_zero_loss | pooled_resubstitution | two_feature | initial_anchor_pos_dist_mean | le | 1.788770 | initial_anchor_margin_mean | gt | 0.799296 | and | 285 | 269 | 296 | 16 | 0 | 35 |
| safe_zero_loss | 101 | two_feature | initial_anchor_neg_dist_mean | gt | 1.874664 | initial_anchor_margin_mean | le | -0.082744 | and | 20 | 19 | 33 | 1 | 0 | 10 |
| safe_zero_loss | 202 | two_feature | initial_anchor_neg_dist_mean | gt | 1.488679 | initial_anchor_margin_mean | le | -0.148144 | and | 38 | 40 | 42 | 0 | 2 | 5 |
| safe_zero_loss | 303 | two_feature | initial_anchor_neg_dist_mean | gt | 2.913545 | initial_anchor_margin_mean | gt | 0.764402 | or | 35 | 36 | 40 | 4 | 5 | 15 |
| safe_zero_loss | 404 | two_feature | initial_anchor_pos_dist_mean | le | 1.905613 | initial_anchor_neg_dist_mean | gt | 1.722819 | and | 34 | 39 | 35 | 1 | 6 | 30 |
| safe_zero_loss | 505 | two_feature | initial_anchor_pos_dist_mean | le | 1.835749 | initial_anchor_margin_mean | gt | 0.799296 | and | 41 | 40 | 43 | 1 | 0 | 5 |
| safe_zero_loss | 606 | two_feature | initial_anchor_neg_dist_mean | gt | 1.789299 | initial_anchor_margin_mean | le | -0.089249 | and | 16 | 16 | 15 | 0 | 0 | 2 |
| safe_zero_loss | 707 | two_feature | initial_anchor_pos_dist_mean | le | 1.349273 | initial_anchor_margin_mean | gt | 0.802912 | and | 36 | 36 | 50 | 0 | 0 | 0 |
| safe_zero_loss | 808 | two_feature | initial_anchor_pos_dist_mean | le | 1.940199 | initial_anchor_margin_mean | gt | 0.655060 | and | 43 | 43 | 38 | 0 | 0 | 0 |
| best_delta | pooled_resubstitution | one_feature | initial_anchor_neg_dist_mean | gt | 1.421888 |  |  |  |  | 303 | 269 | 296 | 60 | 26 | 291 |
| best_delta | 101 | two_feature | initial_anchor_pos_dist_mean | gt | 2.206263 | initial_anchor_neg_dist_mean | le | 2.210326 | or | 23 | 19 | 33 | 11 | 7 | 40 |
| best_delta | 202 | two_feature | initial_anchor_pos_dist_mean | gt | 2.117641 | initial_anchor_margin_mean | gt | 0.303079 | or | 44 | 40 | 42 | 4 | 0 | 25 |
| best_delta | 303 | one_feature | initial_anchor_neg_dist_mean | gt | 1.421888 |  |  |  |  | 40 | 36 | 40 | 9 | 5 | 40 |
| best_delta | 404 | two_feature | initial_anchor_pos_dist_mean | gt | 2.114375 | initial_anchor_margin_mean | gt | 0.256112 | or | 35 | 39 | 35 | 2 | 6 | 45 |
| best_delta | 505 | two_feature | initial_anchor_pos_dist_mean | gt | 2.114375 | initial_anchor_margin_mean | gt | 0.799296 | or | 42 | 40 | 43 | 2 | 0 | 20 |
| best_delta | 606 | two_feature | initial_anchor_pos_dist_mean | gt | 2.114375 | initial_anchor_margin_mean | gt | 0.627487 | or | 17 | 16 | 15 | 1 | 0 | 10 |
| best_delta | 707 | two_feature | initial_anchor_pos_dist_mean | le | 1.905613 | initial_anchor_neg_dist_mean | gt | 1.406656 | and | 37 | 36 | 50 | 1 | 0 | 5 |
| best_delta | 808 | two_feature | initial_anchor_pos_dist_mean | gt | 2.153548 | initial_anchor_margin_mean | gt | 0.206206 | or | 39 | 43 | 38 | 1 | 5 | 40 |

## Artifacts

- Selector CSV: `results/sota_candidate/cau_selector_feature_loo_rows.csv`.
- Split baseline CSV: `results/sota_candidate/cau_selector_feature_split_baselines.csv`.
