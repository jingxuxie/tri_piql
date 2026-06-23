# Official Robomimic Coverage-Aware Score-Gap Summary

This report summarizes the matched official Robomimic BC-RNN-GMM comparison on Robomimic Can paired low-dimensional data.

The coverage-aware score-gap selector is now parameterized as a hidden-label-free label-budget rule: select a score-gap prefix, but require at least `4 x` the number of labeled-positive demos. With 10 labeled-positive demos, this gives the same effective floor as the earlier `--gap-select-min-unlabeled-demos 40` setting.

Protocol:

- Labels: 10 successful demos, 10 failed demos, 160 unlabeled demos.
- Backbone: official Robomimic BC-RNN-GMM, actor MLP head `1024,1024`, sequence length 10.
- Training budget: 200 epochs x 100 steps = 20k optimizer steps.
- Checkpoints: 5k, 10k, 15k, 20k optimizer steps.
- Evaluation: 10 rollouts per checkpoint from held-out validation-positive initial states, horizon 400.

Artifacts:

- Coverage-aware seed 0: `results/robomimic_official_bc_rnn_gap_min40_seed0_mlphead_eval/REPORT.md`
- Coverage-aware seed 1: `results/robomimic_official_bc_rnn_gap_min40_seed1_mlphead_eval/REPORT.md`
- Coverage-aware seed 2: `results/robomimic_official_bc_rnn_gap_min40_seed2_mlphead_eval/REPORT.md`
- Label-budget-rule setup seed 0: `results/robomimic_official_bc_rnn_gap_posx4_seed0_mlphead_setup/REPORT.md`
- Label-budget-rule setup seed 1: `results/robomimic_official_bc_rnn_gap_posx4_seed1_mlphead_setup/REPORT.md`
- Label-budget-rule setup seed 2: `results/robomimic_official_bc_rnn_gap_posx4_seed2_mlphead_setup/REPORT.md`
- Fixed top-80 seed 0: `results/robomimic_official_bc_rnn_top80_seed0_mlphead_eval/REPORT.md`
- Fixed top-80 seed 1: `results/robomimic_official_bc_rnn_top80_seed1_mlphead_eval/REPORT.md`
- Fixed top-80 seed 2: `results/robomimic_official_bc_rnn_top80_seed2_mlphead_eval/REPORT.md`
- Current adaptive selector summary: `results/robomimic_adaptive_masscap_selector_summary/REPORT.md`
- Positive-count selector sweep: `results/robomimic_adaptive_selector_sweep_pos_count/REPORT.md`

The `posx4` setup artifacts reproduce the exact same selected demo IDs as the evaluated `min40` runs for seeds 0, 1, and 2, while using distinct HDF5 mask keys:

| seed | same selected demos as min40 | effective min selected unlabeled demos | train filter key |
|---:|---|---:|---|
| 0 | yes | 40 | `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed0_train` |
| 1 | yes | 40 | `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed1_train` |
| 2 | yes | 40 | `tri_positive_plus_classifier_gap_unlabeled_demos_posx4_max80_seed2_train` |

## Support Selection

| method | seed | train demos | selected unlabeled | hidden-positive selected | hidden-bad selected | purity |
|---|---:|---:|---:|---:|---:|---:|
| coverage-aware score-gap | 0 | 83 | 73 | 67 | 6 | 0.918 |
| coverage-aware score-gap | 1 | 55 | 45 | 45 | 0 | 1.000 |
| coverage-aware score-gap | 2 | 76 | 66 | 65 | 1 | 0.985 |
| fixed top-80 | 0 | 90 | 80 | 72 | 8 | 0.900 |
| fixed top-80 | 1 | 90 | 80 | 70 | 10 | 0.875 |
| fixed top-80 | 2 | 90 | 80 | 74 | 6 | 0.925 |

Aggregate support:

| method | selected unlabeled | hidden-positive selected | hidden-bad selected | aggregate purity |
|---|---:|---:|---:|---:|
| coverage-aware score-gap | 184 | 177 | 7 | 0.962 |
| fixed top-80 | 240 | 216 | 24 | 0.900 |

## Rollout Success

Per-seed success:

| method | seed | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|---:|
| coverage-aware score-gap | 0 | 0.100 | 0.700 | 0.800 | 0.900 |
| coverage-aware score-gap | 1 | 0.200 | 0.800 | 0.900 | 0.900 |
| coverage-aware score-gap | 2 | 0.100 | 0.900 | 0.900 | 0.900 |
| fixed top-80 | 0 | 0.300 | 0.700 | 0.700 | 0.700 |
| fixed top-80 | 1 | 0.200 | 0.800 | 0.800 | 0.900 |
| fixed top-80 | 2 | 0.200 | 0.600 | 0.700 | 0.900 |

Three-seed mean success:

| method | 5k | 10k | 15k | 20k |
|---|---:|---:|---:|---:|
| coverage-aware score-gap | 0.133 | 0.800 | 0.867 | 0.900 |
| fixed top-80 | 0.233 | 0.700 | 0.733 | 0.833 |

## Interpretation

Coverage-aware score-gap with the `4 x` labeled-positive coverage floor is the current best Robomimic selector. It is not better at the earliest 5k checkpoint, but it has better mean success at 10k, 15k, and 20k while selecting substantially fewer hidden-bad demos than fixed top-80.

The important method lesson is purity plus coverage. Pure largest-gap selection failed on seed 2 because it selected only 9 unlabeled demos; fixed top-80 fixed that failure by adding coverage but admitted more hidden-bad support. The min40 score-gap rule keeps most of the coverage benefit while reducing contamination.

This is a stronger paper-facing story than "weighted BC is best": scarce positive and negative labels can calibrate unlabeled support selection, but the selector must avoid both contamination and under-coverage.

Next research question: run seeds 1 and 2 for the 40 hidden-positive / 80 hidden-bad intermediate comparison. Seed 0 now supports the mass-capped selector: it keeps this coverage mode on the balanced split, switches to precision mode under heavier contamination, and uses a mass cap when a score-gap cut over-expands support.
