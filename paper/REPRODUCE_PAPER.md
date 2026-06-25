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

Final paper artifacts are staged under:

- `../results/final_paper/`

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
python scripts/plot_can40_precision_coverage.py
python scripts/summarize_final_endpoint_matrix.py
python scripts/summarize_primary_endpoint_uncertainty.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/summarize_bad_label_control_table.py
python scripts/plot_score_shape_diagnostics.py
python scripts/summarize_can20_support_audit.py
```

Then validate local artifact references and compile the standalone draft plus
the provisional ICLR-format draft:

```bash
make -C paper validate
```

The `paper/Makefile` gate rebuilds both PDFs, regenerates the paired-bootstrap
audit, runs the Python validators, and fails if the LaTeX warning scans find
matches. The expanded manual command sequence is:

```bash
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
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
| Can 20 support audit | `../results/final_paper/ablations/can_paired_pos20_bad80_support_audit_3split_REPORT.md` | `../scripts/summarize_can20_support_audit.py` |

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
  scripts/validate_paper_artifact_refs.py \
  scripts/validate_paper_claim_numbers.py \
  scripts/validate_paper_structure.py
python scripts/summarize_primary_endpoint_paired_bootstrap.py
python scripts/plot_primary_endpoint_paired_deltas.py
python scripts/summarize_bad_label_control_table.py
python scripts/validate_paper_claim_numbers.py
python scripts/validate_paper_structure.py
python scripts/validate_paper_artifact_refs.py
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/triage_bc_paper.tex
latexmk -pdf -cd -interaction=nonstopmode -halt-on-error paper/iclr2026/main.tex
rg -n "undefined|Undefined|LaTeX Warning|Package natbib Warning|Overfull" paper/iclr2026/main.log
pdfinfo paper/iclr2026/main.pdf
git diff --check
```

`make -C paper all` aliases the same Makefile validation gate.

Expected current validator results:

```text
validated paper claim numbers and claim contract against staged CSVs and manuscript text
validated paper figure order, figure-map rows, and PDF layout
checked 72 unique artifact references
```

The count may increase if this reproduction file or new appendix artifacts are
added to the validator.
