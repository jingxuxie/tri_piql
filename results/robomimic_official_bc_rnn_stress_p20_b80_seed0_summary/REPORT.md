# Official Robomimic Heavy-Contamination Stress Check

This stress check uses the same Robomimic Can paired low-dimensional data, but changes the unlabeled pool from the default 80 hidden-positive / 80 hidden-bad demos to 20 hidden-positive / 80 hidden-bad demos.

Protocol:

- Labels: 10 successful demos, 10 failed demos.
- Unlabeled stress pool: 20 hidden-positive demos, 80 hidden-bad demos.
- Backbone: official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Training budget: 200 epochs x 100 steps = 20k optimizer steps.
- Evaluation: 10 rollouts per checkpoint from held-out validation-positive initial states, horizon 400.

Artifacts:

- Stress split: `results/robomimic_inspection/can_paired_low_dim_stress_pos20_bad80/REPORT.md`
- Selector score analysis: `results/robomimic_selector_score_analysis_stress_p20_b80/REPORT.md`
- Matched three-selector summary: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md`
- Coverage-aware setup seed 0: `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed0_mlphead_setup/REPORT.md`
- Coverage-aware eval seed 0: `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Coverage-aware setup/eval seed 1: `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed1_mlphead_setup/REPORT.md`, `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Coverage-aware setup/eval seed 2: `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed2_mlphead_setup/REPORT.md`, `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed2_mlphead_eval/REPORT.md`
- Precision-biased top-20 setup seed 0: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed0_mlphead_setup/REPORT.md`
- Precision-biased top-20 eval seed 0: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Precision-biased top-20 setup/eval seed 1: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed1_mlphead_setup/REPORT.md`, `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Precision-biased top-20 setup/eval seed 2: `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed2_mlphead_setup/REPORT.md`, `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed2_mlphead_eval/REPORT.md`
- Fixed top-80 setup seed 0: `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed0_mlphead_setup/REPORT.md`
- Fixed top-80 eval seed 0: `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Fixed top-80 setup/eval seed 1: `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed1_mlphead_setup/REPORT.md`, `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Fixed top-80 setup/eval seed 2: `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed2_mlphead_setup/REPORT.md`, `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed2_mlphead_eval/REPORT.md`

## Support Selection

Support-only diagnostics across three classifier seeds:

| method | seed | train demos | selected unlabeled | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|---:|---:|
| coverage-aware score-gap posx4 | 0 | 58 | 48 | 20 | 28 | 0.417 |
| coverage-aware score-gap posx4 | 1 | 66 | 56 | 20 | 36 | 0.357 |
| coverage-aware score-gap posx4 | 2 | 63 | 53 | 20 | 33 | 0.377 |
| precision-biased top-20 | 0 | 30 | 20 | 15 | 5 | 0.750 |
| precision-biased top-20 | 1 | 30 | 20 | 14 | 6 | 0.700 |
| precision-biased top-20 | 2 | 30 | 20 | 16 | 4 | 0.800 |
| fixed top-80 | 0 | 90 | 80 | 20 | 60 | 0.250 |
| fixed top-80 | 1 | 90 | 80 | 20 | 60 | 0.250 |
| fixed top-80 | 2 | 90 | 80 | 20 | 60 | 0.250 |

Aggregate support:

| method | selected unlabeled | hidden-positive selected | hidden-bad selected | aggregate purity |
|---|---:|---:|---:|---:|
| coverage-aware score-gap posx4 | 157 | 60 | 97 | 0.382 |
| precision-biased top-20 | 60 | 45 | 15 | 0.750 |
| fixed top-80 | 240 | 60 | 180 | 0.250 |

## Three-Seed Rollout

Top-20 per-seed success:

| seed | 5k | 10k | 15k | 20k |
|---:|---:|---:|---:|---:|
| 0 | 0.000 | 0.500 | 0.300 | 0.800 |
| 1 | 0.000 | 0.400 | 0.500 | 0.600 |
| 2 | 0.000 | 0.200 | 0.500 | 0.600 |

Posx4 per-seed success:

| seed | 5k | 10k | 15k | 20k |
|---:|---:|---:|---:|---:|
| 0 | 0.200 | 0.400 | 0.300 | 0.400 |
| 1 | 0.000 | 0.200 | 0.300 | 0.300 |
| 2 | 0.000 | 0.200 | 0.300 | 0.300 |

Top-80 per-seed success:

| seed | 5k | 10k | 15k | 20k |
|---:|---:|---:|---:|---:|
| 0 | 0.000 | 0.000 | 0.300 | 0.300 |
| 1 | 0.100 | 0.200 | 0.100 | 0.200 |
| 2 | 0.100 | 0.500 | 0.100 | 0.200 |

Aggregate success:

| method | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| top-20 mean | 0.000 | 0.367 | 0.433 | 0.667 |
| posx4 mean | 0.067 | 0.267 | 0.300 | 0.333 |
| fixed top-80 mean | 0.067 | 0.233 | 0.167 | 0.233 |
| top-20 minus posx4 mean | -0.067 | 0.100 | 0.133 | 0.333 |
| top-20 minus fixed top-80 mean | -0.067 | 0.133 | 0.267 | 0.433 |

## Interpretation

The balanced-split `4 x` labeled-positive coverage floor is not the right stress selector by itself. It recovers all 20 available hidden-positive unlabeled demos on all three classifier seeds, but under this 80% bad unlabeled pool it admits many low-confidence hidden-bad demos.

The selector score analysis shows the precision-biased top-20 rule is cleaner across seeds, selecting 45 hidden-positive and 15 hidden-bad demos in aggregate. Posx4 recovers all 60 hidden-positive demos across seeds, but it also selects 97 hidden-bad demos. Fixed top-80 selects 180 hidden-bad demos. In the matched three-seed policy check, top-20 reaches mean 0.667 success at 20k, compared with 0.333 for posx4 and 0.233 for fixed top-80.

The Robomimic story is now split by contamination regime: balanced data favors coverage-aware score-gap, while heavy contamination needs a precision-biased cap or a selector that adapts its purity/coverage tradeoff.
