# Minari Tri-PIQL Smoke: `D4RL/pointmaze/large-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
Score steps: `2`.
Actor steps: `2`.
Classifier steps: `2`.
Evaluation episodes: `1`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.000 | 0.000 | 5.0 |
| weighted_bc_classifier | 0.000 | 0.000 | 5.0 |
| tri_piql_q_bc | 0.000 | 0.000 | 5.0 |
| tri_piql_score_awbc | 0.000 | 0.000 | 5.0 |

## Score Diagnostics

- Learned q pos/neg/unlabeled mean: `0.453` / `0.557` / `0.487`.
- Learned q bias: `-0.000`.
- Positive-vs-negative q AUC: `0.342`.
- Learned trajectory score gap: `-0.096`.
- Unlabeled q vs label-score Spearman: `-0.022`.
- Unlabeled q top/bottom quartile mean: `0.482` / `0.488`.
- Transition score pos/neg/unlabeled mean: `0.005` / `0.006` / `0.005`.

## Classifier Baseline Diagnostics

- Labeled accuracy: `0.488`.
- Positive/negative/unlabeled probability mean: `0.497` / `0.497` / `0.497`.

## Interpretation

- This is a short real-data smoke for the Tri-PIQL mechanism, not a final benchmark row.
- The score model uses positive-vs-negative trajectory ranking, signed good/bad transition constraints, latent unlabeled trajectory weights, and a random-action conservative term.
- `tri_piql_q_bc` tests whether latent trajectory weighting alone is useful before applying the score advantage exponent.
- The promoted comparison is `tri_piql_score_awbc` and `tri_piql_q_bc` against `weighted_bc_classifier` under the same split and rollout budget.
