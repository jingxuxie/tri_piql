# v0.2 Policy-Coverage Diagnostic

Split: `results/final_paper/splits/can_paired_pos40_bad80_split22/split_indices.json`.
Feature kind: `initial_state`.
Summary CSV: `results/final_paper/tables/v02_policy_coverage_diagnostic_split22.csv`.
Per-initial CSV: `results/final_paper/tables/v02_policy_coverage_diagnostic_split22_per_initial.csv`.

This diagnostic is hidden-label-audit evidence, not a selector freeze. It asks whether
candidate train sets cover the valid-positive reset states used by endpoint evaluation.
Initial distances are nearest-neighbor distances in standardized initial demo state space.
Trajectory distances are mean transition-level nearest-neighbor distances in standardized
low-dimensional observation-action space.

## Endpoint and Coverage Summary

| method | success | train pos/bad | valid pos-NN mean | valid pos-NN max | traj pos-NN mean | bad closer | bad margin |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all_train_positive_oracle | 0.980 | 90/0 | 2.451 | 3.798 | 2.387 | 0 | nan |
| positive_only_nn | 0.760 | 47/3 | 2.807 | 3.919 | 2.658 | 1 | 0.814 |
| positive_nn_risk_fusion_top40 | 0.640 | 50/0 | 2.807 | 3.919 | 2.651 | 0 | nan |
| bc_all_mixed | 0.560 | 90/90 | 2.451 | 3.798 | 2.387 | 0 | 0.000 |
| triage_bc | 0.520 | 46/37 | 2.812 | 3.919 | 2.682 | 7 | -0.159 |
| weighted_bc | 0.440 | 50/80 | 2.807 | 3.919 | 2.651 | 8 | -0.315 |

## Proxy Correlations

| proxy | correlation_with_endpoint |
| --- | --- |
| valid_nn_positive_mean | -0.478 |
| valid_transition_nn_positive_mean | -0.482 |
| train_bad_count | -0.729 |
| valid_bad_minus_positive_mean | 0.991 |

## Immediate Read

- Treat these correlations as descriptive only; this split has few methods and shared valid starts.
- A useful v0.2 proxy should penalize bad-demo admission while preserving coverage of valid-positive start states and expert transitions.
- If a high-purity candidate loses despite good support labels, inspect the per-initial CSV for uncovered reset states or trajectories.
