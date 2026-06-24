---
name: Cover Letter Generator
description: This skill should be used when the user asks to "write a cover letter", "generate a cover letter", "draft a cover letter for this job", "write a letter of interest", or "create a cover letter to go with my resume". It produces a tailored, compelling cover letter matched to the candidate's resume and, when provided, a specific job description and company.
version: 0.1.0
---

# Cover Letter Generator

Produce a tailored, persuasive cover letter in the candidate's voice, matched to their
resume and — when supplied — a specific job description and company. Output is written as
canonical Markdown, then optionally rendered to PDF or `.odt` via `document-conversion`.

## Operating principles

- **Never fabricate.** Draw only on real experience from the resume and what the user
  states. Mark any missing specific (a metric, a named project) with
  `[CONFIRM: ...]` rather than inventing it.
- **Complement, don't repeat.** A cover letter is not a prose restatement of the resume.
  It selects 2–3 of the most relevant accomplishments and explains their *significance*
  and *fit* for this role.
- **Match voice to level.** For executives, lead with strategic impact, leadership
  philosophy, and business outcomes; keep it confident and concise.

## Inputs to gather

1. **Resume** (canonical Markdown; extract via `document-conversion` if needed).
2. **Job description** — paste text or URL contents. Optional but strongly recommended.
3. **Company name and any specifics** the user knows (mission, recent news, hiring manager).
4. **Tone preference** (default: confident, warm, professional).

## Structure

Keep it to one page / 3–4 tight paragraphs:

1. **Opening hook** — state the role, a genuine reason for interest in *this* company, and
   a one-line value proposition. Avoid "I am writing to apply for...".
2. **Proof paragraph(s)** — 2–3 specific, quantified accomplishments mapped directly to the
   job's top requirements. Show fit, not just history.
3. **Culture/why-them** — connect the candidate's motivations and values to the company.
4. **Close** — confident call to action and thanks.

## Workflow

1. Extract the role's top requirements and keywords from the job description (when provided).
2. Select the candidate's strongest matching evidence from the resume.
3. Draft in the structure above; keep each claim verifiable.
4. Tighten: remove clichés ("team player", "hit the ground running"), passive voice, and
   anything already obvious from the resume.
5. Save as Markdown; offer to render to PDF/`.odt` and to match the resume's template via
   `resume-template-editor` for visual consistency.

## Coordination

When the user wants both a tailored resume *and* cover letter for one posting, the
`job-tailoring` skill orchestrates this skill alongside `resume-content-editor`.

## Output

A complete cover letter in Markdown, a list of any `[CONFIRM: ...]` items to verify, and an
offer to render the final document.
