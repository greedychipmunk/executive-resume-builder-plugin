#!/usr/bin/env python3
"""Extract an existing PDF or LibreOffice (.odt) resume into structured Markdown.

Markdown is the canonical, editable source. Importing always goes through this
script so downstream skills edit clean text. Extraction artifacts (merged
columns, dropped bullets, scrambled order) are surfaced as warnings because they
usually reveal real ATS parsing problems worth telling the user about.

Fallback chains:
  .odt :  pandoc -> gfm   (preferred)        -> LibreOffice odt->txt
  .pdf :  pdfplumber                          -> pypdf -> `pdftotext -layout`

Usage:
  python extract.py resume.pdf            # prints Markdown to stdout
  python extract.py resume.odt -o out.md  # writes Markdown to file
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

BULLET_RE = re.compile(r"^[•‣◦⁃∙•◦‣·*\-–]\s+")
SECTION_WORDS = {
    "experience", "professional experience", "work experience", "employment",
    "education", "skills", "technical skills", "core competencies", "summary",
    "professional summary", "profile", "certifications", "projects", "awards",
    "publications", "leadership", "volunteer", "languages", "interests",
}


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def libreoffice_bin() -> str | None:
    for cand in ("soffice", "libreoffice"):
        if have(cand):
            return cand
    for path in (
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
        "/usr/lib/libreoffice/program/soffice",                  # Linux pkg
        "/opt/libreoffice/program/soffice",
    ):
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def clean_gfm(md: str) -> str:
    """Strip Pandoc's empty anchor spans (e.g. <span id="anchor"></span>) and
    other empty <span> wrappers it emits when converting .odt headings to GFM."""
    md = re.sub(r'<span id="[^"]*"></span>', "", md)
    md = re.sub(r"<span[^>]*></span>", "", md)
    return re.sub(r"[ \t]+\n", "\n", md)


def warn(msg: str) -> None:
    sys.stderr.write(f"warning: {msg}\n")


# --- .odt -------------------------------------------------------------------

def extract_odt(path: str) -> str:
    if have("pandoc"):
        proc = subprocess.run(["pandoc", path, "-t", "gfm"], capture_output=True, text=True)
        if proc.returncode == 0 and proc.stdout.strip():
            return clean_gfm(proc.stdout)
        warn(f"pandoc failed on .odt, trying LibreOffice: {proc.stderr.strip()}")
    binname = libreoffice_bin()
    if binname:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([binname, "--headless", "--convert-to", "txt",
                            "--outdir", tmp, path], capture_output=True, text=True)
            txt = os.path.join(tmp, os.path.splitext(os.path.basename(path))[0] + ".txt")
            if os.path.isfile(txt):
                with open(txt, encoding="utf-8", errors="replace") as fh:
                    return textify(fh.read())
    raise RuntimeError("cannot read .odt: install `pandoc` or LibreOffice.")


# --- .pdf -------------------------------------------------------------------

def extract_pdf(path: str) -> str:
    # 1) pdfplumber (best layout awareness)
    try:
        import pdfplumber  # type: ignore

        pages = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")
            if len(pdf.pages) > 1:
                warn("multi-page PDF: verify section/role order survived extraction.")
        return textify("\n".join(pages))
    except ImportError:
        pass
    except Exception as exc:  # pragma: no cover - corrupt pdf etc.
        warn(f"pdfplumber error: {exc}; trying pypdf.")

    # 2) pypdf
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(path)
        text = "\n".join((pg.extract_text() or "") for pg in reader.pages)
        warn("used pypdf (no layout model): two-column resumes may interleave.")
        return textify(text)
    except ImportError:
        pass
    except Exception as exc:  # pragma: no cover
        warn(f"pypdf error: {exc}; trying pdftotext.")

    # 3) pdftotext CLI
    if have("pdftotext"):
        proc = subprocess.run(["pdftotext", "-layout", path, "-"],
                              capture_output=True, text=True)
        if proc.returncode == 0:
            return textify(proc.stdout)

    raise RuntimeError("cannot read PDF: `pip install pdfplumber pypdf` or install poppler "
                       "(`brew install poppler`) for pdftotext.")


# --- shared text -> markdown heuristics -------------------------------------

def textify(raw: str) -> str:
    """Light heuristics: collapse whitespace, mark likely headings/bullets."""
    lines = [ln.rstrip() for ln in raw.replace("\r", "").split("\n")]
    out: list[str] = []
    blank = 0
    for ln in lines:
        stripped = ln.strip()
        if not stripped:
            blank += 1
            if blank <= 1:
                out.append("")
            continue
        blank = 0
        # bullet?
        if BULLET_RE.match(stripped):
            out.append("- " + BULLET_RE.sub("", stripped))
            continue
        # section heading? (short line matching a known section word, any case)
        key = stripped.lower().strip(": ")
        if key in SECTION_WORDS or (len(stripped) <= 40 and stripped.isupper()):
            out.append("")
            out.append(f"## {stripped.title() if stripped.isupper() else stripped}")
            out.append("")
            continue
        out.append(stripped)
    md = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract PDF/.odt resume to Markdown")
    ap.add_argument("input", help="input .pdf or .odt file")
    ap.add_argument("-o", "--output", help="output .md (default: stdout)")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        sys.stderr.write(f"error: input not found: {args.input}\n")
        return 2

    ext = os.path.splitext(args.input)[1].lower()
    try:
        if ext == ".pdf":
            md = extract_pdf(args.input)
        elif ext == ".odt":
            md = extract_odt(args.input)
        elif ext in (".md", ".markdown", ".txt"):
            with open(args.input, encoding="utf-8", errors="replace") as fh:
                md = fh.read()
        else:
            sys.stderr.write(f"error: unsupported input '{ext}'. Use .pdf or .odt\n")
            return 2
    except RuntimeError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(md)
        print(f"wrote {args.output}")
        warn("review the Markdown for extraction artifacts before editing.")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
