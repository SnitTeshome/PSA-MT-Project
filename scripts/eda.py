"""Week 2 EDA over the collected PSA dataset(s).

Domain-agnostic by design: globs every data/raw/<domain>/*_psas.csv it can find and
concatenates them, so it already runs meaningfully on a single finished domain (today:
agriculture only) and will pick up health/security/education/governance automatically
the moment those branches merge — no changes needed here when that happens.

Covers the Week 2 milestone checklist: domain distribution, text length histograms,
vocabulary size, language-pair statistics, and progress against the team-wide
>=5,000-parallel-sentence target (Week 1 success criterion, still relevant as a Week 2
gap-check).

Usage:
    python scripts/eda.py                      # auto-discovers data/raw/*/*_psas.csv
    python scripts/eda.py path/to/one_file.csv  # single file

Outputs summary stats to stdout and saves histograms to reports/eda/ (created if absent).
"""

import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "reports" / "eda"
SENTENCE_TARGET = 5000
SPLIT_RE = re.compile(r"[.!?]+")


def discover_csvs() -> list[Path]:
    return sorted((REPO_ROOT / "data" / "raw").glob("*/*_psas.csv"))


def load(paths: list[Path]) -> pd.DataFrame:
    if not paths:
        sys.exit(
            "no PSA CSVs found under data/raw/*/*_psas.csv — "
            "run from the repo root, or pass a path explicitly"
        )
    frames = []
    for p in paths:
        df = pd.read_csv(p, dtype=str)
        df["__source_file"] = p.name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def sentence_count(text: str) -> int:
    if not isinstance(text, str) or not text.strip():
        return 0
    return len([s for s in SPLIT_RE.split(text) if s.strip()])


def vocab_size(series: pd.Series) -> int:
    tokens = set()
    for text in series.dropna():
        tokens.update(text.lower().split())
    return len(tokens)


def main(paths: list[Path]) -> None:
    df = load(paths)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loaded {len(df)} rows from {df['__source_file'].nunique()} file(s): "
          f"{sorted(df['__source_file'].unique())}\n")

    print("=== Domain distribution ===")
    print(df["Domain"].value_counts().to_string())
    if "Sub_Category" in df.columns:
        print("\n=== Sub-category distribution ===")
        print(df["Sub_Category"].value_counts().to_string())

    print("\n=== Parallel sentence count vs Week 1 target ===")
    en_sents = df["English"].apply(sentence_count).sum()
    sw_sents = df["Kiswahili"].fillna("").apply(sentence_count).sum()
    print(f"English sentences (approx, punctuation-split): {en_sents}")
    print(f"Kiswahili sentences (approx, punctuation-split): {sw_sents}")
    print(f"Target: >={SENTENCE_TARGET} parallel sentences team-wide "
          f"({'MET' if min(en_sents, sw_sents) >= SENTENCE_TARGET else 'NOT MET'})")

    print("\n=== Vocabulary size (whitespace-split, lowercased) ===")
    print(f"English vocab: {vocab_size(df['English'])}")
    print(f"Kiswahili vocab: {vocab_size(df['Kiswahili'])}")

    print("\n=== Length stats (words) ===")
    for col in ["English", "Kiswahili"]:
        words = df[col].fillna("").str.split().str.len()
        words = words[words > 0]
        print(f"{col}: min {words.min()}, median {int(words.median())}, "
              f"mean {words.mean():.1f}, max {words.max()}")
        fig, ax = plt.subplots()
        ax.hist(words, bins=20)
        ax.set_title(f"{col} length distribution (words)")
        ax.set_xlabel("words")
        ax.set_ylabel("rows")
        fig.savefig(OUT_DIR / f"length_hist_{col.lower()}.png", dpi=120)
        plt.close(fig)

    print("\n=== Language-pair / translation-source statistics ===")
    if "Metadata" in df.columns:
        team_translated = df["Metadata"].fillna("").str.contains("translation=team")
        print(f"Team-translated rows: {team_translated.sum()} / {len(df)} "
              f"({100 * team_translated.mean():.1f}%)")
        print(f"Genuine source-pair rows: {(~team_translated).sum()} / {len(df)}")
    if "Target_Language" in df.columns:
        filled = df["Target_Language"].fillna("").str.strip() != ""
        print(f"Rows with Target_Language already filled: {filled.sum()} / {len(df)} "
              f"(expected ~0 pre-Week-3 — these are still placeholders per the schema)")

    fig, ax = plt.subplots()
    df["Domain"].value_counts().plot(kind="bar", ax=ax)
    ax.set_title("Domain distribution")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "domain_distribution.png", dpi=120)
    plt.close(fig)

    print(f"\nHistograms saved to {OUT_DIR}/")


if __name__ == "__main__":
    args = [Path(p) for p in sys.argv[1:]]
    main(args if args else discover_csvs())
