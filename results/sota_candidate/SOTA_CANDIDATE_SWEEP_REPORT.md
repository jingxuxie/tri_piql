# SOTA Candidate Sweep Summary

This report aggregates the focused candidate sweep from `triage_bc_sota_candidate_plan.md`.
It is intended as paper-facing claim-boundary evidence, not as a new method result.

## Decision

- The focused SOTA-candidate sweep is negative: no candidate clears its first-stage gate.
- The best Can404 endpoint candidates in this sweep reach `16/20`, while the matched positive-only anchor is `17/20`.
- CCG-Distill has development headroom on Lift606, but the fixed confidence signal fails the Lift707 transfer gate.
- First-state policy-distribution features improve the offline CAU selector audit, but the pooled frozen rule transfers neutrally on fresh split909 by opening no CAU starts.
- A linear learned router over those policy features also fails, opening all CAU starts on fresh split909.
- A per-step support-margin router is the strongest current sequence-aware diagnostic, but the two 50-episode no-retune checks are not enough for a method claim.
- The paper should stay framed as a precision/coverage empirical study unless a future router or state-conditional policy-quality signal captures CAU-dominant splits while preserving positive-only anchors.

## Aggregate Table

| candidate | primary gate | best candidate | positive | best matched reference | delta vs positive | status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1. Sequence-Masked Risk-Weighted BC | Can404 valid-positive starts | 10/20 | 17/20 | 17/20 | -7 | reject |
| 2. Contrastive Action-Unlikelihood BC | Can404 valid-positive starts | 16/20 | 17/20 | 17/20 | -1 | reject |
| 3. Conformal Confidence-Gated Specialist Distillation | Lift707 fixed-threshold transfer | 10/20 | 12/20 | 12/20 | -2 | preflight_no_go |
| 4. Safe Support Expansion | Can404 valid-positive starts | 12/20 | 17/20 | 17/20 | -5 | reject |
| 5. Preference-Style Sequence Objective | Can404 valid-positive starts | 16/20 | 17/20 | 17/20 | -1 | reject |
| 6. Classifier-Reward IQL-AWBC | Can404 valid-positive starts | 13/20 | 17/20 | 17/20 | -4 | reject |

## Readout

- Support or transition-mass diagnostics were not sufficient predictors of endpoint success: SM-RWBC, SafeExpand, and IQL-AWBC improved local diagnostics but failed Can404.
- Action-level and preference-style objectives can match the older Candidate C screen but still do not beat the positive-only anchor.
- The Can404 anchor-overlap audit shows the near-miss candidates trade away positive-only successes: CAU gains 2 starts but loses 3 positive-only starts, while Demo-DPO gains 1 and loses 2.
- A post-hoc feature-gate upper bound gives one CAU-plus-positive hypothesis at 18/20 with zero same-screen anchor losses, but the threshold is selected on Can404 endpoint outcomes and must be treated as a fresh-validation hypothesis only.
- The frozen CAU-plus-positive fallback passes one fresh split-505 screen and its 50-episode confirmation: first-20 routed 16/20 versus positive-only 15/20; 50-episode routed 41/50 versus positive-only 40/50; both have 0 anchor losses at epoch 200.
- The next predeclared fresh split-303 screen is neutral for the deployable fallback: CAU alone reaches 17/20, but routed fallback remains 15/20 versus positive-only 15/20, with 0 anchor losses.
- A two-feature gate selected on completed 303/404/505 screens (`initial_anchor_pos_dist_mean <= 1.273665 or initial_anchor_neg_dist_mean > 3.131861`) has stronger fresh follow-up but still does not clear a methods/SOTA bar: split101 confirms at 24/50 routed versus positive-only 19/50 with 0 losses, while split202 50-episode confirmation is neutral at 40/50 versus 40/50 despite CAU alone reaching 42/50.
- The 50-episode five-split CAU-alone follow-up changes the original first20 readout from a hard rejection to a useful method seed: CAU reaches 193/250 versus positive-only 174/250, weighted BC 158/250, TRIAGE-BC v0.1 171/250, and best old baseline per split 192/250; it still trails v0.2 selected union 197/250 and the best non-oracle per split including v0.2.
- A post-hoc CAU-plus-v0.2 portfolio preflight was the best pre-fresh hypothesis, not claim evidence: `estimated_positive_mass_gt_47.631032` selects CAU on splits 303;404;505 and v0.2 on splits 101;202, reaching 208/250 (+11 versus always-v0.2, +15 versus always-CAU).
- The first fresh split606 endpoint validation rejects promoting that portfolio unchanged: the gate-selected CAU branch reaches 15/20 versus positive-only 16/20; frozen v0.2 union reaches 14/20, the cleaner risk-fusion diagnostic reaches 15/20, and the proper 130-demo expanded-mask CAU diagnostic reaches 12/20.
- The GMM-confidence router follow-up gives a useful negative/positive split: labeled q25 calibration is neutral on split606 at 16/20, a same-screen split606 threshold can reach 18/20 but is post-hoc, and that frozen threshold fails split707 at 15/20 while CAU alone reaches 20/20 first-20 and 50/50 on the 50-episode confirmation versus positive-only 36/50 and weighted BC 39/50.
- The next fixed-CAU validation on split808 is negative against the strongest baseline: CAU reaches 38/50 versus positive-only 43/50 and the older Candidate E gate 42/50. This turns the split707 win into useful heterogeneity evidence, not a promotable fixed-method dominance result.
- The leave-one-split-out CAU selector feature audit confirms that the remaining headroom is not captured by simple initial support-distance features: positive-only is 269/370, always-CAU is 296/370, and the per-episode oracle switch is 331/370; the safe selector reaches 263/370 with 7 gains and 13 losses, while the best-delta selector reaches 277/370 with 31 gains and 23 losses.
- Replacing support-distance features with first-state policy-distribution features gives a stronger offline selector signal but still does not create a deployable router: positive-only is 269/370, always-CAU is 296/370, and the per-episode oracle switch is 331/370; the safe held-out selector reaches 276/370 with 29 gains and 22 losses, while the best-delta selector reaches 299/370 with 44 gains and 14 losses. The pooled frozen rule on fresh split909 reaches 15/20 versus positive-only 15/20 and CAU-alone 9/20, with 0 CAU opens.
- A linear learned router over the same first-state policy features also fails the transfer test: LOO safe reaches 277/370 with 25 gains and 17 losses, while LOO best-delta reaches 278/370 with 26 gains and 17 losses. Training on completed splits and freezing to split909 opens all CAU starts, giving 9/20 safe and 9/20 best-delta versus positive-only 15/20.
- The per-step support-margin router is the strongest sequence-aware CAU follow-up so far, but it remains a validation candidate rather than a paper claim: fixed threshold 0.05 aggregates to 51/60 across splits 909/808/707 versus positive-only 47/60 and CAU 43/60, with 5 gains and 1 loss versus positive-only. Per split it reaches 16/20 on split909, 18/20 on split808, and 17/20 on split707. The first no-retune held-out guardrail on split606 is neutral at 16/20 versus positive-only 16/20 and CAU 15/20; including split606, the same threshold is 67/80 versus positive-only 63/80 and CAU 58/80. The 50-episode split606 validation is stronger: 42/50 router versus positive-only 38/50 and CAU 41/50, with 7 gains and 3 losses versus positive-only. The next 50-episode split101 no-retune check is mixed-negative: 25/50 versus positive-only 19/50 but below CAU 33/50. Across these two 50-episode validations, the router is 67/100 versus positive-only 57/100 and CAU 74/100, with 15 gains and 5 losses versus positive-only. A persistent support-margin variant also fails split101, reaching 20/50 versus non-persistent 25/50 and CAU 33/50.
- The IQL-AWBC branch is especially diagnostic: classifier-reward advantages separated labeled positives and negatives offline, yet extraction collapsed without anchoring and remained weak with anchoring.
- The responsible paper use remains a development appendix: CAU action-conflict is a useful but inconsistent Can method seed, and the hidden-label-free router needed to preserve anchors and select it is still unresolved.

## Artifacts

- Summary CSV: `results/sota_candidate/sota_candidate_sweep_summary.csv`.
- Anchor-overlap report: `results/sota_candidate/CAN404_ANCHOR_OVERLAP_REPORT.md`.
- Anchor feature-gate preflight: `results/sota_candidate/CAN404_ANCHOR_FEATURE_GATE_PREFLIGHT_REPORT.md`.
- CAU fallback fresh split-505 validation: `results/sota_candidate/CAN505_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md`.
- CAU fallback fresh split-303 validation: `results/sota_candidate/CAN303_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md`.
- CAU two-feature gate audit: `results/sota_candidate/CAU_GATE_FEATURE_AUDIT_REPORT.md`.
- CAU two-feature gate fresh validation: `results/sota_candidate/CAU_TWO_FEATURE_GATE_FRESH_VALIDATION_REPORT.md`.
- CAU five-split endpoint follow-up: `results/sota_candidate/CAU_ACTION_CONFLICT_CAN_FIVE_SPLIT_ENDPOINT_REPORT.md`.
- CAU plus v0.2 portfolio preflight: `results/sota_candidate/CAU_V02_PORTFOLIO_PREFLIGHT_REPORT.md`.
- CAU plus v0.2 fresh606 validation: `results/sota_candidate/CAU_V02_FRESH606_ENDPOINT_VALIDATION_REPORT.md`.
- CAU/GMM router follow-up: `results/sota_candidate/CAU_GMM_ROUTER_FOLLOWUP_REPORT.md`.
- CAU selector feature LOO audit: `results/sota_candidate/CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md`.
- CAU policy-feature selector LOO audit: `results/sota_candidate/CAU_POLICY_FEATURE_SELECTOR_LOO_AUDIT_REPORT.md`.
- CAU policy-feature fresh split909 screen: `results/sota_candidate/CAU_POLICY_FEATURE_FRESH909_REPORT.md`.
- CAU policy-feature learned-router audit: `results/sota_candidate/CAU_POLICY_FEATURE_LEARNED_ROUTER_AUDIT_REPORT.md`.
- CAU sequence support-margin router: `results/sota_candidate/CAU_SEQUENCE_SUPPORT_ROUTER_REPORT.md`.
- Candidate 1 report: `results/sota_candidate/sm_rwbc_can404_screen_REPORT.md`.
- Candidate 2 report: `results/sota_candidate/cau_action_conflict_can404_screen_REPORT.md`.
- Candidate 3 report: `results/sota_candidate/ccg_distill_lift_preflight_REPORT.md`.
- Candidate 4 report: `results/sota_candidate/safeexpand_can404_screen_REPORT.md`.
- Candidate 5 report: `results/sota_candidate/demo_preference_can404_screen_REPORT.md`.
- Candidate 6 report: `results/sota_candidate/anchored_iql_awbc_can404_screen_REPORT.md`.
