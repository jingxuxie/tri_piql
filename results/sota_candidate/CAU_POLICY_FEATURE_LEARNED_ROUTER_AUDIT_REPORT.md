# CAU Policy-Feature Learned Router Audit

This no-rollout diagnostic fits standardized ridge scores from first-state policy features to CAU-vs-positive endpoint deltas.
Thresholds are selected on training splits only. The audit tests leave-one-split-out transfer across completed splits and a frozen train-on-completed evaluation on fresh split909.

## Decision

- LOO safe learned router: `277/370` with `25` gains and `17` losses versus positive-only.
- LOO best-delta learned router: `278/370` with `26` gains and `17` losses versus positive-only.
- Fresh split909 safe learned router: `9/20` versus positive-only `15/20` and CAU `9/20`, opening `20` CAU starts.
- Fresh split909 best-delta learned router: `9/20` versus positive-only `15/20` and CAU `9/20`, opening `20` CAU starts.
- Fresh split909 deterministic first-state oracle is only `16/20` over `10` repeated initial states; the per-episode oracle is `16/20`.
- A same-screen threshold upper bound can reach `16/20` with `1` gains and `0` losses using `positive_support_pos_dist gt 2.444725`; this is post-hoc and only shows that one recoverable start exists. The same-screen best-delta upper bound reaches `16/20` with `1` gains and `0` losses.
- Treat this as a diagnostic only unless both LOO and fresh transfer improve the positive-only anchor with controlled losses.

## Rows

| selector_mode | heldout_split | feature_group | target | alpha | threshold | test_routed_successes | test_positive_successes | test_cau_successes | test_gains_vs_positive | test_losses_vs_positive | test_opened_episodes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| safe_zero_loss | 101 | all_policy_features | delta | 0.1 | 0.081157 | 29 | 19 | 33 | 17 | 7 | 40 |
| safe_zero_loss | 202 | policy_only | loss_averse | 0.01 | 0.090886 | 42 | 40 | 42 | 6 | 4 | 50 |
| safe_zero_loss | 303 | all_policy_features | loss_averse | 0.01 | 0.052438 | 36 | 36 | 40 | 0 | 0 | 0 |
| safe_zero_loss | 404 | policy_only | loss_averse | 10.0 | 0.023282 | 35 | 39 | 35 | 2 | 6 | 35 |
| safe_zero_loss | 505 | policy_only | loss_averse | 100.0 | 0.062645 | 40 | 40 | 43 | 0 | 0 | 0 |
| safe_zero_loss | 606 | policy_only | loss_averse | 1.0 | 0.060361 | 16 | 16 | 15 | 0 | 0 | 0 |
| safe_zero_loss | 707 | all_policy_features | delta | 100.0 | 0.162091 | 36 | 36 | 50 | 0 | 0 | 0 |
| safe_zero_loss | 808 | policy_only | loss_averse | 1.0 | 0.018421 | 43 | 43 | 38 | 0 | 0 | 0 |
| safe_zero_loss | fresh909 | policy_only | loss_averse | 10.0 | 0.008421 | 9 | 15 | 9 | 1 | 7 | 20 |
| best_delta | 101 | all_policy_features | delta | 0.1 | 0.081157 | 29 | 19 | 33 | 17 | 7 | 40 |
| best_delta | 202 | policy_only | loss_averse | 1.0 | -0.009963 | 42 | 40 | 42 | 6 | 4 | 50 |
| best_delta | 303 | all_policy_features | loss_averse | 10.0 | -0.168674 | 36 | 36 | 40 | 0 | 0 | 0 |
| best_delta | 404 | policy_only | delta | 0.01 | 0.064325 | 35 | 39 | 35 | 2 | 6 | 50 |
| best_delta | 505 | all_policy_features | delta | 0.01 | 0.153843 | 40 | 40 | 43 | 0 | 0 | 0 |
| best_delta | 606 | policy_only | delta | 0.1 | 0.092636 | 17 | 16 | 15 | 1 | 0 | 2 |
| best_delta | 707 | all_policy_features | delta | 0.01 | 0.002005 | 36 | 36 | 50 | 0 | 0 | 0 |
| best_delta | 808 | all_policy_features | loss_averse | 0.01 | -0.081239 | 43 | 43 | 38 | 0 | 0 | 0 |
| best_delta | fresh909 | policy_only | delta | 0.1 | 0.073700 | 9 | 15 | 9 | 1 | 7 | 20 |

## Artifacts

- Summary CSV: `/home/eston/tri-piql/results/sota_candidate/cau_policy_feature_learned_router_summary.csv`.
- Fresh split909 feature rows: `/home/eston/tri-piql/results/sota_candidate/cau_policy_feature_fresh909_rows.csv`.
- Development feature rows: `/home/eston/tri-piql/results/sota_candidate/cau_policy_feature_rows.csv`.
