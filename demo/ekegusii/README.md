# `demo/ekegusii/`

The dictionary-prompted Ekegusii translation demo, plus four NLLB-200-backed
directions (Kiswahili both ways, Somali, Dholuo) that need no extra setup at all.
Separate from `../app.py` (the fine-tuned mT5/NLLB Gradio demo) and from
`../../notebooks/PSA_Translate_FromDriveToAnyone.ipynb`.

## Install

```bash
cd demo/ekegusii
pip install -r requirements.txt

# torch is CPU-only on purpose -- the plain PyPI wheel pulls multi-GB CUDA builds
# even on a machine with no GPU. Install it from the CPU wheel index instead:
pip install torch==2.12.1 --index-url https://download.pytorch.org/whl/cpu

# one-time NLTK corpus download, used by the dictionary's synonym-fallback matching:
python -m nltk.downloader wordnet omw-1.4
```

## Run

```bash
streamlit run app.py
```

The app itself handles the rest of the setup -- it tells you what's missing and
gives you options, rather than a separate pre-flight script. Specifically:

- **Kiswahili/Somali/Dholuo directions (4 of 5) work immediately**, no extra
  files or credentials -- they run a public pretrained model (NLLB-200) entirely
  locally.
- **The Ekegusii direction needs two things you have to bring yourself**, both
  explained with exact instructions inside the app's "Setup" panel on first load:
  1. **A dictionary file** -- licensed, paid-access material not included in
     this repo. See `data/dictionaries/README.md`.
  2. **An LLM backend credential** -- Cohere, AWS Bedrock, Azure OpenAI, or your
     own OpenAI-compatible endpoint. Pick one in the app; it tells you where to
     get a key for whichever you choose. Nothing is written to disk -- kept in
     the browser session only, and only sent to the provider you pick.

Without the dictionary, the Ekegusii direction stays hidden rather than running
in some silently-degraded mode -- the dictionary hints are the mechanism this
project validated, not an optional extra.

## What the numbers mean without the optional corpora

The retrieval bank behind the Ekegusii direction always includes
`data/splits/agriculture/ekegusii_train.csv` (repo root, already committed).
Two more sources widen it (see `data/optional_corpora/README.md`) but are
usage-restricted at their source and not shipped here. With just the built-in
agriculture split, you get this project's validated agriculture-domain numbers
(recall 0.878, chrF 49.2); general/cross-domain phrasing (greetings, small
talk, non-agriculture PSA domains) will be noticeably weaker without the extra
sources -- a known, already-documented gap, not a bug.
