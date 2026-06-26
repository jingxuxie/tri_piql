# Lift Hard-Negative Endpoint Smoke

This is a bounded endpoint smoke on generated split seed 101, not a final paper endpoint row.
All policies use official Robomimic BC-RNN-GMM with 50 epochs, 100 gradient steps per epoch, and 10 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| bad_aware_proxy_top40 | 0.525 | 0.525 | 0.237 | 2/10 | 127.8 |
| state_action_positive_nn_top40 | 0.175 | 0.175 | 0.412 | 1/10 | 141.4 |

## Interpretation

- Best row: `bad_aware_proxy_top40` with `2/10` successes.
- Positive-NN top40 is the support baseline and gets `1/10` successes after selecting `33` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `1` successes in this bounded check.
- The pure bad-aware candidate is best in this smoke; verify at the frozen endpoint budget before treating the cleaner support as a policy-quality claim.
- The smoke is directionally consistent with the support audit, but the absolute success rates are low and the evaluation budget is only 10 episodes.
- Next decision: rerun the best candidate and positive-NN baseline at the frozen 200-epoch / 50-episode endpoint budget on split 101, then decide whether to expand to split seeds 202 and 303.

## Outputs

- `results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/endpoint_smoke_10ep_summary.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/eval_smoke_10ep/metrics.csv`
- `results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/eval_smoke_10ep/episode_metrics.csv`
