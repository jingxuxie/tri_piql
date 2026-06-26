# Candidate K Lift606 Confidence-Feature Audit

Candidate K asks whether richer deployable first-step policy features can
identify when Lift606 should leave the positive-only anchor for triage.
This is an offline audit over existing first-20 rollouts, not a validated
router result.

## Outcome Ceiling

- Positive-only: `14/20`.
- Triage: `13/20`.
- Weighted: `6/20`.
- Non-deployable oracle over the three policies: `17/20`.
- Best one-feature positive-to-triage threshold in this audit: `16/20`.

## Best One-Feature Gates

| feature | direction | threshold | successes | episodes | switches |
| --- | --- | --- | --- | --- | --- |
| positive_logp_under_triage | lt | 5.928396 | 16 | 20 | 3 |
| positive_logp_under_triage | lt | 6.269868 | 16 | 20 | 4 |
| positive_entropy | lt | 1.212422 | 16 | 20 | 6 |
| positive_entropy | lt | 1.232623 | 16 | 20 | 7 |
| positive_top_prob | gt | 0.483061 | 16 | 20 | 7 |
| positive_top_prob | gt | 0.474613 | 16 | 20 | 8 |
| triage_minus_positive_support_margin | lt | -0.008534 | 16 | 20 | 15 |
| triage_minus_positive_support_margin | lt | -0.000362 | 16 | 20 | 16 |

## Read

- Unlike nearest support-margin routing, at least one first-step
  confidence feature beats positive-only in this exploratory audit.
- This is post-hoc on 20 starts, so it is only a candidate generator.
  The next step is a tiny live router evaluation with the simplest
  winning feature and then a fresh split check if it survives.

## Artifacts

- Feature CSV: `results/candidate_g_fresh_preflight/candidate_k_lift_confidence_features.csv`.
- Threshold audit CSV: `results/candidate_g_fresh_preflight/candidate_k_lift_confidence_threshold_audit.csv`.
