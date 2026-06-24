---
name: Resume Analyzer
description: This skill should be used when the user asks to "analyze my resume", "score my resume", "review my resume", "is my resume ATS friendly", "check my resume for problems", "audit my resume", "what's wrong with my resume", or "how strong is my resume". It produces a scored, prioritized audit covering ATS compatibility, keyword coverage, impact density, red flags, length, and executive readiness.
version: 0.1.0
---

# Resume Analyzer

Audit an existing resume and produce a scored, prioritized report of what to fix. This
skill diagnoses; it does not rewrite (hand off to `resume-content-editor`) or restyle
(hand off to `resume-template-editor`).

## Operating principles

- **Work from canonical Markdown.** If given a PDF or `.odt`, extract it first via
  `document-conversion` so the analysis reflects the real parsed text — this also reveals
  ATS parsing problems (lost columns, missing text, garbled order).
- **Be specific and prioritized.** Every finding cites the exact bullet/section and gives a
  concrete fix. Rank by impact: blockers first, polish last.
- **Optionally tie to a target.** If the user supplies a job description, score keyword and
  competency coverage against it (or defer that to `job-tailoring`).

## What to evaluate

1. **ATS compatibility** — parseable structure, standard headings, selectable text, no
   text-in-images, contact details in the body, safe fonts/columns. See
   `references/ats-rules.md`.
2. **Impact density** — share of bullets that are quantified accomplishments vs. plain
   responsibilities. Flag weak verbs and passive voice.
3. **Keyword coverage** — presence of role-relevant skills/terms (against a job description
   when available).
4. **Red flags** — unexplained gaps, job-hopping framing, inconsistent dates/tense,
   buzzword overload, outdated skills, missing dates.
5. **Length & structure** — appropriate length for level; logical section order; summary
   present and strong.
6. **Executive readiness** (for senior candidates) — leadership scope, P&L/business impact,
   strategic framing. See `references/executive-framing.md`.

## Workflow

1. Extract to Markdown if needed.
2. Run `tools/ats_score.py` on the file for the heuristic/keyword score (pass the job
   description path when provided). Read the script if it needs environment adjustment.
3. Layer qualitative analysis on top of the script's output across the six dimensions.
4. Produce the report.

## Report format

```
RESUME AUDIT — Overall: <score>/100

ATS Compatibility        <score>/100
Impact & Quantification  <score>/100
Keyword Coverage         <score>/100
Structure & Length       <score>/100
Executive Readiness      <score>/100   (if applicable)

TOP FIXES (prioritized)
1. [blocker]  <section/bullet> — <problem> → <concrete fix>
2. ...

STRENGTHS
- ...
```

## Output

Deliver the scored report and offer to apply fixes via `resume-content-editor` /
`resume-template-editor`, or to tailor to a posting via `job-tailoring`.
