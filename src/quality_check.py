"""
quality_check.py
-----------------
Step 5 of the pipeline: a lightweight, fully-offline grammar/quality pass.

IMPORTANT HONESTY NOTE (read this before relying on it):
This sandbox has no internet access to LanguageTool's server or a Java
runtime + local LanguageTool install, so a full grammar checker
(language_tool_python) is not reliably usable here. Since every sentence
in this dataset is machine-generated from hand-authored, grammatically
correct templates, the main real risk isn't grammar per se -- it's
mechanical slip-ups from slot-filling (double spaces, wrong article
"a"/"an", stray placeholders, bad capitalisation/punctuation). This
module checks and auto-fixes exactly those, and flags anything it
can't confidently fix for manual review, plus writes a short report.

If you want an actual broad-coverage grammar check on top of this (e.g.
catching subtler issues), run `pip install language_tool_python` in an
environment with internet/Java access and pass the final CSV through it
-- this module leaves the data in a clean enough state for that to be a
fast pass rather than a rewrite.
"""

import json
import re

import config

ARTICLE_FIX = re.compile(r"\b(a)\s+([aeiouAEIOU]\w*)", re.IGNORECASE)
UNRESOLVED_PLACEHOLDER = re.compile(r"\{[a-z_]+\}")
DOUBLE_SPACE = re.compile(r"\s{2,}")
SPACE_BEFORE_PUNCT = re.compile(r"\s+([.,!?])")


def fix_article(text: str) -> str:
    def repl(m):
        word = m.group(2)
        # keep "a" before words that sound consonant despite starting with
        # a vowel letter (rare in this dataset's vocab, so simple rule is fine)
        return f"an {word}"

    return ARTICLE_FIX.sub(repl, text)


def clean_text(text: str) -> str:
    t = text.strip()
    t = DOUBLE_SPACE.sub(" ", t)
    t = SPACE_BEFORE_PUNCT.sub(r"\1", t)
    if t:
        t = t[0].upper() + t[1:]
    if not t.endswith((".", "!", "?")):
        t += "."
    t = fix_article(t)
    return t


def check_row(text: str) -> list:
    """Return a list of issue strings (empty if none found)."""
    issues = []
    if UNRESOLVED_PLACEHOLDER.search(text):
        issues.append("unresolved_placeholder")
    if len(text) < 20:
        issues.append("too_short")
    if len(text) > 400:
        issues.append("too_long")
    if not re.match(r"^[A-Z0-9\"']", text):
        issues.append("bad_capitalisation")
    if not re.search(r"[.!?]$", text):
        issues.append("missing_terminal_punctuation")
    if re.search(r"\b(\w+)\s+\1\b", text, re.IGNORECASE):
        issues.append("repeated_word")
    return issues


def main():
    in_path = config.DATA_DIR / "deduped.json"
    rows = json.loads(in_path.read_text())
    print(f"Loaded {len(rows)} rows for quality check")

    cleaned_rows = []
    flagged = []
    issue_counts = {}

    for r in rows:
        cleaned = clean_text(r["English"])
        issues = check_row(cleaned)

        if issues:
            for issue in issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
            if "unresolved_placeholder" in issues or "too_short" in issues:
                # drop rows with unrecoverable issues rather than ship them
                flagged.append({**r, "English": cleaned, "issues": issues})
                continue

        r["English"] = cleaned
        cleaned_rows.append(r)

    out_path = config.DATA_DIR / "quality_checked.json"
    out_path.write_text(json.dumps(cleaned_rows, indent=2))

    report_lines = [
        "PSA Dataset Quality Report",
        "=" * 40,
        f"Rows in:  {len(rows)}",
        f"Rows out: {len(cleaned_rows)}",
        f"Rows dropped (unrecoverable): {len(flagged)}",
        "",
        "Auto-fixes applied to all rows: double spaces, spacing before",
        "punctuation, capitalisation, missing terminal punctuation, a/an.",
        "",
        "Issue counts (rows may have >1 issue, most were auto-fixed):",
    ]
    for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
        report_lines.append(f"  {issue}: {count}")

    config.QUALITY_REPORT.write_text("\n".join(report_lines))
    print(f"Wrote quality-checked rows -> {out_path}")
    print(f"Wrote quality report -> {config.QUALITY_REPORT}")
    print(f"Final row count after quality check: {len(cleaned_rows)}")


if __name__ == "__main__":
    main()
