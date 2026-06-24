#!/usr/bin/env python3
"""Render canonical Markdown resume/cover-letter to PDF or LibreOffice (.odt).

Markdown is the source of truth; PDF and .odt are render artifacts. This script
routes through a fallback chain so a missing dependency never yields a silently
broken document:

  PDF :  pandoc + weasyprint/wkhtmltopdf (CSS template, selectable text)
         -> pandoc md->odt then headless LibreOffice odt->pdf
  ODT :  pandoc md->odt (optional --reference-doc styling)
         -> headless LibreOffice as fallback

Templates live in ``templates/<name>/`` and may contain:
  - ``style.css``     applied to the HTML->PDF engines
  - ``reference.odt`` applied as the .odt / odt->pdf style reference

Usage:
  python convert.py resume.md -o resume.pdf --template ats-plain
  python convert.py resume.md -o resume.odt --template executive-classic
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(PLUGIN_ROOT, "templates")


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr)


def resolve_template(name: str | None) -> dict[str, str | None]:
    """Return paths to a template's css / reference.odt, if present."""
    out: dict[str, str | None] = {"css": None, "reference": None}
    if not name:
        return out
    base = os.path.join(TEMPLATES_DIR, name)
    if not os.path.isdir(base):
        sys.stderr.write(f"warning: template '{name}' not found in {TEMPLATES_DIR}\n")
        return out
    css = os.path.join(base, "style.css")
    ref = os.path.join(base, "reference.odt")
    out["css"] = css if os.path.isfile(css) else None
    out["reference"] = ref if os.path.isfile(ref) else None
    return out


def libreoffice_bin() -> str | None:
    # On PATH (Linux / when symlinked)
    for cand in ("soffice", "libreoffice"):
        if have(cand):
            return cand
    # Common install locations not on PATH (notably the macOS .app bundle)
    for path in (
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
        "/usr/lib/libreoffice/program/soffice",                  # Linux pkg
        "/opt/libreoffice/program/soffice",
    ):
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def lo_convert(src: str, out_format: str, outdir: str) -> tuple[bool, str]:
    """Convert ``src`` to ``out_format`` (e.g. 'pdf', 'odt') via headless LibreOffice."""
    binname = libreoffice_bin()
    if not binname:
        return False, "LibreOffice (soffice) not found"
    rc, log = run([binname, "--headless", "--convert-to", out_format,
                   "--outdir", outdir, src])
    return rc == 0, log


def md_to_odt(src: str, dst: str, reference: str | None) -> tuple[bool, str]:
    if have("pandoc"):
        cmd = ["pandoc", src, "-o", dst, "--standalone"]
        if reference:
            cmd += [f"--reference-doc={reference}"]
        rc, log = run(cmd)
        if rc == 0:
            return True, "pandoc"
        return False, f"pandoc failed: {log}"
    return False, "pandoc not installed (required to read Markdown)"


def md_to_pdf(src: str, dst: str, css: str | None, reference: str | None) -> tuple[bool, str]:
    # 1) pandoc -> HTML -> PDF with a CSS-capable engine (best fidelity + selectable text)
    if have("pandoc"):
        for engine in ("weasyprint", "wkhtmltopdf"):
            if have(engine):
                cmd = ["pandoc", src, "-o", dst, "--standalone",
                       f"--pdf-engine={engine}"]
                if css:
                    cmd += ["--css", css]
                rc, log = run(cmd)
                if rc == 0:
                    return True, f"pandoc+{engine}"
        # 2) pandoc md->odt, then LibreOffice odt->pdf
        if libreoffice_bin():
            with tempfile.TemporaryDirectory() as tmp:
                tmp_odt = os.path.join(tmp, "intermediate.odt")
                ok, why = md_to_odt(src, tmp_odt, reference)
                if not ok:
                    return False, why
                ok, log = lo_convert(tmp_odt, "pdf", tmp)
                produced = os.path.join(tmp, "intermediate.pdf")
                if ok and os.path.isfile(produced):
                    shutil.move(produced, dst)
                    return True, "pandoc(odt)+libreoffice"
                return False, f"LibreOffice odt->pdf failed: {log}"
    return False, ("no working PDF engine found. Install one of: "
                   "`pandoc` + `weasyprint` (pip install weasyprint), or "
                   "`pandoc` + LibreOffice (brew install --cask libreoffice).")


def main() -> int:
    ap = argparse.ArgumentParser(description="Render Markdown resume to PDF or .odt")
    ap.add_argument("input", help="canonical Markdown file")
    ap.add_argument("-o", "--output", required=True, help="output .pdf or .odt path")
    ap.add_argument("--template", help="template name under templates/")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        sys.stderr.write(f"error: input not found: {args.input}\n")
        return 2

    ext = os.path.splitext(args.output)[1].lower()
    tpl = resolve_template(args.template)
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    if ext == ".odt":
        ok, info = md_to_odt(args.input, args.output, tpl["reference"])
    elif ext == ".pdf":
        ok, info = md_to_pdf(args.input, args.output, tpl["css"], tpl["reference"])
    else:
        sys.stderr.write(f"error: unsupported output extension '{ext}'. Use .pdf or .odt\n")
        return 2

    if ok:
        print(f"wrote {args.output} (via {info})")
        return 0
    sys.stderr.write(f"error: conversion failed. {info}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
