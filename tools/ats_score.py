#!/usr/bin/env python3
"""Heuristic ATS / impact / keyword scorer for a Markdown resume.

Pure standard library so it runs before any pip install. Produces a deterministic
score across four dimensions (plus optional keyword coverage against a job
description) and prints either a readable report or JSON.

Usage:
  python ats_score.py resume.md
  python ats_score.py resume.md --job job.txt
  python ats_score.py resume.md --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().\-]{7,}\d)")
NUMBER_RE = re.compile(r"(\$?\d[\d,.]*\s?%?|\b\d+\s*(?:x|X|\+)?)")
BULLET_RE = re.compile(r"^\s*[-*•]\s+(.*)$")

STRONG_VERBS = {
    "led", "directed", "drove", "launched", "built", "scaled", "grew", "delivered",
    "spearheaded", "transformed", "founded", "negotiated", "secured", "reduced",
    "increased", "generated", "saved", "accelerated", "owned", "established",
    "orchestrated", "pioneered", "overhauled", "restructured", "championed",
    "architected", "designed", "shipped", "executed", "expanded", "optimized",
    "streamlined", "mentored", "managed", "created", "developed", "implemented",
}
WEAK_OPENERS = {
    "responsible", "worked", "helped", "assisted", "involved", "participated",
    "duties", "tasked", "handled", "various", "supported",
}
STANDARD_SECTIONS = {
    "experience", "education", "skills", "summary", "profile", "certifications",
    "projects", "leadership",
}
EXEC_TERMS = {
    "p&l", "p & l", "revenue", "ebitda", "board", "strategy", "strategic", "vision",
    "stakeholder", "transformation", "growth", "operating", "budget", "headcount",
    "scaled", "org", "leadership", "executive", "c-suite", "gtm", "roadmap",
}
STOPWORDS = {
    "the", "and", "for", "with", "you", "your", "our", "are", "will", "have", "has",
    "this", "that", "from", "all", "who", "what", "they", "their", "them", "a", "an",
    "to", "of", "in", "on", "as", "is", "be", "or", "we", "at", "by", "it", "we're",
    "able", "role", "job", "work", "team", "company", "position", "candidate",
    "experience", "years", "ability", "including", "etc", "must", "should", "plus",
}


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def clamp(v: float) -> int:
    return max(0, min(100, round(v)))


def get_bullets(text: str) -> list[str]:
    return [m.group(1).strip() for ln in text.splitlines() if (m := BULLET_RE.match(ln))]


def get_sections(text: str) -> set[str]:
    found = set()
    for ln in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.*)$", ln.strip())
        head = (m.group(1) if m else ln).strip().lower()
        for s in STANDARD_SECTIONS:
            if s in head:
                found.add(s)
    return found


def score_ats(text: str) -> tuple[int, list[str]]:
    notes: list[str] = []
    score = 100.0
    if not EMAIL_RE.search(text):
        score -= 20; notes.append("No email address detected in body text.")
    if not PHONE_RE.search(text):
        score -= 10; notes.append("No phone number detected.")
    sections = get_sections(text)
    missing = {"experience", "education", "skills"} - sections
    if missing:
        score -= 8 * len(missing)
        notes.append(f"Missing/non-standard section heading(s): {', '.join(sorted(missing))}.")
    # tables and images are ATS hazards in Markdown source
    if re.search(r"^\s*\|.*\|", text, re.M):
        score -= 15; notes.append("Table syntax found — many ATS parsers mangle tables.")
    if re.search(r"!\[[^\]]*\]\(", text):
        score -= 15; notes.append("Image found — ATS cannot read text inside images.")
    words = len(re.findall(r"\w+", text))
    if words < 250:
        score -= 10; notes.append(f"Very short ({words} words) — likely under-detailed.")
    if words > 1300:
        score -= 8; notes.append(f"Long ({words} words) — consider tightening.")
    return clamp(score), notes


def score_impact(text: str) -> tuple[int, list[str]]:
    bullets = get_bullets(text)
    notes: list[str] = []
    if not bullets:
        return 0, ["No bullet points found — accomplishments should be bulleted."]
    quantified = strong = weak = 0
    for b in bullets:
        first = b.split()[0].lower().strip(":,.") if b.split() else ""
        if NUMBER_RE.search(b):
            quantified += 1
        if first in STRONG_VERBS:
            strong += 1
        if first in WEAK_OPENERS:
            weak += 1
    n = len(bullets)
    q_ratio, s_ratio = quantified / n, strong / n
    score = 100.0 * (0.55 * q_ratio + 0.45 * s_ratio) - (weak / n) * 25
    notes.append(f"{quantified}/{n} bullets quantified ({q_ratio:.0%}); "
                 f"{strong}/{n} start with a strong action verb.")
    if weak:
        notes.append(f"{weak} bullet(s) open with weak language (e.g. 'responsible for').")
    return clamp(score), notes


def tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z][a-zA-Z+#.&\-]{2,}", text.lower())
            if w not in STOPWORDS]


def score_keywords(resume: str, job: str | None) -> tuple[int | None, list[str]]:
    if not job:
        return None, ["No job description supplied — keyword coverage skipped."]
    job_freq = Counter(tokens(job))
    top = [w for w, _ in job_freq.most_common(25)]
    resume_set = set(tokens(resume))
    hits = [w for w in top if w in resume_set]
    missing = [w for w in top if w not in resume_set]
    score = clamp(100.0 * len(hits) / max(1, len(top)))
    notes = [f"Matched {len(hits)}/{len(top)} top job keywords."]
    if missing:
        notes.append("Missing keywords worth addressing (only if genuinely true): "
                     + ", ".join(missing[:12]) + ".")
    return score, notes


def score_executive(text: str) -> tuple[int, list[str]]:
    low = text.lower()
    present = sum(1 for t in EXEC_TERMS if t in low)
    score = clamp(100.0 * present / 8)  # ~8 distinct exec signals = full marks
    return score, [f"{present} executive/leadership signal term(s) present."]


def main() -> int:
    ap = argparse.ArgumentParser(description="Heuristic ATS/impact resume scorer")
    ap.add_argument("resume", help="resume Markdown file")
    ap.add_argument("--job", help="optional job description (.txt/.md) for keyword coverage")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a report")
    args = ap.parse_args()

    if not os.path.isfile(args.resume):
        sys.stderr.write(f"error: resume not found: {args.resume}\n")
        return 2
    text = read(args.resume)
    job = read(args.job) if args.job and os.path.isfile(args.job) else None

    ats, ats_n = score_ats(text)
    impact, imp_n = score_impact(text)
    kw, kw_n = score_keywords(text, job)
    exe, exe_n = score_executive(text)

    parts = [ats, impact, exe] + ([kw] if kw is not None else [])
    overall = clamp(sum(parts) / len(parts))

    result = {
        "overall": overall,
        "dimensions": {
            "ats_compatibility": {"score": ats, "notes": ats_n},
            "impact_quantification": {"score": impact, "notes": imp_n},
            "keyword_coverage": {"score": kw, "notes": kw_n},
            "executive_readiness": {"score": exe, "notes": exe_n},
        },
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    def block(title: str, score, notes: list[str]) -> None:
        s = "n/a" if score is None else f"{score}/100"
        print(f"\n{title:<26} {s}")
        for note in notes:
            print(f"  - {note}")

    print(f"RESUME AUDIT — Overall: {overall}/100")
    block("ATS Compatibility", ats, ats_n)
    block("Impact & Quantification", impact, imp_n)
    block("Keyword Coverage", kw, kw_n)
    block("Executive Readiness", exe, exe_n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
