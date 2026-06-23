# Minari Tri-PIQL Smoke: `D4RL/pointmaze/large-dense-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-dense-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
Score steps: `800`.
Actor steps: `700`.
Classifier steps: `300`.
Evaluation episodes: `10`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.500 | 42.861 | 580.7 |
| weighted_bc_classifier | 0.300 | 48.194 | 684.6 |
| tri_piql_q_bc | 0.100 | 51.389 | 727.1 |
| tri_piql_score_awbc | 0.100 | 43.648 | 732.2 |

## Score Diagnostics

- Learned q pos/neg/unlabeled mean: `0.720` / `0.406` / `0.482`.
- Learned q bias: `0.082`.
- Positive-vs-negative q AUC: `0.952`.
- Learned trajectory score gap: `33.140`.
- Unlabeled q vs label-score Spearman: `0.254`.
- Unlabeled q top/bottom quartile mean: `0.571` / `0.431`.
- Transition score pos/neg/unlabeled mean: `1.464` / `-0.444` / `0.253`.

## Classifier Baseline Diagnostics

- Labeled accuracy: `0.796`.
- Positive/negative/unlabeled probability mean: `0.673` / `0.307` / `0.454`.

## Interpretation

- This is a short real-data smoke for the Tri-PIQL mechanism, not a final benchmark row.
- The score model uses positive-vs-negative trajectory ranking, signed good/bad transition constraints, latent unlabeled trajectory weights, and a random-action conservative term.
- `tri_piql_q_bc` tests whether latent trajectory weighting alone is useful before applying the score advantage exponent.
- The promoted comparison is `tri_piql_score_awbc` and `tri_piql_q_bc` against `weighted_bc_classifier` under the same split and rollout budget.
