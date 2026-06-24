---
name: Resume Content Editor
description: This skill should be used when the user asks to "improve my resume", "rewrite this bullet", "strengthen my resume", "make my experience sound more impactful", "edit my resume content", "quantify my accomplishments", "fix weak wording", or "write my professional summary". It rewrites and restructures resume content (bullets, summaries, experience ordering, impact, narrative) while leaving visual formatting untouched.
version: 0.1.0
---

# Resume Content Editor

Rewrite and strengthen the *content* of a resume — wording, structure, impact, and
narrative. This skill never changes visual styling or layout; that is the job of
`resume-template-editor`. Content edits operate on the **canonical Markdown** source.

## Operating principles

- **Edit the canonical `.md`.** If the resume only exists as PDF or `.odt`, first invoke
  the `document-conversion` skill to extract it to Markdown, then edit that.
- **Never fabricate.** Do not invent employers, titles, dates, metrics, degrees, or
  certifications. When a strong bullet needs a number the user has not supplied, insert a
  placeholder like `[QUANTIFY: e.g., 30% / $2M / 12 reports]` and ask for the real figure.
- **Preserve formatting.** Do not introduce or alter template/layout markup. Touch only
  the words and their order.

## Workflow

1. **Establish context.** Confirm target role/level, industry, and audience (ATS vs. human
   reviewer). For executive candidates, bias toward leadership scope, P&L/business impact,
   and board-level framing.
2. **Diagnose.** Read each section and flag: weak verbs, responsibility-only bullets (no
   outcome), missing metrics, passive voice, jargon, redundancy, and chronology issues.
3. **Rewrite bullets with the impact formula.** Convert duties into accomplishments using
   **Action verb → What you did → Quantified result/context** (CAR/STAR). Lead with the
   strongest, most quantified bullets in each role.
4. **Sharpen the top.** Craft or tighten the headline and professional summary (3–5 lines)
   so it states the candidate's value proposition and seniority up front.
5. **Order for impact.** Use reverse-chronological experience by default; within each role,
   order bullets by impact, not time.
6. **Align language** to the target role's vocabulary without keyword-stuffing (see
   `job-tailoring` when a specific posting is supplied).
7. **Trim.** Enforce sensible length (typically 1 page early-career, 2 pages senior/exec).
   Remove filler, dated skills, and obvious statements.

## Reference material

Consult these as needed (do not inline their full contents):

- `references/action-verbs.md` — strong, categorized action verbs and weak verbs to avoid.
- `references/quantification-guide.md` — how to find and frame metrics; before/after examples.
- `references/executive-framing.md` — leadership narrative, scope language, C-suite framing.

## Output

Write changes back to the canonical Markdown file. Summarize what changed and why, and list
any `[QUANTIFY: ...]` placeholders the user still needs to fill in. To deliver PDF or `.odt`,
hand off to `document-conversion`.
