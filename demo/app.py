#!/usr/bin/env python3
"""
app.py -- PSA-MT Web Application

Priority:
1. NLLB (PSA-MT-Outputs-v2)
2. mT5 Per-Direction (PSA-MT-Outputs)

Features
--------
✓ Automatic model selection
✓ Confidence estimation
✓ Translation comparison
✓ Feedback logging
✓ Example PSAs
"""

import torch
import numpy as np
import pandas as pd
import gradio as gr

from pathlib import Path
from datetime import datetime

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)

from translate_psa import (
    DEVICE,
    MAX_LEN,
    NLLB_CODE,
)

# =============================================================================
# MODEL LOCATIONS
# =============================================================================

PROJECT_ROOT = Path.cwd()

# -------------------------------------------------------------------------
# NLLB (Outputs-v2)
# -------------------------------------------------------------------------

NLLB_ROOT = (
    PROJECT_ROOT
    / "PSA-MT-Outputs-v2"
    / "models"
    / "fine_tuned"
    / "nllb"
)

# -------------------------------------------------------------------------
# mT5 (Outputs)
# -------------------------------------------------------------------------

MT5_ROOT = (
    PROJECT_ROOT
    / "PSA-MT-Outputs"
    / "models"
    / "fine_tuned"
    / "mt5"
)

# =============================================================================
# NLLB MODELS
# =============================================================================

NLLB_MODELS = {

    "English_to_Ekegusii":
        NLLB_ROOT / "English_to_Ekegusii" / "best",

    "Kiswahili_to_Ekegusii":
        NLLB_ROOT / "Kiswahili_to_Ekegusii" / "best",

}

# =============================================================================
# mT5 PER-DIRECTION MODELS
# =============================================================================

MT5_MODELS = {

    "English_to_Ekegusii":
        MT5_ROOT / "per_direction" / "English_to_Ekegusii" / "best",

    "English_to_Kiswahili":
        MT5_ROOT / "per_direction" / "English_to_Kiswahili" / "best",

    "Kiswahili_to_English":
        MT5_ROOT / "per_direction" / "Kiswahili_to_English" / "best",

    "Kiswahili_to_Ekegusii":
        MT5_ROOT / "per_direction" / "Kiswahili_to_Ekegusii" / "best",

    "Ekegusii_to_Kiswahili":
        MT5_ROOT / "per_direction" / "Ekegusii_to_Kiswahili" / "best",

    "Ekegusii_to_English":
        MT5_ROOT / "per_direction" / "Ekegusii_to_English" / "best",

}

# =============================================================================
# MODEL CACHE
# =============================================================================

_model_cache = {}
# =============================================================================
# LOAD MODEL
# =============================================================================

def load_checkpoint(path):
    """
    Load a model once and cache it for future use.
    """

    key = str(path)

    if key not in _model_cache:

        print(f"\nLoading model:\n{path}\n")

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


# =============================================================================
# AUTOMATIC MODEL SELECTION
# =============================================================================

def resolve_checkpoint(src, tgt):
    """
    Priority:

        1. NLLB (Outputs-v2)
        2. mT5 per-direction

    Returns
    -------
    (path, model_type)
    """

    direction = f"{src}_to_{tgt}"

    # ---------------------------------------------------------
    # Priority 1
    # NLLB
    # ---------------------------------------------------------

    if direction in NLLB_MODELS:

        path = NLLB_MODELS[direction]

        if (path / "config.json").exists():

            print("Using NLLB model")

            return (
                path,
                "nllb"
            )

    # ---------------------------------------------------------
    # Priority 2
    # mT5
    # ---------------------------------------------------------

    if direction in MT5_MODELS:

        path = MT5_MODELS[direction]

        if (path / "config.json").exists():

            print("Using mT5 model")

            return (
                path,
                "mt5"
            )

    # ---------------------------------------------------------

    return (
        None,
        None
    )


# =============================================================================
# TRANSLATION ROUTER
# =============================================================================

@torch.no_grad()
def translate_with_confidence(
    text,
    src,
    tgt,
    model_choice="Auto"
):

    if not text.strip():
        return "", ""

    if src == tgt:
        return (
            "Source and target language must differ.",
            ""
        )

    direction = f"{src}_to_{tgt}"

    # ==========================================================
    # AUTO
    # ==========================================================

    if model_choice == "Auto":

        path, model_type = resolve_checkpoint(src, tgt)

        if path is None:
            return (
                f"No trained model found for {direction}.",
                ""
            )

        return _translate_one(
            text,
            src,
            tgt,
            path,
            model_type
        )

    # ==========================================================
    # NLLB ONLY
    # ==========================================================

    elif model_choice == "NLLB only":

        if direction not in NLLB_MODELS:
            return (
                f"No NLLB checkpoint for {direction}.",
                ""
            )

        path = NLLB_MODELS[direction]

        return _translate_one(
            text,
            src,
            tgt,
            path,
            "nllb"
        )

    # ==========================================================
    # mT5 ONLY
    # ==========================================================

    elif model_choice == "mT5 only":

        if direction not in MT5_MODELS:
            return (
                f"No mT5 checkpoint for {direction}.",
                ""
            )

        path = MT5_MODELS[direction]

        return _translate_one(
            text,
            src,
            tgt,
            path,
            "mt5"
        )

    # ==========================================================
    # BOTH (COMPARE)
    # ==========================================================

    elif model_choice == "Both (compare)":

        outputs = []
        confidences = []

        # -----------------------------
        # NLLB
        # -----------------------------

        if direction in NLLB_MODELS:

            out, conf = _translate_one(
                text,
                src,
                tgt,
                NLLB_MODELS[direction],
                "nllb"
            )

            outputs.append(
                f"===== NLLB =====\n{out}"
            )

            confidences.append(
                f"NLLB Confidence: {conf}"
            )

        # -----------------------------
        # mT5
        # -----------------------------

        if direction in MT5_MODELS:

            out, conf = _translate_one(
                text,
                src,
                tgt,
                MT5_MODELS[direction],
                "mt5"
            )

            outputs.append(
                f"===== mT5 =====\n{out}"
            )

            confidences.append(
                f"mT5 Confidence: {conf}"
            )

        if len(outputs) == 0:

            return (
                f"No checkpoint exists for {direction}.",
                ""
            )

        return (
            "\n\n".join(outputs),
            "\n".join(confidences)
        )

    # ==========================================================

    return (
        "Unknown model option.",
        ""
    )



# ============================================================
# CHUNK 4/4
# Entry point + final verification
# ============================================================

def main():
    print("=" * 80)
    print("PSA MACHINE TRANSLATION PIPELINE")
    print("=" * 80)

    print("\nConfiguration:")
    print(f"Source language : {SOURCE_LANGUAGE}")
    print(f"Target languages: {TARGET_LANGUAGES}")
    print(f"Device          : {DEVICE}")

    print("\nModel paths:")
    print(f"NLLB path : {NLLB_PATH}")
    print(f"mT5 path  : {MT5_PATH}")

    print("\nLoading translation models...")
    
    try:
        nllb_model, nllb_tokenizer = load_nllb()
        print("✓ NLLB model loaded successfully")
    except Exception as e:
        print(f"✗ Failed loading NLLB model: {e}")
        nllb_model, nllb_tokenizer = None, None

    try:
        mt5_model, mt5_tokenizer = load_mt5()
        print("✓ mT5 model loaded successfully")
    except Exception as e:
        print(f"✗ Failed loading mT5 model: {e}")
        mt5_model, mt5_tokenizer = None, None


    if nllb_model is None and mt5_model is None:
        raise RuntimeError(
            "No translation model could be loaded. "
            "Check model checkpoints and paths."
        )


    print("\nStarting PSA translation test...\n")

    sample_text = (
        "Wash your hands regularly to prevent the spread of diseases."
    )

    print("Input:")
    print(sample_text)


    for target in TARGET_LANGUAGES:

        print("\n" + "-" * 80)
        print(f"Translation: English → {target}")
        print("-" * 80)

        try:
            result = translate_text(
                text=sample_text,
                target_language=target,
                nllb_model=nllb_model,
                nllb_tokenizer=nllb_tokenizer,
                mt5_model=mt5_model,
                mt5_tokenizer=mt5_tokenizer
            )

            print("Translation:")
            print(result["translation"])

            print("\nConfidence:")
            print(
                f"{result['confidence']:.4f}"
            )

            print(
                "Model used:",
                result["model"]
            )

        except Exception as e:
            print(
                f"Translation failed for {target}: {e}"
            )


    print("\n" + "=" * 80)
    print("Translation pipeline verification completed")
    print("=" * 80)



if __name__ == "__main__":
    main()