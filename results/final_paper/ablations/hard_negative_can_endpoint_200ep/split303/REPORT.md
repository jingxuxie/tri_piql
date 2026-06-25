# Hard-Negative Can Split-303 Endpoint Check

This is a single-split endpoint check on generated split seed 303, not a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 0.975 | 0.975 | 0.013 | 36/50 | 190.5 |
| state_action_positive_nn_top40 | 0.800 | 0.800 | 0.100 | 34/50 | 198.1 |

## Interpretation

- Best row: `hybrid_rank_fusion_badaware_heavy_top40` with `36/50` successes.
- Positive-NN top40 is the support baseline and gets `34/50` successes after selecting `8` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `2` successes in this bounded check.
- The endpoint effect aligns with the support diagnostic: the hybrid keeps near-positive coverage while strongly reducing action-conflict bad-demo admission.
- The three-split aggregate is recorded in `results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md`.

## Outputs

- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/eval_50ep/metrics.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303/eval_50ep/episode_metrics.csv`
