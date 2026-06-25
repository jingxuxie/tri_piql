# Can Paired 40p/80b Final Split 11 Endpoint

This is the first frozen final-split run under `METHOD_FREEZE.md`.

Protocol:

- Task: Robomimic Can Paired low-dimensional sparse.
- Split: 10 labeled positives, 10 labeled negatives, 40 hidden-positive unlabeled, 80 hidden-bad unlabeled.
- Final split seed: `11`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Policy: official Robomimic BC-RNN-GMM, 200 epochs x 100 steps.
- Evaluation: fixed 20k checkpoint, 50 validation-positive rollouts, horizon 400, rollout seed 0.

Results:

| method | router branch | selected unlabeled | hidden-positive | hidden-bad | purity | 20k success |
|---|---|---:|---:|---:|---:|---:|
| TRIAGE-BC | hard_adaptive_masscap | 70 | 40 | 30 | 0.571 | 0.760 |
| weighted BC | classifier-probability sampler | 120 | 40 | 80 | 0.333 | 0.720 |

Interpretation:

- Direction favors TRIAGE-BC on this first fresh final split, but the gap is small: 0.040 over 50 episodes.
- TRIAGE selected all 40 available hidden positives while filtering out 50 of 80 hidden bad demos.
- This is a useful frozen-test data point, not a complete final claim. The same comparison still needs split seeds 22 and 33.
