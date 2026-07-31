"""Full production Kiswahili translation of all 15,000 rows in the working file
-- a dedicated cloud machine-translation API as primary, with automatic
fallback to NLLB-200-distilled-600M for whatever it can't finish. Supersedes
the earlier plan of merging in the teammate's existing `English_sw` column
(`psa_pipeline/output/kenyan_psa_ekegusii_kiswahili_15000_merged.csv`, now
superseded).

Why the switch away from the teammate's file (see docs/week4_swahili_dholuo_
summary.md for the full backend comparison): a manual QA read found a
systematic "Office of the Auditor-General" -> "Ofisi ya Mhariri Mkuu"
(literally "Office of the Editor-in-Chief") mistranslation in 181 of 200
relevant rows. Rather than patch a single found error on top of a file whose
overall QA process is undocumented, this project's Week 4 backend comparison
already had a clear, independently-verified answer: the cloud MT API scored
chrF 80.7 on a 160-row, 5-domain cross-domain benchmark -- the best of every
backend tested (NLLB 67.7, general-purpose LLM backends 33.7-39.8). This is a
quality decision, not a comment on the original contribution -- see the doc
for the fair, full writeup.

Why the cloud-MT/NLLB SPLIT (not pure cloud MT): the cloud MT resource used is
an entry-tier subscription with a hard 2,000,000-character-per-MONTH cap
(permanent, not a per-request throttle) -- verified independently, not
assumed. This job alone needs ~1.85M input characters, ~93% of the entire
monthly cap, and some of that cap may already be consumed by this session's
own earlier comparison-stage testing (the 160-row benchmark, `scripts/
qa_azure_language_check.py`, etc.). Rather than precompute a budget and stop
early, this script reacts to the REAL API response: it keeps calling the
cloud MT API until it itself signals it can't continue (a 429 that doesn't
clear after patient backoff, or any non-200/429 error e.g. 403 quota-
exceeded), at which point it stops calling that API entirely and routes every
remaining untranslated row to NLLB-200 instead -- this project's established
best free/open alternative for Kiswahili (chrF 67.7 vs. 33-40 for the
general-purpose LLM backends tested). `Kiswahili_tool` is set per-row
(`cloud_mt_api` or `nllb_200`) so this is never blended silently.

NLLB inference runs on a remote GPU platform (the same deployed app used for
the Dholuo bulk job -- see NLP/Project/psa_mt_week4_internal/, private,
outside this repo) via `run_nllb_fallback()`, which this script calls
directly.

Checkpointed per-chunk (`Kiswahili` + `Kiswahili_tool` together) to a local
JSON file, resumable if interrupted (same discipline as scripts/
translate_and_qa.py and the prior Ekegusii bulk job).

Usage:
    export AZURE_TRANSLATOR_KEY=...
    export AZURE_TRANSLATOR_ENDPOINT=...
    export AZURE_TRANSLATOR_REGION=...
    python scripts/translate_kiswahili_cloud_mt_bulk.py
"""

import json
import os
import re
import subprocess
import sys
import time
from collections import Counter

import pandas as pd
import requests

SOURCE = "psa_pipeline/output/kenyan_psa_ekegusii_15000_translated.csv"
CHECKPOINT = "psa_pipeline/output/.kiswahili_cloud_mt_checkpoint.json"
OUT = "psa_pipeline/output/kenyan_psa_kiswahili_cloud_mt_15000_translated.csv"
CLOUD_MT_CHUNK = 50
CLOUD_MT_INTER_CHUNK_SLEEP = 1.0

# The NLLB-fallback path shells out to the private psa_mt_week4_internal
# scripts (submit_nllb.py/poll_nllb.py against an already-deployed remote-GPU
# app) rather than importing that platform's client library directly --
# keeps this file free of any specific-compute-vendor reference.
NLLB_FALLBACK_DIR = "/home/coder/workspace/NLP/Project/psa_mt_week4_internal"
NLLB_CHUNK = 2000


def get_cloud_mt_config():
    key = os.environ.get("AZURE_TRANSLATOR_KEY")
    endpoint = os.environ.get("AZURE_TRANSLATOR_ENDPOINT")
    region = os.environ.get("AZURE_TRANSLATOR_REGION")
    if not key or not endpoint or not region:
        sys.exit("Set AZURE_TRANSLATOR_KEY, AZURE_TRANSLATOR_ENDPOINT, AZURE_TRANSLATOR_REGION -- no fallback")
    return key, endpoint, region


def cloud_mt_translate_or_none(texts, src, tgt, key, endpoint, region, retries=5, base_wait=8):
    """Returns the translation list on success, or None if the cloud MT API
    signals it can't continue (persistent 429 after patient backoff, or any
    other non-200 status e.g. 403 quota-exceeded) -- None is the fallback
    trigger, not a fatal error."""
    if not texts:
        return []
    for attempt in range(retries):
        resp = requests.post(
            f"{endpoint}translate?api-version=3.0&from={src}&to={tgt}",
            headers={
                "Ocp-Apim-Subscription-Key": key,
                "Ocp-Apim-Subscription-Region": region,
                "Content-Type": "application/json",
            },
            json=[{"Text": t} for t in texts],
            timeout=60,
        )
        if resp.status_code == 200:
            return [d["translations"][0]["text"] for d in resp.json()]
        if resp.status_code == 429:
            wait = base_wait * (attempt + 1)
            print(f"    429 (attempt {attempt + 1}/{retries}): {resp.text[:200]!r} -- waiting {wait}s...")
            time.sleep(wait)
            continue
        print(f"    Cloud MT API non-200 status {resp.status_code}: {resp.text[:300]!r}")
        return None
    print(f"    Cloud MT API still returning 429 after {retries} patient retries -- treating as exhausted.")
    return None


def run_nllb_fallback(rows, tgt="swh_Latn"):
    """rows: list of {"psa_id","english"}. Submits to the deployed remote-GPU
    NLLB app in chunks, polls each to completion, returns {psa_id: translation}."""
    results = {}
    for i in range(0, len(rows), NLLB_CHUNK):
        chunk = rows[i:i + NLLB_CHUNK]
        chunk_path = f"/tmp/nllb_fallback_chunk_{i}.json"
        call_path = f"/tmp/nllb_fallback_call_{i}.txt"
        out_path = f"/tmp/nllb_fallback_out_{i}.json"
        with open(chunk_path, "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False)

        subprocess.run(
            ["python3", "submit_nllb.py", chunk_path, call_path, tgt],
            cwd=NLLB_FALLBACK_DIR, check=True,
        )
        print(f"    NLLB fallback chunk {i}-{i + len(chunk)}: submitted, polling...")
        while True:
            proc = subprocess.run(
                ["python3", "poll_nllb.py", call_path, out_path, "30"],
                cwd=NLLB_FALLBACK_DIR, check=True, capture_output=True, text=True,
            )
            if "DONE" in proc.stdout:
                break
            time.sleep(10)

        with open(out_path, encoding="utf-8") as f:
            chunk_results = json.load(f)
        for r in chunk_results:
            results[r["psa_id"]] = r["translation"]
        print(f"    NLLB fallback chunk {i}-{i + len(chunk)}: done ({len(chunk_results)} rows)")
    return results


# --- generic degeneracy check, same as scripts/compare_backends.py ---

def tokenize_words(text):
    return re.findall(r"[^\W\d_]+", text.lower(), re.UNICODE)


def char_trigrams(text):
    t = re.sub(r"\s+", " ", text.lower())
    return [t[i:i + 3] for i in range(len(t) - 2)]


def is_degenerate(text, en_source=None, min_ttr=0.40, max_trigram_repeat_ratio=0.35, max_en_copy_ratio=0.5):
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


def load_checkpoint():
    if os.path.exists(CHECKPOINT):
        with open(CHECKPOINT, encoding="utf-8") as f:
            data = json.load(f)
        # migrate the old checkpoint format (plain str) written before the
        # cloud-MT/NLLB split existed -- those rows are known-cloud-MT.
        migrated = {}
        for pid, v in data.items():
            if isinstance(v, str):
                migrated[pid] = {"translation": v, "tool": "cloud_mt_api"}
            else:
                migrated[pid] = v
        return migrated
    return {}


def save_checkpoint(checkpoint):
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def main():
    key, endpoint, region = get_cloud_mt_config()
    df = pd.read_csv(SOURCE, dtype=str)

    checkpoint = load_checkpoint()
    todo = df[~df["PSA_ID"].isin(checkpoint.keys())]
    print(f"{len(checkpoint)} already done, {len(todo)} remaining of {len(df)}")

    ids = todo["PSA_ID"].tolist()
    texts = todo["English"].tolist()

    cloud_mt_exhausted = False
    i = 0
    while i < len(texts) and not cloud_mt_exhausted:
        chunk_ids = ids[i:i + CLOUD_MT_CHUNK]
        chunk_texts = texts[i:i + CLOUD_MT_CHUNK]
        translations = cloud_mt_translate_or_none(chunk_texts, "en", "sw", key, endpoint, region)
        if translations is None:
            cloud_mt_exhausted = True
            print(f"  Cloud MT API exhausted at row {i}/{len(texts)} of this run -- switching to NLLB-200 for the rest.")
            break
        for pid, t in zip(chunk_ids, translations):
            checkpoint[pid] = {"translation": t, "tool": "cloud_mt_api"}
        save_checkpoint(checkpoint)
        print(f"  Cloud MT API: {min(i + CLOUD_MT_CHUNK, len(texts))}/{len(texts)} done, checkpointed")
        i += CLOUD_MT_CHUNK
        time.sleep(CLOUD_MT_INTER_CHUNK_SLEEP)

    remaining = df[~df["PSA_ID"].isin(checkpoint.keys())]
    if len(remaining):
        print(f"\n{len(remaining)} rows remaining -- routing to NLLB-200 (remote GPU) fallback.")
        rows = [{"psa_id": r.PSA_ID, "english": r.English} for r in remaining.itertuples()]
        nllb_results = run_nllb_fallback(rows, tgt="swh_Latn")
        for pid, t in nllb_results.items():
            checkpoint[pid] = {"translation": t, "tool": "nllb_200"}
        save_checkpoint(checkpoint)

    df["Kiswahili"] = df["PSA_ID"].map(lambda pid: checkpoint[pid]["translation"] if pid in checkpoint else None)
    df["Kiswahili_tool"] = df["PSA_ID"].map(lambda pid: checkpoint[pid]["tool"] if pid in checkpoint else None)
    n_missing = df["Kiswahili"].isna().sum()
    if n_missing:
        sys.exit(f"{n_missing} rows still missing a Kiswahili translation after the run -- not writing output")

    tool_counts = df["Kiswahili_tool"].value_counts()
    print(f"\nKiswahili_tool split:\n{tool_counts}")

    degenerate = df.apply(lambda r: is_degenerate(r["Kiswahili"], en_source=r["English"]), axis=1)
    df["Kiswahili_review_flag"] = None
    df.loc[degenerate, "Kiswahili_review_flag"] = "degenerate"
    print(f"Degenerate flagged: {degenerate.sum()}/{len(df)}")

    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}: {len(df)} rows")


if __name__ == "__main__":
    main()
