# Minari BC Smoke: `D4RL/pointmaze/large-dense-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-dense-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
Train steps per actor: `600`.
Classifier steps: `300`.
Evaluation episodes: `10`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.300 | 51.021 | 675.1 |
| bc_pos_unlabeled | 0.300 | 58.403 | 646.9 |
| bc_all | 0.200 | 61.356 | 690.6 |
| weighted_bc_classifier | 0.100 | 72.695 | 743.5 |

## Classifier Diagnostics

- Labeled accuracy: `0.796`.
- Positive transition probability mean: `0.673`.
- Negative transition probability mean: `0.307`.
- Unlabeled transition probability mean: `0.454`.

## Interpretation

- This is a train/eval pipeline smoke, not a final Tri-PIQL result.
- `weighted_bc_classifier` is the relevant simple filtering baseline for the next Tri-PIQL comparison.
