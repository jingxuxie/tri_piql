# Robomimic Can Shuffle42 Adaptive Masscap Validation

This is a held-out-style validation of the hidden-free router's hard-support branch on a new shuffled 40 positive / 80 bad paired-Can split.

Split: `results/robomimic_inspection/can_paired_low_dim_pos40_bad80_shuffle42/split_indices.json`.
Selector analysis: `results/robomimic_selector_score_analysis_pos40_bad80_shuffle42/REPORT.md`.
Policy backbone: official Robomimic BC-RNN-GMM.
Evaluation: 10 rollouts per checkpoint, held-out validation-positive initial states, horizon 400, CUDA.

## Router Decision

The hidden-free router chooses `hard_adaptive_masscap` because the unlabeled score distribution has no large saturated plateau: only `3.0` unlabeled demos score at least `0.95`, far below the soft-weighting floor of `400`.

Support audit over seeds:

| selected unlabeled | hidden positive | hidden bad | purity | rule mode |
|---:|---:|---:|---:|---|
| 63.3 +/- 2.5 | 39.3 +/- 1.2 | 24.0 +/- 1.7 | 0.621 +/- 0.014 | adaptive_masscap_coverage_gap |

## Policy Results

| seed | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.300 | 0.700 | 0.700 | 0.700 | 0.700 |
| 1 | 0.100 | 0.800 | 0.800 | 0.600 | 0.800 |
| 2 | 0.100 | 0.800 | 0.700 | 0.600 | 0.800 |
| mean | 0.167 | 0.767 | 0.733 | 0.633 | 0.767 |
| std | 0.115 | 0.058 | 0.058 | 0.058 | 0.058 |

## Interpretation

- The router's hard branch transfers to a new shuffled 40p/80b split without using hidden unlabeled labels in the decision.
- The fixed 20k endpoint is positive but lower than the original 40p/80b split (`0.633` versus `0.733`), while the 10k and 15k means remain strong (`0.767` and `0.733`).
- This should be treated as validation evidence for the hard branch, not as a new main benchmark row or a claim that hard support always beats soft weighting.
