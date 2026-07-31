"""One-off vendor-name scrub for shared-repo disclosure compliance
(OPERATING_CONVENTIONS.md rule #5). Applies phrase-level-first, then
word-level regex replacements across the flagged files. Run once, review
the diff, then delete this script (it's not meant to be a reusable pipeline
step, just a cleanup pass).

Usage:
    python scripts/scrub_vendor_names.py
"""

import re

FILES = [
    "docs/ekegusii_transfer_learning.md",
    "docs/week3_performance_summary.md",
    "docs/week4_swahili_dholuo_summary.md",
    "data/README.md",
    "data/raw/agriculture/EKEGUSII_CORPUS_IMPORT.md",
    "data/raw/agriculture/README.md",
    "data/raw/agriculture/SOURCES.md",
    "data/raw/agriculture/WEEK1_REPORT.md",
    "data/raw/agriculture/farmradio_manual/README.md",
    "scripts/qa_azure_language_check.py",
    "scripts/translate_and_qa.py",
]

# Longest/most-specific patterns first so they consume the vendor name before
# a shorter, generic pattern would otherwise leave a dangling fragment.
REPLACEMENTS = [
    (r"\bAWS Bedrock\b", "a hosted foundation-model API"),
    (r"\bBedrock's\b", "that API's"),
    (r"\bBedrock\b", "a hosted foundation-model API"),
    (r"\bAzure Translator\b", "a cloud translation API"),
    (r"\bAzure OpenAI\b", "a cloud LLM API"),
    (r"\bAzure's\b", "that service's"),
    (r"\bAzure\b", "a cloud translation API"),
    (r"\bCohere's\b", "that API's"),
    (r"\bCohere\b", "a general-purpose LLM API"),
    (r"\bModal\.com\b", "a remote GPU platform"),
    (r"\bModal's\b", "that platform's"),
    (r"\bModal\b", "a remote GPU platform"),
    (r"\bLightning AI\b", "a remote GPU platform"),
    (r"\bLightning's\b", "that platform's"),
    (r"\bKaggle's\b", "that notebook service's"),
    (r"\bKaggle GPU\b", "a cloud GPU notebook"),
    (r"\bKaggle\b", "a cloud GPU notebook service"),
    (r"\bAWS\b", "a cloud compute platform"),
]


def scrub(text: str) -> str:
    for pattern, repl in REPLACEMENTS:
        text = re.sub(pattern, repl, text)
    return text


def main():
    for path in FILES:
        with open(path) as f:
            original = f.read()
        cleaned = scrub(original)
        if cleaned != original:
            with open(path, "w") as f:
                f.write(cleaned)
            print(f"Scrubbed: {path}")
        else:
            print(f"No change needed: {path}")


if __name__ == "__main__":
    main()
