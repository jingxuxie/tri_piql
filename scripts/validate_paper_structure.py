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
]

EXPECTED_TABLE_LABELS = [
    "tab:main-results",
    "tab:bad-label-controls",
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
        "| Appendix Table | `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | Bad-label versus positive-only control summary. |",
    ],
    ROOT / "paper" / "REPRODUCE_PAPER.md": [
        "| Figure 1, method diagram | `../results/final_paper/figures/triage_bc_method_diagram.pdf` | `../scripts/plot_triage_bc_method_diagram.py` |",
        "| Figure 2, PointNav mechanism | `../results/final_paper/figures/pointnav_controlled_mechanism.pdf` | `../scripts/summarize_pointnav_controlled_mechanism.py` |",
        "| Figure 3, primary robotics matrix | `../results/final_paper/figures/robotics_primary_endpoint_matrix.pdf` | `../scripts/summarize_final_endpoint_matrix.py` |",
        "| Figure 4, Can precision/coverage | `../results/final_paper/figures/can40_precision_coverage.pdf` | `../scripts/summarize_can40_score_support_tradeoff.py`, then `../scripts/plot_can40_precision_coverage.py` |",
        "| Figure 5, score-shape diagnostics | `../results/final_paper/figures/score_shape_diagnostics.pdf` | `../scripts/plot_score_shape_diagnostics.py` |",
        "| Primary paired delta figure | `../results/final_paper/figures/primary_endpoint_paired_deltas.pdf` | `../scripts/plot_primary_endpoint_paired_deltas.py` |",
        "| Bad-label control summary | `../results/final_paper/tables/bad_label_control_summary_REPORT.md` | `../scripts/summarize_bad_label_control_table.py` |",
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
        if standalone_pages != 15:
            failures.append(f"paper/triage_bc_paper.pdf has {standalone_pages} pages, expected 15")
        if iclr_pages != 14:
            failures.append(f"paper/iclr2026/main.pdf has {iclr_pages} pages, expected 14")
        if "8     C ONCLUSION" not in page9:
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
