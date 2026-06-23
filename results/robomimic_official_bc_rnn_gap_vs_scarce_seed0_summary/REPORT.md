# Official Robomimic BC-RNN-GMM Gap vs Scarce Positive

This is a same-backbone seed-0 comparison on Robomimic Can paired low-dimensional data.

Update: the same-backbone fixed top-80 support control has since been run. Use `results/robomimic_official_bc_rnn_seed0_support_controls/REPORT.md` for the current seed-0 Robomimic interpretation.

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

## Support

| source | train demos | selected unlabeled demos | selected hidden-positive demos | selected hidden-bad demos | selected purity |
|---|---:|---:|---:|---:|---:|
| labeled positive | 10 | 0 | 0 | 0 | n/a |
| score-gap selected support | 43 | 33 | 33 | 0 | 1.000 |

The score-gap selector recovered 33 hidden-positive unlabeled demonstrations and no hidden-bad demonstrations in this seed-0 run.

## Rollout Metrics

| source | checkpoint epoch | approx gradient steps | success | avg return | avg length |
|---|---:|---:|---:|---:|---:|
| labeled positive | 50 | 5k | 0.000 | 0.000 | 400.0 |
| labeled positive | 100 | 10k | 0.000 | 0.000 | 400.0 |
| labeled positive | 150 | 15k | 0.000 | 0.000 | 400.0 |
| labeled positive | 200 | 20k | 0.100 | 0.100 | 385.3 |
| score-gap selected support | 50 | 5k | 0.100 | 0.100 | 373.0 |
| score-gap selected support | 100 | 10k | 0.700 | 0.700 | 206.2 |
| score-gap selected support | 150 | 15k | 0.700 | 0.700 | 197.7 |
| score-gap selected support | 200 | 20k | 0.700 | 0.700 | 207.3 |

## Artifacts

- Gap setup: `results/robomimic_official_bc_rnn_gap_seed0_mlphead_setup/REPORT.md`.
- Gap evaluation: `results/robomimic_official_bc_rnn_gap_seed0_mlphead_eval/REPORT.md`.
- Scarce setup: `results/robomimic_official_bc_rnn_scarce_seed0_mlphead_setup/REPORT.md`.
- Scarce evaluation: `results/robomimic_official_bc_rnn_scarce_seed0_mlphead_eval/REPORT.md`.
- Evaluator script: `scripts/evaluate_robomimic_official_policy.py`.
- Setup script: `scripts/prepare_robomimic_official_bc_rnn.py`.

## Interpretation

- The previous local GMM extractor was not the right baseline for Robomimic policy quality; it could exploit support weakly but had unstable checkpoint behavior.
- With the official Robomimic BC-RNN-GMM backbone and default MLP head, the recovered score-gap support produces a much stronger policy: 0.700 success at 10k, 15k, and 20k steps.
- The matched scarce-positive-only BC-RNN-GMM control remains weak under the same training and evaluation protocol, reaching only 0.100 at 20k.
- The failed direct-RNN-head official run should be treated as a configuration negative, not as evidence against the support signal: removing the Robomimic default actor MLP head gave 0.000 success across 5k-20k.

This is still a single-seed Robomimic result. It is strong enough to keep Robomimic in the plan, but the later fixed top-80 control shows that the current score-gap advantage is compact pure support, not higher rollout success on seed 0.
