# Can Prefix-Positive Diagnostic Figure

This is a controlled Robomimic diagnostic, not a primary benchmark row. Trusted positive labels are early successful-demo prefixes, failures are explicit negatives, and the unlabeled pool contains full successful and failed demonstrations.

## Aggregate

| candidate | support purity | hidden pos | hidden bad | endpoint | avg len |
|---|---:|---:|---:|---:|---:|
| prefix_bad_aware_state_top80 | 0.813 | 195 | 45 | 119/150 (0.793) | 171.3 |
| prefix_state_action_nn_top80 | 0.155 | 37 | 203 | 6/150 (0.040) | 388.3 |

## Per-Split Endpoint Counts

| split | bad-aware top80 | positive-NN top80 |
|---:|---:|---:|
| 101 | 26/50 | 1/50 |
| 202 | 43/50 | 2/50 |
| 303 | 50/50 | 3/50 |

## Interpretation

- Bad-aware prefix support leads positive-only prefix retrieval by `113` successes over `150` endpoint rollouts.
- This mirrors the controlled PointNav prefix-positive mechanism in Robomimic Can.
- Keep the result as generated diagnostic evidence because the split construction changes the default benchmark setting.

## Outputs

- `results/final_paper/tables/can_prefix_positive_diagnostic.csv`
- `results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md`
- `results/final_paper/figures/can_prefix_positive_diagnostic.png`
- `results/final_paper/figures/can_prefix_positive_diagnostic.pdf`
