# TRIAGE-BC Claim Package

Status: current evidence package as of 2026-06-26.

This package consolidates the results that are defensible for a paper draft and separates them from diagnostics that should stay out of the main claims.

## Short Answer On The Baseline

Weighted BC should not be treated as weak. Once implemented with the official Robomimic BC-RNN-GMM backbone and classifier-probability sampling, it is a strong baseline:

- Can 40 positive / 80 bad split: weighted BC has the best 10k mean success (`0.600`) and is close at 15k (`0.700`), but drops below mass-capped hard support at 20k (`0.567` versus `0.733`).
- Can 20 positive / 80 bad frozen diagnostic: weighted BC is clearly weak on the split-11 50-episode endpoint (`0.360`), while TRIAGE-BC / adaptive masscap reaches `0.660`. However, positive-only NN top20 reaches `0.680` on split 11 and also wins the split-22 endpoint extension (`0.400` versus `0.260`). The three-split support audit keeps the same caveat: TRIAGE recovers more hidden positives (`54/60` versus `49/60`) but admits many more hidden-bad demos (`69/240` versus `11/240`).
- Can 80 positive / 80 bad frozen diagnostic: fresh support audits on split seeds 11/22/33 favor positive-only NN top80 over both TRIAGE-BC / adaptive masscap and classifier-score top80. On the best-case split-33 endpoint, TRIAGE-BC has higher support purity (`0.975` versus `0.900`) but lower coverage and lower success (`0.860` versus `0.980`).
- Lift MG: weighted BC is much stronger than all-demo cloning (`0.533` versus `0.200` at 20k), but hard `pos_min` support is better at the original fixed 20k endpoint (`0.667`). A 50-episode endpoint check keeps `pos_min` ahead of weighted BC (`0.600` versus `0.533`) but shows only a small edge over positive-only NN top160 (`0.600` versus `0.560`). The fresh frozen Lift matrix now argues for a stronger caveat: over three full five-method split rows, all-positive oracle reaches `0.700`, weighted BC reaches `0.620`, positive-only NN top160 reaches `0.547`, TRIAGE-BC / pos-min reaches `0.493`, and all-demo BC reaches `0.207`. Split 33 is especially diagnostic: TRIAGE-BC has perfect selected-support purity but only `0.440` endpoint success, while weighted BC reaches `0.720` and nearly matches the all-positive oracle at `0.760`.
- Can MG sparse: matched controls now favor weighted BC at fixed 20k (`0.333`) over all-positive support (`0.200`), pos-p10 hard support (`0.167`), and all-demo cloning (`0.100`), but the absolute success is still modest enough to keep this as a stress diagnostic. The staged branch-proxy check confirms that simple positive/negative likelihood cannot replace router-v2 abstention.
- Generated Can diagnostics: hard-negative, coverage-shift, and prefix-positive split constructions now isolate settings where explicit bad labels help against matched positive-only retrieval. These are mechanism diagnostics, not primary benchmark rows, and their evidence boundary is frozen in `REGIME_PROBE_SUITE.md`. The concise summary artifact is `results/final_paper/tables/generated_regime_probe_summary_REPORT.md`: hard-negative Can reaches `104/150` versus positive-NN `91/150` (`+13/150`), coverage-shift Can reaches `120/150` versus `103/150` (`+17/150`), and prefix-positive Can reaches `119/150` versus `6/150` (`+113/150`).
- v0.2 development update: a union candidate that keeps positive-only NN support and adds risk-fusion demos improves the pooled Can 40p/80b development endpoint row to `116/150`, versus positive-only NN `108/150`, TRIAGE-BC v0.1 `99/150`, and weighted BC `90/150`. This is not yet a promoted method claim because it loses split 11 to positive-only NN and does not solve Lift MG or Can MG.
- v0.2 portfolio update: a hidden-label-free mass/count router chooses Can 40 union, Lift weighted BC, and Can MG abstention. On the two primary development endpoints it reached `209/300`, versus the strongest pre-union per-task baselines at `201/300` and v0.1 at `173/300`.
- v0.2 fresh-gate update: after freezing the router in `METHOD_FREEZE_V02.md`, fresh Can 40p/80b split seeds `101`/`202`/`303`/`404`/`505` reach `197/250` for the selected hard-union branch versus `192/250` for best per-split non-oracle baselines. Fresh Lift MG split seeds `101`/`202`/`303`/`404`/`505` reach `143/250` for the selected weighted branch versus `146/250` for best per-split non-oracle baselines after completing all five v0.1 TRIAGE audit rows. Combined selected rows are `340/500` versus `338/500` for the best completed non-oracle baseline per split. The paired initial-state bootstrap intervals are descriptive and cross zero for Can (`[-0.144, 0.168]`), Lift (`[-0.083, 0.140]`), and combined (`[-0.074, 0.120]`), so this is a completed but very cautious Can+Lift fresh-gate result.
- v0.2 router-regret update: the current A2 table in `results/final_paper_v02/tables/v02_router_regret_REPORT.md` shows completed Can+Lift regret to the audit-only oracle branch selector of `23/500` for v0.2, compared with `64/500` for always positive-only NN and `62/500` for always weighted BC. The five-split fresh Lift v0.1 hard-support audit is now complete and ties weighted BC in aggregate at `143/250`, while the per-split Lift oracle is `154/250`. Generated Can probes separately show zero regret for bad-aware hard support on hard-negative, coverage-shift, and prefix-positive Can probes.
- Active-abstention update: `results/final_paper/tables/active_abstention_evaluation_REPORT.md` makes the C2 Can MG stress claim explicit. Router-v2 abstains on original and shuffled Can MG, where mass/count are `1947.9`/`1025.7` and `1466.3`/`515.7`. Assigned router-v2 rows average `0.700` fixed-20k success with minimum `0.600`; abstained rows average `0.217` and top out at `0.333`. Original-MG likelihood proxies match best success in `0/6` cases; shuffled MG gets `6/6` only because the staged hard and soft forced branches both reach `0.100`. This supports abstention as risk control, not endpoint dominance.
- Non-Can C1 smoke update: `results/final_paper/ablations/lift_hard_negative_endpoint_smoke/split101/REPORT.md` is the first Lift hard-negative endpoint feasibility check. It uses only split `101`, 50 training epochs, and 10 rollouts. Bad-aware proxy top40 reaches `2/10` versus state-action positive-NN top40 `1/10`, with cleaner support on that split (`21` hidden positives and `19` hidden bad demos versus `7` and `33`). This is directionally consistent but too weak and under-budgeted for a non-Can endpoint claim.
- Non-Can C1 full-budget endpoint update: `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md` aggregates split seeds `101`/`202`/`303` at 200 epochs and 50 rollouts per split. Bad-aware proxy top40 reaches `15/150` versus state-action positive-NN top40 `5/150`, selecting 82 hidden positives and 38 hidden bad demos versus 12 hidden positives and 108 hidden bad demos. This is completed non-Can mechanism evidence, but the absolute success rate is low, so it remains exploratory rather than a primary endpoint claim.

The Can 40p/80b checkpoint-selection diagnostic also rules out a simple "weighted only needed a better checkpoint" explanation: weighted BC oracle-best is `0.700`, while masscap oracle-best is `0.767`. A seed-0 50k-budget check adds that weighted BC does not simply need longer optimization: it peaks at 10k (`0.700`) and is lower at 20k/30k/40k/50k (`0.500`/`0.300`/`0.500`/`0.300`). A three-seed 50-episode endpoint check keeps masscap ahead at fixed 20k on every seed, with mean success `0.680` versus `0.573`, but also shows the endpoint gap is modest and the 10-episode estimates were noisy. The primary frozen final Can 40p/80b splits under `METHOD_FREEZE.md` are directionally consistent against weighted BC and all-demo cloning: TRIAGE-BC reaches pooled `0.660` versus weighted BC `0.600` and all-demo BC `0.540` over 150 endpoint rollouts. However, the matched positive-only NN top40 control is stronger on this same frozen matrix, with pooled success `0.720`. A diagnostic all-positive oracle reaches `0.980`, showing that the evaluation starts are highly solvable with broad true-positive support and that all non-oracle support converters leave substantial headroom. The frozen Can 20p/80b diagnostic sharpens the same message: TRIAGE-BC beats weighted BC by a large margin on split 11 (`0.660` versus `0.360`), but positive-only NN top20 is higher on both completed endpoint splits (`54/100` versus `46/100` pooled), and the three-split support audit shows TRIAGE trades extra hidden-positive recall for much higher bad admission. The fresh frozen Can 80p/80b diagnostic is even more direct: positive-only NN top80 beats TRIAGE-BC on the split-33 endpoint (`0.980` versus `0.860`) despite TRIAGE having higher support purity. The supported claim is therefore not "weighted BC is bad", "hard filtering always wins", or "bad labels are necessary on Can." The supported claim is narrower: score-to-policy conversion matters, hard support can beat soft weighted sampling and pooled mixed-log cloning, and positive-only retrieval remains a very strong no-bad-label baseline that the paper must foreground.

## Proposed Paper Frame

Working title:

> When Do Bad Demonstrations Help Offline Imitation? A Precision-Coverage Study

Current paper-facing thesis:

> When successful demonstrations are scarce and offline logs are heavily contaminated, explicit negative demonstrations can calibrate a desirability score over unlabeled behavior. The score can recover useful hidden-positive support or soft sampling weights, but the key algorithmic issue is the precision/coverage conversion from scores to policy training data. Controlled PointNav and generated Can diagnostics show regimes where bad labels help; frozen Robomimic Can and Lift show that strong positive-only retrieval and weighted BC remain essential baselines.

This is a narrower but much better-supported story than the original full Tri-PIQL claim. The strongest robotics evidence currently supports tri-signal score-calibrated imitation with a competent sequence BC backbone, not a complete inverse-Q method that uniformly beats weighted BC across tasks.

## Main Supported Claims

| Claim | Status | Evidence | Caveat |
|---|---|---|---|
| Contaminated unlabeled logs hurt naive BC. | supported | Continuous PointNav all-data BC degrades from `0.460` to `0.153` success as bad fraction rises from 50% to 95%; Robomimic Lift MG all-demo reaches only `0.200` at 20k and `0.207` pooled over three fresh frozen Lift splits; Can MG all-demo reaches `0.100`; frozen Can 40p/80b all-demo is the weakest pooled endpoint row at `0.540`. | Needs strong BC backbone for robotics interpretation; frozen Can split 22 is an exception where all-demo exceeds TRIAGE-BC. |
| Scarce positive and bad labels can recover useful hidden-positive support. | supported | Continuous PointNav score-gap demo BC gets `1.000` success at 50/75/90/95% bad; the equal label-budget-5 and label-budget-2 PointNav sweeps both preserve `1.000` score-gap success on all four bad fractions; with 5 positives, the bad-label-count sweep shows 1/2/5 bad demos are enough for near-perfect or perfect score-gap demo BC and pure selected support; development Robomimic Can balanced support has `0.962` aggregate purity and `0.900` 20k success. | In robotics this is currently a selector/backbone result, not the full inverse-Q objective; fresh frozen balanced Can support audits show positive-only NN can be stronger than bad-aware scoring. |
| Generated Can diagnostics isolate when bad labels help over positive-only retrieval. | supported as diagnostic evidence | `results/final_paper/tables/generated_regime_probe_summary_REPORT.md` summarizes hard-negative Can hybrid `104/150` versus state-action positive-NN `91/150` (`+13/150`), coverage-shift Can hybrid `120/150` versus positive-NN `103/150` (`+17/150`), and prefix-positive Can bad-aware support `119/150` versus prefix positive-NN `6/150` (`+113/150`). | Generated split constructions only; keep them as mechanism evidence separate from primary frozen Robomimic benchmark rows. |
| The selector must trade off purity and coverage. | supported | Development balanced Can uses coverage-gap; development 20p/80b favored top20 precision; the frozen Can 40p/80b support sweep shows classifier top-k moving from high precision/low recall to high recall/high contamination, with TRIAGE-BC at `110/120` hidden-positive recall but `80/240` hidden-bad admission; fresh frozen Can 20p/80b support audit shows TRIAGE recovers `54/60` hidden positives but admits `69/240` hidden bad demos, while positive-only NN top20 recovers `49/60` and admits `11/240`; fresh frozen Can 80p/80b split 33 shows higher TRIAGE purity but lower endpoint success than positive-only. | A single fixed top-k or single threshold is not enough; fresh Can diagnostics increasingly favor positive-only NN unless the bad-aware converter can improve both coverage and action quality. |
| A theory-lite proposition explains the empirical reversals. | supported as organizing analysis | `Proposition 1 (coverage-contamination criterion)` in the manuscript states that adding unlabeled support should help when marginal coverage gain exceeds normalized marginal contamination cost. The weighted analogue replaces selected count with effective sample size and bad count with weighted bad-action mass. | This is an explanatory proposition for the observed hard/soft/abstention regimes, not a formal guarantee for nonlinear BC-RNN-GMM policy learning. |
| Support purity alone is not a sufficient v0.2 policy-quality proxy. | supported as a no-go result | The action-risk candidate improves the support audit but fails the endpoint gate. On Can 40p/80b split 11, positive-NN/risk fusion selects `39` hidden positives and `1` hidden bad demo yet reaches `0.820`, below positive-only NN at `0.840`. On split 22, it selects `40` hidden positives and `0` hidden bad demos yet reaches `0.640`, below positive-only NN at `0.760`. | Do not promote the current action-risk candidate as TRIAGE-BC v0.2. Any next v0.2 needs a stronger policy-quality proxy, a different candidate generator, or an explicit abstention/router framing. |
| Simple policy-quality proxies do not reliably select endpoint-best branches. | supported as a consolidated no-go table | `results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md` aggregates likelihood, contrastive likelihood, negative rejection, support purity, hidden-positive recall, coverage, and initial/transition coverage checks. Deployable proxy attempts match endpoint winners in only `2/11` rows; audit-only support rows match `3/6`; coverage-only winners match `2/4`; original Can MG likelihood-style proxies match `0/6`. | Treat policy-quality prediction as open. The honest method framing is a frozen portfolio plus abstention/caveats, not a single validated hidden-label-free proxy. |
| Risk information can help when it complements positive-only support on Can 40p/80b. | supported as development evidence only | The union of positive-only NN top40 and positive-NN/risk-fusion top40 selects `119/120` hidden positives and `16/240` hidden bad demos, then reaches `116/150` endpoint successes versus positive-only NN `108/150`, TRIAGE-BC v0.1 `99/150`, and weighted BC `90/150`. The component ablation in `results/final_paper/tables/hard_union_component_ablation_REPORT.md` shows risk-fusion alone has better hidden support labels (`117/120`, `3/240`) but worse same-split endpoint success (`73/100`, `-0.070` versus positive-only), and classifier-only top40 is support-only and dominated by positive-only (`85/120`, `35/240`). | This is Can-only development evidence, not a final v0.2 claim: it loses split 11 to positive-only NN and has not solved Lift MG or Can MG. |
| A cross-task portfolio shape is plausible but fragile on the fresh Can+Lift gate. | supported as very cautious v0.2 evidence | The mass/count portfolio router selects Can 40 union and Lift weighted BC. On fresh split seeds `101`/`202`/`303`/`404`/`505`, Can reaches `197/250` selected versus `192/250` best per-split baselines, Lift reaches `143/250` selected versus `146/250` best per-split baselines after completing all five v0.1 rows, and the combined selected rows reach `340/500` versus `338/500`. Paired-bootstrap intervals cross zero for Can, Lift, and combined in `results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md`. | Can has a modest pooled margin and one severe losing split. Lift is negative against the per-split oracle and v0.2 is only barely positive overall, so this is not a decisive high-impact methods result. |
| The v0.2 portfolio reduces regret versus positive-only and weighted fixed branches. | supported as current A2 evidence | In `results/final_paper_v02/tables/v02_router_regret_REPORT.md`, completed Can+Lift regret to the audit-only oracle branch selector is `23/500` for v0.2, versus `64/500` for always positive-only NN and `62/500` for always weighted BC. It now ties the completed always-hard-support row on Can+Lift because fresh Lift v0.1 also totals `143/250`. Generated Can probes separately show zero regret for bad-aware hard support on hard-negative, coverage-shift, and prefix-positive settings. | This is not yet a complete fixed-branch leaderboard across every regime, and the portfolio claim is now a cautious regret/tie story rather than dominance over every fixed branch. |
| Active abstention is justified on ambiguous Can MG score shapes. | supported as stress/limitation evidence | The active-abstention audit marks original and shuffled Can MG as `stress_abstain`: mass/count are `1947.9`/`1025.7` and `1466.3`/`515.7`, assigned rows average `0.700` with minimum `0.600`, and abstained rows top out at `0.333`. Original-MG proxies match best success in `0/6` cases; shuffled MG gets `6/6` only because both forced branches reach `0.100`. | This does not make Can MG a main success row. It says the current hidden-label-free router should abstain until a coverage-sensitive policy-quality proxy is validated. |
| Hard selected support can beat soft weighted BC at fixed later checkpoints. | supported on paired Can; contradicted on fresh frozen Lift | Can 40p/80b: masscap `0.733` versus weighted `0.567` at 20k, with a three-seed 50-episode endpoint check of `0.680` versus `0.573`; the primary frozen final splits give TRIAGE-BC `0.660` versus weighted BC `0.600` pooled over 150 endpoint rollouts. Fresh Can 20p/80b split 11 gives TRIAGE-BC `33/50` versus weighted BC `18/50`. Lift MG: pos-min `0.667` versus weighted `0.533` at the original 20k endpoint, with a 50-episode endpoint check of `0.600` versus `0.533`; fresh frozen Lift rows now favor weighted BC, `0.620` versus TRIAGE-BC `0.493`. | Weighted BC is competitive and can win decisively; positive-only NN is stronger than TRIAGE-BC on frozen Can 40p/80b (`0.720` versus `0.660`), fresh Can 20p/80b split 11 (`34/50` versus `33/50`), and fresh frozen Lift (`0.547` versus `0.493`). |
| Soft weighted BC can be better when broad coverage matters. | supported diagnostic on Can MG | Can MG sparse has a large high-score plateau; weighted BC beats matched all-positive, all-demo, and pos-p10 controls at fixed 20k (`0.333` versus `0.200`, `0.100`, and `0.167`). The staged branch-proxy check shows simple likelihood proxies choose all-positive support on original Can MG even though weighted is rollout-best. | Stress diagnostic only: absolute success is modest; router-v2 abstention remains the honest final-method posture until a coverage-sensitive policy-quality proxy is validated. |
| Bad labels are strictly necessary. | not supported | Positive-only NN top40 is strong on Can 40p/80b and is the best non-oracle primary frozen Can endpoint row so far (`0.720` versus TRIAGE-BC `0.660`, weighted BC `0.600`, and all-demo BC `0.540`). Fresh Can 20p/80b now favors positive-only NN top20 on both completed endpoint splits (`54/100` versus `46/100` pooled) and admits far fewer hidden-bad demos in the three-split support audit (`11/240` versus `69/240`). Fresh Can 80p/80b split 33 favors positive-only NN top80 by six successes (`49/50` versus `43/50`) even though TRIAGE has higher support purity. Lift positive-only NN top160 is viable and close to bad-aware `pos_min` in the original 50-episode endpoint check (`0.560` versus `0.600`), and it beats TRIAGE-BC on the three fresh frozen Lift rows (`0.547` versus `0.493`). | Better claim: bad labels can improve support purity and sometimes policy performance, but strong no-bad-label retrieval must be treated as a first-class baseline. |
| Current full Tri-PIQL/IQL actor extraction beats all baselines on real continuous-control tasks. | not supported | Minari PointMaze/Kitchen and early Robomimic feed-forward/GMM extractors were negative or unstable. | Keep these as diagnostics, not main claims. |

## Core Tables

Detailed CSVs are in `results/paper_tables/`:

- `continuous_pointnav_table.csv`
- `robotics_core_table.csv`
- `claim_matrix.csv`

The forward-looking method contract is frozen in `METHOD_FREEZE.md`, with machine-readable settings in `configs/final_method.yaml` and `configs/final_eval.yaml`. Existing results outside `results/final_paper/` are development, validation, ablation, or diagnostic evidence unless explicitly rerun under this freeze. The completed frozen Can 40p/80b endpoints are staged in `results/final_paper/tables/can_paired_pos40_bad80_split11_endpoint_REPORT.md`, `results/final_paper/tables/can_paired_pos40_bad80_split22_endpoint_REPORT.md`, `results/final_paper/tables/can_paired_pos40_bad80_split33_endpoint_REPORT.md`, and `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`; the aggregate table now includes positive-only NN top40, all-demo BC, and diagnostic all-positive oracle controls. The frozen Can 20p/80b split-11 endpoint diagnostic is staged in `results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic_REPORT.md`, with the three-split support audit and split-22 endpoint extension staged in `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md`. The fresh balanced Can 80p/80b support and split-33 endpoint diagnostic is staged in `results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`.

The hard-vs-soft score conversion diagnostic is in `results/robomimic_hard_soft_tradeoff_summary/`. The first hidden-label-free router candidate is in `results/robomimic_hidden_free_router_summary/`, with shuffled-split validation anchors in `results/robomimic_hidden_free_router_validation_shuffle42/`, `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_3seed_summary/`, `results/robomimic_lift_mg_shuffle42_posmin_3seed_summary/`, and `results/robomimic_can_mg_shuffle42_router_branch_seed0_summary/`. A follow-up score-shape audit is in `results/robomimic_router_feature_diagnostics/`, the stricter abstention router is summarized in `results/robomimic_router_v2_abstention_summary/`, and the failed Can MG likelihood-proxy attempt is staged in `results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md`. Can 40p/80b masscap-vs-weighted checkpoint-selection, one-seed long-budget, and higher-episode endpoint diagnostics are in `results/robomimic_can40_checkpoint_selection_masscap_weighted/`, `results/robomimic_can40_long_budget_seed0_summary/`, `results/robomimic_can40_endpoint_50ep_summary/`, and `results/robomimic_can40_endpoint_50ep_3seed_summary/`. Support-side Square and Transport quality transfer diagnostics are in `results/robomimic_square_quality_transfer_summary/` and `results/robomimic_transport_quality_transfer_summary/`; the first Square policy smoke is a negative result in `results/robomimic_square_quality_policy_smoke_summary/`.

No-bad-label controls: `results/robomimic_bad_label_ablation/REPORT.md` and `results/robomimic_official_bc_rnn_posonly_nn_top40_pos40_bad80_3seed_summary/REPORT.md` show that positive-only NN is a strong Can 40p/80b control. The staged bad-label control summary in `results/final_paper/tables/bad_label_control_summary_REPORT.md` consolidates the current paper-facing caveat: controlled PointNav supports label-efficient bad-label calibration, while the frozen Can diagnostics and frozen Lift endpoint do not support a broad bad-label-over-positive-only policy claim. The Lift diagnostic in `results/robomimic_lift_mg_posonly_nn_top160_3seed_summary/REPORT.md` shows a different regime: positive-only NN top80 is high-purity but coverage-limited, broader positive-only support quickly admits bad demos, and top160 remains below bad-aware `pos_min` at fixed 15k/20k and oracle-by-seed mean. The higher-episode endpoint check in `results/robomimic_lift_mg_endpoint_50ep_summary/REPORT.md` narrows that gap, and the fresh frozen Lift matrix reverses the policy ordering in favor of weighted BC and positive-only NN. Lift should therefore support a bad-label calibration/stability claim rather than a bad-label policy-benefit claim.

Generated Can diagnostics: `results/final_paper/tables/generated_regime_probe_summary_REPORT.md` is the concise paper-facing summary, while `results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md`, `results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md`, and `results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md` provide the detailed probe reports. They show that bad-aware support can beat matched positive-only retrieval when negative demos are action-conflicting, when scarce positives under-cover initial-pose support, or when trusted positives are only successful-demo prefixes. These diagnostics should be described as generated split constructions rather than as primary benchmark rows.

The regime-probe evidence boundary is frozen in `REGIME_PROBE_SUITE.md`. It
marks completed probes versus negative-control regimes, records expected
winners, endpoint budgets, and allowed claims, and prevents the generated
diagnostics from being presented as default benchmark rows.

v0.2 development diagnostics: `results/final_paper/tables/proxy_endpoint_validation_REPORT.md`, `results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md`, `results/final_paper/tables/v02_action_risk_candidate_support_REPORT.md`, `results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/REPORT.md`, and `results/final_paper/tables/v02_policy_coverage_diagnostic_REPORT.md` document the original no-go. Coverage-only, likelihood-style, rejection, simple action-risk, support-purity, recall, and initial/transition coverage proxies do not reliably predict endpoint winners; the consolidated table has only `2/11` deployable proxy matches and `3/6` audit-only support matches. The best-looking action-risk replacement candidate improves hidden-label support purity but still trails positive-only NN on Can 40p/80b split seeds 11 and 22. The follow-up union artifacts in `results/final_paper/tables/v02_union_candidate_support_REPORT.md` and `results/final_paper/ablations/v02_union_endpoint_200ep_can40/REPORT.md` show a more promising complement strategy on Can 40p/80b, with `116/150` pooled endpoint successes versus positive-only NN `108/150`. The refreshed candidate-family and router reports in `results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md`, `results/final_paper/tables/proxy_endpoint_validation_REPORT.md`, and `results/final_paper/tables/v02_portfolio_router_REPORT.md` show the v0.2 development direction: Can union plus Lift weighted plus Can MG abstention, `209/300` on primary development endpoints. The frozen follow-up is the five-split fresh Can+Lift gate in `results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`, with the current regret framing in `results/final_paper_v02/tables/v02_router_regret_REPORT.md`.

### Continuous PointNav

This is the cleanest controlled mechanism result. Positive labels are only route prefixes, so positive-only BC cannot solve the full route. Unlabeled data contains hidden safe full routes and hidden trap trajectories.

| bad frac | all-data BC | pos+unlabeled BC | weighted BC state-action | score-gap demo BC |
|---:|---:|---:|---:|---:|
| 0.50 | 0.460 | 0.453 | 0.400 | 1.000 |
| 0.75 | 0.367 | 0.300 | 0.000 | 1.000 |
| 0.90 | 0.233 | 0.247 | 0.000 | 1.000 |
| 0.95 | 0.153 | 0.060 | 0.200 | 1.000 |

Source: `results/continuous_pointnav_gap_select_contamination_5seed_merged/REPORT.md`.

Label-budget diagnostic: `results/final_paper/ablations/continuous_pointnav_label_budget5_gap_selection_REPORT.md` repeats the contamination sweep with only 5 positive prefixes and 5 bad shortcut trajectories. Score-gap demo BC still reaches `1.000` success at 50/75/90/95% bad unlabeled data and matches the hidden-good oracle. BC-all reaches only `0.400`/`0.340`/`0.240`/`0.100`, positive+unlabeled BC reaches `0.467`/`0.293`/`0.147`/`0.113`, and local weighted BC reaches `0.200`/`0.200`/`0.000`/`0.140`. The gap selector chooses pure hidden-good support on every row. This strengthens the label-efficiency version of the controlled mechanism claim.

Stress label-budget diagnostic: `results/final_paper/ablations/continuous_pointnav_label_budget2_gap_selection_REPORT.md` repeats the same sweep with only 2 positive prefixes and 2 bad shortcut trajectories. Score-gap demo BC and gap-posterior BC both reach `1.000` success at 50/75/90/95% bad unlabeled data, again matching the hidden-good oracle. BC-all reaches `0.460`/`0.360`/`0.180`/`0.140`, positive+unlabeled BC reaches `0.440`/`0.320`/`0.133`/`0.120`, and local weighted BC reaches `0.147`/`0.000`/`0.173`/`0.000`. The gap selector keeps pure hidden-good support on every row, while fixed top-fraction and fixed-prior posterior converters become brittle at 95% bad contamination. This is the strongest controlled evidence that adaptive score-to-support conversion matters under extreme label scarcity.

Bad-label-count diagnostic: `results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md` fixes the positive budget at 5 prefixes and varies the bad-demo count over 1/2/5. Score-gap demo BC reaches `1.000` success in all rows for 1 and 5 bad demos, and `1.000`/`1.000`/`0.973`/`0.993` for 2 bad demos at 50/75/90/95% bad unlabeled data. Gap selection has `1.000` demo and transition purity in every row and admits zero hidden-bad demos on average. This supports a label-efficiency claim for explicit bad labels, while still showing converter variance: gap-posterior BC is brittle at 95% for 2 and 5 bad demos.

Controlled PointNav mechanism table and figure: `results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md` and `results/final_paper/figures/pointnav_controlled_mechanism.png` consolidate the current Table 1 / mechanism figure candidate. The figure foregrounds the hardest equal-label-budget setting (`n_+=n_-=2`) and the fixed-positive bad-label-count ablation (`n_+=5`, `n_-\in\{1,2,5\}`), which is the cleanest evidence that scarce explicit bad labels can calibrate hidden-good support recovery.

### Robomimic Can Paired

All rows use official Robomimic BC-RNN-GMM with 20k optimizer steps and held-out validation-positive initial states.

| split | method | selected unlabeled | hidden-positive | hidden-bad | purity | 10k | 15k | 20k |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 80p/80b | coverage-aware score-gap | 61.3 | 59.0 | 2.3 | 0.962 | 0.800 | 0.867 | 0.900 |
| 80p/80b | fixed top80 | 80.0 | 72.0 | 8.0 | 0.900 | 0.700 | 0.733 | 0.833 |
| 20p/80b | top20 precision | 20.0 | 15.0 | 5.0 | 0.750 | 0.367 | 0.433 | 0.667 |
| 20p/80b | posx4 coverage-gap | 52.3 | 20.0 | 32.3 | 0.382 | 0.267 | 0.300 | 0.333 |
| 20p/80b | fixed top80 | 80.0 | 20.0 | 60.0 | 0.250 | 0.233 | 0.167 | 0.233 |
| 40p/80b | mass-capped adaptive | 50.0 | 36.3 | 13.7 | 0.728 | 0.500 | 0.733 | 0.733 |
| 40p/80b | weighted BC sampler | 120.0 | 40.0 | 80.0 | 0.333 | 0.600 | 0.700 | 0.567 |
| 40p/80b | top20 precision | 20.0 | 19.7 | 0.3 | 0.983 | 0.567 | 0.667 | 0.700 |
| 40p/80b | positive-only NN top40 | 40.0 | 31.0 | 9.0 | 0.775 | 0.433 | 0.533 | 0.633 |

Sources:

- `results/robomimic_official_bc_rnn_gap_min40_3seed_summary/REPORT.md`
- `results/robomimic_official_bc_rnn_top20_stress_p20_b80_3seed_summary/REPORT.md`
- `results/robomimic_official_bc_rnn_pos40_bad80_3seed_summary/REPORT.md`

Checkpoint-selection diagnostic: `results/robomimic_can40_checkpoint_selection_masscap_weighted/RULE_SUMMARY.md` compares existing Can 40p/80b masscap and weighted checkpoints. Masscap remains ahead at fixed 15k/20k (`0.733`/`0.733`) and oracle-best (`0.767`) versus weighted (`0.700`/`0.567`, oracle-best `0.700`). Train-support and labeled-positive likelihood select the fixed-20k endpoint and preserve the hard-support edge; held-out positive likelihood is noisy and reverses the comparison (`0.467` masscap versus `0.667` weighted), while positive-minus-negative contrastive likelihood selects weak early checkpoints. This supports fixed-budget reporting and argues against claiming best-checkpoint numbers from simple likelihood rules.

Longer-budget diagnostic: `results/robomimic_can40_long_budget_seed0_summary/REPORT.md` trains seed 0 from scratch to 50k using the original 20k train masks. Masscap reaches `0.300`/`0.800`/`0.800`/`0.700`/`0.600` at 10k/20k/30k/40k/50k, while weighted BC reaches `0.700`/`0.500`/`0.300`/`0.500`/`0.300`. This is only one seed, but it directly argues against "weighted BC just needs a longer run" as the default explanation.

Higher-episode endpoint diagnostic: `results/robomimic_can40_endpoint_50ep_3seed_summary/REPORT.md` re-evaluates the original fixed-20k masscap and weighted endpoints for 50 episodes on all three seeds. Masscap remains ahead on every seed (`0.700`/`0.620`/`0.720` versus `0.560`/`0.500`/`0.660`), with mean success `0.680` versus `0.573`. The gap shrinks relative to the 10-episode table (`0.107` versus `0.167`) and approximate pooled binomial intervals overlap, so this strengthens the direction while weakening any claim that the endpoint gap is large or precisely estimated from 10 episodes.

Frozen final splits: `results/final_paper/tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md` summarizes the completed primary Can 40p/80b split seeds under the frozen method contract. Router-v2 chooses hard adaptive masscap for TRIAGE-BC on all three splits. TRIAGE-BC reaches `0.760`/`0.520`/`0.700` on split seeds 11/22/33 versus weighted BC `0.720`/`0.440`/`0.640`, giving pooled endpoint success `0.660` versus `0.600`. Positive-only NN top40 reaches `0.840`/`0.760`/`0.560`, giving pooled endpoint success `0.720` and high-purity support (`106` hidden positives and `14` hidden bads selected across the three splits). All-demo BC reaches `0.500`/`0.560`/`0.560`, giving pooled endpoint success `0.540`; split 22 is an exception where all-demo exceeds TRIAGE-BC. Diagnostic all-positive oracle reaches `0.980` on every split, or `147/150` pooled, using 90 true-positive train demos per split. This means the frozen Can result supports hard support over soft weighting and pooled all-demo cloning, but not a bad-label benefit over strong no-bad-label retrieval. The oracle gap also shows that support conversion remains the bottleneck.

Can 40p/80b score-support tradeoff: `results/final_paper/ablations/can40_score_support_tradeoff_REPORT.md` aggregates the frozen split seeds into a precision/coverage sweep. Classifier-score top-k moves from high precision but low hidden-positive recall (`top10`: purity `0.867`, recall `0.217`) to high recall but high bad admission (`top80`: purity `0.483`, recall `0.967`, hidden-bad admission `0.517`). TRIAGE-BC adaptive masscap recovers `110/120` hidden positives and admits `80/240` hidden bad demos, reaching `99/150` endpoint successes. Positive-only NN top40 recovers `106/120` hidden positives but admits only `14/240` hidden bad demos, reaching `108/150` endpoint successes. Weighted BC has full recall and full bad admission, reaching `90/150`. This is the clearest Can evidence that support conversion is a precision/coverage problem, and it explains why the no-bad baseline beats TRIAGE on this matrix. The corresponding figure is staged as `results/final_paper/figures/can40_precision_coverage.png` and `.pdf`.

Hard-union component ablation: `results/final_paper/tables/hard_union_component_ablation_REPORT.md` isolates the v0.2 Can 40p/80b union. Positive-only NN top40 is the anchor at `108/150`; risk-fusion top40 improves support labels to `117/120` hidden positives and `3/240` hidden bad demos but reaches only `73/100` on its two endpoint splits; the union recovers `119/120` hidden positives with `16/240` hidden bad demos and reaches `116/150`. The answer is combination, not replacement: the union preserves the positive-only branch while adding risk-derived coverage, and the pooled gain comes from splits 22 and 33 while split 11 still favors positive-only NN.

Failure-mode initial-state audit: `results/final_paper/tables/failure_mode_initial_states_REPORT.md` compares positive-only NN, weighted BC, v0.2 hard union, and all-demo BC on three representative paired Can 40p/80b initial states from existing endpoint rollouts. It shows a hard-union rescue on split `33` / `demo_105` (`5/5` union versus `0/5` positive-only and `0/5` all-demo), a positive-anchor regression on split `11` / `demo_39` (`5/5` positive-only versus `0/5` union), and a soft-pool rescue on split `33` / `demo_99` (`5/5` weighted versus `1/5` union). This is appendix intuition only: grasp and loop labels are metric proxies from success and horizon-length failures, not video-level annotations.

Prefix-length robustness: `results/final_paper/tables/can_prefix_length_robustness_REPORT.md` varies the labeled-positive prefix length for the generated Can prefix-positive probe. At fixed top80 support over split seeds `101/202/303`, bad-aware state support clears matched prefix positive-NN support for short, default, and long prefixes: hidden-positive recall deltas are `+0.400`, `+0.658`, and `+0.737`, while hidden-bad admission deltas are `-0.400`, `-0.658`, and `-0.737`. This is support-only construction robustness; it strengthens the generated-probe mechanism story but does not add a new endpoint result.

Non-Can generated support diagnostic: `results/final_paper/ablations/lift_hard_negative_action_conflict_REPORT.md` is the first generated hard-negative/action-conflict support audit outside Can. On Lift MG generated split seeds `101/202/303`, state-action positive-NN top40 selects only `12/120` hidden positives and admits `108/240` hidden bad demos, while bad-aware proxy top40 selects `82/120` hidden positives and admits `38/240` hidden bad demos. The endpoint companion in `results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md` is directionally consistent at `15/150` versus `5/150`, but the absolute success is low enough that this remains exploratory non-Can mechanism evidence rather than a primary benchmark claim.

Cross-regime precision/coverage frontier: `results/final_paper/tables/precision_coverage_frontier_REPORT.md` and `results/final_paper/figures/precision_coverage_frontier.png` place the primary Can 40p/80b and Lift MG rows, Can 20p/80b and Can 80p/80b diagnostics, and generated hard-negative, coverage-shift, and prefix-positive Can probes on one hidden-positive-recall versus hidden-bad-admission plane. The matched comparison table makes the current thesis explicit: generated probes show positive endpoint deltas when bad-aware/hybrid support improves both recall and bad-admission relative to positive-only retrieval, while default Can 40p/80b and Lift MG show failures of a single hard-support rule because positive-only precision or broad weighted coverage can dominate endpoint success.

Frozen Can 20p/80b diagnostic: `results/final_paper/ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic_REPORT.md` tests one fresh split seed under heavier contamination. Positive-only NN top20 reaches `34/50`, TRIAGE-BC / adaptive masscap reaches `33/50`, and weighted BC reaches `18/50`. The three-split support audit and split-22 endpoint extension in `results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md` explain the broader pattern: TRIAGE-BC recovers more hidden positives than positive-only NN top20 (`54/60` versus `49/60`), but admits far more hidden-bad demos (`69/240` versus `11/240`), and positive-only wins the two completed endpoint splits (`54/100` versus `46/100`). Weighted BC samples the full 20/80 contaminated pool on every split; only the split-11 weighted endpoint was trained and it reaches `18/50`. This is useful evidence against soft weighting under heavy contamination, but it is not a positive bad-label policy-benefit result because positive-only retrieval remains a cleaner and stronger completed endpoint baseline.

Frozen Can 80p/80b diagnostic: `results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md` audits fresh balanced split seeds 11/22/33 and trains the best-case split-33 endpoint comparison. Positive-only NN top80 has better hidden-positive coverage on all three support audits and higher purity on splits 11 and 22. On split 33, TRIAGE-BC has higher support purity (`39/40`, `0.975`) but positive-only NN has broader support (`72/80`, `0.900`) and better endpoint success (`49/50` versus `43/50`). This reinforces the positive-only baseline caveat even in the balanced setting.

Primary Robomimic endpoint matrix: `results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md` and `results/final_paper/figures/robotics_primary_endpoint_matrix.png` consolidate the current main Figure 3 candidate. This matrix includes only the completed primary frozen three-split Can 40p/80b and Lift MG rows, avoiding visual promotion of incomplete Can 20p/80b and Can 80p/80b diagnostics. The broader diagnostic matrix remains staged as `results/final_paper/tables/robotics_current_endpoint_matrix_REPORT.md` and `results/final_paper/figures/robotics_current_endpoint_matrix.png`.

Primary endpoint uncertainty: `results/final_paper/tables/primary_endpoint_uncertainty_REPORT.md` adds descriptive uncertainty summaries for the primary Can 40p/80b and Lift MG endpoint matrix. Can 40p/80b favors TRIAGE-BC over weighted BC on every split, but the pooled gap is small (`+0.060`) and rollout-level Wilson intervals overlap (`0.581`--`0.731` for TRIAGE-BC versus `0.520`--`0.675` for weighted BC). Positive-only NN remains higher pooled (`0.720`, interval `0.643`--`0.786`). Lift MG favors weighted BC pooled (`0.620` versus `0.493` for TRIAGE-BC), but the split deltas are not direction-consistent because TRIAGE-BC wins split 11. The paired initial-state bootstrap audit in `results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md` averages repeated rollouts by validation initial state and resamples split seeds and initial states: Can TRIAGE-BC minus weighted BC is `+0.060` with interval `[-0.113, 0.240]`; Lift weighted BC minus TRIAGE-BC is `+0.122` with interval `[-0.100, 0.317]`; only Lift TRIAGE-BC over all-demo BC is strictly positive with interval `[0.211, 0.400]`. These intervals are descriptive rather than formal independent-test claims because endpoint rollouts reuse validation-positive start pools within each split and only three split seeds are available.

Score-shape diagnostics: `results/final_paper/tables/score_shape_diagnostics_REPORT.md` and `results/final_paper/figures/score_shape_diagnostics.png` consolidate the current Figure 4 candidate. Frozen Can 40p/80b has moderate score overlap (`positive_mean=0.713`, `bad_mean=0.368`) that motivates adaptive precision/coverage conversion. Frozen Lift MG has strong score separation (`positive_frac_ge_0p95=0.399`, `bad_frac_ge_0p95=0.002`) but still under-covers at the policy endpoint. Can MG is explicitly marked as a stress diagnostic: `0.518` of hidden positives and `0.094` of hidden bad demos exceed score `0.95`, giving the high-score plateau that motivates router-v2 abstention.

### Robomimic Lift MG

Lift MG is the most informative cross-task robotics transfer result so far because it now shows support-side bad-label benefits, policy-level split sensitivity, and a clear case where broad weighted coverage beats purer hard support.

| method | train demos | selected unlabeled | purity | 10k | 15k | 20k | best-per-seed |
|---|---:|---:|---:|---:|---:|---:|---:|
| pos-min calibrated threshold | 247.3 | 237.3 | 0.864 | 0.267 | 0.533 | 0.667 | 0.700 |
| positive-only NN top160 | 170.0 | 160.0 | 0.787 | 0.300 | 0.333 | 0.567 | 0.567 |
| weighted BC sampler | 1430.0 | 1420.0 | 0.194 | 0.300 | 0.500 | 0.533 | 0.633 |
| all train positives | 286.0 | 276.0 | 1.000 | 0.433 | 0.700 | 0.633 | 0.733 |
| all train demos | 1440.0 | 1420.0 | 0.194 | 0.033 | 0.167 | 0.200 | 0.267 |

Sources: `results/robomimic_lift_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`, `results/robomimic_lift_mg_posonly_nn_top160_3seed_summary/REPORT.md`, `results/robomimic_lift_mg_endpoint_50ep_summary/REPORT.md`, `results/final_paper/tables/lift_mg_mg_sparse_split11_endpoint_summary_REPORT.md`, `results/final_paper/tables/lift_mg_mg_sparse_split22_endpoint_summary_REPORT.md`, `results/final_paper/tables/lift_mg_mg_sparse_split33_endpoint_summary_REPORT.md`, and `results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md`.

No-bad-label Lift diagnostic: `results/robomimic_lift_mg_posonly_nn_top160_3seed_summary/REPORT.md` tests positive-only nearest-neighbor support. Positive-only NN top80 selects 78 hidden-positive and 2 hidden-bad demos but is coverage-limited on seed 0. Top160 selects 126 hidden-positive and 34 hidden-bad demos, reaching three-seed mean success `0.300`/`0.333`/`0.567` at 10k/15k/20k and oracle-by-seed mean `0.567`. Bad-aware `pos_min` selects 203 hidden-positive and 27 hidden-bad demos on seed 0 support diagnostics and reaches `0.267`/`0.533`/`0.667` with oracle-by-seed mean `0.700`. This supports a calibrated bad-label benefit on Lift without claiming bad labels are universally required.

Higher-episode Lift endpoint diagnostic: `results/robomimic_lift_mg_endpoint_50ep_summary/REPORT.md` re-evaluates fixed-20k endpoints for bad-aware `pos_min`, weighted BC, and positive-only NN top160 over 50 episodes per seed. The 50-episode means are `0.600`, `0.533`, and `0.560`, respectively. This keeps the hard-support edge over weighted BC, but the edge over positive-only NN is small and approximate intervals overlap. The paper should therefore emphasize calibrated score-to-support conversion and strong baselines, not a broad claim that bad labels are necessary.

Fresh frozen Lift rows: `results/final_paper/tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md` summarizes the three full five-method frozen rows. Weighted BC reaches `0.480`/`0.660`/`0.720` on split seeds 11/22/33, positive-only NN top160 reaches `0.460`/`0.680`/`0.500`, and TRIAGE-BC / pos-min reaches `0.540`/`0.500`/`0.440`. Pooled over 150 endpoint rollouts, weighted BC reaches `0.620`, positive-only NN reaches `0.547`, and TRIAGE-BC reaches `0.493`. All-positive oracle reaches `0.660`/`0.680`/`0.760`, or `0.700` pooled, while all-demo BC reaches only `0.260`/`0.200`/`0.160`, or `0.207` pooled. Bad labels improve support purity on all three splits, but the fixed-endpoint policy result is dominated by coverage-sensitive baselines.

Classifier top-k ablation: `results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary_REPORT.md` tests a simple broader hard-support rescue, selecting the top160 unlabeled demos by classifier score. Support purity is high on every split (`0.963`/`0.938`/`0.988`), but pooled endpoint success is only `0.453`. It improves split 33 (`0.660` versus TRIAGE-BC `0.440`) but fails on split 11 and split 22 (`0.320`/`0.380`). This rules out fixed classifier top-k as the missing Lift converter and reinforces that policy-quality prediction or a more task-aware precision/coverage rule is needed.

### Robomimic Can MG Sparse

Can MG is a calibration stress diagnostic, not a main positive result yet.

| method | seeds | selected/weighted unlabeled | purity | 10k | 15k | 20k | best |
|---|---:|---:|---:|---:|---:|---:|---:|
| top160 selected support | 1 | 160 | 0.706 | 0.100 | 0.100 | 0.000 | 0.100 |
| weighted BC sampler | 3 | 3840 | 0.179 | 0.133 | 0.200 | 0.333 | 0.367 |
| all train positives | 3 | 688 | 1.000 | 0.033 | 0.133 | 0.200 | 0.233 |
| all train demos | 3 | 3840 | 0.179 | 0.000 | 0.200 | 0.100 | 0.233 |
| pos-p10 calibrated threshold | 3 | 773 | 0.538 | 0.000 | 0.100 | 0.167 | 0.167 |

Source: `results/robomimic_can_mg_official_bc_rnn_controls_3seed_summary/REPORT.md`.

### Hard-Vs-Soft Conversion Diagnostic

The current selector-score evidence supports treating weighted BC as a branch of the method family. A support-only diagnostic now compares score-plateau shape with current policy anchors:

| analysis | observed best mode | support diagnostic | score >= 0.95 demos | best clean hard prefix |
|---|---|---|---:|---:|
| Can paired 80p/80b | hard coverage | hard-support candidate | 0.0 | 80 |
| Can paired 40p/80b | hard mass-capped | hard-support candidate | 0.0 | 50 |
| Can paired 20p/80b | hard precision | hard-support candidate | 0.0 | 20 |
| Lift MG sparse | hard threshold | hard-support candidate | 85.3 | 320 |
| Can MG sparse | soft weighting | soft-weighting candidate | 652.3 | 160 |

Source: `results/robomimic_hard_soft_tradeoff_summary/REPORT.md`.

Interpretation: Can MG has a large high-score plateau, but the clean hard prefix is much smaller than the plateau. The matched controls now support soft sampling as the better Can MG stress-diagnostic branch at fixed 20k, while paired Can and Lift have cleaner hard prefixes matching their hard-support wins.

### Hidden-Free Router Candidate

The first method-level router removes the diagnostic hidden-label purity term. It uses only labeled positive/negative score calibration and the unlabeled score distribution:

| analysis | router branch | training rule | score >= 0.95 demos | labeled-positive p10 | anchored 20k |
|---|---|---|---:|---:|---:|
| Can paired 80p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.748 | 0.900 |
| Can paired 40p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.748 | 0.733 |
| Can paired 20p/80b | hard adaptive masscap | adaptive masscap | 0.0 | 0.749 | 0.667 |
| Lift MG sparse | hard pos-min threshold | pos-min calibrated threshold | 85.3 | 0.887 | 0.667 |
| Can MG sparse | soft weighted | classifier-probability weighted sampler | 652.3 | 0.943 | 0.333 |

Source: `results/robomimic_hidden_free_router_summary/REPORT.md`.

Shuffled validation splits:

| analysis | router branch | selected unlabeled | hidden-positive | purity | 10k | 15k | 20k |
|---|---|---:|---:|---:|---:|---:|---:|
| Can paired 40p/80b shuffle42 | hard adaptive masscap | 63.3 | 39.3 | 0.621 | 0.767 | 0.733 | 0.633 |
| Lift MG shuffle42 | hard pos-min threshold | 199.3 | 185.0 | 0.928 | 0.400 | 0.400 | 0.600 |
| Can MG shuffle42 | hard pos-min threshold | 649.0 | 414.0 | 0.638 | 0.000 | 0.200 | 0.100 |

Sources:

- `results/robomimic_official_bc_rnn_shuffle42_adaptive_masscap_3seed_summary/REPORT.md`
- `results/robomimic_lift_mg_shuffle42_posmin_3seed_summary/REPORT.md`
- `results/robomimic_can_mg_shuffle42_router_branch_seed0_summary/REPORT.md`

Interpretation: this is now a concrete algorithmic candidate rather than only a post-hoc diagnostic, but the shuffled validations expose real limits. The hard branches transfer on Can 40p/80b and Lift MG, but both fixed-20k endpoints are below the corresponding original splits: Can 40p/80b is `0.633` versus `0.733`, and Lift MG is `0.600` versus `0.667`. The Can MG shuffle is a sharper fragility result: the current absolute plateau rule flips from soft weighted to hard `pos_min`, and a seed-0 hard/soft comparison is weak for both (`0.100` fixed 20k each). The router should therefore be presented as an early method candidate with real validation signal and visible split sensitivity, not as the final central paper method.

Feature audit: `results/robomimic_router_feature_diagnostics/REPORT.md` compares hidden-label-free score-shape rules. A mass-only alternative marks both Can MG splits as soft-like, but the Can MG shuffled seed-0 soft policy remains weak; a large-pos-min alternative keeps the same Can MG branch flip as the current rule. The stricter router v2 in `results/robomimic_router_v2_abstention_summary/REPORT.md` therefore abstains on both original and shuffled Can MG, while assigning paired Can and Lift hard-support branches. Across its six assigned Can/Lift rows, fixed-20k success has mean `0.700` and minimum `0.600`; the two abstained Can MG rows have mean `0.217` and maximum `0.333`.

### Router V2 Abstention Candidate

Router v2 is the safest current method-level candidate:

| class | rows | decision | fixed-20k outcome |
|---|---:|---|---:|
| paired Can + Lift, original and shuffled | 6 | assigned hard support | mean `0.700`, min `0.600` |
| Can MG, original and shuffled | 2 | abstain / stress diagnostic | mean `0.217`, max `0.333` |

This reframes the method away from forcing a hard-vs-soft answer on every task. The supported paper-facing method is now a high-confidence hard-support converter with abstention on large ambiguous score shapes. Can MG remains useful because it exposes where a future validation-proxy or quality-estimator branch is needed.

### Can MG Branch-Proxy Attempt

`results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md` tests a natural hidden-label-free replacement for abstention: score trained final-20k branches by BC log-likelihood on labeled and held-out positive/negative masks. This does **not** work well enough:

- On original Can MG, the rollout-best final-20k method is weighted sampling (`0.333`), but all tested likelihood proxies choose all-positive support (`0.200`).
- On shuffled Can MG, the hard and soft seed-0 branches tie at `0.100`, so likelihood can select a branch but cannot detect that both branches are weak.

Interpretation: positive imitation and negative rejection are not enough on Can MG. The missing proxy must capture coverage-sensitive rollout quality; until then, router v2 abstention is the more honest method behavior.

### Square Quality Transfer Diagnostic

`results/robomimic_square_quality_transfer_summary/REPORT.md` adds a support-side transfer check on a new Robomimic task family, NutAssemblySquare. Square MH has relative-quality masks (`better`, `okay`, `worse`) but no reward-failure demonstrations, so this is **not** a main bad-demo benchmark.

Using 10 `better_train` positives, 10 `worse_train` negatives, and an 80/80 hidden `better`/`worse` unlabeled mix:

| quantity | value |
|---|---:|
| labeled-positive mean score | `0.939` |
| labeled-negative mean score | `0.053` |
| `pos_min` selected purity | `0.803` |
| adaptive-masscap selected purity | `0.712` |
| hidden-free router branch | hard adaptive masscap |

Interpretation: scarce relative-quality labels transfer to a new manipulation task and produce a useful desirability score. This strengthens the score-calibration mechanism claim, but it remains support-only until a quality-sensitive Square policy evaluation is added.

A first bounded Square policy smoke was added in `results/robomimic_square_quality_policy_smoke_summary/`. It trained official BC-RNN-GMM policies for better-only support, mixed better+worse support, and adaptive-masscap support on seed 0. All three methods get `0.000` success at epoch 50 and epoch 100 over 10 held-out `better_valid` initial-state rollouts with horizon 500. This is a negative/inconclusive policy result; Square should remain support-side transfer evidence unless a stronger Square policy setup or direct quality-sensitive evaluator is added.

### Transport Quality Transfer Diagnostic

`results/robomimic_transport_quality_transfer_summary/REPORT.md` adds a second support-side relative-quality transfer check on TwoArmTransport. Transport MH has `better`/`okay`/`worse` masks and all `300` trajectories are reward-positive, so this is also **not** a failure-demo benchmark.

Using 10 `better_train` positives, 10 `worse_train` negatives, and the remaining 35/35 hidden `better`/`worse` train demos as unlabeled:

| quantity | value |
|---|---:|
| labeled-positive mean score | `0.988` |
| labeled-negative mean score | `0.014` |
| top-30 selected purity | `1.000` |
| `pos_min` selected purity | `1.000` |
| adaptive-masscap selected purity | `0.972` |

Interpretation: scarce relative-quality labels transfer cleanly to a harder two-arm manipulation task and recover almost all hidden `better` support. This strengthens the cross-task score-calibration mechanism, but it remains support-side evidence only.

## Submission Readiness Snapshot

Current status as of 2026-06-25:

| Criterion | Status | Evidence |
|---|---|---|
| Best or tied-best non-oracle v0.2 on at least two real robotics settings | yellow | Fresh v0.2 Can is best on 4/5 splits (`197/250` versus `192/250` best baselines) but has a severe split-404 reversal. Fresh v0.2 Lift is negative against best completed per-split baselines (`143/250` versus `146/250`) after the completed five-split v0.1 audit, although weighted and v0.1 hard support tie in aggregate at `143/250`. |
| Fresh frozen-split evidence for the promoted method | yellow/green | v0.2 has completed fresh Can 40p/80b and Lift MG split seeds `101`/`202`/`303`/`404`/`505` under `METHOD_FREEZE_V02.md`; generated Can diagnostics have three-split endpoint checks. The evidence is complete for the five-split gate, but still cautious for a strong methods claim. |
| Strong positive-only and weighted baselines | green | Official BC-RNN-GMM positive-only NN and weighted BC baselines are included in the primary Can and Lift matrices. |
| Proxy-vs-endpoint analysis is convincing enough for method selection | yellow | Coverage-only proxy failed earlier and action-risk support gains failed endpoint confirmation. The frozen mass/count router now passes Can+Lift fresh testing, but Lift's `+6/150` aggregate margin and the fresh-gate paired-bootstrap intervals are too weak to call the proxy decisively validated. |
| Mechanism evidence that explicit bad labels can help | green for diagnostics | Controlled PointNav and generated Can hard-negative, coverage-shift, and prefix-positive splits show large bad-aware wins over matched positive-only retrieval. |

This means the current package is ready for a careful diagnostic or benchmark-style paper, and it has a plausible but cautious TRIAGE-BC v0.2 selector result. It is still not a decisive high-impact main-conference methods result unless the paper frames Lift as branch selection rather than a new weighted-BC-beating algorithm.

## Unsupported Or Risky Claims

Do not claim:

- "Weighted BC is bad." It is strong when implemented correctly.
- "Hard support is always better than soft weights." Can MG matched controls contradict this at fixed 20k, though it remains a stress diagnostic rather than a main benchmark claim.
- "Bad labels are required." Positive-only NN is the strongest current frozen Can 40p/80b row, and positive-only NN also beats TRIAGE-BC on the fresh frozen Lift aggregate.
- "The full inverse-Q objective is validated on Robomimic." The strongest robotics rows are classifier-ranked support / weighted sampling plus official BC-RNN-GMM.
- "Best checkpoint proves the method." Fixed-budget reporting is cleaner; Lift and Can 40p/80b likelihood diagnostics show simple hidden-label-free checkpoint rules are too brittle. Ten-episode Robomimic evaluations should also be treated as noisy endpoint estimates.

## Next Experiments

Highest value next steps:

1. Do not spend more endpoint GPU on the unchanged action-risk candidate family. It already failed split-11 and split-22 endpoint gates despite strong support audits.
2. Add the remaining frozen Can 40p/80b controls under the same 50-episode endpoint protocol only if they answer a specific claim gap. Positive-only NN top40, all-demo BC, and all-positive oracle are now complete; positive-only NN is the strongest non-oracle Can row.
3. Replace router-v2 abstention with a validated hidden-label-free policy-quality proxy only if Can MG should become a main positive result rather than a stress diagnostic; simple positive/negative BC likelihood and current coverage/action-risk proxies are now ruled out.
4. Add more Lift evidence only if it answers a new claim gap, such as policy-seed variance, a higher-success non-Can task family, or a validated policy-quality converter. The v0.1 three-split five-method endpoint table, the classifier-top160 ablation, the v0.2 fresh selected-weighted gate, and the generated Lift hard-negative split-101/202/303 endpoint are complete; none supports a simple hard-support bad-label policy-benefit claim.
5. If best-checkpoint reporting is desired, design a stronger predeclared checkpoint-selection rule; current Lift and Can 40p/80b likelihood diagnostics do not solve the issue.
6. If using Square or Transport MH beyond support diagnostics, replace sparse-success evaluation with a quality-sensitive evaluator; sparse success alone is unsuitable because the downloaded MH demos are all successful.
7. If returning to the original Tri-PIQL objective, compare it against the official weighted BC sampler, not the earlier under-configured weighted BC.

## Bottom Line

The baseline now works well enough to shape the paper, but the frozen Can and Lift rows force a narrower story. v0.1 TRIAGE-BC beats weighted BC and pooled all-demo cloning on Can, yet positive-only retrieval is stronger there. The frozen v0.2 router fixes the Can row with a fresh hard-union win and switches Lift to weighted BC, yielding a barely positive selected-vs-baseline Can+Lift gate while tying the completed always-hard-support branch on Can+Lift. The credible method claim should focus on score-to-policy conversion, contaminated-log robustness, and calibrated branch selection, with bad-label policy benefits claimed only in regimes where they beat strong no-bad-label retrieval and weighted sampling.
