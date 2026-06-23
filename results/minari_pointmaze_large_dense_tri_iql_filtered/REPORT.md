# Minari Tri-PIQL IQL Smoke: `D4RL/pointmaze/large-dense-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-dense-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
IQL/reward steps: `1000`.
Actor steps: `700`.
Classifier steps: `300`.
Evaluation episodes: `10`.
Trajectory reduction: `sum`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.500 | 41.841 | 581.4 |
| weighted_bc_classifier | 0.300 | 46.758 | 660.8 |
| tri_iql_awbc_raw | 0.100 | 29.309 | 726.7 |
| tri_iql_awbc_norm | 0.100 | 32.140 | 727.6 |
| tri_iql_awbc_topq | 0.000 | 39.706 | 800.0 |
| tri_iql_awbc_pos_only | 0.100 | 28.948 | 727.8 |

## V/Q Diagnostics

- Learned q pos/neg/unlabeled mean: `0.760` / `0.371` / `0.475`.
- Positive-vs-negative q AUC: `0.983`.
- Learned reward trajectory gap: `753.088`.
- Unlabeled q vs label-score Spearman: `0.299`.
- Raw advantage pos/neg/unlabeled mean: `1.263` / `-0.762` / `0.104`.
- Normalized actor weight pos/unlabeled mean: `1.970` / `0.586`.
- Top-q actor threshold/kept fraction: `0.621` / `0.320`.

## Classifier Baseline Diagnostics

- Labeled accuracy: `0.796`.
- Positive/negative/unlabeled probability mean: `0.673` / `0.307` / `0.454`.

## Interpretation

- This is a bounded real-data smoke for adding IQL-style V/Q structure to Tri-PIQL.
- `tri_iql_awbc_raw` uses raw Q-V advantages; `tri_iql_awbc_norm` normalizes advantages before actor weighting.
- `tri_iql_awbc_topq` keeps only top-quartile unlabeled trajectories by learned q; `tri_iql_awbc_pos_only` tests whether the advantage model helps without unlabeled data.
- The relevant comparison is against BC-positive and classifier-weighted BC under the same split and rollout budget.
