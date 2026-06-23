# Official Robomimic 40p/80b Weighted BC Three-Seed Control

This report adds the soft classifier-probability weighted BC baseline to the intermediate Robomimic Can split with 40 hidden-positive and 80 hidden-bad unlabeled demos.

Protocol:

- Split: `results/robomimic_inspection/can_paired_low_dim_pos40_bad80/split_indices.json`
- Labels: 10 successful demos, 10 failed demos.
- Training support: 10 labeled positive demos plus all 120 unlabeled demos.
- Unlabeled weighting: demo-level classifier positive probability, floor 0.05, consumed by a `WeightedRandomSampler`.
- Seeds: 0, 1, 2.
- Backbone: official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Training budget: 200 epochs x 100 steps = 20k optimizer steps.
- Evaluation: 10 rollouts per checkpoint from held-out validation-positive initial states, horizon 400.

Artifacts:

- Setup directories: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed{0,1,2}_mlphead_setup`
- Training directories: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed{0,1,2}_mlphead_train`
- Evaluation directories: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_seed{0,1,2}_mlphead_eval`
- CSV summary: `results/robomimic_official_bc_rnn_weighted_prob_pos40_bad80_3seed_summary/summary.csv`

## Weighting Diagnostics

The weighted sampler does not hard-select support. It keeps every unlabeled demo, including all 80 hidden-bad demos, but samples hidden-positive demos with higher probability.

| seed | train demos | weighted unlabeled | hidden-positive unlabeled | hidden-bad unlabeled | raw unlabeled purity | mean demo weight | hidden-positive mean weight | hidden-bad mean weight |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 130 | 120 | 40 | 80 | 0.333 | 0.490 | 0.677 | 0.333 |
| 1 | 130 | 120 | 40 | 80 | 0.333 | 0.494 | 0.692 | 0.332 |
| 2 | 130 | 120 | 40 | 80 | 0.333 | 0.480 | 0.683 | 0.313 |
| mean | 130 | 120 | 40 | 80 | 0.333 | 0.488 | 0.684 | 0.326 |

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
| classifier probability weighted sampler | 0.267 +/- 0.125 | 0.600 +/- 0.163 | 0.700 +/- 0.082 | 0.567 +/- 0.047 |

Seed-level details:

| seed | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.400 | 0.800 | 0.800 | 0.500 | 0.800 |
| 1 | 0.300 | 0.600 | 0.600 | 0.600 | 0.600 |
| 2 | 0.100 | 0.400 | 0.700 | 0.600 | 0.700 |

## Interpretation

Weighted BC is a real baseline here, not a strawman. It has the best 10k mean in this comparison and is close to mass-capped adaptive at 15k.

Its weakness is fixed-budget endpoint stability. At 20k it is lower than mass-capped adaptive (`0.567` vs `0.733`) and top20 precision (`0.700`). The likely reason is visible in the support: all 80 hidden-bad demos remain in the sampler with nontrivial average weight (`0.326`), so the policy still trains on conflicting manipulation behavior.

The right paper-facing claim is therefore not that weighted BC is bad. Classifier scores help both soft weighting and hard selection. The stronger Can result is that hard, calibrated support selection gives the cleaner fixed-20k behavior in the intermediate contamination regime, while weighted BC is a competitive classifier-only baseline that should be included.
