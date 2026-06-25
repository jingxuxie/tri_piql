# Can Coverage-Shift Endpoint Smoke

This is a bounded endpoint smoke on generated split seed 101, not a final paper endpoint row.
All policies use official Robomimic BC-RNN-GMM with 50 epochs, 100 gradient steps per epoch, and 10 valid-positive evaluation starts.

## Result

| candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 0.975 | 0.975 | 0.013 | 4/10 | 308.0 |
| bad_aware_proxy_top40 | 1.000 | 1.000 | 0.000 | 2/10 | 350.8 |
| state_action_positive_nn_top40 | 0.850 | 0.850 | 0.075 | 0/10 | 400.0 |

## Interpretation

- Best row: `hybrid_rank_fusion_badaware_heavy_top40` with `4/10` successes.
- Positive-NN top40 is the support baseline and gets `0/10` successes after selecting `6` hidden-bad demos on this split.
- The best row is ahead of positive-NN by `4` successes in this bounded check.
- The pure bad-aware support is cleaner but not best in the smoke; the best endpoint candidate should be prioritized for the next run.
- The endpoint effect is directionally consistent with the support audit: the hybrid keeps almost all hidden-positive coverage while removing most hidden-bad contamination under initial-pose coverage shift.
- Next decision: rerun the best candidate and positive-NN baseline at the frozen 200-epoch / 50-episode endpoint budget on split 101, then decide whether to expand to split seeds 202 and 303.

## Outputs

- `results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/endpoint_smoke_summary.csv`
- `results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/eval_smoke_all/metrics.csv`
- `results/final_paper/ablations/can_coverage_shift_endpoint_smoke/split101/eval_smoke_all/episode_metrics.csv`
