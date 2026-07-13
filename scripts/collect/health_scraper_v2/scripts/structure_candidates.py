"""Turn a confirmed candidate CSV into the official schema-shaped dataset.

This fills the missing step in the pipeline: fetchers produce messy
'_candidates_<source>.csv' files, a human manually confirms which rows are
genuine English+Kiswahili pairs, and THIS script takes those confirmed rows
and writes them into the official 9-column schema so validate_psa_csv.py
can check them.

Expected input CSV: any columns, but must include at minimum an English
text column and a Kiswahili text column (you tell this script which via
--eng-col / --sw-col). A 'source' / 'url' column is picked up automatically
if present; otherwise pass --source to apply the same source to every row.

Usage:
    python structure_candidates.py \\
        --input data/raw/health/_candidates_moh.csv \\
        --output data/raw/health/health_psas.csv \\
        --domain Health \\
        --subcategory "Disease Prevention and Control" \\
        --prefix HEALTH \\
        --eng-col english_text \\
        --sw-col swahili_text \\
        --source-col source_url \\
        --date 2026-07-13

If --output already exists, new rows are appended (PSA_ID numbering
continues from the current max) rather than overwritten.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

SCHEMA = [
    "PSA_ID", "Domain", "Sub_Category", "English", "Kiswahili",
    "Target_Language", "Source", "Date", "Metadata",
]


def next_start_number(existing_df: pd.DataFrame, prefix: str) -> int:
    if existing_df is None or existing_df.empty:
        return 1
    ids = existing_df["PSA_ID"].dropna()
    ids = ids[ids.str.startswith(prefix + "_")]
    if ids.empty:
        return 1
    nums = ids.str.replace(prefix + "_", "", regex=False).astype(int)
    return int(nums.max()) + 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True, help="confirmed candidate CSV")
    p.add_argument("--output", required=True, help="schema-shaped CSV to write/append to")
    p.add_argument("--domain", required=True, help="e.g. Health")
    p.add_argument("--subcategory", required=True, help="e.g. 'Disease Prevention and Control'")
    p.add_argument("--prefix", required=True, help="PSA_ID prefix, e.g. HEALTH")
    p.add_argument("--eng-col", required=True, help="column name holding English text")
    p.add_argument("--sw-col", required=True, help="column name holding Kiswahili text")
    p.add_argument("--source-col", default=None, help="column name holding source URL, if present")
    p.add_argument("--source", default=None, help="fixed source string to use for every row (if no --source-col)")
    p.add_argument("--date", default=None, help="fixed date (YYYY-MM-DD) to use for every row")
    p.add_argument("--date-col", default=None, help="column name holding per-row date, if present")
    p.add_argument("--metadata", default="collected via scraper - review before final submission",
                    help="fixed metadata note applied to every row (Metadata is a mandatory "
                         "field in the schema validator, so this can't be blank)")
    args = p.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        sys.exit(f"input not found: {in_path}")

    raw = pd.read_csv(in_path, dtype=str)
    for col in (args.eng_col, args.sw_col):
        if col not in raw.columns:
            sys.exit(f"column '{col}' not found in {in_path}. Columns present: {list(raw.columns)}")

    out_path = Path(args.output)
    existing = pd.read_csv(out_path, dtype=str) if out_path.exists() else None
    start_n = next_start_number(existing, args.prefix)

    rows = []
    skipped = 0
    for i, r in raw.iterrows():
        eng = str(r[args.eng_col]).strip() if pd.notna(r[args.eng_col]) else ""
        sw = str(r[args.sw_col]).strip() if pd.notna(r[args.sw_col]) else ""
        if not eng or not sw:
            skipped += 1
            continue  # never invent a missing half of the pair

        source = ""
        if args.source_col and args.source_col in raw.columns and pd.notna(r[args.source_col]):
            source = str(r[args.source_col]).strip()
        elif args.source:
            source = args.source

        date = ""
        if args.date_col and args.date_col in raw.columns and pd.notna(r[args.date_col]):
            date = str(r[args.date_col]).strip()
        elif args.date:
            date = args.date

        rows.append({
            "PSA_ID": f"{args.prefix}_{start_n + len(rows):03d}",
            "Domain": args.domain,
            "Sub_Category": args.subcategory,
            "English": eng,
            "Kiswahili": sw,
            "Target_Language": "",
            "Source": source,
            "Date": date,
            "Metadata": args.metadata,
        })

    new_df = pd.DataFrame(rows, columns=SCHEMA)
    combined = pd.concat([existing, new_df], ignore_index=True) if existing is not None else new_df
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(out_path, index=False)

    print(f"Wrote {len(new_df)} new rows to {out_path} (skipped {skipped} incomplete pairs)")
    print(f"Total rows in {out_path}: {len(combined)}")
    print(f"\nNext step: python validate_psa_csv.py {out_path}")


if __name__ == "__main__":
    main()
