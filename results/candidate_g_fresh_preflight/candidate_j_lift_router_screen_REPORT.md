# Candidate J Lift606 Router Screen

**Status: failed screen.** Candidate J tests whether a deployable
support-distance gate can repair Candidate I's Lift mild-tail failure by
routing among existing positive-only, triage, and weighted policies.

## Baselines

| method | first20_successes | first20_episodes | eval50_successes | eval50_episodes |
| --- | --- | --- | --- | --- |
| positive_only_nn | 14 | 20 | 28 | 50 |
| triage_bc | 13 | 20 | 23 | 50 |
| weighted_bc | 6 | 20 | 16 | 50 |

## Router Screens

| method | successes | episodes | choices_positive | choices_triage | choices_weighted |
| --- | --- | --- | --- | --- | --- |
| margin_labeled | 11 | 20 | 798 | 524 | 373 |
| positive_anchor_labeled | 11 | 20 | 798 | 524 | 373 |
| positive_anchor_anchor_support | 10 | 20 | 675 | 654 | 494 |
| init_posdist3_pos_to_triage | 14 | 20 | 1405 | 0 | 0 |

## Initial-Distance Audit

| threshold | successes | episodes | switches |
| --- | --- | --- | --- |
| 0.946463 | 14 | 20 | 14 |
| 1.009414 | 14 | 20 | 13 |
| 1.07892 | 14 | 20 | 12 |
| 1.683104 | 14 | 20 | 6 |
| 1.785377 | 14 | 20 | 5 |
| 1.874567 | 14 | 20 | 4 |
| 2.089064 | 14 | 20 | 3 |
| 3.327602 | 14 | 20 | 0 |

The initial-distance audit is post-hoc and only checks whether any
threshold over the logged first-step positive-action distance could beat
positive-only on the first 20 starts. It cannot: the best threshold ties
positive-only at `14/20`.

## Read

- The non-deployable oracle over positive, triage, and weighted is `17/20`,
  so the policy set has headroom, but the tested support-distance gates do
  not expose it.
- Per-step labeled-support margin routing is worse than the positive-only
  anchor (`11/20` versus `14/20`).
- Adding the Lift606 positive-NN anchor demos to the support scorer makes
  the margin router worse (`10/20`).
- The simple initial positive-distance gate with threshold `3.0` never opens
  and exactly reproduces positive-only first-20 behavior.
- Next router work needs richer deployable features, likely temporal
  confidence or policy self-likelihood features, not just nearest labeled
  state-action margin.

## Artifacts

- Baseline CSV: `results/candidate_g_fresh_preflight/candidate_j_lift_router_baselines.csv`.
- Router summary CSV: `results/candidate_g_fresh_preflight/candidate_j_lift_router_summary.csv`.
- Threshold audit CSV: `results/candidate_g_fresh_preflight/candidate_j_lift_router_initdist_threshold_audit.csv`.
- Per-initial CSV: `results/candidate_g_fresh_preflight/candidate_j_lift_router_per_initial.csv`.
- Evaluator: `scripts/evaluate_robomimic_router_policy.py` now accepts
  `--positive-anchor-diagnostics` for non-Can anchor-support routing.
