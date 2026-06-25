# Hard-Negative Can Three-Split Endpoint Check

This is a generated hard-negative Can diagnostic over split seeds 101, 202, 303. It is stronger than a single-split development check, but it should be framed as targeted diagnostic evidence rather than as a primary Robomimic benchmark row.
All policies use official Robomimic BC-RNN-GMM with 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts per split.

## Aggregate Result

| candidate | success | success rate | mean support purity | hidden-positive selected | hidden-bad selected | avg len |
|---|---:|---:|---:|---:|---:|---:|
| hybrid_rank_fusion_badaware_heavy_top40 | 104/150 | 0.693 | 0.942 | 113 | 7 | 198.9 |
| state_action_positive_nn_top40 | 91/150 | 0.607 | 0.583 | 70 | 50 | 223.3 |

## Per-Split Result

| split | candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---:|---|---:|---:|---:|---:|---:|
| 101 | hybrid_rank_fusion_badaware_heavy_top40 | 0.900 | 0.900 | 0.050 | 33/50 | 205.8 |
| 101 | state_action_positive_nn_top40 | 0.400 | 0.400 | 0.300 | 30/50 | 218.0 |
| 202 | hybrid_rank_fusion_badaware_heavy_top40 | 0.950 | 0.950 | 0.025 | 35/50 | 200.4 |
| 202 | state_action_positive_nn_top40 | 0.550 | 0.550 | 0.225 | 27/50 | 253.7 |
| 303 | hybrid_rank_fusion_badaware_heavy_top40 | 0.975 | 0.975 | 0.013 | 36/50 | 190.5 |
| 303 | state_action_positive_nn_top40 | 0.800 | 0.800 | 0.100 | 34/50 | 198.1 |

## Interpretation

- Best aggregate row: `hybrid_rank_fusion_badaware_heavy_top40` with `104/150` successes.
- The best row is ahead of state-action positive-NN top40 by `13` successes over `150` paired-budget rollouts.
- The endpoint effect aligns with the support diagnostic: the hybrid keeps near-positive coverage while strongly reducing action-conflict bad-demo admission.
- This result is suitable as targeted hard-negative evidence; keep the primary benchmark claims separate from the generated diagnostic.

## Outputs

- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/endpoint_200ep_3split_summary.csv`
- `results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md`
