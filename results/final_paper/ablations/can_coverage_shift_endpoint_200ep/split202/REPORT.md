# Can Coverage-Shift Split-202 Endpoint Check

This is a single-split endpoint check on generated split seed 202, not a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 0.975 | 0.975 | 0.013 | 41/50 | 174.5 |
| state_action_positive_nn_top40 | 0.850 | 0.850 | 0.075 | 29/50 | 238.5 |

## Interpretation

- Best row: `hybrid_rank_fusion_badaware_heavy_top40` with `41/50` successes.
- Positive-NN top40 is the support baseline and gets `29/50` successes after selecting `6` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `12` successes in this bounded check.
- The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.
- The three-split aggregate is recorded in `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md`.

## Outputs

- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/eval_50ep/metrics.csv`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/eval_50ep/episode_metrics.csv`
