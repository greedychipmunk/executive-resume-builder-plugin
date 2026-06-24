---
name: Resume Template Editor
description: This skill should be used when the user asks to "edit my resume template", "change my resume layout", "create a resume template", "adjust the formatting/typography/spacing", "make a two-column resume", "redesign my resume", "change fonts or section order", or "make my resume look more executive". It edits and creates visual templates and layout only — it never rewrites the candidate's accomplishments or claims.
version: 0.1.0
---

# Resume Template Editor

Create and edit the *visual presentation* of a resume — section structure, typography,
spacing, columns, headers, and color. This skill changes layout only. It never rewrites
content claims; that is the job of `resume-content-editor`.

## Operating principles

- **Layout, not content.** Apply styling and structure without altering the words,
  metrics, employers, or ordering of accomplishments.
- **ATS-first by default.** Default output must parse cleanly through Applicant Tracking
  Systems: single-column or ATS-safe two-column, standard section headings, selectable
  text, no critical content inside images, no text in headers/footers, common fonts.
  Offer a visually richer "human-only" variant separately when appropriate.
- **Content stays canonical Markdown.** Templates render the canonical `.md` into PDF or
  `.odt`. Editing a template means editing the styling layer (CSS / reference doc / Pandoc
  template), not the Markdown content.

## Starter templates

Templates live in `templates/`. Each is a styling layer applied at render time:

- `templates/ats-plain/` — maximally ATS-safe, single column, plain typography. Default.
- `templates/executive-classic/` — refined serif, generous spacing, leadership-oriented.
- `templates/modern-twocolumn/` — ATS-safe two-column with a skills/contact sidebar.

## Workflow

1. **Confirm intent.** Determine the delivery target (ATS upload vs. emailed/printed for a
   human), seniority, and any brand constraints (color, font preferences).
2. **Pick or create a base template** from `templates/`.
3. **Edit the styling layer**, not the content:
   - For PDF output: adjust the template's CSS (or LaTeX) — margins, font family/size,
     line height, section dividers, accent color, header block.
   - For `.odt` output: adjust the Pandoc `--reference-doc` styling.
4. **Render** by invoking the `document-conversion` skill / `tools/convert.py`. Never
   rasterize text to an image in an ATS template.
5. **Validate ATS-safety**: confirm the rendered PDF has selectable text and that section
   headings and contact details sit in the document body, not in headers/footers.

## Reference material

- `references/ats-rules.md` — ATS parsing rules, safe vs. unsafe layout patterns, font
  and structure guidance. Consult before finalizing any template.

## Output

Save the modified template under `templates/`, render a preview via `document-conversion`,
and report what styling changed. Confirm whether the result is ATS-safe or human-only.
