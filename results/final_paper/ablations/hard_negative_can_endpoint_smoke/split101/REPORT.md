# Hard-Negative Can Endpoint Smoke

This is a bounded endpoint smoke on generated split seed 101, not a final paper endpoint row.
All policies use official Robomimic BC-RNN-GMM with 50 epochs, 100 gradient steps per epoch, and 10 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 0.900 | 0.900 | 0.050 | 4/10 | 287.9 |
| bad_aware_proxy_top40 | 1.000 | 1.000 | 0.000 | 1/10 | 373.3 |
| state_action_positive_nn_top40 | 0.400 | 0.400 | 0.300 | 0/10 | 400.0 |

## Interpretation

- Best row: `hybrid_rank_fusion_badaware_heavy_top40` with `4/10` successes.
- Positive-NN top40 is the support baseline and gets `0/10` successes after selecting `24` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `4` successes in this bounded check.
- The pure bad-aware support is cleaner but not best in the smoke; the best endpoint candidate should be prioritized for the next run.
- The endpoint effect aligns with the support diagnostic: the hybrid keeps near-positive coverage while strongly reducing action-conflict bad-demo admission.
- The 200-epoch / 50-episode split-101 follow-up is recorded in `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/REPORT.md`.

## Outputs

- `results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/endpoint_smoke_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/eval_smoke_all/metrics.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_smoke/split101/eval_smoke_all/episode_metrics.csv`
