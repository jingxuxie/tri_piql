# Candidate F Lift Transfer Audit

This audit reuses completed Lift MG endpoint rows and applies the same
`0.5 * unlabeled_prob_mean` low-tail statistic used by Candidate F on Can.
No new Lift rollouts are claimed here.

| split | min/mean | #<thr | frac<thr | positive | weighted | triage | can-style | tail-severity | best |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | ---: |
| 101 | 0.353 | 3 | 0.019 | 28/50 | 31/50 | 36/50 | weighted 31/50 | triage 36/50 | 36/50 |
| 202 | 0.200 | 4 | 0.025 | 25/50 | 30/50 | 34/50 | weighted 30/50 | triage 34/50 | 34/50 |
| 303 | 1.401 | 0 | 0.000 | 21/50 | 19/50 | 20/50 | positive 21/50 | positive 21/50 | 21/50 |
| 404 | 0.133 | 8 | 0.050 | 25/50 | 30/50 | 29/50 | weighted 30/50 | weighted 30/50 | 30/50 |
| 505 | 0.162 | 21 | 0.131 | 26/50 | 33/50 | 24/50 | weighted 33/50 | weighted 33/50 | 33/50 |
| total |  | 36 |  | 125/250 | 143/250 | 143/250 | 145/250 | 154/250 | 154/250 |

## Read

- The direct Can-style transfer, `any low tail -> weighted`, reaches
  `145/250` on Lift, only slightly above always-weighted and always-triage
  (`143/250`) and below the per-split baseline oracle (`154/250`).
- Lift suggests a richer tail-severity interpretation: no low tail selects
  positive-only, mild low tail selects triage/hard support, and severe low
  tail selects weighted. That matches the completed Lift baseline oracle
  (`154/250`) but is diagnostic, not yet a frozen method.
- Combining frozen Can Candidate F (`198/250`) with this Lift tail-severity
  diagnostic gives `352/500`, versus the combined
  completed baseline oracle `346/500`.
- The evidence therefore supports a Can-frozen Candidate F claim now, and
  a possible broader Can+Lift tail-severity router as the next method
  candidate.

## Artifacts

- CSV: `results/candidate_breakthrough/candidate_f_lift_transfer_audit.csv`.
