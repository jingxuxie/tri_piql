# Candidate B Router Screen

This screen evaluates deployable action-level routers over existing split-404 policies.
All loaded RNN policies are called at every timestep, and the router selects one action
using labeled-support state-action margins.

## First-20 Summary

| method | kind | success | rate | avg len | positive choices | weighted choices |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | baseline | 17/20 | 0.850 | 148.2 |  |  |
| Weighted BC full pool | baseline | 13/20 | 0.650 | 211.5 |  |  |
| TRIAGE-BC v0.1 hard support | baseline | 14/20 | 0.700 | 195.4 |  |  |
| v0.2 positive-NN/risk union top40 | baseline | 7/20 | 0.350 | 299.6 |  |  |
| Candidate A transition-weighted e200 | candidate_a | 12/20 | 0.600 | 222.5 |  |  |
| Router labeled support, positive bias 0.25 | candidate_b_router | 15/20 | 0.750 | 176.7 | 2894 | 640 |
| Router labeled support, no bias | candidate_b_router | 16/20 | 0.800 | 162.2 | 1801 | 1443 |
| Router positive-anchor support, no bias | candidate_b_router | 16/20 | 0.800 | 164.6 | 1723 | 1569 |
| Router labeled support, switch threshold 0.10 | candidate_b_router | 16/20 | 0.800 | 162.2 | 2623 | 622 |
| Router labeled support, switch threshold 0.05 | candidate_b_router | 14/20 | 0.700 | 193.6 | 2414 | 1457 |

## Read

- Best deployable router is `Router labeled support, no bias` at `16/20`, versus positive-only `17/20`.
- Non-deployable per-initial oracle over these rows is `19/20`, so routing has headroom.
- The current margin gate is not enough to beat the positive-only anchor: it tends to recover `demo_99` and sometimes `demo_39`, but loses `demo_189`.
- Small switch-threshold variants do not solve the tradeoff: threshold `0.10` stays at `16/20`, while threshold `0.05` drops to `14/20`.
- Do not scale this router unchanged. A better Candidate B needs an initial-state or confidence rule that preserves `demo_189` while identifying true coverage gaps.

## Per-Initial Counts

| initial | positive | weighted | v0.1 | union | cand A | router bias | router no-bias | router anchor-support | thr0.10 | thr0.05 | oracle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| demo_5 | 2 | 0 | 2 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 2 |
| demo_29 | 2 | 1 | 2 | 0 | 1 | 1 | 2 | 1 | 2 | 2 | 2 |
| demo_39 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| demo_45 | 2 | 1 | 2 | 0 | 0 | 2 | 2 | 2 | 2 | 1 | 2 |
| demo_53 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| demo_81 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| demo_89 | 2 | 1 | 2 | 0 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| demo_99 | 1 | 1 | 1 | 0 | 1 | 1 | 2 | 2 | 2 | 2 | 2 |
| demo_105 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| demo_189 | 2 | 2 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 2 |

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_b_router_screen_summary.csv`.
- Per-initial CSV: `results/candidate_breakthrough/candidate_b_router_screen_per_initial.csv`.
