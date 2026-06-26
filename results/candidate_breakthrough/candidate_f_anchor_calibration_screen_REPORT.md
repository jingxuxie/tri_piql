# Candidate F Anchor-Calibration First-20 Screen

Candidate F is a hypothesis from train/support statistics:

- compute classifier probabilities for the positive-NN selected unlabeled
  support set;
- set the tail threshold to half of the full unlabeled pool's mean
  classifier probability;
- if any selected demo falls below that threshold, use weighted BC as the
  split-level anchor;
- otherwise use Candidate E, the positive anchor with initial-distance
  fallback to weighted BC.

This rule uses no endpoint outcomes or hidden labels. The remaining
hyperparameter is the tail fraction `0.5`.

| split | min prob | unlabeled mean | min/mean | tail thr | #<thr | source | positive | weighted | triage | cand E | cand F | delta vs best |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 101 | 0.125 | 0.406 | 0.309 | 0.203 | 2 | weighted_anchor | 7/20 | 12/20 | 11/20 | 7/20 | 12/20 | +0 |
| 202 | 0.395 | 0.404 | 0.978 | 0.202 | 0 | candidate_e_gate | 17/20 | 13/20 | 12/20 | 17/20 | 17/20 | +0 |
| 303 | 0.390 | 0.472 | 0.826 | 0.236 | 0 | candidate_e_gate | 15/20 | 10/20 | 13/20 | 15/20 | 15/20 | +0 |
| 404 | 0.306 | 0.443 | 0.692 | 0.221 | 0 | candidate_e_gate | 17/20 | 13/20 | 14/20 | 19/20 | 19/20 | +2 |
| 505 | 0.380 | 0.475 | 0.800 | 0.237 | 0 | candidate_e_gate | 15/20 | 12/20 | 14/20 | 16/20 | 16/20 | +1 |
| total |  |  |  |  | 2 |  | 71/100 | 60/100 | 64/100 | 74/100 | 79/100 | +3 |

## 50-Episode Assembled Endpoint Estimate

This table combines completed 50-episode baselines with isolated-RNG
Candidate E 50-episode runs where available. For splits where the
isolated first-20 gate never opened and no router-50 run was launched,
the positive-only 50-episode result is used as a no-gate substitution.

| split | positive | weighted | triage | cand E / subst | cand F | delta vs best | source |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 101 | 19/50 | 37/50 | 28/50 | n/a | 37/50 | +0 | missing_router_50 |
| 202 | 40/50 | 33/50 | 36/50 | 40/50 | 40/50 | +0 | positive_50_no_gate_in_first20 |
| 303 | 36/50 | 25/50 | 35/50 | 36/50 | 36/50 | +0 | positive_50_no_gate_in_first20 |
| 404 | 39/50 | 33/50 | 36/50 | 46/50 | 46/50 | +7 | candidate_e_initial_posdist_gate_weighted_split404_eval50_isolated_rng |
| 505 | 40/50 | 30/50 | 36/50 | 39/50 | 39/50 | -1 | candidate_e_initial_posdist_gate_weighted_split505_eval50_isolated_rng |
| total | 174/250 | 158/250 | 171/250 | n/a | 198/250 | +6 | mixed observed and no-gate substitution |

## Read

- The calibrated low-probability tail rule selects weighted only on split
  101, where the fixed positive anchor was the main failure.
- The normalized tail ratio is `0.309` on split 101 versus at least
  `0.692` on the other splits, so any tail fraction in roughly
  `[0.35, 0.65]` would make the same anchor decision.
- With isolated-RNG router evaluation, the resulting first-20 aggregate
  is `79/100`, exceeding the completed per-split baseline oracle over
  positive-only, weighted, and triage (`76/100`).
- The assembled 50-episode estimate is `198/250`, versus positive-only
  `174/250` and the per-split baseline oracle `192/250`. The gain is
  mostly split 101 weighted anchoring plus split 404 isolated-RNG
  Candidate E (`46/50`).
- This is closer to a frozen rule than the fixed `0.2` threshold because
  the cutoff is tied to the unlabeled pool's classifier score scale. It
  has now been consolidated in
  `results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md`.

## Artifacts

- Summary CSV: `results/candidate_breakthrough/candidate_f_anchor_calibration_first20_summary.csv`.
- Frozen matrix: `results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md`.
- Teacher-forced negative audit:
  `results/candidate_breakthrough/candidate_f_teacher_forced_anchor_audit_REPORT.md`.
