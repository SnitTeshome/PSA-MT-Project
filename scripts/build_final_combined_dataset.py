"""Build the final combined 15,000-row dataset: PSA_ID, Domain, English,
Ekegusii(+tool/flag), Kiswahili(+tool/flag), Dholuo(+tool/flag),
Content_Type_Flag. Merges the three per-language production files (Ekegusii
already resolved a prior session; Kiswahili via a cloud MT API + NLLB-200
fallback; Dholuo via NLLB-200 on a remote GPU platform -- both this session, see docs/
week4_swahili_dholuo_summary.md for the full backend comparison and the
teammate-work-override rationale for Kiswahili) into one file, verifying every
join rather than assuming the three files agree.

`Content_Type_Flag` is a dataset-level content-type signal, independent of and
NOT a substitute for the per-language `*_review_flag` columns (those are
translation QA, this is "does this row's English even read as a PSA at all").
Applies the user-shared PSA-vs-Press-Release-vs-Other-Government-Communication
framework's Step 1/2 keyword heuristic (`NLP/Project/PSA FRAMEWORK.pdf`, one
level up from this repo, private outer workspace) against the `English`
column: rows matching a press-release keyword with NO PSA keyword are flagged
`press_release_style` (reads as an event/launch announcement, e.g. "X launches
a Y campaign," not an instruction/warning to the public) rather than excluded
-- the translation work already done for them stays, the framework-mismatch
is made visible instead. This is an independent, larger-scale signal on the
same relevance-filtering gap the team's own Week 1 report already flagged as
incomplete (624 LLM-flagged rows, only 54 manually reviewed).

Usage:
    python scripts/build_final_combined_dataset.py
"""

import re

import pandas as pd

KISWAHILI_PATH = "psa_pipeline/output/kenyan_psa_kiswahili_cloud_mt_15000_translated.csv"
DHOLUO_PATH = "psa_pipeline/output/kenyan_psa_dholuo_nllb_15000_translated.csv"
OUT_PATH = "data/processed/kenyan_psa_15000_final.csv"

SHARED_COLS = ["PSA_ID", "Domain", "English", "Ekegusii", "Ekegusii_tool", "Ekegusii_review_flag"]

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


def main():
    kisw = pd.read_csv(KISWAHILI_PATH, dtype=str)
    dhol = pd.read_csv(DHOLUO_PATH, dtype=str)

    assert len(kisw) == 15000 and len(dhol) == 15000
    assert set(kisw["PSA_ID"]) == set(dhol["PSA_ID"])
    assert kisw["PSA_ID"].duplicated().sum() == 0
    assert dhol["PSA_ID"].duplicated().sum() == 0

    # Verify the two files agree on every shared column before trusting either
    # as the base -- don't silently assume.
    check = kisw[SHARED_COLS].merge(dhol[SHARED_COLS], on="PSA_ID", suffixes=("_k", "_d"))
    for col in ["Domain", "English", "Ekegusii", "Ekegusii_tool"]:
        mismatches = (check[f"{col}_k"].fillna("") != check[f"{col}_d"].fillna("")).sum()
        assert mismatches == 0, f"{col} disagrees between the Kiswahili and Dholuo production files ({mismatches} rows)"

    merged = kisw.merge(
        dhol[["PSA_ID", "Dholuo", "Dholuo_tool", "Dholuo_review_flag"]],
        on="PSA_ID", how="left", validate="one_to_one",
    )
    assert merged["Dholuo"].isna().sum() == 0

    has_psa = merged["English"].str.contains(PSA_KEYWORD_RE, na=False)
    has_press = merged["English"].str.contains(PRESS_KEYWORD_RE, na=False)
    press_only = has_press & ~has_psa
    merged["Content_Type_Flag"] = None
    merged.loc[press_only, "Content_Type_Flag"] = "press_release_style"

    cols = [
        "PSA_ID", "Domain", "English",
        "Ekegusii", "Ekegusii_tool", "Ekegusii_review_flag",
        "Kiswahili", "Kiswahili_tool", "Kiswahili_review_flag",
        "Dholuo", "Dholuo_tool", "Dholuo_review_flag",
        "Content_Type_Flag",
    ]
    merged = merged[cols]

    print(f"Final combined dataset: {merged.shape}")
    print(f"Columns: {merged.columns.tolist()}")
    print(f"\nNull counts:\n{merged.isna().sum()}")
    print(f"\nEkegusii_tool:\n{merged['Ekegusii_tool'].value_counts()}")
    print(f"\nKiswahili_tool:\n{merged['Kiswahili_tool'].value_counts()}")
    print(f"\nDholuo_tool:\n{merged['Dholuo_tool'].value_counts()}")
    print(f"\nEkegusii_review_flag:\n{merged['Ekegusii_review_flag'].value_counts(dropna=False)}")
    print(f"\nKiswahili_review_flag:\n{merged['Kiswahili_review_flag'].value_counts(dropna=False)}")
    print(f"\nDholuo_review_flag:\n{merged['Dholuo_review_flag'].value_counts(dropna=False)}")
    print(f"\nContent_Type_Flag:\n{merged['Content_Type_Flag'].value_counts(dropna=False)}")
    print(f"\nContent_Type_Flag=press_release_style by Domain:\n"
          f"{merged.loc[press_only, 'Domain'].value_counts()}")

    merged.to_csv(OUT_PATH, index=False)
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
