# Can Prefix-Positive Endpoint Check

This controlled Robomimic diagnostic labels only early prefixes of successful Can demos as positives, uses failed demos as explicit negatives, and trains official BC-RNN-GMM policies on selected full trajectories.

## Result

| candidate | support purity | hidden-positive selected | hidden-bad selected | success | avg len |
|---|---:|---:|---:|---:|---:|
| prefix_bad_aware_state_top80 | 0.850 | 68 | 12 | 43/50 (0.860) | 150.9 |
| prefix_state_action_nn_top80 | 0.163 | 13 | 67 | 2/50 (0.040) | 387.7 |

## Interpretation

- Best row: `prefix_bad_aware_state_top80` with `43/50` successes.
- Best candidate leads the prefix-NN baseline by `41` successes over `50` matched rollouts.
- This split-level report is one slice of the prefix-positive endpoint diagnostic.
- Use the aggregate report, not any one split, for paper-facing claims.
