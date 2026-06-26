# Lift Hard-Negative Split-303 Endpoint Check

This is a single-split endpoint check on generated split seed 303, not a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| bad_aware_proxy_top40 | 0.575 | 0.575 | 0.212 | 2/50 | 145.0 |
| state_action_positive_nn_top40 | 0.125 | 0.125 | 0.438 | 1/50 | 147.5 |

## Interpretation

- Best row: `bad_aware_proxy_top40` with `2/50` successes.
- Positive-NN top40 is the support baseline and gets `1/50` successes after selecting `35` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `1` successes in this bounded check.
- The bad-aware candidate is best on this split; use the aggregate report for claim scope.
- The endpoint effect is consistent with the support audit: the bad-aware candidate keeps more hidden-positive coverage while reducing action-conflict bad-demo admission.
- The three-split aggregate is recorded in `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`.

## Outputs

- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split303/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split303/eval_50ep/metrics.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split303/eval_50ep/episode_metrics.csv`
