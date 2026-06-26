# Lift Hard-Negative Three-Split Endpoint Check

This is a generated Lift hard-negative/action-conflict diagnostic over split seeds 101, 202, 303. It is stronger than a single-split development check, but it should be framed as targeted diagnostic evidence rather than as a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts per split.

## Aggregate Result

| candidate | success | success rate | mean support purity | hidden-positive selected | hidden-bad selected | avg len |
|---|---:|---:|---:|---:|---:|---:|
| bad_aware_proxy_top40 | 15/150 | 0.100 | 0.683 | 82 | 38 | 139.9 |
| state_action_positive_nn_top40 | 5/150 | 0.033 | 0.100 | 12 | 108 | 146.8 |

## Per-Split Result

| split | candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---:|---|---:|---:|---:|---:|---:|
| 101 | bad_aware_proxy_top40 | 0.525 | 0.525 | 0.237 | 7/50 | 137.3 |
| 101 | state_action_positive_nn_top40 | 0.175 | 0.175 | 0.412 | 3/50 | 143.6 |
| 202 | bad_aware_proxy_top40 | 0.950 | 0.950 | 0.025 | 6/50 | 137.2 |
| 202 | state_action_positive_nn_top40 | 0.000 | 0.000 | 0.500 | 1/50 | 149.2 |
| 303 | bad_aware_proxy_top40 | 0.575 | 0.575 | 0.212 | 2/50 | 145.0 |
| 303 | state_action_positive_nn_top40 | 0.125 | 0.125 | 0.438 | 1/50 | 147.5 |

## Interpretation

- Best aggregate row: `bad_aware_proxy_top40` with `15/150` successes.
- The best row is ahead of state-action positive-NN top40 by `10` successes over `150` paired-budget rollouts.
- The endpoint effect is directionally consistent with the support audits: bad-aware proxy top40 selects substantially more hidden-positive demos and fewer hard negatives than state-action positive-NN top40.
- This is completed three-split non-Can mechanism evidence, but it remains a low-success exploratory diagnostic rather than a primary Robomimic benchmark row.

## Outputs

- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`
