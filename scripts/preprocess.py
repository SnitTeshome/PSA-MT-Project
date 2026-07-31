"""Week 2 preprocessing pipeline skeleton: normalization, tokenization,
code-switching flagging, and a starter cultural-term glossary.

This is a STARTING POINT, not a finished pipeline — three pieces are explicitly
partial and say so at the point of use:

  - Tokenization: whitespace/regex-based for both languages. Good enough for word
    counts and rough alignment; not linguistically correct for Kiswahili's
    agglutinative morphology. A real Swahili tokenizer (e.g. spacy's `sw` support is
    thin) is an open Week 2 decision, not resolved here.
  - Code-switching flag: a closed-class function-word heuristic (per-token, checks
    against small English/Swahili stopword sets), not a trained language-ID model.
    fastText's lid.176 would be more accurate but isn't installed yet — see the repo's
    tooling notes for why this was deferred rather than silently worked around.
  - Glossary: ~20 seed terms likely to recur across PSA domains (drought, vaccination,
    curfew, etc.). The Week 2 checklist calls for a native-speaker validation pass —
    this glossary is exactly the artifact that pass should grow and correct, not a
    finished reference.

Usage:
    python scripts/preprocess.py data/raw/agriculture/agriculture_psas.csv
"""

import sys
import unicodedata
from pathlib import Path

import pandas as pd

EN_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "to", "of", "and", "in",
    "on", "for", "with", "at", "by", "from", "this", "that", "will", "be",
}
SW_STOPWORDS = {
    "na", "ya", "wa", "za", "la", "kwa", "ni", "cha", "vya", "katika",
    "kutoka", "hii", "hiyo", "watu", "wote", "kila", "au",
}

GLOSSARY = {
    "drought": "ukame",
    "famine": "njaa",
    "flood": "mafuriko",
    "vaccination": "chanjo",
    "quarantine": "karantini",
    "curfew": "amri ya kutotoka nje",
    "subsidy": "ruzuku",
    "cooperative": "chama cha ushirika",
    "extension officer": "afisa ugani",
    "fertilizer": "mbolea",
    "pesticide": "dawa ya kuua wadudu",
    "livestock": "mifugo",
    "harvest": "mavuno",
    "planting season": "msimu wa kupanda",
    "early warning": "tahadhari ya mapema",
    "disease outbreak": "mlipuko wa ugonjwa",
    "relief food": "chakula cha msaada",
    "registration": "usajili",
    "deadline": "tarehe ya mwisho",
    "advisory": "shauri",
}


def normalize(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFC", text)
    text = " ".join(text.split())
    return text.strip()


def tokenize(text: str) -> list[str]:
    return normalize(text).split()


def flag_code_switching(kiswahili_text: str) -> bool:
    """Rough heuristic only — see module docstring. Flags a row for human review,
    does not classify it."""
    tokens = {t.lower().strip(".,!?") for t in tokenize(kiswahili_text)}
    has_en = bool(tokens & EN_STOPWORDS)
    has_sw = bool(tokens & SW_STOPWORDS)
    return has_en and has_sw


def apply_glossary_check(text: str) -> list[str]:
    """Returns glossary English terms present in an English PSA — use this to check
    the Kiswahili side used the glossary's matching term rather than a synonym."""
    lower = text.lower()
    return [term for term in GLOSSARY if term in lower]


def main(path: str) -> None:
    csv_path = Path(path)
    if not csv_path.exists():
        sys.exit(f"file not found: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)

    df["English_norm"] = df["English"].apply(normalize)
    df["Kiswahili_norm"] = df["Kiswahili"].fillna("").apply(normalize)
    df["English_tokens"] = df["English_norm"].apply(tokenize)
    df["Kiswahili_tokens"] = df["Kiswahili_norm"].apply(tokenize)
    df["possible_code_switch"] = df["Kiswahili_norm"].apply(flag_code_switching)
    df["glossary_terms"] = df["English_norm"].apply(apply_glossary_check)

    flagged = df[df["possible_code_switch"]]
    print(f"{len(df)} rows processed")
    print(f"{len(flagged)} row(s) flagged for possible code-switching "
          f"(heuristic — review manually):")
    for _, r in flagged.iterrows():
        print(f"  {r['PSA_ID']}: {r['Kiswahili_norm'][:80]}")

    with_terms = df[df["glossary_terms"].str.len() > 0]
    print(f"\n{len(with_terms)} row(s) contain a glossary term")

    out_path = csv_path.with_name(csv_path.stem + "_preprocessed.csv")
    df.drop(columns=["English_tokens", "Kiswahili_tokens"]).to_csv(out_path, index=False)
    print(f"\nWrote {out_path} (token columns dropped for CSV readability; "
          f"re-tokenize on load if needed downstream)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/preprocess.py <path-to-domain-csv>")
    main(sys.argv[1])
