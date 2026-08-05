#!/usr/bin/env python3
"""
translate_psa.py

Standalone inference pipeline for PSA-MT.

Model priority:
1. Fine-tuned NLLB
2. Fine-tuned mT5 per-direction
3. Fine-tuned mT5 combined

"""

from pathlib import Path
import argparse

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)


# ============================================================
# Configuration
# ============================================================

MAX_LEN = 128

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print("Using device:", DEVICE)


# ============================================================
# Language codes
# ============================================================

NLLB_CODE = {

    "English": "eng_Latn",

    "Kiswahili": "swh_Latn",

    # Ekegusii workaround
    "Ekegusii": "kin_Latn",
}



# ============================================================
# Model roots
# ============================================================

NLLB_ROOT = Path(
    "PSA-MT-Outputs-v2/models/fine_tuned/nllb"
)


MT5_ROOT = Path(
    "PSA-MT-Outputs/models/fine_tuned/mt5"
)



# ============================================================
# NLLB checkpoints
# ============================================================

NLLB_DIR_PATHS = {

    "English_to_Ekegusii":
        NLLB_ROOT
        / "English_to_Ekegusii"
        / "best",


    "Kiswahili_to_Ekegusii":
        NLLB_ROOT
        / "Kiswahili_to_Ekegusii"
        / "best",
}



# ============================================================
# mT5 checkpoints
# ============================================================

MT5_PER_DIRECTION_PATHS = {


    "English_to_Kiswahili":
        MT5_ROOT
        / "per_direction"
        / "English_to_Kiswahili"
        / "best",


    "Kiswahili_to_English":
        MT5_ROOT
        / "per_direction"
        / "Kiswahili_to_English"
        / "best",


    # Latest available English → Ekegusii
    "English_to_Ekegusii":
        MT5_ROOT
        / "ablation_full_finetune"
        / "English_to_Ekegusii"
        / "checkpoint-1830",


    "Kiswahili_to_Ekegusii":
        MT5_ROOT
        / "per_direction"
        / "Kiswahili_to_Ekegusii"
        / "best",


    "Ekegusii_to_Kiswahili":
        MT5_ROOT
        / "per_direction"
        / "Ekegusii_to_Kiswahili"
        / "best",
}



# ============================================================
# Combined mT5
# ============================================================

MT5_COMBINED_PATH = (
    MT5_ROOT
    / "combined"
    / "best"
)



# ============================================================
# Model cache
# ============================================================

_model_cache = {}




def load_checkpoint(path):

    """
    Load tokenizer and model once.
    Handles Transformers 5.x NLLB tokenizer compatibility.
    """

    key = str(path)


    if key not in _model_cache:


        # -----------------------------------
        # NLLB tokenizer compatibility fix
        # -----------------------------------

        import json
        from pathlib import Path


        path = Path(path)

        tokenizer_config = path / "tokenizer_config.json"


        backup = None


        if tokenizer_config.exists():

            with open(tokenizer_config, "r") as f:
                config = json.load(f)


            if isinstance(
                config.get("extra_special_tokens"),
                list
            ):

                backup = config["extra_special_tokens"]

                config["extra_special_tokens"] = {}


                with open(tokenizer_config, "w") as f:
                    json.dump(
                        config,
                        f,
                        indent=2
                    )


        tokenizer = AutoTokenizer.from_pretrained(
            path,
            local_files_only=True
        )


        model = (
            AutoModelForSeq2SeqLM
            .from_pretrained(
                path,
                local_files_only=True
            )
            .to(DEVICE)
            .eval()
        )


        _model_cache[key] = (
            tokenizer,
            model
        )


    return _model_cache[key]


# ============================================================
# Automatic checkpoint selection
# ============================================================

def resolve_checkpoint(src, tgt):

    direction = f"{src}_to_{tgt}"


    # -----------------------------
    # Priority 1: NLLB
    # -----------------------------

    if direction in NLLB_DIR_PATHS:

        path = NLLB_DIR_PATHS[direction]

        if (path / "config.json").exists():

            return path, "nllb"



    # -----------------------------
    # Priority 2: mT5 per direction
    # -----------------------------

    if direction in MT5_PER_DIRECTION_PATHS:

        path = MT5_PER_DIRECTION_PATHS[direction]

        if (path / "config.json").exists():

            return path, "mt5"



    # -----------------------------
    # Priority 3: mT5 combined
    # -----------------------------

    if (MT5_COMBINED_PATH / "config.json").exists():

        return MT5_COMBINED_PATH, "mt5"



    return None, None

# ============================================================
# mT5 inference
# ============================================================


@torch.no_grad()

def translate_mt5(
    text,
    src,
    tgt,
    model_path
):


    tokenizer, model = load_checkpoint(
        model_path
    )


    prompt = (
        f"translate {src} to {tgt}: {text}"
    )


    encoded = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LEN
    ).to(DEVICE)



    output = model.generate(
        **encoded,
        max_length=MAX_LEN
    )


    return tokenizer.decode(
        output[0],
        skip_special_tokens=True
    ).strip()



# ============================================================
# NLLB inference
# ============================================================


@torch.no_grad()

def translate_nllb(
    text,
    src,
    tgt,
    model_path
):


    tokenizer, model = load_checkpoint(
        model_path
    )


    tokenizer.src_lang = (
        NLLB_CODE[src]
    )


    encoded = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LEN
    ).to(DEVICE)



    forced_bos = tokenizer.convert_tokens_to_ids(
        NLLB_CODE[tgt]
    )


    output = model.generate(
        **encoded,
        forced_bos_token_id=forced_bos,
        max_length=MAX_LEN
    )



    result = tokenizer.decode(
        output[0],
        skip_special_tokens=True
    ).strip()



    return result



# ============================================================
# Automatic translation
# ============================================================


@torch.no_grad()

def translate(
    text,
    src,
    tgt
):


    checkpoint, model_type = resolve_checkpoint(
        src,
        tgt
    )



    if checkpoint is None:

        raise RuntimeError(
            f"No checkpoint found for {src}->{tgt}"
        )



    print(
        "\nUsing:",
        model_type.upper()
    )

    print(
        "Checkpoint:",
        checkpoint
    )



    if model_type == "nllb":


        return translate_nllb(
            text,
            src,
            tgt,
            checkpoint
        )


    else:


        return translate_mt5(
            text,
            src,
            tgt,
            checkpoint
        )



# ============================================================
# CLI
# ============================================================


def main():


    parser = argparse.ArgumentParser()


    parser.add_argument(
        "--text",
        required=True
    )


    parser.add_argument(
        "--src",
        required=True,
        choices=[
            "English",
            "Kiswahili",
            "Ekegusii"
        ]
    )


    parser.add_argument(
        "--tgt",
        required=True,
        choices=[
            "English",
            "Kiswahili",
            "Ekegusii"
        ]
    )


    args = parser.parse_args()



    output = translate(
        args.text,
        args.src,
        args.tgt
    )



    print("\nTranslation:")
    print(output)



if __name__ == "__main__":

    main()