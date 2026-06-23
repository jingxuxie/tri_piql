# MiniGrid Discrete Smoke: `D4RL/minigrid/fourrooms-v0`

Split path: `results/minari_inspection/D4RL__minigrid__fourrooms-v0/split_indices.json`.
Policy steps: `2`.
Classifier steps: `2`.
Evaluation episodes: `2`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.000 | 0.000 | 20.0 |
| bc_pos_unlabeled | 0.000 | 0.000 | 20.0 |
| bc_all | 0.000 | 0.000 | 20.0 |
| weighted_bc_state_action | 0.000 | 0.000 | 20.0 |
| bc_positive_sa_rerank_alpha0.5 | 0.000 | 0.000 | 20.0 |

## State-Action Classifier Diagnostics

- Labeled accuracy: `0.458`.
- Positive/negative/unlabeled probability mean: `0.501` / `0.501` / `0.501`.

## Interpretation

- This is a fast discrete-action real-data smoke for tri-signal filtering and reranking.
- `weighted_bc_state_action` clones positives plus unlabeled transitions weighted by the state-action classifier.
- Reranking uses the BC-positive policy logits plus a state-action classifier bonus.
