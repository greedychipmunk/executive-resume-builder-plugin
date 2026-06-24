# ATS Rules Reference

Applicant Tracking Systems (ATS) parse a resume into structured fields before a
human ever sees it. A visually beautiful resume that an ATS cannot parse can be
silently rejected or garbled. This reference defines what keeps a resume
ATS-safe, and what breaks it.

## How an ATS reads a resume

1. Ingests the file (PDF/DOCX/ODT) and extracts a **linear text stream**.
2. Splits that stream into **sections** using recognizable headings.
3. Maps content into fields: contact, work history (title/company/dates), education,
   skills.
4. Indexes the text for **keyword/competency matching** against the job posting.

Anything that disrupts the linear text stream or hides text from extraction is a
hazard.

## Safe vs. unsafe

### File format
- **Safe:** PDF with selectable text, DOCX, ODT.
- **Unsafe:** scanned/image PDFs, PDFs where text is outlined to paths, exotic
  formats. Always confirm the exported PDF has *selectable* text.

### Layout
- **Safe:** single column. ATS-safe two-column is acceptable *only* if the reading
  order still linearizes sensibly; test by extracting it back to text.
- **Unsafe:** text in **headers/footers** (often dropped), text inside **text
  boxes**, **tables** for layout (cells can be read out of order), **multi-column**
  flows that interleave, content inside **images/logos/icons**, sidebars with
  critical info that linearize before or after the wrong section.

### Headings
- **Safe:** standard, literal section names — `Summary`, `Experience` (or
  `Professional Experience` / `Work Experience`), `Education`, `Skills`,
  `Certifications`, `Projects`.
- **Unsafe:** clever/renamed sections — "Where I've Made Magic", "My Journey" — the
  parser won't recognize them.

### Contact info
- Put name and contact (email, phone, city/state, LinkedIn) in the **body**, on
  separate lines or a single delimited line — never only in a header/footer.

### Dates
- Consistent, parseable format: `Jan 2020 – Mar 2024` or `2020–2024`. Put dates
  next to the role. Avoid date-only-in-a-graphic timelines.

### Fonts & glyphs
- **Safe:** common fonts (Calibri, Arial, Helvetica, Garamond, Georgia, Times).
- **Unsafe:** decorative fonts, icon fonts for data, special glyphs/emoji for
  bullets. Use a plain bullet (`-` / `•`).

### Graphics
- **Unsafe for ATS:** skill rating bars, charts, headshots, logos carrying text,
  infographics. The ATS reads none of it. Keep these for a separate human-only
  version if at all.

## Keyword strategy (honest)

- Mirror the **exact terminology** of the target posting where the candidate
  genuinely has the experience — include both the spelled-out term and the acronym
  on first use (e.g. "Search Engine Optimization (SEO)") so either match hits.
- Place keywords naturally inside real accomplishment bullets and a skills section —
  **never** keyword-stuff, use white/hidden text, or list skills the candidate
  lacks. ATS and recruiters both penalize this, and it fails in interviews.
- A dedicated, scannable **Skills** section helps both ATS indexing and the human
  6-second skim.

## Length & structure

- **Length:** ~1 page for early career; 2 pages is standard and appropriate for
  senior/executive candidates; 3 only for academic CVs or deep executive histories.
- **Order:** Contact → Summary/Headline → Experience (reverse-chronological) →
  Skills → Education → (Certifications/Projects/Awards as relevant). Senior
  candidates may place a short "Core Competencies" line near the top.
- Reverse-chronological is the most ATS-friendly format. Functional/skills-only
  formats parse poorly and signal gap-hiding to recruiters.

## Pre-flight checklist

- [ ] Exported file has selectable text (copy-paste it back out to verify).
- [ ] No critical info in headers/footers, text boxes, tables, or images.
- [ ] Standard section headings.
- [ ] Contact info in the body.
- [ ] Consistent, parseable dates next to each role.
- [ ] Common font; plain bullets; no icon fonts/emoji as data.
- [ ] Reverse-chronological; appropriate length.
- [ ] Round-trip test: run the output back through `tools/extract.py` and confirm
      the text comes out in the right order with nothing lost.
