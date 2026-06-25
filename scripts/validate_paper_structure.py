from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEX_DOCS = [
    ROOT / "paper" / "triage_bc_paper.tex",
    ROOT / "paper" / "iclr2026" / "main.tex",
]

EXPECTED_FIGURE_LABELS = [
    "fig:pipeline",
    "fig:pointnav",
    "fig:matrix",
    "fig:precision",
    "fig:score-shapes",
    "fig:diagnostic-matrix",
    "fig:paired-deltas",
    "fig:prefix-positive-can",
]

EXPECTED_TABLE_LABELS = [
    "tab:main-results",
    "tab:v02-gate",
    "tab:bad-label-controls",
    "tab:hard-negative-can",
    "tab:coverage-shift-can",
]

EXPECTED_DOC_ROWS = {
    ROOT / "PAPER_DRAFT_OUTLINE.md": [
        "| Figure 1 | `results/final_paper/figures/triage_bc_method_diagram.png` | TRIAGE-BC pipeline |",
        "| Figure 2 | `results/final_paper/figures/pointnav_controlled_mechanism.png` | Controlled mechanism result |",
        "| Figure 3 | `results/final_paper/figures/robotics_primary_endpoint_matrix.png` | Primary Robomimic endpoint matrix |",
        "| Figure 4 | `results/final_paper/figures/can40_precision_coverage.png` | Precision/coverage frontier |",
        "| Figure 5 | `results/final_paper/figures/score_shape_diagnostics.png` | Score-shape and abstention diagnostic |",
        "| Appendix Figure | `results/final_paper/figures/primary_endpoint_paired_deltas.png` | Paired initial-state endpoint uncertainty |",
        "| Appendix Table | `results/final_paper/tables/bad_label_control_summary.csv` | Bad-label versus positive-only control summary |",
    ],
    ROOT / "paper" / "MANUSCRIPT_CHECKLIST.md": [
        "| Figure 1 | `../results/final_paper/figures/triage_bc_method_diagram.pdf` | TRIAGE-BC pipeline and hidden-label-free flow. |",
        "| Figure 2 | `../results/final_paper/figures/pointnav_controlled_mechanism.pdf` | Controlled mechanism evidence. |",
        "| Figure 3 | `../results/final_paper/figures/robotics_primary_endpoint_matrix.pdf` | Primary Robomimic endpoint matrix. |",
        "| Figure 4 | `../results/final_paper/figures/can40_precision_coverage.pdf` | Can 40 precision/coverage frontier. |",
        "| Figure 5 | `../results/final_paper/figures/score_shape_diagnostics.pdf` | Score-shape and abstention diagnostics. |",
        "| Appendix Figure | `../results/final_paper/figures/primary_endpoint_paired_deltas.pdf` | Paired initial-state endpoint uncertainty. |",
        "| Appendix Figure | `../results/final_paper/figures/can_prefix_positive_diagnostic.pdf` | Can prefix-positive generated diagnostic. |",
        "| Main Table | In-source table `tab:v02-gate` in `../paper/triage_bc_paper.tex` | Fresh v0.2 Can+Lift endpoint gate. |",
        "| Appendix Table | `../results/final_paper_v02/tables/v02_fresh_gate_REPORT.md` | Combined v0.2 fresh Can+Lift endpoint gate. |",
        "| Appendix Table | `../results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md` | Fresh v0.2 paired initial-state uncertainty audit. |",
        "| Appendix Table | `../results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md` | Fresh v0.2 hidden-label audit and branch decisions. |",
        "| Appendix Table | `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | Bad-label versus positive-only control summary. |",
        "| Appendix Table | `../results/final_paper/ablations/hard_negative_can_action_conflict_REPORT.md` | Support-only hard-negative Can action-conflict diagnostic. |",
        "| Appendix Table | `../results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md` | Three-split hard-negative Can endpoint check. |",
        "| Appendix Table | `../results/final_paper/ablations/can_coverage_shift_REPORT.md` | Support-only coverage-shift Can diagnostic. |",
        "| Appendix Table | `../results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md` | Three-split coverage-shift Can endpoint check. |",
        "| Appendix Table | `../results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md` | Three-split prefix-positive Can endpoint check. |",
    ],
    ROOT / "paper" / "REPRODUCE_PAPER.md": [
        "| Figure 1, method diagram | `../results/final_paper/figures/triage_bc_method_diagram.pdf` | `../scripts/plot_triage_bc_method_diagram.py` |",
        "| Figure 2, PointNav mechanism | `../results/final_paper/figures/pointnav_controlled_mechanism.pdf` | `../scripts/summarize_pointnav_controlled_mechanism.py` |",
        "| Figure 3, primary robotics matrix | `../results/final_paper/figures/robotics_primary_endpoint_matrix.pdf` | `../scripts/summarize_final_endpoint_matrix.py` |",
        "| Figure 4, Can precision/coverage | `../results/final_paper/figures/can40_precision_coverage.pdf` | `../scripts/summarize_can40_score_support_tradeoff.py`, then `../scripts/plot_can40_precision_coverage.py` |",
        "| Figure 5, score-shape diagnostics | `../results/final_paper/figures/score_shape_diagnostics.pdf` | `../scripts/plot_score_shape_diagnostics.py` |",
        "| Primary paired delta figure | `../results/final_paper/figures/primary_endpoint_paired_deltas.pdf` | `../scripts/plot_primary_endpoint_paired_deltas.py` |",
        "| Bad-label control summary | `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | `../scripts/summarize_bad_label_control_table.py` |",
        "| Fresh v0.2 Can+Lift gate | `../results/final_paper_v02/tables/v02_fresh_gate_REPORT.md` | `../scripts/summarize_v02_fresh_gate.py` |",
        "| Fresh v0.2 uncertainty audit | `../results/final_paper_v02/tables/v02_fresh_gate_uncertainty_REPORT.md` | `../scripts/summarize_v02_fresh_gate_uncertainty.py` |",
        "| Fresh v0.2 router support audit | `../results/final_paper_v02/tables/v02_fresh_router_support_REPORT.md` | `../scripts/summarize_v02_fresh_router_support_audit.py` |",
        "| Master evidence tables | `../results/final_paper/tables/baseline_strength_REPORT.md` | `../scripts/summarize_master_evidence_tables.py` |",
        "| Candidate-family audit | `../results/final_paper/tables/candidate_family_oracle_proxy_REPORT.md` | `../scripts/summarize_candidate_family_audit.py` |",
        "| Hybrid support audit | `../results/final_paper/tables/hybrid_candidate_support_REPORT.md` | `../scripts/summarize_hybrid_candidate_support_audit.py` |",
        "| Hard-negative Can diagnostic | `../results/final_paper/ablations/hard_negative_can_action_conflict_REPORT.md` | `../scripts/summarize_hard_negative_can_action_conflict_audit.py` |",
        "| Hard-negative Can endpoint check | `../results/final_paper/ablations/hard_negative_can_endpoint_200ep/REPORT.md` | `../scripts/summarize_hard_negative_can_endpoint_smoke.py` |",
        "| Coverage-shift Can diagnostic | `../results/final_paper/ablations/can_coverage_shift_REPORT.md` | `../scripts/summarize_can_coverage_shift_audit.py` |",
        "| Coverage-shift Can endpoint check | `../results/final_paper/ablations/can_coverage_shift_endpoint_200ep/REPORT.md` | `../scripts/summarize_hard_negative_can_endpoint_smoke.py` |",
        "| Prefix-positive Can diagnostic figure | `../results/final_paper/figures/can_prefix_positive_diagnostic.pdf` | `../scripts/summarize_can_prefix_positive_endpoint.py`, then `../scripts/plot_can_prefix_positive_diagnostic.py` |",
        "| Prefix-positive Can diagnostic report | `../results/final_paper/tables/can_prefix_positive_diagnostic_REPORT.md` | `../scripts/plot_can_prefix_positive_diagnostic.py` |",
    ],
}

LABEL_PATTERN = re.compile(r"\\label\{(fig:[^}]+)\}")
TABLE_LABEL_PATTERN = re.compile(r"\\label\{(tab:[^}]+)\}")
PDF_PAGES_PATTERN = re.compile(r"^Pages:\s+(\d+)$", re.MULTILINE)


def command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.STDOUT)
    except FileNotFoundError as exc:
        raise RuntimeError(f"required command not found: {args[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"{' '.join(args)} failed:\n{exc.output}") from exc


def pdf_pages(path: Path) -> int:
    output = command_output(["pdfinfo", str(path.relative_to(ROOT))])
    match = PDF_PAGES_PATTERN.search(output)
    if not match:
        raise RuntimeError(f"could not parse page count from pdfinfo for {path.relative_to(ROOT)}")
    return int(match.group(1))


def pdf_page_text(path: Path, page: int) -> str:
    return command_output(
        [
            "pdftotext",
            "-layout",
            "-f",
            str(page),
            "-l",
            str(page),
            str(path.relative_to(ROOT)),
            "-",
        ]
    )


def main() -> None:
    failures: list[str] = []

    for doc in TEX_DOCS:
        text = doc.read_text(encoding="utf-8")
        labels = LABEL_PATTERN.findall(text)
        if labels != EXPECTED_FIGURE_LABELS:
            failures.append(
                f"{doc.relative_to(ROOT)} figure labels are {labels}, "
                f"expected {EXPECTED_FIGURE_LABELS}"
            )
        table_labels = TABLE_LABEL_PATTERN.findall(text)
        if table_labels != EXPECTED_TABLE_LABELS:
            failures.append(
                f"{doc.relative_to(ROOT)} table labels are {table_labels}, "
                f"expected {EXPECTED_TABLE_LABELS}"
            )

    for doc, rows in EXPECTED_DOC_ROWS.items():
        text = doc.read_text(encoding="utf-8")
        for row in rows:
            if row not in text:
                failures.append(f"{doc.relative_to(ROOT)} missing figure-map row: {row}")

    try:
        standalone_pages = pdf_pages(ROOT / "paper" / "triage_bc_paper.pdf")
        iclr_pages = pdf_pages(ROOT / "paper" / "iclr2026" / "main.pdf")
        page9 = pdf_page_text(ROOT / "paper" / "iclr2026" / "main.pdf", 9)
        page10 = pdf_page_text(ROOT / "paper" / "iclr2026" / "main.pdf", 10)
        page11 = pdf_page_text(ROOT / "paper" / "iclr2026" / "main.pdf", 11)
    except RuntimeError as exc:
        failures.append(str(exc))
    else:
        if standalone_pages != 17:
            failures.append(f"paper/triage_bc_paper.pdf has {standalone_pages} pages, expected 17")
        if iclr_pages != 15:
            failures.append(f"paper/iclr2026/main.pdf has {iclr_pages} pages, expected 15")
        if not re.search(r"\b8\s+C ONCLUSION\b", page9):
            failures.append("paper/iclr2026/main.pdf page 9 no longer contains the conclusion heading")
        if "R EFERENCES" in page9:
            failures.append("paper/iclr2026/main.pdf page 9 contains references; main text budget drifted")
        if "R EFERENCES" not in page10:
            failures.append("paper/iclr2026/main.pdf page 10 no longer starts the references")
        if "A    A S IMPLE P RECISION /C OVERAGE A NALYSIS" not in page11:
            failures.append("paper/iclr2026/main.pdf page 11 no longer starts the appendix")

    if failures:
        print("paper structure validation failed:")
        for failure in failures:
            print(f"- {failure}")
        sys.exit(1)

    print("validated paper figure order, figure-map rows, and PDF layout")


if __name__ == "__main__":
    main()
