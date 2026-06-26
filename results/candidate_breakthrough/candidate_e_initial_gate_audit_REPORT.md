# Candidate E Initial-Gate Feature Audit

This audit computes first-step deployable support features for positive-only, weighted BC, and Candidate C.
Rollout outcomes are included only to diagnose whether an initial-state gate has signal; they are not training labels for a deployable rule.

## First-20 Outcome Ceiling

- Positive-only: `17/20`.
- Weighted BC: `13/20`.
- Candidate C: `16/20`.
- Best existing deployable router in this audit: `16/20`.
- Per-initial oracle over listed methods: `19/20`.

## Initial Features

| initial | pos margin | weighted margin | cand C margin | weighted-pos | candC-pos | positive | weighted | cand C | router | oracle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| demo_5 | 1.531578 | 1.413608 | 1.518865 | -0.117970 | -0.012713 | 2 | 0 | 2 | 2 | 2 |
| demo_29 | 0.656503 | 0.564819 | 0.720095 | -0.091684 | 0.063592 | 2 | 1 | 1 | 2 | 2 |
| demo_39 | 0.119516 | 0.176759 | 0.114334 | 0.057243 | -0.005182 | 0 | 1 | 0 | 0 | 1 |
| demo_45 | 0.943251 | 0.988700 | 0.718239 | 0.045449 | -0.225012 | 2 | 1 | 2 | 2 | 2 |
| demo_53 | -0.418778 | -0.463354 | -0.436955 | -0.044576 | -0.018177 | 2 | 2 | 2 | 2 | 2 |
| demo_81 | 0.984836 | 0.932458 | 0.804504 | -0.052378 | -0.180332 | 2 | 2 | 2 | 2 | 2 |
| demo_89 | -0.112073 | -0.024754 | -0.151370 | 0.087319 | -0.039297 | 2 | 1 | 2 | 2 | 2 |
| demo_99 | 0.556016 | 0.479187 | 0.492593 | -0.076829 | -0.063423 | 1 | 1 | 1 | 2 | 2 |
| demo_105 | -0.282707 | -0.322729 | -0.386047 | -0.040022 | -0.103340 | 2 | 2 | 2 | 2 | 2 |
| demo_189 | 0.626989 | 0.642123 | 0.541887 | 0.015134 | -0.085102 | 2 | 2 | 2 | 0 | 2 |

## Read

- A useful deployable gate must identify the `demo_39` coverage gap without switching away from `demo_189` and other positive-anchor successes.
- If first-step margins cannot separate those cases, a router needs temporal confidence features rather than a pure initial-state rule.

## Artifacts

- Feature CSV: `results/candidate_breakthrough/candidate_e_initial_gate_feature_audit.csv`.
