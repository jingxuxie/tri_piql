# Official Robomimic BC-RNN-GMM Seed-2 Coverage Stress

This run tests the failure mode exposed by seed-2 support selection: the score-gap cutoff is perfectly pure but selects very few demonstrations.

Common setup:

- Dataset split: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
- Environment: `PickPlaceCan` version `1.5.1`.
- Policy backbone: official Robomimic `BC_RNN_GMM`.
- Actor head: Robomimic default MLP head, `1024,1024`.
- RNN: 2-layer LSTM, hidden dim 400, sequence length 10.
- GMM modes: 5.
- Optimization budget: 200 epochs x 100 steps = 20k gradient steps.
- Evaluation: 10 held-out positive initial states, horizon 400, CUDA policy inference.

## Support Diagnostics

| seed | source | train demos | selected unlabeled demos | hidden-positive selected | hidden-bad selected | purity |
|---:|---|---:|---:|---:|---:|---:|
| 0 | score-gap cutoff | 43 | 33 | 33 | 0 | 1.000 |
| 0 | fixed top-80 | 90 | 80 | 72 | 8 | 0.900 |
| 1 | score-gap cutoff | 55 | 45 | 45 | 0 | 1.000 |
| 1 | fixed top-80 | 90 | 80 | 70 | 10 | 0.875 |
| 2 | score-gap cutoff | 19 | 9 | 9 | 0 | 1.000 |
| 2 | fixed top-80 | 90 | 80 | 74 | 6 | 0.925 |

## Seed-2 Rollout Metrics

| source | checkpoint epoch | approx gradient steps | success | avg return | avg length |
|---|---:|---:|---:|---:|---:|
| score-gap cutoff | 50 | 5k | 0.000 | 0.000 | 400.0 |
| score-gap cutoff | 100 | 10k | 0.000 | 0.000 | 400.0 |
| score-gap cutoff | 150 | 15k | 0.100 | 0.100 | 372.0 |
| score-gap cutoff | 200 | 20k | 0.000 | 0.000 | 400.0 |
| fixed top-80 | 50 | 5k | 0.200 | 0.200 | 343.7 |
| fixed top-80 | 100 | 10k | 0.600 | 0.600 | 223.6 |
| fixed top-80 | 150 | 15k | 0.700 | 0.700 | 198.9 |
| fixed top-80 | 200 | 20k | 0.900 | 0.900 | 137.0 |

## Artifacts

- Score-gap setup: `results/robomimic_official_bc_rnn_gap_seed2_mlphead_setup/REPORT.md`.
- Score-gap evaluation: `results/robomimic_official_bc_rnn_gap_seed2_mlphead_eval/REPORT.md`.
- Top-80 setup: `results/robomimic_official_bc_rnn_top80_seed2_mlphead_setup/REPORT.md`.
- Top-80 evaluation: `results/robomimic_official_bc_rnn_top80_seed2_mlphead_eval/REPORT.md`.

## Interpretation

- Score-gap purity is not sufficient for policy quality. On seed 2 it selects only 9 unlabeled demonstrations, and the resulting official BC-RNN-GMM policy peaks at 0.100 success.
- Fixed top-80 includes 6 hidden-bad demonstrations but also 74 hidden-positive demonstrations, and reaches 0.900 success at 20k.
- The current largest-gap cutoff is too conservative under some classifier orderings. The next method branch should add a coverage-aware support rule, for example a minimum selected-demo floor, a validation-free plateau criterion, or a soft weighting rule over the high-ranked support.
- The paper story should be adjusted away from "weighted BC is best" toward "positive/negative labels identify useful unlabeled support, but support selection must trade off purity and coverage."
