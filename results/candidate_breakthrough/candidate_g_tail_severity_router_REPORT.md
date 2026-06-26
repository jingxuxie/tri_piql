# Candidate G Tail-Severity Router

This is a next-candidate assembly from completed endpoint rows only.
It uses the same low-tail threshold as Candidate F:
`0.5 * unlabeled_prob_mean`.

Router rule:

- no low-probability tail: use the clean positive anchor;
- mild low tail (`below_fraction < 0.03`): use triage/hard support;
- severe low tail: use weighted BC.

For Can, the clean positive anchor is Candidate E's initial-distance gate.
For Lift, the clean positive anchor is the positive-only policy.

| task | split | #<thr | frac<thr | choice | candidate | best | delta |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| can40 | 101 | 2 | 0.050 | weighted | 37/50 | 37/50 | +0 |
| can40 | 202 | 0 | 0.000 | candidate_e_gate | 40/50 | 40/50 | +0 |
| can40 | 303 | 0 | 0.000 | candidate_e_gate | 36/50 | 36/50 | +0 |
| can40 | 404 | 0 | 0.000 | candidate_e_gate | 46/50 | 39/50 | +7 |
| can40 | 505 | 0 | 0.000 | candidate_e_gate | 39/50 | 40/50 | -1 |
| lift_mg | 101 | 3 | 0.019 | triage | 36/50 | 36/50 | +0 |
| lift_mg | 202 | 4 | 0.025 | triage | 34/50 | 34/50 | +0 |
| lift_mg | 303 | 0 | 0.000 | positive | 21/50 | 21/50 | +0 |
| lift_mg | 404 | 8 | 0.050 | weighted | 30/50 | 30/50 | +0 |
| lift_mg | 505 | 21 | 0.131 | weighted | 33/50 | 33/50 | +0 |
| can40 | total | 2 |  |  | 198/250 | 192/250 | +6 |
| lift_mg | total | 36 |  |  | 154/250 | 154/250 | +0 |
| combined | total | 38 |  |  | 352/500 | 346/500 | +6 |

## Read

- Candidate G reaches `352/500`, versus the
  completed per-split baseline oracle `346/500`.
- On Can 40p/80b it is identical to frozen Candidate F: `198/250`
  versus baseline oracle `192/250`.
- On Lift MG it matches the completed per-split baseline oracle:
  `154/250`.
- This is not yet a paper claim. The `0.03` mild-tail cutoff is a new
  hyperparameter discovered after inspecting completed Lift rows, so the
  correct next step is a pre-registered/frozen endpoint check.

## Mild-Cutoff Sensitivity

| mild cutoff | Can | Lift | combined | best | delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.000 | 198/250 | 145/250 | 343/500 | 346/500 | -3 |
| 0.020 | 198/250 | 150/250 | 348/500 | 346/500 | +2 |
| 0.025 | 198/250 | 150/250 | 348/500 | 346/500 | +2 |
| 0.026 | 198/250 | 154/250 | 352/500 | 346/500 | +6 |
| 0.030 | 198/250 | 154/250 | 352/500 | 346/500 | +6 |
| 0.040 | 198/250 | 154/250 | 352/500 | 346/500 | +6 |
| 0.050 | 198/250 | 154/250 | 352/500 | 346/500 | +6 |
| 0.051 | 189/250 | 153/250 | 342/500 | 346/500 | -4 |
| 0.060 | 189/250 | 153/250 | 342/500 | 346/500 | -4 |

The best combined row is stable only for a narrow mild-cutoff band around
`0.026` to `0.050` under the strict `< cutoff` rule. That is promising,
but it is not enough to claim robust transfer without a fresh freeze.

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_g_tail_severity_router_summary.csv`.
- Sensitivity CSV: `results/candidate_breakthrough/candidate_g_tail_severity_router_sensitivity.csv`.
