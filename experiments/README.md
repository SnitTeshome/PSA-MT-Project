# `experiments/` — fine-tuning experiment scripts

- **`finetune_nllb_ekegusii.py`** — fine-tunes NLLB-200-distilled-600M on
  English-Ekegusii pairs, adding `guz_Latn` as a new language token (Ekegusii isn't
  one of NLLB's 200 natively supported languages). Designed to run in a hosted
  notebook environment with a free GPU tier. This is one of the fine-tuning
  experiments referenced in `docs/ekegusii_transfer_learning.md` (§1-15) — outcome:
  outperformed by the dictionary-prompted LLM approach ultimately carried forward,
  see `docs/results_summary.md` for the full comparison.

Renamed from its original download-duplicate filename (`finetune_nllb_ekegusii (1).py`)
during the documentation pass that produced this README — no content change.
