# Can Prefix-Positive 3-Split Endpoint Check

This is a controlled Robomimic diagnostic, not a primary benchmark row. It tests whether explicit bad labels help when trusted successes provide only early trajectory prefixes and the useful full trajectories are hidden inside the unlabeled pool.

Completed split seeds: `101, 202, 303`.
All completed rows use official Robomimic BC-RNN-GMM, 200 epochs, 100 gradient steps per epoch, and 50 valid-positive evaluation starts per split.

## Aggregate Result

| candidate | splits | success | success rate | mean support purity | hidden-positive selected | hidden-bad selected | avg len |
|---|---:|---:|---:|---:|---:|---:|---:|
| prefix_bad_aware_state_top80 | 3 | 119/150 | 0.793 | 0.813 | 195 | 45 | 171.3 |
| prefix_state_action_nn_top80 | 3 | 6/150 | 0.040 | 0.155 | 37 | 203 | 388.3 |

## Per-Split Result

| split | candidate | support purity | hidden-positive recall | hidden-bad admission | success | avg len |
|---:|---|---:|---:|---:|---:|---:|
| 101 | prefix_bad_aware_state_top80 | 0.625 | 0.625 | 0.375 | 26/50 | 248.5 |
| 101 | prefix_state_action_nn_top80 | 0.138 | 0.138 | 0.863 | 1/50 | 394.6 |
| 202 | prefix_bad_aware_state_top80 | 0.850 | 0.850 | 0.150 | 43/50 | 150.9 |
| 202 | prefix_state_action_nn_top80 | 0.163 | 0.163 | 0.838 | 2/50 | 387.7 |
| 303 | prefix_bad_aware_state_top80 | 0.963 | 0.963 | 0.037 | 50/50 | 114.6 |
| 303 | prefix_state_action_nn_top80 | 0.163 | 0.163 | 0.838 | 3/50 | 382.6 |

## Interpretation

- Best aggregate row: `prefix_bad_aware_state_top80` with `119/150` successes.
- Best row leads the prefix state-action NN top80 baseline by `113` successes over `150` matched rollouts.
- This is the first Robomimic result that directly mirrors the PointNav prefix-positive mechanism.
- This is strong controlled robotics evidence for the prefix-positive mechanism, but it is not a primary benchmark row because the split construction changes the default Robomimic setting.

## Outputs

- `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/endpoint_200ep_aggregate_summary.csv`
- `results/final_paper/ablations/can_prefix_positive_endpoint_200ep/REPORT.md`
