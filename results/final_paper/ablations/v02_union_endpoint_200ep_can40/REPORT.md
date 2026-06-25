# v0.2 Union Candidate Can 40p/80b Endpoint Summary

This aggregates the bounded three-split endpoint gate for the union candidate.
The candidate keeps positive-only NN support and adds risk-fusion demos; it was developed after the action-risk replacement candidate failed endpoint checks.

## Aggregate Endpoint Rows

| method_id | method_role | split_count | success_count | eval_episodes | endpoint_success | split_successes |
| --- | --- | --- | --- | --- | --- | --- |
| all_train_positive_oracle | oracle_control | 3 | 147 | 150 | 0.980 | 11:0.980;22:0.980;33:0.980 |
| positive_nn_risk_union_top40 | union_candidate | 3 | 116 | 150 | 0.773 | 11:0.760;22:0.780;33:0.780 |
| positive_nn_risk_fusion_top40 | failed_v02_gate | 2 | 73 | 100 | 0.730 | 11:0.820;22:0.640 |
| positive_only_nn | strong_baseline | 3 | 108 | 150 | 0.720 | 11:0.840;22:0.760;33:0.560 |
| triage_bc | v01_method | 3 | 99 | 150 | 0.660 | 11:0.760;22:0.520;33:0.700 |
| weighted_bc | strong_baseline | 3 | 90 | 150 | 0.600 | 11:0.720;22:0.440;33:0.640 |
| bc_all_mixed | mixed_log_baseline | 3 | 81 | 150 | 0.540 | 11:0.500;22:0.560;33:0.560 |

## Split Winners

| split_seed | winner | winner_success | best_existing_baseline | best_existing_success | union_minus_best_existing |
| --- | --- | --- | --- | --- | --- |
| 11 | positive_only_nn | 0.840 | positive_only_nn | 0.840 | -0.080 |
| 22 | positive_nn_risk_union_top40 | 0.780 | positive_only_nn | 0.760 | +0.020 |
| 33 | positive_nn_risk_union_top40 | 0.780 | triage_bc | 0.700 | +0.080 |

## Read

- Union reaches `116/150` (`0.773`), versus positive-only NN `0.720`, TRIAGE-BC v0.1 `0.660`, and weighted BC `0.600`.
- Union is the best non-oracle row on `2/3` split seeds and pooled best over 150 rollouts.
- This is the first Can 40p/80b candidate that beats the strong positive-only row in the pooled frozen endpoint matrix.
- It is still not a full high-impact v0.2 result: Lift MG and Can MG remain unresolved, and the candidate loses split 11 to positive-only NN.

## Outputs

- `results/final_paper/ablations/v02_union_endpoint_200ep_can40/endpoint_200ep_3split_summary.csv`
- split reports under `results/final_paper/ablations/v02_union_endpoint_200ep_can40/split*/REPORT.md`
