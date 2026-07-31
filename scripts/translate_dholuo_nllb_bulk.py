"""Full production Dholuo translation of all 15,000 rows in the working file
via NLLB-200-distilled-600M -- the model that won the Week 4 backend
comparison (chrF 53.7 on the 160-row cross-domain benchmark, vs. 16-23 for
general-purpose LLM backends; the cloud MT API used for Kiswahili has no
Dholuo support at all, confirmed via its live `/languages` API). See docs/
week4_swahili_dholuo_summary.md for the full comparison.

Run on a remote GPU platform purely for speed/reliability over the local-CPU
path already proven this session -- same model, same decoding config, not a
different backend decision. This script shells out to the private
NLP/Project/psa_mt_week4_internal/ scripts (submit_nllb.py/poll_nllb.py
against an already-deployed app) rather than importing the remote-GPU
platform's own client library directly -- keeps this shared-repo file free of
any specific-compute-vendor reference, same convention already applied to
scripts/translate_kiswahili_cloud_mt_bulk.py's NLLB-fallback path.

Checkpointed per-chunk, resumable if interrupted (same discipline as every
other bulk job this project has run).

Usage:
    python scripts/translate_dholuo_nllb_bulk.py
"""

import json
import os
import re
import subprocess
import sys
import time
from collections import Counter

import pandas as pd

SOURCE = "psa_pipeline/output/kenyan_psa_ekegusii_15000_translated.csv"
CHECKPOINT = "psa_pipeline/output/.dholuo_nllb_checkpoint.json"
OUT = "psa_pipeline/output/kenyan_psa_dholuo_nllb_15000_translated.csv"

NLLB_DIR = "/home/coder/workspace/NLP/Project/psa_mt_week4_internal"
CHUNK = 2000


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
            return json.load(f)
    return {}


def save_checkpoint(checkpoint):
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def translate_chunk(rows, chunk_tag):
    chunk_path = f"/tmp/dholuo_bulk_chunk_{chunk_tag}.json"
    call_path = f"/tmp/dholuo_bulk_call_{chunk_tag}.txt"
    out_path = f"/tmp/dholuo_bulk_out_{chunk_tag}.json"
    with open(chunk_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False)

    subprocess.run(
        ["python3", "submit_nllb.py", chunk_path, call_path, "luo_Latn"],
        cwd=NLLB_DIR, check=True,
    )
    print(f"  chunk {chunk_tag}: submitted {len(rows)} rows, polling...")
    while True:
        proc = subprocess.run(
            ["python3", "poll_nllb.py", call_path, out_path, "60"],
            cwd=NLLB_DIR, check=True, capture_output=True, text=True,
        )
        if "DONE" in proc.stdout:
            break
        print(f"    chunk {chunk_tag}: not ready yet, waiting...")
        time.sleep(15)

    with open(out_path, encoding="utf-8") as f:
        return json.load(f)


def main():
    df = pd.read_csv(SOURCE, dtype=str)
    checkpoint = load_checkpoint()
    todo = df[~df["PSA_ID"].isin(checkpoint.keys())]
    print(f"{len(checkpoint)} already done, {len(todo)} remaining of {len(df)}")

    rows = [{"psa_id": r.PSA_ID, "english": r.English} for r in todo.itertuples()]
    for i in range(0, len(rows), CHUNK):
        chunk = rows[i:i + CHUNK]
        results = translate_chunk(chunk, chunk_tag=i)
        for r in results:
            checkpoint[r["psa_id"]] = r["translation"]
        save_checkpoint(checkpoint)
        print(f"  {min(i + CHUNK, len(rows))}/{len(rows)} of this run's remaining rows done, checkpointed "
              f"({len(checkpoint)}/{len(df)} total)")

    df["Dholuo"] = df["PSA_ID"].map(checkpoint)
    n_missing = df["Dholuo"].isna().sum()
    if n_missing:
        sys.exit(f"{n_missing} rows still missing a Dholuo translation after the run -- not writing output")

    df["Dholuo_tool"] = "nllb_200_distilled_600m"
    degenerate = df.apply(lambda r: is_degenerate(r["Dholuo"], en_source=r["English"]), axis=1)
    df["Dholuo_review_flag"] = None
    df.loc[degenerate, "Dholuo_review_flag"] = "degenerate"
    print(f"Degenerate flagged: {degenerate.sum()}/{len(df)}")

    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT}: {len(df)} rows")


if __name__ == "__main__":
    main()
