# Candidate M Temporal Confidence Router

**Status: rejected at the Lift606 development gate.** Candidate M tests
whether Candidate K/L's learned GMM confidence signal should be used
during rollout rather than only as an initial episode gate.

## Lift606 Baselines

| method | successes | avg_len |
| --- | --- | --- |
| positive_only_nn | 14/20 | 70.25 |
| triage_bc | 13/20 | 78.45 |
| weighted_bc | 6/20 | 124.75 |
| initial_confidence_q25 | 18/20 | 44.8 |

## Temporal Screens

| method | successes | avg_len | threshold_source | threshold | calibration_values | gate_open_mean | gate_open_min | gate_open_max | choices_positive | choices_triage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| temporal_initial_q25 | 7/20 | 112.65 | labeled_positive_quantile | 6.180339 | 10 | 107.3 | 21 | 148 | 107 | 2146 |
| temporal_sequence_q25 | 7/20 | 108.25 | labeled_positive_sequence_quantile | 1.762162 | 1500 | 92.35 | 8 | 147 | 318 | 1847 |

## Read

- Per-step temporal gating is much worse than positive-only and the
  initial confidence gate on the development split.
- Initial-state q25 calibration over-switches immediately: it chooses
  triage for `2146` of `2253` executed timesteps.
- Sequence-timestep q25 calibration lowers the threshold from `6.180339`
  to `1.762162`, but still chooses triage for `1847` of `2165` executed
  timesteps and remains at `7/20`.
- Do not run a fresh Lift707 screen for this direct temporal router.
  The next useful direction is a policy-training change or a less
  twitchy learned gate with a predeclared hysteresis/persistence rule.

## Artifacts

- Summary CSV: `results/candidate_g_fresh_preflight/candidate_m_temporal_confidence_router_summary.csv`.
- Initial-q25 eval: `results/candidate_g_fresh_preflight/lift606_router_temporal_confidence_labeledpos_q25_eval20/REPORT.md`.
- Sequence-q25 eval: `results/candidate_g_fresh_preflight/lift606_router_temporal_confidence_labeledpos_seq_q25_eval20/REPORT.md`.
