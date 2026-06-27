# SM-RWBC Can404 Screen

This is the first SOTA Candidate 1 screen from `triage_bc_sota_candidate_plan.md`.
It tests broad-pool sequence-masked risk-weighted BC on the severe Can split-404 regression case.

## Result

| method | successes | success rate | avg len | delta vs positive |
| --- | ---: | ---: | ---: | ---: |
| Positive-only NN top40 | 17/20 | 0.850 | 148.2 | 0 |
| Weighted BC full pool | 13/20 | 0.650 | 211.5 | -4 |
| Candidate C sequence-mask e200 | 16/20 | 0.800 | 167.7 | -1 |
| Candidate X extra-only negative-action e200 | 14/20 | 0.700 | 201.5 | -3 |
| SM-RWBC m0.03 lambda2 combined e100 | 10/20 | 0.500 | 260.0 | -7 |
| SM-RWBC m0.03 lambda2 combined e200 | 10/20 | 0.500 | 260.6 | -7 |

## Decision

- Best SM-RWBC checkpoint: `10/20`.
- Positive-only NN matched screen: `17/20`.
- Previous Candidate C sequence mask: `16/20`.
- Decision: `reject` for this broad-pool `m_min=0.03`, `lambda=2`, `combined` recipe.

Read: the preflight reduced hidden-bad transition mass in the broad pool, but the endpoint policy still collapses below the positive-only anchor. Do not scale this recipe unchanged to Can505 or Lift.

## Artifacts

- Preflight report: `results/sota_candidate/sm_rwbc_can404_m003_lam2_combined_preflight/sm_rwbc_preflight_REPORT.md`.
- Eval report: `results/sota_candidate/sm_rwbc_can404_m003_lam2_combined_eval20/REPORT.md`.
- Summary CSV: `results/sota_candidate/sm_rwbc_can404_screen_summary.csv`.
