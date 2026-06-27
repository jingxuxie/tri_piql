# Can404 Anchor Feature-Gate Preflight

This is a post-hoc upper-bound audit over existing first-20 Can404 endpoint screens.
It tests whether simple hidden-label-free initial-state features from the prior Candidate E/V audit could route from positive-only to a near-miss candidate while preserving positive-only successes.

Important caveat: thresholds are selected on the same Can404 endpoint outcomes. This is not a deployable method or a validation result.

## Summary

- Positive-only anchor: `17/20`.
- CAU has a same-screen post-hoc zero-loss gate: `18/20`, gains `1`, losses `0`, feature `initial_anchor_pos_dist_mean` `gt` `2.883000`, opened initials `demo_39`.
- Demo-DPO and Candidate C have no zero-loss gain gate in this small feature family.
- This is enough to define a future validation hypothesis, but not enough to justify a paper-facing methods claim.

## Best Same-Screen Gates

| method | candidate alone | best routed | feature gate | opened initials | gains | losses | status |
| --- | ---: | ---: | --- | --- | ---: | ---: | --- |
| CAU action-conflict | 16/20 | 18/20 | initial_anchor_pos_dist_mean gt 2.883000 | demo_39 | 1 | 0 | posthoc_hypothesis_only |
| Demo-DPO ref-centered | 16/20 | 17/20 | initial_anchor_pos_dist_mean le 0.803999 |  | 0 | 0 | no_anchor_preserving_gate_found |
| Candidate C sequence mask | 16/20 | 17/20 | initial_anchor_pos_dist_mean le 0.803999 |  | 0 | 0 | no_anchor_preserving_gate_found |

## Decision

- Do not run a full endpoint matrix from this same-screen result.
- The only defensible follow-up would be a predeclared fresh validation: freeze the CAU-plus-positive fallback feature rule from this audit, then test it on a fresh split after training the corresponding candidate policy.
- If that fresh split shows any positive-only anchor loss, stop immediately.

## Artifacts

- Summary CSV: `results/sota_candidate/can404_anchor_feature_gate_preflight.csv`.
- Report: `results/sota_candidate/CAN404_ANCHOR_FEATURE_GATE_PREFLIGHT_REPORT.md`.
