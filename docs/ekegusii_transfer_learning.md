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

## Sources

- FLORES-200 README: https://github.com/facebookresearch/flores/blob/main/flores200/README.md
- No Language Left Behind (NLLB): https://arxiv.org/pdf/2207.04672
- AfroXLMR: https://arxiv.org/pdf/2204.06487
- Serengeti: https://arxiv.org/abs/2212.10785
- MAFAND-MT, "A Few Thousand Translations Go a Long Way" (NAACL 2022): https://arxiv.org/abs/2205.02022
- Low-Resource NMT for Southern African Languages: https://arxiv.org/pdf/2104.00366
- Ombui, Wagacha & Ng'ang'a (2014), InterlinguaPlus Ekegusii-Swahili: https://aclanthology.org/W14-2209/
- Few-Shot Cross-Lingual Transfer for Prompting LLMs: https://arxiv.org/abs/2403.06018
