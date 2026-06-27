# Final Claim Contract

This file is the paper-facing contract for the current TRIAGE-BC evidence package. It freezes what the manuscript may claim, what it must not claim, and which artifacts support the final story. It is deliberately narrower than a methods-dominance claim.

## Paper Position

TRIAGE-BC should be presented as a precision/coverage study with a frozen portfolio-router method component.

Central claim:

> Offline imitation from scarce trusted successes, scarce known failures, and a mixed unlabeled log is a score-to-support conversion problem. Failure demonstrations can help when they improve the precision/coverage frontier of policy-training support, but strong positive-only retrieval, broad weighted coverage, and abstention remain first-class alternatives.

This is not a validated inverse-Q robotics method. The robotics evidence validates score-calibrated support conversion with official Robomimic BC-RNN-GMM policies, not the full inverse-Q / Tri-PIQL actor-extraction objective.

## Main Claims Allowed

| Claim | Allowed strength | Evidence |
|---|---|---|
| Mixed logs can hurt naive cloning. | Main paper. | PointNav mixed-log degradation; Lift MG all-demo `31/150`; Can 40p/80b all-demo `81/150`. |
| Scarce bad labels can help recover hidden-good support when positives are incomplete. | Main mechanism claim. | PointNav score-gap support reaches `1.000` success with `n_+=n_-=2`; generated Can prefix-positive reaches `119/150` versus `6/150`. |
| Hard support can beat weighted sampling in action-conflict regimes. | Narrow main/diagnostic claim. | Can 40p/80b TRIAGE-BC `99/150` versus weighted BC `90/150`; hard-negative Can `104/150` versus `91/150`. |
| Broad weighted coverage can win when coverage dominates. | Main caveat and mechanism claim. | Lift MG weighted BC is strongest at `93/150`; Can MG stress rows favor weighted BC at `0.333`. |
| Generated Can regime probes identify where failures help. | Main diagnostic claim, not default benchmark claim. | `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`: hard-negative `104/150` versus `91/150`, coverage-shift `120/150` versus `103/150`, prefix-positive `119/150` versus `6/150`. |
| v0.2 portfolio routing is plausible but fragile. | Very cautious method evidence. | Fresh Can+Lift selected branches are barely positive at `340/500` versus `338/500`; router regret `23/500` versus `64/500` for always positive-only NN and `62/500` for always weighted BC. |
| Policy-quality prediction remains open. | Main limitation. | Proxy no-go table, action-risk endpoint no-go, and Can MG abstention diagnostics. |
| Focused SOTA-candidate search is still not promotable, and CAU action-conflict is useful but inconsistent. | Claim-boundary evidence only. | `results/sota_candidate/SOTA_CANDIDATE_SWEEP_REPORT.md`: best Can404 short-screen candidates reach `16/20` versus positive-only `17/20`; CCG transfer reaches `10/20` versus positive-only `12/20`; anchored IQL-AWBC reaches `13/20`. `results/sota_candidate/CAN404_ANCHOR_OVERLAP_REPORT.md` shows CAU gains 2 starts but loses 3 positive-only starts, while Demo-DPO gains 1 and loses 2. `results/sota_candidate/CAN404_ANCHOR_FEATURE_GATE_PREFLIGHT_REPORT.md` gives a post-hoc CAU fallback hypothesis; `results/sota_candidate/CAN505_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md` gives one positive frozen-threshold fresh split: `16/20` routed versus `15/20` positive-only on the first-20 screen and `41/50` routed versus `40/50` positive-only on the 50-episode confirmation, both with zero anchor losses. `results/sota_candidate/CAN303_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md` is neutral for the deployable fallback: CAU alone reaches `17/20`, but routed fallback remains `15/20` versus positive-only `15/20` with zero losses. `results/sota_candidate/CAU_TWO_FEATURE_GATE_FRESH_VALIDATION_REPORT.md` is stronger but still unpromoted: split101 reaches `24/50` routed versus `19/50` positive-only, while split202 is neutral at `40/50` routed versus `40/50` positive-only despite CAU alone reaching `42/50`. `results/sota_candidate/CAU_ACTION_CONFLICT_CAN_FIVE_SPLIT_ENDPOINT_REPORT.md` shows CAU-alone reaches `193/250`, beating positive-only `174/250`, weighted BC `158/250`, TRIAGE-BC v0.1 `171/250`, and best old baseline per split `192/250`, but still trailing v0.2 selected union `197/250`. `results/sota_candidate/CAU_V02_FRESH606_ENDPOINT_VALIDATION_REPORT.md` rejects the post-hoc CAU-plus-v0.2 portfolio on split606: gate-selected CAU reaches `15/20` versus positive-only `16/20`, and the proper 130-demo expanded-mask diagnostic reaches `12/20`. `results/sota_candidate/CAU_GMM_ROUTER_FOLLOWUP_REPORT.md` shows the GMM router does not transfer; CAU-alone is strong on split707 (`50/50` versus positive-only `36/50` and weighted BC `39/50`) but loses the next split808 validation to positive-only (`38/50` versus `43/50`). `results/sota_candidate/CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md` shows remaining selector headroom but no deployable support-distance rule: positive-only is `269/370`, always-CAU is `296/370`, oracle switch is `331/370`, safe LOO selection is `263/370`, and best-delta LOO selection is `277/370` with `23` losses. |

## Mandatory Caveats

- Positive-only NN is the strongest non-oracle frozen Can 40p/80b row: `108/150` versus TRIAGE-BC `99/150` and weighted BC `90/150`.
- Weighted BC is strongest on frozen Lift MG: `93/150` versus positive-only NN `82/150` and TRIAGE-BC `74/150`.
- The v0.2 fresh gate is not a formal significance claim. Paired-bootstrap intervals cross zero for Can, Lift, and combined.
- The v0.2 fresh gate is a selected-vs-strong-baseline/v0.1 audit; optional fresh all-demo/all-positive diagnostic categories are represented (`4/4` with at least one split each) but remain partial-by-split controls and must not be implied as a complete fresh leaderboard.
- Endpoint rollouts are not fully independent because they reuse validation-positive start pools within split seeds.
- The correct framing is a score-to-support conversion problem, not a universal algorithmic superiority claim.
- The Lift and Can MG evidence shows broad weighted coverage can beat purer hard support.
- The generated Lift hard-negative endpoint gate is exploratory only: completed splits `101/202/303` are `15/150` versus `5/150`, with selected support of 82 hidden positives and 38 hidden bad demos versus 12 hidden positives and 108 hidden bad demos. Absolute success remains low, so this is non-Can mechanism evidence rather than a primary endpoint claim.
- The focused SOTA-candidate sweep should not be promoted as a method result: SM-RWBC, CCG-Distill, SafeExpand, Demo-DPO, and simple IQL-AWBC all fail their first short-screen gates. CAU action-conflict has the strongest follow-up, reaching `193/250` over five Can splits, but it still loses individual splits and trails v0.2 selected union `197/250`. The frozen one-feature CAU fallback has one positive split-505 first-20 screen plus a 50-episode confirmation, but the split-303 fresh screen is neutral for the deployable rule. The two-feature CAU gate adds one positive split101 50-episode confirmation and one neutral split202 50-episode confirmation. The post-hoc CAU-plus-v0.2 portfolio reaches `208/250`, but the first fresh split606 validation selects CAU and loses to positive-only (`15/20` versus `16/20`), and the proper 130-demo expanded-mask CAU diagnostic reaches only `12/20`. Split707 CAU-alone is a strong fresh development result (`50/50` versus positive-only `36/50` and weighted `39/50`), but the split606 GMM router threshold does not transfer (`15/20`, no CAU opens), and split808 CAU loses to positive-only (`38/50` versus `43/50`). A support-distance LOO audit has oracle switching headroom (`331/370`) but the safe selector is below positive-only (`263/370` versus `269/370`) and the best-delta selector loses `23` positive-only starts, so simple initial-distance features are not deployable. Do not report a validated hidden-label-free SOTA method or consistent fixed-CAU dominance.

## Claims Forbidden

- Do not claim bad labels are required.
- Do not claim TRIAGE-BC uniformly beats weighted BC.
- Do not claim TRIAGE-BC uniformly beats positive-only retrieval.
- Do not claim hard support always wins.
- Do not claim weighted BC is weak.
- Do not claim support purity alone predicts endpoint policy quality.
- Do not claim best checkpoint proves the method.
- Do not claim the full inverse-Q / Tri-PIQL actor-extraction method is validated on Robomimic.

## Main Evidence Artifacts

- `paper/triage_bc_paper.tex`
- `paper/iclr2026/main.tex`
- `paper/REVIEWER_CLAIM_SUMMARY.md`
- `paper/MANUSCRIPT_CHECKLIST.md`
- `paper/REPRODUCE_PAPER.md`
- `REGIME_PROBE_SUITE.md`
- `METHOD_FREEZE.md`
- `METHOD_FREEZE_V02.md`
- `results/PAPER_CLAIM_PACKAGE.md`
- `results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`
- `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`
- `results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md`
- `results/final_paper_v02/tables/v02_router_regret_REPORT.md`
- `results/final_paper/tables/active_abstention_evaluation_REPORT.md`
- `results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md`
- `results/final_paper/tables/submission_readiness_audit_REPORT.md`
- `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`
- `results/candidate_breakthrough/candidate_breakthrough_decision_REPORT.md`
- `results/sota_candidate/SOTA_CANDIDATE_SWEEP_REPORT.md`
- `results/sota_candidate/CAN505_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md`
- `results/sota_candidate/CAN303_CAU_FALLBACK_FRESH_VALIDATION_REPORT.md`
- `results/sota_candidate/CAU_GATE_FEATURE_AUDIT_REPORT.md`
- `results/sota_candidate/CAU_TWO_FEATURE_GATE_FRESH_VALIDATION_REPORT.md`
- `results/sota_candidate/CAU_ACTION_CONFLICT_CAN_FIVE_SPLIT_ENDPOINT_REPORT.md`
- `results/sota_candidate/CAU_V02_PORTFOLIO_PREFLIGHT_REPORT.md`
- `results/sota_candidate/CAU_V02_FRESH606_ENDPOINT_VALIDATION_REPORT.md`
- `results/sota_candidate/CAU_GMM_ROUTER_FOLLOWUP_REPORT.md`
- `results/sota_candidate/CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md`

## Readiness Status

The package is ready for a careful high-quality empirical submission if the paper remains framed as a precision/coverage study with cautious v0.2 portfolio-router evidence. It is not ready for a top-tier methods/SOTA-style dominance claim unless future evidence establishes stronger fixed-branch wins, a second non-Can endpoint bad-label benefit, or a validated hidden-label-free policy-quality proxy.

Recent Candidate F / output-anchor / two-feature rescue / transition-objective searches are development evidence for that boundary: Candidate F has a scoped Can discovery result but fails the predeclared fresh validation gate, and the later rescue or training-side variants do not clear their first validation checks. The subsequent six-family SOTA-candidate sweep also fails its first short-screen gate: the best Can404 candidates are `16/20` versus positive-only `17/20`, anchored IQL-AWBC reaches only `13/20`, and the near misses lose positive-only anchor starts. A post-hoc CAU fallback feature gate reaches `18/20` on the same Can404 screen; with that threshold frozen, split 505 reaches `16/20` routed versus positive-only `15/20` on the first-20 screen and `41/50` routed versus positive-only `40/50` on the 50-episode confirmation, but split 303 is neutral for the deployable fallback (`15/20` routed versus `15/20` positive-only) even though CAU alone reaches `17/20`. A stronger two-feature gate selected on completed 303/404/505 screens reaches `24/50` routed versus `19/50` positive-only on split101, then is neutral on split202 50-episode confirmation (`40/50` routed versus `40/50` positive-only) despite CAU alone reaching `42/50`. The stronger CAU-alone five-split follow-up reaches `193/250`, beating positive-only, weighted BC, v0.1 TRIAGE-BC, and the best old baseline per split by `1/250`, but it still trails v0.2 selected union by `4/250`. A post-hoc CAU-plus-v0.2 portfolio preflight reaches `208/250` by choosing CAU on `303/404/505` and v0.2 on `101/202`; its first fresh split606 validation is negative (`15/20` gate-selected CAU versus `16/20` positive-only), and a proper expanded-mask CAU check with the full 130-demo transition-weight filter reaches only `12/20`. The GMM-confidence follow-up does not solve routing; split707 CAU-alone confirms a large fresh Can gain (`50/50` versus positive-only `36/50` and weighted `39/50`), but split808 CAU loses to positive-only (`38/50` versus `43/50`). The LOO selector feature audit confirms the remaining issue: oracle switching reaches `331/370`, but safe support-distance selection reaches only `263/370` versus positive-only `269/370`. This is useful heterogeneity evidence, not a current paper claim.

The validation gate is:

```bash
make -C paper validate
```
