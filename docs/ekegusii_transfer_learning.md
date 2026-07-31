# Ekegusii MT via Bantu-language transfer learning

**Course pivot (2026-07-22):** the lecturer has moved the whole class from a per-group
free choice of third target language to **Ekegusii** specifically. This doc replaces
Somali-choice planning (`data/SOMALI_SOURCES.md`, now marked superseded) with grounded
research on transfer-learning strategies for Ekegusii, since Ekegusii has **zero**
coverage in NLLB-200/FLORES-200, mT5, or mBART-50 (confirmed in Week 2 prep, unchanged).

## 1. Bantu-language coverage in existing MT/NLP resources

NLLB-200/FLORES-200 cover roughly 20 Bantu languages: `swh` (Swahili), `kin`
(Kinyarwanda), `run` (Kirundi), `lug` (Luganda), `sna` (Shona), `zul` (Zulu), `xho`
(Xhosa), `nya` (Chichewa/Nyanja), `nso`/`sot`/`tsn`/`tso`/`ssw` (Sotho-Tswana-Tsonga-Swati
group), `lin` (Lingala), `kon` (Kikongo), `umb` (Umbundu), `kmb` (Kimbundu), `bem`
(Bemba), `cjk` (Chokwe), `tum` (Tumbuka). **Gusii (`guz`) is absent.**
([FLORES-200 README](https://github.com/facebookresearch/flores/blob/main/flores200/README.md))

Swahili is the best-resourced of these and the standing recommendation as a transfer
bridge — but this is a **resourcing/typology-of-convenience** argument, not close genetic
kinship: Swahili is Bantu zone G40 (Sabaki), Gusii is zone JE42. Gusii's actual closest
relatives (Kikuyu, Kamba, Luhya) have essentially no MT resources either. The shared
value is the general Bantu inventory — agglutinative verb morphology, noun-class
prefixes — not close subgroup relationship.
([NLLB paper](https://arxiv.org/pdf/2207.04672))

Multilingual African LMs: **AfriBERTa** (11 languages) includes only Swahili and
"Gahuza" (Kinyarwanda+Kirundi mix) as Bantu. **AfroXLMR** (20-61 languages) likely
includes several Bantu languages (Swahili, Kinyarwanda, Shona, Xhosa, Zulu) but `guz`
coverage is unconfirmed. **Serengeti/Cheetah** claim up to 517 African languages/varieties
for pretraining, which raises the possibility Gusii text was swept in, but this is
unconfirmed from the paper/model card — don't assume it without checking directly.
([AfroXLMR](https://arxiv.org/pdf/2204.06487), [Serengeti](https://arxiv.org/abs/2212.10785))

## 2. Documented transfer-learning methods for low-resource Bantu MT (with actual numbers)

**Fine-tuning a multilingual pretrained MT model on small in-domain parallel data** is
the best-evidenced method. Masakhane's MAFAND-MT (NAACL 2022) fine-tuned M2M-100 (418M),
mBART50, mT5/AfriMT5, ByT5/AfriByT5 on **1,466-7,838 news sentence pairs per language**,
3 epochs (10 for news-only), batch size 10, lr 5e-5. Reported BLEU (M2M-100, fine-tuned
vs. zero-shot): en→lug 0.8→14.3, lug→en 3.7→20.0; en→tsn 1.1→24.7, tsn→en 3.3→20.0;
en→zul 5.6→21.0; en→swa 20.1→26.7. This is the single most relevant precedent for our
data scale (4,816 pairs sits mid-range of their 1.4k-7.8k).
([arXiv:2205.02022](https://arxiv.org/abs/2205.02022))

**Joint training among closely-related languages** beat single-pair baselines
substantially: joint English-isiXhosa-isiZulu training reached **BLEU 18.6±1.0 for
en→zul, +9.9 BLEU over the single-pair baseline.**
([arXiv:2104.00366](https://arxiv.org/pdf/2104.00366))

**Swahili pivot translation** is discussed in the literature as "technically viable" for
Bantu targets but no published BLEU number was found for a Swahili-pivoted system
specifically — plausible, not a scored method.

**Rule-based interlingua transfer exploiting shared Bantu morphology — done specifically
for Ekegusii.** Ombui, Wagacha & Ng'ang'a (2014) built an InterlinguaPlus Ekegusii↔Swahili
system storing shared base forms plus separate affix tables, explicitly exploiting
Bantu noun-class/agglutination overlap. Reported **>50% accuracy on general domain, ~90%
on a narrow domain (obituaries)**. Note: rule-based accuracy, not BLEU/chrF, so not
directly comparable to neural benchmarks below — but it's the only concrete prior
evidence that Ekegusii-Swahili shared morphology is exploitable, **and it's worth noting
this is prior work by this course's own lecturer** (same surname as our Ekegusii Corpus
source), which likely explains the pivot to Ekegusii specifically.
([ACL Anthology W14-2209](https://aclanthology.org/W14-2209/))

**Few-shot LLM prompting**: mixed, modest results for Kinyarwanda/Hausa/Luganda in the
literature; no number found for a language at Ekegusii's near-zero pretraining-exposure
level — extrapolating a score here would be invented, not found.

**Back-translation** with a related-language model is a general strategy in the
literature; no Bantu-specific BLEU delta attributable to it alone was found.

## 3. Masakhane / MAFAND-MT scope check

16 languages: Bambara, Ghomala, Ewe, Fon, Hausa, Igbo, Kinyarwanda, Luganda, Dholuo
(Nilotic, not Bantu), Mossi, Chichewa/Nyanja, Nigerian-Pidgin, Setswana, Twi, Wolof, and
Zulu and/or Xhosa. **No Kenyan Bantu language, and no Gusii or Gusii-adjacent language,
is in scope.** Dholuo is the only Kenyan language covered and it's Nilotic — unrelated to
Ekegusii's Bantu morphology, so it isn't a usable precedent for Ekegusii specifically
despite being "Kenyan." ([arXiv:2205.02022](https://arxiv.org/abs/2205.02022))

## 4. Practical recommendation for this project

Given 4,816 English-Ekegusii PSA pairs (`data/raw/agriculture/_candidates_ekegusii_corpus.csv`
plus whatever Health/Education/Security/Governance domains collect) plus a ~56k-word
monolingual Ekegusii corpus, on CPU only, in 3-4 weeks:

- **Primary approach**: fine-tune `facebook/nllb-200-distilled-600M` (CPU-tractable) by
  adding Ekegusii as a new language tag, initializing its embedding from Swahili's
  (`swh_Latn`) token/embedding, then fine-tuning on the collected pairs for a handful of
  epochs (mirroring MAFAND-MT's 3-10 epoch regime). This directly operationalizes the
  shared-Bantu-morphology premise the 2014 InterlinguaPlus result already validated
  informally.
- **Secondary/comparison baseline**: fine-tune mT5-small directly on the same data (as
  MAFAND-MT did for their smallest-model comparisons); optionally a naive few-shot
  LLM-prompting baseline for contrast, treated as a weak baseline only since no evidence
  supports strong few-shot performance on a totally unseen language.
- Use the monolingual corpus for tokenizer/vocabulary augmentation (Ekegusii-specific
  subwords) rather than expecting it to support meaningful back-translation at only ~56k
  words.

**Realistic score range — honestly caveated**: no published BLEU/chrF exists for
Ekegusii itself. Extrapolating from MAFAND-MT's comparable-scale results for languages
*already present* in the pretrained model (en→lug 14.3, en→tsn 24.7, en→zul 21.0 BLEU),
adjusted down for Ekegusii's zero pretraining exposure, a defensible planning range is
**BLEU 8-18 / chrF 25-40 for English→Ekegusii**, with Ekegusii→English likely a few
points higher (the xx→en pattern held consistently in MAFAND-MT). Report this as an
estimate grounded in analogous published results, not a guaranteed outcome.

## 5. Closest Bantu relatives to Gusii, and what NLP resources exist for them

Guthrie classification: Gusii is **JE.42**, and its closest relative by that classification
is **Kuria (JE.43)** — both sit in the **Mara group** of East Nyanza/Great Lakes Bantu,
alongside **Logooli (E.41, part of the Luhya cluster)** and **Suba (JE.403)**, with mutual
intelligibility reported to varying degrees across this cluster. This is standard
reference-classification information (Guthrie/Maho system), not something the academic
literature search below independently surfaced — "Kuria" did not appear once across three
targeted searches, so treat the Kuria/Logooli/Suba grouping as reliable-but-not-separately-
peer-reviewed-here, and verify against Glottolog/Ethnologue directly before citing it as a
load-bearing claim in the final report.

**What NLP resources actually exist for this cluster: thin, but not zero.** No paper found
covers Kuria or Suba specifically. The one concrete hit is **Kencorpus** (Wanjala et al.,
described in Nakatumba-Nabende et al. 2024, *Applied AI Letters* 5(2), DOI 10.1002/ail2.92) —
a Kenyan corpus with Dholuo↔Swahili **and Luhya↔Swahili** parallel text, plus POS-tagging/QA
data. Since Logooli is a Luhya-cluster language and one of Gusii's closer relatives, this is
the nearest thing to an actual NLP resource for a Gusii-adjacent language found so far — worth
checking directly whether Kencorpus's specific Luhya variety is Logooli, since "Luhya" itself
spans ~14 dialects. No second rule-based/interlingua Bantu MT system beyond the 2014 Ombui et
al. paper (§2 above) was found; useful *linguistic* (not MT) background on Bantu noun-class/
verbal morphology if the embedding-seeding approach in §4 needs refining: Salzmann (2011, DOI
10.1111/j.1749-818X.2011.00270.x, noun-class/locative-inversion typology), Gibson (2018, DOI
10.1111/1467-968X.12136, formal model of Bantu verbal morphology), Diercks (2011, DOI
10.1111/j.1467-9612.2011.00165.x, Lubukusu/Luhya infinitive-doubling data).

## 6. Bible/scripture text as an additional Ekegusii parallel-data source

Ekegusii has a full published Bible translation, **"Ebibilia Enchenu"** (Bible Society of
Kenya, revised 2020/2021), with translation work going back to 1929 (Gospel of Matthew,
Seventh-Day Adventist Mission). Verified directly (not just literature-inferred) across
multiple official channels:

- **Rosetta Project / Internet Archive** (`archive.org/details/rosettaproject_guz_gen-1`) —
  Genesis in Ekegusii, full text/EPUB/PDF, from the Long Now Foundation's language-archive
  project (published by United Bible Societies, 1990) — built specifically to enable this
  kind of computational/comparative reuse, no extraction of any kind needed.
- **ScriptureEarth.org** (SIL) aggregates seven official Ekegusii resources: Bible.is
  (text+audio+video streaming), eBible.org, YouVersion, Global Recordings Network, the JESUS
  Film.
- **find.bible/bibles/GUZGUZ** — a Genesis-only PDF is a direct ~255KB download; the full New
  Testament is a 2.16MB scanned PDF via The Bible Archive.

**No explicit open-reuse license was found on any of these pages** — Bible Society of Kenya
holds copyright. Treat this the same way this project already treats other externally-sourced
reference material: fine for research/coursework use with proper citation, not a green light
for bulk redistribution without checking terms first.

**Why a same-publisher bilingual bundle isn't necessary**: Bible text is universally
verse-numbered (book:chapter:verse), so any English translation (KJV is public domain) aligns
automatically against any Ekegusii translation by verse ID, with no need for both to come from
one publisher. This is exactly how the one directly comparable precedent in the literature did
it — **Adjeisah, Liu, Nyabuga, Nortey, Song & Yuan (2021)**, "Pseudotext Injection and Advance
Filtering of Low-Resource Corpus for Neural Machine Translation," *Computational Intelligence
and Neuroscience* 2021, DOI 10.1155/2021/6682385 — built English-Twi MT from 4 English Bible
versions × 2 Twi versions aligned purely by verse number (124,400 pairs from YouVersion), then
supplemented with OPUS's JW300 monolingual Twi text for backtranslation augmentation, reaching
BLEU ~18-19 both directions.

**Honest caveat on domain mismatch.** Bible register (formal/archaic) is a poor match for PSA
register (short, directive, contemporary public-advisory). The more recent mainstream
African-NLP corpus efforts (Masakhane, Kencorpus, Sunbird AI, AI4D) have moved toward
newly-collected civic/news-domain text rather than religious corpora — no single source states
this is *because* of domain mismatch, but the pattern is suggestive. Recommendation if this is
pursued: treat Bible-derived Ekegusii text as (a) tokenizer/vocabulary augmentation, alongside
the existing 56k-word monolingual corpus, or (b) a data-augmentation supplement mixed with real
PSA rows — not a substitute for genuine PSA-domain parallel text, and expect some of the same
register-mismatch risk already documented for the CSA-paraphrase cluster elsewhere in this
project. **Do not pursue this via unofficial APK extraction from an Android Bible app** — the
official channels above provide the identical text with far less risk (no unverified binary,
no reverse-engineering an app's bundled assets instead of using content the publisher already
distributes for this exact kind of reuse).

**Update (2026-07-28, later same session): the full New Testament was fetched and aligned,
no OCR needed.** The `find.bible/bibles/GUZGUZ/` New Testament PDF (`archive.org/download/
GUZGUZ_DBS_HS/...`, 2.16MB) turned out to have a real embedded text layer, not a bare scan —
confirmed with PyMuPDF before reaching for `tesseract`. Parsed into 27 books / 260 chapters /
7,932 verses, then aligned by verse ID against the public-domain KJV (`aruljohn/Bible-kjv`)
to produce **7,930 clean English-Ekegusii parallel verse pairs** — exactly the
verse-ID-alignment method this section recommended, now actually executed. Full detail,
data-quality caveats (16 minor parsing anomalies, 0.2%), and file locations:
`NLP/Data/EkegusiiCorpus/bible_alt_sources/README.md`. YouVersion scraping was evaluated and
deliberately not pursued — the PDF route already yielded the complete NT at higher (born-digital)
quality than scraping the same underlying translation would add. The register-mismatch caveat
above still applies in full: this is tokenizer/augmentation material, not a PSA-domain
substitute, and has not been merged into `agriculture_psas.csv`.

## 7. Implementation status (2026-07-28)

The tag-seeding mechanism in §4 (add `guz_Latn`, resize embeddings, copy `swh_Latn`'s row) is
now verified working end-to-end on CPU: before any fine-tuning, the seeded tag produces a
correct Swahili translation when asked to generate — confirming the "warm start" premise this
whole approach depends on. A fine-tuning script (`scripts/finetune_nllb_ekegusii.py`), a
provenance-stratified split builder (`scripts/build_splits.py` — see the circular-evaluation
risk this exists to guard against, in the workspace's `project_psa_mt_week3_prep` notes), and
an environment dispatcher (`scripts/runtime.py`) all exist and have been exercised against the
real dataset.

**Full-parameter fine-tuning of the 600M model needs a real GPU** — confirmed by attempting it
locally: AdamW's optimizer state for all parameters exceeds available memory. The natural next
idea, freezing everything except the embedding/output layer, was tried and *also* failed
locally, for a reason specific to this model: NLLB-200's vocabulary spans 200 languages (256k
tokens), so its embedding matrix alone is ~262M of the 600M parameters (~44%) — "freeze
everything but the embedding" barely reduces the trainable footprint here. **LoRA** (Hu et al.
2021, "LoRA: Low-Rank Adaptation of Large Language Models," https://arxiv.org/abs/2106.09685)
— small low-rank adapters on the attention projections, base weights (including the huge
embedding table) fully frozen — sidesteps this: confirmed locally with only 1.18M of 616M
parameters trainable (0.19%), a full smoke-scale training step completing in under 10 seconds
where the other two approaches both failed. This is also the standard published technique for
adapting a large pretrained MT model to a low-resource language, not a workaround specific to
this project's development environment. All three modes (`lora` / `freeze_embed` / `full`) are
selectable in `scripts/finetune_nllb_ekegusii.py`, so `lora` vs `full` becomes a natural
additional ablation once real GPU compute is available — no result exists yet for that
comparison, and none should be assumed until it's actually run.

**Real remote-GPU run completed 2026-07-28 — mechanically successful, translation quality
not yet there, and a real architectural reason why.** `kernel_finetune.py` (LoRA on
`q_proj`/`v_proj` only) ran end-to-end on the full 811 train / 75 val split, 6 epochs:
`train_loss` 6.43 (down from 8.11 at the 2-step smoke scale), `train_runtime` 231.9s,
20.99 samples/sec, on a Tesla P100 (the scheduler assigned P100 again despite requesting T4 — the
already-known quirk). **But the post-training sample translation is still essentially
fluent Swahili, not Ekegusii** — for "Announcement of expansion plan sourcing school meals
from local farmers while integrating climate-resilient crops," the `guz_Latn`-tagged output
("Tangazo la mpango wa upanuzi wa kupata chakula...") is nearly word-for-word identical to
the *smoke test's* pre-trained-scale output, differing only in one word choice
(`kupata`/`kununua`, both "obtain"). 492 real gradient steps produced almost no lexical
shift away from the Swahili seed.

**Root cause, reasoned from the architecture, not just observed as a mystery**: LoRA with
`target_modules=["q_proj", "v_proj"]` and no `modules_to_save` leaves the embedding table
and output projection **fully frozen** after `add_ekegusii_tag()`'s one-time copy of
`swh_Latn`'s row into the new `guz_Latn` slot. Attention-only LoRA can reweight *how* the
model attends, but the actual lexical identity of the new tag — which token probabilities
the decoder assigns per position — lives in the (frozen) embedding/LM-head weights, which
never move from their Swahili-seeded values. This is architecturally why the tag stays
Swahili-shaped regardless of how many attention-only gradient steps run: **there is
currently no trainable path for the new tag's lexical realization to diverge from its seed**.
Note: an earlier reading of the kernel log took a PEFT warning to mean
`tie_word_embeddings=False` for this checkpoint. **Corrected 2026-07-28, verified by loading
the checkpoint directly**: `config.tie_word_embeddings` is actually `True`, and
`lm_head.weight` is the literal same `nn.Parameter` object as the input embedding's weight
(confirmed via `is` identity check, not just value equality). The practical conclusion is
unchanged either way — the embedding *and* the LM head both need to become trainable, not
just one — but the mechanical reason differs: it's not that they're separately-initialized
matrices, it's that any `modules_to_save`-style wrapping breaks the live Python object tie for
whichever reference isn't itself wrapped, orphaning it as a frozen copy of the pre-fix
weights. See the corrected fix below.

**Practical implication for the next run, not yet attempted**: `freeze_embed` mode
(previously ruled out for *local* use only, because NLLB's 256k-token embedding table
optimizer state — ~262M params × ~4 bytes/param × 4 for AdamW moments ≈ 4.2GB — exceeded
this container's 9GB CPU cgroup) may well fit comfortably within the remote GPU's 16-17GB,
where this run's own memory probe showed only 6.49GB peak used by the much smaller
LoRA-on-attention configuration. Worth trying `--mode freeze_embed` (or extending LoRA's
`modules_to_save` to include `embed_tokens`/the LM head) as the next ablation specifically
*because* the diagnosis above points at embeddings, not attention, as where this tag's
learning actually needs to happen — this is a targeted hypothesis to test, not a repeat of
the already-ruled-out local attempt.

**Diagnosis sharpened further, 2026-07-28 (same day), while building the dictionary
knowledgebase (§9)**: this isn't just "unfreezing embeddings would help quality" — it's
architecturally necessary for the tag mechanism to work *at all*. NLLB-200 shares one
subword vocabulary across all 200 languages; individual content-word tokens are not
per-language. The only signal distinguishing "translate to `guz_Latn`" from "translate to
`swh_Latn`" is the language tag's own embedding row, which `add_ekegusii_tag()` copies
byte-for-byte from `swh_Latn` and LoRA (`q_proj`/`v_proj` only) never touches. **The two
tags are therefore mathematically identical inputs to every downstream layer** — there is
no signal difference for attention-only adaptation to key off of, regardless of gradient
steps run.

**Fix implemented and verified locally, 2026-07-28 (same day, later session)**: not
`modules_to_save=["embed_tokens", "lm_head"]` as first proposed — that deep-copies the
*entire* 256k-row embedding table independently at each wrapped location (~1GB × 3 ≈ 3GB)
and OOM-killed this container's 9GB CPU cgroup on a plain forward+backward smoke test.
Investigating why led to a better-targeted fix: PEFT's `trainable_token_indices` mechanism
trains a small per-row delta for specified token indices only, instead of copying the whole
table. Empirically confirmed post-`resize_token_embeddings()`: `model.model.shared`,
`encoder.embed_tokens`, and `decoder.embed_tokens` are the literal same Python object (`is`
returns `True`), and `lm_head.weight is shared.weight` also holds. The working config is:
```python
LoraConfig(
    ..., target_modules=["q_proj", "v_proj"],
    trainable_token_indices={"shared": [new_id], "lm_head": [new_id]},
    ensure_weight_tying=True,
)
```
Verified end-to-end on CPU with the real checkpoint and real tokenizer: `named_parameters()`
shows exactly **one** deduplicated 1024-dim `trainable_tokens_delta` (proving the tie held
across all 4 wrapped locations — shared, encoder, decoder, lm_head — rather than diverging
into independent copies), and a real forward+backward pass produced a nonzero gradient on it
(abs-sum ≈ 28.6). This is the smallest correct fix: only the new tag's row becomes trainable,
the other 256k rows (199 other languages) stay frozen, avoiding both the OOM and any
unnecessary catastrophic-forgetting risk to the pretrained model's other languages. Applied
in `kernel_finetune.py`'s `apply_lora()`; not yet run on real a cloud GPU notebook with this exact
script (`SMOKE=True` staged first, per the project's standard iterate-before-committing
discipline).

## 8. Vocabulary/register comparison: Bible corpus vs. PSA domain corpus (2026-07-28)

Prompted by a direct question — do the Bible and PSA Ekegusii corpora share word meanings,
or does the same word mean different things in each register, and has this exact problem
(combining a Bible-derived corpus with a different-domain corpus for low-resource MT) been
solved before? Both a literature search and a real computational comparison were done rather
than reasoning from first principles.

### 8.1 Prior art (Scholar Gateway + web search)

**Directly on point**: Marashian, Rice, Gessler, Palmer & von der Wense (2025), "From Priest
to Doctor: Domain Adaptation for Low-Resource Neural Machine Translation," COLING 2025
(arXiv:2412.00966) — the closest published analogue to this exact problem. Starting from
*only* Bible parallel data + a bilingual dictionary + monolingual target-domain text (no
in-domain parallel data at all, a harder starting position than ours), their best method
(**DALI**, adapted from Hu et al. 2019) builds a dictionary from the ~5,000 most frequent
target-domain lemmas, forward-translates monolingual target-domain text word-by-word through
that dictionary to make pseudo-parallel data, then trains on Bible + pseudo-parallel data
together. Concrete result: government-domain BLEU 0.85→5.76 (ChrF 18.97→39.66), medical-domain
BLEU 1.29→13.47 (ChrF 18.28→42.47). They explicitly report the register-leakage failure mode
we'd expect: outputs "translate in a religious tone" even after adaptation.

**Reassuring for our specific situation**: González Servín, Maldonado Sifuentes, Kolesnicova &
Sidorov (2026), "Evaluating the Impact of Domain Adaptation on Transformer-based Models for
Low-Resource Purépecha-Spanish Translation," IJCoPI 17(2):27-37 (DOI
10.61467/2007.1558.2026.v17i2.1265) — pretrains on a Bible corpus, then fine-tunes on a small
(1,297-pair) out-of-domain set. Zero-shot Bible-only transfer to the new domain was
near-useless (BLEU 0.23-1.99), but fine-tuning on the small in-domain set alone lifted BLEU to
21-29. **This validates the plan already in place here**: we're not in the "Bible-only" harder
case those two papers start from — we already have 961 real PSA rows to fine-tune on — so the
Bible corpus's job is narrower (vocabulary/tokenizer augmentation, not the primary training
signal), and the Purépecha result suggests genuine in-domain fine-tuning (already the plan,
via `finetune_nllb_ekegusii.py`) should dominate any register skew from Bible-derived data,
provided it comes *after* the Bible-derived pretraining, not mixed in undifferentiated.

**A concrete filtering technique worth reusing**: Adjeisah, Liu, Nyabuga, Nortey, Song & Yuan
(2021) (already cited above) filtered Bible-derived pseudo-parallel English-Twi pairs by
squared Mahalanobis distance and round-trip-translation similarity before injecting them into
training — the same discipline this project's own `translate_and_qa.py` round-trip-scoring
already applies to its own synthetic data, so this is a validation of an approach already in
use here, not a new one to adopt.

**Sense-shift detection (general technique, not Bible-specific)**: the standard approach for
"does word X mean something different in corpus A vs. corpus B" is diachronic/cross-domain
embeddings — train a small word-embedding space per corpus, then compare a shared word's
nearest neighbours across the two spaces (Hamilton, Leskovec & Jurafsky 2016; surveyed in
Kutuzov, Øvrelid, Oepen & Velldal 2018, ACL C18-1117). Not run here (corpora are small enough
that direct concordance reading, §8.3, was more informative per word actually checked), but
worth doing properly if this scales to checking hundreds of shared words rather than a
hand-picked handful.

**JW300 status, confirmed**: pulled from OPUS after a 2023 legal audit found jw.org's terms
prohibit text/data mining; JW (the copyright holder) denied Masakhane's continued-use request.
Irrelevant to us directly (`Ebibilia Enchenu` was sourced directly from Internet Archive /
find.bible, not JW300) but worth knowing given how often JW300 shows up in this literature.

### 8.2 Computational vocabulary comparison (real numbers, not estimated)

Compared `psa_en_guz_parallel.csv`'s Ekegusii column (4,816 real PSA sentences — the
lecturer-provided Ekegusii Corpus before promotion/dedup into `agriculture_psas.csv`, chosen
because it's the cleanest single-register PSA sample) against
`bible_alt_sources/ekegusii_kjv_aligned.csv`'s 7,930 NT verses:

- **Vocabulary size**: PSA 15,097 unique word types over 93,677 tokens; Bible 18,954 types
  over 113,955 tokens.
- **Overlap is small in vocabulary, large in running text — the classic Zipfian split**: only
  2,099 word types (~14% of either vocabulary) are shared, but those shared types cover
  ~51-54% of each corpus's *running text* (token-weighted). In other words: grammar/function
  words overlap heavily, content words diverge sharply — confirming the register gap is
  concentrated in vocabulary, not grammar, which is exactly where a Bible-pretrained
  tokenizer would actually help (subword coverage of shared morphology) without necessarily
  teaching wrong content-word associations.
- **Bible-only top words are almost entirely proper nouns and religious register**: `nyasaye`
  (God, 1,386), `yesu` (Jesus, 956), `kristo` (Christ, 558), `tata` (Father, 245), `paulo`,
  `petero`, `yohana`, `yerusalemu`, `hekalu` (temple) — none of which have any PSA-domain use.
- **PSA-only top words are exactly the "worldly"/modern vocabulary the Bible corpus
  categorically lacks**: `oboremi` (agriculture, 603), `chisukuru` (schools, 308), `amasomo`
  (education, 285), `abarimu` (teachers, 153), `eserikari` (government, 127), `eminisitiri`
  (ministry, 104), `engencho` (a GBV/gender-context term, 122, **zero occurrences anywhere in
  the 7,930-verse Bible corpus**) — direct, quantified confirmation of the hypothesis that the
  Bible corpus can't cover modern civic/institutional vocabulary, not just a plausible guess.
- **Sentence structure**: PSA sentences average 19.5 words vs. Bible's 14.4 — PSA messages
  pack more clauses per sentence (advisory framing: condition + action + reminder in one
  message); type-token ratio is similar in both (~0.16), so this isn't a difference in lexical
  richness per se, just in structure and topic.

### 8.3 Shared words with different senses by register — the concrete "what can mean what" evidence

Concordance-checked a handful of frequent shared content words directly (not just counted):

- **`obonda`** — a genuine, risky polysemy. PSA: "resources/assets" (`obonda bwa motwe` =
  "capital resources," `obonda bwoboremi` = "agricultural resources"). Bible: "kingdom"
  (`obonda bw'igoro` = "the kingdom of heaven," used dozens of times). These are essentially
  unrelated senses sharing one word form — a model trained on mixed Bible+PSA data without any
  disambiguating signal risks generating "kingdom" where "resources" was meant, or vice versa.
- **`omonene`** — a milder version of the same pattern. PSA: modifies political/institutional
  titles (`omogambi omonene` = "Deputy President," i.e. "senior/principal"). Bible: a standalone
  divine honorific, "the LORD" (`Omonene`, capitalized). Same core sense ("great/senior one")
  but the referent-class is register-specific (civic official vs. God) — less risky than
  `obonda` since the surrounding context (a name/title vs. a sentence about God) strongly
  disambiguates, but still a real associative bias a small fine-tune might not fully correct.
- **`omonto`** — a stable control case: "person/man" in both registers with no real sense
  shift (PSA: "kera omonto" = "every person"; Bible: "omonto oboronge" = "a just man"). Useful
  as a reminder that not every shared word is a landmine — most of the 2,099 shared types are
  probably like this, not like `obonda`.
- **`abanto`** — mostly stable ("people"), but PSA has a domain-specific idiomatic extension
  not seen in the Bible sample: `abanto abanene` ("big/grown people") = "adults" (as in adult
  literacy programmes) — an idiom a Bible-only model would have no reason to have learned.

### 8.4 Morphology and discourse-marker differences (computational, not hand-coded rules)

Word-initial trigram frequency (a cheap, rule-free proxy for prefix/morpheme distribution)
surfaced two real, sizeable differences, both consistent with the two corpora's genres:

- **`aka-` (narrative past-tense marker): 2.52% of Bible word-initial trigrams vs. 0.05% of
  PSA's.** Matches the Bible-only word list directly — `akabatebia` ("he told them"),
  `akamotebia` ("he told him/her"), `akagenda` ("he went"), `akabora` ("he said") are exactly
  the 3rd-person past-tense narrative forms that dominate Biblical storytelling prose. PSA
  text is overwhelmingly imperative/advisory, not narrative, so this tense form is almost
  absent there.
- **Discourse connectives skew hard in both directions**: `korende` ("but/however") and
  `naki` ("for/because") appear at Bible-rates of 1,488 and 1,141 vs. PSA's 61 and 3
  respectively — narrative prose leans on contrastive/causal connectives. `nigo` (a
  therefore/imperative-framing marker) runs the other way: 590 in PSA vs. 37 in Bible — advisory
  PSA text leans on directive framing markers narrative prose doesn't need.
- **An orthographic-register difference, not just lexical**: the elided contraction form
  `as'` (e.g. `as'ense` = "in the land/earth") accounts for 4.51% of Bible word-initial
  trigrams but **0%** in PSA, where the same preposition is written out in full as `ase`
  instead. This suggests the professionally-typeset 1990 Bible translation applies traditional
  Ekegusii elision orthography more consistently than the PSA corpus's translators did — a
  genuinely useful thing for a tokenizer to see more of, independent of the content-word
  mismatch above.

### 8.5 Practical takeaway

All of this is consistent with the plan already in `docs/ekegusii_transfer_learning.md` §6 and
`bible_alt_sources/README.md`: use the Bible corpus for **tokenizer/subword vocabulary
coverage and general Bantu morphology exposure**, not as undifferentiated extra training data
mixed in with PSA rows — the `obonda`/`omonene` sense-shift risk is real and quantified, not
hypothetical, and the Purépecha precedent (§8.1) suggests the planned in-domain LoRA fine-tune
on real PSA data should be enough to override any register skew, provided Bible-derived data
(if used for training at all) precedes rather than randomly interleaves with the PSA
fine-tuning stage. No code changes made as a result of this analysis — it's a documented
caution for whoever runs the next ablation, not an action taken.

## 9. Ekegusii dictionary knowledgebase (2026-07-28, same day)

Full build: dictionary source/access, parser methodology + honest limitations,
EN↔GUZ lexicon extraction, tokenizer-fragmentation check, dictionary-substitution
augmentation attempt (weak result, reported honestly), and the root-family morphology
diagnostic set are all documented in
`NLP/Project/ekegusii_internal/dictionaries/README.md` (kept private — paid/copyrighted
commercial dictionaries, not for redistribution). Summary of what's there: 4,040
Enchengeria headwords / 5,204 total word forms parsed and POS-tagged from the dictionary's
own printed abbreviation key; cross-referenced against this doc's §8 corpus comparison
(confirmed `oboremi`="Farming," refined `omonene` as one core sense not two, confirmed
`obonda` is genuinely absent from the dictionary); found that root-stripped coverage of
the PSA/Bible corpora roughly doubles exact-match coverage (the concrete version of the
"blunt tool" argument); DALI-style monolingual augmentation attempt yielded low coverage
(10-16%), reported as a real limitation not a success.

## 10. Corpus-correctness re-check against the CURRENT training splits (2026-07-29)

§9's dictionary-coverage numbers (3.3%/6.9% surface/root-stripped type coverage) were run
against `psa_en_guz_parallel.csv` — the raw, pre-dedup 4,816-sentence lecturer file — not
the actual 961-row corpus (`ekegusii_train/val/test.csv`) `kernel_finetune.py` trains on.
Re-ran the same dictionary-coverage method directly against the current training splits to
check whether the earlier finding still holds on the file that actually matters:

**Current corpus (961 real rows, 3,690 word types, 22,014 tokens) vs. the Enchengeria
dictionary**: surface-match 6.7% of types / 28.6% of running text; root-stripped 12.0% of
types / 35.6% of running text — **roughly double** §9's numbers on the raw pre-dedup file.
Makes sense: the curated/QA-filtered (`qa_roundtrip` score in each row's `Metadata` column)
961-row set is smaller and more repetitive than the raw 4,816-sentence file, so its
vocabulary concentrates on higher-frequency, better-attested words.

**Spot-checked the top-60 most frequent words still uncovered even after root-stripping —
not garbled, just outside the dictionary's scope**: `igoro` ("heaven/above") and `nigo`
(the directive/therefore marker) are both already independently confirmed real Ekegusii by
§8.3/§8.4's separate corpus analysis, just not dictionary headwords. `kenya` and `csa`
(Climate-Smart Agriculture, a real English acronym used as-is in Ekegusii PSA text) are a
proper noun and a code-switched acronym respectively — no bilingual dictionary would list
either. The rest (`bwa`, `gose`, `as`, `bwao`) are short function words/linkers, which
general-purpose dictionaries systematically under-list in every language. **No evidence the
corpus's actual Ekegusii is wrong** — the coverage gap is the dictionary's traditional-register
scope (no PSA-specific civic/agricultural vocabulary, no function words, no proper
nouns/acronyms as headwords), not corpus error, consistent with §8's finding that PSA's
"worldly"/modern vocabulary is exactly what a general dictionary (or the Bible) lacks.

**On whether this means training should extend beyond agri-PSA (question raised
2026-07-29)**: the evidence already in this document argues for caution, not expansion,
despite the corpus itself checking out as legitimate:
- Bible corpus: §8.3 already found a genuine, quantified sense-collision risk
  (`obonda` = "resources" in PSA vs. "kingdom" in Bible — not a stylistic register
  difference, an outright different meaning for the same surface form). §8.5's standing
  recommendation — Bible for tokenizer/subword coverage only, or as a pretraining stage
  strictly *before* PSA fine-tuning, never blended/interleaved — still holds and is not
  contradicted by today's re-check.
- Dictionary-based (DALI-style) augmentation: §9 already tried this and got a weak result
  (10.2%/16.4% exact/root-stripped per-sentence coverage on unrelated monolingual text,
  only 52 of 3,880 sentences usable) — not a meaningful lever for expanding real training
  pairs right now.
- The actual blocker on translation quality was never data breadth — it was mechanical:
  §7's embedding/LoRA fix (now implemented, `trainable_token_indices` on the tag row) is
  what makes the model capable of learning *anything* Ekegusii-specific at all. Expanding
  domain coverage before confirming that fix works is solving the wrong problem first.

**Recommendation**: don't extend training data scope yet. Get a clean signal from the fixed
`kernel_finetune.py` on the existing 811/75/75 agri-PSA split first (a cloud GPU notebook service kernel v7 smoke
run in progress as of this note) — only after confirming the tag can learn *something*
does it make sense to ask whether broader domain coverage would help it learn *better*.

## 11. Real full run with the fix (kernel v8, 2026-07-29) — mechanism confirmed, output still unchanged

**Kernel v7 (SMOKE=True)** ran clean on real a cloud GPU notebook (Tesla P100 again): trainable
params 1,180,672/616M (0.19%, matches the local verification exactly), `grad_norm`
nonzero and moving across the 2 smoke steps (0.4214 → 0.5999), no errors.

**Kernel v8 (SMOKE=False, real 811-row/6-epoch run) — genuine training happened, but
the decoded sample output did not change.** `grad_norm` stayed consistently in the
0.4-0.6 range for all 492 steps (real gradient flow throughout, not a fluke), and
`eval_loss` decreased monotonically every epoch: 6.878 → 6.43 → 6.158 → 5.97 → 5.864 →
5.834 (final `train_loss` 6.411). **But the post-training sample translation is
essentially unchanged from the pre-fix v6 run** — same English input, same
near-identical Swahili output ("Tangazo la mpango wa upanuzi wa kupata chakula cha
shule kutoka kwa wakulima wa ndani..."), same word choice (`kupata`) as v6's run.

**Honest interpretation, per this doc's own standing instruction not to declare victory
on loss curves alone**: the embedding fix was *necessary* (it removed a structural
impossibility — the tag literally could not move before) but is not, on its own, at
this scale, *sufficient* to produce visibly different decoded output. The loss
reduction is real (the model measurably got better at assigning probability to the
correct target tokens), but a single 1024-dim delta, trained for only 492 steps at
`lr=5e-5` (calibrated for MAFAND-MT's full-parameter fine-tuning precedent, not for a
single newly-added row), apparently isn't a large enough perturbation to flip
beam-search's argmax-driven decoding away from the deeply-entrenched Swahili-shaped
prior. This is a real, mundane "not enough signal yet" finding, not evidence the
`trainable_token_indices` mechanism itself is broken (the gradient-flow proof in §7
still stands).

**Candidate next hypotheses, not yet tried, needing a decision on which to pursue**:
1. A separate, higher learning rate specifically for the new trainable params (tag
   delta + LoRA), since 5e-5 was picked for a full-parameter precedent, not a
   single-row/low-rank-adapter setup — PEFT supports per-param-group optimizer LRs.
2. More epochs (6 was chosen to match MAFAND-MT's full-finetune range at a comparable
   data scale, but that precedent doesn't necessarily transfer to this narrower
   training target).
3. Increase LoRA rank (`r=8` → higher) so attention adapters have more capacity to
   redirect generation toward the shifted tag's associated content, not just the tag
   embedding itself.
4. Now that a real GPU run is confirmed to have 17GB headroom (6.49GB peak used),
   revisit `modules_to_save` on the full embedding table (the originally-proposed,
   memory-heavier fix) as an ablation — more capacity to move, at a real memory cost
   that's now known to fit on a cloud GPU notebook even if not locally.

## 12. Option A/B lexical-constraint comparison (2026-07-29) — B works, A doesn't

Rather than guessing among hypothesis 1-4 above, ran a real comparison: can the model be
taught to substitute the right Ekegusii word for Swahili's default, using the Enchengeria
dictionary (`ekegusii_internal/dictionaries/enchengeria_en_guz_lexicon.csv`, 2,155 usable
EN-GUZ entries) as ground truth, on a 15-row held-out set (`ekegusii_test.csv`, scored by
`ekegusii_internal/lexical_constraint_eval/`) via a meaning-focused, morphology-tolerant
content-word-recall metric (deliberately not BLEU/chrF as primary — grammar is explicitly
deferred, per the framing this comparison was run under).

**Option A (decode-time logit-biasing, no retraining) — doesn't work in its naive form,
confirmed decisively by a full bias sweep (2026-07-29, later same day).** Initial test:
boosting dictionary-matched Ekegusii tokens' logits during beam search at bias=8.0
consistently produced degenerate, repetitive garbage (e.g. "orororya obororemi
oboremioremiaremiarimo...") that technically contained target substrings (gaming a crude
recall metric into showing false improvement) but was not real Ekegusii; at bias=2.0, no
measurable effect at all. **Followed up with a 9-point sweep (bias 1.0-6.0 in 0.5-1.0
steps) on a 4-sentence subset to map the actual transition, using the corrected
`is_degenerate()` from §15**: bias 1.0 through 3.5 produced **literally zero effect** —
byte-identical output to unconstrained baseline at every step, not just "small effect."
Bias 4.0-5.0 produced a barely-measurable gain (recall 0.000→0.062, one correct word
across 4 sentences). By bias 6.0, degeneration was already appearing (1/4 flagged) for
that same negligible gain. **Conclusion: no usable middle ground exists at any tested
strength** — the technique doesn't fail gracefully, it has a narrow, useless transition
directly from "no effect" to "breaks," confirmed with real data rather than inferred
from two points. HF's hard constrained-beam-search (`force_words_ids`) wasn't tried
because it requires `trust_remote_code=True` (fetches code from a Hub repo at runtime)
for this transformers version — declined as unwarranted remote-code execution for an
experiment script; this remains the one genuinely untested variant of Option A, distinct
in mechanism (hard guarantee vs. soft probability nudge) from everything ruled out above.

**Option B (terminology-constrained fine-tuning, Dinu et al. 2019-style) — works cleanly.**
Annotate the English source with dictionary-matched substitutions inline before training
(`"soil"` → `"soil (amaroba)"`), teaching the model a copy-the-parenthetical skill via
the same architecture as kernel v8 (LoRA + `trainable_token_indices`, nothing else
changed) — same annotation applied at inference. Real a cloud GPU notebook results
(`ekegusii_internal/kaggle_finetune_option_b/kernel_option_b.py`, kernel v3 smoke + v4
real run):

| Config | Recall | chrF | Degenerate |
|---|---|---|---|
| Baseline (no annotation, no bias) | 0.022 | 15.4 | 0/15 |
| Annotated-source (Option B) | 0.809 | 17.8 | 0/15 |
| Hybrid (annotated + logit-bias) | 0.809 | 18.2 | 0/15 |

Smoke (20 rows/1 epoch: 0.787 recall) and the full run (811 rows/6 epochs: 0.809) are
nearly identical — this is a cheap, quickly-learned skill, not one that needed the full
data/epoch budget. `train_loss` (6.397) is statistically indistinguishable from kernel
v8's failed run (6.411) — reconfirms, concretely this time, the standing caution against
judging by loss curves alone.

**Honest scope of what this fixes**: only words the dictionary covers (~6.7-12% of
corpus vocabulary, per §10) get corrected — the surrounding sentence is still
Swahili-structured. This is exactly "get the words right, defer grammar" as scoped, not
a general translation-quality fix. The dictionary's coverage is now the binding
constraint on how far Option B can go — see §13.

## 13. Dictionary expansion via corpus word-alignment (2026-07-29) — proposed, not yet built

Given §12's result, the next lever is dictionary coverage, not mechanism. Proposed:
bilingual lexicon induction via statistical word alignment (`fast_align`/IBM Model 2 —
CPU-only, well-suited to this corpus size, doesn't depend on pretrained embeddings
Ekegusii doesn't have) on the two real parallel corpora already in hand — 961 real PSA
rows (24-30% dictionary overlap per §8.2, register-matched to the actual training
target) and 7,930 Bible pairs (tag by source register to preserve the already-documented
sense-collision signal, e.g. `obonda`, rather than erasing it by merging blindly).
Frequency-filter (require a pairing to recur across multiple sentences before trusting
it) and cross-validate against existing Enchengeria entries via the same root-stripping
logic already built (`lexicon_lookup.py::strip_prefix`), consolidating inflected surface
forms under shared roots the way `enchengeria_lexicon_flat.csv`'s `root_headword`
structure already does. This directly attacks Option B's actual bottleneck: more
dictionary entries -> more of each sentence becomes annotatable -> proportionally more
of the corpus gets word-correct output.

## 14. Dictionary expansion via corpus word-alignment — built and validated (2026-07-29)

Implemented per §13's proposal, code in `ekegusii_internal/dictionary_expansion/`.

**Sources used — deliberately not agriculture-PSA-only**, per explicit instruction:
`ekegusii_train.csv`+`ekegusii_val.csv` (886 real rows; `test.csv` excluded to avoid
leaking eval-set information into the dictionary), the Bible NT (7,930 pairs),
`PSA_KE_Final.csv` (2,899 rows, genuinely multi-domain — Health, Education, etc, not
just Agriculture) and `Misc/psa_dataset_cleaned.csv` (3,064 rows, an alternate
pipeline's output for overlapping source material — kept anyway since repeated
co-occurrence only strengthens alignment confidence, no training-duplication risk the
way it would have for model training). `_candidates_ekegusii_corpus.csv` was checked and
excluded: 906/913 rows are exact content-duplicates of what's already in the 886
training rows (pre-promotion IDs, same underlying sentences), only 7 genuinely new.
Total: 14,779 sentence pairs, 11,946 EN word types, 29,942 GUZ word types.

**Method**: `nltk.translate.IBMModel2`, one model trained across all sources combined
(more co-occurrence evidence than training separately per register), 8 EM iterations,
298s on CPU. Each sentence's Viterbi alignment produces (English word, Ekegusii word)
correspondences; aggregated by frequency across the whole corpus, kept only pairs
recurring 3+ times (single-occurrence "alignments" from a statistical aligner are
typically noise).

**Quality check, before trusting any of it**: the top-30 highest-frequency aligned pairs
were manually checked against this document's own §8 findings, built independently
weeks earlier through direct concordance reading — and they match almost exactly:
`lord→omonene` (§8.3's exact finding), `but→korende` and `for→naki` (§8.4's exact
Bible-register connective findings), `man→omonto` (§8.3's stable-control-case finding),
`agriculture→oboremi`, `farmers→abaremi`, `schools→chisukuru`, `market→echiro` (all
match §8.2's PSA-only vocabulary list exactly). The alignment also independently
rediscovered genuine synonymy without being told to look for it: `"for"` split into
`naki` (914, bible) vs `ekiagera` (371, bible+other — a different sense, "because"), and
`"and"` split into `naende` (bible-only) vs `amo` (used across every register) — this is
the concrete "more on synonyms" outcome that was asked for, produced automatically by
the alignment rather than hand-curated.

**Cross-validated against Enchengeria** (13,746 pairs cleared the frequency floor):
123 CONFIRMED (word/root already in Enchengeria under a matching gloss — independent
confirmation), 3,492 NEW_SENSE (word/root exists in Enchengeria but under a different
gloss — the structured version of the `obonda`-style polysemy finding), 10,131 NEW_WORD
(no Enchengeria match at all). Honest caveat: the CONFIRMED/NEW_SENSE split undercounts
true confirmations, since it only catches literal substring overlap between glosses —
`man→omonto` (existing gloss "a person") lands in NEW_SENSE despite being a correct
near-synonym match, not a genuine new sense. The classification is a crude first pass on
top of alignment quality that's independently strong, not a measure of alignment quality
itself.

**Coverage impact, measured two ways**: against the corpus the alignment partly trained
on (train+val+test combined), root-stripped type coverage went 12.0%→76.3% (35.6%→91.9%
of running text) — expected to be large since alignment saw those sentences directly.
The honest, non-circular number is **test.csv alone (75 rows the alignment never saw)**:
root-stripped coverage **18.8%→75.1% of types, 36.4%→86.6% of running text** — real
generalization, not overfitting to the alignment's own source sentences, because most of
the gain comes from Bible/PSA_KE_Final/psa_dataset_cleaned vocabulary that's general
enough to recur in unseen agriculture-PSA sentences too. Constraint density on the same
15-row Option B eval set jumped from ~3 dictionary matches per sentence (original
2,155-entry lexicon) to the 10-constraint cap on every single sentence (expanded
9,911-entry+ lexicon) — see §15 for whether that translates into better Option B output,
not just better raw coverage.

## 15. Plugging the expanded dictionary into Option B — mixed result, real regression found

Re-ran Option B (same architecture, same 811-row/6-epoch training) with the expanded
dictionary driving annotation instead of the original 2,155-entry one. Kernel:
`ekegusii_internal/kaggle_finetune_option_b_expanded/`.

| Config | Recall | chrF | Degenerate/failed (corrected metric) |
|---|---|---|---|
| Baseline (plain) | 0.020 | 15.4 | 0/15 |
| **Original dict** (~3 constraints/sentence) | **0.809** | 17.8 | **1/15 (7%)** |
| **Expanded dict** (~10 constraints/sentence) | 0.473 | **22.4** | **5/15 (33%)** |

**Not a clean win — a real, evidenced trade-off.** chrF improved (more correct content
overall) but recall dropped and failure rate roughly quadrupled. This isn't a metric
artifact: `is_degenerate()` originally reported 0/15 for the expanded run, which was
wrong — a full manual read of all 15 outputs found 2 cases of mode-collapse into
similar-but-not-identical word fragments (e.g. `"ogokomera ogosimeka ogogokera
ogokeria..."`, no exact token repeats, so the original exact-token-repetition check
missed it) and 3 cases of the model falling back to copying the English source through
almost verbatim instead of translating at all (a failure mode the checker never tested
for). `is_degenerate()` was widened (char-trigram repetition, 4-char-prefix-collapse
ratio, English-source-overlap check) and validated 15/15 against manual judgment on this
batch before being trusted — then applied retroactively to the original-dictionary run
too, for a fair comparison (1/15, not the 0/15 first reported).

**Likely cause, reasoned not guessed**: annotation density per sentence, not dictionary
quality. The dictionary itself is independently validated (§14's cross-reference against
prior manual analysis, genuine held-out coverage gains). What changed is asking the same
small-capacity training recipe (LoRA + one trainable tag row, architecture unchanged) to
learn a harder task — copying ~10 parenthetical insertions per sentence instead of ~3 —
and it appears to sometimes lose track under that higher load, either garbling output or
giving up and echoing the English source.

**Natural next step, not yet tried**: cap constraints per sentence (e.g. 3-5, prioritizing
CONFIRMED/NEW_SENSE entries over the less-verified NEW_WORD bucket) even when using the
larger dictionary — keep the proven annotation density, gain the better word choices.
The expanded dictionary itself remains a validated, reusable asset regardless of this
specific integration's result — `expanded_dictionary.csv`
(`ekegusii_internal/dictionary_expansion/`) is available for this or other uses (POS-
informed embedding init from §9's earlier idea, further manual curation, etc).

## 16. Independent methodology pivot — dictionary as inference-time context, not training signal (2026-07-29)

Prompted by a direct question: given Option A (decode-time logit-biasing, decisively
dead) and Option B (terminology-constrained fine-tuning, works but hit a real
density/capacity ceiling — §15), is there a fundamentally different way to use the
dictionary that doesn't share their common failure mechanism? Deliberately set aside
both prior approaches and re-surveyed the literature from scratch rather than trying to
patch either one further.

**The shared failure mechanism in A and B**: both ask a small fine-tuned NLLB-200-600M
model to *learn*, via gradient descent on 811 sentences, to reliably use the dictionary.
Every documented failure (the embedding-tying bug, the flat logit-bias sweep, the
density/capacity ceiling) is a symptom of that specific mechanism, not evidence that
dictionaries don't help.

**What the 2023-2026 literature converges on instead**: feed the dictionary as
inference-time context to a large pretrained instruction-following LLM, not as training
signal.

- **DIPMT** (Ghazvininejad et al. 2023, arXiv:2302.07856) — per-word dictionary hints
  inserted directly into the prompt ("in this context, X means Y"), zero retraining.
  +13 BLEU in low-resource/out-of-domain settings.
- **Chain-of-Dictionary** (Lu et al., EMNLP 2024) — extends this with multi-pivot-
  language dictionary chains.
- **Retrieval-augmented prompting** (Mambai study, arXiv:2404.04809, EURALI 2024) —
  dictionary entries *and* retrieved similar real parallel sentences assembled
  per-sentence into the prompt.
- **Hybrid Dictionary→RAG→LLM** (Paiwan, MDPI 2026, doi:10.3390/engproc2025120052) —
  closest resource-scale analogue to this project: handcrafted dictionary → deterministic
  word-level gloss → LLM fluency post-edit, not end-to-end LLM translation. BLEU
  1.7-4.4 → 40.8-51.9 on a 250-sentence extremely-low-resource set.

**On morphology specifically** (the "does knowing the morphology help" question):
mixed, condition-dependent evidence, not a flat yes/no. Raw grammar-book prose fed to an
LLM does *not* reliably help — Aycock & Bawden (arXiv:2409.19151) re-examined the MTOB
benchmark (Tanzer et al. 2024, arXiv:2309.16575 — Kalamang, chrF peaked at 44.7/45.8 vs.
51.6/57.0 human) and found "almost all improvement stems from the book's parallel
examples," not the grammatical explanations; a Southern Quechua→Spanish study
(arXiv:2406.15625) independently confirms it ("morpheme translations improve model
outputs, but information from the grammar and corpus have a null or even negative
effect"). But *structured/codified* rules do help — Zhang et al. 2025, "Read it in Two
Steps" (ACL 2025, arXiv:2506.01796): representing grammar as structured/code-like
functions, retrieved per-word rather than dumped whole, gave +13.1% BLEU; the bottleneck
was rule *retrieval*, not rule quality.

**One more independent lever, noted but not pursued this session**: Shi et al. 2022
(doi:10.1155/2022/5296946) used a seed dictionary of comparable size to this project's
(1,000-2,000 entries) to *mine* real parallel sentences from monolingual text via
cross-lingual embeddings + a classifier — a different mechanism from DALI's
word-substitution pseudo-parallel generation (§9, weak result on off-domain text). BLEU
7.3→29.14 on Uyghur-Chinese. Worth trying against the unused Bible/liturgy monolingual
corpus if this direction is revisited.

**Deliberately dropped**: further NLLB/LoRA fine-tuning (the Option A/B family, for the
reason above) and hand-built shallow-transfer RBMT/Apertium-style rule systems — the
literal embodiment of "dictionary + morphology should suffice," but general RBMT
literature confirms it needs weeks of dedicated linguist rule-writing time, and its own
documented weak point is lexical disambiguation (Costa-jussà 2015) — the same problem a
bare dictionary already has.

## 17. Phase-1 prototype: dictionary-prompted LLM translation — results (2026-07-29)

Built `ekegusii_internal/llm_dict_prompt/run_prototype.py`. Two conditions, both via a
general-purpose LLM at inference time only, zero fine-tuning: **baseline** (zero-shot,
no dictionary, no examples) vs. **dict_prompted** (DIPMT-style per-word glossary hints
from the curated 2,155-entry Enchengeria lexicon + Mambai-style retrieved real parallel
examples, TF-IDF nearest-neighbour from `ekegusii_train.csv`'s 811 rows). Backend:
a general-purpose LLM API `command-a-03-2025` — the only real, non-placeholder general-LLM API credential
available in `.env` at the time (several other major LLM provider keys were empty placeholders).

First run (15-sentence set, same one Option A/B were scored on, for direct
comparability) surfaced a real prompt-format bug: one output was the model literally
echoing `"in this context in this context..."` from the hint template instead of
translating. Fixed by moving the glossary+examples into a separate system message
(not interleaved with the translation instruction), switching the per-word hint format
from a full templated sentence to a compact `en -> guz` glossary line, and adding
automatic retry (up to 2x, reinforced prompt + higher temperature) on any output that
trips the existing `is_degenerate()` checker.

**Larger, less cherry-picked run** (52 sentences — all of `ekegusii_test.csv`'s 75
held-out rows with >=1 dictionary constraint, not just the top-15 by constraint count):

| Condition | Recall | chrF | Degenerate |
|---|---|---|---|
| baseline (zero-shot) | 0.026 | 21.2 | 2/52 |
| **dict_prompted** | **0.897** | **49.4** | **0/52** |
| *(reference) Option B fine-tuned NLLB, 15-sentence set* | *0.809* | *17.8* | *1/15* |

Both recall and chrF *improved* going from the small cherry-picked set to the larger
one — not a fluke of an easy sample. Manually read a sample of outputs rather than
trusting the metrics alone (per this project's own hard-learned lesson from §14/§15):
dict_prompted outputs are often near word-for-word matches to the real reference;
baseline outputs are fluent-*looking* fabrication that defaults to Swahili-shaped
guesses, not real Ekegusii. One chrF=100/recall=0 case turned out to be a metric quirk
(a near-perfect translation that just didn't happen to reuse the one specific word the
recall metric was tracking), not a real failure.

**Net**: on a larger, honest sample, dictionary-as-inference-time-context clearly beats
Option B's fine-tuned numbers on both recall and fluency, with no GPU, no training run,
and no retraining cycle when the dictionary changes. Code:
`ekegusii_internal/llm_dict_prompt/run_prototype.py`; results in
`prototype_results.json` (15-sentence) and `prototype_results_full.json` (52-sentence,
also the source of `eval_set_full.json`, built fresh rather than mutating the shared
`lexical_constraint_eval/eval_set.json` Option A/B numbers are pinned to).

## 18. Morphology hints ablation — a wash, not a win (2026-07-29)

Directly tested the "dictionary + knowing morphology should suffice" intuition as a
third condition, **dict_prompted_morph** = dict_prompted + a morphology block: a small,
hand-verified set of real reciprocal/applicative root→derived-form examples grepped
straight from the dictionary's raw entry text (e.g. `checha` "to peel" →
`checherana` "to peel each other" [reciprocal], `chabiti` "to beat" → `chabiteria`
"to beat for someone" [applicative] — each individually verified against
`enchengeria_entries.jsonl` before inclusion, not fabricated), plus any sentence-specific
root-family match from the flat lexicon (`enchengeria_lexicon_flat.csv`'s
`root_headword` grouping, 85 usable families). Structured/codified examples per §16's
literature finding, not a prose grammar explanation.

Coverage was checked *before* building this: the specific per-sentence family lookup
only matches 2 of 52 eval sentences; the two formally-tagged derivation categories
(reciprocal/applicative in `pos_tags`) turned out to have **zero** entries with a usable
English gloss on both root and derived form when checked directly (the earlier §9-built
`morphology_family_evalset.jsonl`'s "42 usable families" and the DERIV_TAGS-based
extraction don't overlap as cleanly as expected).

| Condition | Recall | chrF | Degenerate |
|---|---|---|---|
| dict_prompted (no morphology) | 0.878 | 49.2 | 1/52 |
| dict_prompted_morph | 0.846 | 50.8 | 1/52 |

Net negative on recall (4 sentences worse, 2 better), slight positive on chrF, same
final degenerate count (first-attempt failures roughly doubled, 3→7, but the existing
retry mechanism caught all of them). Checked whether the model ever actually *used* the
taught patterns: searched all 52 outputs for the six example derived words verbatim —
**zero hits**. Consistent with the coverage math above: the general cheat-sheet's
example verbs (peel, send, deprive, mourn, beat — personal/pocket-dictionary
vocabulary) essentially never overlap with this agriculture-domain eval set, so the
model had almost no on-topic opportunity to apply what it was taught.

**Honest read**: this doesn't falsify the underlying idea (Zhang et al. 2025 got +13.1%
BLEU from structured rules done right, §16) — it falsifies *this instantiation*. The
dictionary's morphological documentation is real (§9) but too sparse and
domain-mismatched to give the model actionable signal on agriculture-topic sentences. A
fair retest would need either domain-matched verb examples or an eval set actually
containing verb-extension-relevant content, neither of which this dictionary currently
supplies at scale. Not worth pursuing further without new morphology data. Code:
`ekegusii_internal/llm_dict_prompt/morphology_lookup.py`; results in
`prototype_results_morph.json`.

### 18.1 Retest with real grammar-sourced paradigm data — a real win this time (2026-07-29)

SS18 concluded the null result was a data-starvation artifact (6 off-domain
dictionary pairs, 0/52 eval-sentence overlap), not a real verdict on the underlying
idea. This session amassed two reference grammars — Whiteley (1956) *A Practical
Introduction to Gusii* (scanned, OCR'd via tesseract 5.5.0 on PyMuPDF page renders,
350dpi — no text layer existed) and Nyarigoti & Ntabo (2020) *An Introductory Grammar
of EkeGusii* (turned out to already have a real extractable text layer on 143/153
pages once checked directly with PyMuPDF, contrary to this thread's own initial
assumption — no OCR needed there after all) — and pulled 19 additional root→derived
pairs from their verb-extension sections (SS26/31/37 Prepositional/Causative/
Reciprocal/Reversive in Whiteley; SS3.5.7/4.8 Reciprocal Pronouns/Passive Voice in
Nyarigoti & Ntabo), on top of the original 6, for 25 total in
`morphology_lookup.py`'s `GENERAL_MORPHOLOGY_EXAMPLES`. Every pair was read directly
off the source page and cross-checked before inclusion — ambiguous OCR (the SS38
"Synopsis of C and D forms" table, whose columns tesseract visibly scrambled) was
left out rather than guessed at.

Coverage checked *before* rerunning, same discipline as SS18: `simeka`/`simora`
(plant/dig up — literally agriculture vocabulary) matches 5/52 eval sentences,
`konya` (help) 8/52, `manya` (know) 7/52, `ikera`/`etera` 10/52 each — real,
substantial overlap versus 0/52 for the original set.

Reran the exact same `dict_prompted_morph` mechanism (unchanged code, PSA-only train
bank, same 52-sentence `eval_set_full.json`) via `run_morph_retest.py`:

| Condition | Recall | chrF | Degenerate |
|---|---|---|---|
| dict_prompted (no morphology, control) | 0.878 | 49.2 | 1/52 |
| dict_prompted_morph (SS18, 6 off-domain pairs) | 0.846 | 50.8 | 1/52 |
| dict_prompted_morph (retest, 25 real-coverage pairs) | **0.922** | **51.1** | **0/52** |

This time both metrics improve over the control simultaneously (SS18's attempt
traded recall for chrF; this doesn't), and the degenerate count drops rather than
holds steady. Checked whether the model actually used the taught forms, the same
verbatim-search discipline as SS18: **4 of the 25 taught derived words appear
verbatim in the outputs this time** (`ikera`, `etera`, `ringora`, `enana` — SS18
found zero), direct evidence of real causal use, not a coincidental metric bump.

**Honest caveat, checked by hand, not just the aggregate numbers** (per this
workspace's standing "verify generated text, not just metrics" discipline): spot-
checking the 3 sentences where a taught form's use could be judged against the
reference —
- AGRI_252: output's `Goikera` matches the reference translation's own word choice
  exactly — a clean, correct hit.
- AGRI_974 ("...worms and all that complement each other"): output uses `enana`
  ("give to one another") where the reference uses a different reciprocal-marked
  verb (`bikoererania`) — not the literal expected word, but a reasonable transfer
  of the *reciprocal pattern* to a new mutual-action context, which is the
  hints' intended function per `morphology_lookup.py`'s own docstring ("use the
  pattern shown, not necessarily the exact word listed").
- AGRI_344 (irrigation/water-saving efficiency): output uses `ringora` ("unfold")
  twice in a water-conservation context where "unfold" doesn't fit semantically —
  a likely misapplication, borrowing a taught word without matching its meaning to
  the sentence.

So: a genuine, verified positive result on this eval set, but usage quality is mixed
(1 clean hit, 1 reasonable pattern-transfer, 1 likely misfire), not a uniformly
correct mechanism. Also worth flagging against this project's stated priority
(general Ekegusii coherence first, agriculture-domain specialization second, since
general competence is what transfers to any specific setting): this retest only
measures the agriculture eval set. Before wiring the expanded morphology hints into
`translate.py`'s production path, the fair next check is the same
verbatim-usage-and-spot-check discipline against a **general/non-agriculture** set
(e.g. greetings, Bible-corpus material) to confirm the hints help broadly and don't
introduce off-domain misfires like the AGRI_344 case above at a higher rate outside
agriculture text. Code: `morphology_lookup.py` (updated 2026-07-29),
`run_morph_retest.py` (new); results in `prototype_results_morph_retest.json`.

## 19. Streamlit deliverable (2026-07-29)

`ekegusii_internal/llm_dict_prompt/translate.py` factors the validated `dict_prompted`
mechanism out of the eval harness into a reusable `EkegusiiTranslator` class (loads the
dictionary + retrieval bank once; `.translate()` per sentence, retry-on-degenerate
built in) — the Week 3 "inference script" deliverable. `streamlit_app.py` is a thin
single-button UI on top of it: English text box, Translate button, Ekegusii output, a
collapsible "dictionary words used" panel for transparency. Verified end-to-end with a
real Playwright browser test (fill → click → real output rendered), not just an import
smoke test — screenshot confirms the UI renders correctly. Running on port 8502 (8501
is the live Hyperlocal dashboard, left untouched), accessible at
`https://vsc.sparkaltest.com/proxy/8502/`.

**Known limitation, found via manual testing after the demo went live: this is a
domain-specific translator, not a general one.** Tested `"Good morning"` through the
live app: output was wrong, translating "morning" as `chinsemo` ("sessions"). Root
cause, diagnosed not guessed: the retrieval bank (`ekegusii_train.csv`) is 100%
agriculture-PSA text with zero greetings/small-talk, so TF-IDF retrieval for an
out-of-domain input returns the *least-bad* available match rather than a genuinely
relevant one — here, a `"MORNING SESSION"` (workshop) example, which then contaminated
the model's word choice for "morning." Separately, the dictionary *does* contain real
greeting vocabulary (`amakuania`/`amasoge` = "greetings") and phrase-length glosses
*do* match (verified: `"greetings to all farmers"` correctly hits `amakuania`,
`"a bad place"` matches as a full 3-word phrase — the lookup isn't word-only) but only
via **exact substring matching, not semantic/paraphrase matching**: "Good morning"
doesn't literally contain the word "greetings," so the real dictionary entry was never
reached. Every eval run in §17-18 (recall 0.897/chrF 49.4 etc.) used
`ekegusii_test.csv`, which — like the training data — is exclusively long-form
agriculture-PSA-style sentences; short conversational phrases and greetings were never
part of the eval methodology at any point in this project (Option A/B included). The
validated numbers describe performance on agriculture-PSA-style input specifically, not
general-purpose translation.

**Fixed properly, not patched**: a first attempt closed this gap with a small hardcoded
`common_phrases.csv` exact-match lookup (12 pairs sourced from a web search) — explicitly
rejected in favour of genuine generalization. Real fix: the retrieval bank now draws from
**both** the 811-row agriculture-PSA train split **and** the real, licensed 7,930-pair
Ekegusii New Testament corpus (§6, `ekegusii_kjv_aligned.csv`) — Bible text naturally
contains everyday sayings/greetings/blessings the PSA corpus has zero of. Re-tested:
`"Peace be with you"` → `"Omwoyo w'omorembe ubane na'we"`, closely mirroring the Bible's
own retrieved blessing pattern (`"Nyasaye bw'omorembe abe amo nainwe"`) — genuinely
grounded, not fabricated. **No regression on the original agriculture-PSA numbers**:
re-ran the first 15 rows of the 52-sentence eval set with the expanded pool, recall
0.956/chrF 50.3 vs. the PSA-only pool's ~0.87-0.90/49 on the same rows — TF-IDF still
favours the closer in-domain match when one exists, so broadening the pool cost nothing
measurable on the validated domain. Register-mismatch risk from §8 (`obonda` sense
collision, Bible's `aka-` narrative-tense over-representation) is real and not separately
mitigated here (no per-query register classifier) — a deliberate, flagged trade for this
specific problem, not a solved risk. The web-search-sourced `common_phrases.csv` is kept
on disk only as a record of the rejected first attempt, not used by `translate.py`.

**Licensing constraint, worth remembering before treating this as team-repo-ready**:
this app depends on the Enchengeria dictionary CSVs, which live in `ekegusii_internal/`
specifically because they're personal paid-access copyrighted material (§9) that can't
be redistributed into the shared `PSA-MT-Project` team repo. The app is a working
personal-branch demo, not yet a committable team deliverable — that needs an explicit
team decision (smaller redistributable dictionary subset, or per-user KNLS access)
before it goes into the shared repo. Also worth flagging against the Week 3 rubric's
literal "≥2 pre-trained models fine-tuned few-shot" line: this session's winning
approach is prompting, not fine-tuning — a deliberate, evidence-backed pivot (§16), but
worth documenting explicitly as such rather than silently reframed as a second
fine-tuned model.

## 20. Lemma + WordNet-synonym dictionary fallback (2026-07-29)

Direct question raised: are word similarities considered when a direct dictionary
translation isn't available? Answer at the time: no -- `find_source_constraints()` is
exact substring matching only, confirmed to miss same-word form variants ("to help" in
the dictionary vs "help" in the input, since 91 of the dictionary's verb glosses are
phrased in the infinitive) and true synonym gaps ("purchase" when only "buy" is
covered).

**Checked whether the dictionary itself lacks common phrases, or whether that was a
parsing artifact of the EPUB conversion.** Confirmed via the dictionary's own front
matter ("How to Use this Dictionary," §1.0-2.5): it is explicitly a word-level
lexicographic dictionary (Simple words/Derivatives/Compounds/Homographs/Affixes), not
a phrasebook -- no "common phrases"/"greetings"/"expressions" section exists. Not a
parsing artifact; this is the source's actual, stated scope. Of the parsed CSV's 1,205
multi-word English glosses, ~98% are legitimate descriptive phrases defining a single
Ekegusii word (normal practice for culturally-specific terms with no one-word English
equivalent), and only ~1-2% are genuine parsing artifacts, narrowly confined to
affix-type headwords (e.g. `-a`'s entry has a Swahili grammar note that leaked into the
English-gloss field due to unusual inline formatting specific to affix entries).

**Built `ekegusii_internal/llm_dict_prompt/semantic_fallback.py`**: lemma-tier
normalization (safe, same-meaning) tried first, then a WordNet-synonym tier only if
that misses. A real danger was found and fixed while building the synonym tier: naive
lemma-string matching let "help" match the dictionary's "aids" -> `enyamoreo` (which in
this PSA-domain dictionary means the HIV/AIDS disease, not "assistance") -- WordNet
genuinely lists "aids" as a valid plural-of-"aid" sense too, just not its own top
sense, so neither "any synset overlap" nor "query's top synsets vs. the dictionary
word's full synset list" avoided it. Fixed by requiring **both** words' own top-2
WordNet synsets to intersect, which correctly rejects that collision while still
finding legitimate pairs (assist~help, crops~harvest via the shared "yield" sense).
Accepted trade-off: this also misses some legitimate pairs buried deeper in either
word's sense list (buy/purchase's shared sense is buy's #2, purchase's #5) --
intentional, since a wrong-domain injection is worse than a missed synonym for a
last-resort fallback tier.

**Tested on the same 52-sentence eval set**: recall 0.906 vs. control's 0.895, chrF
45.2 vs. 46.6 -- essentially neutral on this metric, but 41/52 (79%) of sentences
gained at least one additional hint the plain exact-matcher missed entirely (mostly
safe lemma-tier catches: harvesting→harvest, markets→market, farm→farming; genuine
synonym catches: agriculture~farming, assistance~help, price~prices). Manually
reviewed every fallback hit generated on the eval set -- no dangerous substitutions
found (the aid/AIDS-class case is what the top-2/top-2 fix specifically closed).
Promoted into the live `translate.py`/`streamlit_app.py` and verified end-to-end with a
real Playwright browser test (not just a function call) -- `"Help farmers buy seeds"` →
`"Gosiira abaremi okogora imbe."`, both words now correctly grounded via the lemma
tier, transparently shown in the UI's new "Inferred word matches" panel with
same-confidence (lemma) vs. lower-confidence (synonym, phrased "approximately like X")
distinguished for the reader.

## 21. a general-purpose LLM API trial quota exhausted; open-source model validated as a viable, much cheaper alternative (2026-07-29)

**a general-purpose LLM API trial-key headroom checked for real, not assumed — insufficient for the
planned bulk multi-domain translation task.** A live rate-limit probe confirmed the
account is on that API's trial tier: **20 calls/minute and 1,000 calls/month total**,
across all endpoints. A 100-phrase general-domain test (baseline / dict_prompted_semantic
/ dict_prompted_semantic_morph, ~300 planned calls) run this session hit the ceiling
directly — every call started failing after 4 retries with empty output partway
through the baseline condition, confirmed by inspecting the run log (77/88 baseline
calls returned nothing). The job was killed rather than left running, since continuing
could not produce usable data until the monthly quota resets. **This general-domain
retest of the morphology hints (SS18.1) is still outstanding** — retry once quota
resets, or run it via the open-model path below instead.

**Given this, validated an open-source model on a rented GPU (a remote GPU platform) as the
backend for the eventual bulk task**, using the exact same eval set (`eval_set_full.json`,
52 agriculture sentences) and the exact same scoring code (`content_word_recall`,
`is_degenerate`, `sacrebleu`) already used for every a general-purpose LLM API number in this document —
a like-for-like comparison, not a new methodology. Model: `Qwen/Qwen2.5-7B-Instruct-AWQ`
(4-bit quantized, ~5.2GB), served via vLLM's offline batch API on a single T4 GPU
(15GB VRAM) — no persistent server, no networking, ~25-30 minutes of total GPU time
across setup + two runs, well under $1.

First attempt (dict_prompted mechanism, no retry-on-degenerate logic) already showed
promising recall but a real weakness: **recall 0.909, chrF 43.0, degenerate 6/52**
(two clear repetition-loop failures, e.g. `"...kueleza kueleza kueleza kueleza..."`,
`"...amaroba akotere amaroba akotere..."`) — a materially higher failure rate than
that API's, and not actually a fair comparison, since the script hadn't ported that API's
retry-on-degenerate mechanism (up to 2 retries, reinforced prompt + higher
temperature). Added it (wave-batched: regenerate only the still-degenerate subset
each retry round) and reran:

| Condition | Recall | chrF | Degenerate |
|---|---|---|---|
| a general-purpose LLM API `dict_prompted` (command-a-03-2025, no morphology) | 0.878 | 49.2 | 1/52 |
| a general-purpose LLM API `dict_prompted_morph` (real grammar data, SS18.1) | **0.922** | **51.1** | **0/52** |
| Qwen2.5-7B-Instruct-AWQ `dict_prompted` (open, T4, retry-enabled) | **0.910** | 44.7 | 1/52 |

**Recall and degenerate rate are now essentially on par with a general-purpose LLM API** (recall even
edges out that API's non-morphology condition) once the retry mechanism was matched
fairly. chrF is meaningfully lower (~4.5-6.4 points), consistent with a much smaller
model producing less precise/fluent Ekegusii construction even when the right content
words land. Spot-checked the one remaining "degenerate" flag (`AGRI_193`) by hand: it's
a false positive, not real degeneration — the output correctly preserves
`"Kenyatta University, Jomo Kenyatta University of Agriculture and Technology (JKUA)"`
verbatim (real institution names, same choice a human translator would make), which
trips the English-copy-ratio heuristic. Spot-checked previously-degenerate cases after
retry (`AGRI_918`, `AGRI_1032`, `AGRI_252`) -- all now read as real, coherent
Ekegusii-shaped text, not garbage.

**Conclusion: Qwen2.5-7B-Instruct-AWQ on a single T4 is a viable backend for the bulk
multi-domain translation task**, at a small fraction of a general-purpose LLM API production pricing and
with no rate ceiling (vLLM batches hundreds of sentences per minute vs. a general-purpose LLM API trial's
20/minute). Not yet run against the general-domain (non-agriculture) eval set --
that's the fair next check before fully committing to it for the bulk job, same
discipline as SS18.1's agriculture-only caveat. Code: `open_model_translate.py`
(scratchpad, not yet committed to a permanent location -- promote if this becomes the
production path); results: `open_model_results_retry.json`.

**a cloud compute platform credentials updated the same day (free-tier window, time-boxed) -- checked
a hosted foundation-model API as a third path, and it turned out to be the best one found so far.**
The platform's model-listing command shows a large catalogue (a general-purpose LLM API, Meta Llama
3/3.1/3.3/4, Mistral, Qwen3, Amazon Nova, and more) already accessible on this
account with no explicit request step. that API's own `command-r-plus-v1:0` returned
`ResourceNotFoundException: marked ... Legacy ... not actively used in the last 30
days` -- a provider-side deprecation gate, not an IAM/account problem. **`meta.
llama3-70b-instruct-v1:0` worked immediately** via that API's model-agnostic converse-style
call (its SDK's runtime client -- same system/user
message shape as every other backend's chat API, no per-provider prompt templating
needed). Ran the identical `dict_prompted` mechanism (TF-IDF retrieval + dictionary
hints, same retry-on-degenerate logic as the Lightning run) against the same
52-sentence eval set, straight from this container -- no self-hosting, no GPU
rental, just billed API calls:

| Condition | Recall | chrF | Degenerate |
|---|---|---|---|
| a general-purpose LLM API `dict_prompted` (no morphology) | 0.878 | 49.2 | 1/52 |
| a general-purpose LLM API `dict_prompted_morph` (real grammar data) | 0.922 | 51.1 | 0/52 |
| Qwen2.5-7B-Instruct-AWQ (Lightning, retry-enabled) | 0.910 | 44.7 | 1/52* |
| **Llama3-70b-instruct (a hosted foundation-model API, retry-enabled)** | 0.904 | **54.8** | **0/52** |

**a hosted foundation-model API/Llama3-70b has the best chrF of every backend tested, including that API's
own best (morphology-enhanced) condition, with zero degenerate outputs and recall
on par with the rest.** Spot-checked by hand: several outputs match the reference
almost phrase-for-phrase (`"kogacha rigesa"`, `"korenda ebirengo biganeiries ase
rirorio"` -- both near-verbatim matches). **Current frontrunner for the bulk
multi-domain translation task** -- cheaper than a a general-purpose LLM API production key, no
self-hosting/GPU-management overhead unlike Lightning, best quality found so far.
Not yet checked: exact per-token a hosted foundation-model API pricing for this model, and account-level
throughput quotas at bulk scale (this was 52 sequential calls with no throttling
hit, not yet stress-tested at thousands of calls). Not yet retested on
general/non-agriculture content, same open item as the Qwen/Lightning result above.
Code: `run_bedrock_test.py`; results: `bedrock_results.json`. Full handoff for
continuing this work: `WEEK3_4_MARATHON_HANDOFF.md`.

## 22. Cross-domain retest before the 50,000-row bulk job (2026-07-29) -- real quality gap found, plus a hard throughput ceiling

Before committing the validated `dict_prompted_semantic` mechanism (SS21) to translating
the team-wide 50,000-row synthetic pool (`psa_pipeline/output/kenyan_psa_synthetic_50000.csv`,
5 domains: Education/Health/Agriculture/Security/Governance, ~10k rows each, English-only
so far), two open items from SS21 were closed out: the general-domain retest (killed by
that API's quota exhaustion) and per-token pricing/throughput at bulk scale.

**Two eval sets, real references, same scoring code as every prior number in this doc:**

1. `general_eval_set.json` (100 everyday phrases -- greetings, food, family, body parts;
   real reference Ekegusii, cross-validated independently, SS18). a hosted foundation-model API/Llama3-70b:
   baseline recall 0.000/chrF 13.3, **production `dict_prompted_semantic` recall 1.000/chrF
   31.1**, 0/100 degenerate. Recall is clean but chrF is far below the agriculture number
   (45-55) -- and a manual read of 20 outputs confirmed this is real, not a metric
   artifact: several single-word/short-phrase translations use a different (possibly
   synonymous, possibly wrong -- can't confirm without a native speaker) Ekegusii word
   than the reference (`"Help"` -> `Gosiira` vs ref `Nkonye`; `"Heart"` -> `omoyo` vs ref
   `Enkoro`). This eval set is isolated vocabulary, not full sentences, so it's a weaker
   proxy for the 50k job (which translates full PSA sentences) than the test below.
2. **New, better resource for this specific question**: `NLP/Data/EkegusiiCorpus/processed/
   psa_en_guz_parallel.csv` -- 4,816 REAL English->Ekegusii full-sentence PSA pairs,
   lecturer-provided, spanning the exact same 5 domains as the 50k pool (Education 1,261
   / Health 1,058 / Agriculture 1,008 / Security 989 / Governance 502). This has sat
   unused as a retrieval-bank/eval source until now (previously only mined for 925
   agriculture-candidate rows). Sampled 15 real sentences each from Education/Health/
   Security/Governance (Agriculture excluded, already validated), ran through
   `dict_prompted_semantic` on a hosted foundation-model API: **recall 0.957, chrF 26.6, degenerate 0/60**.
   Per-domain chrF: Education 23.3, Health 26.7, Security 22.4, Governance 34.0 -- all
   well below the agriculture range.

**Manual read of 12 cross-domain outputs (not just the metric) found real, specific
defects**, not just a lower-fluency register mismatch: (a) numeric/named facts dropped
in health PSAs -- an Mpox case-count sentence ("98 people infected... 2 died") came back
with the numbers replaced by vague quantifiers, and a "measles-rubella, tetanus" campaign
lost the specific disease names; (b) English jargon left uninflected/untranslated in a
governance sentence about SACCO regulation ("aba' stakeholders", "aba' media", "SACCO
business", "pyramid schemes" repeated 4x in a way that reads like a mild repetition loop
`is_degenerate()` didn't catch); (c) at least one output (a "vigilant before the election"
reminder) reads as Swahili-shaped fabrication ("kuchora kwa obokonyi...") rather than real
Ekegusii, similar to the very first pre-fix failure mode documented in `translate.py`'s own
docstring, just not caught by the current heuristic; (d) a university-targeted voter-education
sentence came back saying "schools" instead of "universities" -- a real word-choice error,
not a stylistic variant. **Conclusion: recall/degenerate-rate alone are not sufficient
evidence of readiness outside agriculture** -- content-word coverage holds, but fluency,
factual/numeric completeness, and code-switch leakage all degrade in ways a native speaker
would catch immediately and a downstream reader (the PSA's actual audience) would find
either confusing or actively wrong. **Recommended fix before the bulk job, not yet done**:
fold `psa_en_guz_parallel.csv`'s ~3,800 non-agriculture rows into the retrieval bank
(currently PSA-agriculture + Bible only) so TF-IDF retrieval can surface a genuinely
relevant same-domain example for Health/Education/Security/Governance sentences instead of
the closest-available agriculture or Bible-register one; also tighten `is_degenerate()` to
catch short-ngram repetition below its current threshold and untranslated-English-token runs.

**a hosted foundation-model API throughput ceiling -- a hard blocker for the realtime API at this scale, not yet
known when SS21 was written.** The platform's own quota-check command confirms (this account, region-pinned,
not adjustable): **40 on-demand requests/minute** and 300,000 tokens/minute for
`meta.llama3-70b-instruct-v1:0`. At ~1-1.15x call overhead for retries, 50,000 rows through
the realtime converse-style loop (the same request pattern used for the earlier benchmark run) would take **roughly 24
hours of continuous sequential calls** -- impractical for a class deadline and this
container's per-command execution limits. **Fix: use that API's batch inference API instead**
(`CreateModelInvocationJob`), which supports up to 100,000 records in a single job (`Records
per batch inference job for Llama 3.1 70B Instruct` quota, adjustable, currently 100,000) --
the entire 50k dataset fits in one job. Batch inference uses the model's native
`invoke_model` request body shape, not the Converse API's `system`/`messages` shape
currently used everywhere in this codebase -- **porting the prompt-building logic to batch
format is real, not-yet-done engineering work**, not a config change.

**Cost estimate (not yet billed, verify at run time)**: measured real prompt sizes from
`build_dict_prompted_semantic_messages` (~1,580 system chars + ~180 user chars per call,
~3 few-shot examples + up to 6 glossary hints) and that API's published on-demand rate for
this model (**$2.65/1M input tokens, $3.50/1M output tokens**, per a cloud compute platform's pricing page).
Rough estimate at 50,000 rows x ~1.15 (retry overhead) x ~500 input + ~80 output tokens/call:
**~$90-120 total** for the full 50k-row job -- higher than SS21's unverified "$35-50, cheaper
than a general-purpose LLM API" guess, now a real computed number, still to be confirmed against actual
a hosted foundation-model API billing once the batch job runs (token counts here are a chars/4 heuristic, not an
exact tokenizer count).

Code: `run_general_test_bedrock.py`, `run_crossdomain_test_bedrock.py`; results:
`general_test_results_bedrock.json`, `crossdomain_test_results_bedrock.json`,
`crossdomain_eval_set.json`. Full handoff for the 50k bulk job specifically (retrieval-bank
expansion, batch-inference port, branch/push plan): see the dedicated handoff doc referenced
from `WEEK3_4_MARATHON_HANDOFF.md`.

## Sources

- FLORES-200 README: https://github.com/facebookresearch/flores/blob/main/flores200/README.md
- No Language Left Behind (NLLB): https://arxiv.org/pdf/2207.04672
- AfroXLMR: https://arxiv.org/pdf/2204.06487
- Serengeti: https://arxiv.org/abs/2212.10785
- MAFAND-MT, "A Few Thousand Translations Go a Long Way" (NAACL 2022): https://arxiv.org/abs/2205.02022
- Low-Resource NMT for Southern African Languages: https://arxiv.org/pdf/2104.00366
- Ombui, Wagacha & Ng'ang'a (2014), InterlinguaPlus Ekegusii-Swahili: https://aclanthology.org/W14-2209/
- Few-Shot Cross-Lingual Transfer for Prompting LLMs: https://arxiv.org/abs/2403.06018
- Guthrie classification of Bantu languages: https://en.wikipedia.org/wiki/Guthrie_classification_of_Bantu_languages
- Nakatumba-Nabende et al. (2024), "Building Text and Speech Benchmark Datasets... for Low-Resourced East African Languages," *Applied AI Letters* 5(2): https://doi.org/10.1002/ail2.92
- Adjeisah et al. (2021), "Pseudotext Injection and Advance Filtering of Low-Resource Corpus for NMT," *Computational Intelligence and Neuroscience* 2021: https://doi.org/10.1155/2021/6682385
- Rosetta Project, Ekegusii Genesis translation (Internet Archive): https://archive.org/details/rosettaproject_guz_gen-1
- ScriptureEarth.org, Ekegusii scripture index: https://www.scriptureearth.org/00i-Scripture_Index.php?iso=guz
- find.bible, Ekegusii Bible (GUZGUZ): https://find.bible/bibles/GUZGUZ/
- Marashian, Rice, Gessler, Palmer & von der Wense (2025), "From Priest to Doctor: Domain Adaptation for Low-Resource NMT," COLING 2025: https://arxiv.org/abs/2412.00966
- González Servín, Maldonado Sifuentes, Kolesnicova & Sidorov (2026), "Evaluating the Impact of Domain Adaptation on Transformer-based Models for Low-Resource Purépecha-Spanish Translation," *IJCoPI* 17(2): https://doi.org/10.61467/2007.1558.2026.v17i2.1265
- Hamilton, Leskovec & Jurafsky (2016), diachronic word embeddings for semantic-shift detection: https://arxiv.org/abs/1605.09096
- Kutuzov, Øvrelid, Oepen & Velldal (2018), survey of diachronic/cross-domain semantic-shift detection, ACL C18-1117: https://aclanthology.org/C18-1117/
- Van Asch & Daelemans (2010), "Using Domain Similarity for Performance Estimation," ACL W10-2605: https://aclanthology.org/W10-2605/
- Tanzer, Suzgun, Visser, Jurafsky & Melas-Kyriazi (2024), "A Benchmark for Learning to Translate a New Language from One Grammar Book" (MTOB), ICLR 2024: https://arxiv.org/abs/2309.16575
- Aycock & Bawden (2024), "Can LLMs Really Learn to Translate a Low-Resource Language from One Grammar Book?": https://arxiv.org/abs/2409.19151
- Ghazvininejad, Gonen & Zettlemoyer (2023), "Dictionary-based Phrase-level Prompting of Large Language Models for Machine Translation" (DIPMT): https://arxiv.org/abs/2302.07856
- Lu, Yang, Huang, Zhang, Lam & Wei (2024), "Chain-of-Dictionary Prompting Elicits Translation in Large Language Models," EMNLP 2024: https://aclanthology.org/2024.emnlp-main.55/
- Hindley et al. (2024), "Low-Resource Machine Translation through Retrieval-Augmented LLM Prompting: A Study on the Mambai Language," EURALI 2024: https://arxiv.org/abs/2404.04809
- Hybrid Dictionary-RAG-LLM for Paiwan-Mandarin (2026), MDPI Engineering Proceedings: https://doi.org/10.3390/engproc2025120052
- Zhang, Lin, Liu, Zhang & Feng (2025), "Read it in Two Steps: Translating Extremely Low-Resource Languages with Code-Augmented Grammar Books," ACL 2025: https://arxiv.org/abs/2506.01796
- Southern Quechua→Spanish in-context translation ablation (morpheme vs. grammar vs. corpus context): https://arxiv.org/abs/2406.15625
- Shi, Yue, Liu, Xu, Xu & Ahmad (2022), "Obtaining Parallel Sentences in Low-Resource Language Pairs with Minimal Supervision," *Computational Intelligence and Neuroscience* 2022: https://doi.org/10.1155/2022/5296946
- Khiu et al. (2024), "Predicting MT Performance on Low-Resource Languages: The Role of Domain Similarity," EACL Findings: https://arxiv.org/abs/2402.02633
