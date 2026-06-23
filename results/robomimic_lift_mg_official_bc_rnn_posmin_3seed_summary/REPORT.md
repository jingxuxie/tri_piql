# Robomimic Lift MG Pos-Min Official BC-RNN-GMM Three-Seed Summary

Dataset: `data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5`.

Split: `results/robomimic_inspection/lift_mg_low_dim_sparse/split_indices.json`.

Selector: `positive_plus_classifier_demo_threshold_unlabeled_demos` with `--demo-threshold-rule pos_min`.

The `pos_min` threshold is hidden-label-free: it trains the positive-vs-negative state-action classifier on the 10 labeled-positive and 10 labeled-negative demos, averages classifier probabilities per demo, then keeps unlabeled demos whose score is at least the minimum labeled-positive demo score.

Protocol:

- Official Robomimic BC-RNN-GMM backbone.
- `1024,1024` actor head, 2-layer LSTM with hidden size `400`, 5 GMM modes.
- `20,000` optimizer steps, saved at `5k / 10k / 15k / 20k`.
- Evaluation uses `10` held-out reward-positive Lift initial states and horizon `150`.

## Support

| seed | train demos | selected unlabeled | hidden positive | hidden bad | purity |
|---:|---:|---:|---:|---:|---:|
| 0 | 240 | 230 | 203 | 27 | 0.883 |
| 1 | 254 | 244 | 206 | 38 | 0.844 |
| 2 | 248 | 238 | 206 | 32 | 0.866 |
| mean | 247.3 | 237.3 | 205.0 | 32.3 | 0.864 |

## Policy Results

Success rate over 10 held-out reward-positive starts per seed:

| seed | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.200 | 0.400 | 0.600 | 0.800 | 0.800 |
| 1 | 0.200 | 0.200 | 0.500 | 0.400 | 0.500 |
| 2 | 0.000 | 0.200 | 0.500 | 0.800 | 0.800 |
| mean | 0.133 | 0.267 | 0.533 | 0.667 | 0.700 |

## Interpretation

The support result is stable: across seeds, the rule selects about 237 unlabeled demos with about 205 hidden reward-positive demos and 32 hidden bad demos. This converts the original unlabeled pool from `19.4%` reward-positive to `86.4%` selected-positive support on average.

The policy result is useful but not as clean as the seed-0 summary alone. Seeds 0 and 2 reach `0.800` at 20k, matching the seed-0 oracle all-positive result, but seed 1 peaks at `0.500` and drops to `0.400` at 20k. The three-seed mean reaches `0.667` at 20k and `0.700` best-per-seed.

The honest Lift claim is now: `pos_min` is a simple hidden-label-free selector that robustly purifies and expands support on a second Robomimic task, and it often trains a strong BC-RNN-GMM policy. Same-seed controls are now available in `results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`: `pos_min` is far above all-demo cloning and close to all-positive oracle support, but not uniformly equal to oracle at every checkpoint.

Next comparison to make this paper-facing: evaluate whether support-validation checkpoint selection would pick seed 1's 15k checkpoint instead of 20k, and decide whether the paper should report fixed 20k or selected-checkpoint performance.

Artifacts:

- Seed 0 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed0_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_posmin_seed0_eval/REPORT.md`
- Seed 1 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed1_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_posmin_seed1_eval/REPORT.md`
- Seed 2 setup/eval: `results/robomimic_lift_mg_official_bc_rnn_posmin_seed2_setup/REPORT.md`, `results/robomimic_lift_mg_official_bc_rnn_posmin_seed2_eval/REPORT.md`
- Same-seed controls: `results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`
