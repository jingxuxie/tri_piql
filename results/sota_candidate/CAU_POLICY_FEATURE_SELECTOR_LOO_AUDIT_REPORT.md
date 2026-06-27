# CAU Policy-Feature Selector LOO Audit

This development audit tests first-state policy-distribution features for selecting between positive-only and CAU.
Features include GMM confidence, entropy, action disagreement, cross-policy log-probability, and labeled support margins.
Thresholds are selected from a coarse quantile grid using completed splits only, then evaluated leave-one-split-out.

## Decision

- Baselines over the audited splits: positive-only `269/370`, always-CAU `296/370`, and per-episode oracle switch `331/370`.
- Leave-one-split-out safe selector score: `276/370` with `29` gains and `22` losses versus positive-only.
- Leave-one-split-out best-delta selector score: `299/370` with `44` gains and `14` losses versus positive-only.
- Policy features expose some signal, but the useful rules still lose positive-only starts; do not deploy without a stricter anchor-preservation mechanism.

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

| selector_mode | heldout_split | gate_label | feature | direction | threshold | feature_2 | direction_2 | threshold_2 | operator | test_routed_successes | test_positive_successes | test_cau_successes | test_gains_vs_positive | test_losses_vs_positive | test_opened_episodes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| safe_zero_loss | pooled_resubstitution | two_feature | cau_minus_positive_support_margin | le | 0.126906 | positive_support_margin | gt | 0.627420 | and | 293 | 269 | 296 | 24 | 0 | 64 |
| safe_zero_loss | 101 | two_feature | cau_logp_margin_vs_positive | gt | 0.700273 | cau_top_scale_mean | gt | 0.104820 | and | 32 | 19 | 33 | 20 | 7 | 40 |
| safe_zero_loss | 202 | two_feature | cau_minus_positive_support_margin | le | -0.103924 | cau_minus_positive_logit_gap | le | -16.154610 | or | 40 | 40 | 42 | 0 | 0 | 5 |
| safe_zero_loss | 303 | two_feature | cau_logp_margin_vs_positive | gt | 0.667477 | positive_support_margin | gt | 0.303167 | and | 37 | 36 | 40 | 6 | 5 | 20 |
| safe_zero_loss | 404 | two_feature | positive_cau_action_l2 | gt | 0.081332 | positive_support_margin | gt | 0.451646 | and | 34 | 39 | 35 | 1 | 6 | 25 |
| safe_zero_loss | 505 | two_feature | cau_minus_positive_support_margin | le | 0.111773 | positive_support_margin | gt | 0.650140 | and | 41 | 40 | 43 | 1 | 0 | 5 |
| safe_zero_loss | 606 | two_feature | cau_minus_positive_support_margin | le | 0.126906 | positive_support_margin | gt | 0.627420 | and | 16 | 16 | 15 | 0 | 0 | 4 |
| safe_zero_loss | 707 | two_feature | cau_minus_positive_support_margin | le | 0.124516 | positive_support_margin | gt | 0.650140 | and | 37 | 36 | 50 | 1 | 0 | 5 |
| safe_zero_loss | 808 | two_feature | positive_support_margin | gt | 0.206030 | cau_minus_positive_logit_gap | gt | -3.406572 | and | 39 | 43 | 38 | 0 | 4 | 10 |
| best_delta | pooled_resubstitution | two_feature | cau_logp_margin_vs_positive | gt | 0.757865 | cau_support_margin | gt | 0.837440 | or | 310 | 269 | 296 | 57 | 16 | 245 |
| best_delta | 101 | two_feature | cau_logp_margin_vs_positive | gt | 0.700273 | positive_cau_action_l2 | gt | 0.080743 | and | 28 | 19 | 33 | 16 | 7 | 35 |
| best_delta | 202 | two_feature | cau_logp_margin_vs_positive | gt | 0.799573 | cau_support_margin | gt | 0.799229 | or | 44 | 40 | 42 | 4 | 0 | 15 |
| best_delta | 303 | two_feature | cau_logp_margin_vs_positive | gt | 0.667477 | cau_top_scale_mean | le | 0.129451 | and | 40 | 36 | 40 | 10 | 6 | 50 |
| best_delta | 404 | two_feature | cau_logp_margin_vs_positive | gt | 0.678646 | cau_top_scale_mean | le | 0.129451 | and | 39 | 39 | 35 | 0 | 0 | 10 |
| best_delta | 505 | two_feature | cau_logp_margin_vs_positive | gt | 0.667477 | positive_top_prob | gt | 0.999998 | and | 40 | 40 | 43 | 0 | 0 | 0 |
| best_delta | 606 | two_feature | cau_logp_margin_vs_positive | gt | 0.576382 | cau_minus_positive_support_margin | le | 0.126906 | and | 16 | 16 | 15 | 1 | 1 | 10 |
| best_delta | 707 | two_feature | cau_logp_margin_vs_positive | gt | 0.667477 | cau_top_scale_mean | le | 0.128964 | and | 49 | 36 | 50 | 13 | 0 | 45 |
| best_delta | 808 | two_feature | cau_logp_margin_vs_positive | gt | 0.717695 | positive_support_margin | gt | 0.656079 | or | 43 | 43 | 38 | 0 | 0 | 0 |

## Artifacts

- Feature CSV: `/home/eston/tri-piql/results/sota_candidate/cau_policy_feature_rows.csv`.
- Selector CSV: `/home/eston/tri-piql/results/sota_candidate/cau_policy_feature_selector_loo_rows.csv`.
- Split baseline CSV: `/home/eston/tri-piql/results/sota_candidate/cau_policy_feature_split_baselines.csv`.
