# Lift Hard-Negative Split-202 Endpoint Check

This is a single-split endpoint check on generated split seed 202, not a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| bad_aware_proxy_top40 | 0.950 | 0.950 | 0.025 | 6/50 | 137.2 |
| state_action_positive_nn_top40 | 0.000 | 0.000 | 0.500 | 1/50 | 149.2 |

## Interpretation

- Best row: `bad_aware_proxy_top40` with `6/50` successes.
- Positive-NN top40 is the support baseline and gets `1/50` successes after selecting `40` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `5` successes in this bounded check.
- The bad-aware candidate is best on this split; use the aggregate report for claim scope.
- The endpoint effect is consistent with the support audit: the bad-aware candidate keeps near-positive coverage while sharply reducing action-conflict bad-demo admission.
- The three-split aggregate is recorded in `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`.

## Outputs

- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/eval_50ep/metrics.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/eval_50ep/episode_metrics.csv`
