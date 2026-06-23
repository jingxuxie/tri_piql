# Minari Action Rerank Smoke: `D4RL/pointmaze/large-dense-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-dense-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
BC steps: `700`.
State-action classifier steps: `500`.
Evaluation episodes: `10`.
Candidate count: `64`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.400 | 48.788 | 623.4 |
| weighted_bc_obs_classifier | 0.300 | 50.300 | 622.9 |
| bc_sa_rerank_noise0.1_penalty0.05 | 0.100 | 60.335 | 745.0 |
| bc_sa_rerank_noise0.1_penalty0.2 | 0.100 | 67.697 | 776.3 |
| bc_sa_rerank_noise0.25_penalty0.05 | 0.300 | 58.518 | 710.4 |
| bc_sa_rerank_noise0.25_penalty0.2 | 0.100 | 60.702 | 741.8 |

## State-Action Classifier Diagnostics

- Labeled accuracy: `0.809`.
- Positive/negative/unlabeled probability mean: `0.695` / `0.284` / `0.441`.
- Positive/negative/unlabeled logit mean: `0.945` / `-1.355` / `-0.476`.

## Interpretation

- This tests policy extraction by keeping positive BC as the anchor and using a learned state-action quality score only to rerank nearby candidate actions.
- A positive result would show that bad-action information is useful without retraining the actor on noisy advantage weights.
