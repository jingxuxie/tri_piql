# Can Coverage-Shift Split-303 Endpoint Check

This is a single-split endpoint check on generated split seed 303, not a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 1.000 | 1.000 | 0.000 | 40/50 | 180.8 |
| state_action_positive_nn_top40 | 0.925 | 0.925 | 0.037 | 39/50 | 177.7 |

## Interpretation

- Best row: `hybrid_rank_fusion_badaware_heavy_top40` with `40/50` successes.
- Positive-NN top40 is the support baseline and gets `39/50` successes after selecting `3` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `1` successes in this bounded check.
- The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.
- The three-split aggregate is recorded in `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md`.

## Outputs

- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/endpoint_200ep_summary.csv`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/eval_50ep/metrics.csv`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/eval_50ep/episode_metrics.csv`
