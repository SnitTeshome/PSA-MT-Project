"""Week 4 backend comparison for Kiswahili and Dholuo translation, run on the
cross-domain benchmarks built by build_crossdomain_benchmark.py (all 5 PSA
domains, NOT the agriculture-only data/splits/agriculture/*_test.csv split --
see that script's docstring for why the agriculture-only split alone would be
methodologically unsound here, same failure mode already documented for
Ekegusii in docs/week3_performance_summary.md).

Unlike the Ekegusii dict-prompted mechanism (a different, unrelated private
project directory), Kiswahili (swh_Latn) and Dholuo (luo_Latn) are both
natively supported by facebook/nllb-200-distilled-600M -- no dictionary/
retrieval scaffolding needed, so this script does plain sentence-level
translation for every backend and scores directly against each benchmark's
gold reference column with sacrebleu chrF.

Backends:
  - nllb     : facebook/nllb-200-distilled-600M, local CPU (both languages)
  - cloud_mt : a dedicated cloud machine-translation API (Kiswahili only --
               confirmed 2026-07-30 that its supported-language list has no
               Dholuo/`luo` entry, so this is skipped automatically for Dholuo)

Checkpointed per (lang, backend) to data/splits/crossdomain/results_<lang>_
<backend>.json, keyed by PSA_ID, resumable if interrupted.

Usage:
    python scripts/compare_backends.py --lang kiswahili --backend nllb
    python scripts/compare_backends.py --lang kiswahili --backend cloud_mt
    python scripts/compare_backends.py --lang all --backend all   # everything
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter

import pandas as pd
import sacrebleu

BENCH = {
    "kiswahili": {
        "path": "data/splits/crossdomain/kiswahili_benchmark.csv",
        "gold_col": "Kiswahili",
        "nllb_tgt": "swh_Latn",
        "cloud_mt_tgt": "sw",
        "lang_name": "Kiswahili (Swahili)",
    },
    "dholuo": {
        "path": "data/splits/crossdomain/dholuo_benchmark.csv",
        "gold_col": "Dholuo",
        "nllb_tgt": "luo_Latn",
        "cloud_mt_tgt": None,
        "lang_name": "Dholuo (Luo), a Nilotic language of western Kenya",
    },
}

RESULTS_DIR = "data/splits/crossdomain"


# --------------------------------------------------------------------------- #
# Degeneracy check -- generic, language-agnostic (works on any Latin-script
# output): repetition-loop / low-type-token-ratio / English-copy-through.
# Adapted from the pattern already proven in this project's Ekegusii work
# (a private lexicon-lookup module) but reimplemented standalone here since
# that directory lives outside this repo and is not meant to be an import
# dependency of it.
# --------------------------------------------------------------------------- #

def tokenize_words(text: str) -> list[str]:
    return re.findall(r"[^\W\d_]+", text.lower(), re.UNICODE)


def char_trigrams(text: str) -> list[str]:
    t = re.sub(r"\s+", " ", text.lower())
    return [t[i:i + 3] for i in range(len(t) - 2)]


def is_degenerate(text: str, en_source: str = None, min_ttr=0.40,
                   max_trigram_repeat_ratio=0.35, max_en_copy_ratio=0.5) -> bool:
    if not text or not text.strip():
        return True
    tokens = tokenize_words(text)
    if len(tokens) >= 4 and len(set(tokens)) / len(tokens) < min_ttr:
        return True
    trigrams = char_trigrams(text)
    if len(trigrams) >= 12:
        counts = Counter(trigrams)
        if counts.most_common(1)[0][1] / len(trigrams) > max_trigram_repeat_ratio:
            return True
    if en_source:
        en_words = set(tokenize_words(en_source))
        out_words = set(tokenize_words(text))
        if en_words and len(out_words & en_words) / len(en_words) > max_en_copy_ratio:
            return True
    return False


# --------------------------------------------------------------------------- #
# NLLB (local CPU)
# --------------------------------------------------------------------------- #

class NLLB:
    NAME = "facebook/nllb-200-distilled-600M"

    def __init__(self):
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        print(f"Loading {self.NAME} (CPU)...")
        self.tok = AutoTokenizer.from_pretrained(self.NAME)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.NAME)

    def translate(self, texts: list[str], tgt: str, src: str = "eng_Latn", batch: int = 16) -> list[str]:
        self.tok.src_lang = src
        forced_bos = self.tok.convert_tokens_to_ids(tgt)
        out = []
        for i in range(0, len(texts), batch):
            chunk = texts[i:i + batch]
            inputs = self.tok(chunk, return_tensors="pt", padding=True, truncation=True, max_length=128)
            # no_repeat_ngram_size + beam search: same repetition-loop fix already
            # applied in scripts/translate_and_qa.py's NLLB class.
            gen = self.model.generate(**inputs, forced_bos_token_id=forced_bos, max_length=128,
                                       no_repeat_ngram_size=3, num_beams=4)
            out.extend(self.tok.batch_decode(gen, skip_special_tokens=True))
            print(f"    NLLB {min(i + batch, len(texts))}/{len(texts)}")
        return out


# --------------------------------------------------------------------------- #
# Cloud machine-translation API (Kiswahili only -- confirmed no Dholuo/luo
# support). Credential env var names are that provider's own required names.
# --------------------------------------------------------------------------- #

def get_cloud_mt_config():
    key = os.environ.get("AZURE_TRANSLATOR_KEY")
    endpoint = os.environ.get("AZURE_TRANSLATOR_ENDPOINT")
    region = os.environ.get("AZURE_TRANSLATOR_REGION")
    if not key or not endpoint or not region:
        sys.exit("Set AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_ENDPOINT, AZURE_TRANSLATOR_REGION")
    return key, endpoint, region


def translate_cloud_mt(texts: list[str], src: str, tgt: str) -> list[str]:
    import requests
    key, endpoint, region = get_cloud_mt_config()
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
        print(f"    cloud_mt {min(i + 90, len(texts))}/{len(texts)}")
    return out


# --------------------------------------------------------------------------- #
# Checkpointing + scoring
# --------------------------------------------------------------------------- #

def checkpoint_path(lang: str, backend: str) -> str:
    return f"{RESULTS_DIR}/results_{lang}_{backend}.json"


def load_checkpoint(lang: str, backend: str) -> dict:
    path = checkpoint_path(lang, backend)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkpoint(lang: str, backend: str, data: dict) -> None:
    with open(checkpoint_path(lang, backend), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def score(lang: str, backend: str) -> None:
    cfg = BENCH[lang]
    df = pd.read_csv(cfg["path"], dtype=str)
    results = load_checkpoint(lang, backend)
    if not results:
        print(f"No results found for {lang}/{backend} -- run translation first.")
        return

    recalls_deg, chrfs = [], []
    n_deg = 0
    by_domain = {}
    for _, row in df.iterrows():
        psa_id = row["PSA_ID"]
        if psa_id not in results:
            continue
        translation = results[psa_id]["translation"]
        gold = row[cfg["gold_col"]]
        chrf = sacrebleu.sentence_chrf(translation, [gold]).score
        deg = is_degenerate(translation, en_source=row["English"])
        chrfs.append(chrf)
        if deg:
            n_deg += 1
        d = row["Domain"]
        by_domain.setdefault(d, []).append(chrf)

    avg_chrf = sum(chrfs) / len(chrfs) if chrfs else 0.0
    print(f"\n--- {lang} / {backend}: n={len(chrfs)}  chrF={avg_chrf:.1f}  degenerate={n_deg}/{len(chrfs)} ---")
    for d, vals in sorted(by_domain.items()):
        print(f"    {d:20s} n={len(vals):3d}  chrF={sum(vals) / len(vals):.1f}")


def run_translation(lang: str, backend: str) -> None:
    cfg = BENCH[lang]
    df = pd.read_csv(cfg["path"], dtype=str)
    results = load_checkpoint(lang, backend)
    todo = df[~df["PSA_ID"].isin(results.keys())]
    print(f"{lang}/{backend}: {len(results)} already done, {len(todo)} remaining of {len(df)}")
    if todo.empty:
        score(lang, backend)
        return

    if backend == "nllb":
        nllb = NLLB()
        texts = todo["English"].tolist()
        translations = nllb.translate(texts, tgt=cfg["nllb_tgt"])
        for psa_id, t in zip(todo["PSA_ID"], translations):
            results[psa_id] = {"translation": t, "retries_used": 0}
        save_checkpoint(lang, backend, results)

    elif backend == "cloud_mt":
        if cfg["cloud_mt_tgt"] is None:
            print(f"  This cloud MT API has no {lang} support -- skipping (confirmed via its /languages endpoint).")
            return
        texts = todo["English"].tolist()
        translations = translate_cloud_mt(texts, src="en", tgt=cfg["cloud_mt_tgt"])
        for psa_id, t in zip(todo["PSA_ID"], translations):
            results[psa_id] = {"translation": t, "retries_used": 0}
        save_checkpoint(lang, backend, results)

    else:
        raise ValueError(f"Unknown backend {backend}")

    score(lang, backend)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["kiswahili", "dholuo", "all"], required=True)
    parser.add_argument("--backend", choices=["nllb", "cloud_mt", "all", "score-only"], required=True)
    args = parser.parse_args()

    langs = list(BENCH.keys()) if args.lang == "all" else [args.lang]
    backends = ["nllb", "cloud_mt"] if args.backend == "all" else [args.backend]

    for lang in langs:
        for backend in backends:
            if backend == "score-only":
                score(lang, "nllb")
                score(lang, "cloud_mt")
                continue
            print(f"\n=== {lang} / {backend} ===")
            run_translation(lang, backend)


if __name__ == "__main__":
    main()
