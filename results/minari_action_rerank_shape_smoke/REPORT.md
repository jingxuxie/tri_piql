# Minari Action Rerank Smoke: `D4RL/pointmaze/large-dense-v2`

Split path: `results/minari_inspection/D4RL__pointmaze__large-dense-v2/split_indices.json`.
Observation keys: `['observation', 'desired_goal']`.
BC steps: `2`.
State-action classifier steps: `2`.
Evaluation episodes: `1`.
Candidate count: `8`.

## Metrics

| method | success | return | length |
|---|---:|---:|---:|
| bc_positive | 0.000 | 0.001 | 5.0 |
| weighted_bc_obs_classifier | 0.000 | 0.001 | 5.0 |
| bc_sa_rerank_noise0.1_penalty0.1 | 0.000 | 0.249 | 5.0 |

## State-Action Classifier Diagnostics

- Labeled accuracy: `0.485`.
- Positive/negative/unlabeled probability mean: `0.492` / `0.493` / `0.492`.
- Positive/negative/unlabeled logit mean: `-0.034` / `-0.030` / `-0.031`.

## Interpretation

- This tests policy extraction by keeping positive BC as the anchor and using a learned state-action quality score only to rerank nearby candidate actions.
- A positive result would show that bad-action information is useful without retraining the actor on noisy advantage weights.
