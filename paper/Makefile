.PHONY: all validate standalone iclr clean

ROOT := ..

all: validate

validate:
	cd $(ROOT) && python -m py_compile scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/plot_primary_endpoint_paired_deltas.py scripts/summarize_bad_label_control_table.py
	cd $(ROOT) && python scripts/summarize_primary_endpoint_paired_bootstrap.py
	cd $(ROOT) && python scripts/plot_primary_endpoint_paired_deltas.py
	cd $(ROOT) && python scripts/summarize_bad_label_control_table.py
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
