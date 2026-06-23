# Robomimic Lift Positive-Only NN Control

This diagnostic tests a no-bad-label nearest-neighbor support selector on the Lift MG sparse split.
It uses the same official Robomimic BC-RNN-GMM backbone and the same three policy seeds as the bad-aware Lift control.

## Seed-0 Support Sweep

| method | train demos | selected unlabeled | hidden positive | hidden bad | purity |
|---|---:|---:|---:|---:|---:|
| posonly_nn_top80 | 90 | 80 | 78 | 2 | 0.975 |
| posonly_nn_top160 | 170 | 160 | 126 | 34 | 0.787 |
| posonly_nn_top240 | 250 | 240 | 143 | 97 | 0.596 |
| posonly_nn_top320 | 330 | 320 | 164 | 156 | 0.512 |
| bad_aware_pos_min | 240 | 230 | 203 | 27 | 0.883 |

## Three-Seed Policy Results

| method | 5k mean | 10k mean | 15k mean | 20k mean | oracle-by-seed mean |
|---|---:|---:|---:|---:|---:|
| posonly_nn_top160 | 0.400 | 0.300 | 0.333 | 0.567 | 0.567 |
| bad_aware_pos_min | 0.133 | 0.267 | 0.533 | 0.667 | 0.700 |

## Interpretation

- Positive-only NN has a sharp precision/coverage tradeoff on Lift MG: top80 is high purity (`0.975`) but recovers only 78 hidden-positive demos; top160 recovers 126 hidden positives but already admits 34 hidden-bad demos.
- Broad positive-only NN support degrades quickly: top240 has purity `0.596` and top320 has purity `0.512`.
- Across three policy seeds, bad-aware `pos_min` is stronger at the fixed 15k and 20k budgets and under oracle-by-seed checkpoint selection.
- The no-bad-label top160 policy is not collapsed, but it does not remove the need for explicit bad-demo calibration on Lift MG.
