# Candidate S Labeled Initial-Risk Router

**Status: rejected.** Candidate S trains a small balanced logistic
classifier from labeled positive versus labeled negative initial states,
then keeps the positive-only policy unless the classifier score falls
below a labeled-positive quantile.

The primary recipe is policy-feature logistic q25. Other feature sets and
quantiles are diagnostic only.

## Primary q25 Policy-Feature Gate

| split | successes | positive | triage | oracle | switches | threshold |
| --- | --- | --- | --- | --- | --- | --- |
| lift606 | 12/20 | 14/20 | 13/20 | 17/20 | 13 | 0.659325 |
| lift707 | 12/20 | 12/20 | 9/20 | 13/20 | 11 | 0.834395 |

## Diagnostic Ablation Rows

| split | feature_set | quantile | successes | switches | threshold |
| --- | --- | --- | --- | --- | --- |
| lift606 | obs_policy | 0.25 | 14/20 | 16 | 0.830022 |
| lift606 | obs_policy | 0.5 | 14/20 | 17 | 0.928934 |
| lift606 | obs | 0.1 | 13/20 | 4 | 0.387067 |
| lift606 | policy | 0.1 | 13/20 | 8 | 0.460665 |
| lift606 | policy | 0.5 | 13/20 | 17 | 0.8715 |
| lift606 | obs | 0.25 | 12/20 | 8 | 0.470329 |
| lift707 | policy | 0.25 | 12/20 | 11 | 0.834395 |
| lift707 | obs | 0.1 | 11/20 | 8 | 0.414547 |
| lift707 | policy | 0.1 | 11/20 | 9 | 0.743305 |
| lift707 | obs_policy | 0.5 | 10/20 | 13 | 0.92229 |
| lift707 | policy | 0.5 | 10/20 | 13 | 0.901315 |
| lift707 | obs_policy | 0.1 | 9/20 | 11 | 0.875562 |

## Read

- Candidate S does not clear the development gate. The primary q25
  policy-feature gate reaches `12/20` on
  Lift606 versus positive-only `14/20`.
- This means a labeled positive/negative initial classifier is not a
  sufficient branch-quality proxy for the current Lift policy pair.
- Do not spend live endpoint budget on this learned initial-risk gate.

## Artifacts

- Feature CSV: `results/candidate_g_fresh_preflight/candidate_s_labeled_initial_risk_features.csv`.
- Summary CSV: `results/candidate_g_fresh_preflight/candidate_s_labeled_initial_risk_summary.csv`.
- Per-initial CSV: `results/candidate_g_fresh_preflight/candidate_s_labeled_initial_risk_per_initial.csv`.
