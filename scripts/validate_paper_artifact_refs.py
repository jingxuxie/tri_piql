from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "PAPER_DRAFT_OUTLINE.md",
    ROOT / "FINAL_CLAIM_CONTRACT.md",
    ROOT / "paper" / "MANUSCRIPT_CHECKLIST.md",
    ROOT / "paper" / "README.md",
    ROOT / "paper" / "REPRODUCE_PAPER.md",
    ROOT / "paper" / "REVIEWER_CLAIM_SUMMARY.md",
    ROOT / "paper" / "triage_bc_draft.md",
    ROOT / "results" / "final_paper" / "README.md",
]
TEX_DOCS = [
    ROOT / "paper" / "triage_bc_paper.tex",
    ROOT / "paper" / "iclr2026" / "main.tex",
]

PATH_PATTERN = re.compile(
    r"`((?:\.\./)?(?:results|configs|paper|scripts|METHOD_FREEZE|PAPER_DRAFT_OUTLINE|FINAL_CLAIM_CONTRACT|REGIME_PROBE_SUITE|tri_piql_paper_completion_plan)[^`]*?)`"
)
INCLUDEGRAPHICS_PATTERN = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
BIBLIOGRAPHY_PATTERN = re.compile(r"\\bibliography\{([^}]+)\}")
TEX_PATH_PATTERN = re.compile(r"\\path\{([^}]+)\}")


def normalize(raw: str, doc: Path) -> Path | None:
    if "{" in raw or "}" in raw:
        return None
    if raw.endswith("/"):
        return None
    if raw.startswith("../"):
        return (doc.parent / raw).resolve()
    return (ROOT / raw).resolve()


def normalize_tex_path(raw: str, doc: Path) -> Path | None:
    if "{" in raw or "}" in raw:
        return None
    if raw.startswith("/"):
        return Path(raw).resolve()
    return (doc.parent / raw).resolve()


def main() -> None:
    missing: list[str] = []
    checked: list[Path] = []
    for doc in DOCS:
        text = doc.read_text(encoding="utf-8")
        for match in PATH_PATTERN.finditer(text):
            raw = match.group(1).strip()
            path = normalize(raw, doc)
            if path is None:
                continue
            checked.append(path)
            if not path.exists():
                missing.append(f"{doc.relative_to(ROOT)} -> {raw}")

    for doc in TEX_DOCS:
        text = doc.read_text(encoding="utf-8")
        for match in TEX_PATH_PATTERN.finditer(text):
            raw = match.group(1).strip()
            if not raw.startswith(("../", "../../", "/", "results/", "configs/", "paper/", "scripts/")):
                continue
            path = normalize_tex_path(raw, doc)
            if path is None or raw.endswith("/"):
                continue
            checked.append(path)
            if not path.exists():
                missing.append(f"{doc.relative_to(ROOT)} -> {raw}")
        for match in INCLUDEGRAPHICS_PATTERN.finditer(text):
            raw = match.group(1).strip()
            path = normalize_tex_path(raw, doc)
            if path is None:
                continue
            checked.append(path)
            if not path.exists():
                missing.append(f"{doc.relative_to(ROOT)} -> {raw}")
        for match in BIBLIOGRAPHY_PATTERN.finditer(text):
            raw_items = match.group(1).split(",")
            for raw_item in raw_items:
                raw = raw_item.strip()
                if not raw:
                    continue
                bib_path = normalize_tex_path(f"{raw}.bib", doc)
                if bib_path is None:
                    continue
                checked.append(bib_path)
                if not bib_path.exists():
                    missing.append(f"{doc.relative_to(ROOT)} -> {raw}.bib")

    if missing:
        print("missing artifact references:")
        for item in missing:
            print(f"- {item}")
        sys.exit(1)

    unique_count = len({path for path in checked})
    print(f"checked {unique_count} unique artifact references")


if __name__ == "__main__":
    main()
