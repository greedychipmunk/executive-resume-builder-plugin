# AGENTS.md — Executive Resume Builder

Instructions for any AI agent (Claude Code, Codex, etc.) working in this repository.
This file is authoritative: it outranks default agent behavior and is read before any task.

---

## 1. What this project is

**Executive Resume Builder** is a Claude Code **plugin** that packages the most
sophisticated, modern résumé-writing techniques into a set of composable skills.

Its job is to help a user:

1. Create a new résumé from scratch, or improve an existing one.
2. Edit résumé **content** (wording, structure, impact) independently from résumé
   **template/layout** (typography, spacing, sections, visual design).
3. Generate a **tailored résumé and cover letter** for a specific job description —
   this is optional and only happens when a job description is supplied.
4. **Read and generate** résumés in three document formats: **PDF**, **Markdown**,
   and **LibreOffice** (`.odt`).

The plugin targets, but is not limited to, **senior / executive** candidates, so the
techniques bias toward leadership narrative, quantified business impact, board- and
C-suite-level framing, and ATS (Applicant Tracking System) compatibility.

---

## 2. Core design principles

These principles govern every skill and tool. When in doubt, follow them.

- **Markdown is the canonical source of truth.** Every résumé is authored and stored
  as structured Markdown. PDF and `.odt` are *rendered outputs* derived from it. Never
  treat a PDF as the editable master — extract it to Markdown first, edit, then re-render.
- **Content and layout are strictly separated.** `resume-content-editor` never touches
  visual styling; `resume-template-editor` never rewrites a candidate's accomplishments.
  This lets either change independently without breaking the other.
- **Conversions go through shared tools, not per-skill code.** All format reading and
  writing routes through the scripts in `tools/` (Pandoc + headless LibreOffice). Skills
  call these tools; they do not re-implement parsing or rendering.
- **Evidence over assertion.** Résumé bullets must be quantified and verifiable. Skills
  should push the user for metrics ("increased X by Y% over Z") rather than vague claims,
  and must never fabricate numbers, employers, dates, or credentials.
- **Truthfulness is non-negotiable.** The plugin optimizes presentation of *real*
  experience. It does not invent experience. If the user asks to fabricate, decline and
  offer to reframe genuine experience instead.
- **ATS-first, human-second-pass.** Default output must parse cleanly through ATS
  software (simple structure, standard section headings, no text-in-images, selectable
  text). A separate, visually richer template may be offered for human-only delivery.

---

## 3. Repository layout

```
executive-resume-builder/
├── AGENTS.md                  # This file (also the agent entry point)
├── README.md                  # Human-facing overview & install instructions
├── .claude-plugin/
│   └── plugin.json            # Plugin manifest (name, version, metadata)
├── commands/
│   └── resume-expert.md       # /resume-expert guided entry point
├── hooks/
│   ├── hooks.json             # PreToolUse registration
│   └── warn-canonical-overwrite.py  # Warn before overwriting a canonical .md
├── skills/                    # One directory per skill (auto-discovered)
│   ├── resume-content-editor/
│   │   └── SKILL.md
│   ├── resume-template-editor/
│   │   └── SKILL.md
│   ├── cover-letter-generator/
│   │   └── SKILL.md
│   ├── resume-analyzer/
│   │   └── SKILL.md
│   ├── job-tailoring/
│   │   └── SKILL.md
│   └── document-conversion/
│       └── SKILL.md
├── tools/                     # Shared, skill-agnostic scripts
│   ├── convert.py             # Format conversion (md ⇄ pdf ⇄ odt) via Pandoc/LibreOffice
│   ├── extract.py             # Read PDF/odt → structured Markdown
│   └── ats_score.py           # Heuristic ATS/keyword scoring
├── templates/                 # Reusable résumé & cover-letter templates
│   ├── executive-classic/
│   ├── modern-twocolumn/
│   └── ats-plain/
├── references/                # Deep knowledge skills load on demand
│   ├── action-verbs.md
│   ├── ats-rules.md
│   ├── executive-framing.md
│   └── quantification-guide.md
└── assets/                    # Fonts, CSS, reference docs for rendering
```

> Paths inside skills and tools must use `${CLAUDE_PLUGIN_ROOT}` so they resolve
> regardless of where the plugin is installed. Never hard-code absolute paths.

---

## 4. Skills

Each skill is a directory under `skills/` containing a `SKILL.md` with YAML frontmatter
(`name`, `description`) followed by instructions. Descriptions must be written so the
model reliably triggers the skill — state *when* to use it, with concrete cues.

### Required skills (per project spec)

| Skill | Purpose |
|-------|---------|
| `resume-content-editor` | Rewrite, restructure, and strengthen résumé **content** — bullets, summaries, experience ordering, impact/quantification, narrative. Format-agnostic; operates on canonical Markdown. |
| `resume-template-editor` | Edit and create **visual templates/layouts** — sections, typography, spacing, columns, color, headers. Touches presentation only, never content claims. |
| `cover-letter-generator` | Produce a tailored, compelling cover letter matched to a résumé and (optionally) a job description, in the executive voice. |

### Additional skills (included to make the plugin complete)

| Skill | Purpose |
|-------|---------|
| `resume-analyzer` | Audit an existing résumé: ATS compatibility, keyword coverage, impact density, red flags (gaps, jargon, weak verbs), length, executive readiness. Produces a scored report with prioritized fixes. |
| `job-tailoring` | Given a job description, tailor the résumé **and** cover letter: extract role keywords/competencies, map to the candidate's real experience, reorder/reweight, and flag genuine gaps. Orchestrates the content + cover-letter skills. |
| `document-conversion` | Read and generate PDF, Markdown, and LibreOffice formats by calling `tools/`. The single entry point for any format I/O. |

When adding a new skill, follow the `skill-development` / `plugin-dev:skill-structure`
conventions, keep `SKILL.md` lean, and push lengthy domain knowledge into `references/`
loaded on demand (progressive disclosure).

---

## 5. Document formats & toolchain

All format work is centralized in `tools/`. Skills shell out to these; they do not parse
or render documents themselves.

**Pipeline (canonical Markdown at the center):**

```
PDF  ┐                       ┌→  PDF   (Pandoc → HTML/LaTeX, or LibreOffice headless)
.odt ├→  extract → Markdown ─┤
.md  ┘   (canonical source)  ├→  .odt  (Pandoc, or LibreOffice headless)
                             └→  .md   (canonical, always written)
```

- **Read PDF → Markdown:** `pdftotext`/`pdfplumber` (text + layout) → cleanup to structured MD.
- **Read .odt → Markdown:** Pandoc (`pandoc input.odt -t gfm`).
- **Markdown → PDF:** Pandoc with a CSS/LaTeX template, or render HTML → PDF. ATS output
  must keep selectable text — never rasterize to an image.
- **Markdown → .odt:** Pandoc (`pandoc input.md -o output.odt --reference-doc=...`).

**External dependencies** (document, install on setup — neither is currently present):

- **Pandoc** — universal document converter. `brew install pandoc`
- **LibreOffice** (`soffice` headless) — robust `.odt`/PDF rendering & fallback.
  `brew install --cask libreoffice`
- Python libs for extraction/scoring (see `requirements.txt` once created):
  `pdfplumber`, `pypdf`, `python-frontmatter`.

Tools must **degrade gracefully**: if Pandoc is missing, fall back to LibreOffice headless
(or vice versa) and tell the user which dependency to install rather than failing silently.

---

## 6. Conventions for agents

- **Confirm the format and target audience** (ATS vs. human, executive level, target role)
  before generating, unless the user already specified them.
- **Never fabricate** employers, titles, dates, metrics, degrees, or certifications.
  Ask the user for real numbers; if unavailable, mark with a clear placeholder like
  `[QUANTIFY: e.g., 30% / $2M / 15 reports]`.
- **Always write/update the canonical `.md`** when editing, even if the user wants a PDF —
  the Markdown is the source, the PDF is a build artifact.
- **Keep skills decoupled.** A content edit must not change the template; a template edit
  must not change content. `job-tailoring` orchestrates other skills rather than
  duplicating their logic.
- **Use `${CLAUDE_PLUGIN_ROOT}`** for every internal path.
- **Prefer the dedicated tools** in `tools/` over ad-hoc shell pipelines for conversions.

---

## 7. Plugin development workflow

1. Edit/add a skill under `skills/<name>/SKILL.md`. Validate frontmatter (`name`,
   `description`) and that the trigger description is specific.
2. Put shared logic in `tools/`; put long-form domain knowledge in `references/`.
3. Update `.claude-plugin/plugin.json` if metadata/version changes.
4. Test conversions round-trip (md → pdf → extract → md) and confirm ATS-plain output
   keeps selectable text.
5. Keep `README.md` (human docs) and this `AGENTS.md` (agent docs) in sync with reality.

---

## 8. Out of scope / guardrails

- No fabrication of credentials or experience.
- No mass-generating applications or automating job-board spam.
- No scraping behind logins. Job descriptions are supplied by the user as text/URL.
- This plugin advises on presentation and writing; it is not legal or immigration advice.
