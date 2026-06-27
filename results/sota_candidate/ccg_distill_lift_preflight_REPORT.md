# CCG-Distill Lift Preflight

This is the SOTA Candidate 3 preflight from `triage_bc_sota_candidate_plan.md`.
It asks whether the existing Lift specialist/gate evidence is strong enough to justify a new distillation training run.

## Decision

**Status: preflight no-go.** Do not spend a fresh CCG-Distill train/eval cycle until the teacher-selection signal improves.

The planned go/no-go criterion was to beat positive-only on both Lift606 and Lift707.
Existing evidence does not clear the teacher-quality bar:

- Tuned first-step confidence router on Lift606: `18/20` versus positive-only `14/20`.
- The same fixed router on Lift707: `10/20` versus positive-only `12/20`.
- Best Lift606-selected threshold transferred to Lift707: `11/20`.
- Even the leaky Lift707 one-feature upper bound reaches only `13/20`.
- Best direct temporal/persistent confidence router on Lift606: `13/20`.
- Best single-policy anchor-union training proxy on Lift606: `11/20`.

## Summary Table

| evidence | split | method | successes | delta vs positive | note |
| --- | --- | --- | ---: | ---: | --- |
| live_router | lift606 | positive_only_nn | 14/20 | 0 | Candidate K first-step confidence screen. |
| live_router | lift606 | triage_bc | 13/20 | -1 | Candidate K first-step confidence screen. |
| live_router | lift606 | weighted_bc | 6/20 | -8 | Candidate K first-step confidence screen. |
| live_router | lift606 | confidence_router_thr6p27 | 18/20 | 4 | Candidate K first-step confidence screen. |
| live_router | lift707 | positive_only_nn | 12/20 | 0 | Candidate K fixed threshold transfer. |
| live_router | lift707 | triage_bc | 9/20 | -3 | Candidate K fixed threshold transfer. |
| live_router | lift707 | confidence_router_thr6p27 | 10/20 | -2 | Candidate K fixed threshold transfer. |
| calibrated_transfer | lift707 | best_lift606_selected_positive_logp_under_triage | 11/20 | -1 | Best Lift606-selected one-feature threshold transferred to Lift707. |
| leaky_upper_bound | lift707 | best_lift707_leaky_triage_minus_positive_logit_gap | 13/20 | 1 | Diagnostic only: threshold selected on the same Lift707 starts. |
| temporal_router | lift606 | temporal_initial_q25 | 7/20 | -7 | Per-step confidence gate. |
| temporal_router | lift606 | temporal_sequence_q25 | 7/20 | -7 | Per-step confidence gate. |
| persistent_router | lift606 | persistent_sequence_q25_k10 | 13/20 | -1 | Temporal gate with hysteresis. |
| persistent_router | lift606 | persistent_sequence_q25_k20 | 11/20 | -3 | Temporal gate with hysteresis. |
| training_side_anchor_union | lift606 | candidate_o_epoch50 | 1/20 | -13 | anchor_union_from_scratch: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | candidate_o_epoch100 | 5/20 | -9 | anchor_union_from_scratch: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | candidate_p_epoch20_posinit_finetune | 11/20 | -3 | positive_initialized_union: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | model_epoch_1 | 10/20 | -4 | candidate_q_short_finetune: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | model_epoch_2 | 10/20 | -4 | candidate_q_short_finetune: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | model_epoch_3 | 9/20 | -5 | candidate_q_short_finetune: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | model_epoch_4 | 11/20 | -3 | candidate_q_short_finetune: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | model_epoch_5 | 10/20 | -4 | candidate_q_short_finetune: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | pos_to_anchor_union_p20_alpha_0p05 | 11/20 | -3 | candidate_r_interpolation: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | pos_to_anchor_union_p20_alpha_0p10 | 10/20 | -4 | candidate_r_interpolation: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | pos_to_anchor_union_p20_alpha_0p20 | 10/20 | -4 | candidate_r_interpolation: closest prior evidence for training a single policy from mixed specialists. |
| training_side_anchor_union | lift606 | pos_to_anchor_union_p20_alpha_0p35 | 10/20 | -4 | candidate_r_interpolation: closest prior evidence for training a single policy from mixed specialists. |
| learned_initial_risk_gate | lift606 | policy_feature_logistic_q25 | 12/20 | -2 | Balanced labeled positive/negative initial-state classifier. |
| learned_initial_risk_gate | lift707 | policy_feature_logistic_q25 | 12/20 | 0 | Balanced labeled positive/negative initial-state classifier. |

## Read

- Candidate K showed real development-split headroom, so the policy set is not hopeless.
- Candidate L/S show that labeled split calibration and learned initial-risk classification do not recover that headroom on Lift707.
- Candidate M/N show that using the confidence feature per step is too twitchy even with persistence.
- Candidate O/P/Q/R show that naive single-policy training over positive plus triage support damages the positive-only anchor.
- A CCG-Distill implementation would mainly distill a weak/non-transferring gate, so the expected value is lower than moving to a genuinely different objective such as the Offline RL/IQL revisit.

## Artifacts

- Summary CSV: `results/sota_candidate/ccg_distill_lift_preflight_summary.csv`.
- Source router reports: `results/candidate_g_fresh_preflight/candidate_k_confidence_router_screen_REPORT.md`, `candidate_l_calibrated_confidence_router_REPORT.md`, `candidate_m_temporal_confidence_router_REPORT.md`, `candidate_n_persistent_confidence_router_REPORT.md`.
- Source training-side reports: `results/candidate_g_fresh_preflight/candidate_o_lift_anchor_union_screen_REPORT.md`, `candidate_p_posinit_anchor_union_screen_REPORT.md`, `candidate_qr_anchor_protection_screen_REPORT.md`.
