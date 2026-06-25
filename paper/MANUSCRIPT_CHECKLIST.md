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
- Bibliography: `../paper/references.bib`
- Reproduction checklist: `../paper/REPRODUCE_PAPER.md`
- Section and number map: `../PAPER_DRAFT_OUTLINE.md`
- Claim package: `../results/PAPER_CLAIM_PACKAGE.md`
- Frozen method contract: `../METHOD_FREEZE.md`
- Final artifact root: `../results/final_paper/`

Current status: the standalone draft is claim-safe and compileable, and a
provisional ICLR 2026 conversion also compiles. The ICLR source uses the
official ICLR 2026 style files as a provisional submission shell; refresh the
style files if the target venue or target year changes. The current ICLR PDF is
14 pages total, with references beginning on page 10 and the appendix beginning
on page 11. The result order is PointNav-first mechanism evidence, then
Robomimic endpoint evidence.

## Main-Paper Claims

| Claim | Status | Evidence |
|---|---|---|
| Mixed logs can hurt naive cloning. | Supported. | Lift all-demo `31/150`; Can 40 all-demo `81/150`; PointNav mixed-log degradation in `../results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md`. |
| Scarce positives and failures can recover useful hidden support in a controlled mechanism task. | Supported. | PointNav label-budget-2 score-gap support reaches `1.000` success in `../results/final_paper/tables/pointnav_controlled_mechanism_REPORT.md` and `../results/final_paper/figures/pointnav_controlled_mechanism.pdf`. |
| Hard selected support can beat soft weighted sampling under paired Can contamination. | Supported, narrow. | Can 40p/80b: TRIAGE-BC `99/150`, weighted BC `90/150`, all-demo BC `81/150` in `../results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`. |
| Strong positive-only retrieval must be a first-class baseline. | Supported. | Can 40p/80b positive-only NN `108/150`; Can 20 and Can 80 diagnostics in `../results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md` and `../results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`. |
| Broad weighted coverage can beat purer hard support. | Supported. | Lift MG weighted BC `93/150`, TRIAGE-BC `74/150`, positive-only NN `82/150` in `../results/final_paper/tables/robotics_primary_endpoint_matrix_REPORT.md`. |
| Ambiguous MG score shapes require abstention or better branch validation. | Supported as limitation. | Score-shape figure `../results/final_paper/figures/score_shape_diagnostics.pdf` and branch-proxy failure report `../results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md`. |

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
| Main Table | In-source table in `../paper/triage_bc_paper.tex` | Main Can 40p/80b and Lift MG endpoint counts. |
| Appendix Table | In-source table `tab:bad-label-controls` backed by `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | Bad-label versus positive-only control summary in the compiled appendix. |
| Appendix Table | `../results/final_paper/tables/primary_endpoint_paired_bootstrap_REPORT.md` | Paired initial-state bootstrap uncertainty audit. |
| Appendix Table | `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | Bad-label versus positive-only control summary. |
| Appendix Reproducibility Map | In-source appendix in `../paper/triage_bc_paper.tex` and `../paper/iclr2026/main.tex` | Fixed method contract, regeneration docs, diagnostic evidence, and artifact references. |

## Appendix-Only Diagnostics

| Diagnostic | Status | Evidence |
|---|---|---|
| PointNav bad-label count | Appendix-only mechanism evidence. | With 5 positive prefixes and `1/2/5` labeled bad shortcuts, selected support has `1.000` demo purity, `1.000` transition purity, and `0 hidden-bad` demos in every row; `1 labeled bad shortcut` and 5 labeled bad shortcuts both reach `1.000` success at all tested contamination levels in `../results/final_paper/ablations/continuous_pointnav_bad_label_count_npos5_REPORT.md`. |
| Can 20p/80b | Appendix-only caveat. | Positive-only `54/100`, TRIAGE-BC `46/100`, weighted split-11 `18/50`; support audit finds TRIAGE `54/60` hidden positives and `69/240` hidden bad versus positive-only `49/60` hidden positives and `11/240` hidden bad in `../results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md`. |
| Can 80p/80b | Appendix-only caveat. | Split-33 positive-only `49/50`, TRIAGE-BC `43/50`; report in `../results/final_paper/ablations/can_paired_balanced_80p80b_support_and_split33_endpoint_REPORT.md`. |
| Can MG | Abstention / branch-proxy limitation. | Original-MG weighted BC is rollout-best at `0.333`, while proxies choose all-positive at `0.200`, in `../results/final_paper/ablations/can_mg_branch_proxy_summary/REPORT.md`. |
| Lift classifier top160 | Coverage limitation. | Fixed classifier top160 reaches `68/150`, below weighted BC `93/150`, in `../results/final_paper/ablations/lift_mg_classifier_top160_endpoint_summary_REPORT.md`. |
| Square / Transport | Repository-only for now. | Keep in `../results/PAPER_CLAIM_PACKAGE.md` unless a later draft needs support-side relative-quality diagnostics. |

## Required Validation Before Any Submission Draft

Run from the repository root:

```bash
make -C paper validate
python -m py_compile scripts/summarize_final_endpoint_matrix.py scripts/summarize_primary_endpoint_uncertainty.py scripts/summarize_primary_endpoint_paired_bootstrap.py scripts/plot_primary_endpoint_paired_deltas.py scripts/summarize_bad_label_control_table.py scripts/validate_paper_artifact_refs.py scripts/validate_paper_claim_numbers.py scripts/validate_paper_structure.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/summarize_bad_label_control_table.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
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
- Artifact validator checks 72 unique references, including the ICLR
  source graphics and bibliography.
- Claim-number validator passes against staged CSVs, the standalone manuscript,
  the ICLR manuscript, and the Markdown draft, and it enforces the core
  overclaim-avoidance caveats.
- Structure validator passes for manuscript figure-label order, figure-map
  rows, required table labels, PDF page counts, and ICLR page-boundary markers.
- Paired bootstrap audit regenerates from staged per-episode metrics.
- Paired initial-state delta figure regenerates from staged per-episode metrics.
- Bad-label control summary regenerates from staged final-paper tables and
  support audits.
- PDF compiles from `../paper/triage_bc_paper.tex`.
- LaTeX log scan has no warning, underfull, or overfull matches.
- ICLR PDF compiles from `../paper/iclr2026/main.tex`; the current page audit
  has references on page 10 and appendix material starting on page 11.
- The paper remains explicit that the result is score-to-support conversion for
  behavior cloning, not validated inverse-Q robotics.

## Open Decisions

1. Confirm the final venue/year and refresh the style files if the target is
   not ICLR 2026.
2. Add venue-specific tests only if the chosen venue expects them; the current
   paper uses Wilson intervals, paired initial-state bootstraps, and split-level
   context.
