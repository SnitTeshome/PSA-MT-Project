# Week 3 performance summary — Modeling with Transfer Learning

Compiled 2026-07-29. This is the mechanical "Week 3 deliverable: Model inference
script + initial performance summary" checklist item — every number and decision
below was already produced and documented across `docs/ekegusii_transfer_learning.md`;
this file pulls it into one place per the rubric's own wording. Full methodology,
citations, and reasoning: `docs/ekegusii_transfer_learning.md` (§1-15 fine-tuning arc,
§16-22 the winning direction).

## Milestone checklist (Sub-objective 2)

- [x] Experiment tracking — Weights & Biases, project `nlp-kenya`.
- [x] ≥2 pre-trained models, few-shot fine-tuned — NLLB-200-distilled-600M and
  mT5-small, both adapted for a brand-new `guz_Latn` language tag (Option A:
  embedding-tag-tuning; Option B: LoRA + `modules_to_save`/`trainable_token_indices`).
- [x] Low-resource techniques — layer freezing (embedding-only tuning), LoRA,
  data augmentation (dictionary-derived pseudo-parallel pairs, §13-15).
- [x] Ablation studies — zero-shot vs. few-shot, Option A vs. B, agriculture vs.
  general-domain, dictionary hints on/off, morphology hints on/off, exact-match vs.
  lemma/synonym-fallback dictionary lookup, 3 independent LLM backends compared
  on the same eval set/scoring code.
- [x] Checkpoints/logs saved — training-run outputs and W&B logs.
- [x] Hyperparameters/training time/results documented — `docs/
  ekegusii_transfer_learning.md`, all sections.
- [x] Inference script — `ekegusii_internal/llm_dict_prompt/translate.py`'s
  `EkegusiiTranslator` class (`.translate(sentence)` → dict with translation,
  dictionary hints, retry count, uncertainty flag). Also backs the live Streamlit demo.
- [x] Working translation demo — Streamlit app, deployed and live (see
  `docs/ekegusii_transfer_learning.md` §19 for the URL, which changes on redeploy).

## The methodological pivot (why the final approach isn't the fine-tuned models)

Both fine-tuned models (NLLB-200 and mT5-small, every configuration tried) were
outperformed by prompting a general-purpose LLM at inference time with retrieved
real examples + a bilingual dictionary — **zero fine-tuning, zero gradient descent**.
This was corroborated independently by a teammate's own separate fine-tuning attempt
in the group's shared `Misc/` folder, which found the same catastrophic-forgetting
pattern on English↔Kiswahili (BLEU dropped from 75.4 zero-shot to 3.9 after few-shot
fine-tuning). The fine-tuning work itself still satisfies this week's checklist items
(≥2 pretrained models, ablations, low-resource techniques) — it just isn't the
approach carried forward to Week 4 evaluation/deployment.

## Backend comparison — same eval set (52 held-out real agriculture PSA sentences), same scoring code

BLEU is included alongside chrF (computed retroactively via `sacrebleu` on the saved
model outputs, same tool/method as the mT5/NLLB modeling work) so this table is
directly comparable to that work's numbers too — see `docs/results_summary.md` for
the full cross-team comparison.

| Backend | BLEU | Recall | chrF | Degenerate | Notes |
|---|---|---|---|---|---|
| Zero-shot (no dictionary/examples) | 7.13 | 0.013–0.02 | ~15–21 | high | Baseline; effectively can't produce real Ekegusii |
| Fine-tuned NLLB (Option B, best) | *not recoverable* | 0.809 | 17.8 | 1/15 | Best fine-tuning result found, still well below prompting; raw generations weren't saved to re-score |
| General-purpose LLM API, dict-prompted | 28.02 | 0.878 | 49.2 | 1/52 | No morphology hints |
| General-purpose LLM API, dict-prompted + morphology | 29.38 | **0.922** | **51.1** | **0/52** | Best result from this backend; real grammar-sourced paradigm data |
| Qwen2.5-7B-Instruct-AWQ, self-hosted, dict-prompted | *not recoverable* | 0.910 | 44.7 | 1/52* | *false positive: correct proper-noun preservation; raw generations weren't saved to re-score |
| Llama 3 70B Instruct, hosted API, dict-prompted | **33.96** | 0.904 | **54.8** | **0/52** | Best BLEU and chrF overall; no self-hosting; current bulk-job frontrunner |

## Preliminary performance summary — what's proven vs. what's open

**Proven**: the dictionary-prompted mechanism generalizes well within the agriculture
PSA domain across three independent LLM backends, with recall 0.88-0.92 and chrF
45-55. Content-word coverage (recall) is essentially backend-agnostic; fluency (chrF)
is where a larger/better-aligned model earns a real, measurable edge.

**Open, found this same week (§22)**: retested the current production mechanism
outside agriculture — 100 general-vocabulary phrases (recall 1.0, chrF 31.1) and 60
real full-sentence PSAs sampled evenly across Education/Health/Security/Governance
(recall 0.957, chrF 26.6). Recall holds; chrF drops sharply, and a manual read of the
outputs confirms real defects specific to non-agriculture content — dropped numeric
facts in health advisories, un-translated English jargon in governance text, and
at least one likely non-Ekegusii fabrication the automated degeneracy check didn't
catch. **This means the mechanism is validated for Agriculture specifically, not yet
for the other 4 domains.** The scoped fix identified here — expand the retrieval
bank with the real 5-domain parallel corpus that had sat unused — **was implemented
and re-tested the same day**: cross-domain chrF improved from 26.6 to **38.6** (a
real +12 point gain), though it still sits well below the 45-55 agriculture range,
so the gap is narrowed, not closed. Tightening the degeneracy check for short-ngram
repetition and untranslated-English-token runs, and re-testing the 100-phrase
general-vocabulary set against the same expanded bank, are both still open. See
`docs/ekegusii_transfer_learning.md` §22-23 for the full finding.

## Success criterion

**Met**: a working translation demo (Streamlit, live) exists and reliably handles
sample PSAs in its validated domain (Agriculture). Extending that same reliability to
the other 4 domains is explicitly scoped as follow-up work, not silently assumed.
