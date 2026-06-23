# Minari BC Smoke: `D4RL/kitchen/mixed-v2`

Split path: `results/minari_inspection/D4RL__kitchen__mixed-v2/split_indices.json`.
Observation keys: `['observation']`.
Train steps per actor: `2`.
Classifier steps: `2`.
Evaluation episodes: `1`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.000 | 0.000 | 5.0 |
| bc_pos_unlabeled | 0.000 | 0.000 | 5.0 |
| bc_all | 0.000 | 0.000 | 5.0 |
| weighted_bc_classifier | 0.000 | 0.000 | 5.0 |

## Classifier Diagnostics

- Labeled accuracy: `0.634`.
- Positive transition probability mean: `0.500`.
- Negative transition probability mean: `0.494`.
- Unlabeled transition probability mean: `0.498`.

## Interpretation

- This is a train/eval pipeline smoke, not a final Tri-PIQL result.
- `weighted_bc_classifier` is the relevant simple filtering baseline for the next Tri-PIQL comparison.
