# Candidate K Confidence Router Screen

**Status: rejected as a frozen candidate.** Candidate K routes from
positive-only to triage when the positive top-mode action has low learned
GMM log-likelihood under the triage policy. Threshold `6.269868` was
selected from the Lift606 exploratory audit and then tested unchanged on
Lift707.

## Lift606 Development Screen

| method | successes | avg len |
| --- | ---: | ---: |
| positive_only_nn | 14/20 | 70.25 |
| triage_bc | 13/20 | 78.45 |
| weighted_bc | 6/20 | 124.75 |
| confidence_router_thr5p93 | 15/20 | 63.95 |
| confidence_router_thr6p27 | 18/20 | 44.8 |

On the tuned Lift606 first-20 screen, the confidence router reaches
`18/20`, above positive-only `14/20` and triage `13/20`.

## Lift606 Broader Endpoint

| method | successes | avg len |
| --- | ---: | ---: |
| positive_only_nn | 28/50 | 85.18 |
| triage_bc | 23/50 | 100.12 |
| weighted_bc | 16/50 | 122.46 |
| confidence_router_thr6p27 | 32/50 | 78.12 |

The same threshold reaches `32/50`, above positive-only `28/50`, triage
`23/50`, and weighted `16/50` on Lift606.

## Lift707 Fresh Screen

| method | successes | avg len |
| --- | ---: | ---: |
| positive_only_nn | 12/20 | 82.05 |
| triage_bc | 9/20 | 98.1 |
| confidence_router_thr6p27 | 10/20 | 92.25 |

The fixed threshold does not transfer to Lift707: the router reaches
`10/20`, below positive-only `12/20` and only above triage `9/20`.

## Read

- Learned GMM confidence has real local signal on Lift606, unlike nearest
  support-margin routing.
- The fixed threshold is not stable enough for a method claim. Candidate K
  should not be scaled as-is.
- The next useful direction is either threshold calibration from labeled
  validation features, or a temporal confidence gate that adapts within an
  episode, not another globally fixed Lift threshold.

## Artifacts

- Summary CSV: `results/candidate_g_fresh_preflight/candidate_k_confidence_router_summary.csv`.
- Feature audit report: `results/candidate_g_fresh_preflight/candidate_k_lift_confidence_audit_REPORT.md`.
- Lift606 router 50-episode eval: `results/candidate_g_fresh_preflight/lift606_router_confidence_poslogp_triage_thr6p27_eval50/REPORT.md`.
- Lift707 router eval: `results/candidate_g_fresh_preflight/lift707_router_confidence_poslogp_triage_thr6p27_eval20/REPORT.md`.
