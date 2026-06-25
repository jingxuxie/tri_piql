# Can Coverage-Shift Three-Split Endpoint Check

This is a generated scarce-positive coverage-shift Can diagnostic over split seeds 101, 202, 303. It is stronger than a single-split development check, but it should be framed as targeted diagnostic evidence rather than as a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts per split.

## Aggregate Result

| candidate | success | success rate | mean support purity | hidden-positive selected | hidden-bad selected | avg len |
|---|---:|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 120/150 | 0.800 | 0.983 | 118 | 2 | 182.7 |
| state_action_positive_nn_top40 | 103/150 | 0.687 | 0.875 | 105 | 15 | 207.5 |

## Per-Split Result

| split | candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---:|---|---:|---:|---:|---:|---:|
| 101 | hybrid_rank_fusion_badaware_heavy_top40 | 0.975 | 0.975 | 0.013 | 39/50 | 192.6 |
| 101 | state_action_positive_nn_top40 | 0.850 | 0.850 | 0.075 | 35/50 | 206.4 |
| 202 | hybrid_rank_fusion_badaware_heavy_top40 | 0.975 | 0.975 | 0.013 | 41/50 | 174.5 |
| 202 | state_action_positive_nn_top40 | 0.850 | 0.850 | 0.075 | 29/50 | 238.5 |
| 303 | hybrid_rank_fusion_badaware_heavy_top40 | 1.000 | 1.000 | 0.000 | 40/50 | 180.8 |
| 303 | state_action_positive_nn_top40 | 0.925 | 0.925 | 0.037 | 39/50 | 177.7 |

## Interpretation

- Best aggregate row: `hybrid_rank_fusion_badaware_heavy_top40` with `120/150` successes.
- The best row is ahead of state-action positive-NN top40 by `17` successes over `150` paired-budget rollouts.
- The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.
- This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows unless the manuscript explicitly frames it as generated diagnostic evidence.

## Outputs

- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/endpoint_200ep_3split_summary.csv`
- `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md`
