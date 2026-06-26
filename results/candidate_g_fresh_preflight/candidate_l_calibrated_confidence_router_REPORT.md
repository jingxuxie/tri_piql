# Candidate L Calibrated Confidence Router

**Status: rejected.** Candidate L calibrates the Candidate K first-step
GMM confidence threshold from labeled split data instead of carrying one
global threshold across Lift splits.

## Live Calibrated q25 Router

| split | positive | triage | calibrated q25 | effective threshold | choices positive | choices triage |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| lift606 | 14/20 | 13/20 | 18/20 | 6.180339 | 626 | 270 |
| lift707 | 12/20 | 9/20 | 10/20 | 4.164663 | 1207 | 701 |

The calibrated q25 threshold preserves Candidate K's Lift606 screen
result, but it still fails the fresh Lift707 transfer check.

## Development Threshold Transfer

Top one-feature thresholds selected on Lift606, then applied unchanged
to Lift707 using existing positive/triage outcome traces:

| feature | direction | threshold | successes | switches | fresh_successes | fresh_switches |
| --- | --- | --- | --- | --- | --- | --- |
| positive_logp_under_triage | lt | 5.928396 | 16 | 3 | 11 | 8 |
| positive_logp_under_triage | lt | 6.269868 | 16 | 4 | 11 | 10 |
| positive_entropy | lt | 1.212422 | 16 | 6 | 10 | 7 |
| positive_logp_margin_vs_triage | gt | 1.98351 | 16 | 6 | 9 | 13 |
| positive_entropy | lt | 1.232623 | 16 | 7 | 10 | 8 |
| positive_logp_margin_vs_triage | gt | 1.648598 | 16 | 7 | 9 | 14 |
| positive_top_prob | gt | 0.483061 | 16 | 7 | 10 | 3 |
| positive_logp_margin_vs_triage | gt | 1.389582 | 16 | 8 | 9 | 16 |
| positive_top_prob | gt | 0.474613 | 16 | 8 | 10 | 4 |
| positive_logp_margin_vs_triage | gt | 1.214422 | 16 | 9 | 9 | 16 |

## Fresh-Split Upper Bound

This table is leaky and diagnostic only. It asks whether any one-step
feature could have beaten positive-only on Lift707 if tuned on the
same starts:

| feature | direction | threshold | successes | episodes | switches |
| --- | --- | --- | --- | --- | --- |
| triage_minus_positive_logit_gap | gt | 0.795782 | 13 | 20 | 1 |
| triage_minus_positive_logit_gap | gt | 0.745513 | 13 | 20 | 2 |
| triage_minus_positive_top_prob | gt | 0.209232 | 13 | 20 | 2 |
| triage_minus_positive_logit_gap | gt | 0.697046 | 13 | 20 | 3 |
| triage_minus_positive_top_prob | gt | 0.196373 | 13 | 20 | 3 |
| positive_logp_margin_vs_triage | lt | 1.543361 | 13 | 20 | 5 |
| triage_logp_margin_vs_positive | gt | 3.104578 | 13 | 20 | 7 |
| positive_support_margin | lt | 0.574561 | 13 | 20 | 9 |
| triage_logp_under_positive | lt | 4.918347 | 13 | 20 | 10 |
| triage_logp_under_positive | lt | 5.233951 | 13 | 20 | 11 |

## Read

- None of the best Lift606-selected one-feature thresholds beats
  positive-only on Lift707 (`12/20`); the best reaches
  `11/20`.
- The leaky Lift707 upper bound is `13/20`, only one
  success above positive-only, so initial confidence routing is a weak
  abstraction for this Lift setting.
- Candidate L should not be scaled as a frozen method. The next high-value
  direction is temporal gating or a candidate that changes the trained policy,
  not another fixed initial threshold.

## Artifacts

- Feature CSV: `results/candidate_g_fresh_preflight/candidate_l_lift_cross_split_confidence_features.csv`.
- Transfer audit CSV: `results/candidate_g_fresh_preflight/candidate_l_lift606_to_707_threshold_transfer.csv`.
- Fresh leaky audit CSV: `results/candidate_g_fresh_preflight/candidate_l_lift707_fresh_leaky_threshold_audit.csv`.
- Lift606 q25 live eval: `results/candidate_g_fresh_preflight/lift606_router_confidence_labeledpos_q25_eval20/REPORT.md`.
- Lift707 q25 live eval: `results/candidate_g_fresh_preflight/lift707_router_confidence_labeledpos_q25_eval20/REPORT.md`.
