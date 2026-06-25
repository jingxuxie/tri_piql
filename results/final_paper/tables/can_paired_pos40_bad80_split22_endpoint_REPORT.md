# Can Paired 40p/80b Final Split 22 Endpoint

This is the second frozen final-split run under `METHOD_FREEZE.md`.

Protocol:

- Task: Robomimic Can Paired low-dimensional sparse.
- Split: 10 labeled positives, 10 labeled negatives, 40 hidden-positive unlabeled, 80 hidden-bad unlabeled.
- Final split seed: `22`, with shuffled label pools.
- Policy/classifier seed: `0`.
- Policy: official Robomimic BC-RNN-GMM, 200 epochs x 100 steps.
- Evaluation: fixed 20k checkpoint, 50 validation-positive rollouts, horizon 400, rollout seed 0.

Results:

| method | router branch | selected unlabeled | hidden-positive | hidden-bad | purity | 20k success |
|---|---|---:|---:|---:|---:|---:|
| TRIAGE-BC | hard_adaptive_masscap | 73 | 36 | 37 | 0.493 | 0.520 |
| weighted BC | classifier-probability sampler | 120 | 40 | 80 | 0.333 | 0.440 |

Interpretation:

- Direction again favors TRIAGE-BC, with a gap of 0.080 over 50 endpoint episodes.
- This split is tougher than split 11: TRIAGE selected support has lower purity (`0.493` versus `0.571`) and misses 4 of 40 hidden positives.
- Absolute endpoint success is lower for both methods, so the result supports robustness to a harder split but also shows real split sensitivity.
- Across frozen split seeds 11 and 22 so far, TRIAGE-BC is `0.640` versus weighted BC `0.580` over 100 total endpoint rollouts. Split seed 33 is still required before making the final-test claim.
