# v0.2 Union Candidate Endpoint Gate

This is a single-split endpoint gate for a union candidate that keeps positive-only NN support and adds risk-fusion demos.
It is not a frozen v0.2 result; it decides whether the union family deserves more endpoint budget.

## Endpoint Summary

| method_id | method_role | endpoint_success | success_count | eval_episodes | train_positive_count | train_bad_count |
| --- | --- | --- | --- | --- | --- | --- |
| all_train_positive_oracle | oracle_control | 0.98 | 49 | 50 | 90 | 0 |
| positive_only_nn | strong_baseline | 0.84 | 42 | 50 | 46 | 4 |
| positive_nn_risk_fusion_top40 | failed_v02_gate | 0.82 | 41 | 50 | 49 | 1 |
| positive_nn_risk_union_top40 | union_candidate | 0.76 | 38 | 50 | 50 | 5 |
| triage_bc | v01_method | 0.76 | 38 | 50 | 50 | 30 |
| weighted_bc | strong_baseline | 0.72 | 36 | 50 | 50 | 80 |
| bc_all_mixed | mixed_log_baseline | 0.5 | 25 | 50 | 90 | 90 |

## Read

- Union reaches `0.760` (38/50) on split 11.
- This is `-0.080` versus positive-only NN (0.84) and `-0.080` versus the best existing non-oracle row (positive_only_nn at 0.84).
- Versus risk fusion, the delta is `-0.060`.
- Per-initial mean delta versus positive-only is `-0.080` over 10 validation starts.
- Interpretation: negative split gate against the strongest existing non-oracle baseline.
- Next gate: aggregate all completed Can 40p/80b union split checks before spending additional GPU budget.

## Outputs

- `results/final_paper/ablations/v02_union_endpoint_200ep_can40/split11/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/v02_union_endpoint_200ep_can40/split11/endpoint_200ep_per_initial.csv`
