# Official Robomimic Heavy-Contamination Three-Selector Check

This report compares precision-biased top-20 selection, coverage-aware score-gap posx4, and fixed top-80 selection on the heavy-contamination Robomimic Can stress split, using three official BC-RNN-GMM seeds for each selector. Top-20 is also the precision branch chosen by the hidden-label-free mass-capped adaptive selector on this split.

Protocol:

- Split: `results/robomimic_inspection/can_paired_low_dim_stress_pos20_bad80/split_indices.json`
- Labels: 10 successful demos, 10 failed demos.
- Unlabeled stress pool: 20 hidden-positive demos, 80 hidden-bad demos.
- Selectors:
  - Top-20: top 20 unlabeled demos by mean trajectory classifier score.
  - Posx4: score-gap with a minimum support floor of `4 x labeled_positive_demo_count`.
  - Top-80: fixed top 80 unlabeled demos by mean trajectory classifier score.
- Mass-capped adaptive rule: estimates unlabeled positive-demo mass from classifier scores without hidden labels. On this split the estimates are 32.6-35.9 demos, below the effective coverage floor of 40, so it chooses the top-20 precision branch.
- Backbone: official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Training budget: 200 epochs x 100 steps = 20k optimizer steps.
- Evaluation: 10 rollouts per checkpoint from held-out validation-positive initial states, horizon 400.

Artifacts:

- Selector analysis: `results/robomimic_selector_score_analysis_stress_p20_b80/REPORT.md`
- Current adaptive selector summary: `results/robomimic_adaptive_masscap_selector_summary/REPORT.md`
- Positive-count selector sweep: `results/robomimic_adaptive_selector_sweep_pos_count/REPORT.md`
- Top-20 seed 0 setup/eval:
  - `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed0_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Top-20 seed 1 setup/eval:
  - `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed1_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Top-20 seed 2 setup/eval:
  - `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed2_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top20_stress_p20_b80_seed2_mlphead_eval/REPORT.md`
- Posx4 seed 0 setup/eval:
  - `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed0_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Posx4 seed 1 setup/eval:
  - `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed1_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Posx4 seed 2 setup/eval:
  - `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed2_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_gap_posx4_stress_p20_b80_seed2_mlphead_eval/REPORT.md`
- Top-80 seed 0 setup/eval:
  - `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed0_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed0_mlphead_eval/REPORT.md`
- Top-80 seed 1 setup/eval:
  - `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed1_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed1_mlphead_eval/REPORT.md`
- Top-80 seed 2 setup/eval:
  - `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed2_mlphead_setup/REPORT.md`
  - `results/robomimic_official_bc_rnn_top80_stress_p20_b80_seed2_mlphead_eval/REPORT.md`

## Support Selection

| method | seed | train demos | selected unlabeled | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|---:|---:|
| top-20 | 0 | 30 | 20 | 15 | 5 | 0.750 |
| top-20 | 1 | 30 | 20 | 14 | 6 | 0.700 |
| top-20 | 2 | 30 | 20 | 16 | 4 | 0.800 |
| posx4 | 0 | 58 | 48 | 20 | 28 | 0.417 |
| posx4 | 1 | 66 | 56 | 20 | 36 | 0.357 |
| posx4 | 2 | 63 | 53 | 20 | 33 | 0.377 |
| top-80 | 0 | 90 | 80 | 20 | 60 | 0.250 |
| top-80 | 1 | 90 | 80 | 20 | 60 | 0.250 |
| top-80 | 2 | 90 | 80 | 20 | 60 | 0.250 |

Aggregate support:

| method | selected unlabeled | hidden-positive selected | hidden-bad selected | aggregate purity |
|---|---:|---:|---:|---:|
| top-20 | 60 | 45 | 15 | 0.750 |
| posx4 | 157 | 60 | 97 | 0.382 |
| top-80 | 240 | 60 | 180 | 0.250 |

## Rollout Success

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
| top-20 population std | 0.000 | 0.125 | 0.094 | 0.094 |
| posx4 mean | 0.067 | 0.267 | 0.300 | 0.333 |
| posx4 population std | 0.094 | 0.094 | 0.000 | 0.047 |
| top-80 mean | 0.067 | 0.233 | 0.167 | 0.233 |
| top-80 population std | 0.047 | 0.205 | 0.094 | 0.047 |
| top-20 minus posx4 mean | -0.067 | 0.100 | 0.133 | 0.333 |
| top-20 minus top-80 mean | -0.067 | 0.133 | 0.267 | 0.433 |

## Interpretation

The mass-capped adaptive selector chooses its top-20 precision branch on this stress split, and that branch gives the strongest matched result under 80% bad unlabeled contamination. It reaches mean 0.667 success at 20k, versus 0.333 for posx4 and 0.233 for fixed top-80. All three top-20 seeds reach at least 0.600 by 20k.

The mechanism is support contamination. Posx4 recovers all 20 available hidden-positive demos on every seed, but it also admits 97 hidden-bad demos in aggregate. Fixed top-80 admits 180 hidden-bad demos. Top-20 gives up some hidden-positive coverage but cuts hidden-bad selection to 15 demos in aggregate, which is better for this high-contamination regime.

The method implication is that the selector should adapt its purity/coverage tradeoff to the unlabeled contamination regime. The balanced split has enough estimated positive mass for coverage-aware score-gap; this heavy-contamination split falls below that mass threshold and uses the precision branch.
