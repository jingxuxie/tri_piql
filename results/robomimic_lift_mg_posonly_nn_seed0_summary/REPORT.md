# Robomimic Lift Positive-Only NN Control

This diagnostic tests a no-bad-label nearest-neighbor support selector on the Lift MG sparse split.
It uses the same official Robomimic BC-RNN-GMM backbone as the main Lift rows, but only seed 0 has been trained so far.

## Support Sweep

| method | train demos | selected unlabeled | hidden positive | hidden bad | purity |
|---|---:|---:|---:|---:|---:|
| posonly_nn_top80 | 90 | 80 | 78 | 2 | 0.975 |
| posonly_nn_top160 | 170 | 160 | 126 | 34 | 0.787 |
| posonly_nn_top240 | 250 | 240 | 143 | 97 | 0.596 |
| posonly_nn_top320 | 330 | 320 | 164 | 156 | 0.512 |
| bad_aware_pos_min | 240 | 230 | 203 | 27 | 0.883 |

## Seed-0 Policy Results

| method | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| posonly_nn_top80 | 0.300 | 0.300 | 0.400 | 0.400 | 0.400 |
| posonly_nn_top160 | 0.500 | 0.200 | 0.200 | 0.500 | 0.500 |
| bad_aware_pos_min | 0.200 | 0.400 | 0.600 | 0.800 | 0.800 |

## Interpretation

- Positive-only NN has a sharp precision/coverage tradeoff on Lift MG: top80 is high purity (`0.975`) but recovers only 78 hidden-positive demos; top160 recovers 126 hidden positives but already admits 34 hidden-bad demos.
- Broad positive-only NN support degrades quickly: top240 has purity `0.596` and top320 has purity `0.512`.
- The seed-0 policy check favors the bad-aware `pos_min` selector: it reaches `0.800` at 20k, while positive-only NN top80 reaches `0.400` and top160 reaches `0.500` at 20k.
- This is a one-seed policy diagnostic, not yet a three-seed main table row. It is enough to show that Lift is a better candidate than Can 40p/80b for an explicit-bad-label calibration story.
