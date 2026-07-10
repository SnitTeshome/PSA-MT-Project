"""Validate a domain PSA CSV against the shared schema.

Usage:
    python scripts/validate_psa_csv.py data/raw/agriculture/agriculture_psas.csv

Checks (hard failures exit 1 with a descriptive message):
  - exact header match with the shared schema
  - every mandatory field filled (Target_Language is the only optional one)
  - PSA_ID format <PREFIX>_### and uniqueness
  - no exact-duplicate English or Kiswahili texts
  - no EXAMPLE_* template rows left in
  - English/Kiswahili not identical (would mean a copy-paste, not a translation)

Soft warnings (printed, do not fail):
  - langdetect disagreement on the English/Kiswahili columns (noisy on short
    directive sentences, so advisory only)
  - rows longer than 80 words (schema wants short PSAs, not articles)

Ends with summary stats: rows, sub-category distribution, length stats.
"""

import re
import sys
from pathlib import Path

import pandas as pd

SCHEMA = [
    "PSA_ID", "Domain", "Sub_Category", "English", "Kiswahili",
    "Target_Language", "Source", "Date", "Metadata",
]
MANDATORY = [c for c in SCHEMA if c != "Target_Language"]
ID_PATTERN = re.compile(r"^[A-Z]+_\d{3,}$")
MAX_WORDS = 80

try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    HAVE_LANGDETECT = True
except ImportError:
    HAVE_LANGDETECT = False


def fail(msg: str) -> None:
    sys.exit(f"VALIDATION FAILED: {msg}")


def main(path: str) -> None:
    csv_path = Path(path)
    if not csv_path.exists():
        fail(f"file not found: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)

    if list(df.columns) != SCHEMA:
        fail(
            f"header mismatch in {csv_path}\n"
            f"  expected: {SCHEMA}\n"
            f"  found:    {list(df.columns)}"
        )
    if df.empty:
        fail(f"{csv_path} has a header but no data rows")

    example_rows = df[df["PSA_ID"].str.startswith("EXAMPLE", na=False)]
    if not example_rows.empty:
        fail(f"template example rows still present: {example_rows['PSA_ID'].tolist()} — delete them")

    for col in MANDATORY:
        blank = df[df[col].isna() | (df[col].str.strip() == "")]
        if not blank.empty:
            fail(f"column '{col}' is empty in rows (PSA_ID): "
                 f"{blank['PSA_ID'].fillna('<no id>').tolist()[:10]}")

    bad_ids = df[~df["PSA_ID"].str.match(ID_PATTERN, na=False)]
    if not bad_ids.empty:
        fail(f"PSA_ID not matching <PREFIX>_###: {bad_ids['PSA_ID'].tolist()[:10]}")

    dup_ids = df[df["PSA_ID"].duplicated(keep=False)]
    if not dup_ids.empty:
        fail(f"duplicate PSA_IDs: {sorted(dup_ids['PSA_ID'].unique())}")

    for col in ["English", "Kiswahili"]:
        dups = df[df[col].str.strip().str.lower().duplicated(keep=False)]
        if not dups.empty:
            fail(f"duplicate {col} texts in rows: {dups['PSA_ID'].tolist()}")

    identical = df[df["English"].str.strip() == df["Kiswahili"].str.strip()]
    if not identical.empty:
        fail(f"English and Kiswahili identical (not a translation) in rows: "
             f"{identical['PSA_ID'].tolist()}")

    warnings = 0
    for col in ["English", "Kiswahili"]:
        long_rows = df[df[col].str.split().str.len() > MAX_WORDS]
        for _, r in long_rows.iterrows():
            print(f"WARNING {r['PSA_ID']}: {col} is {len(r[col].split())} words "
                  f"(> {MAX_WORDS}) — PSAs should be short, is this an article?")
            warnings += 1

    if HAVE_LANGDETECT:
        expect = {"English": "en", "Kiswahili": "sw"}
        for col, code in expect.items():
            for _, r in df.iterrows():
                try:
                    got = detect(r[col])
                except Exception:
                    got = "?"
                if got != code:
                    print(f"WARNING {r['PSA_ID']}: langdetect says {col} looks like "
                          f"'{got}', expected '{code}' — double-check the text")
                    warnings += 1
    else:
        print("NOTE: langdetect not installed — language sanity check skipped "
              "(pip install langdetect)")

    print(f"\nOK: {csv_path} — {len(df)} rows, all hard checks passed, {warnings} warning(s)")
    print("\nSub-category distribution:")
    print(df["Sub_Category"].value_counts().to_string())
    words = df["English"].str.split().str.len()
    print(f"\nEnglish length (words): min {words.min()}, median {int(words.median())}, "
          f"max {words.max()}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/validate_psa_csv.py <path-to-domain-csv>")
    main(sys.argv[1])
