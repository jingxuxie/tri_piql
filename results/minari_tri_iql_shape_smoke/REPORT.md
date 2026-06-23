# Minari Tri-PIQL IQL Smoke: `D4RL/pointmaze/large-dense-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-dense-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
IQL/reward steps: `2`.
Actor steps: `2`.
Classifier steps: `2`.
Evaluation episodes: `1`.
Trajectory reduction: `sum`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.000 | 0.001 | 5.0 |
| weighted_bc_classifier | 0.000 | 0.001 | 5.0 |
| tri_iql_awbc_raw | 0.000 | 0.001 | 5.0 |
| tri_iql_awbc_norm | 0.000 | 0.001 | 5.0 |
| tri_iql_awbc_topq | 0.000 | 0.001 | 5.0 |
| tri_iql_awbc_pos_only | 0.000 | 0.001 | 5.0 |

## V/Q Diagnostics

- Learned q pos/neg/unlabeled mean: `0.471` / `0.573` / `0.489`.
- Positive-vs-negative q AUC: `0.375`.
- Learned reward trajectory gap: `-4.607`.
- Unlabeled q vs label-score Spearman: `-0.137`.
- Raw advantage pos/neg/unlabeled mean: `0.019` / `0.020` / `0.027`.
- Normalized actor weight pos/unlabeled mean: `1.416` / `0.735`.
- Top-q actor threshold/kept fraction: `0.624` / `0.256`.

## Classifier Baseline Diagnostics

- Labeled accuracy: `0.515`.
- Positive/negative/unlabeled probability mean: `0.498` / `0.497` / `0.497`.

## Interpretation

- This is a bounded real-data smoke for adding IQL-style V/Q structure to Tri-PIQL.
- `tri_iql_awbc_raw` uses raw Q-V advantages; `tri_iql_awbc_norm` normalizes advantages before actor weighting.
- `tri_iql_awbc_topq` keeps only top-quartile unlabeled trajectories by learned q; `tri_iql_awbc_pos_only` tests whether the advantage model helps without unlabeled data.
- The relevant comparison is against BC-positive and classifier-weighted BC under the same split and rollout budget.
