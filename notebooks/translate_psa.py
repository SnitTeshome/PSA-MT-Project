# Week 3 CLI deliverable: python translate_psa.py --text "..." --src English --tgt Kiswahili --model models_week3/mt5_English_to_Kiswahili
import argparse, torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

NLLB_CODE = {"English": "eng_Latn", "Kiswahili": "swh_Latn", "Ekegusii": None}
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def translate(text, src, tgt, model_path, model_type):
    tok = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(DEVICE)
    if model_type == "nllb":
        tok.src_lang = NLLB_CODE[src]
        enc = tok(text, return_tensors="pt", truncation=True, max_length=128).to(DEVICE)
        gen = model.generate(**enc, forced_bos_token_id=tok.convert_tokens_to_ids(NLLB_CODE[tgt]),
                             max_length=128)
    else:
        enc = tok(f"translate {src} to {tgt}: {text}", return_tensors="pt",
                  truncation=True, max_length=128).to(DEVICE)
        gen = model.generate(**enc, max_length=128)
    return tok.batch_decode(gen, skip_special_tokens=True)[0].strip()

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Translate a PSA between English/Kiswahili/Ekegusii.")
    ap.add_argument("--text", required=True)
    ap.add_argument("--src", required=True)
    ap.add_argument("--tgt", required=True)
    ap.add_argument("--model", required=True, help="path to a saved checkpoint")
    ap.add_argument("--model_type", default="mt5", choices=["mt5", "nllb"])
    a = ap.parse_args()
    print(translate(a.text, a.src, a.tgt, a.model, a.model_type))
