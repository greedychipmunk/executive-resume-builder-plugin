---
name: Job Tailoring
description: This skill should be used when the user supplies a job description and asks to "tailor my resume to this job", "customize my resume for this posting", "match my resume to this job description", "tailor my resume and cover letter", "optimize my resume for this role", or "apply for this job". It orchestrates resume and cover-letter customization against a specific posting — extracting requirements, mapping them to real experience, reweighting content, and flagging genuine gaps.
version: 0.1.0
---

# Job Tailoring

Tailor a resume — and optionally a cover letter — to one specific job description. This
skill is an **orchestrator**: it analyzes the posting, then drives `resume-content-editor`
and `cover-letter-generator` rather than duplicating their logic.

## Operating principles

- **Never fabricate to match.** Tailoring reweights and reframes *real* experience. If the
  candidate lacks a required qualification, flag it as a genuine gap — do not invent it.
- **Keep a master, produce a variant.** Preserve the canonical master resume; write the
  tailored version to a clearly named copy (e.g. `resume--<company>-<role>.md`).
- **Honest keyword alignment.** Mirror the posting's real vocabulary where the candidate
  genuinely has the experience. Never keyword-stuff or list skills the user doesn't have.

## Inputs

1. **Job description** — pasted text or URL contents (the user supplies it; do not scrape
   behind logins).
2. **Master resume** — canonical Markdown (extract via `document-conversion` if needed).
3. Whether a **cover letter** is also wanted.

## Workflow

1. **Parse the posting.** Extract: job title, must-have qualifications, nice-to-haves, core
   responsibilities, and the key skills/keywords (including exact phrasings and acronyms).
2. **Map to the candidate.** For each top requirement, find the strongest matching evidence
   in the master resume. Build a coverage table: requirement → matching evidence → strong /
   weak / missing.
3. **Reweight and reorder.** Via `resume-content-editor`: surface the most relevant roles
   and bullets, foreground matching accomplishments, and align wording to the posting's
   real terminology. Keep the canonical content separate from layout.
4. **Report gaps.** List must-haves with weak or missing coverage so the user can decide
   how to address them honestly.
5. **Cover letter (if requested).** Hand the parsed requirements and matched evidence to
   `cover-letter-generator` so the letter reinforces the same top 2–3 fit points.
6. **Render.** Offer to produce PDF/`.odt` for both documents via `document-conversion`,
   styled consistently via `resume-template-editor`.

## Output

- A tailored resume variant (saved as a named copy, master untouched).
- An optional matching cover letter.
- A requirement-coverage table and an honest list of gaps.
