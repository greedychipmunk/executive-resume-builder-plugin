# Templates

Each template is a **styling layer** applied at render time by `tools/convert.py`.
It changes presentation only — never the résumé content, which lives in canonical
Markdown. This is what keeps the `resume-content-editor` and `resume-template-editor`
skills decoupled.

## Available templates

| Template | Use for | ATS-safe |
|----------|---------|----------|
| `ats-plain` | Default. Pure ATS uploads. Single column, no color. | ✅ Yes |
| `executive-classic` | Senior/executive, refined serif, human + ATS. | ✅ Yes |
| `modern-twocolumn` | Human-facing delivery (email/print), accent color. | ⚠️ Risk — test first |

## Files in a template

- **`style.css`** — applied to the Pandoc HTML→PDF path (WeasyPrint/wkhtmltopdf).
  This ships now and drives PDF rendering.
- **`reference.odt`** — *(optional, not committed)* the LibreOffice style reference
  used for `.odt` output and the ODT→PDF fallback path.

## Generating a `reference.odt`

`reference.odt` is a binary and must be generated with Pandoc (so it isn't checked
in). Create one, restyle it in LibreOffice, and drop it in the template folder:

```bash
# 1) produce a starter reference doc
pandoc -o templates/<name>/reference.odt --print-default-data-file=reference.odt 2>/dev/null \
  || pandoc /dev/null -o templates/<name>/reference.odt

# 2) open it in LibreOffice Writer, edit the paragraph/heading STYLES
#    (Heading 1 = name, Heading 2 = sections, etc.), save as .odt

# 3) convert.py will auto-apply it when you pass --template <name>
```

If no `reference.odt` exists, `.odt` output still works with Pandoc defaults.

## Rendering

```bash
python tools/convert.py resume.md -o resume.pdf --template ats-plain
python tools/convert.py resume.md -o resume.odt --template executive-classic
```

Always run the ATS round-trip test (`references/ats-rules.md`) before submitting a
two-column layout.
