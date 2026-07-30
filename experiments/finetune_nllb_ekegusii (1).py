"""
finetune_nllb_ekegusii.py

Fine-tune Meta's NLLB-200 (distilled 600M) on your English-Ekegusii pairs
from df_with_swahili.csv, to produce a model that actually translates
Ekegusii rather than guessing from a general-purpose chat LLM.

WHY NLLB-200
------------
NLLB was purpose-built by Meta for low-resource language translation and
already understands related Bantu languages (Swahili, Kinyarwanda,
Luganda) reasonably well. Ekegusii ("guz") is NOT one of its 200
supported languages, so we add it as a new language token and teach the
model what Ekegusii looks like using your real parallel data, rather
than training a translation model completely from scratch.

RUN THIS IN GOOGLE COLAB (free T4 GPU): Runtime -> Change runtime type -> GPU

BEFORE YOU RUN
---------------
1. Upload df_with_swahili.csv to the Colab session (left sidebar -> Files
   -> upload), or mount Google Drive and point DATA_PATH at it there.
2. Run this cell first to install dependencies:
       !pip install -q transformers datasets sacrebleu sentencepiece accelerate evaluate

WHAT THIS SCRIPT DOES
----------------------
1. Loads df_with_swahili.csv, filters out empty/duplicate/length-outlier
   rows using the len_ratio column (IQR-based, not a guessed threshold).
2. Splits into train/val/test (85/10/5), fixed seed for reproducibility.
3. Loads NLLB-200-distilled-600M, adds "guz_Latn" as a new language code
   (NLLB doesn't have Ekegusii), and resizes the embedding matrix,
   initializing the new token from the average of related Bantu
   languages already in NLLB (Swahili, Kinyarwanda, Luganda) rather than
   a random vector -- this gives the new language token a head start.
4. Fine-tunes with a low learning rate and few epochs (small-data regime
   -- overfitting is the real risk here, not underfitting).
5. Evaluates on the held-out test split with BLEU and chrF.
6. Saves the fine-tuned model, plus a CSV of test-set predictions vs.
   references for you (or a native Ekegusii speaker) to spot-check.
"""

import os
import re
import random
import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)
import evaluate

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
DATA_PATH = "df_with_swahili.csv"
MODEL_NAME = "facebook/nllb-200-distilled-600M"
NEW_LANG_CODE = "guz_Latn"                     # Ekegusii, Latin script (not in NLLB by default)
RELATED_LANGS = ["swh_Latn", "kin_Latn", "lug_Latn"]  # Swahili, Kinyarwanda, Luganda -- used to seed the new embedding
SRC_LANG = "eng_Latn"

OUTPUT_DIR = "nllb_ekegusii_finetuned"
PREDICTIONS_FILE = "test_predictions.csv"

RANDOM_SEED = 42
MAX_LENGTH = 128
TRAIN_FRAC, VAL_FRAC = 0.85, 0.10               # remaining 0.05 -> test

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)


# ----------------------------------------------------------------------
# STEP 1: Load + clean the data
# ----------------------------------------------------------------------
def load_and_filter_data(path):
    df = pd.read_csv(path)
    df = df.dropna(subset=["en_clean", "guz_clean"])
    df = df[(df["en_clean"].str.strip() != "") & (df["guz_clean"].str.strip() != "")]

    # Drop exact duplicate pairs
    before = len(df)
    df = df.drop_duplicates(subset=["en_clean", "guz_clean"])
    print(f"Dropped {before - len(df)} exact duplicate pairs.")

    # IQR-based outlier filtering on len_ratio, instead of a guessed cutoff
    if "len_ratio" in df.columns:
        q1, q3 = df["len_ratio"].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        before = len(df)
        df = df[(df["len_ratio"] >= lower) & (df["len_ratio"] <= upper)]
        print(f"len_ratio IQR bounds: [{lower:.3f}, {upper:.3f}]. "
              f"Dropped {before - len(df)} outlier rows.")

    print(f"Final usable rows: {len(df)}")
    return df.reset_index(drop=True)


def split_data(df):
    df = df.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
    n = len(df)
    n_train = int(n * TRAIN_FRAC)
    n_val = int(n * VAL_FRAC)
    train_df = df.iloc[:n_train]
    val_df = df.iloc[n_train:n_train + n_val]
    test_df = df.iloc[n_train + n_val:]
    print(f"Split -> train: {len(train_df)}, val: {len(val_df)}, test: {len(test_df)}")
    return train_df, val_df, test_df


# ----------------------------------------------------------------------
# STEP 2: Add Ekegusii as a new language to NLLB
# ----------------------------------------------------------------------
def add_new_language_token(model, tokenizer, new_code, related_codes):
    """
    NLLB identifies languages via special tokens like 'eng_Latn'. Ekegusii
    isn't one of them, so we add it as a brand-new token and resize the
    model's embedding matrix. Instead of a random initialization for the
    new token, we seed it with the average embedding of related Bantu
    languages NLLB already knows -- this gives fine-tuning a head start
    instead of learning the new language token from nothing.
    """
    if new_code in tokenizer.additional_special_tokens:
        print(f"{new_code} already present in tokenizer.")
        return

    tokenizer.add_special_tokens({"additional_special_tokens": [new_code]})
    model.resize_token_embeddings(len(tokenizer))

    new_id = tokenizer.convert_tokens_to_ids(new_code)
    embedding_matrix = model.get_input_embeddings().weight.data

    related_ids = []
    for code in related_codes:
        try:
            related_ids.append(tokenizer.convert_tokens_to_ids(code))
        except KeyError:
            print(f"  (warning) related language code {code} not found in tokenizer, skipping")

    if related_ids:
        seed_vector = embedding_matrix[related_ids].mean(dim=0)
        embedding_matrix[new_id] = seed_vector
        print(f"Seeded '{new_code}' embedding from average of {related_codes}")
    else:
        print(f"No related-language embeddings found; '{new_code}' left at random init.")


# ----------------------------------------------------------------------
# STEP 3: Tokenization
# ----------------------------------------------------------------------
def build_tokenize_fn(tokenizer, new_lang_id):
    def tokenize_fn(batch):
        tokenizer.src_lang = SRC_LANG
        model_inputs = tokenizer(
            batch["en_clean"], max_length=MAX_LENGTH, truncation=True
        )
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(
                batch["guz_clean"], max_length=MAX_LENGTH, truncation=True
            )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    return tokenize_fn


# ----------------------------------------------------------------------
# STEP 4: Evaluation metrics (BLEU + chrF)
# ----------------------------------------------------------------------
bleu_metric = evaluate.load("sacrebleu")
chrf_metric = evaluate.load("chrf")


def compute_metrics_fn(tokenizer):
    def compute_metrics(eval_preds):
        preds, labels = eval_preds
        if isinstance(preds, tuple):
            preds = preds[0]

        preds = np.where(preds != -100, preds, tokenizer.pad_token_id)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)

        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        bleu = bleu_metric.compute(
            predictions=decoded_preds,
            references=[[l] for l in decoded_labels],
        )
        chrf = chrf_metric.compute(
            predictions=decoded_preds,
            references=[[l] for l in decoded_labels],
        )
        return {"bleu": bleu["score"], "chrf": chrf["score"]}
    return compute_metrics


# ----------------------------------------------------------------------
# STEP 5: Simple Swahili-contamination check on final predictions
# ----------------------------------------------------------------------
def tokenize_words(text):
    return set(re.findall(r"[a-zA-Z']+", str(text).lower()))


def contamination_report(predictions, ekegusii_vocab, swahili_vocab):
    scores = []
    for pred in predictions:
        tokens = tokenize_words(pred)
        if not tokens:
            scores.append(0.0)
            continue
        overlap_sw = len(tokens & swahili_vocab) / len(tokens)
        overlap_guz = len(tokens & ekegusii_vocab) / len(tokens)
        scores.append(overlap_sw - overlap_guz)
    flagged = sum(1 for s in scores if s > 0.15)
    print(f"Contamination check: {flagged}/{len(scores)} predictions "
          f"look more Swahili than Ekegusii (score > 0.15)")
    return scores


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    df = load_and_filter_data(DATA_PATH)
    train_df, val_df, test_df = split_data(df)

    print("\nLoading tokenizer and model (this downloads ~2.4GB the first time)...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

    add_new_language_token(model, tokenizer, NEW_LANG_CODE, RELATED_LANGS)
    new_lang_id = tokenizer.convert_tokens_to_ids(NEW_LANG_CODE)

    train_ds = Dataset.from_pandas(train_df[["en_clean", "guz_clean"]])
    val_ds = Dataset.from_pandas(val_df[["en_clean", "guz_clean"]])
    test_ds = Dataset.from_pandas(test_df[["en_clean", "guz_clean"]])

    tokenize_fn = build_tokenize_fn(tokenizer, new_lang_id)
    train_ds = train_ds.map(tokenize_fn, batched=True, remove_columns=train_ds.column_names)
    val_ds = val_ds.map(tokenize_fn, batched=True, remove_columns=val_ds.column_names)

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        weight_decay=0.01,
        save_total_limit=2,
        num_train_epochs=6,
        predict_with_generate=True,
        fp16=torch.cuda.is_available(),
        load_best_model_at_end=True,
        metric_for_best_model="bleu",
        logging_steps=25,
        report_to="none",
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics_fn(tokenizer),
    )

    print("\nStarting fine-tuning...")
    trainer.train()

    print("\nSaving fine-tuned model to", OUTPUT_DIR)
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # ------------------------------------------------------------------
    # Final evaluation on the held-out TEST split (never seen during training)
    # ------------------------------------------------------------------
    print("\nGenerating predictions on held-out test set...")
    model.eval()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)

    predictions = []
    tokenizer.src_lang = SRC_LANG
    for text in test_df["en_clean"].tolist():
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(device)
        generated = model.generate(
            **inputs,
            forced_bos_token_id=new_lang_id,
            max_length=MAX_LENGTH,
        )
        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        predictions.append(decoded)

    references = test_df["guz_clean"].tolist()
    bleu = bleu_metric.compute(predictions=predictions, references=[[r] for r in references])
    chrf = chrf_metric.compute(predictions=predictions, references=[[r] for r in references])
    print(f"\nTEST SET RESULTS -- BLEU: {bleu['score']:.2f}  chrF: {chrf['score']:.2f}")

    # Contamination check on real fine-tuned model output (not a mock!)
    ekegusii_vocab = set()
    for text in train_df["guz_clean"].tolist():
        ekegusii_vocab |= tokenize_words(text)
    swahili_vocab = set()
    for text in train_df["sw_clean"].dropna().tolist():
        swahili_vocab |= tokenize_words(text)
    scores = contamination_report(predictions, ekegusii_vocab, swahili_vocab)

    out_df = pd.DataFrame({
        "english": test_df["en_clean"].tolist(),
        "reference_ekegusii": references,
        "predicted_ekegusii": predictions,
        "contamination_score": scores,
    })
    out_df.to_csv(PREDICTIONS_FILE, index=False)
    print(f"\nTest predictions saved to {PREDICTIONS_FILE} -- "
          f"have a native Ekegusii speaker spot-check a sample of these "
          f"before trusting the model on new data.")


if __name__ == "__main__":
    main()
