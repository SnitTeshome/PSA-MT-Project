# Week 3 Report — Model Building: Machine Translation of PSAs

**DSA 4020A: Natural Language Processing · Group One**
_Week 3: Modeling with Transfer Learning (Sub-objective 2)_

**▶ Model-building notebook (Google Colab):** https://colab.research.google.com/drive/1GzBrKXOmP7Kb-XSd9mqTrEgpp9W70NGB?usp=sharing

This stage fine-tunes and evaluates translation models on the curated PSA corpus
(`psa_main_transformed.csv`, 19,795 aligned English–Kiswahili–Ekegusii sentences from Week 2). The
goal is a working proof-of-concept translator for **English → Kiswahili** and the low-resource
**English → Ekegusii**, with baselines, ablations, tracked experiments and a live demo.

---

## 1. Models

Two pretrained sequence-to-sequence models were used via Hugging Face `transformers`:

| Model | Role | Why |
|---|---|---|
| **NLLB-200-distilled-600M** | Strong baseline for English↔Kiswahili | Already supports both languages; excellent zero-shot quality |
| **mT5-small** | Fine-tuned workhorse for all directions incl. Ekegusii | Text-to-text and language-agnostic — the only path to **Ekegusii**, which NLLB-200 does not cover |

This satisfies the "≥2 pretrained models" requirement and directly frames the transfer-learning
story: NLLB anchors the well-resourced pair, mT5 carries the low-resource one.

---

## 2. Data & splits

- Input: `psa_main_transformed.csv` — 19,795 rows, **100% coverage** for English, Kiswahili and Ekegusii.
- Splits are built inside the notebook and are **leakage-safe** (grouped by `PSA_ID`, stratified by domain): **15,833 train / 1,980 dev / 1,982 test** per direction.
- The wide table is melted into directional sentence pairs; this run trained the two "into-target" directions used by the demo: **English → Kiswahili** and **English → Ekegusii**.
- Training used a **few-shot cap of 4,000 examples** per direction (the low-resource setting), evaluated on the full dev/test sets.

---

## 3. Training setup (hyperparameters)

| Setting | mT5-small | NLLB-200-distilled |
|---|---|---|
| Mode | Few-shot fine-tune | Zero-shot (not fine-tuned) |
| Optimiser | Adafactor | — |
| Learning rate | 1e-3 | — |
| Epochs | 3 | — |
| Batch size | 16 | — |
| Max length | 128 tokens | 128 tokens |
| Encoder | Unfrozen | — |
| Train examples/direction | 4,000 (few-shot cap) | — |
| Decoding | beam search + `<extra_id_N>` cleanup | beam search, `forced_bos_token_id` for target lang |

Outputs were persisted to Google Drive (`/content/drive/MyDrive/psa_week3/`) so checkpoints survive a
Colab disconnect. Training time was ~10–13 minutes per mT5 direction on a Colab GPU.

---

## 4. Experiment tracking

Runs were logged with **MLflow** (experiment `psa-mt-week3`) — parameters, BLEU/chrF metrics and per-epoch curves are captured for each training run.

---

## 5. Results

Metrics are **BLEU** and **chrF++** (via `sacrebleu`) on the held-out test set (1,982 sentences).

### 5.1 Overall performance summary

| Model | Direction | Setting | BLEU | chrF++ |
|---|---|---|--:|--:|
| **mT5-small** | English → Kiswahili | few-shot fine-tune | **68.08** | **78.38** |
| NLLB-200-distilled | English → Kiswahili | zero-shot | 57.73 | 74.71 |
| NLLB-200-distilled | Kiswahili → English | zero-shot | 46.37 | 67.76 |
| mT5-small | English → Ekegusii | few-shot fine-tune | 5.81 | 26.15 |

### 5.2 Fine-tuning vs zero-shot (ablation)

Fine-tuning mT5 on the PSA data **beat the strong NLLB zero-shot baseline** for English → Kiswahili
(**68.08 vs 57.73 BLEU**), showing the domain fine-tuning paid off. Per-epoch dev progress:

| Epoch | En → Kiswahili (BLEU / chrF) | En → Ekegusii (BLEU / chrF) |
|--:|--:|--:|
| 1 | 42.31 / 58.88 | 3.01 / 20.20 |
| 2 | 66.64 / 76.78 | 4.61 / 24.51 |
| 3 | 68.42 / 79.63 | 6.43 / 27.29 |

Both directions improve monotonically across epochs.

### 5.3 Per-domain results (English → Kiswahili, mT5)

| Domain | BLEU | chrF++ | Test rows |
|---|--:|--:|--:|
| Security & Safety | 75.49 | 86.00 | 302 |
| Education | 73.60 | 82.68 | 426 |
| Agriculture | 67.89 | 78.44 | 401 |
| Governance | 67.14 | 78.28 | 347 |
| Health | 63.66 | 75.60 | 407 |
| **Security** | **7.18** | **32.76** | 99 |

Quality is strong and consistent (63–75 BLEU) across five domains. The small **Security** subset
(99 rows) is a sharp outlier at 7.18 BLEU — see Limitations.

---

## 6. Key findings

- **Fine-tuning beat the baseline for Kiswahili.** mT5 fine-tuned reached **68.08 BLEU / 78.38 chrF**, above NLLB zero-shot (57.73 / 74.71) — domain adaptation to PSA text helped.
- **NLLB zero-shot is a strong, free baseline** for English↔Kiswahili (57.73 / 46.37 BLEU) with no training, and remains a good fallback.
- **Ekegusii is the hard, low-resource case.** mT5 reached only **5.81 BLEU / 26.15 chrF**, but improved every epoch and produces recognisable output — the chrF of 26 shows real character-level signal. This gap is exactly the challenge the project targets.
- **Domain performance is even** except for the tiny **Security** subset, whose collapse (7.18 BLEU) flags a data issue rather than a modelling one.
- **Training is cheap and fast** (~10–13 min/direction on one GPU), so scaling up epochs, data and directions is feasible.

---

## 7. Artifacts & files

| File | Description |
|---|---|
| [`PSA_Week3_Modeling_TransferLearning.ipynb`](https://colab.research.google.com/drive/1GzBrKXOmP7Kb-XSd9mqTrEgpp9W70NGB?usp=sharing) | Training + evaluation notebook (builds splits, trains, evaluates, saves) — open in Colab |
| `PSA_Translate_FromDrive.ipynb` | Standalone inference notebook — loads the trained models and translates typed sentences |

---

## 8. How to reproduce

1. Open the [**model-building notebook in Colab**](https://colab.research.google.com/drive/1GzBrKXOmP7Kb-XSd9mqTrEgpp9W70NGB?usp=sharing) and set the runtime to **GPU** (Runtime → Change runtime type → GPU).
2. Run Section 0 (auto-installs dependencies).
3. Provide `psa_main_transformed.csv` when Section 1b prompts (or place it next to the notebook).
4. Run top to bottom. Checkpoints and results save to `MyDrive/psa_week3/`.

Lean config used for this run (finishes in ~30–40 min): 2 directions, `FEWSHOT_N=4000`,
mT5 `epochs=3`, NLLB fine-tuning off, freeze ablation off. Scale these up for stronger results.

---

## 9. Inference / demo

**`PSA_Translate_FromDrive.ipynb`** downloads the trained models from the shared Drive folder and prompts for a sentence — anyone can run it, no training needed.

---

## 10. Limitations & next steps

- **Ekegusii quality is low (5.81 BLEU).** Next: train the reverse and Kiswahili↔Ekegusii directions, remove the 4,000-example cap (use all ~15.8k), add more epochs, and try back-translation augmentation and a joint many-to-many mT5 so Kiswahili data lifts Ekegusii.
- **The "Security" domain collapses (7.18 BLEU, 99 rows).** It should be merged into "Security & Safety" (as done in the cleaning notebook) and re-checked — the split label and tiny size likely explain the outlier.
- **Evaluation caveat:** the corpus is ~76% synthetic. Report test scores on `real_collected` rows separately in Week 4, and add **COMET** and **human evaluation** (fluency / adequacy / cultural accuracy) alongside BLEU/chrF.
- **Decoding:** this run used light decoding for speed; enabling wider beam search should give a small quality bump for the final demo.
