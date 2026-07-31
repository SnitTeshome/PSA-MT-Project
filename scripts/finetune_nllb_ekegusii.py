"""Fine-tune facebook/nllb-200-distilled-600M on English->Ekegusii, using a
new 'guz_Latn' language tag seeded from Swahili's ('swh_Latn') embedding.

Rationale + expected BLEU range: docs/ekegusii_transfer_learning.md.
The tag-seeding mechanism itself (add token, resize embeddings, copy the
Swahili embedding row) is verified working on this container's CPU --
see ekegusii_internal/test_nllb_new_lang_tag.py. This script wraps that
mechanism in an actual Seq2SeqTrainer loop.

Two run modes:
  --smoke   tiny subset (default 8 rows), 1 epoch -- pipeline check only.
            CONFIRMED EMPIRICALLY (2026-07-28): --smoke still OOM-kills on
            THIS container even for a tiny subset, because full-parameter
            AdamW optimizer state for a 600M-param model needs ~4x params in
            fp32 (weights+grad+2 Adam moments) = ~9.6GB, which alone exceeds
            this container's 9GB cgroup cap before the base model, dataloader,
            or Python overhead are even counted (`cat /sys/fs/cgroup/memory.events`
            showed oom_kill incrementing on both attempts). A parallel test
            with google/mt5-small (300M params, ~3.6GB incremental optimizer
            state) completed in 7.5s with no issue -- so the Trainer/collator/
            tokenization code path itself is sound, this is purely an NLLB-
            200-distilled-600M-on-this-container memory ceiling problem.
            PRACTICAL CONSEQUENCE: use mt5-small locally to smoke-test the
            *training loop structure*; only verify the NLLB-specific tag-
            seeding mechanism locally (tokenizer/embedding surgery + a
            generate() call -- see ekegusii_internal/test_nllb_new_lang_tag.py,
            which does NOT call .train() and is memory-safe). The actual
            NLLB-200 --smoke/full fine-tune must run on a free hosted GPU
            notebook service from the start, never attempted locally.
  (default) the real run -- meant for a free hosted GPU notebook kernel, NOT
            this container. See the private kernel wrapper (outside this
            repo) that pins torch before importing this.

Usage:
    # local CPU smoke test
    python scripts/finetune_nllb_ekegusii.py --smoke \\
        --train data/splits/agriculture/ekegusii_train.csv \\
        --val   data/splits/agriculture/ekegusii_val.csv \\
        --out   /tmp/ekegusii_smoke_ckpt

    # real run (hosted GPU notebook kernel, via the kernel wrapper)
    python scripts/finetune_nllb_ekegusii.py \\
        --train data/splits/agriculture/ekegusii_train.csv \\
        --val   data/splits/agriculture/ekegusii_val.csv \\
        --out   /mnt/gpu_workdir/ekegusii_ckpt \\
        --epochs 6
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import get_runtime_for_task  # noqa: E402

MODEL_NAME = "facebook/nllb-200-distilled-600M"
NEW_LANG = "guz_Latn"
SEED_LANG = "swh_Latn"
SRC_LANG = "eng_Latn"


def apply_lora(model, r: int = 8, alpha: int = 16):
    """Wrap the model with LoRA adapters on attention projections only.

    Added 2026-07-28 after freeze_transformer_body() alone still OOM-killed
    locally (see project_psa_mt_week3_prep memory): NLLB-200's vocabulary is
    unusually large (256k tokens) because it covers 200 languages, so its
    embedding matrix alone is ~262M params -- ~44% of the whole 600M model.
    "Freeze everything except the embedding" therefore still leaves an
    enormous matrix trainable, defeating the point. LoRA sidesteps this
    entirely: the embedding and every other base-model weight stay frozen
    (contributing zero optimizer-state memory), and only small low-rank
    adapter matrices on attention projections are trainable -- typically
    <1% of total parameters regardless of how large the embedding table is.
    This is also the standard, published approach for exactly this
    scenario (low-resource language adaptation of a large pretrained MT
    model), not a workaround specific to this container.
    """
    from peft import LoraConfig, TaskType, get_peft_model

    config = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        r=r,
        lora_alpha=alpha,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
    )
    return get_peft_model(model, config)


def freeze_transformer_body(model) -> tuple[int, int]:
    """Freeze every parameter except the (tied) token embedding / output
    projection matrix. Returns (n_trainable, n_frozen) parameter counts.

    Two independent reasons to do this, not just one:
      1. Memory: AdamW optimizer state is only allocated for parameters with
         requires_grad=True (HF Trainer's create_optimizer filters on this).
         Freezing the transformer body leaves only the ~262M-parameter
         embedding matrix trainable instead of the full 600M -- confirmed
         2026-07-28 to fit locally where full fine-tuning OOM-kills (see
         project_psa_mt_week3_prep memory for the exact numbers).
      2. This is also a principled modeling choice for this specific task,
         not just a memory hack: the transformer body's learned Bantu-
         morphology handling (agglutinative verb structure, noun-class
         agreement) is exactly what the Swahili-seeding strategy is betting
         on reusing. Freezing it and only updating the embedding/output
         layer lets the model learn new *lexical* mappings for Ekegusii
         vocabulary while keeping that structural machinery untouched --
         "reuse structure, adapt lexicon," the same premise
         docs/ekegusii_transfer_learning.md's embedding-seeding idea rests on.
    """
    trainable_ids = {id(model.get_input_embeddings().weight)}
    out_emb = model.get_output_embeddings()
    if out_emb is not None:
        trainable_ids.add(id(out_emb.weight))

    n_trainable = 0
    n_frozen = 0
    for p in model.parameters():
        if id(p) in trainable_ids:
            p.requires_grad = True
            n_trainable += p.numel()
        else:
            p.requires_grad = False
            n_frozen += p.numel()
    return n_trainable, n_frozen


def add_ekegusii_tag(tok, model) -> int:
    """Add guz_Latn, seeded from swh_Latn. Returns the new token id.
    Verified mechanism -- see ekegusii_internal/test_nllb_new_lang_tag.py."""
    seed_id = tok.convert_tokens_to_ids(SEED_LANG)
    existing_id = tok.convert_tokens_to_ids(NEW_LANG)
    if existing_id != tok.unk_token_id:
        # already added in this process (e.g. this function called twice) -- reuse it
        return existing_id

    tok.add_special_tokens({"additional_special_tokens": [NEW_LANG]})
    new_id = tok.convert_tokens_to_ids(NEW_LANG)
    model.resize_token_embeddings(len(tok))
    with torch.no_grad():
        in_emb = model.get_input_embeddings()
        in_emb.weight[new_id] = in_emb.weight[seed_id].clone()
        out_emb = model.get_output_embeddings()
        if out_emb is not None and out_emb.weight.data_ptr() != in_emb.weight.data_ptr():
            out_emb.weight[new_id] = out_emb.weight[seed_id].clone()
    return new_id


def load_pairs(csv_path: str, limit: int | None) -> tuple[list[str], list[str]]:
    df = pd.read_csv(csv_path, dtype=str)
    df = df[df["Ekegusii"].fillna("").str.strip() != ""]
    df = df[df["English"].fillna("").str.strip() != ""]
    if limit:
        df = df.head(limit)
    return df["English"].tolist(), df["Ekegusii"].tolist()


def build_dataset(tok, english: list[str], ekegusii: list[str], new_id: int):
    from datasets import Dataset

    tok.src_lang = SRC_LANG

    def _tokenize(batch):
        # as_target_tokenizer() is gone in this transformers version -- text_target
        # is the current API for tokenizing the label side in one call.
        model_inputs = tok(
            batch["english"], text_target=batch["ekegusii"],
            max_length=128, truncation=True,
        )
        # Force the decoder to start from the new Ekegusii tag, same as
        # forced_bos_token_id does at inference time.
        model_inputs["labels"] = [
            [new_id] + lab[1:] if lab else lab for lab in model_inputs["labels"]
        ]
        return model_inputs

    ds = Dataset.from_dict({"english": english, "ekegusii": ekegusii})
    return ds.map(_tokenize, batched=True, remove_columns=["english", "ekegusii"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--val", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--smoke", action="store_true",
                         help="tiny subset + 1 epoch, pipeline check only, run locally on CPU")
    parser.add_argument("--smoke-rows", type=int, default=8)
    parser.add_argument("--epochs", type=int, default=6,
                         help="MAFAND-MT used 3-10 epochs at this data scale; ignored under --smoke")
    parser.add_argument("--mode", choices=["lora", "freeze_embed", "full"], default="lora",
                         help="lora (default): LoRA adapters on attention only, memory-safe "
                              "locally, standard technique for this scenario. freeze_embed: "
                              "only the embedding/output layer trainable -- confirmed 2026-07-28 "
                              "to STILL OOM-kill locally, since NLLB's embedding table alone is "
                              "~262M params (~44% of the model) -- kept only for an explicit "
                              "ablation against lora on a real GPU. full: every parameter "
                              "trainable -- confirmed to OOM-kill locally even under --smoke, "
                              "GPU only.")
    args = parser.parse_args()

    rt = get_runtime_for_task("smoke_test" if args.smoke else "finetune_mt")
    print(rt.summary())
    if not args.smoke and not rt.has_gpu:
        print("\nWARNING: --smoke was not passed but no GPU was detected. A real fine-tune "
              "on local CPU will be extremely slow and risks the container's memory ceiling "
              "(see project_psa_mt_week3_prep.md risk #4) -- strongly consider running this "
              "on a free hosted GPU notebook service instead (see the private kernel wrapper).")

    print(f"\nLoading {MODEL_NAME}...")
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    new_id = add_ekegusii_tag(tok, model)
    print(f"'{NEW_LANG}' tag id: {new_id} (seeded from '{SEED_LANG}')")

    if args.mode == "full":
        n_trainable = sum(p.numel() for p in model.parameters())
        print(f"--mode full: all {n_trainable/1e6:.1f}M params trainable "
              f"(WILL OOM ON CPU -- confirmed 2026-07-28, GPU only)")
    elif args.mode == "freeze_embed":
        n_trainable, n_frozen = freeze_transformer_body(model)
        print(f"--mode freeze_embed: {n_trainable/1e6:.1f}M trainable (embedding/output "
              f"layer), {n_frozen/1e6:.1f}M frozen (STILL OOMs on CPU -- see docstring)")
    else:  # lora
        model = apply_lora(model)
        model.print_trainable_parameters()

    limit = args.smoke_rows if args.smoke else None
    train_en, train_guz = load_pairs(args.train, limit)
    val_en, val_guz = load_pairs(args.val, limit if args.smoke else None)
    print(f"train pairs: {len(train_en)}, val pairs: {len(val_en)}")
    if len(train_en) == 0:
        sys.exit(f"No English/Ekegusii pairs found in {args.train} -- check the split file")

    train_ds = build_dataset(tok, train_en, train_guz, new_id)
    val_ds = build_dataset(tok, val_en, val_guz, new_id) if val_en else None

    collator = DataCollatorForSeq2Seq(tok, model=model)

    training_args = Seq2SeqTrainingArguments(
        output_dir=args.out,
        num_train_epochs=1 if args.smoke else args.epochs,
        per_device_train_batch_size=rt.recommended_batch_size if not args.smoke else 2,
        per_device_eval_batch_size=rt.recommended_batch_size if not args.smoke else 2,
        learning_rate=5e-5,  # MAFAND-MT's recipe
        eval_strategy="epoch" if (val_ds is not None and not args.smoke) else "no",
        save_strategy="epoch",
        save_total_limit=2,
        logging_steps=1 if args.smoke else 20,
        report_to=["wandb"] if not args.smoke else [],
        fp16=(rt.recommended_precision == "fp16"),
        bf16=(rt.recommended_precision == "bf16"),
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=collator,
        processing_class=tok,
    )

    print(f"\n{'SMOKE TEST' if args.smoke else 'FINE-TUNING'} starting...")
    trainer.train()
    trainer.save_model(args.out)
    tok.save_pretrained(args.out)
    print(f"\nSaved checkpoint + tokenizer to {args.out}")

    if args.smoke:
        print("\nSMOKE TEST PASSED -- loop ran end to end, checkpoint saved. "
              "This does NOT mean the model translates Ekegusii well (1 epoch on "
              f"{len(train_en)} rows) -- it only proves the training pipeline itself "
              "is sound before spending real hosted-GPU-hours on the full run.")


if __name__ == "__main__":
    main()
