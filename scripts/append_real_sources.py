"""Append QA-filtered real PSA data on top of the synthetic base dataset, with
honest per-row provenance labeling.

Background: `build_final_combined_dataset.py`'s 15,000-row output is entirely
synthetic (template-generated English, LLM/MT-translated targets) -- verified
via exact-text overlap check against every real corpus in this workspace
(agriculture_psas.csv, psa_pipeline/data/clean_real_with_quality_labels.csv):
zero overlap, all three. It never incorporated the team's actual collected/
verified PSA data. This script fixes that by appending (not replacing) real
rows from two sources, after applying this project's own PSA-vs-Press-Release
QA framework independently to each -- corpus-provided labels (a filename
saying "PSA", a Domain column) are not trusted at face value, per the
standing instruction that externally-sourced data gets the same scrutiny
regardless of what it claims about itself.

Sources:
  1. data/raw/agriculture/agriculture_psas.csv (11,695 rows) -- already has
     Kiswahili/Somali/Dholuo real-translated at 100%, Ekegusii sparse (8.2%,
     Ekegusii has no automated MT fallback, unlike the other three).
  2. NLP/Data/EkegusiiCorpus/raw/_PSA_EnGuz.csv (4,818 rows, all 5 domains) --
     real English<->Ekegusii pairs, but only Ekegusii is present; Kiswahili/
     Somali/Dholuo are null here and need a follow-up translation pass.

QA policy (user-decided): keep PSA-keyword hits AND the ambiguous bucket
(flagged for review, not excluded) -- exclude only rows that read as clear
Press Releases (press/legal keyword present, no PSA keyword). Same regex as
`build_final_combined_dataset.py`, kept in sync deliberately -- do not let
these drift apart.

Dedup: exact-English-text collision, both against each other and against the
synthetic base. Where agriculture_psas.csv and the EkegusiiCorpus both cover
the same real sentence, agriculture_psas.csv wins (it already has 3 of 4
target languages filled; the corpus only has Ekegusii for that same text).

Output intentionally NOT named with a row count (the whole point of this
script is growing the dataset past 15,000) -- see OUT_PATH.

Usage:
    python scripts/append_real_sources.py
"""

import re

import pandas as pd

BASE_PATH = "data/processed/kenyan_psa_15000_final.csv"
AGRI_PATH = "data/raw/agriculture/agriculture_psas.csv"
GUZ_CORPUS_PATH = "/home/coder/workspace/NLP/Data/EkegusiiCorpus/raw/_PSA_EnGuz.csv"
OUT_PATH = "data/processed/kenyan_psa_multilingual_dataset.csv"

PSA_KEYWORD_RE = re.compile(
    r"\b(advise[sd]?|urge[sd]?|warn(s|ed)?|remind[s]?|all Kenyans are requested|"
    r"public is hereby informed|deadline|alert)\b",
    re.IGNORECASE,
)
PRESS_KEYWORD_RE = re.compile(
    r"\b(launch(ed|es)?|inaugurat(ed|es)|announc(ed|es)|statement by the Cabinet Secretary|"
    r"official visit|media invited)\b",
    re.IGNORECASE,
)
LEGAL_KEYWORD_RE = re.compile(
    r"\b(it is notified for the general information|pursuant to|"
    r"in exercise of the powers|Gazette Notice|tender No\.?)\b",
    re.IGNORECASE,
)

FINAL_COLS = [
    "PSA_ID", "Domain", "English",
    "Ekegusii", "Ekegusii_tool", "Ekegusii_review_flag",
    "Kiswahili", "Kiswahili_tool", "Kiswahili_review_flag",
    "Somali", "Somali_tool", "Somali_review_flag",
    "Dholuo", "Dholuo_tool", "Dholuo_review_flag",
    "Content_Type_Flag", "Provenance", "Source",
]


def classify_content_type(english: pd.Series) -> pd.Series:
    has_psa = english.str.contains(PSA_KEYWORD_RE, na=False)
    has_press = english.str.contains(PRESS_KEYWORD_RE, na=False) | english.str.contains(LEGAL_KEYWORD_RE, na=False)
    flag = pd.Series(None, index=english.index, dtype=object)
    flag.loc[has_press & ~has_psa] = "press_release_style"
    flag.loc[~has_psa & ~has_press] = "ambiguous_needs_review"
    return flag


def load_base():
    base = pd.read_csv(BASE_PATH, dtype=str)
    for col in ["Somali", "Somali_tool", "Somali_review_flag", "Source"]:
        base[col] = None
    base["Provenance"] = "synthetic"
    return base[FINAL_COLS]


def load_agriculture_real():
    df = pd.read_csv(AGRI_PATH, dtype=str)
    flag = classify_content_type(df["English"].fillna(""))
    keep = flag != "press_release_style"
    dropped = (~keep).sum()
    print(f"agriculture_psas.csv: {len(df)} total, dropping {dropped} press-release-style, keeping {keep.sum()}")
    df = df[keep].copy()
    df["Content_Type_Flag"] = flag[keep]

    out = pd.DataFrame(index=df.index)
    out["PSA_ID"] = df["PSA_ID"]
    out["Domain"] = df["Domain"]
    out["English"] = df["English"]
    out["Ekegusii"] = df["Ekegusii"]
    out["Ekegusii_tool"] = df["Ekegusii"].notna().map({True: "real_source", False: None})
    out["Ekegusii_review_flag"] = None
    out["Kiswahili"] = df["Kiswahili"]
    out["Kiswahili_tool"] = df["Kiswahili"].notna().map({True: "real_source", False: None})
    out["Kiswahili_review_flag"] = None
    out["Somali"] = df["Somali"]
    out["Somali_tool"] = df["Somali"].notna().map({True: "real_source", False: None})
    out["Somali_review_flag"] = None
    out["Dholuo"] = df["Dholuo"]
    out["Dholuo_tool"] = df["Dholuo"].notna().map({True: "real_source", False: None})
    out["Dholuo_review_flag"] = None
    out["Content_Type_Flag"] = df["Content_Type_Flag"]
    out["Provenance"] = "real"
    out["Source"] = df["Source"]
    return out[FINAL_COLS]


def load_ekegusii_corpus_real():
    df = pd.read_csv(GUZ_CORPUS_PATH, dtype=str)
    flag = classify_content_type(df["en"].fillna(""))
    keep = flag != "press_release_style"
    dropped = (~keep).sum()
    print(f"EkegusiiCorpus _PSA_EnGuz.csv: {len(df)} total, dropping {dropped} press-release-style, keeping {keep.sum()}")
    df = df[keep].copy()
    df["Content_Type_Flag"] = flag[keep]

    out = pd.DataFrame(index=df.index)
    out["PSA_ID"] = "GUZCORP_" + df["PSA_Id"].astype(str)
    out["Domain"] = df["Domain"]
    out["English"] = df["en"]
    out["Ekegusii"] = df["guz"]
    out["Ekegusii_tool"] = "real_source"
    out["Ekegusii_review_flag"] = None
    for lang in ["Kiswahili", "Somali", "Dholuo"]:
        out[lang] = None
        out[f"{lang}_tool"] = None
        out[f"{lang}_review_flag"] = "pending_translation"
    out["Content_Type_Flag"] = df["Content_Type_Flag"]
    out["Provenance"] = "real"
    out["Source"] = "EkegusiiCorpus (_PSA_EnGuz.csv, private outer-workspace corpus)"
    return out[FINAL_COLS]


def main():
    base = load_base()
    agri_real = load_agriculture_real()
    guz_real = load_ekegusii_corpus_real()

    print(f"\nBase (synthetic): {len(base)}")
    print(f"Agriculture real (QA-passed): {len(agri_real)}")
    print(f"EkegusiiCorpus real (QA-passed): {len(guz_real)}")

    # Dedup: agriculture_psas.csv wins over EkegusiiCorpus on exact English-text collision
    # (it has 3/4 languages already; the corpus only has Ekegusii for the same text).
    agri_text = set(agri_real["English"].str.strip())
    before = len(guz_real)
    guz_real = guz_real[~guz_real["English"].str.strip().isin(agri_text)]
    print(f"EkegusiiCorpus rows dropped as duplicates of agriculture_psas.csv: {before - len(guz_real)}")

    base_text = set(base["English"].str.strip())
    before = len(agri_real)
    agri_real = agri_real[~agri_real["English"].str.strip().isin(base_text)]
    print(f"Agriculture-real rows dropped as duplicates of the synthetic base: {before - len(agri_real)}")
    before = len(guz_real)
    guz_real = guz_real[~guz_real["English"].str.strip().isin(base_text)]
    print(f"EkegusiiCorpus rows dropped as duplicates of the synthetic base: {before - len(guz_real)}")

    combined = pd.concat([base, agri_real, guz_real], ignore_index=True)
    assert combined["PSA_ID"].duplicated().sum() == 0, "PSA_ID collision after merge -- fix before writing"

    # Domain-label normalization -- same fix the team's own clean_real.py already applied
    # to the original real corpus (see Week 1 report SS6), reintroduced here because this
    # script merges fresh from raw sources rather than the already-normalized clean_real.csv.
    combined["Domain"] = combined["Domain"].replace({"Security": "Security & Safety"})

    print(f"\nFinal combined dataset: {combined.shape}")
    print(f"\nProvenance:\n{combined['Provenance'].value_counts()}")
    print(f"\nContent_Type_Flag:\n{combined['Content_Type_Flag'].value_counts(dropna=False)}")
    print(f"\nDomain distribution:\n{combined['Domain'].value_counts()}")
    print(f"\nLanguage fill rates:")
    for lang in ["Ekegusii", "Kiswahili", "Somali", "Dholuo"]:
        filled = combined[lang].notna().sum()
        print(f"  {lang}: {filled}/{len(combined)} ({filled/len(combined)*100:.1f}%)")

    combined.to_csv(OUT_PATH, index=False)
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
