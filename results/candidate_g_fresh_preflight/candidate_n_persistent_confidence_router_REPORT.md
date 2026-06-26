# Candidate N Persistent Confidence Router

**Status: rejected at the Lift606 development gate.** Candidate N keeps
Candidate M's temporal confidence feature but adds hysteresis: start from
positive-only, require several consecutive low-confidence steps, then
switch to triage for the rest of the episode.

## Lift606 Context

| method | successes | avg_len |
| --- | --- | --- |
| positive_only_nn | 14/20 | 70.25 |
| triage_bc | 13/20 | 78.45 |
| weighted_bc | 6/20 | 124.75 |
| initial_confidence_q25 | 18/20 | 44.8 |
| raw_temporal_sequence_q25 | 7/20 | 108.25 |

## Persistent Screens

| method | successes | avg_len | threshold | threshold_source | persistence_steps | switched_episodes | gate_open_mean | choices_positive | choices_triage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| persistent_sequence_q25_k10 | 13/20 | 74.95 | 1.762162 | labeled_positive_sequence_quantile | 10 | 13 | 56.85 | 528 | 971 |
| persistent_sequence_q25_k20 | 11/20 | 85.25 | 1.762162 | labeled_positive_sequence_quantile | 20 | 9 | 69.5 | 731 | 974 |

## Read

- Persistence repairs most of the raw temporal over-switching damage, but
  it still does not clear the positive-only dev baseline.
- k10 reaches `13/20`, below positive-only `14/20` and far below the
  initial confidence gate `18/20`.
- k20 is stricter but worse at `11/20`, so simply delaying the switch is
  not a useful Lift repair.
- No fresh Lift707 eval was run for Candidate N. The router line should
  stop here unless a learned gate or policy-training change gives a
  stronger development-split signal.

## Artifacts

- Summary CSV: `results/candidate_g_fresh_preflight/candidate_n_persistent_confidence_router_summary.csv`.
- k10 eval: `results/candidate_g_fresh_preflight/lift606_router_persistent_confidence_labeledpos_seq_q25_k10_eval20/REPORT.md`.
- k20 eval: `results/candidate_g_fresh_preflight/lift606_router_persistent_confidence_labeledpos_seq_q25_k20_eval20/REPORT.md`.
