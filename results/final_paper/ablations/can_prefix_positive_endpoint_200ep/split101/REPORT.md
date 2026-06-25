# Can Prefix-Positive Endpoint Check

This controlled Robomimic diagnostic labels only early prefixes of successful Can demos as positives, uses failed demos as explicit negatives, and trains official BC-RNN-GMM policies on selected full trajectories.

## Result

| candidate | support purity | hidden-positive selected | hidden-bad selected | success | avg len |
|---|---:|---:|---:|---:|---:|
| prefix_bad_aware_state_top80 | 0.625 | 50 | 30 | 26/50 (0.520) | 248.5 |
| prefix_state_action_nn_top80 | 0.138 | 11 | 69 | 1/50 (0.020) | 394.6 |

## Interpretation

- Best row: `prefix_bad_aware_state_top80` with `26/50` successes.
- Best candidate leads the prefix-NN baseline by `25` successes over `50` matched rollouts.
- This split-level report is one slice of the prefix-positive endpoint diagnostic.
- Use the aggregate report, not any one split, for paper-facing claims.
