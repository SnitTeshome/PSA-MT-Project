"""Quick real comparison for Somali: cloud translation API vs NLLB-200, scored
against real gold Somali already present in agriculture_psas.csv (100%
filled, team-verified). Same method as the Kiswahili/Dholuo comparison
(docs/week4_swahili_dholuo_summary.md) -- picks a backend empirically rather
than assuming either wins, cross-domain sample not agriculture-only.

Credential env var names are that provider's own required names.

Usage:
    python scripts/compare_somali_backends.py
"""

import os
import random

import pandas as pd
import requests
import sacrebleu

random.seed(42)

N_SAMPLE = 40


def cloud_mt_translate(texts, src, tgt):
    key = os.environ["AZURE_TRANSLATOR_KEY"]
    endpoint = os.environ["AZURE_TRANSLATOR_ENDPOINT"]
    region = os.environ["AZURE_TRANSLATOR_REGION"]
    out = []
    for i in range(0, len(texts), 50):
        chunk = texts[i:i + 50]
        resp = requests.post(
            f"{endpoint}translate?api-version=3.0&from={src}&to={tgt}",
            headers={"Ocp-Apim-Subscription-Key": key, "Ocp-Apim-Subscription-Region": region,
                     "Content-Type": "application/json"},
            json=[{"Text": t} for t in chunk], timeout=60,
        )
        resp.raise_for_status()
        out.extend([d["translations"][0]["text"] for d in resp.json()])
    return out


def nllb_translate(texts, src, tgt):
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
    tok.src_lang = src
    forced_bos = tok.convert_tokens_to_ids(tgt)
    out = []
    for i in range(0, len(texts), 8):
        chunk = texts[i:i + 8]
        inputs = tok(chunk, return_tensors="pt", padding=True, truncation=True, max_length=128)
        gen = model.generate(**inputs, forced_bos_token_id=forced_bos, max_length=128,
                              no_repeat_ngram_size=3, num_beams=4)
        out.extend(tok.batch_decode(gen, skip_special_tokens=True))
    del model
    return out


def main():
    df = pd.read_csv("data/raw/agriculture/agriculture_psas.csv", dtype=str)
    gold = df[df["Somali"].notna() & df["English"].notna()].sample(N_SAMPLE, random_state=42)
    en = gold["English"].tolist()
    ref = gold["Somali"].tolist()

    print(f"Sample: {len(en)} rows with real gold Somali")

    cloud_out = cloud_mt_translate(en, "en", "so")
    cloud_chrf = sacrebleu.corpus_chrf(cloud_out, [ref]).score
    print(f"Cloud MT chrF: {cloud_chrf:.1f}")

    nllb_out = nllb_translate(en, "eng_Latn", "som_Latn")
    nllb_chrf = sacrebleu.corpus_chrf(nllb_out, [ref]).score
    print(f"NLLB-200 chrF: {nllb_chrf:.1f}")

    print("\n=== 3 sample comparisons ===")
    for i in range(3):
        print(f"EN:    {en[i]}")
        print(f"GOLD:  {ref[i]}")
        print(f"CLOUD: {cloud_out[i]}")
        print(f"NLLB:  {nllb_out[i]}")
        print()

    winner = "cloud_mt" if cloud_chrf > nllb_chrf else "nllb"
    print(f"Winner: {winner} (Cloud MT {cloud_chrf:.1f} vs NLLB {nllb_chrf:.1f})")


if __name__ == "__main__":
    main()
