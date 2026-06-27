# Reproducing The Current Paper Artifacts

This file gives the shortest reliable path from the frozen evidence package to
the current manuscript PDF. It separates cheap artifact regeneration from
expensive Robomimic training and evaluation.

## Environment

Use the project conda environment:

```bash
conda activate tri-piql
```

GPU Robomimic commands should set:

```bash
export XLA_PYTHON_CLIENT_PREALLOCATE=false
export MUJOCO_GL=egl
```

Plotting commands are written to use a temporary Matplotlib config directory via
their scripts.

## Frozen Method Contract

The paper-facing contract is:

- `../METHOD_FREEZE.md`
- `../configs/final_method.yaml`
- `../configs/final_eval.yaml`
- `../METHOD_FREEZE_V02.md`
- `../configs/final_method_v02.yaml`
- `../configs/final_eval_v02.yaml`

Final paper artifacts are staged under:

- `../results/final_paper/`
- `../results/final_paper_v02/`

Results outside `../results/final_paper/` are development, validation,
ablation, or diagnostic evidence unless explicitly copied into the staged final
package.

## Cheap Regeneration

These commands regenerate the current paper-facing tables and figures from
existing staged results. They should finish quickly and do not retrain policies.

```bash
python scripts/plot_triage_bc_method_diagram.py
python scripts/summarize_pointnav_controlled_mechanism.py
python scripts/summarize_can40_score_support_tradeoff.py
python scripts/summarize_v02_union_candidate_audit.py
python scripts/summarize_v02_union_endpoint_aggregate.py
python scripts/summarize_hard_union_component_ablation.py
python scripts/summarize_failure_mode_initial_states.py
python scripts/plot_can40_precision_coverage.py
python scripts/summarize_final_endpoint_matrix.py
python scripts/summarize_primary_endpoint_uncertainty.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/summarize_bad_label_control_table.py
python scripts/summarize_master_evidence_tables.py
python scripts/summarize_can40_score_support_tradeoff.py
python scripts/summarize_v02_union_candidate_audit.py
python scripts/summarize_v02_union_endpoint_aggregate.py
python scripts/summarize_hard_union_component_ablation.py
python scripts/summarize_failure_mode_initial_states.py
python scripts/summarize_candidate_family_audit.py
python scripts/summarize_hybrid_candidate_support_audit.py
python scripts/summarize_hard_negative_can_action_conflict_audit.py
python scripts/summarize_lift_hard_negative_action_conflict_audit.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits
python scripts/summarize_can_coverage_shift_audit.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows unless the manuscript explicitly frames it as generated diagnostic evidence.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md
python scripts/summarize_can_prefix_positive_endpoint.py
python scripts/plot_can_prefix_positive_diagnostic.py
python scripts/summarize_can_prefix_length_robustness.py
python scripts/summarize_generated_regime_probe_table.py
python scripts/summarize_precision_coverage_frontier.py
python scripts/summarize_policy_quality_proxy_no_go.py
python scripts/summarize_active_abstention_evaluation.py
python scripts/summarize_v02_fresh_can_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
python scripts/summarize_v02_fresh_lift_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
python scripts/summarize_v02_fresh_router_support_audit.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables --split-seeds 101 202 303 404 505 --tasks can40 lift_mg
python scripts/summarize_v02_fresh_gate.py --root results/final_paper_v02
python scripts/summarize_v02_fresh_gate_uncertainty.py --root results/final_paper_v02
python scripts/summarize_v02_fresh_baseline_coverage.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
python scripts/summarize_v02_router_regret_table.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables
python scripts/summarize_sota_cau_v02_portfolio_preflight.py
python scripts/summarize_sota_cau_v02_fresh606_endpoint_validation.py
python scripts/summarize_sota_can606_gmm_confidence_cau_router.py
python scripts/summarize_sota_cau_gmm_router_followup.py
python scripts/summarize_sota_cau_selector_feature_audit.py
python scripts/summarize_sota_candidate_sweep.py
python scripts/summarize_submission_readiness_audit.py
python scripts/plot_score_shape_diagnostics.py
python scripts/summarize_can20_support_audit.py
```

Then validate local artifact references and compile the standalone draft plus
the provisional ICLR-format draft:

```bash
make -C paper validate
```

The `paper/Makefile` gate rebuilds both PDFs, regenerates the paired-bootstrap
audit, master evidence tables, candidate-family audit, hybrid support audit,
the hard-negative, coverage-shift, and prefix-positive diagnostics, the
v0.2 fresh Can+Lift gate, the v0.2 fresh-gate uncertainty audit, and the
submission-readiness audit, runs the Python validators, and fails if the
configured LaTeX log scans find matches.
The expanded manual command sequence is:

```bash
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
python scripts/summarize_can_coverage_shift_audit.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows unless the manuscript explicitly frames it as generated diagnostic evidence.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md
python scripts/summarize_can_prefix_positive_endpoint.py
python scripts/plot_can_prefix_positive_diagnostic.py
python scripts/summarize_can_prefix_length_robustness.py
python scripts/summarize_precision_coverage_frontier.py
python scripts/summarize_policy_quality_proxy_no_go.py
python scripts/summarize_active_abstention_evaluation.py
python scripts/summarize_v02_fresh_can_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
python scripts/summarize_v02_fresh_lift_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
python scripts/summarize_v02_fresh_router_support_audit.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables --split-seeds 101 202 303 404 505 --tasks can40 lift_mg
python scripts/summarize_v02_fresh_gate.py --root results/final_paper_v02
python scripts/summarize_v02_fresh_gate_uncertainty.py --root results/final_paper_v02
python scripts/summarize_v02_fresh_baseline_coverage.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
python scripts/summarize_v02_router_regret_table.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables
python scripts/summarize_sota_cau_v02_portfolio_preflight.py
python scripts/summarize_sota_cau_v02_fresh606_endpoint_validation.py
python scripts/summarize_sota_can606_gmm_confidence_cau_router.py
python scripts/summarize_sota_cau_gmm_router_followup.py
python scripts/summarize_sota_cau_selector_feature_audit.py
python scripts/summarize_sota_candidate_sweep.py
python scripts/summarize_submission_readiness_audit.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_method_freeze_v02.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
```

The compiled PDFs are:

- `../paper/triage_bc_paper.pdf`
- `../paper/iclr2026/main.pdf`

The ICLR-format source uses the official ICLR 2026 style files as a provisional
submission shell. Refresh `../paper/iclr2026/iclr2026_conference.sty` and
`../paper/iclr2026/iclr2026_conference.bst` if the target venue or year changes.

## Main Artifact Map

| Paper item | Generated artifact | Regenerator |
|---|---|---|
| Figure 1, method diagram | `../results/final_paper/figures/triage_bc_method_diagram.pdf` | `../scripts/plot_triage_bc_method_diagram.py` |
| Figure 2, PointNav mechanism | `../results/final_paper/figures/pointnav_controlled_mechanism.pdf` | `../scripts/summarize_pointnav_controlled_mechanism.py` |
| Figure 3, primary robotics matrix | `../results/final_paper/figures/robotics_primary_endpoint_matrix.pdf` | `../scripts/summarize_final_endpoint_matrix.py` |
| Figure 4, Can precision/coverage | `../results/final_paper/figures/can40_precision_coverage.pdf` | `../scripts/summarize_can40_score_support_tradeoff.py`, then `../scripts/plot_can40_precision_coverage.py` |
| Figure 5, score-shape diagnostics | `../results/final_paper/figures/score_shape_diagnostics.pdf` | `../scripts/plot_score_shape_diagnostics.py` |
| Primary endpoint uncertainty | `../results/final_paper/tables/primary_endpoint_uncertainty_REPORT.md` | `../scripts/summarize_primary_endpoint_uncertainty.py` |
| Primary paired bootstrap audit | `../results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md` | `../scripts/summarize_primary_endpoint_paired_bootstrap.py` |
| Primary paired delta figure | `../results/final_paper/figures/primary_endpoint_paired_deltas.pdf` | `../scripts/plot_primary_endpoint_paired_deltas.py` |
| Bad-label control summary | `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | `../scripts/summarize_bad_label_control_table.py` |
| Fresh v0.2 Can+Lift gate | `../results/final_paper_v02/tables/v02_fresh_gate_REPORT.md` | `../scripts/summarize_v02_fresh_gate.py` |
| Fresh v0.2 uncertainty audit | `../results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md` | `../scripts/summarize_v02_fresh_gate_uncertainty.py` |
| Fresh v0.2 baseline coverage audit | `../results/final_paper_v02/tables/v02_fresh_baseline_coverage_REPORT.md` | `../scripts/summarize_v02_fresh_baseline_coverage.py` |
| Fresh v0.2 router support audit | `../results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md` | `../scripts/summarize_v02_fresh_router_support_audit.py` |
| v0.2 router-regret table | `../results/final_paper_v02/tables/v02_router_regret_REPORT.md` | `../scripts/summarize_v02_router_regret_table.py` |
| SOTA-candidate sweep no-go | `../results/sota_candidate/SOTA_CANDIDATE_SWEEP_REPORT.md` | `../scripts/summarize_sota_candidate_sweep.py` |
| CAU-plus-v0.2 portfolio preflight | `../results/sota_candidate/CAU_V02_PORTFOLIO_PREFLIGHT_REPORT.md` | `../scripts/summarize_sota_cau_v02_portfolio_preflight.py` |
| CAU-plus-v0.2 fresh606 validation | `../results/sota_candidate/CAU_V02_FRESH606_ENDPOINT_VALIDATION_REPORT.md` | `../scripts/summarize_sota_cau_v02_fresh606_endpoint_validation.py` |
| CAU/GMM router follow-up | `../results/sota_candidate/CAU_GMM_ROUTER_FOLLOWUP_REPORT.md` | `../scripts/summarize_sota_cau_gmm_router_followup.py` |
| CAU selector feature LOO audit | `../results/sota_candidate/CAU_SELECTOR_FEATURE_LOO_AUDIT_REPORT.md` | `../scripts/summarize_sota_cau_selector_feature_audit.py` |
| Master evidence tables | `../results/final_paper/tables/baseline_strength_REPORT.md` | `../scripts/summarize_master_evidence_tables.py` |
| Candidate-family audit | `../results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md` | `../scripts/summarize_candidate_family_audit.py` |
| Hybrid support audit | `../results/final_paper/tables/hybrid_candidate_support_REPORT.md` | `../scripts/summarize_hybrid_candidate_support_audit.py` |
| Hard-negative Can diagnostic | `../results/final_paper/ablations/hard_negative_can_action_conflict_REPORT.md` | `../scripts/summarize_hard_negative_can_action_conflict_audit.py` |
| Hard-negative Lift support diagnostic | `../results/final_paper/ablations/lift_hard_negative_action_conflict_REPORT.md` | `../scripts/summarize_lift_hard_negative_action_conflict_audit.py` |
| Hard-negative Lift three-split endpoint gate | `../results/final_paper/ablations/lift_hard_negative_endpoint_200ep/REPORT.md` | manual GPU runs documented in the aggregate report |
| Hard-negative Can endpoint check | `../results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md` | `../scripts/summarize_hard_negative_can_endpoint_smoke.py` |
| Coverage-shift Can diagnostic | `../results/final_paper/ablations/can_coverage_shift_REPORT.md` | `../scripts/summarize_can_coverage_shift_audit.py` |
| Coverage-shift Can endpoint check | `../results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md` | `../scripts/summarize_hard_negative_can_endpoint_smoke.py` |
| Prefix-positive Can diagnostic figure | `../results/final_paper/figures/can_prefix_positive_diagnostic.pdf` | `../scripts/summarize_can_prefix_positive_endpoint.py`, then `../scripts/plot_can_prefix_positive_diagnostic.py` |
| Prefix-positive Can diagnostic report | `../results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md` | `../scripts/plot_can_prefix_positive_diagnostic.py` |
| Prefix-length robustness support sweep | `../results/final_paper/tables/can_prefix_length_robustness_REPORT.md` | `../scripts/summarize_can_prefix_length_robustness.py` |
| Generated regime-probe summary | `../results/final_paper/tables/generated_regime_probe_summary_REPORT.md` | `../scripts/summarize_generated_regime_probe_table.py` |
| Cross-regime precision/coverage frontier | `../results/final_paper/figures/precision_coverage_frontier.pdf` and `../results/final_paper/tables/precision_coverage_frontier_REPORT.md` | `../scripts/summarize_precision_coverage_frontier.py` |
| Policy-quality proxy no-go table | `../results/final_paper/tables/policy_quality_proxy_no_go_REPORT.md` | `../scripts/summarize_policy_quality_proxy_no_go.py` |
| Active abstention evaluation | `../results/final_paper/tables/active_abstention_evaluation_REPORT.md` | `../scripts/summarize_active_abstention_evaluation.py` |
| Hard-union component ablation | `../results/final_paper/tables/hard_union_component_ablation_REPORT.md` | `../scripts/summarize_hard_union_component_ablation.py` |
| Failure-mode initial-state audit | `../results/final_paper/tables/failure_mode_initial_states_REPORT.md` | `../scripts/summarize_failure_mode_initial_states.py` |
| Submission-readiness audit | `../results/final_paper/tables/submission_readiness_audit_REPORT.md` | `../scripts/summarize_submission_readiness_audit.py` |
| Action-risk v0.2 endpoint no-go | `../results/final_paper/ablations/v02_action_risk_endpoint_200ep_can40/REPORT.md` | staged endpoint-check report |
| Action-risk v0.2 policy-coverage diagnostic | `../results/final_paper/tables/v02_policy_coverage_diagnostic_REPORT.md` | `../scripts/summarize_v02_policy_coverage_diagnostic.py` |
| Can 20 support audit | `../results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md` | `../scripts/summarize_can20_support_audit.py` |
| Candidate-breakthrough development audit | `../results/candidate_breakthrough/candidate_breakthrough_decision_REPORT.md` | `../scripts/summarize_candidate_breakthrough_decision.py` |
| Reviewer-facing claim summary | `../paper/REVIEWER_CLAIM_SUMMARY.md` | manually maintained claim-contract summary guarded by validators |
| Final claim contract | `../FINAL_CLAIM_CONTRACT.md` | manually maintained final allowed-claim boundary guarded by validators |

## Expensive Frozen Runs

The common final-run entry point is:

```bash
XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql \
  python scripts/run_final_matrix.py \
  --task can_paired \
  --split-type pos40_bad80 \
  --split-seed 11 \
  --method triage_bc \
  --policy-seed 0 \
  --stage all
```

Primary frozen Robomimic rows use split seeds `11`, `22`, and `33`, policy seed
`0`, fixed epoch-200 endpoints, and 50 validation-positive rollouts per split.

Primary task/method combinations:

- Can 40p/80b: `--task can_paired --split-type pos40_bad80`
- Lift MG: `--task lift_mg --split-type mg_sparse`
- Methods: `triage_bc`, `weighted_bc`, `positive_only_nn`, `bc_all_mixed`,
  `all_train_positive_oracle`

The broad matrix is intentionally expensive. For paper edits, prefer the cheap
regeneration commands above unless a specific claim gap requires rerunning a
frozen row.

## Validation Gates

Before treating the draft as synchronized with the evidence package, run:

```bash
make -C paper validate
python -m py_compile \
  scripts/summarize_final_endpoint_matrix.py \
  scripts/summarize_primary_endpoint_uncertainty.py \
  scripts/summarize_primary_endpoint_paired_bootstrap.py \
  scripts/plot_primary_endpoint_paired_deltas.py \
  scripts/summarize_bad_label_control_table.py \
  scripts/summarize_master_evidence_tables.py \
  scripts/summarize_can40_score_support_tradeoff.py \
  scripts/summarize_v02_union_candidate_audit.py \
  scripts/summarize_v02_union_endpoint_aggregate.py \
  scripts/summarize_hard_union_component_ablation.py \
  scripts/summarize_failure_mode_initial_states.py \
  scripts/summarize_candidate_family_audit.py \
  scripts/summarize_hybrid_candidate_support_audit.py \
  scripts/summarize_hard_negative_can_action_conflict_audit.py \
  scripts/summarize_lift_hard_negative_action_conflict_audit.py \
  scripts/summarize_can_coverage_shift_audit.py \
  scripts/summarize_hard_negative_can_endpoint_smoke.py \
  scripts/summarize_can_prefix_positive_endpoint.py \
  scripts/plot_can_prefix_positive_diagnostic.py \
  scripts/summarize_can_prefix_length_robustness.py \
  scripts/summarize_precision_coverage_frontier.py \
  scripts/summarize_policy_quality_proxy_no_go.py \
  scripts/summarize_active_abstention_evaluation.py \
  scripts/summarize_v02_fresh_gate_uncertainty.py \
  scripts/summarize_sota_cau_v02_portfolio_preflight.py \
  scripts/summarize_sota_cau_v02_fresh606_endpoint_validation.py \
  scripts/summarize_sota_can606_gmm_confidence_cau_router.py \
  scripts/summarize_sota_cau_gmm_router_followup.py \
  scripts/summarize_sota_cau_selector_feature_audit.py \
  scripts/summarize_sota_candidate_sweep.py \
  scripts/validate_paper_artifact_refs.py \
  scripts/validate_paper_claim_numbers.py \
  scripts/validate_paper_structure.py \
  scripts/validate_method_freeze_v02.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/summarize_bad_label_control_table.py
python scripts/summarize_master_evidence_tables.py
python scripts/summarize_can40_score_support_tradeoff.py
python scripts/summarize_v02_union_candidate_audit.py
python scripts/summarize_v02_union_endpoint_aggregate.py
python scripts/summarize_hard_union_component_ablation.py
python scripts/summarize_failure_mode_initial_states.py
python scripts/summarize_candidate_family_audit.py
python scripts/summarize_hybrid_candidate_support_audit.py
python scripts/summarize_hard_negative_can_action_conflict_audit.py
python scripts/summarize_lift_hard_negative_action_conflict_audit.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits
python scripts/summarize_can_prefix_positive_endpoint.py
python scripts/plot_can_prefix_positive_diagnostic.py
python scripts/summarize_can_prefix_length_robustness.py
python scripts/summarize_precision_coverage_frontier.py
python scripts/summarize_policy_quality_proxy_no_go.py
python scripts/summarize_active_abstention_evaluation.py
python scripts/summarize_sota_can606_gmm_confidence_cau_router.py
python scripts/summarize_sota_cau_gmm_router_followup.py
python scripts/summarize_sota_cau_selector_feature_audit.py
python scripts/summarize_sota_candidate_sweep.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
python scripts/validate_method_freeze_v02.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/triage_bc_paper.pdf
pdfinfo paper/iclr2026/main.pdf
git diff --check
```

`make -C paper all` aliases the same Makefile validation gate.

Expected current validator results:

```text
validated paper claim numbers and claim contract against staged CSVs and manuscript text
validated paper figure order, figure-map rows, and PDF layout
checked 151 unique artifact references
validated METHOD_FREEZE_V02 against v0.2 router code and staged artifacts
```

The standalone PDF is currently 18 pages and the provisional ICLR PDF is
currently 15 pages. The artifact-reference count may increase if this
reproduction file or new appendix artifacts are added to the validator.
