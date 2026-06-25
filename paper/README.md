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

Authoritative supporting files:

- `../PAPER_DRAFT_OUTLINE.md`: section plan, figure map, and main numbers.
- `../METHOD_FREEZE.md`: frozen TRIAGE-BC v0.1 method contract.
- `../results/PAPER_CLAIM_PACKAGE.md`: current claim package and caveats.
- `../results/final_paper/README.md`: staged final-paper artifact index.

Status:

- The canonical editable source remains the standalone `article` draft at
  `../paper/triage_bc_paper.tex`.
- A provisional ICLR 2026 conversion is available at
  `../paper/iclr2026/main.tex`. It uses the official ICLR 2026 style files as a
  submission-format shell; refresh these files if the target venue or target
  year changes. The ICLR author guide used for this provisional shell is
  https://iclr.cc/Conferences/2026/AuthorGuide.
- The current ICLR compile is 14 pages total. References begin on page 10 and
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
regenerates the paired-bootstrap audit, runs the Python validators, and fails if
the LaTeX warning scans find matches.

The expanded manual command sequence is:

```bash
python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/plot_primary_endpoint_paired_deltas.py scripts/summarize_bad_label_control_table.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/summarize_bad_label_control_table.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
```
