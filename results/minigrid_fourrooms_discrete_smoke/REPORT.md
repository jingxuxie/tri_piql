# MiniGrid Discrete Smoke: `D4RL/minigrid/fourrooms-v0`

Split path: `results/minari_inspection/D4RL__minigrid__fourrooms-v0/split_indices.json`.
Policy steps: `1000`.
Classifier steps: `700`.
Evaluation episodes: `100`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.050 | 0.048 | 95.2 |
| bc_pos_unlabeled | 0.050 | 0.048 | 95.2 |
| bc_all | 0.050 | 0.048 | 95.2 |
| weighted_bc_state_action | 0.050 | 0.048 | 95.2 |
| bc_positive_sa_rerank_alpha0.5 | 0.050 | 0.048 | 95.2 |
| bc_positive_sa_rerank_alpha1 | 0.050 | 0.048 | 95.2 |
| bc_positive_sa_rerank_alpha2 | 0.010 | 0.009 | 99.1 |

## State-Action Classifier Diagnostics

- Labeled accuracy: `0.791`.
- Positive/negative/unlabeled probability mean: `0.657` / `0.354` / `0.418`.

## Interpretation

- This is a fast discrete-action real-data smoke for tri-signal filtering and reranking.
- `weighted_bc_state_action` clones positives plus unlabeled transitions weighted by the state-action classifier.
- Reranking uses the BC-positive policy logits plus a state-action classifier bonus.
