# Lift Hard-Negative Split-101 Endpoint Check

This is a single-split endpoint check on generated split seed 101, not a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| bad_aware_proxy_top40 | 0.525 | 0.525 | 0.237 | 7/50 | 137.3 |
| state_action_positive_nn_top40 | 0.175 | 0.175 | 0.412 | 3/50 | 143.6 |

## Interpretation

- Best row: `bad_aware_proxy_top40` with `7/50` successes.
- Positive-NN top40 is the support baseline and gets `3/50` successes after selecting `33` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `4` successes in this bounded check.
- The bad-aware candidate is best on this split; use the aggregate report for claim scope.
- The endpoint result is directionally consistent with the support audit: bad-aware proxy top40 keeps more hidden-positive support and admits fewer hidden-bad demos than state-action positive-NN top40.
- The three-split aggregate is recorded in `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`.

## Outputs

- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/eval_50ep/metrics.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/eval_50ep/episode_metrics.csv`
