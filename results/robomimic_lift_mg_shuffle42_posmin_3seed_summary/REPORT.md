# Robomimic Lift MG Shuffle42 Pos-Min Validation

This is a shuffled-split validation of the hidden-free router's hard `pos_min` branch on Robomimic Lift MG sparse.

Split: `results/robomimic_inspection/lift_mg_low_dim_sparse_shuffle42/split_indices.json`.
Selector analysis: `results/robomimic_lift_mg_selector_score_analysis_shuffle42/REPORT.md`.
Policy backbone: official Robomimic BC-RNN-GMM.
Evaluation: 10 rollouts per checkpoint, held-out validation-positive initial states, horizon 150, CUDA.

## Router Decision

The hidden-free router chooses `hard_pos_min_threshold`: labeled-positive p10 is high (`0.922`) and the saturated-score plateau is modest (`159.3` demos, below the soft-weighting floor of `400`).

Actual setup support over the three policy seeds:

| train demos | selected unlabeled | hidden positive | hidden bad | purity |
|---:|---:|---:|---:|---:|
| 209.3 +/- 3.8 | 199.3 +/- 3.8 | 185.0 +/- 4.4 | 14.3 +/- 1.2 | 0.928 +/- 0.006 |

## Policy Results

Success rate over 10 held-out reward-positive Lift starts:

| seed | 5k | 10k | 15k | 20k | best |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.200 | 0.400 | 0.300 | 0.400 | 0.400 |
| 1 | 0.200 | 0.600 | 0.600 | 0.800 | 0.800 |
| 2 | 0.000 | 0.200 | 0.300 | 0.600 | 0.600 |
| mean | 0.133 | 0.400 | 0.400 | 0.600 | 0.600 |
| std | 0.115 | 0.200 | 0.173 | 0.200 | 0.200 |

## Interpretation

- The router's hard `pos_min` branch transfers to a new Lift MG split: it keeps high-purity support and reaches `0.600` fixed-20k mean success.
- The validation is weaker than the original Lift split (`0.600` versus `0.667` at fixed 20k, and `0.600` versus `0.700` best-per-seed), so Lift remains sensitive to split and validation starts.
- This is useful branch-validation evidence, but it should strengthen the caveat around checkpoint and split robustness rather than be used as a bigger headline result.
