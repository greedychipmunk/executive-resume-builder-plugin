---
name: Document Conversion
description: This skill should be used when the user asks to "convert my resume to PDF", "export to Word/LibreOffice/odt", "read this PDF resume", "extract text from my resume PDF", "import my existing resume", "generate a PDF/odt", or whenever another resume skill needs to read or write a non-Markdown format. It is the single entry point for all PDF, Markdown, and LibreOffice (.odt) reading and writing.
version: 0.1.0
---

# Document Conversion

Read and generate resumes and cover letters across **PDF**, **Markdown**, and
**LibreOffice (`.odt`)**. This is the only skill that touches document formats directly;
all other skills route format I/O through it.

## Canonical-Markdown pipeline

```
PDF  ┐                       ┌→  PDF   (render from Markdown, selectable text)
.odt ├→  extract → Markdown ─┤
.md  ┘   (canonical source)  ├→  .odt
                             └→  .md   (always the editable master)
```

Markdown is the editable master. PDF and `.odt` are render artifacts. When importing,
always extract to Markdown first; when exporting, always render *from* the Markdown.

## Tools

Call these scripts (under `tools/`); do not hand-roll parsing or rendering:

- **`tools/extract.py <input.pdf|input.odt> [-o output.md]`** — reads a PDF or `.odt` and
  writes structured Markdown. Use for importing an existing resume.
- **`tools/convert.py <input.md> -o <output.pdf|output.odt> [--template <name>]`** —
  renders canonical Markdown to PDF or `.odt`, optionally applying a `templates/` style.

Run with the plugin root, e.g.:
`python "${CLAUDE_PLUGIN_ROOT}/tools/convert.py" resume.md -o resume.pdf --template ats-plain`

## Dependencies

These external tools do the heavy lifting; check availability and guide installation if
missing (do not fail silently):

- **Pandoc** — `brew install pandoc` (macOS) / `apt-get install pandoc` (Debian/Ubuntu).
- **LibreOffice** (`soffice` headless) — `brew install --cask libreoffice`. Used for robust
  `.odt`/PDF rendering and as a fallback.
- Python libs for extraction: `pdfplumber`, `pypdf`.

**Graceful degradation:** if Pandoc is unavailable, fall back to LibreOffice headless (and
vice versa). If neither is present, report exactly which dependency to install rather than
producing a broken file.

## Workflow

1. **Importing.** Run `extract.py`; review the Markdown for parsing artifacts (merged
   columns, dropped bullets, garbled order) — these often reveal ATS problems worth noting
   to the user. Clean up obvious extraction noise.
2. **Exporting.** Confirm the target format and (for PDF/odt) the desired template, then run
   `convert.py`. For ATS delivery, verify the output keeps selectable text and never
   rasterizes content to an image.
3. Report the output path and any dependency or fidelity caveats.

## Output

The requested file(s) plus the canonical Markdown, with notes on any extraction/rendering
caveats.
