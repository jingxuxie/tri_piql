# Can Paired 40p/80b Frozen Final Endpoint Summary

Completed frozen final split seeds: `11`, `22`, and `33`.

Protocol:

- Method contract: `METHOD_FREEZE.md`.
- Task: Robomimic Can Paired low-dimensional sparse.
- Split type: 10 labeled positives, 10 labeled negatives, 40 hidden-positive unlabeled, 80 hidden-bad unlabeled.
- Policy/classifier seed: `0` for each split.
- Policy: official Robomimic BC-RNN-GMM, fixed 20k endpoint.
- Evaluation: 50 validation-positive rollouts per method and split, horizon 400, rollout seed 0.
- Execution note: all-demo split 22 and 33 endpoint evaluations and all-positive oracle endpoint evaluations used the CPU device fallback after CUDA escalation timed out in Codex; checkpoint, seed, init-state mode, episodes, and horizon were unchanged.

Endpoint results:

| split seed | TRIAGE-BC | weighted BC | positive-only NN top40 | all-demo BC | all-positive oracle | TRIAGE - weighted | TRIAGE - positive-only | TRIAGE - all-demo | TRIAGE - oracle |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 | 0.760 | 0.720 | 0.840 | 0.500 | 0.980 | +0.040 | -0.080 | +0.260 | -0.220 |
| 22 | 0.520 | 0.440 | 0.760 | 0.560 | 0.980 | +0.080 | -0.240 | -0.040 | -0.460 |
| 33 | 0.700 | 0.640 | 0.560 | 0.560 | 0.980 | +0.060 | +0.140 | +0.140 | -0.280 |
| pooled | 0.660 | 0.600 | 0.720 | 0.540 | 0.980 | +0.060 | -0.060 | +0.120 | -0.320 |

Support audit:

| method | selected unlabeled | hidden-positive | hidden-bad | purity |
|---|---:|---:|---:|---:|
| TRIAGE-BC pooled | 190 | 110 | 80 | 0.579 |
| weighted BC pooled | 360 | 120 | 240 | 0.333 |
| positive-only NN top40 pooled | 120 | 106 | 14 | 0.883 |

All-demo BC does not select unlabeled support, so support purity is undefined. It trains on all 180 train demos in each split, or 540 train demos pooled.

All-positive oracle is a diagnostic upper-bound row, not a deployable method: it trains on all true-positive train demos. This is 90 demos per split, or 270 demos pooled.

Interpretation:

- All three primary frozen final split seeds favor TRIAGE-BC over classifier-probability weighted BC at the fixed 20k endpoint.
- The hard-vs-weighted aggregate is modest: 99/150 successes for TRIAGE-BC versus 90/150 for weighted BC.
- All-demo mixed cloning is the weakest pooled row at 81/150 successes, although split 22 is an exception where all-demo BC exceeds TRIAGE-BC.
- Positive-only NN top40 is stronger than both on this frozen Can matrix: 108/150 successes and high-purity support.
- All-positive oracle is far stronger at 147/150 successes, showing that the frozen evaluation starts are highly solvable with broad true-positive support and that all non-oracle support converters leave substantial headroom.
- This directly weakens any bad-label benefit claim on Can 40p/80b. The Can final split should be written as oracle diagnostic highest, positive-only retrieval strongest among non-oracle controls, TRIAGE-BC better than weighted BC and pooled all-demo cloning, and a strong no-bad-label caveat.
