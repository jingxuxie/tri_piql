# Robomimic Can MG Shuffle42 Router Branch Check

This is a seed-0 check of the hidden-free router's Can MG soft/hard decision boundary on a shuffled Can MG sparse split.

Split: `results/robomimic_inspection/can_mg_low_dim_sparse_shuffle42/split_indices.json`.
Selector analysis: `results/robomimic_selector_score_analysis_can_mg_shuffle42/REPORT.md`.
Policy backbone: official Robomimic BC-RNN-GMM.
Evaluation: 10 rollouts per checkpoint, held-out validation-positive initial states, horizon 400, CUDA.

## Router Decision

The current router does **not** choose the soft branch on this shuffled split. The unlabeled plateau above score `0.95` is only `312.7` demos, below the soft floor of `400`, so the rule selects `hard_pos_min_threshold`.

This is different from the original Can MG split, where the same rule selected soft weighting because the plateau count was `652.3`.

## Support And Weights

| source | train demos | selected/weighted unlabeled | hidden positive | hidden bad | purity | hidden-positive mean weight | hidden-bad mean weight |
|---|---:|---:|---:|---:|---:|---:|---:|
| hard pos-min | 659 | 649 | 414 | 235 | 0.638 |  |  |
| soft weighted counterfactual | 3850 | 3840 | 688 | 3152 | 0.179 | 0.861 | 0.318 |

## Seed-0 Policy Results

| source | 5k | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|
| hard pos-min | 0.000 | 0.000 | 0.200 | 0.100 | 0.200 |
| soft weighted counterfactual | 0.000 | 0.100 | 0.100 | 0.100 | 0.100 |

## Interpretation

- The soft-branch trigger is not stable under this Can MG split shuffle: the router flips from soft weighted to hard `pos_min`.
- The seed-0 policy check does not show a soft-weighting rescue on this split. Both branches are weak, with hard `pos_min` only slightly better at its best checkpoint.
- This is a useful fragility result for the router: the score model still separates labeled positives from negatives and gives hidden positives much higher soft weights, but the fixed absolute plateau threshold is too brittle to support a strong method claim.
- The next router iteration should use a more robust score-shape or validation proxy before spending on more Can MG seeds.
