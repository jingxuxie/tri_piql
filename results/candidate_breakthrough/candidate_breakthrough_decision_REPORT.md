# Candidate-Breakthrough Decision Report

**Status: no general methods-dominance claim yet.** The current search
produced one clean Can-only discovery result, but the predeclared fresh
Can validation gate failed early and the Lift follow-ups reject the
deployable routers and simple anchor-union policy-training variants
tested so far.

## Decision Summary

| area | status | key_result | decision | artifact |
| --- | --- | --- | --- | --- |
| Can discovery matrix | promising but scoped | Candidate F 198/250 vs positive 174/250, weighted 158/250, triage 171/250, per-split oracle 192/250 | Keep as Can 40p/80b discovery evidence, not a general robotics claim. | results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md |
| Fresh Can smokes | neutral | Candidate F 31/40 ties positive-only 31/40; weighted is 29/40 | Historical smoke only; superseded by the failed predeclared fresh validation matrix. | results/candidate_g_fresh_preflight/candidate_f_fresh_can_smokes_REPORT.md |
| Fresh Can validation | failed early | Candidate F 81/100 vs best completed baselines 84/100; worse on 2/2 completed validation rows, while the 4/5 no-worse gate allows at most 1 | Stop Candidate F scaling; the predeclared fresh validation gate is already impossible. | results/candidate_f_can_fresh_validation/tables/candidate_f_can_fresh_validation_STATUS.md |
| Lift transfer | not transferred | Can-style Candidate F transfer 145/250 vs Lift oracle 154/250; tail-severity diagnostic 154/250 is not frozen | Treat Lift as a limitation or abstention case until a new frozen proxy exists. | results/candidate_breakthrough/candidate_f_lift_transfer_audit_REPORT.md |
| Lift routers | rejected | Best local confidence gate 32/50 beats Lift606 positive 28/50, but transfers to Lift707 at 10/20 vs positive 12/20; temporal 7/20, persistent 13/20 | Stop scalar initial-threshold, temporal-confidence, and persistence router tuning. | results/candidate_g_fresh_preflight/candidate_k_confidence_router_screen_REPORT.md |
| Anchor-union training | rejected | Positive-init fine-tune 11/20 and best Q/R rescue 11/20 remain below positive-only 14/20 | Stop lower-weight triage-extra BC targets; a future training candidate needs a different objective. | results/candidate_g_fresh_preflight/candidate_qr_anchor_protection_screen_REPORT.md |
| Transition-level objectives | rejected | Can404 sequence-mask 16/20 and best negative-action hinge 14/20 remain below positive-only 17/20 | Stop the current transition-weight, sequence-mask, and nearest-negative hinge recipes unchanged. | results/candidate_breakthrough/candidate_d_endpoint_screen_REPORT.md |
| Policy interpolation | rejected | Best Can404 positive-to-weighted interpolation 16/20 at alpha 0.05 vs positive-only 17/20 | Stop naive parameter interpolation; anchor preservation needs an explicit objective, not weight averaging. | results/candidate_breakthrough/candidate_t_policy_interpolation_screen_REPORT.md |
| Anchor-L2 fine-tuning | neutral/rejected | Best Can404 positive-initialized sequence-mask fine-tune 17/20 at epoch 5 vs positive-only 17/20 | Do not scale normalized parameter-L2 anchoring; use output-level anchoring or a different objective if continuing training-side work. | results/candidate_breakthrough/candidate_u_anchor_l2_screen_REPORT.md |
| Output-anchor fine-tuning | failed first validation | Best Can404 first-20 output-anchor checkpoint 18/20 vs positive-only 17/20; Can404 50-episode check 39/50 ties positive-only 39/50; frozen Can505 check 38/50 vs positive-only 40/50 | Do not scale as a paper-facing method; output anchoring is informative but failed the first non-404 validation gate. | results/candidate_breakthrough/candidate_v_anchor_logprob_screen_REPORT.md |
| Two-feature weighted-rescue gate | diagnostic/rejected | Candidate W 85/100 ties Candidate E 85/100 over splits 404+505; split404 46/50 but split505 39/50 vs positive-only 40/50 | Do not promote scalar initial support-distance plus margin gating; it preserves the known rescue but does not clear validation. | results/candidate_breakthrough/candidate_w_two_feature_gate_REPORT.md |
| Labeled initial-risk gate | rejected | Primary q25 policy gate: Lift606 12/20 vs positive 14/20; Lift707 12/20 vs positive 12/20 | Do not spend live endpoint budget on this learned initial-risk proxy. | results/candidate_g_fresh_preflight/candidate_s_labeled_initial_risk_router_REPORT.md |

## Candidate F Can Discovery Matrix

| split | candidate_f_source | positive | weighted | triage | best_baseline | candidate_f | delta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | weighted_anchor | 19/50 | 37/50 | 28/50 | 37/50 | 37/50 | 0 |
| 202 | candidate_e_gate | 40/50 | 33/50 | 36/50 | 40/50 | 40/50 | 0 |
| 303 | candidate_e_gate | 36/50 | 25/50 | 35/50 | 36/50 | 36/50 | 0 |
| 404 | candidate_e_gate | 39/50 | 33/50 | 36/50 | 39/50 | 46/50 | 7 |
| 505 | candidate_e_gate | 40/50 | 30/50 | 36/50 | 40/50 | 39/50 | -1 |
| total |  | 174/250 | 158/250 | 171/250 | 192/250 | 198/250 | 6 |

Read: Candidate F is the strongest completed candidate on Can 40p/80b,
but most of its aggregate edge comes from the split-404 rescue. It should
be reported as scoped Can evidence.

## Fresh Can Smoke Check

| method | successes |
| --- | --- |
| candidate_f | 31/40 |
| positive_only_nn | 31/40 |
| candidate_e_gate | 29/40 |
| weighted_bc | 29/40 |
| triage_bc | 10/20 |

Read: the two fresh first-20 Can smokes are neutral. They do not erase the
Can discovery matrix, but they did not justify a methods claim by themselves.

## Fresh Can Frozen Validation

| seed | candidate_f_branch | positive | weighted | triage | candidate_f | best_baseline | delta | no_worse |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 808 | candidate_e_gate | 43/50 | 25/50 | 16/50 | 42/50 | 43/50 | -1 | 0 |
| 909 | candidate_e_gate | 41/50 | 18/50 | 22/50 | 39/50 | 41/50 | -2 | 0 |

Read: the predeclared fresh Can validation matrix failed early. Candidate F
is worse than the best completed baseline on both completed validation
rows, so the 4/5 no-worse gate is impossible even before running the
remaining seeds.

## Lift Transfer Check

| split | positive | weighted | triage | best | can_style | tail_severity |
| --- | --- | --- | --- | --- | --- | --- |
| 101 | 28/50 | 31/50 | 36/50 | 36/50 | 31/50 | 36/50 |
| 202 | 25/50 | 30/50 | 34/50 | 34/50 | 30/50 | 34/50 |
| 303 | 21/50 | 19/50 | 20/50 | 21/50 | 21/50 | 21/50 |
| 404 | 25/50 | 30/50 | 29/50 | 30/50 | 30/50 | 30/50 |
| 505 | 26/50 | 33/50 | 24/50 | 33/50 | 33/50 | 33/50 |
| total | 125/250 | 143/250 | 143/250 | 154/250 | 145/250 | 154/250 |

Read: direct Can-style transfer is below the Lift per-split baseline
oracle. The tail-severity rule is diagnostic because the mild/severe
cutoff was discovered after looking at completed Lift rows.

## Recommended Paper Action

- Keep the main paper framing as a precision-coverage study, with
  controlled diagnostics and careful Robomimic branch-selection results.
- Move Candidate F to scoped Can discovery / failed-development evidence;
  do not spend more endpoint budget on the remaining fresh validation seeds
  for a methods-dominance claim.
- Treat Lift as a limitation/abstention case for now. The tested router
  proxies and anchor-union policy-training variants should not be tuned
  further without a materially different objective or proxy.
- Do not claim weighted BC is bad. The evidence says weighted BC is strong
  in some coverage-heavy regimes and hard/anchor support is strong in
  others.

## Artifacts

- Decision CSV: `results/candidate_breakthrough/candidate_breakthrough_decision_summary.csv`.
- Can matrix: `results/candidate_breakthrough/candidate_f_frozen_matrix_REPORT.md`.
- Fresh Can smokes: `results/candidate_g_fresh_preflight/candidate_f_fresh_can_smokes_REPORT.md`.
- Fresh Can validation: `results/candidate_f_can_fresh_validation/tables/candidate_f_can_fresh_validation_STATUS.md`.
- Lift transfer audit: `results/candidate_breakthrough/candidate_f_lift_transfer_audit_REPORT.md`.
- Lift router reports: `results/candidate_g_fresh_preflight/candidate_k_confidence_router_screen_REPORT.md`,
  `results/candidate_g_fresh_preflight/candidate_l_calibrated_confidence_router_REPORT.md`,
  `results/candidate_g_fresh_preflight/candidate_m_temporal_confidence_router_REPORT.md`, and
  `results/candidate_g_fresh_preflight/candidate_n_persistent_confidence_router_REPORT.md`.
- Training-side reports: `results/candidate_g_fresh_preflight/candidate_o_lift_anchor_union_screen_REPORT.md`,
  `results/candidate_g_fresh_preflight/candidate_p_posinit_anchor_union_screen_REPORT.md`, and
  `results/candidate_g_fresh_preflight/candidate_qr_anchor_protection_screen_REPORT.md`.
- Transition-level reports: `results/candidate_breakthrough/candidate_a_endpoint_screen_REPORT.md`,
  `results/candidate_breakthrough/candidate_c_endpoint_screen_REPORT.md`, and
  `results/candidate_breakthrough/candidate_d_endpoint_screen_REPORT.md`.
- Policy-composition and anchor reports: `results/candidate_breakthrough/candidate_t_policy_interpolation_screen_REPORT.md`,
  `results/candidate_breakthrough/candidate_u_anchor_l2_screen_REPORT.md`, and
  `results/candidate_breakthrough/candidate_v_anchor_logprob_screen_REPORT.md`.
- Candidate V failure analysis: `results/candidate_breakthrough/candidate_v_failure_analysis_REPORT.md`.
- Candidate W two-feature gate: `results/candidate_breakthrough/candidate_w_two_feature_gate_REPORT.md`.
- Learned initial-risk report: `results/candidate_g_fresh_preflight/candidate_s_labeled_initial_risk_router_REPORT.md`.
