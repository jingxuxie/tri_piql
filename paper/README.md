# TRIAGE-BC Paper Draft

This directory contains manuscript-facing text derived from the frozen
`results/final_paper/` evidence package.

Current files:

- `../paper/triage_bc_draft.md`: claim-safe Markdown manuscript draft.
- `../paper/triage_bc_paper.tex`: standalone compileable LaTeX manuscript
  scaffold.
- `../paper/iclr2026/main.tex`: provisional ICLR-format LaTeX manuscript
  derived from the standalone source.
- `../paper/iclr2026/main.pdf`: compiled provisional ICLR-format PDF.
- `../paper/references.bib`: initial bibliography for the LaTeX scaffold.
- `../paper/iclr2026/references.bib`: bibliography copy used by the ICLR shell.
- `../paper/Makefile`: local build helper for the standalone and ICLR-format
  LaTeX scaffolds.
- `../paper/REPRODUCE_PAPER.md`: commands and artifact map for regenerating
  the current paper package from staged evidence.
- `../paper/MANUSCRIPT_CHECKLIST.md`: claim, figure, appendix, validation, and
  open-decision checklist for template conversion.
- `../scripts/validate_paper_artifact_refs.py`: checks that draft artifact
  references resolve to local files.
- `../scripts/validate_paper_claim_numbers.py`: checks quoted manuscript
  numbers against staged final-paper CSVs and enforces the main claim-contract
  caveats.
- `../scripts/validate_paper_structure.py`: checks figure-label order,
  figure-map rows, PDF page counts, and ICLR page-boundary markers.
- `../scripts/summarize_primary_endpoint_paired_bootstrap.py`: regenerates the
  paired initial-state bootstrap audit for the primary endpoint matrix.
- `../scripts/plot_primary_endpoint_paired_deltas.py`: regenerates the paired
  initial-state delta CSV, report, and appendix uncertainty figure.
- `../scripts/summarize_bad_label_control_table.py`: regenerates the compact
  bad-label control summary table and report.
- `../scripts/summarize_master_evidence_tables.py`: regenerates standardized
  endpoint/support master tables and the baseline-strength completeness report.
- `../scripts/summarize_candidate_family_audit.py`: regenerates the
  candidate-family oracle/proxy audit for the v0.2 decision gate.
- `../scripts/summarize_hybrid_candidate_support_audit.py`: regenerates the
  support-only hybrid positive-NN / classifier candidate audit.
- `../scripts/summarize_hard_negative_can_action_conflict_audit.py`:
  regenerates the hard-negative Can action-conflict support diagnostic.
- `../scripts/summarize_hard_negative_can_endpoint_smoke.py`: regenerates
  the hard-negative Can endpoint smoke and three-split endpoint-check summaries
  from completed metrics.
- `../scripts/summarize_can_prefix_positive_endpoint.py`: regenerates the
  prefix-positive Can split and aggregate endpoint summaries from completed
  evaluations.
- `../scripts/plot_can_prefix_positive_diagnostic.py`: regenerates the
  prefix-positive Can paper-facing summary CSV, report, and appendix-ready
  figure.
- `../scripts/summarize_v02_fresh_can_endpoint.py`,
  `../scripts/summarize_v02_fresh_lift_endpoint.py`,
  `../scripts/summarize_v02_fresh_router_support_audit.py`, and
  `../scripts/summarize_v02_fresh_gate.py`: regenerate the frozen v0.2 fresh
  Can+Lift endpoint gate and router support audit.
- `../scripts/summarize_v02_fresh_gate_uncertainty.py`: regenerates the paired
  initial-state uncertainty audit for the frozen v0.2 fresh gate.

Authoritative supporting files:

- `../PAPER_DRAFT_OUTLINE.md`: section plan, figure map, and main numbers.
- `../METHOD_FREEZE.md`: frozen TRIAGE-BC v0.1 method contract.
- `../METHOD_FREEZE_V02.md`: frozen TRIAGE-BC v0.2 portfolio-router contract.
- `../results/PAPER_CLAIM_PACKAGE.md`: current claim package and caveats.
- `../results/final_paper/README.md`: staged final-paper artifact index.
- `../results/final_paper_v02/README.md`: staged fresh v0.2 artifact index.

Status:

- The canonical editable source remains the standalone `article` draft at
  `../paper/triage_bc_paper.tex`.
- A provisional ICLR 2026 conversion is available at
  `../paper/iclr2026/main.tex`. It uses the official ICLR 2026 style files as a
  submission-format shell; refresh these files if the target venue or target
  year changes. The ICLR author guide used for this provisional shell is
  https://iclr.cc/Conferences/2026/AuthorGuide.
- The current standalone compile is 17 pages.
- The current ICLR compile is 15 pages total. References begin on page 10 and
  the appendix begins on page 11, so the main text fits the ICLR 2026 9-page
  submission main-text budget.
- Main claims should remain synchronized with `results/PAPER_CLAIM_PACKAGE.md`
  and `results/paper_tables/claim_matrix.csv`.

Validation:

The shortest manuscript gate is:

```bash
make -C paper validate
```

`make -C paper all` currently aliases the same gate. It rebuilds both PDFs,
regenerates the paired-bootstrap audit, master evidence tables,
candidate-family audit, hybrid support audit, hard-negative Can support
diagnostic, hard-negative endpoint-check summaries, coverage-shift diagnostics,
prefix-positive diagnostic artifacts, the v0.2 fresh Can+Lift gate, and the
v0.2 fresh-gate uncertainty audit, runs the Python validators, and fails if the
configured LaTeX log scans find matches.

The expanded manual command sequence is:

```bash
python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/plot_primary_endpoint_paired_deltas.py scripts/summarize_bad_label_control_table.py scripts/summarize_master_evidence_tables.py scripts/summarize_candidate_family_audit.py scripts/summarize_hybrid_candidate_support_audit.py scripts/summarize_hard_negative_can_action_conflict_audit.py scripts/summarize_can_coverage_shift_audit.py scripts/summarize_hard_negative_can_endpoint_smoke.py scripts/summarize_can_prefix_positive_endpoint.py scripts/plot_can_prefix_positive_diagnostic.py scripts/summarize_v02_fresh_can_endpoint.py scripts/summarize_v02_fresh_lift_endpoint.py scripts/summarize_v02_fresh_router_support_audit.py scripts/summarize_v02_fresh_gate.py scripts/summarize_v02_fresh_gate_uncertainty.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/summarize_bad_label_control_table.py
python scripts/summarize_master_evidence_tables.py
python scripts/summarize_candidate_family_audit.py
python scripts/summarize_hybrid_candidate_support_audit.py
python scripts/summarize_hard_negative_can_action_conflict_audit.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split101 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split202 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep/split303 --eval-subdir eval_50ep --summary-name endpoint_200ep_summary.csv --report-name REPORT.md
python scripts/summarize_hard_negative_can_endpoint_smoke.py --root results/final_paper/ablations/hard_negative_can_endpoint_200ep --eval-subdir eval_50ep --summary-name endpoint_200ep_3split_summary.csv --report-name REPORT.md --aggregate-splits
python scripts/summarize_can_prefix_positive_endpoint.py
python scripts/plot_can_prefix_positive_diagnostic.py
python scripts/summarize_v02_fresh_can_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303
python scripts/summarize_v02_fresh_lift_endpoint.py --root results/final_paper_v02 --split-seeds 101 202 303
python scripts/summarize_v02_fresh_router_support_audit.py --root results/final_paper_v02 --out-dir results/final_paper_v02/tables --split-seeds 101 202 303 --tasks can40 lift_mg
python scripts/summarize_v02_fresh_gate.py --root results/final_paper_v02
python scripts/summarize_v02_fresh_gate_uncertainty.py --root results/final_paper_v02
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
rg -n "undefined|Undefined|LaTeX Warning|Package .*Warning|Overfull|Underfull" paper/triage_bc_paper.log
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
```
