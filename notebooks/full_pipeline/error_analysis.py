#!/usr/bin/env python3
"""
error_analysis.py -- automatic error-analysis pass required by the Week 4 checklist:
"Perform error analysis and document limitations."

Flags likely failure patterns per direction: empty outputs, outputs that just copy the
source (no translation happened), suspiciously short outputs, and repeated n-grams (a
common low-resource NMT failure mode). Saves a full per-example CSV plus a printed
worst-N preview for manual inspection -- automatic heuristics narrow down what to look at,
they don't replace actually reading the translations.

Usage:
    python error_analysis.py \\
        --data_dir data_processed --direction English_to_Ekegusii \\
        --model_path models/fine_tuned/mt5/combined/best --model_type mt5 \\
        --out error_analysis_English_to_Ekegusii.csv
"""

import argparse
from pathlib import Path

import pandas as pd
import sacrebleu
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from translate_psa import NLLB_CODE, MAX_LEN, DEVICE


@torch.no_grad()
def batch_translate(texts, src, tgt, model_path, model_type, batch_size=8):
    tok = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(DEVICE).eval()
    out = []
    for i in range(0, len(texts), batch_size):
        batch = list(texts[i:i + batch_size])
        if model_type == "nllb":
            tok.src_lang = NLLB_CODE[src]
            enc = tok(batch, return_tensors="pt", padding=True, truncation=True,
                      max_length=MAX_LEN).to(model.device)
            forced = tok.convert_tokens_to_ids(NLLB_CODE[tgt])
            gen = model.generate(**enc, forced_bos_token_id=forced, max_length=MAX_LEN)
        else:
            prompt = [f"translate {src} to {tgt}: {t}" for t in batch]
            enc = tok(prompt, return_tensors="pt", padding=True, truncation=True,
                      max_length=MAX_LEN).to(model.device)
            gen = model.generate(**enc, max_length=MAX_LEN)
        out.extend(tok.batch_decode(gen, skip_special_tokens=True))
    return [o.strip() for o in out]


def has_repeat(text, n=3):
    toks = str(text).split()
    return any(toks[i:i + n] == toks[i + n:i + 2 * n] for i in range(max(0, len(toks) - 2 * n)))


def run_error_analysis(data_dir, direction, model_path, model_type, out, n_worst=15):
    src, tgt = direction.split("_to_")
    test_path = Path(data_dir) / f"{direction}.test.csv"
    if not test_path.exists():
        raise FileNotFoundError(f"{test_path} not found.")

    df = pd.read_csv(test_path).dropna(subset=["src_text", "tgt_text"]).reset_index(drop=True)
    preds = batch_translate(df["src_text"].tolist(), src, tgt, model_path, model_type)
    df["prediction"] = preds

    df["chrf"] = [sacrebleu.sentence_chrf(p, [r], word_order=2).score
                 for p, r in zip(df["prediction"], df["tgt_text"])]
    df["error_empty_output"] = df["prediction"].str.strip().eq("")
    df["error_copied_source"] = (df["prediction"].str.strip().str.lower()
                                 == df["src_text"].str.strip().str.lower())
    df["error_much_shorter"] = (df["prediction"].str.split().apply(len)
                                < df["tgt_text"].str.split().apply(len) * 0.5)
    df["error_repetition"] = df["prediction"].apply(has_repeat)

    df.to_csv(out, index=False, encoding="utf-8-sig")

    print(f"[{direction}] {len(df)} test examples")
    print(f"  mean chrF          : {df['chrf'].mean():.1f}")
    print(f"  empty output       : {df['error_empty_output'].sum()}")
    print(f"  copied source      : {df['error_copied_source'].sum()}")
    print(f"  much shorter than ref: {df['error_much_shorter'].sum()}")
    print(f"  repetition detected: {df['error_repetition'].sum()}")
    print(f"\nSaved full annotated results to {out}")

    print(f"\nWorst {n_worst} examples by chrF:")
    worst = df.sort_values("chrf").head(n_worst)
    with pd.option_context("display.max_colwidth", 60):
        print(worst[["src_text", "tgt_text", "prediction", "chrf"]].to_string(index=False))

    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data_dir", required=True, help="Folder containing <direction>.test.csv files")
    ap.add_argument("--direction", required=True, help='e.g. "English_to_Ekegusii"')
    ap.add_argument("--model_path", required=True)
    ap.add_argument("--model_type", required=True, choices=["mt5", "nllb"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--n_worst", type=int, default=15)
    args = ap.parse_args()

    out = args.out or f"error_analysis_{args.direction}.csv"
    run_error_analysis(args.data_dir, args.direction, args.model_path, args.model_type, out, args.n_worst)
