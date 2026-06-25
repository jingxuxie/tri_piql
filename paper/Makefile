.PHONY: all validate standalone iclr clean

ROOT := ..

all: validate

validate:
	cd $(ROOT) && python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/plot_primary_endpoint_paired_deltas.py scripts/summarize_bad_label_control_table.py scripts/summarize_master_evidence_tables.py scripts/summarize_candidate_family_audit.py scripts/summarize_hybrid_candidate_support_audit.py scripts/summarize_hard_negative_can_action_conflict_audit.py scripts/summarize_can_coverage_shift_audit.py scripts/summarize_hard_negative_can_endpoint_smoke.py scripts/summarize_can_prefix_positive_endpoint.py scripts/plot_can_prefix_positive_diagnostic.py scripts/summarize_v02_fresh_can_endpoint.py scripts/summarize_v02_fresh_lift_endpoint.py scripts/summarize_v02_fresh_router_support_audit.py scripts/summarize_v02_fresh_gate.py scripts/summarize_v02_fresh_gate_uncertainty.py
	cd $(ROOT) && python scripts/summarize_primary_endpoint_paired_bootstrap.py
	cd $(ROOT) && python scripts/plot_primary_endpoint_paired_deltas.py
	cd $(ROOT) && python scripts/summarize_bad_label_control_table.py
	cd $(ROOT) && python scripts/summarize_master_evidence_tables.py
	cd $(ROOT) && python scripts/summarize_candidate_family_audit.py
	cd $(ROOT) && python scripts/summarize_hybrid_candidate_support_audit.py
	cd $(ROOT) && python scripts/summarize_hard_negative_can_action_conflict_audit.py
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits
	cd $(ROOT) && python scripts/summarize_can_coverage_shift_audit.py
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows until the multi-split check is run.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split101/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows until the multi-split check is run.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split202/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows until the multi-split check is run.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/split303/REPORT.md
	cd $(ROOT) && python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/can_coverage_shift_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits --diagnostic-name 'Can Coverage-Shift' --diagnostic-description 'generated scarce-positive coverage-shift Can diagnostic' --mechanism-sentence 'The endpoint effect is consistent with the support audit: the hybrid keeps nearly all hidden-positive coverage while reducing hidden-bad contamination under initial-pose coverage shift.' --claim-scope-sentence 'This is targeted coverage-shift diagnostic evidence; keep it separate from the primary Robomimic benchmark rows unless the manuscript explicitly frames it as generated diagnostic evidence.' --followup-path results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md
	cd $(ROOT) && python scripts/summarize_can_prefix_positive_endpoint.py
	cd $(ROOT) && python scripts/plot_can_prefix_positive_diagnostic.py
	cd $(ROOT) && python scripts/summarize_v02_fresh_can_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303
	cd $(ROOT) && python scripts/summarize_v02_fresh_lift_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303
	cd $(ROOT) && python scripts/summarize_v02_fresh_router_support_audit.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables --split-seeds 101 202 303 --tasks can40 lift_mg
	cd $(ROOT) && python scripts/summarize_v02_fresh_gate.py --root results/final_paper_v02
	cd $(ROOT) && python scripts/summarize_v02_fresh_gate_uncertainty.py --root results/final_paper_v02
	latexmk -pdf -interaction=nonstopmode -halt-on-error triage_bc_paper.tex
	latexmk -pdf -cd -interaction=nonstopmode -halt-on-error iclr2026/main.tex
	cd $(ROOT) && python scripts/validate_paper_claim_numbers.py
	cd $(ROOT) && python scripts/validate_paper_structure.py
	cd $(ROOT) && python scripts/validate_paper_artifact_refs.py
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
