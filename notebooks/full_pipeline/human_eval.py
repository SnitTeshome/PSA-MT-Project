#!/usr/bin/env python3
"""
human_eval.py -- builds and scores the human-evaluation sheet required by the Week 4
checklist: "Conduct human evaluation (fluency, adequacy, cultural accuracy) with native
speakers (100+ test sentences)."

This script can build the sheet and score a completed one -- it cannot, and does not
pretend to, provide the actual human judgments. Real native speakers must fill in the
*_1to5 columns before `score` produces meaningful numbers.

Reuses NLLB_CODE/MAX_LEN/DEVICE from translate_psa.py rather than redefining them. Loads
each checkpoint once (not per-row, unlike calling translate_psa.py's functions directly in
a loop, which would reload the model 100+ times -- impractically slow for this use case).

Usage:
    # Build the sheet: samples test sentences, runs your trained model, saves a CSV to fill in
    python human_eval.py build \\
        --data_dir data_processed \\
        --model_path models/fine_tuned/mt5/combined/best --model_type mt5 \\
        --directions English_to_Ekegusii Kiswahili_to_Ekegusii \\
        --n 120 --out human_eval_template.csv

    # After native speakers have filled in fluency_1to5 / adequacy_1to5 / cultural_accuracy_1to5:
    python human_eval.py score --sheet human_eval_template.csv
"""

import argparse
from pathlib import Path

import pandas as pd
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


def build_sheet(data_dir, model_path, model_type, directions, n, out, seed=42):
    rows = []
    per_bucket = max(1, n // len(directions))
    for direction in directions:
        src, tgt = direction.split("_to_")
        test_path = Path(data_dir) / f"{direction}.test.csv"
        if not test_path.exists():
            print(f"WARNING: {test_path} not found -- skipping {direction}.")
            continue
        df = pd.read_csv(test_path).dropna(subset=["src_text", "tgt_text"])
        sample = df.sample(min(len(df), per_bucket), random_state=seed).reset_index(drop=True)
        preds = batch_translate(sample["src_text"].tolist(), src, tgt, model_path, model_type)
        for i, row in sample.iterrows():
            rows.append({
                "direction": direction,
                "domain": row.get("Domain", ""),
                "source_text": row["src_text"],
                "reference_translation": row["tgt_text"],
                "model_translation": preds[i],
                "fluency_1to5": "",
                "adequacy_1to5": "",
                "cultural_accuracy_1to5": "",
                "evaluator_notes": "",
            })

    sheet = pd.DataFrame(rows)
    sheet.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"Saved {len(sheet)} sentences to {out}.")
    if len(sheet) < 100:
        print(f"WARNING: only {len(sheet)} sentences -- checklist asks for 100+. "
              f"Increase --n or check your test-set sizes.")
    print("Send this file to native speakers to fill in the *_1to5 columns, "
          "then run: python human_eval.py score --sheet " + str(out))


def score_sheet(sheet_path):
    df = pd.read_csv(sheet_path)
    cols = ["fluency_1to5", "adequacy_1to5", "cultural_accuracy_1to5"]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    n_rated = df[cols].notna().all(axis=1).sum()
    print(f"{n_rated} / {len(df)} rows have all three ratings filled in.")
    if n_rated == 0:
        print("No completed ratings found -- have native speakers fill in the *_1to5 "
              "columns before scoring.")
        return

    summary = df.groupby("direction")[cols].mean().round(2)
    print("\nAverage human-eval scores by direction (1-5 scale):")
    print(summary)

    out_path = Path(sheet_path).with_suffix("").as_posix() + ".summary.csv"
    summary.to_csv(out_path)
    print(f"\nSaved summary to {out_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Sample test sentences and generate translations to be rated")
    b.add_argument("--data_dir", required=True, help="Folder containing <direction>.test.csv files")
    b.add_argument("--model_path", required=True)
    b.add_argument("--model_type", required=True, choices=["mt5", "nllb"])
    b.add_argument("--directions", nargs="+", required=True)
    b.add_argument("--n", type=int, default=120, help="Total sentences across all directions (checklist asks for 100+)")
    b.add_argument("--out", default="human_eval_template.csv")

    s = sub.add_parser("score", help="Summarize a completed human-eval sheet")
    s.add_argument("--sheet", required=True)

    args = ap.parse_args()
    if args.cmd == "build":
        build_sheet(args.data_dir, args.model_path, args.model_type, args.directions,
                    args.n, args.out)
    else:
        score_sheet(args.sheet)
