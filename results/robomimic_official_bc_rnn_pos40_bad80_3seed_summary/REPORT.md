# Official Robomimic 40p/80b Three-Seed Selector Check

This report compares the current mass-capped adaptive selector against original coverage-gap and top20 precision on the intermediate Robomimic Can split with 40 hidden-positive and 80 hidden-bad unlabeled demos.

Protocol:

- Split: `results/robomimic_inspection/can_paired_low_dim_pos40_bad80/split_indices.json`
- Labels: 10 successful demos, 10 failed demos.
- Unlabeled pool: 40 hidden-positive demos, 80 hidden-bad demos.
- Seeds: 0, 1, 2.
- Backbone: official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Training budget: 200 epochs x 100 steps = 20k optimizer steps.
- Evaluation: 10 rollouts per checkpoint from held-out validation-positive initial states, horizon 400.

Artifacts:

- Selector analysis: `results/robomimic_selector_score_analysis_pos40_bad80/REPORT.md`
- Seed-0 snapshot: `results/robomimic_official_bc_rnn_pos40_bad80_seed0_summary/REPORT.md`
- Mass-capped setup/eval directories: `results/robomimic_official_bc_rnn_adaptive_masscap_pos40_bad80_seed{0,1,2}_mlphead_{setup,eval}`
- Coverage-gap setup/eval directories: `results/robomimic_official_bc_rnn_gap_posx4_pos40_bad80_seed{0,1,2}_mlphead_{setup,eval}`
- Top20 setup/eval directories: `results/robomimic_official_bc_rnn_top20_pos40_bad80_seed{0,1,2}_mlphead_{setup,eval}`
- Positive-only NN top40 setup/eval directories: `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_seed{0,1,2}_mlphead_{setup,eval}`
- Classifier probability weighted-sampler setup/eval directories: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed{0,1,2}_mlphead_{setup,eval}`

## Support Selection

| method | train demos mean | selected unlabeled mean | hidden-positive mean | hidden-bad mean | purity mean | selection rules |
|---|---:|---:|---:|---:|---:|---|
| mass-capped adaptive | 60.0 | 50.0 | 36.3 | 13.7 | 0.728 | adaptive_masscap_top_estimated_mass |
| classifier probability weighted sampler | 130.0 | 120.0 | 40.0 | 80.0 | 0.333 | demo_probability_weighting |
| coverage-gap | 84.0 | 74.0 | 40.0 | 34.0 | 0.541 | score_gap |
| top20 precision | 30.0 | 20.0 | 19.7 | 0.3 | 0.983 | fixed_top |
| positive-only NN top40 | 50.0 | 40.0 | 31.0 | 9.0 | 0.775 | positive_nn_top |

The weighted sampler does not hard-select support. Its purity row is the raw unlabeled composition; mean hidden-positive demo weight is 0.684 versus 0.326 for hidden-bad demos.

## Rollout Success

Mean over seeds:

| method | 5k | 10k | 15k | 20k | best-per-seed mean |
|---|---:|---:|---:|---:|---:|
| mass-capped adaptive | 0.167 | 0.500 | 0.733 | 0.733 | 0.767 |
| classifier probability weighted sampler | 0.267 | 0.600 | 0.700 | 0.567 | 0.700 |
| coverage-gap | 0.167 | 0.333 | 0.567 | 0.600 | 0.667 |
| top20 precision | 0.033 | 0.567 | 0.667 | 0.700 | 0.700 |
| positive-only NN top40 | 0.167 | 0.433 | 0.533 | 0.633 | 0.767 |

Mean +/- population standard deviation:

| method | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| mass-capped adaptive | 0.167 +/- 0.125 | 0.500 +/- 0.082 | 0.733 +/- 0.047 | 0.733 +/- 0.094 |
| classifier probability weighted sampler | 0.267 +/- 0.125 | 0.600 +/- 0.163 | 0.700 +/- 0.082 | 0.567 +/- 0.047 |
| coverage-gap | 0.167 +/- 0.094 | 0.333 +/- 0.236 | 0.567 +/- 0.170 | 0.600 +/- 0.082 |
| top20 precision | 0.033 +/- 0.047 | 0.567 +/- 0.047 | 0.667 +/- 0.047 | 0.700 +/- 0.082 |
| positive-only NN top40 | 0.167 +/- 0.170 | 0.433 +/- 0.249 | 0.533 +/- 0.189 | 0.633 +/- 0.170 |

Seed-level details:

| method | seed | selected | hidden-positive | hidden-bad | purity | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| mass-capped adaptive | 0 | 50 | 36 | 14 | 0.720 | 0.300 | 0.500 | 0.800 | 0.800 | 0.800 |
| mass-capped adaptive | 1 | 52 | 36 | 16 | 0.692 | 0.200 | 0.600 | 0.700 | 0.600 | 0.700 |
| mass-capped adaptive | 2 | 48 | 37 | 11 | 0.771 | 0.000 | 0.400 | 0.700 | 0.800 | 0.800 |
| classifier probability weighted sampler | 0 | 120 | 40 | 80 | 0.333 | 0.400 | 0.800 | 0.800 | 0.500 | 0.800 |
| classifier probability weighted sampler | 1 | 120 | 40 | 80 | 0.333 | 0.300 | 0.600 | 0.600 | 0.600 | 0.600 |
| classifier probability weighted sampler | 2 | 120 | 40 | 80 | 0.333 | 0.100 | 0.400 | 0.700 | 0.600 | 0.700 |
| coverage-gap | 0 | 73 | 40 | 33 | 0.548 | 0.100 | 0.500 | 0.800 | 0.600 | 0.800 |
| coverage-gap | 1 | 77 | 40 | 37 | 0.519 | 0.300 | 0.000 | 0.500 | 0.500 | 0.500 |
| coverage-gap | 2 | 72 | 40 | 32 | 0.556 | 0.100 | 0.500 | 0.400 | 0.700 | 0.700 |
| top20 precision | 0 | 20 | 19 | 1 | 0.950 | 0.000 | 0.600 | 0.700 | 0.700 | 0.700 |
| top20 precision | 1 | 20 | 20 | 0 | 1.000 | 0.100 | 0.500 | 0.600 | 0.600 | 0.600 |
| top20 precision | 2 | 20 | 20 | 0 | 1.000 | 0.000 | 0.600 | 0.700 | 0.800 | 0.800 |
| positive-only NN top40 | 0 | 40 | 31 | 9 | 0.775 | 0.400 | 0.700 | 0.800 | 0.400 | 0.800 |
| positive-only NN top40 | 1 | 40 | 31 | 9 | 0.775 | 0.000 | 0.500 | 0.400 | 0.800 | 0.800 |
| positive-only NN top40 | 2 | 40 | 31 | 9 | 0.775 | 0.100 | 0.100 | 0.400 | 0.700 | 0.700 |

## Interpretation

The three-seed 40p/80b result supports the mass-cap refinement, but with useful caveats. Soft weighted BC is not weak: it has the best 10k mean and is close to mass-capped adaptive at 15k. Its limitation is fixed-budget endpoint stability; at 20k it is lower than mass-capped adaptive (`0.567` vs `0.733`) because it keeps all 80 hidden-bad demos in the sampler with nontrivial average weight.

Top20 precision is also very competitive because it selects nearly pure hidden-positive support, and it has a strong 20k mean. Its limitation is coverage: it uses only about half of the hidden-positive demos available in this split. Coverage-gap has the opposite problem. It recovers every hidden-positive demo, but admits 34 hidden-bad demos on average and is weaker by 15k/20k.

The positive-only NN top40 control is strong: without labeled bad demos, it ties masscap on best-per-seed mean. But it is worse at the fixed 10k/15k/20k checkpoints and has higher variance, so it weakens any claim that bad labels are strictly necessary while still supporting a stability claim for bad-aware adaptive selection.

Mass-capped adaptive selection takes the intended middle ground. It admits far fewer hidden-bad demos than coverage-gap or weighted sampling, uses substantially more hidden-positive support than top20 or positive-only NN top40, and has the best 15k and 20k mean success in this intermediate contamination regime. This strengthens the paper-facing selector story: classifier scores help soft weighting too, but intermediate contamination benefits from converting those scores into calibrated hard support.
