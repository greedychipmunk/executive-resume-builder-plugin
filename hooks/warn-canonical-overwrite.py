#!/usr/bin/env python3
"""PreToolUse hook: warn before a Write overwrites a canonical résumé/cover-letter.

Markdown is this plugin's source of truth. A `Write` replaces a file wholesale, so
overwriting an existing canonical résumé/cover-letter `.md` can destroy the master
copy. This hook intercepts `Write`, and when the target is an existing Markdown file
that looks like résumé/cover-letter content, returns a `permissionDecision: "ask"` so
the user must confirm. `Edit` (targeted, non-destructive) is intentionally not guarded.

Reads the hook JSON on stdin; emits a PreToolUse decision on stdout. Always exits 0 —
a guard must never crash the tool pipeline; on any uncertainty it stays silent (allow).
"""
from __future__ import annotations

import json
import os
import re
import sys

# Plugin/standard docs that are Markdown but are not résumé sources — never guard these.
SKIP_BASENAMES = {
    "readme.md", "agents.md", "skill.md", "claude.md", "gemini.md",
    "contributing.md", "changelog.md", "license.md", "code_of_conduct.md",
}

NAME_RE = re.compile(r"(resume|r[ée]sum[ée]|\bcv\b|cover[-_ ]?letter)", re.I)
EMAIL_RE = re.compile(r"[\w.%+\-]+@[\w.\-]+\.\w{2,}")
SECTION_PATTERNS = [
    r"^#{1,3}\s+(professional\s+)?summary\b",
    r"^#{1,3}\s+(professional\s+|work\s+)?experience\b",
    r"^#{1,3}\s+education\b",
    r"^#{1,3}\s+(technical\s+)?skills\b",
    r"^#{1,3}\s+core\s+competencies\b",
    r"^#{1,3}\s+certifications\b",
    r"\bcover letter\b",
]


def looks_canonical(path: str) -> bool:
    """Heuristic: an existing résumé/cover-letter Markdown source worth protecting."""
    name = os.path.basename(path).lower()
    if name in SKIP_BASENAMES:
        return False
    named = bool(NAME_RE.search(name))
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(4000)
    except OSError:
        head = ""
    markers = sum(1 for pat in SECTION_PATTERNS
                  if re.search(pat, head, re.IGNORECASE | re.MULTILINE))
    has_email = bool(EMAIL_RE.search(head))
    content_hit = markers >= 2 or (markers >= 1 and has_email)
    return named or content_hit


def main() -> int:
    try:
        data = json.loads(sys.stdin.read() or "{}")
    except (ValueError, json.JSONDecodeError):
        return 0  # unparseable input — stay out of the way

    if data.get("tool_name") != "Write":
        return 0

    path = (data.get("tool_input") or {}).get("file_path") or ""
    if not path.lower().endswith((".md", ".markdown")):
        return 0
    if not os.path.isfile(path):
        return 0  # new file — not an overwrite
    if not looks_canonical(path):
        return 0

    reason = (
        f"'{os.path.basename(path)}' looks like a canonical résumé/cover-letter source "
        "and already exists — this Write will overwrite it entirely. Consider: use Edit "
        "for targeted changes, save a tailored version under a new name "
        "(e.g. resume--company-role.md) to preserve the master, or back up the original "
        "first. Confirm to overwrite."
    )
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        },
        "systemMessage": reason,
    }
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
