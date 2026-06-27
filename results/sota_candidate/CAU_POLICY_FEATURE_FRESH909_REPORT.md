# CAU Policy-Feature Fresh Split909 Screen

This report evaluates a predeclared policy-feature gate on fresh split909.
The gate uses the pooled development rule from the completed CAU policy-feature audit:

- route from positive-only to CAU when `alt_logp_margin_vs_anchor > 0.757864` or `alt_support_margin > 0.837440`.
- `anchor` is positive-only NN and `alt` is CAU action-conflict.
- comparisons below use the first 20 matched valid-positive starts for every method.

## Decision

- Positive-only NN reaches `15/20` on the matched first-20 screen.
- CAU action-conflict alone reaches `9/20`.
- The fixed policy-feature gate reaches `15/20` with `0` gains and `0` losses versus positive-only.
- The best non-gate reference on this first-20 screen is `Positive-only NN / Candidate E gate` at `15/20`.
- This is neutral transfer, not a promotable method result: the fixed rule defers entirely to positive-only on this screen, so it preserves the anchor but does not capture any CAU-helped starts.

## First-20 Matched Starts

| label | screen_score | delta_vs_positive | gains_vs_positive | losses_vs_positive | gate_open_episodes | all_available_score |
| --- | --- | --- | --- | --- | --- | --- |
| Positive-only NN | 15/20 | 0 | 0 | 0 |  | 41/50 |
| Weighted BC | 8/20 | -7 | 1 | 8 |  | 18/50 |
| TRIAGE-BC v0.1 | 8/20 | -7 | 1 | 8 |  | 22/50 |
| Candidate E gate | 15/20 | 0 | 0 | 0 | 1 | 39/50 |
| CAU action-conflict | 9/20 | -6 | 1 | 7 |  | 9/20 |
| CAU policy-feature gate | 15/20 | 0 | 0 | 0 | 0 | 15/20 |

## Artifacts

- Summary CSV: `results/sota_candidate/cau_policy_feature_fresh909_summary.csv`.
- Policy-feature gate eval: `results/sota_candidate/cau_policy_feature_gate_can909_eval20/REPORT.md`.
- CAU action-conflict eval: `results/sota_candidate/cau_action_conflict_can909_b005_m05_eval20/REPORT.md`.
