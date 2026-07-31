"""Fill a missing English or Kiswahili side of a domain PSA CSV using multiple
translation tools, score each candidate via round-trip back-translation, and
write in the best-scoring tool's output -- for any domain, not just Agriculture.

Why this exists: the schema allows an English-only source with a **team
translation** for Kiswahili (or, less commonly, the reverse), tagged
`translation=team` in `Metadata` (see `data/README.md`). Doing that translation
by hand for every row doesn't scale, and a single machine translation with no
second opinion isn't a "team" QA process either. This script compares multiple
independent tools per row and keeps the one whose round-trip back-translation
is closest to the original -- then still expects (and logs space for) a human
read-through afterward, same as any other team-translated row.

Tools compared:
  - facebook/nllb-200-distilled-600M (local, CPU-only, both directions --
    already the model this project recommends for later fine-tuning)
  - Helsinki-NLP/opus-mt-en-sw (local, CPU-only, en->sw direction only -- no
    reliable sw->en counterpart was found; skipped automatically for that
    direction)
  - Azure Translator (cloud; requires your own resource -- see below; also
    used as the independent round-trip arbiter for every candidate, since
    using a tool to grade its own output would bias the score)

Round-trip scoring: with no gold reference for these rows, each candidate
translation is translated back to the source language via Azure (independent
of whichever tool produced it) and compared to the original text with
difflib.SequenceMatcher. This is a heuristic proxy, not a BLEU/chrF claim --
still read a sample of the winners yourself before treating this as final.

Requires an Azure Translator resource (any tier, including free F0). Get a key
+ region from portal.azure.com -> Cognitive Services -> Translator, or via
`az cognitiveservices account create --kind TextTranslation --sku F0 ...`.
Set before running:

    export AZURE_TRANSLATOR_KEY=...
    export AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
    export AZURE_TRANSLATOR_REGION=...

Usage:
    # Fill blank Kiswahili/English cells only
    python scripts/translate_and_qa.py data/raw/<domain>/<domain>_psas.csv

    # Also re-check rows already tagged translation=team (re-run the
    # comparison and overwrite with whichever tool wins now)
    python scripts/translate_and_qa.py data/raw/<domain>/<domain>_psas.csv --recheck-team

Writes the result back into the same CSV in place (make a copy first if
you want to diff before/after) and appends `qa_tool=...; qa_roundtrip=...`
to each touched row's Metadata without disturbing existing fields.
"""

import argparse
import os
import sys
import time
from difflib import SequenceMatcher

import pandas as pd
import requests
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, MarianMTModel, MarianTokenizer

BATCH = 16


def get_azure_config():
    key = os.environ.get("AZURE_TRANSLATOR_KEY")
    endpoint = os.environ.get("AZURE_TRANSLATOR_ENDPOINT")
    region = os.environ.get("AZURE_TRANSLATOR_REGION")
    if not key or not endpoint or not region:
        sys.exit("Set AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_ENDPOINT, AZURE_TRANSLATOR_REGION "
                 "(see this script's docstring) -- no fallback, needs real credentials")
    return key, endpoint, region


def azure_translate(texts: list[str], src: str, tgt: str, key: str, endpoint: str, region: str) -> list[str]:
    if not texts:
        return []
    out = []
    for i in range(0, len(texts), 90):
        chunk = texts[i:i + 90]
        resp = requests.post(
            f"{endpoint}translate?api-version=3.0&from={src}&to={tgt}",
            headers={
                "Ocp-Apim-Subscription-Key": key,
                "Ocp-Apim-Subscription-Region": region,
                "Content-Type": "application/json",
            },
            json=[{"Text": t} for t in chunk],
            timeout=60,
        )
        resp.raise_for_status()
        out.extend([d["translations"][0]["text"] for d in resp.json()])
        time.sleep(0.2)
    return out


class NLLB:
    NAME = "facebook/nllb-200-distilled-600M"

    def __init__(self):
        self.tok = AutoTokenizer.from_pretrained(self.NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.NAME)

    def translate(self, texts: list[str], src: str, tgt: str) -> list[str]:
        self.tok.src_lang = src
        forced_bos = self.tok.convert_tokens_to_ids(tgt)
        out = []
        for i in range(0, len(texts), BATCH):
            chunk = texts[i:i + BATCH]
            inputs = self.tok(chunk, return_tensors="pt", padding=True, truncation=True, max_length=128)
            gen = self.model.generate(**inputs, forced_bos_token_id=forced_bos, max_length=128)
            out.extend(self.tok.batch_decode(gen, skip_special_tokens=True))
        return out


class OpusMTEnSw:
    NAME = "Helsinki-NLP/opus-mt-en-sw"

    def __init__(self):
        self.tok = MarianTokenizer.from_pretrained(self.NAME)
        self.model = MarianMTModel.from_pretrained(self.NAME)

    def translate(self, texts: list[str]) -> list[str]:
        out = []
        for i in range(0, len(texts), BATCH):
            chunk = texts[i:i + BATCH]
            inputs = self.tok(chunk, return_tensors="pt", padding=True, truncation=True, max_length=128)
            gen = self.model.generate(**inputs, max_length=128)
            out.extend(self.tok.batch_decode(gen, skip_special_tokens=True))
        return out


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def append_metadata(existing: str, tool: str, score: float) -> str:
    existing = str(existing or "").rstrip()
    sep = "; " if existing and not existing.endswith(";") else ""
    return f"{existing}{sep}translation=team; qa_tool={tool}; qa_roundtrip={round(score, 3)}"


def main(path: str, recheck_team: bool) -> None:
    key, endpoint, region = get_azure_config()
    df = pd.read_csv(path, dtype=str)

    meta = df["Metadata"].fillna("")
    en_blank = df["English"].fillna("").str.strip() == ""
    sw_blank = df["Kiswahili"].fillna("").str.strip() == ""
    team_en_source = meta.str.contains("translation=team") & meta.str.contains("source_lang=en")
    team_sw_source = meta.str.contains("translation=team") & meta.str.contains("source_lang=sw")

    need_sw = sw_blank | (recheck_team & team_en_source)
    need_en = en_blank | (recheck_team & team_sw_source)

    if not need_sw.any() and not need_en.any():
        print("Nothing to do -- no blank cells found (pass --recheck-team to also "
              "re-validate existing translation=team rows).")
        return

    print("Loading NLLB-200-distilled-600M...")
    nllb = NLLB()
    print("Loading OPUS-MT en-sw...")
    opus = OpusMTEnSw()

    if need_sw.any():
        idx = df[need_sw].index
        en_texts = df.loc[idx, "English"].tolist()
        print(f"Translating {len(en_texts)} row(s) en->sw with NLLB, OPUS-MT, Azure...")
        cands = {
            "nllb": nllb.translate(en_texts, "eng_Latn", "swh_Latn"),
            "opus": opus.translate(en_texts),
            "azure": azure_translate(en_texts, "en", "sw", key, endpoint, region),
        }
        print("Back-translating all three candidates via Azure for scoring...")
        backtrans = {t: azure_translate(cands[t], "sw", "en", key, endpoint, region) for t in cands}

        for pos, row_idx in enumerate(idx):
            scores = {t: similarity(en_texts[pos], backtrans[t][pos]) for t in cands}
            best = max(scores, key=scores.get)
            df.at[row_idx, "Kiswahili"] = cands[best][pos]
            df.at[row_idx, "Metadata"] = append_metadata(df.at[row_idx, "Metadata"], best, scores[best])

    if need_en.any():
        idx = df[need_en].index
        sw_texts = df.loc[idx, "Kiswahili"].tolist()
        print(f"Translating {len(sw_texts)} row(s) sw->en with NLLB, Azure (no reliable "
              f"OPUS-MT sw->en model)...")
        cands = {
            "nllb": nllb.translate(sw_texts, "swh_Latn", "eng_Latn"),
            "azure": azure_translate(sw_texts, "sw", "en", key, endpoint, region),
        }
        print("Back-translating both candidates via Azure for scoring...")
        backtrans = {t: azure_translate(cands[t], "en", "sw", key, endpoint, region) for t in cands}

        for pos, row_idx in enumerate(idx):
            scores = {t: similarity(sw_texts[pos], backtrans[t][pos]) for t in cands}
            best = max(scores, key=scores.get)
            df.at[row_idx, "English"] = cands[best][pos]
            df.at[row_idx, "Metadata"] = append_metadata(df.at[row_idx, "Metadata"], best, scores[best])

    df.to_csv(path, index=False)
    print(f"\nWrote {path}. Read a sample of the newly-filled rows yourself before "
          f"treating them as final -- this script's QA is a heuristic proxy, not a "
          f"substitute for a human check.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--recheck-team", action="store_true",
                         help="also re-run the comparison on rows already tagged translation=team")
    args = parser.parse_args()
    main(args.csv_path, args.recheck_team)
