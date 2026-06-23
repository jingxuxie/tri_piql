# Minari Tri-PIQL Smoke: `D4RL/pointmaze/large-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
Score steps: `800`.
Actor steps: `700`.
Classifier steps: `300`.
Evaluation episodes: `10`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.500 | 0.500 | 449.7 |
| weighted_bc_classifier | 0.500 | 0.500 | 525.8 |
| tri_piql_q_bc | 0.200 | 0.200 | 676.3 |
| tri_piql_score_awbc | 0.400 | 0.400 | 525.5 |

## Score Diagnostics

- Learned q pos/neg/unlabeled mean: `0.724` / `0.243` / `0.575`.
- Learned q bias: `-0.052`.
- Positive-vs-negative q AUC: `1.000`.
- Learned trajectory score gap: `119.712`.
- Unlabeled q vs label-score Spearman: `0.686`.
- Unlabeled q top/bottom quartile mean: `0.701` / `0.436`.
- Transition score pos/neg/unlabeled mean: `1.868` / `-4.670` / `-1.646`.

## Classifier Baseline Diagnostics

- Labeled accuracy: `0.912`.
- Positive/negative/unlabeled probability mean: `0.821` / `0.166` / `0.405`.

## Interpretation

- This is a short real-data smoke for the Tri-PIQL mechanism, not a final benchmark row.
- The score model uses positive-vs-negative trajectory ranking, signed good/bad transition constraints, latent unlabeled trajectory weights, and a random-action conservative term.
- `tri_piql_q_bc` tests whether latent trajectory weighting alone is useful before applying the score advantage exponent.
- The promoted comparison is `tri_piql_score_awbc` and `tri_piql_q_bc` against `weighted_bc_classifier` under the same split and rollout budget.
