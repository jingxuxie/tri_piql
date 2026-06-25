# Final Paper Artifact Staging

This directory is reserved for fresh final-split TRIAGE-BC runs under
`METHOD_FREEZE.md`.

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
- `tables/robotics_current_endpoint_matrix_REPORT.md`: broader diagnostic endpoint matrix; keeps Can 40p/80b and Lift MG as primary frozen three-split rows while marking Can 20p/80b and Can 80p/80b as diagnostic single-split endpoint rows.
- `tables/pointnav_controlled_mechanism_REPORT.md`: controlled PointNav Table 1 / mechanism figure source; with only 2 positive prefixes and 2 bad shortcut demos, TRIAGE gap support reaches `1.000` success at all tested bad fractions, while mixed and weighted baselines degrade.
- `tables/score_shape_diagnostics_REPORT.md`: Figure 4 score-shape source; aggregates frozen Can 40p/80b and Lift MG score diagnostics plus the Can MG stress diagnostic to show overlap, hard-threshold separation, and high-score plateau failure modes.
- `ablations/lift_mg_classifier_top160_endpoint_summary_REPORT.md`: Lift classifier-score top160 ablation; improves split 33 but fails overall, reaching `0.453` pooled over 150 endpoint rollouts.
- `ablations/can_paired_pos20_bad80_split11_endpoint_diagnostic_REPORT.md`: single-split Can 20p/80b diagnostic; positive-only NN top20 reaches `0.680`, TRIAGE-BC / adaptive masscap reaches `0.660`, and weighted BC reaches `0.360` over 50 endpoint rollouts.
- `ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md`: Can 20p/80b support audit over frozen split seeds 11/22/33 plus split-22 endpoint extension; TRIAGE-BC recovers `54/60` hidden positives but admits `69/240` hidden bad demos, while positive-only NN top20 recovers `49/60` hidden positives and admits only `11/240` hidden bad demos; over the two completed endpoint splits, positive-only NN reaches `54/100` versus TRIAGE-BC `46/100`.
- `ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`: balanced Can 80p/80b support audit for split seeds 11/22/33 plus split-33 endpoint check; positive-only NN top80 reaches `0.980` versus TRIAGE-BC / adaptive masscap `0.860` over 50 endpoint rollouts.
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
