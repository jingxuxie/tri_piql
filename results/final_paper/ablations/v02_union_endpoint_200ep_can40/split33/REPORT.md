# v0.2 Union Candidate Endpoint Gate

This is a single-split endpoint gate for a union candidate that keeps positive-only NN support and adds risk-fusion demos.
It is not a frozen v0.2 result; it decides whether the union family deserves more endpoint budget.

## Endpoint Summary

| method_id | method_role | endpoint_success | success_count | eval_episodes | train_positive_count | train_bad_count |
| --- | --- | --- | --- | --- | --- | --- |
| all_train_positive_oracle | oracle_control | 0.98 | 49 | 50 | 90 | 0 |
| positive_nn_risk_union_top40 | union_candidate | 0.78 | 39 | 50 | 49 | 8 |
| triage_bc | v01_method | 0.7 | 35 | 50 | 44 | 13 |
| weighted_bc | strong_baseline | 0.64 | 32 | 50 | 50 | 80 |
| positive_only_nn | strong_baseline | 0.56 | 28 | 50 | 43 | 7 |
| bc_all_mixed | mixed_log_baseline | 0.56 | 28 | 50 | 90 | 90 |

## Read

- Union reaches `0.780` (39/50) on split 33.
- This is `+0.220` versus positive-only NN (0.56) and `+0.080` versus the best existing non-oracle row (triage_bc at 0.7).
- No risk-fusion endpoint row is available for this split.
- Per-initial mean delta versus positive-only is `+0.220` over 10 validation starts.
- Interpretation: positive split gate, but this still needs aggregate and cross-task validation.
- Next gate: aggregate all completed Can 40p/80b union split checks before spending additional GPU budget.

## Outputs

- `results/final_paper/ablations/v02_union_endpoint_200ep_can40/split33/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/v02_union_endpoint_200ep_can40/split33/endpoint_200ep_per_initial.csv`
