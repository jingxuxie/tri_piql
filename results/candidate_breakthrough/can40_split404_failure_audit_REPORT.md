# Candidate-Breakthrough Split-404 Audit

This is a failure-focused preflight audit for `triage_bc_candidate_breakthrough_plan.md`.
It reuses completed fresh Can 40p/80b split-404 endpoint rollouts and does not run a new policy.

## Summary

- Positive-only NN is the split-404 endpoint winner at `39/50`.
- The v0.2 hard union reaches `27/50`, which is `-12` successes below positive-only.
- Weighted BC reaches `33/50` and v0.1 hard support reaches `36/50`.
- The support audit does not explain the reversal by hidden-label counts: union selects `39/40` hidden positives and `5/80` hidden bad demos, versus positive-only `35/40` and `5/80`.
- Per-initial-state accounting shows positive-only beats union on `6/10` starts, union beats positive-only on `2/10`, and they tie on `2/10`.
- Weighted BC beats union on `6/10` starts, showing that broad coverage is still useful on some split-404 states.

Interpretation: split 404 is not mainly a global support-purity failure. The hard union has higher hidden-positive recall than positive-only with the same hidden-bad count, yet it loses many endpoint successes. This points to sequence/action-distribution effects and state-specific branch choice, matching the motivation for transition-risk weighting, sequence masking, or state-level gating.

## Method Summary

| method_id | success_count | eval_episodes | avg_length | selected_hidden_positive | selected_hidden_bad | hidden_positive_recall | hidden_bad_admission |
| --- | --- | --- | --- | --- | --- | --- | --- |
| positive_only_nn_top40 | 39 | 50 | 169.3 | 35 | 5 | 0.875 | 0.062 |
| weighted_bc_full_pool | 33 | 50 | 208.9 | 40 | 80 | 1.000 | 1.000 |
| triage_v01_adaptive_masscap | 36 | 50 | 190.8 | 33 | 26 | 0.825 | 0.325 |
| v02_positive_nn_risk_union_top40 | 27 | 50 | 248.4 | 39 | 5 | 0.975 | 0.062 |

## Pairwise Endpoint Accounting

| left_method | right_method | left_minus_right_successes | left_better_initials | right_better_initials | tied_initials |
| --- | --- | --- | --- | --- | --- |
| positive_only_nn_top40 | v02_positive_nn_risk_union_top40 | 12 | 6 | 2 | 2 |
| weighted_bc_full_pool | v02_positive_nn_risk_union_top40 | 6 | 6 | 2 | 2 |
| triage_v01_adaptive_masscap | v02_positive_nn_risk_union_top40 | 9 | 5 | 1 | 4 |
| positive_only_nn_top40 | weighted_bc_full_pool | 6 | 4 | 3 | 3 |

## Representative Failure Modes

- Positive-anchor regressions: demo_45 (positive 5/5, union 2/5), demo_89 (positive 4/5, union 0/5), demo_99 (positive 4/5, union 1/5).
- Union rescues: demo_81 (union 5/5, positive 4/5).

## Per-Initial-State Table

| initial_demo_id | case_type | positive_only_success_count | weighted_success_count | v01_success_count | union_success_count | union_minus_best_successes |
| --- | --- | --- | --- | --- | --- | --- |
| demo_5 | union_under_best | 5 | 1 | 5 | 4 | -1 |
| demo_29 | union_under_best | 4 | 4 | 4 | 2 | -2 |
| demo_39 | union_under_best | 0 | 3 | 1 | 1 | -2 |
| demo_45 | positive_anchor_regression | 5 | 1 | 3 | 2 | -3 |
| demo_53 | union_tied_best | 5 | 5 | 5 | 5 | 0 |
| demo_81 | union_rescue | 4 | 5 | 5 | 5 | 0 |
| demo_89 | positive_anchor_regression | 4 | 3 | 4 | 0 | -4 |
| demo_99 | positive_anchor_regression | 4 | 2 | 4 | 1 | -3 |
| demo_105 | union_under_best | 5 | 5 | 4 | 4 | -1 |
| demo_189 | union_under_best | 3 | 4 | 1 | 3 | -1 |

## Candidate Implications

- Candidate A/C should keep the positive-only anchor at the transition or timestep level instead of replacing it with a globally unioned support set.
- Candidate B should use state-level fallback: starts such as `demo_89` and `demo_99` need positive-anchor protection, while starts such as `demo_39` need broader weighted coverage.
- More global threshold tuning is unlikely to fix this split because the hard-union support labels are already strong; the failure appears after support is converted into a sequence policy.

## Outputs

- `results/candidate_breakthrough/can40_split404_method_summary.csv`
- `results/candidate_breakthrough/can40_split404_initial_state_audit.csv`
- `results/candidate_breakthrough/can40_split404_pairwise_summary.csv`
- `results/candidate_breakthrough/can40_split404_failure_audit_REPORT.md`
