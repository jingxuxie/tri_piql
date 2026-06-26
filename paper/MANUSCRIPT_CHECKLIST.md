# TRIAGE-BC Manuscript Checklist

This checklist maps the current standalone and provisional ICLR-format
manuscripts to the frozen evidence package. It is intended to be the handoff
checklist for final paper editing and submission-template refreshes.

## Current Draft State

- Standalone LaTeX draft: `../paper/triage_bc_paper.tex`
- Compiled PDF: `../paper/triage_bc_paper.pdf`
- Provisional ICLR source: `../paper/iclr2026/main.tex`
- Provisional ICLR PDF: `../paper/iclr2026/main.pdf`
- Provisional ICLR style bundle: `../paper/iclr2026/iclr2026_conference.sty`,
  `../paper/iclr2026/iclr2026_conference.bst`
- Markdown scaffold: `../paper/triage_bc_draft.md`
- Reviewer-facing claim summary: `../paper/REVIEWER_CLAIM_SUMMARY.md`
- Final claim contract: `../FINAL_CLAIM_CONTRACT.md`
- Bibliography: `../paper/references.bib`
- Reproduction checklist: `../paper/REPRODUCE_PAPER.md`
- Section and number map: `../PAPER_DRAFT_OUTLINE.md`
- Claim package: `../results/PAPER_CLAIM_PACKAGE.md`
- Frozen method contract: `../METHOD_FREEZE.md`
- Final artifact root: `../results/final_paper/`

Current status: the standalone draft is claim-safe and compileable at 18 pages, and a
provisional ICLR 2026 conversion also compiles. The ICLR source uses the
official ICLR 2026 style files as a provisional submission shell; refresh the
style files if the target venue or target year changes. The current ICLR PDF is
15 pages total, with references beginning on page 10 and the appendix beginning
on page 11. The result order is PointNav-first mechanism evidence, then
Robomimic endpoint evidence.

## Main-Paper Claims

| Claim | Status | Evidence |
|---|---|---|
| Mixed logs can hurt naive cloning. | Supported. | Lift all-demo `31/150`; Can 40 all-demo `81/150`; PointNav mixed-log degradation in `../results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md`. |
| Scarce positives and failures can recover useful hidden support in a controlled mechanism task. | Supported. | PointNav label-budget-2 score-gap support reaches `1.000` success in `../results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md` and `../results/final_paper/figures/pointnav_controlled_mechanism.pdf`. |
| Hard selected support can beat soft weighted sampling under paired Can contamination. | Supported, narrow. | Can 40p/80b: TRIAGE-BC `99/150`, weighted BC `90/150`, all-demo BC `81/150` in `../results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`. |
| Generated Can regime probes isolate when failures help. | Supported as generated diagnostics. | `../results/final_paper/tables/generated_regime_probe_summary_REPORT.md` summarizes hard-negative `104/150` versus `91/150` (`+13/150`), coverage-shift `120/150` versus `103/150` (`+17/150`), and prefix-positive `119/150` versus `6/150` (`+113/150`). These are controlled split constructions, not default benchmark rows. |
| Frozen v0.2 portfolio selection barely improves the fresh Can+Lift gate. | Supported, very cautious. | Fresh Can+Lift selected branches `340/500` versus best per-split non-oracle baselines `338/500` in `../results/final_paper_v02/tables/v02_fresh_gate_REPORT.md`; task-level counts are Can `197/250` versus `192/250` and Lift `143/250` versus `146/250` after completing the five-split v0.1 TRIAGE audit. Paired-bootstrap intervals in `../results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md` cross zero for Can, Lift, and combined, so this stays directional branch-selection evidence. |
| Strong positive-only retrieval must be a first-class baseline. | Supported. | Can 40p/80b positive-only NN `108/150`; Can 20 and Can 80 diagnostics in `../results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md` and `../results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`. |
| Broad weighted coverage can beat purer hard support. | Supported. | Lift MG weighted BC `93/150`, TRIAGE-BC `74/150`, positive-only NN `82/150` in `../results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`. |
| Ambiguous MG score shapes require abstention or better branch validation. | Supported as limitation. | Score-shape figure `../results/final_paper/figures/score_shape_diagnostics.pdf`, branch-proxy failure report `../results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md`, and active-abstention audit `../results/final_paper/tables/active_abstention_evaluation_REPORT.md`: original/shuffled MG mass-count pairs are `1947.9`/`1025.7` and `1466.3`/`515.7`; assigned rows average `0.700`. |

## Claims To Avoid

- Do not claim TRIAGE-BC uniformly beats weighted BC.
- Do not claim TRIAGE-BC uniformly beats positive-only retrieval.
- Do not claim bad labels are necessary on Can.
- Do not claim the full Tri-PIQL / inverse-Q actor-extraction method is
  validated on Robomimic.
- Do not use Can 20p/80b, Can 80p/80b, or Can MG as complete main-result rows.
- Do not promote Square/Transport as failure-demo policy benchmarks in the
  current draft.

## Figure And Table Slots

| Slot | Current artifact | Manuscript role |
|---|---|---|
| Figure 1 | `../results/final_paper/figures/triage_bc_method_diagram.pdf` | TRIAGE-BC pipeline and hidden-label-free flow. |
| Figure 2 | `../results/final_paper/figures/pointnav_controlled_mechanism.pdf` | Controlled mechanism evidence. |
| Figure 3 | `../results/final_paper/figures/robotics_primary_endpoint_matrix.pdf` | Primary Robomimic endpoint matrix. |
| Figure 4 | `../results/final_paper/figures/can40_precision_coverage.pdf` | Can 40 precision/coverage frontier. |
| Figure 5 | `../results/final_paper/figures/score_shape_diagnostics.pdf` | Score-shape and abstention diagnostics. |
| Appendix Figure | `../results/final_paper/figures/robotics_current_endpoint_matrix.pdf` | Broader diagnostic endpoint matrix. |
| Appendix Figure | `../results/final_paper/figures/primary_endpoint_paired_deltas.pdf` | Paired initial-state endpoint uncertainty. |
| Appendix Figure | `../results/final_paper/figures/can_prefix_positive_diagnostic.pdf` | Can prefix-positive generated diagnostic. |
| Appendix Figure | `../results/final_paper/figures/precision_coverage_frontier.pdf` | Cross-regime precision/coverage frontier. |
| Main Table | In-source table in `../paper/triage_bc_paper.tex` | Main Can 40p/80b and Lift MG endpoint counts. |
| Main Table | In-source table `tab:v02-gate` in `../paper/triage_bc_paper.tex` | Fresh v0.2 Can+Lift endpoint gate. |
| Main Table | In-source table `tab:regime-probes` in `../paper/triage_bc_paper.tex` | Generated Can regime-probe summary. |
| Appendix Table | `../results/final_paper/tables/generated_regime_probe_summary_REPORT.md` | Concise generated Can regime-probe summary backing `tab:regime-probes`. |
| Appendix Table | `../results/final_paper_v02/tables/v02_fresh_gate_REPORT.md` | Combined v0.2 fresh Can+Lift endpoint gate. |
| Appendix Table | `../results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md` | Fresh v0.2 paired initial-state uncertainty audit. |
| Appendix Table | `../results/final_paper_v02/tables/v02_fresh_baseline_coverage_REPORT.md` | Fresh v0.2 selected-vs-baseline coverage audit, including optional all-demo/all-positive diagnostic status. |
| Appendix Table | `../results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md` | Fresh v0.2 hidden-label audit and branch decisions. |
| Appendix Table | `../results/final_paper_v02/tables/v02_router_regret_REPORT.md` | Current router-regret table over completed fixed branches, v0.2 router, generated regime probes, and Can MG abstention. |
| Appendix Table | In-source table `tab:bad-label-controls` backed by `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | Bad-label versus positive-only control summary in the compiled appendix. |
| Appendix Table | `../results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md` | Paired initial-state bootstrap uncertainty audit. |
| Appendix Table | `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | Bad-label versus positive-only control summary. |
| Appendix Table | `../results/final_paper/tables/baseline_strength_REPORT.md` | Master endpoint/support completeness and baseline-strength report. |
| Appendix Table | `../results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md` | Candidate-family oracle/proxy audit for the v0.2 decision gate. |
| Appendix Table | `../results/final_paper/tables/hybrid_candidate_support_REPORT.md` | Support-only hybrid positive-NN / classifier candidate audit. |
| Appendix Table | `../results/final_paper/ablations/hard_negative_can_action_conflict_REPORT.md` | Support-only hard-negative Can action-conflict diagnostic. |
| Appendix Table | `../results/final_paper/ablations/lift_hard_negative_action_conflict_REPORT.md` | Support-only non-Can Lift hard-negative action-conflict diagnostic. |
| Appendix Table | `../results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md` | Exploratory full-budget three-split Lift hard-negative endpoint gate. |
| Appendix Table | `../results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md` | Three-split hard-negative Can endpoint check. |
| Appendix Table | `../results/final_paper/ablations/can_coverage_shift_REPORT.md` | Support-only coverage-shift Can diagnostic. |
| Appendix Table | `../results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md` | Three-split coverage-shift Can endpoint check. |
| Appendix Table | `../results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md` | Three-split prefix-positive Can endpoint check. |
| Appendix Table | `../results/final_paper/tables/can_prefix_length_robustness_REPORT.md` | Support-only prefix-length robustness sweep for the generated Can prefix-positive probe. |
| Appendix Table | `../results/final_paper/tables/precision_coverage_frontier_REPORT.md` | Cross-regime support frontier and endpoint-backed comparisons. |
| Appendix Table | `../results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md` | Consolidated no-go table for likelihood, rejection, purity, recall, and coverage policy-quality proxies. |
| Appendix Table | `../results/final_paper/tables/active_abstention_evaluation_REPORT.md` | Active abstention audit for original and shuffled Can MG stress rows. |
| Appendix Table | `../results/final_paper/tables/hard_union_component_ablation_REPORT.md` | Can 40 v0.2 hard-union component ablation over positive-only, risk-fusion, union, classifier-only, weighted, and v0.1 support. |
| Appendix Table | `../results/final_paper/tables/failure_mode_initial_states_REPORT.md` | Paired initial-state failure-mode audit over positive-only, weighted, hard-union, and all-demo Can policies. |
| Appendix Table | `../results/final_paper/tables/submission_readiness_audit_REPORT.md` | Generated acceptance-readiness audit over empirical-submission and methods-dominance criteria. |
| Appendix Table | `../results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/REPORT.md` | Action-risk v0.2 endpoint no-go on Can 40p/80b. |
| Appendix Table | `../results/final_paper/tables/v02_policy_coverage_diagnostic_REPORT.md` | Policy-coverage diagnostic for the action-risk no-go. |
| Appendix Reproducibility Map | In-source appendix in `../paper/triage_bc_paper.tex` and `../paper/iclr2026/main.tex` | Fixed method contract, regeneration docs, diagnostic evidence, and artifact references. |
| Reviewer Summary | `../paper/REVIEWER_CLAIM_SUMMARY.md` | One-page claim, evidence, and limitation summary for paper review. |
| Final Claim Contract | `../FINAL_CLAIM_CONTRACT.md` | Final allowed-claim and forbidden-claim boundary for the current paper package. |

## Appendix-Only Diagnostics

| Diagnostic | Status | Evidence |
|---|---|---|
| PointNav bad-label count | Appendix-only mechanism evidence. | With 5 positive prefixes and `1/2/5` labeled bad shortcuts, selected support has `1.000` demo purity, `1.000` transition purity, and `0 hidden-bad` demos in every row; `1 labeled bad shortcut` and 5 labeled bad shortcuts both reach `1.000` success at all tested contamination levels in `../results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md`. |
| Can 20p/80b | Appendix-only caveat. | Positive-only `54/100`, TRIAGE-BC `46/100`, weighted split-11 `18/50`; support audit finds TRIAGE `54/60` hidden positives and `69/240` hidden bad versus positive-only `49/60` hidden positives and `11/240` hidden bad in `../results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md`. |
| Can 80p/80b | Appendix-only caveat. | Split-33 positive-only `49/50`, TRIAGE-BC `43/50`; report in `../results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`. |
| Can MG | Abstention / branch-proxy limitation. | Original-MG weighted BC is rollout-best at `0.333`, while proxies choose all-positive at `0.200`; the active-abstention audit marks original/shuffled MG as `stress_abstain`, with best-success proxy matches `0/6` and `6/6` in `../results/final_paper/tables/active_abstention_evaluation_REPORT.md`. |
| Hard-negative Can action-conflict | Appendix-only support diagnostic. | Generated splits make state-action positive-NN top40 recover `0.583` hidden-positive recall with `0.208` hidden-bad admission, while the bad-aware proxy top40 recovers `1.000` recall with `0.000` bad admission in `../results/final_paper/ablations/hard_negative_can_action_conflict_REPORT.md`; the endpoint companion is the generated hard-negative diagnostic below. |
| Hard-negative Can three-split endpoint | Targeted generated diagnostic. | At 200 epochs and 50 valid-positive rollouts per split, the bad-aware hybrid reaches `104/150` versus state-action positive-NN top40 `91/150` in `../results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md`; keep this separate from the primary Robomimic benchmark rows because the split construction is generated. |
| Lift hard-negative three-split endpoint | Exploratory C1 evidence only. | Bad-aware proxy top40 reaches `15/150` versus state-action positive-NN top40 `5/150` at 200 epochs and 50 valid-positive rollouts per split in `../results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md`; selected support has 82 hidden positives and 38 hidden bad demos versus 12 hidden positives and 108 hidden bad demos. Absolute success is low, so this is non-Can mechanism evidence rather than a primary endpoint claim. |
| Coverage-shift Can support | Appendix-only support diagnostic. | Generated scarce-positive coverage-shift splits make state-action positive-NN top40 recover `105/120` hidden positives with `15/240` hidden-bad admissions, while the bad-aware-heavy hybrid recovers `118/120` hidden positives with `2/240` hidden-bad admissions in `../results/final_paper/ablations/can_coverage_shift_REPORT.md`. |
| Coverage-shift Can three-split endpoint | Targeted generated diagnostic. | At 200 epochs and 50 valid-positive rollouts per split, the bad-aware-heavy hybrid reaches `120/150` versus state-action positive-NN top40 `103/150` in `../results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md`; keep this separate from the primary Robomimic benchmark rows because the split construction is generated. |
| Prefix-positive Can three-split endpoint | Targeted generated diagnostic. | At 200 epochs and 50 valid-positive rollouts per split, prefix bad-aware state top80 reaches `119/150` and selects `195` hidden positives with `45` hidden bad demos, while prefix state-action positive-NN top80 reaches `6/150` and selects `37` hidden positives with `203` hidden bad demos in `../results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md`; keep this separate from the primary Robomimic benchmark rows because the split construction is generated. |
| TRI-Signal regime-probe registry | Paper-facing evidence boundary. | `../REGIME_PROBE_SUITE.md` freezes the completed generated diagnostics and negative-control regimes, labels exploratory versus completed evidence, and states the allowed claim for each probe. |
| Action-risk v0.2 endpoint no-go | Appendix-only method-development diagnostic. | Positive-NN/risk fusion improves support labels on Can 40p/80b but trails positive-only NN at the endpoint: split 11 is `0.820` versus `0.840`, and split 22 is `0.640` versus `0.760`, in `../results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/REPORT.md`; this rejects the current action-risk support-purity story as a deployable v0.2 method. |
| Fresh v0.2 Can+Lift gate | Very cautious main-result update. | Frozen v0.2 selected branches reach `340/500` versus `338/500` for best per-split non-oracle baselines; paired-bootstrap intervals are Can `[-0.144, 0.168]`, Lift `[-0.083, 0.140]`, and combined `[-0.074, 0.120]`, so the gate is barely positive and not a significance claim. |
| v0.2 router regret | Cautious portfolio framing. | Current completed Can+Lift regret to the audit-only oracle branch selector is `23/500` for v0.2, versus `64/500` for always positive-only NN and `62/500` for always weighted BC in `../results/final_paper_v02/tables/v02_router_regret_REPORT.md`; the table now marks both fresh Can and fresh Lift v0.1 as complete, while generated-probe and Can MG cells are either not-applicable, rate-only, or abstention rows by design. |
| Lift classifier top160 | Coverage limitation. | Fixed classifier top160 reaches `68/150`, below weighted BC `93/150`, in `../results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary_REPORT.md`. |
| Square / Transport | Repository-only for now. | Keep in `../results/PAPER_CLAIM_PACKAGE.md` unless a later draft needs support-side relative-quality diagnostics. |

## Required Validation Before Any Submission Draft

Run from the repository root:

```bash
make -C paper validate
python -m py_compile scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/plot_primary_endpoint_paired_deltas.py scripts/summarize_bad_label_control_table.py scripts/summarize_master_evidence_tables.py scripts/summarize_can40_score_support_tradeoff.py scripts/summarize_v02_union_candidate_audit.py scripts/summarize_v02_union_endpoint_aggregate.py scripts/summarize_hard_union_component_ablation.py scripts/summarize_failure_mode_initial_states.py scripts/summarize_candidate_family_audit.py scripts/summarize_hybrid_candidate_support_audit.py scripts/summarize_hard_negative_can_action_conflict_audit.py scripts/summarize_lift_hard_negative_action_conflict_audit.py scripts/summarize_can_coverage_shift_audit.py scripts/summarize_hard_negative_can_endpoint_smoke.py scripts/summarize_can_prefix_positive_endpoint.py scripts/plot_can_prefix_positive_diagnostic.py scripts/summarize_can_prefix_length_robustness.py scripts/summarize_precision_coverage_frontier.py scripts/summarize_policy_quality_proxy_no_go.py scripts/summarize_active_abstention_evaluation.py scripts/summarize_v02_fresh_gate_uncertainty.py scripts/summarize_submission_readiness_audit.py scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/validate_method_freeze_v02.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/summarize_bad_label_control_table.py
python scripts/summarize_master_evidence_tables.py
python scripts/summarize_candidate_family_audit.py
python scripts/summarize_hybrid_candidate_support_audit.py
python scripts/summarize_hard_negative_can_action_conflict_audit.py
python scripts/summarize_lift_hard_negative_action_conflict_audit.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Lift Hard-Negative'
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Lift Hard-Negative'
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Lift Hard-Negative'
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/lift_hard_negative_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Lift Hard-Negative' --aggregate-splits
python scripts/summarize_can40_score_support_tradeoff.py
python scripts/summarize_v02_union_candidate_audit.py
python scripts/summarize_v02_union_endpoint_aggregate.py
python scripts/summarize_hard_union_component_ablation.py
python scripts/summarize_failure_mode_initial_states.py
python scripts/summarize_can_prefix_length_robustness.py
python scripts/summarize_precision_coverage_frontier.py
python scripts/summarize_policy_quality_proxy_no_go.py
python scripts/summarize_active_abstention_evaluation.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_method_freeze_v02.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
pdfinfo paper/triage_bc_paper.pdf
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/iclr2026/main.pdf
pdftotext -layout paper/iclr2026/main.pdf /tmp/triage_iclr_main.txt
git diff --check
```

Expected current checks:

- Makefile validation passes via `make -C paper validate`; `make -C paper all`
  aliases the same gate.
- Artifact validator checks 134 unique references, including the ICLR
  source graphics and bibliography.
- Claim-number validator passes against staged CSVs, the standalone manuscript,
  the ICLR manuscript, and the Markdown draft, and it enforces the core
  overclaim-avoidance caveats.
- Structure validator passes for manuscript figure-label order, figure-map
  rows, required table labels, PDF page counts, and ICLR page-boundary markers.
- Method-freeze validator passes for `METHOD_FREEZE_V02.md`, the v0.2 router
  source, and staged router-support and endpoint-role artifacts.
- Paired bootstrap audit regenerates from staged per-episode metrics.
- Paired initial-state delta figure regenerates from staged per-episode metrics.
- Bad-label control summary regenerates from staged final-paper tables and
  support audits.
- Master endpoint/support evidence tables regenerate from final-paper per-seed
  manifests, support audits, hidden-label audits, and endpoint metrics.
- Candidate-family audit regenerates from the master endpoint table, support
  tradeoff audits, and Can MG proxy summary.
- Hybrid candidate support audit regenerates from staged split files,
  classifier score diagnostics, and full positive-NN support rankings.
- Hard-negative Can action-conflict support diagnostic regenerates generated
  split files plus support-gate CSVs and report.
- Hard-negative Can endpoint summaries regenerate from completed split-101
  smoke plus three 200-epoch endpoint checks and the aggregate report.
- Cross-regime precision/coverage frontier regenerates from staged primary,
  diagnostic, and generated-regime support audits and endpoint summaries.
- Standalone PDF compiles from `../paper/triage_bc_paper.tex` and is 18 pages.
- Standalone LaTeX log scan has no warning, underfull, or overfull matches.
- ICLR PDF compiles from `../paper/iclr2026/main.tex` and is 15 pages; the
  current page audit has references on page 10 and appendix material starting
  on page 11.
- ICLR LaTeX log scan has no undefined-reference, LaTeX/package warning,
  natbib warning, or overfull matches under the Makefile pattern; underfull
  layout messages in the submission shell are tolerated.
- The paper remains explicit that the result is score-to-support conversion for
  behavior cloning, not validated inverse-Q robotics.

## Open Decisions

1. Confirm the final venue/year and refresh the style files if the target is
   not ICLR 2026.
2. Add venue-specific tests only if the chosen venue expects them; the current
   paper uses Wilson intervals, paired initial-state bootstraps, and split-level
   context.
