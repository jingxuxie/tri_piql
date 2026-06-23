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
| bc_positive | 0.200 | 50.908 | 748.3 |
| weighted_bc_obs_classifier | 0.200 | 51.895 | 727.9 |
| bc_sa_rerank_noise0.1_penalty0.05 | 0.300 | 70.656 | 681.3 |
| bc_sa_rerank_noise0.1_penalty0.2 | 0.200 | 69.430 | 700.9 |
| bc_sa_rerank_noise0.25_penalty0.05 | 0.300 | 57.409 | 640.0 |
| bc_sa_rerank_noise0.25_penalty0.2 | 0.300 | 53.033 | 659.6 |

## State-Action Classifier Diagnostics

- Labeled accuracy: `0.825`.
- Positive/negative/unlabeled probability mean: `0.708` / `0.286` / `0.453`.
- Positive/negative/unlabeled logit mean: `1.004` / `-1.324` / `-0.397`.

## Interpretation

- This tests policy extraction by keeping positive BC as the anchor and using a learned state-action quality score only to rerank nearby candidate actions.
- A positive result would show that bad-action information is useful without retraining the actor on noisy advantage weights.
