# Final Paper Artifact Staging

This directory is reserved for fresh final-split TRIAGE-BC runs under
`METHOD_FREEZE.md`.

The next v0.2 development gate is predeclared in `METHOD_FREEZE_V02.md`,
`configs/final_method_v02.yaml`, and `configs/final_eval_v02.yaml`. Those files
freeze the mass/count portfolio router for fresh-split validation; they are not
yet a final paper-method claim.

The final matrix should not silently mix development results with frozen final
test results. Existing results outside this directory remain development,
validation, ablation, or diagnostic evidence unless copied here by a final
runner with the frozen config.

Expected subdirectories:

- `configs/`: copied method, eval, split, and run configs.
- `tables/`: final CSV/Markdown tables.
- `figures/`: generated paper figures.
- `per_seed/`: per split-seed and policy-seed summaries.
- `per_initial_state/`: paired rollout success by evaluation start.
- `support_audits/`: selected demo IDs, hidden-label audit fields, purity, and recall.
- `score_diagnostics/`: score histograms and router features.
- `ablations/`: non-main variants run after the freeze.

Current staged endpoint tables:

- `tables/can_paired_pos40_bad80_split11_endpoint_REPORT.md`: split seed 11, TRIAGE-BC `0.760` versus weighted BC `0.720`.
- `tables/can_paired_pos40_bad80_split22_endpoint_REPORT.md`: split seed 22, TRIAGE-BC `0.520` versus weighted BC `0.440`.
- `tables/can_paired_pos40_bad80_split33_endpoint_REPORT.md`: split seed 33, TRIAGE-BC `0.700` versus weighted BC `0.640`.
- `tables/can_paired_pos40_bad80_final_endpoint_summary_REPORT.md`: completed primary split-seed aggregate with positive-only NN, all-demo, and all-positive oracle controls; all-positive oracle `0.980`, positive-only NN `0.720`, TRIAGE-BC `0.660`, weighted BC `0.600`, and all-demo BC `0.540` over 150 endpoint rollouts.
- `tables/lift_mg_mg_sparse_split11_endpoint_summary_REPORT.md`: first frozen Lift MG split row; all-positive oracle `0.660`, TRIAGE-BC `0.540`, weighted BC `0.480`, positive-only NN top160 `0.460`, and all-demo BC `0.260` over 50 endpoint rollouts.
- `tables/lift_mg_mg_sparse_split22_endpoint_summary_REPORT.md`: second frozen Lift MG split row; positive-only NN top160 and all-positive oracle `0.680`, weighted BC `0.660`, TRIAGE-BC `0.500`, and all-demo BC `0.200` over 50 endpoint rollouts.
- `tables/lift_mg_mg_sparse_split33_endpoint_summary_REPORT.md`: third frozen Lift MG split row; all-positive oracle `0.760`, weighted BC `0.720`, positive-only NN top160 `0.500`, TRIAGE-BC `0.440`, and all-demo BC `0.160` over 50 endpoint rollouts.
- `tables/lift_mg_mg_sparse_final_endpoint_summary_REPORT.md`: completed three-split frozen Lift aggregate; all-positive oracle `0.700`, weighted BC `0.620`, positive-only NN top160 `0.547`, TRIAGE-BC `0.493`, and all-demo BC `0.207` over 150 endpoint rollouts.
- `tables/lift_mg_mg_sparse_core3_endpoint_summary_REPORT.md`: matched three-split frozen Lift non-oracle core aggregate; weighted BC `0.620`, positive-only NN top160 `0.547`, and TRIAGE-BC `0.493` over 150 endpoint rollouts.
- `tables/robotics_primary_endpoint_matrix_REPORT.md`: main Figure 3 endpoint matrix candidate; includes only the completed primary frozen three-split Can 40p/80b and Lift MG rows.
- `tables/primary_endpoint_uncertainty_REPORT.md`: descriptive uncertainty summary for the primary endpoint matrix, including pooled Wilson intervals, split-level variation, and paired split deltas.
- `tables/primary_endpoint_paired_deltas_REPORT.md`: paired initial-state delta figure report for the primary endpoint matrix; source rows are in `tables/primary_endpoint_paired_initial_deltas.csv`.
- `tables/bad_label_control_summary_REPORT.md`: compact bad-label versus positive-only control summary; source rows are in `tables/bad_label_control_summary.csv`.
- `tables/can_prefix_positive_diagnostic.csv` and `tables/can_prefix_positive_diagnostic_REPORT.md`: paper-facing summary for the generated Can prefix-positive diagnostic; figure outputs are `figures/can_prefix_positive_diagnostic.{png,pdf}`.
- `tables/endpoint_master_table.csv`: standardized endpoint/support aggregate rows regenerated from final-paper per-seed artifacts.
- `tables/support_master_table.csv`: standardized per-split support, hidden-label audit, and endpoint-metric rows regenerated from final-paper per-seed artifacts.
- `tables/baseline_strength_REPORT.md`: master baseline-strength and completeness report for the v0.2 decision gate; confirms that current v0.1 is not best non-oracle on either primary robotics task.
- `tables/candidate_family_audit.csv`, `tables/candidate_family_decision_table.csv`, and `tables/candidate_family_oracle_proxy_REPORT.md`: candidate-family oracle/proxy audit for the v0.2 gate; now includes the Can 40 union branch, which reaches `116/150` and is the first endpoint-evaluated bad-aware branch above the strongest positive-only/weighted baseline, while Lift remains won by weighted BC.
- `tables/hybrid_candidate_support_per_split.csv`, `tables/hybrid_candidate_support_summary.csv`, and `tables/hybrid_candidate_support_REPORT.md`: support-only hybrid positive-NN / classifier candidate audit; finds that tested hybrid hard-support rules do not justify immediate endpoint training.
- `tables/proxy_endpoint_validation.csv`, `tables/proxy_endpoint_validation_correlations.csv`, `tables/proxy_endpoint_validation_winners.csv`, and `tables/proxy_endpoint_validation_REPORT.md`: v0.2 proxy-validation diagnostic; the current hidden-label-free coverage-only proxy matches the endpoint winner in only `2/4` evaluated settings and `1/2` primary settings, so it is not ready to freeze.
- `tables/v02_proxy_feature_screen.csv`, `tables/v02_proxy_feature_screen_winners.csv`, and `tables/v02_proxy_feature_screen_REPORT.md`: support-side v0.2 proxy feature screen; simple coverage/classifier-score proxies match the audit-support winner in only `1/28` setting-proxy cases and do not justify endpoint training.
- `tables/v02_action_risk_feature_screen_per_split.csv`, `tables/v02_action_risk_feature_screen.csv`, `tables/v02_action_risk_feature_screen_winners.csv`, and `tables/v02_action_risk_feature_screen_REPORT.md`: support-side v0.2 action-conflict / bad-neighbor feature screen; explicit action-risk proxies match the audit-support winner in only `1/32` setting-proxy cases and still do not justify endpoint training the current hybrid candidate family.
- `tables/v02_action_risk_candidate_support_per_split.csv`, `tables/v02_action_risk_candidate_support_summary.csv`, `tables/v02_action_risk_candidate_support_decision.csv`, and `tables/v02_action_risk_candidate_support_REPORT.md`: direct action-risk candidate support audit; risk-generated candidates dominate the setting-specific positive-NN support baseline in `4/4` settings, but this remains a support gate rather than an endpoint claim.
- `tables/v02_union_candidate_support_per_split.csv`, `tables/v02_union_candidate_support_summary.csv`, and `tables/v02_union_candidate_support_REPORT.md`: support audit for the Can 40p/80b union candidate that keeps positive-only NN support and adds risk-fusion demos; the union selects `119/120` hidden positives and `16/240` hidden bad demos across split seeds 11/22/33.
- `tables/v02_portfolio_router_decisions.csv`, `tables/v02_portfolio_router_summary.csv`, and `tables/v02_portfolio_router_REPORT.md`: development audit for a hidden-label-free mass/count portfolio router; it chooses Can 40 union, Lift weighted BC, and Can MG abstention, reaching `209/300` on the two primary development endpoints versus strongest pre-union per-task baselines `201/300`.
- `../final_paper_v02/tables/v02_fresh_gate_REPORT.md`: fresh frozen v0.2 Can+Lift endpoint gate under `METHOD_FREEZE_V02.md`; selected branches reach `209/300` versus `187/300` for best completed non-oracle baselines per split. Can is the cleaner hard-union improvement (`129/150` versus `113/150`), while Lift is a modest weighted-branch result (`80/150` versus `74/150`).
- `../final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md`: descriptive paired initial-state uncertainty audit for the fresh v0.2 gate; paired-bootstrap intervals cross zero for Can, Lift, and the combined gate, keeping the claim directional.
- `tables/robotics_current_endpoint_matrix_REPORT.md`: broader diagnostic endpoint matrix; keeps Can 40p/80b and Lift MG as primary frozen three-split rows while marking Can 20p/80b and Can 80p/80b as diagnostic single-split endpoint rows.
- `tables/pointnav_controlled_mechanism_REPORT.md`: controlled PointNav Table 1 / mechanism figure source; with only 2 positive prefixes and 2 bad shortcut demos, TRIAGE gap support reaches `1.000` success at all tested bad fractions, while mixed and weighted baselines degrade.
- `tables/score_shape_diagnostics_REPORT.md`: Figure 4 score-shape source; aggregates frozen Can 40p/80b and Lift MG score diagnostics plus the Can MG stress diagnostic to show overlap, hard-threshold separation, and high-score plateau failure modes.
- `ablations/lift_mg_classifier_top160_endpoint_summary_REPORT.md`: Lift classifier-score top160 ablation; improves split 33 but fails overall, reaching `0.453` pooled over 150 endpoint rollouts.
- `ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic_REPORT.md`: single-split Can 20p/80b diagnostic; positive-only NN top20 reaches `0.680`, TRIAGE-BC / adaptive masscap reaches `0.660`, and weighted BC reaches `0.360` over 50 endpoint rollouts.
- `ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md`: Can 20p/80b support audit over frozen split seeds 11/22/33 plus split-22 endpoint extension; TRIAGE-BC recovers `54/60` hidden positives but admits `69/240` hidden bad demos, while positive-only NN top20 recovers `49/60` hidden positives and admits only `11/240` hidden bad demos; over the two completed endpoint splits, positive-only NN reaches `54/100` versus TRIAGE-BC `46/100`.
- `ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`: balanced Can 80p/80b support audit for split seeds 11/22/33 plus split-33 endpoint check; positive-only NN top80 reaches `0.980` versus TRIAGE-BC / adaptive masscap `0.860` over 50 endpoint rollouts.
- `ablations/hard_negative_can_action_conflict_REPORT.md`: support-only generated Can hard-negative/action-conflict diagnostic; state-action positive-NN top40 reaches `0.583` hidden-positive recall with `0.208` hidden-bad admission, while the bad-aware proxy top40 reaches `1.000` recall with `0.000` bad admission over three generated split seeds.
- `ablations/hard_negative_can_endpoint_smoke/split101/REPORT.md`: 50-epoch / 10-rollout endpoint smoke on generated hard-negative Can split 101; hybrid rank fusion reaches `4/10`, pure bad-aware reaches `1/10`, and state-action positive-NN top40 reaches `0/10`.
- `ablations/hard_negative_can_endpoint_200ep/REPORT.md`: 200-epoch / 50-rollout-per-split generated hard-negative Can endpoint check over split seeds 101/202/303; hybrid rank fusion reaches `104/150` versus state-action positive-NN top40 `91/150`. Treat this as targeted generated-diagnostic evidence, not a primary benchmark row.
- `ablations/can_coverage_shift_REPORT.md`: support-only generated Can scarce-positive coverage-shift diagnostic; state-action positive-NN top40 recovers `105/120` hidden positives with `15/240` hidden-bad admissions, while bad-aware top40 recovers `120/120` with `0/240` bad and the bad-aware-heavy hybrid recovers `118/120` with `2/240` bad.
- `ablations/can_coverage_shift_endpoint_smoke/split101/REPORT.md`: 50-epoch / 10-rollout endpoint smoke on generated coverage-shift Can split 101; hybrid rank fusion reaches `4/10`, pure bad-aware reaches `2/10`, and state-action positive-NN top40 reaches `0/10`.
- `ablations/can_coverage_shift_endpoint_200ep/REPORT.md`: 200-epoch / 50-rollout-per-split generated coverage-shift Can endpoint check over split seeds 101/202/303; bad-aware-heavy hybrid reaches `120/150` versus state-action positive-NN top40 `103/150`. Treat this as targeted generated-diagnostic evidence, not a primary benchmark row.
- `ablations/can_prefix_positive_REPORT.md`: support-only Can prefix-positive diagnostic; positive labels are early successful-demo prefixes, failed demos are explicit negatives, and full successful/failed demos are hidden in the unlabeled pool. Prefix bad-aware state top80 selects `195/240` hidden positives with `45/240` hidden-bad admissions, while prefix state-action positive-NN top80 selects `37/240` hidden positives with `203/240` hidden-bad admissions.
- `ablations/can_prefix_positive_endpoint_200ep/REPORT.md`: 200-epoch / 50-rollout-per-split Can prefix-positive endpoint check over split seeds 101/202/303; prefix bad-aware state top80 reaches `119/150` versus matched prefix state-action positive-NN top80 `6/150`. Treat this as controlled robotics diagnostic evidence, not a primary benchmark row.
- `ablations/v02_action_risk_endpoint_smoke_can40/REPORT.md`: 50-epoch / 10-rollout Can 40p/80b split-11 smoke for direct action-risk candidates; positive-NN top40 reaches `4/10`, positive-NN/risk fusion reaches `2/10`, and bad-neighbor-safe top40 reaches `1/10`.
- `ablations/v02_action_risk_endpoint_200ep_can40/REPORT.md`: 200-epoch / 50-rollout Can 40p/80b endpoint gates for action-risk candidates; positive-NN/risk fusion reaches `0.820` on split 11 and `0.640` on split 22, trailing existing positive-NN top40 at `0.840` and `0.760`.
- `ablations/v02_union_endpoint_200ep_can40/REPORT.md`: 200-epoch / 50-rollout Can 40p/80b endpoint gate for the union candidate over split seeds 11/22/33; union reaches `116/150`, beating positive-only NN `108/150`, TRIAGE-BC v0.1 `99/150`, and weighted BC `90/150`, but remains a Can-only development result because it loses split 11 to positive-only NN and does not address Lift MG or Can MG.
- `tables/v02_policy_coverage_diagnostic_REPORT.md` and `tables/v02_policy_coverage_diagnostic_split22_REPORT.md`: non-GPU policy-coverage diagnostics for the action-risk no-go; simple initial-state and transition nearest-neighbor coverage do not explain or rescue the endpoint misses.
- `ablations/continuous_pointnav_label_budget5_gap_selection_REPORT.md`: controlled PointNav equal-label-budget diagnostic; with 5 positive prefixes and 5 bad trajectories, score-gap demo BC reaches `1.000` success at 50/75/90/95% bad unlabeled data and matches the hidden-good oracle.
- `ablations/continuous_pointnav_label_budget2_gap_selection_REPORT.md`: controlled PointNav equal-label-budget stress diagnostic; with only 2 positive prefixes and 2 bad trajectories, score-gap demo BC and gap-posterior BC still reach `1.000` success at 50/75/90/95% bad unlabeled data, while fixed-fraction and fixed-prior converters become brittle at the 95% boundary.
- `ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md`: controlled PointNav bad-label-count diagnostic; with 5 positive prefixes and 1/2/5 bad trajectories, score-gap demo BC remains near-perfect or perfect at all contamination levels and selects pure hidden-good support in every row.
- `ablations/can40_score_support_tradeoff_REPORT.md`: Can 40p/80b precision/coverage support sweep over frozen split seeds 11/22/33; classifier top-k traces the support frontier, TRIAGE-BC recovers `110/120` hidden positives but admits `80/240` hidden bad demos, and positive-only NN top40 has the best non-oracle endpoint row with far less bad admission.
- `ablations/can_mg_branch_proxy_summary/REPORT.md`: Can MG hidden-label-free branch-proxy diagnostic; simple positive/negative likelihood proxies choose all-positive support on original Can MG even though weighted BC is rollout-best at fixed 20k, and the shuffled hard/soft branches are both weak.

Current staged figures:

- `figures/triage_bc_method_diagram.png` and `figures/triage_bc_method_diagram.pdf`: paper Figure 1 candidate showing the TRIAGE-BC tri-signal scoring, hidden-label-free routing, policy-learning, and audit-only paths.
- `figures/can40_precision_coverage.png` and `figures/can40_precision_coverage.pdf`: paper Figure 2 candidate showing the Can 40p/80b top-k support frontier plus TRIAGE-BC, weighted BC, and positive-only NN endpoint markers.
- `figures/robotics_primary_endpoint_matrix.png` and `figures/robotics_primary_endpoint_matrix.pdf`: paper Figure 3 candidate showing only the primary frozen three-split Robomimic endpoint rows.
- `figures/robotics_current_endpoint_matrix.png` and `figures/robotics_current_endpoint_matrix.pdf`: diagnostic Robomimic endpoint matrix, with diagnostic single-split tasks shaded.
- `figures/pointnav_controlled_mechanism.png` and `figures/pointnav_controlled_mechanism.pdf`: controlled PointNav mechanism figure showing the label-budget-2 stress result and the bad-label-count ablation.
- `figures/score_shape_diagnostics.png` and `figures/score_shape_diagnostics.pdf`: paper Figure 4 candidate showing Can 40p/80b score overlap, Lift MG high-purity thresholding, and Can MG high-score plateau abstention evidence.
- `figures/primary_endpoint_paired_deltas.png` and `figures/primary_endpoint_paired_deltas.pdf`: appendix uncertainty figure showing paired initial-state endpoint deltas with bootstrap intervals.
- `figures/can_prefix_positive_diagnostic.png` and `figures/can_prefix_positive_diagnostic.pdf`: appendix-ready summary of the Can prefix-positive generated diagnostic.
- `figures/proxy_endpoint_validation.png` and `figures/proxy_endpoint_validation.pdf`: v0.2 development diagnostic showing that the current coverage-only proxy does not reliably predict endpoint success across Can and Lift settings; not promoted as a main paper figure.
