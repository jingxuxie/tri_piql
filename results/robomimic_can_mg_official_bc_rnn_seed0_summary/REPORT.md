# Robomimic Can MG Sparse Seed-0 Stress Diagnostic

This is a one-seed diagnostic on the official Robomimic Can machine-generated sparse low-dimensional dataset. It is not a main positive result. It tests whether the Lift MG support-purification story also transfers to a much larger bad-dominated Can MG pool.

Protocol:

- Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`
- Inspection: `results/robomimic_inspection/can_mg_low_dim_sparse/REPORT.md`
- Demos: 3,900 total, 718 reward-positive, 3,182 reward-negative.
- Split: 10 labeled positives, 10 labeled negatives, 3,840 unlabeled train demos, 20 validation-positive starts.
- Unlabeled pool: 688 hidden-positive demos and 3,152 hidden-bad demos.
- Backbone: official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Training budget for policy rows: 200 epochs x 100 steps = 20k optimizer steps.
- Evaluation: 10 rollouts per checkpoint from held-out validation-positive initial states, horizon 400.

Artifacts:

- Pos-min setup only: `results/robomimic_can_mg_official_bc_rnn_posmin_seed0_setup/REPORT.md`
- Pos-p10 setup/eval: `results/robomimic_can_mg_official_bc_rnn_posp10_seed0_setup/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_posp10_seed0_eval/REPORT.md`
- Weighted sampler setup/eval: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed0_setup/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_weighted_prob_seed0_eval/REPORT.md`
- Adaptive masscap setup only: `results/robomimic_can_mg_official_bc_rnn_adaptive_masscap_seed0_setup/REPORT.md`
- Coverage-gap setup only: `results/robomimic_can_mg_official_bc_rnn_gap_seed0_setup/REPORT.md`
- Top160 setup/eval: `results/robomimic_can_mg_official_bc_rnn_top160_seed0_setup/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_top160_seed0_eval/REPORT.md`
- All-positive oracle setup/eval: `results/robomimic_can_mg_official_bc_rnn_allpositive_seed0_setup/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_allpositive_seed0_eval/REPORT.md`
- All-demo setup/eval: `results/robomimic_can_mg_official_bc_rnn_alltrain_seed0_setup/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_alltrain_seed0_eval/REPORT.md`

## Support Diagnostics

| source | train demos | selected unlabeled | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|---:|
| pos-min calibrated threshold | 1049 | 1039 | 485 | 554 | 0.467 |
| pos-p10 calibrated threshold | 724 | 714 | 378 | 336 | 0.529 |
| classifier probability weighted sampler | 3850 | 3840 | 688 | 3152 | 0.179 |
| adaptive masscap | 16 | 6 | 3 | 3 | 0.500 |
| coverage-gap posx4 max800 | 809 | 799 | 403 | 396 | 0.504 |
| top160 selected support | 170 | 160 | 113 | 47 | 0.706 |

The current hidden-label-free hard selectors do not fully calibrate on this dataset. Pos-min is too permissive because many hidden-bad demos score above the minimum labeled-positive score. Pos-p10 is a better threshold, selecting fewer false positives while retaining 378 hidden-positive demos. The existing adaptive masscap falls back to the score-gap cutoff and under-selects because classifier scores saturate near 1.0 at the top of the ranking.

The weighted sampler keeps every unlabeled demo, so its raw selected purity is just the bad-dominated unlabeled composition. Its useful signal is in weights: hidden-positive unlabeled demos have mean demo weight 0.885 versus 0.432 for hidden-bad demos.

## Policy Rollouts

| source | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| top160 selected support | 0.000 | 0.100 | 0.100 | 0.000 | 0.100 |
| pos-p10 calibrated threshold | 0.000 | 0.000 | 0.100 | 0.300 | 0.300 |
| classifier probability weighted sampler | 0.000 | 0.300 | 0.200 | 0.400 | 0.400 |
| all train positives | 0.000 | 0.000 | 0.100 | 0.400 | 0.400 |
| all train demos | 0.000 | 0.000 | 0.100 | 0.200 | 0.200 |

## Interpretation

Can MG sparse is a useful stress case, but not a paper-facing positive result yet. The all-positive oracle row reaches 0.400 at 20k, so the dataset is learnable with the same official backbone, but it is substantially weaker than paired Can. All-demo mixed cloning reaches 0.200 at 20k, confirming that the bad-dominated mixed log is harmful.

The hard selected-support rows do not yet close the oracle gap. Fixed top160 has better purity than the hidden-label-free thresholds but reaches only 0.100 best success, suggesting it is coverage-limited. Pos-p10 is a partial calibration fix: it is much broader, beats all-demo cloning at 20k (`0.300` vs `0.200`), and is closer to all-positive oracle support (`0.400`), but it is still not the strongest row.

The soft weighted sampler is strongest on this one-seed Can MG stress screen. It reaches 0.400 at 20k, matching the all-positive oracle and beating all-demo cloning. This is the opposite of paired Can/Lift, where hard selected support had the cleaner fixed-20k result. The likely explanation is that Can MG needs broad coverage; hard thresholds either under-cover or admit too many false positives as unweighted demonstrations, while the sampler can retain coverage and still bias updates toward high-score demos.

Research implication: keep the main robotics claim on paired Can and Lift MG, but treat Can MG as an important calibration stress diagnostic. Score ranking helps, but the right conversion from classifier scores to training data can be task-dependent: hard support is best in paired Can and Lift, while soft weighting is more promising on this large bad-dominated MG pool.
