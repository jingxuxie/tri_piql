# Official Robomimic BC-RNN-GMM Seed-0 Support Controls

This is a same-backbone seed-0 support-control comparison on Robomimic Can paired low-dimensional data.

Common setup:

- Dataset split: `results/robomimic_inspection/can_paired_low_dim/split_indices.json`.
- Environment: `PickPlaceCan` version `1.5.1`.
- Policy backbone: official Robomimic `BC_RNN_GMM`.
- Observation keys: `robot0_eef_pos`, `robot0_eef_quat`, `robot0_gripper_qpos`, `object`.
- RNN: 2-layer LSTM, hidden dim 400, sequence length 10.
- Actor head: Robomimic default MLP head, `1024,1024`.
- GMM modes: 5.
- Optimization budget: 200 epochs x 100 steps = 20k gradient steps.
- Evaluation: 10 held-out positive initial states, horizon 400, CUDA policy inference.

## Support Sets

| source | train demos | selected unlabeled demos | selected hidden-positive demos | selected hidden-bad demos | selected purity |
|---|---:|---:|---:|---:|---:|
| labeled positive | 10 | 0 | 0 | 0 | n/a |
| score-gap cutoff | 43 | 33 | 33 | 0 | 1.000 |
| fixed top-80 | 90 | 80 | 72 | 8 | 0.900 |

The score-gap support is exactly the first 33 demos from the fixed classifier ranking. The fixed top-80 control adds 47 lower-confidence demos, including 8 hidden-bad demos.

## Rollout Metrics

| source | checkpoint epoch | approx gradient steps | success | avg return | avg length |
|---|---:|---:|---:|---:|---:|
| labeled positive | 50 | 5k | 0.000 | 0.000 | 400.0 |
| labeled positive | 100 | 10k | 0.000 | 0.000 | 400.0 |
| labeled positive | 150 | 15k | 0.000 | 0.000 | 400.0 |
| labeled positive | 200 | 20k | 0.100 | 0.100 | 385.3 |
| score-gap cutoff | 50 | 5k | 0.100 | 0.100 | 373.0 |
| score-gap cutoff | 100 | 10k | 0.700 | 0.700 | 206.2 |
| score-gap cutoff | 150 | 15k | 0.700 | 0.700 | 197.7 |
| score-gap cutoff | 200 | 20k | 0.700 | 0.700 | 207.3 |
| fixed top-80 | 50 | 5k | 0.300 | 0.300 | 321.6 |
| fixed top-80 | 100 | 10k | 0.700 | 0.700 | 197.8 |
| fixed top-80 | 150 | 15k | 0.700 | 0.700 | 198.0 |
| fixed top-80 | 200 | 20k | 0.700 | 0.700 | 207.5 |

## Artifacts

- Score-gap setup: `results/robomimic_official_bc_rnn_gap_seed0_mlphead_setup/REPORT.md`.
- Score-gap evaluation: `results/robomimic_official_bc_rnn_gap_seed0_mlphead_eval/REPORT.md`.
- Scarce setup: `results/robomimic_official_bc_rnn_scarce_seed0_mlphead_setup/REPORT.md`.
- Scarce evaluation: `results/robomimic_official_bc_rnn_scarce_seed0_mlphead_eval/REPORT.md`.
- Fixed top-80 setup: `results/robomimic_official_bc_rnn_top80_seed0_mlphead_setup/REPORT.md`.
- Fixed top-80 evaluation: `results/robomimic_official_bc_rnn_top80_seed0_mlphead_eval/REPORT.md`.

## Interpretation

- The official sequence-aware imitation backbone changes the Robomimic baseline substantially: selected-support BC-RNN-GMM reaches 0.700 success, while scarce-positive-only BC-RNN-GMM reaches only 0.100 at 20k.
- On this seed, fixed top-80 matches score-gap at 10k, 15k, and 20k despite including 8 hidden-bad demos. Therefore this result does not support a claim that score-gap outperforms fixed top-k on Robomimic seed 0.
- The supported score-gap claim here is cleaner and more compact support: 33 pure selected unlabeled demos match the rollout success of 80 selected unlabeled demos with 90% purity.
- For a high-impact claim, the next Robomimic control should stress the cutoff more directly: either higher contamination / lower-quality fixed top-k settings or additional seeds where fixed top-k purity varies. The paper story should not say "weighted BC is best" unless a same-backbone control proves it.
