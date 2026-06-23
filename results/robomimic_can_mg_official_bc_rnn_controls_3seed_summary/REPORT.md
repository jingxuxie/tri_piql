# Robomimic Can MG Matched Controls Three-Seed Summary

This report summarizes the matched three-seed official Robomimic BC-RNN-GMM controls for the Can MG sparse stress split.

Dataset: `data/robomimic/v1.5/can/mg/low_dim_sparse_v15.hdf5`.

Split: `results/robomimic_inspection/can_mg_low_dim_sparse/split_indices.json`.

Protocol:

- 10 labeled reward-positive demos and 10 labeled reward-negative demos.
- 3,840 unlabeled train demos: 688 hidden-positive and 3,152 hidden-bad.
- Official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- 20,000 optimizer steps, saved at 5k / 10k / 15k / 20k.
- Evaluation uses 10 held-out reward-positive Can initial states and horizon 400.

Artifacts:

- Weighted sampler summary: `results/robomimic_can_mg_official_bc_rnn_weighted_prob_3seed_summary/REPORT.md`
- Seed 0 one-seed controls: `results/robomimic_can_mg_official_bc_rnn_seed0_summary/REPORT.md`
- All-positive seeds 1/2 evals: `results/robomimic_can_mg_official_bc_rnn_allpositive_seed1_eval/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_allpositive_seed2_eval/REPORT.md`
- All-demo seeds 1/2 evals: `results/robomimic_can_mg_official_bc_rnn_alltrain_seed1_eval/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_alltrain_seed2_eval/REPORT.md`
- Pos-p10 seeds 1/2 evals: `results/robomimic_can_mg_official_bc_rnn_posp10_seed1_eval/REPORT.md`, `results/robomimic_can_mg_official_bc_rnn_posp10_seed2_eval/REPORT.md`

## Support

| source | train demos | unlabeled in policy | hidden positive | hidden bad | support purity | hidden-positive mean weight | hidden-bad mean weight |
|---|---:|---:|---:|---:|---:|---:|---:|
| classifier probability weighted sampler | 3850 | 3840 | 688 | 3152 | 0.179 | 0.878 | 0.419 |
| all train positives | 698 | 688 | 688 | 0 | 1.000 |  |  |
| all train demos | 3860 | 3840 | 688 | 3152 | 0.179 |  |  |
| pos-p10 calibrated threshold | 783 | 773 | 416 | 357 | 0.538 |  |  |

The pos-p10 hard threshold is much purer than the full mixed pool, but it still admits many hidden-bad demos and removes about 272 hidden-positive demos on average. The weighted sampler keeps full coverage and gives hidden-positive unlabeled demos about twice the mean sampling weight of hidden-bad demos.

## Policy Results

Success over 10 held-out reward-positive starts:

| source | seeds | 5k | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|---:|
| classifier probability weighted sampler | 3 | 0.000 | 0.133 | 0.200 | 0.333 | 0.367 |
| all train positives | 3 | 0.000 | 0.033 | 0.133 | 0.200 | 0.233 |
| all train demos | 3 | 0.000 | 0.000 | 0.200 | 0.100 | 0.233 |
| pos-p10 calibrated threshold | 3 | 0.000 | 0.000 | 0.100 | 0.167 | 0.167 |

## Interpretation

The matched controls change the Can MG diagnostic in an important way:

- Weighted sampling is the best matched three-seed Can MG row at the fixed 20k endpoint: `0.333` versus all-positive `0.200`, pos-p10 `0.167`, and all-demo `0.100`.
- Weighted sampling also has the best best-per-seed mean: `0.367` versus `0.233` for all-positive and all-demo, and `0.167` for pos-p10.
- All-demo cloning remains weak, so the bad-dominated mixed log is harmful even with the official sequence backbone.
- The hard pos-p10 threshold purifies the pool but loses too much coverage for this split.

This is diagnostic evidence that broad soft weighting can beat both naive mixed cloning and the current hard-support conversion when Can MG has a large high-score plateau. It should still not be promoted to a main benchmark claim by itself: absolute success is modest, each checkpoint uses 10 eval episodes, and the hard/soft converter is not yet a hidden-label-free method.
