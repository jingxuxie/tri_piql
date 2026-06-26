# Failure-Mode Initial-State Audit

This artifact compares positive-only NN, weighted BC, the v0.2 hard union, and all-demo BC on three representative paired Can 40p/80b initial states.
It reuses existing 50-episode endpoint evaluations; each selected initial state has five repeated rollouts per method.

No videos or direct object-state labels are parsed here. The grasp and loop/miss columns are metric proxies: success is used as the only grasp proxy, and horizon-length failures are treated as timeout/miss/loop proxies.

## Selected Cases

| case_id | case_title | split_seed | initial_demo_id | selection_score | positive_only_success_count | weighted_bc_success_count | union_success_count | all_demo_success_count | case_read |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| union_rescue | Hard-union rescue | 33 | demo_105 | 0.800 | 0/5 | 1/5 | 5/5 | 0/5 | Union succeeds where positive-only, weighted, and all-demo mostly timeout; illustrates the coverage gain from adding risk-derived support. |
| positive_anchor_regression | Positive-anchor regression | 11 | demo_39 | 1.000 | 5/5 | 0/5 | 0/5 | 5/5 | Positive-only succeeds while the union and weighted rows timeout; this is the split-specific regression that keeps the union claim non-uniform. |
| soft_pool_rescue | Soft-pool rescue | 33 | demo_99 | 0.800 | 0/5 | 5/5 | 1/5 | 3/5 | Weighted BC succeeds where hard support struggles; broad weighted coverage remains a first-class branch rather than a disposable baseline. |

## Per-Method Rows

| case_id | method_label | success_count | eval_episodes | avg_trajectory_length | loop_or_miss_proxy | bad_demo_resemblance_proxy |
| --- | --- | --- | --- | --- | --- | --- |
| union_rescue | positive-only NN top40 | 0 | 5 | 400.0 | timeout_or_miss_all_failures | support_gap_or_controller_failure_not_bad-demo-attributed |
| union_rescue | weighted BC full pool | 1 | 5 | 343.6 | timeout_or_miss_all_failures | contamination_compatible_timeout_not_verified |
| union_rescue | positive-NN/risk union top40 | 5 | 5 | 118.8 | no_failure_observed | not_applicable_successful |
| union_rescue | all-demo BC full pool | 0 | 5 | 400.0 | timeout_or_miss_all_failures | contamination_compatible_timeout_not_verified |
| positive_anchor_regression | positive-only NN top40 | 5 | 5 | 125.2 | no_failure_observed | not_applicable_successful |
| positive_anchor_regression | weighted BC full pool | 0 | 5 | 400.0 | timeout_or_miss_all_failures | contamination_compatible_timeout_not_verified |
| positive_anchor_regression | positive-NN/risk union top40 | 0 | 5 | 400.0 | timeout_or_miss_all_failures | support_gap_or_controller_failure_not_bad-demo-attributed |
| positive_anchor_regression | all-demo BC full pool | 5 | 5 | 132.8 | no_failure_observed | not_applicable_successful |
| soft_pool_rescue | positive-only NN top40 | 0 | 5 | 400.0 | timeout_or_miss_all_failures | support_gap_or_controller_failure_not_bad-demo-attributed |
| soft_pool_rescue | weighted BC full pool | 5 | 5 | 123.8 | no_failure_observed | not_applicable_successful |
| soft_pool_rescue | positive-NN/risk union top40 | 1 | 5 | 344.2 | timeout_or_miss_all_failures | support_gap_or_controller_failure_not_bad-demo-attributed |
| soft_pool_rescue | all-demo BC full pool | 3 | 5 | 231.0 | timeout_or_miss_all_failures | contamination_compatible_timeout_not_verified |

## Read

- Union rescue: split `33`, `demo_105` has union `5/5` at average length `118.8`, while positive-only is `0/5`, weighted BC is `1/5`, and all-demo BC is `0/5`.
- Positive-anchor regression: split `11`, `demo_39` has positive-only `5/5` but union `0/5` and weighted BC `0/5`.
- Soft-pool rescue: split `33`, `demo_99` has weighted BC `5/5` while positive-only is `0/5` and union is `1/5`.
- The table supports the current paper framing: the hard union gives a real Can rescue pattern, but weighted coverage and positive-only support remain essential comparator branches.

## Outputs

- `results/final_paper/tables/failure_mode_initial_states.csv`
- `results/final_paper/tables/failure_mode_initial_states_cases.csv`
- `results/final_paper/tables/failure_mode_initial_states_REPORT.md`
