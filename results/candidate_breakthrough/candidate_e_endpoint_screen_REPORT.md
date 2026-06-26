# Candidate E Initial-Gate Endpoint Screen

Candidate E is a confidence-preserving router: use positive-only by default,
but if the positive policy's initial action is far from labeled positive support
(`initial_anchor_pos_dist > 3.0`), force the weighted policy for that episode.
The router evaluator uses isolated per-policy RNG streams for this report.

## 50-Episode Split-404 Summary

| method | kind | success | rate | avg len | gate opens |
| --- | --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | baseline | 39/50 | 0.780 | 169.3 |  |
| Weighted BC full pool | baseline | 33/50 | 0.660 | 208.9 |  |
| TRIAGE-BC v0.1 hard support | baseline | 36/50 | 0.720 | 190.8 |  |
| v0.2 positive-NN/risk union top40 | baseline | 27/50 | 0.540 | 248.4 |  |
| Candidate A transition-weighted | candidate_a | 30/50 | 0.600 | 224.2 |  |
| Candidate E initial support-distance gate (isolated RNG) | candidate_e | 46/50 | 0.920 | 130.3 | 5 |

## First-20 Screen

| method | kind | success | rate | gate opens |
| --- | --- | ---: | ---: | ---: |
| Positive-only NN top40 | baseline | 17/20 | 0.850 |  |
| Candidate B router labeled support, no bias | candidate_b | 16/20 | 0.800 |  |
| Candidate C sequence-mask e200 | candidate_c | 16/20 | 0.800 |  |
| Candidate D negative-action e100 | candidate_d | 14/20 | 0.700 |  |
| Candidate E initial support-distance gate (isolated RNG) | candidate_e | 19/20 | 0.950 | 2 |

## Read

- Candidate E reaches `46/50`, `+7/50` versus positive-only.
- The gate opens only on the high initial positive-support-distance state `demo_39`, where positive-only fails and weighted BC has coverage.
- This is the strongest split-404 candidate in this branch, but it is still a hand-thresholded one-split result.
- Multi-split promotion requires the Candidate F anchor calibration rather than this fixed positive-anchor gate alone.

## Per-Initial 50-Episode Counts

| initial | positive | weighted | v0.1 | union | cand A | cand E | gate opens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| demo_5 | 5 | 1 | 5 | 4 | 4 | 5 | 0 |
| demo_29 | 4 | 4 | 4 | 2 | 1 | 5 | 0 |
| demo_39 | 0 | 3 | 1 | 1 | 3 | 5 | 5 |
| demo_45 | 5 | 1 | 3 | 2 | 0 | 5 | 0 |
| demo_53 | 5 | 5 | 5 | 5 | 5 | 5 | 0 |
| demo_81 | 4 | 5 | 5 | 5 | 5 | 5 | 0 |
| demo_89 | 4 | 3 | 4 | 0 | 4 | 4 | 0 |
| demo_99 | 4 | 2 | 4 | 1 | 3 | 4 | 0 |
| demo_105 | 5 | 5 | 4 | 4 | 5 | 5 | 0 |
| demo_189 | 3 | 4 | 1 | 3 | 0 | 3 | 0 |

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_e_endpoint_screen_summary.csv`.
- Per-initial CSV: `results/candidate_breakthrough/candidate_e_endpoint_screen_per_initial_50.csv`.
- Initial feature audit: `results/candidate_breakthrough/candidate_e_initial_gate_audit_REPORT.md`.
- 50-episode eval: `results/candidate_breakthrough/candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng/REPORT.md`.
