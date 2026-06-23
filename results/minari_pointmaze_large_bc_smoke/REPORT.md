# Minari BC Smoke: `D4RL/pointmaze/large-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
Train steps per actor: `600`.
Classifier steps: `300`.
Evaluation episodes: `10`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.400 | 0.400 | 511.8 |
| bc_pos_unlabeled | 0.300 | 0.300 | 631.7 |
| bc_all | 0.200 | 0.200 | 725.1 |
| weighted_bc_classifier | 0.400 | 0.400 | 564.0 |

## Classifier Diagnostics

- Labeled accuracy: `0.912`.
- Positive transition probability mean: `0.821`.
- Negative transition probability mean: `0.166`.
- Unlabeled transition probability mean: `0.405`.

## Interpretation

- This is a train/eval pipeline smoke, not a final Tri-PIQL result.
- `weighted_bc_classifier` is the relevant simple filtering baseline for the next Tri-PIQL comparison.
