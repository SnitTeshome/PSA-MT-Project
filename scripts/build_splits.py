"""Build provenance-stratified train/val/test splits, per target language.

Why this exists: as of 2026-07-27, 10,037 of 11,695 rows in
agriculture_psas.csv are template-generated synthetic PSAs (tagged
`provenance=synthetic` in Metadata), and their Kiswahili/Somali/Dholuo text
was itself produced by facebook/nllb-200-distilled-600M zero-shot. Evaluating
a fine-tuned NLLB-family model against that same machine-generated text
measures self-consistency, not translation quality -- eval splits for those
three languages must be built from genuinely human-sourced rows only, or
BLEU/chrF will be inflated and meaningless. See
PSA-MT-Project/docs/ekegusii_transfer_learning.md and the workspace memory
entry project_psa_mt_week3_prep.md for the full risk writeup.

Ekegusii is unaffected -- no synthetic row has ever carried Ekegusii, since
no pretrained MT model covers it -- so every Ekegusii-filled row is already
real/human-sourced.

Two provenance tiers, reported and split on separately:
  - "real"          : Metadata does not contain `provenance=synthetic`
  - "strict_human"  : real, AND Metadata's `qa_tool` (if present) does not
                       mention nllb -- i.e. no NLLB involvement anywhere in
                       this row's translation history. This is the tier used
                       to build val/test splits; train pools from everything
                       (including synthetic rows, which the Week 3 brief
                       explicitly permits as data-augmentation material).

Usage:
    python scripts/build_splits.py data/raw/agriculture/agriculture_psas.csv \\
        --out-dir data/splits/agriculture
"""

import argparse
import json
from pathlib import Path

import pandas as pd

LANGUAGES = ["Ekegusii", "Kiswahili", "Somali", "Dholuo"]


def parse_metadata(raw: str) -> dict:
    out = {}
    for part in str(raw or "").split(";"):
        part = part.strip()
        if not part or "=" not in part:
            continue
        k, _, v = part.partition("=")
        out[k.strip().lower()] = v.strip()
    return out


def is_synthetic(meta: dict) -> bool:
    return meta.get("provenance", "").lower() == "synthetic"


def touched_by_nllb(meta: dict) -> bool:
    return "nllb" in meta.get("qa_tool", "").lower()


def build_report(df: pd.DataFrame) -> dict:
    report = {}
    for lang in LANGUAGES:
        has_lang = df[lang].fillna("").str.strip() != ""
        report[lang] = {
            "total_filled": int(has_lang.sum()),
            "real_filled": int((has_lang & df["_real"]).sum()),
            "strict_human_filled": int((has_lang & df["_strict_human"]).sum()),
            "synthetic_filled": int((has_lang & df["_synthetic"]).sum()),
        }
    return report


def main(csv_path: str, out_dir: str, seed: int, val_frac: float, test_frac: float) -> None:
    df = pd.read_csv(csv_path, dtype=str)
    meta_parsed = df["Metadata"].fillna("").map(parse_metadata)
    df["_synthetic"] = meta_parsed.map(is_synthetic)
    df["_nllb_touched"] = meta_parsed.map(touched_by_nllb)
    df["_real"] = ~df["_synthetic"]
    df["_strict_human"] = df["_real"] & ~df["_nllb_touched"]

    print(f"Loaded {len(df)} rows from {csv_path}")
    print(f"  real (provenance != synthetic): {int(df['_real'].sum())}")
    print(f"  strict_human (real AND no NLLB touch anywhere): {int(df['_strict_human'].sum())}")
    print()
    print("Per-language fill counts:")
    print(json.dumps(build_report(df), indent=2))

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print()
    print("Building splits (eval drawn from strict_human pool only):")
    for lang in LANGUAGES:
        eligible = df[df[lang].fillna("").str.strip() != ""]
        eval_pool = eligible[eligible["_strict_human"]]
        n_eval_pool = len(eval_pool)

        if n_eval_pool < 10:
            print(f"  {lang}: WARNING only {n_eval_pool} strict-human rows -- "
                  f"val/test will be tiny or empty, do not trust a BLEU score built on this")

        eval_shuffled = eval_pool.sample(frac=1, random_state=seed)
        n_val = int(n_eval_pool * val_frac)
        n_test = int(n_eval_pool * test_frac)
        val_ids = set(eval_shuffled.iloc[:n_val]["PSA_ID"])
        test_ids = set(eval_shuffled.iloc[n_val:n_val + n_test]["PSA_ID"])
        train_ids = set(eligible["PSA_ID"]) - val_ids - test_ids

        for split_name, ids in [("train", train_ids), ("val", val_ids), ("test", test_ids)]:
            split_df = eligible[eligible["PSA_ID"].isin(ids)].drop(
                columns=["_synthetic", "_nllb_touched", "_real", "_strict_human"]
            )
            split_df.to_csv(out / f"{lang.lower()}_{split_name}.csv", index=False)

        print(f"  {lang}: train={len(train_ids)} (incl. synthetic) "
              f"val={len(val_ids)} test={len(test_ids)} "
              f"(val/test drawn from {n_eval_pool} strict-human rows)")

    print(f"\nWrote splits to {out}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--val-frac", type=float, default=0.1)
    parser.add_argument("--test-frac", type=float, default=0.1)
    args = parser.parse_args()
    main(args.csv_path, args.out_dir, args.seed, args.val_frac, args.test_frac)
