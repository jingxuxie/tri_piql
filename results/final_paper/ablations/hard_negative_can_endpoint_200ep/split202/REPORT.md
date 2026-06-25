# Hard-Negative Can Split-202 Endpoint Check

This is a single-split endpoint check on generated split seed 202, not a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 0.950 | 0.950 | 0.025 | 35/50 | 200.4 |
| state_action_positive_nn_top40 | 0.550 | 0.550 | 0.225 | 27/50 | 253.7 |

## Interpretation

- Best row: `hybrid_rank_fusion_badaware_heavy_top40` with `35/50` successes.
- Positive-NN top40 is the support baseline and gets `27/50` successes after selecting `18` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `8` successes in this bounded check.
- The endpoint effect aligns with the support diagnostic: the hybrid keeps near-positive coverage while strongly reducing action-conflict bad-demo admission.
- The three-split aggregate is recorded in `results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md`.

## Outputs

- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/eval_50ep/metrics.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202/eval_50ep/episode_metrics.csv`
