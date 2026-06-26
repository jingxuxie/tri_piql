.PHONY: all validate standalone iclr clean

ROOT := ..

all: validate

validate:
	cd $(ROOT) && python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/validate_method_freeze_v02.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/plot_primary_endpoint_paired_deltas.py scripts/summarize_bad_label_control_table.py scripts/summarize_master_evidence_tables.py scripts/summarize_can40_score_support_tradeoff.py scripts/summarize_v02_union_candidate_audit.py scripts/summarize_v02_union_endpoint_aggregate.py scripts/summarize_hard_union_component_ablation.py scripts/summarize_failure_mode_initial_states.py scripts/summarize_candidate_family_audit.py scripts/summarize_hybrid_candidate_support_audit.py scripts/summarize_hard_negative_can_action_conflict_audit.py scripts/summarize_lift_hard_negative_action_conflict_audit.py scripts/summarize_can_coverage_shift_audit.py scripts/summarize_hard_negative_can_endpoint_smoke.py scripts/summarize_can_prefix_positive_endpoint.py scripts/plot_can_prefix_positive_diagnostic.py scripts/summarize_can_prefix_length_robustness.py scripts/summarize_generated_regime_probe_table.py scripts/summarize_precision_coverage_frontier.py scripts/summarize_policy_quality_proxy_no_go.py scripts/summarize_active_abstention_evaluation.py scripts/summarize_v02_fresh_can_endpoint.py scripts/summarize_v02_fresh_lift_endpoint.py scripts/summarize_v02_fresh_router_support_audit.py scripts/summarize_v02_fresh_gate.py scripts/summarize_v02_fresh_gate_uncertainty.py scripts/summarize_v02_fresh_baseline_coverage.py scripts/summarize_v02_router_regret_table.py scripts/summarize_submission_readiness_audit.py
	cd $(ROOT) && python scripts/summarize_primary_endpoint_paired_bootstrap.py
	cd $(ROOT) && python scripts/plot_primary_endpoint_paired_deltas.py
	cd $(ROOT) && python scripts/summarize_bad_label_control_table.py
	cd $(ROOT) && python scripts/summarize_master_evidence_tables.py
	cd $(ROOT) && python scripts/summarize_can40_score_support_tradeoff.py
	cd $(ROOT) && python scripts/summarize_v02_union_candidate_audit.py
	cd $(ROOT) && python scripts/summarize_v02_union_endpoint_aggregate.py
	cd $(ROOT) && python scripts/summarize_hard_union_component_ablation.py
	cd $(ROOT) && python scripts/summarize_failure_mode_initial_states.py
	cd $(ROOT) && python scripts/summarize_candidate_family_audit.py
	cd $(ROOT) && python scripts/summarize_hybrid_candidate_support_audit.py
	cd $(ROOT) && python scripts/summarize_hard_negative_can_action_conflict_audit.py
	cd $(ROOT) && python scripts/summarize_lift_hard_negative_action_conflict_audit.py
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Lift Hard-Negative' --diagnostic-description 'generated Lift hard-negative/action-conflict diagnostic' --mechanism-sentence 'The endpoint result is directionally consistent with the support audit: bad-aware proxy top40 keeps more hidden-positive support and admits fewer hidden-bad demos than state-action positive-NN top40.' --claim-scope-sentence 'This is one split of the completed three-split non-Can mechanism evidence; absolute Lift success remains low and should be framed as exploratory.' --followup-path results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split101/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Lift Hard-Negative' --diagnostic-description 'generated Lift hard-negative/action-conflict diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the bad-aware candidate keeps near-positive coverage while sharply reducing action-conflict bad-demo admission.' --claim-scope-sentence 'This is one split of the completed three-split non-Can mechanism evidence; absolute Lift success remains low and should be framed as exploratory.' --followup-path results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split202/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Lift Hard-Negative' --diagnostic-description 'generated Lift hard-negative/action-conflict diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the bad-aware candidate keeps more hidden-positive coverage while reducing action-conflict bad-demo admission.' --claim-scope-sentence 'This is completed three-split non-Can mechanism evidence, but absolute Lift success remains low and should be framed as exploratory.' --followup-path results/final_paper/ablations/lift_hard_negative_endpoint_200ep/split303/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/lift_hard_negative_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Lift Hard-Negative' --diagnostic-description 'generated Lift hard-negative/action-conflict diagnostic' --mechanism-sentence 'The endpoint effect is directionally consistent with the support audits: bad-aware proxy top40 selects substantially more hidden-positive demos and fewer hard negatives than state-action positive-NN top40.' --claim-scope-sentence 'This is completed three-split non-Can mechanism evidence, but it remains a low-success exploratory diagnostic rather than a primary Robomimic benchmark row.' --aggregate-splits
	cd $(ROOT) && python scripts/summarize_can_coverage_shift_audit.py
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is one split of the completed targeted coverage-shift diagnostic; keep it separate from the primary Robomimic benchmark rows.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows unless the manuscript explicitly frames it as generated diagnostic evidence.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md
	cd $(ROOT) && python scripts/summarize_can_prefix_positive_endpoint.py
	cd $(ROOT) && python scripts/plot_can_prefix_positive_diagnostic.py
	cd $(ROOT) && python scripts/summarize_can_prefix_length_robustness.py
	cd $(ROOT) && python scripts/summarize_generated_regime_probe_table.py
	cd $(ROOT) && python scripts/summarize_precision_coverage_frontier.py
	cd $(ROOT) && python scripts/summarize_policy_quality_proxy_no_go.py
	cd $(ROOT) && python scripts/summarize_active_abstention_evaluation.py
	cd $(ROOT) && python scripts/summarize_v02_fresh_can_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
	cd $(ROOT) && python scripts/summarize_v02_fresh_lift_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
	cd $(ROOT) && python scripts/summarize_v02_fresh_router_support_audit.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables --split-seeds 101 202 303 404 505 --tasks can40 lift_mg
	cd $(ROOT) && python scripts/summarize_v02_fresh_gate.py --root results/final_paper_v02
	cd $(ROOT) && python scripts/summarize_v02_fresh_gate_uncertainty.py --root results/final_paper_v02
	cd $(ROOT) && python scripts/summarize_v02_fresh_baseline_coverage.py --root results/final_paper_v02 --split-seeds 101 202 303 404 505
	cd $(ROOT) && python scripts/summarize_v02_router_regret_table.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables
	cd $(ROOT) && python scripts/summarize_submission_readiness_audit.py
	latexmk -pdf -interaction=nonstopmode -halt-on-error triage_bc_paper.tex
	latexmk -pdf -cd -interaction=nonstopmode -halt-on-error iclr2026/main.tex
	cd $(ROOT) && python scripts/validate_paper_claim_numbers.py
	cd $(ROOT) && python scripts/validate_paper_structure.py
	cd $(ROOT) && python scripts/validate_paper_artifact_refs.py
	cd $(ROOT) && python scripts/validate_method_freeze_v02.py
	! rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" triage_bc_paper.log
	! rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" iclr2026/main.log

standalone: triage_bc_paper.pdf

triage_bc_paper.pdf: triage_bc_paper.tex references.bib
	latexmk -pdf -interaction=nonstopmode -halt-on-error triage_bc_paper.tex

iclr: iclr2026/main.pdf

iclr2026/main.pdf: iclr2026/main.tex iclr2026/references.bib
	latexmk -pdf -cd -interaction=nonstopmode -halt-on-error iclr2026/main.tex

clean:
	latexmk -c triage_bc_paper.tex
	latexmk -c -cd iclr2026/main.tex
