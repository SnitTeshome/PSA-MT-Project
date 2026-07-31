"""Build a cross-domain backend-comparison benchmark for Kiswahili and Dholuo,
sampled from `psa_pipeline/data/clean_real_with_quality_labels.csv` (7,156-row
real corpus, all 5 PSA domains), stratified proportionally across every domain.

Why this exists: `data/splits/agriculture/{kiswahili,dholuo}_test.csv` (142 rows)
is Agriculture-domain ONLY. This project already documented, for Ekegusii, that a
mechanism validated only on Agriculture (chrF 45-55) can drop sharply on other
domains (chrF 26-31) on manual retest -- see docs/week3_performance_summary.md.
To avoid repeating that mistake for Kiswahili/Dholuo, the Week 4 backend
comparison must be decided on a benchmark that actually spans all 5 domains, not
just Agriculture.

Sampling rule, per language:
  1. Keep rows where that language's column is non-blank.
  2. Drop rows tagged `quality_status=NOT_INCLUDED_IN_VALIDATION_PASS` in
     Metadata (that status exists specifically to mark rows the team's own QA
     pass decided NOT to treat as validated -- keeping them in a benchmark used
     to pick a translation backend would be inconsistent with that call).
  3. Stratify proportionally to each domain's SHARE OF THAT LANGUAGE's own
     available (post-filter) rows -- not the overall corpus domain mix, and not
     the other language's mix (Kiswahili and Dholuo have very different fill
     rates per domain: Dholuo is thin in Health/Agriculture, ~4% each, vs.
     Kiswahili's ~12/29%).
  4. Largest-remainder rounding so the per-domain counts sum exactly to
     TOTAL_N, with a floor of 1 sampled row for any domain that has data at all.

Caveat carried forward from the task brief, not re-derived here: the Kiswahili
gold in this corpus is majority genuinely team-collected bilingual pairs (see
week_1_report.md); the Dholuo gold has NO qa-tool Metadata tag at all (unlike
the agriculture-splits file's `qa_tool_dholuo=nllb_selfcheck` tag) -- provenance
is undocumented, not merely self-graded, so treat it as "current best guess"
too, same as the agriculture-only Dholuo split, just for a different reason.

Usage:
    python scripts/build_crossdomain_benchmark.py
"""

import re

import pandas as pd

SOURCE = "psa_pipeline/data/clean_real_with_quality_labels.csv"
TOTAL_N = 160
SEED = 42
EXCLUDED_STATUS = "NOT_INCLUDED_IN_VALIDATION_PASS"

LANG_COLUMNS = {"kiswahili": "Kiswahili", "dholuo": "Dholuo"}


def parse_quality_status(metadata: str) -> str:
    m = re.search(r"quality_status=([A-Z_]+)", str(metadata or ""))
    return m.group(1) if m else "UNTAGGED"


def largest_remainder_allocation(domain_counts: pd.Series, total_n: int) -> dict:
    """Proportional allocation of total_n across domains by domain_counts'
    share, using the largest-remainder method so the allocation sums exactly
    to total_n instead of drifting from naive rounding. Every domain with at
    least 1 available row gets at least 1 slot."""
    share = domain_counts / domain_counts.sum()
    raw = share * total_n
    floor_alloc = raw.apply(lambda x: max(1, int(x)))
    floor_alloc = floor_alloc.clip(upper=domain_counts)
    remainder = total_n - floor_alloc.sum()
    remainders = (raw - floor_alloc).sort_values(ascending=False)
    for domain in remainders.index:
        if remainder <= 0:
            break
        if floor_alloc[domain] < domain_counts[domain]:
            floor_alloc[domain] += 1
            remainder -= 1
    return floor_alloc.to_dict()


def build_benchmark(df: pd.DataFrame, lang_col: str, total_n: int, seed: int) -> pd.DataFrame:
    filled = df[lang_col].fillna("").str.strip() != ""
    qstatus_all = df["Metadata"].apply(parse_quality_status)
    mask = filled & (qstatus_all != EXCLUDED_STATUS)
    eligible = df[mask].copy()
    eligible["quality_status"] = qstatus_all[mask]

    domain_counts = eligible["Domain"].value_counts()
    alloc = largest_remainder_allocation(domain_counts, total_n)

    print(f"  Eligible rows (filled, not NOT_INCLUDED_IN_VALIDATION_PASS): {len(eligible)}")
    print(f"  Domain shares of eligible pool: {domain_counts.to_dict()}")
    print(f"  Sampled allocation (target {total_n}): {alloc}")

    parts = []
    for domain, n in alloc.items():
        pool = eligible[eligible["Domain"] == domain]
        parts.append(pool.sample(n=n, random_state=seed))
    sample = pd.concat(parts).sample(frac=1, random_state=seed).reset_index(drop=True)
    return sample[["PSA_ID", "Domain", "English", lang_col, "Source", "Date", "Metadata", "quality_status"]]


def main():
    df = pd.read_csv(SOURCE, dtype=str)
    print(f"Loaded {SOURCE}: {len(df)} rows\n")

    for lang, col in LANG_COLUMNS.items():
        print(f"=== {lang} ({col}) ===")
        sample = build_benchmark(df, col, TOTAL_N, SEED)
        out_path = f"data/splits/crossdomain/{lang}_benchmark.csv"
        sample.to_csv(out_path, index=False)
        print(f"  Wrote {out_path}: {len(sample)} rows")
        print(f"  Final domain counts:\n{sample['Domain'].value_counts().to_string()}")
        print(f"  quality_status mix:\n{sample['quality_status'].value_counts().to_string()}\n")


if __name__ == "__main__":
    main()
