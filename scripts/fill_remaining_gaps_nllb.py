"""Fill every remaining translation gap in the merged multilingual dataset
using NLLB-200 (winner for Somali, chrF 83.1 vs Azure's 65.8 on a real
40-row gold sample from agriculture_psas.csv -- see
scripts/compare_somali_backends.py; already-established winner for Dholuo;
a reasonable, free, no-quota-risk choice for the small remaining Kiswahili
gap too, given Azure's F0 quota is already substantially spent this session).

Gaps filled, in order: Somali (wherever null), Dholuo (wherever null),
Kiswahili (wherever null) -- covers the ~15,000 synthetic rows (missing
Somali) and the ~3,700 EkegusiiCorpus-derived real rows (missing Kiswahili/
Somali/Dholuo, real Ekegusii already present).

Checkpoints every batch to `.gaps_checkpoint.json` so an interruption doesn't
lose progress -- same discipline as every other bulk job this project has run.

Usage:
    python scripts/fill_remaining_gaps_nllb.py
"""

import json
import os
import time

import pandas as pd

IN_PATH = "data/processed/kenyan_psa_multilingual_dataset.csv"
CHECKPOINT_PATH = "psa_pipeline/output/.gaps_checkpoint.json"
BATCH = 32

LANG_CODES = {"Somali": "som_Latn", "Dholuo": "luo_Latn", "Kiswahili": "swh_Latn"}


def load_checkpoint():
    if os.path.exists(CHECKPOINT_PATH):
        with open(CHECKPOINT_PATH) as f:
            return json.load(f)
    return {}


def save_checkpoint(cp):
    with open(CHECKPOINT_PATH, "w") as f:
        json.dump(cp, f)


def main():
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    df = pd.read_csv(IN_PATH, dtype=str)
    cp = load_checkpoint()
    print(f"Loaded checkpoint with {len(cp)} already-translated rows")

    print("Loading NLLB-200-distilled-600M...")
    tok = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")

    for lang, code in LANG_CODES.items():
        needs = df[df[lang].isna() & df["English"].notna()]
        needs = needs[~needs["PSA_ID"].isin(cp.keys()) | ~needs["PSA_ID"].apply(
            lambda pid: lang in cp.get(pid, {}))]
        print(f"\n{lang}: {len(needs)} rows need translation")
        if len(needs) == 0:
            continue

        tok.src_lang = "eng_Latn"
        forced_bos = tok.convert_tokens_to_ids(code)

        rows = needs.to_dict("records")
        for i in range(0, len(rows), BATCH):
            chunk = rows[i:i + BATCH]
            texts = [r["English"] for r in chunk]
            inputs = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
            gen = model.generate(**inputs, forced_bos_token_id=forced_bos, max_length=128,
                                  no_repeat_ngram_size=3, num_beams=4)
            outs = tok.batch_decode(gen, skip_special_tokens=True)

            for r, out in zip(chunk, outs):
                pid = r["PSA_ID"]
                cp.setdefault(pid, {})[lang] = out
            save_checkpoint(cp)

            if (i // BATCH) % 10 == 0:
                elapsed = time.time()
                print(f"  {lang}: {min(i+BATCH, len(rows))}/{len(rows)} done")

    print("\nApplying checkpoint to dataframe...")
    for idx, row in df.iterrows():
        pid = row["PSA_ID"]
        if pid in cp:
            for lang, translation in cp[pid].items():
                if pd.isna(df.at[idx, lang]):
                    df.at[idx, lang] = translation
                    df.at[idx, f"{lang}_tool"] = "nllb_200"

    print(f"\nFinal fill rates:")
    for lang in ["Ekegusii", "Kiswahili", "Somali", "Dholuo"]:
        filled = df[lang].notna().sum()
        print(f"  {lang}: {filled}/{len(df)} ({filled/len(df)*100:.1f}%)")

    df.to_csv(IN_PATH, index=False)
    print(f"\nWrote {IN_PATH}")


if __name__ == "__main__":
    main()
