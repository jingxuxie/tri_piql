# Hard-Negative Can Split-101 Endpoint Check

This is a single-split endpoint check on generated split seed 101, not a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 0.900 | 0.900 | 0.050 | 33/50 | 205.8 |
| state_action_positive_nn_top40 | 0.400 | 0.400 | 0.300 | 30/50 | 218.0 |

## Interpretation

- Best row: `hybrid_rank_fusion_badaware_heavy_top40` with `33/50` successes.
- Positive-NN top40 is the support baseline and gets `30/50` successes after selecting `24` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `3` successes in this bounded check.
- The endpoint effect aligns with the support diagnostic: the hybrid keeps near-positive coverage while strongly reducing action-conflict bad-demo admission.
- The three-split aggregate is recorded in `results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md`.

## Outputs

- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/eval_50ep/metrics.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101/eval_50ep/episode_metrics.csv`
