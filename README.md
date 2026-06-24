# Executive Resume Builder

A Claude Code **plugin** that packages sophisticated, modern résumé-writing technique
into a set of composable skills. It creates and improves résumés, optionally produces a
tailored résumé **and** cover letter for a specific job description, and reads/writes
**PDF**, **Markdown**, and **LibreOffice (`.odt`)**.

Built for senior and executive candidates (leadership narrative, quantified business
impact, ATS compatibility), but useful at any level.

## What it does

- ✍️ Rewrite and strengthen résumé **content** (impact, quantification, narrative).
- 🎨 Edit and create résumé **templates/layouts** — independently from content.
- 💌 Generate tailored **cover letters**.
- 🔎 **Analyze** a résumé with a scored ATS / impact / keyword audit.
- 🎯 **Tailor** a résumé and cover letter to a specific job description.
- 🔁 **Convert** between PDF, Markdown, and LibreOffice formats.

## Design in one line

**Markdown is the canonical source of truth; PDF and `.odt` are render artifacts —
and résumé *content* is kept strictly separate from *layout*.**

## Skills

| Skill | Triggers on (examples) |
|-------|------------------------|
| `resume-content-editor` | "improve my résumé", "rewrite this bullet", "quantify my accomplishments" |
| `resume-template-editor` | "change my résumé layout", "make a two-column résumé", "adjust the formatting" |
| `cover-letter-generator` | "write a cover letter", "draft a cover letter for this job" |
| `resume-analyzer` | "analyze my résumé", "is my résumé ATS friendly", "score my résumé" |
| `job-tailoring` | "tailor my résumé to this job", "customize my résumé for this posting" |
| `document-conversion` | "convert my résumé to PDF", "export to LibreOffice", "read this PDF résumé" |

Skills activate automatically based on the request; they also call one another
(e.g. `job-tailoring` orchestrates `resume-content-editor` + `cover-letter-generator`,
and every format read/write routes through `document-conversion`).

## Repository layout

```
executive-resume-builder/
├── AGENTS.md                 # Instructions for AI agents (authoritative)
├── README.md                 # This file
├── requirements.txt
├── .claude-plugin/plugin.json
├── commands/resume-expert.md # /resume-expert guided entry point
├── hooks/                    # PreToolUse guard for canonical .md sources
├── skills/                   # The six skills (auto-discovered)
├── tools/                    # convert.py · extract.py · ats_score.py
├── references/               # action-verbs · quantification · ats-rules · executive-framing
└── templates/                # ats-plain · executive-classic · modern-twocolumn
```

## Slash command

Run **`/resume-expert`** as a guided entry point — it routes your request to the right
skill. Pass what you need as an argument, or run it bare for a menu:

```
/resume-expert improve my resume and tailor it to this job posting
/resume-expert            # shows the menu of options
```

## Safety: canonical-source guard

A `PreToolUse` hook (`hooks/warn-canonical-overwrite.py`) watches for `Write`
operations that would **overwrite an existing canonical résumé/cover-letter `.md`**.
When it detects one, it asks for confirmation first — nudging toward `Edit` for
targeted changes or saving a tailored copy under a new name, so the master is never
clobbered by accident. It stays silent for new files, non-Markdown files, plugin docs
(README/AGENTS), and `Edit` operations. (Hook changes require restarting Claude Code.)

## Setup

```bash
# Python libs (extraction + optional HTML->PDF). ats_score.py needs none of these.
pip install -r requirements.txt

# System tools for document conversion (install at least one rendering path):
brew install pandoc                 # required to read/write Markdown<->odt
brew install --cask libreoffice     # robust .odt/PDF rendering & fallback
# (Linux: apt-get install pandoc libreoffice poppler-utils)
```

The tools degrade gracefully and tell you exactly what to install if a dependency is
missing — nothing is silently broken.

## Using the tools directly

```bash
# Import an existing résumé to canonical Markdown
python tools/extract.py old-resume.pdf -o resume.md

# Audit it (optionally against a job description)
python tools/ats_score.py resume.md --job job.txt

# Render to PDF or .odt with a template
python tools/convert.py resume.md -o resume.pdf --template ats-plain
python tools/convert.py resume.md -o resume.odt --template executive-classic
```

Start a new résumé from `templates/resume-skeleton.md`.

## Principles & guardrails

- **Truthful by design.** The plugin optimizes the presentation of *real* experience;
  it never fabricates employers, titles, dates, metrics, or credentials. Unknown numbers
  become `[QUANTIFY: …]` placeholders for you to fill.
- **ATS-first** output (selectable text, standard structure), with richer human-only
  variants available.
- This plugin offers writing/presentation guidance — not legal or immigration advice.

## License

MIT
