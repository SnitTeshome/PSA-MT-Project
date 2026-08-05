# Results summary — every metric reported anywhere in this project

Compiled 2026-08-04, after `data/agriculture` caught up to `main`. The group tried
several modeling approaches in parallel across Weeks 3-4, on different languages and
with different metrics — this doc pulls every result into one place so they read as
one collective set of experiments rather than scattered per-person notes. Every
number below traces to a specific doc/script/results file so it can be re-checked
against its source rather than taken on faith.

**Approaches tried, by whoever ran them:**
- Pretrained seq2seq fine-tuning (NLLB-200-distilled-600M zero-shot + mT5-small
  few-shot fine-tune), scored with **BLEU and chrF++** (`sacrebleu`). See
  `docs/week_3_report_model_building.md`.
- NLLB fine-tuning experiments plus a dictionary-prompted LLM approach for
  Ekegusii/Kiswahili/Somali/Dholuo, originally scored with **chrF, recall
  (dictionary content-word coverage), and a degenerate-output rate** — chrF was the
  primary metric for this side of the work since it fits morphologically rich,
  low-resource languages better than BLEU, and recall/degenerate-rate answer
  questions chrF/BLEU can't on their own (did the required content words survive;
  did generation collapse into repetition). See `docs/ekegusii_transfer_learning.md`,
  `docs/week3_performance_summary.md`, `docs/week4_swahili_dholuo_summary.md`.

**Making the numbers comparable**: since BLEU is the metric most readers will
recognize, BLEU was computed retroactively (via `sacrebleu`, same tool both sides
already used) on every saved model output/reference pair from the dictionary-prompted
work, wherever the raw generations were still on disk to score — so the Ekegusii/
cross-domain tables below now carry BLEU alongside chrF, directly comparable to the
mT5/NLLB numbers. Two rows couldn't get a retroactive BLEU score because the raw
generated text wasn't saved anywhere recoverable (marked "not recoverable" below,
not silently left blank).

## Kiswahili (English↔Kiswahili)

| Approach | Setting | BLEU | chrF / chrF++ | Notes |
|---|---|---|---|---|
| mT5-small | few-shot fine-tune, En→Sw | **68.08** | **78.38** | Best BLEU result in the repo; source: `docs/week_3_report_model_building.md` |
| NLLB-200-distilled-600M | zero-shot, En→Sw | 57.73 | 74.71 | |
| NLLB-200-distilled-600M | zero-shot, Sw→En | 46.37 | 67.76 | |
| Cloud translation API | production run, En→Sw | — | **80.7** | 5-domain cross-domain benchmark, 160 rows; best chrF of every backend Bradley tested (`docs/week4_swahili_dholuo_summary.md` §3) |
| NLLB-200-distilled-600M | fallback path, En→Sw | — | 67.7 | Used for the ~31% of the 15,000-row production run the cloud API's quota couldn't cover |
| Qwen2.5 (open model, 32B/72B) | dict-prompted, En→Sw | — | 33.7–39.8 | Clearly the weakest Kiswahili backend tested |

Per-domain mT5 BLEU (En→Sw, few-shot): Security & Safety 75.49, Education
73.60, Agriculture 67.89, Governance 67.14, Health 63.66 — plus a 99-row
leftover "Security" (not "Security & Safety") subset that collapsed to 7.18
BLEU, flagged in the source report as a data/label artifact, not a real
domain-difficulty signal.

Per-epoch mT5 En→Sw BLEU: 42.31 → 66.64 → 68.42 (epochs 1-3).

**Independent corroboration of a shared finding**: a teammate's own separate
fine-tuning attempt (in `Misc/`) found the same catastrophic-forgetting
pattern — BLEU dropped from 75.4 zero-shot to 3.9 after few-shot fine-tuning
on English↔Kiswahili — consistent with the `data/agriculture` conclusion that
fine-tuning underperformed prompting/zero-shot for this project's data scale.

## Ekegusii (English→Ekegusii)

| Approach | Setting | BLEU | chrF++ / chrF | Recall | Degenerate | Notes |
|---|---|---|---|---|---|---|
| mT5-small | few-shot fine-tune | **5.81** | **26.15** | — | — | `docs/week_3_report_model_building.md`; per-epoch BLEU 3.01→4.61→6.43 |
| Fine-tuned NLLB (Option B, best) | terminology-constrained | *not recoverable* | 17.8 | 0.809 | 1/15 | Best fine-tuning result found on the dict-prompt side; raw generations weren't saved to re-score |
| Zero-shot (no dictionary/examples) | baseline, agriculture eval set (52 rows) | 7.13 | ~15–21 | 0.013–0.02 | high | Effectively can't produce real Ekegusii; BLEU computed retroactively via `sacrebleu` on the saved outputs |
| General-purpose LLM API, dict-prompted | agriculture eval set (52 rows) | 28.02 | 49.2 | 0.878 | 1/52 | No morphology hints |
| General-purpose LLM API, dict-prompted + morphology | agriculture eval set (52 rows) | 29.38 | **51.1** | **0.922** | **0/52** | Best result from this backend |
| Qwen2.5-7B-Instruct-AWQ, self-hosted, dict-prompted | agriculture eval set (52 rows) | *not recoverable* | 44.7 | 0.910 | 1/52* | *false positive: correct proper-noun preservation; raw generations weren't saved to re-score |
| Llama 3 70B Instruct, hosted API, dict-prompted | agriculture eval set (52 rows) | **33.96** | **54.8** | 0.904 | **0/52** | Best BLEU and chrF overall; current bulk-job frontrunner |
| Dict-prompted + morphology (production mechanism) | general-vocabulary eval set (100 phrases) | 3.98 (baseline: 1.00) | 31.1 | 1.000 | 0/100 | Cross-domain retest with the 2-bank (agriculture+Bible) retrieval; recall holds, chrF drops vs. agriculture. Not yet re-tested with the 3-bank retrieval below |
| Dict-prompted + morphology, 2-bank retrieval (agriculture+Bible) | cross-domain eval set (60 real sentences, Education/Health/Security/Governance) | 3.32 (baseline: 1.16) | 26.6 | 0.957 | 0/60 | Manual read found real defects (dropped numeric facts, untranslated English jargon) not caught by the automated metric alone |
| Dict-prompted + morphology, 3-bank retrieval (+ 5-domain corpus, 13,497 rows) | same 60-row cross-domain eval set | **14.52** (baseline: 3.41) | **38.6** | 0.881 | 1/60 | +12 chrF / +11.2 BLEU from widening the retrieval bank (`docs/ekegusii_transfer_learning.md` §23) — real improvement, still below the 45-55 agriculture range |

The two 3-bank vs. 2-bank rows above are the fair before/after comparison for the
cross-domain generalization fix; the general-vocabulary row uses a different eval
set (100 short phrases, not full PSA sentences) and still reflects the older 2-bank
retrieval, so it isn't directly comparable to either cross-domain row.

All five backends in the agriculture-domain comparison were scored on the
**same 52 held-out real agriculture PSA sentences with the same scoring
code** — this is the one table above where the numbers are a fair head-to-head. Every
BLEU number in this table (except mT5-small's, already reported that way) was
computed after the fact from the saved model outputs, using the same `sacrebleu`
library the mT5/NLLB work used — same tool, same method, genuinely comparable. The
general-vocabulary and cross-domain rows use different eval sets (noted in each row)
and are not directly comparable to the agriculture row despite sharing a metric.

### Why cross-domain performance varies by domain

The cross-domain row above (chrF 38.6) averages five very different domains
together. Broken out by domain on a single backend (Qwen2.5-72B-Instruct-AWQ,
same 3-bank retrieval mechanism, run on a cloud GPU platform) for the first
time:

| Domain | Real rows in retrieval bank | chrF | BLEU | Recall |
|---|---|---|---|---|
| Agriculture | 1,818 (811 dedicated + 1,007 shared corpus) | **54.0** | **33.1** | 0.849 |
| Health | 1,057 | 52.6 | 27.6 | 0.845 |
| Education | 1,261 | 39.2 | 13.6 | 0.75 (lowest) |
| Security & Safety | 989 | 30.4 | 1.7 | **1.00 (highest)** |
| Governance | 502 (least, by far) | 27.8 (lowest) | 2.4 | 0.857 |

This mechanism doesn't fine-tune, so "training data" here means the real
sentence pairs available to the few-shot retrieval bank at inference time —
more real rows in a domain means better/more relevant examples get
retrieved. The breakdown tells three different stories, not one:

- **Governance** fits the thin-data hypothesis cleanly: the least data by a
  wide margin (502 rows vs. 989-1,261 for every other domain) and the worst
  chrF. A genuine candidate for synthetic-data augmentation of its retrieval
  bank specifically.
- **Education** has more real data than Health and Security yet scores worse
  than Health, so data volume alone doesn't explain it. Its recall is the
  lowest of all five domains (0.75), pointing at a dictionary-coverage gap
  (education-specific terminology underrepresented in the Enchengeria
  dictionary) rather than a data-availability problem. More retrieval
  examples wouldn't fix this directly; better dictionary coverage would.
- **Security & Safety** has perfect recall (1.00 — every dictionary word gets
  found) but the worst BLEU (1.7) and second-worst chrF. Right words, poor
  fluency/structure/grammar — not a data-availability problem at all.

Two data-quality issues surfaced while reading the underlying outputs rather
than trusting the aggregate metric alone. One crossdomain-eval row
(`EDU_798`) has its Ekegusii reference field identical to the English
source — never actually translated — artificially deflating its individual
chrF score; checked across the full 60-row set, this is the only row with
the bug. Separately, 3 of 60 outputs (`HEA_1432`, `SEC_2847`, `GOV_3414`)
contain word patterns that read as possibly a different language rather than
genuine Ekegusii vocabulary — flagged, not confirmed, since judging this
correctly needs native-speaker review, the evaluation gap already named
below.

**If pursuing a fix, don't add synthetic data uniformly across domains.**
Governance is the one case the data actually supports. Education and
Security's weaknesses look like a coverage problem and a fluency problem
respectively, not volume problems — read real outputs by hand before
assuming synthetic data fixes those too.

**Production-scale degenerate-output rate**: after the main bulk translation
job (10,169 rows via a simplified prompt path, see
`docs/ekegusii_transfer_learning.md` §24), 395 rows (3.9%) were flagged
degenerate. A full-dataset re-scan and repair pass fixed 467 of a 482-row
batch (96.9%) using the full dictionary-prompted mechanism; 15 rows remain
honestly flagged rather than force-accepted.

## Somali (English→Somali)

| Approach | chrF | Notes |
|---|---|---|
| NLLB-200-distilled-600M | **83.1** | Winner; 40-row real gold sample from `agriculture_psas.csv`, `scripts/compare_somali_backends.py` |
| Cloud translation API | 65.8 | Same eval set |

Not attempted by the mT5/NLLB modeling work on `main` — NLLB-200 was only
exercised there for English↔Kiswahili and English↔Ekegusii.

## Dholuo (English→Dholuo)

| Approach | chrF | Notes |
|---|---|---|
| NLLB-200-distilled-600M | **53.7** | Unambiguous winner across every backend tested |
| Qwen2.5 (open model, 32B/72B), dict-prompted | fewer repetition loops, +4-7 chrF vs. no-dict | Still not reliably fluent |
| Qwen2.5 (open model, 32B/72B), no dict | 16.0–23.0 | Frequently incoherent — not merely lower quality, often not recognizable as Dholuo at all |

Also not attempted by the `main`-branch modeling work (no Dholuo coverage in
either NLLB-200 or mT5-small runs there).

## What this table does not include

- **The mT5/NLLB numbers above trace to `notebooks/full_pipeline/`**, the
  full-scale run (5 epochs, full dataset) — now executed, with real outputs
  committed alongside it, including a per-domain breakdown, a freeze-vs-full
  fine-tuning ablation, and COMET scores. A separate, lighter run also
  exists in this repo (`notebooks/PSA_Week3_Modeling_TransferLearning44.ipynb`,
  3 epochs on a 4,000-row few-shot subset) with its own, lower numbers on the
  same task — see `notebooks/full_pipeline/README.md` for the side-by-side
  and why they differ. Both are now genuinely reproducible from this repo;
  neither depends on an external, access-controlled notebook anymore.
- **Human/native-speaker evaluation** (fluency, adequacy, cultural accuracy —
  called for in the project's own Week 4 rubric) has not been run by either
  side at scale; both sides substitute targeted manual spot-checks of small
  samples (documented inline in the relevant `docs/` files) rather than a
  scored human-eval pass across 100+ sentences.
- **COMET** (also named in the rubric) is now computed for both approaches.
  Dictionary-prompted: 72.20 (general-vocab) / 67.99 (agriculture) / 59.76
  (crossdomain), all ahead of the fine-tuned models' own COMET scores on a
  0-100 scale — see `notebooks/full_pipeline/results/nllb_comet.csv` and
  `mt5_perdirection_comet.csv` for the fine-tuned side's numbers.
- **A live quality check surfaced a metric/output mismatch** on one
  fine-tuned checkpoint (the mT5 full-finetune English→Ekegusii ablation,
  `notebooks/full_pipeline/results/freeze_vs_full_ablation.csv`): a clean
  12.93 BLEU / 34.99 chrF score, but degenerate repeating output on a live
  demo sample. Same class of issue as the reference-data bug and
  wrong-language-drift flag noted above for the dictionary-prompted side —
  automated metrics alone didn't catch it. Only one sample checked; flagged,
  not yet quantified as widespread.
