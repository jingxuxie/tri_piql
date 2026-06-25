# Can Paired 40p/80b Final Split 33 Endpoint

This is the third frozen final-split run under `METHOD_FREEZE.md`.

Protocol:

- Task: Robomimic Can Paired low-dimensional sparse.
- Split: 10 labeled positives, 10 labeled negatives, 40 hidden-positive unlabeled, 80 hidden-bad unlabeled.
- Final split seed: `33`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Policy: official Robomimic BC-RNN-GMM, 200 epochs x 100 steps.
- Evaluation: fixed 20k checkpoint, 50 validation-positive rollouts, horizon 400, rollout seed 0.

Results:

| method | router branch | selected unlabeled | hidden-positive | hidden-bad | purity | 20k success |
|---|---|---:|---:|---:|---:|---:|
| TRIAGE-BC | hard_adaptive_masscap | 47 | 34 | 13 | 0.723 | 0.700 |
| weighted BC | classifier-probability sampler | 120 | 40 | 80 | 0.333 | 0.640 |

Interpretation:

- Direction again favors TRIAGE-BC, with a gap of 0.060 over 50 endpoint episodes.
- TRIAGE selected cleaner support on this split than on split seeds 11 and 22, but with lower hidden-positive coverage: 34/40 hidden positives and 13/80 hidden bads.
- This completes the primary frozen Can 40p/80b split-seed set. Across seeds 11, 22, and 33, TRIAGE-BC is `0.660` versus weighted BC `0.600` over 150 endpoint rollouts.
