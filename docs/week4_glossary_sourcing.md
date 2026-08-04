# Bilingual glossaries (Week 4 dictionary-prompted ablation)

Small, general-vocabulary EN→target glossaries fetched to test whether feeding a
bilingual dictionary as LLM prompt context improves Kiswahili/Dholuo translation
quality — the same pattern that won for Ekegusii (dictionary-prompted beat
fine-tuning there, see `docs/ekegusii_transfer_learning.md`).

## EN-Kiswahili glossary (163 entries)

Transcribed from the Peace Corps Kenya **Kiswahili Competency Based Manual**
glossary appendix (pp. 233-236), a US Peace Corps training curriculum hosted
public-domain by the Live Lingua Project:
https://www.livelingua.com/peace-corps/Kiswahili/Peace%20Corps%20Kiswahili%20Manual%20-%20Kenya.pdf
Peace Corps training materials are US-government works (public domain) — freely
usable for this coursework project.

General basic vocabulary (food, numbers, common verbs, family/social terms), not
PSA-domain-specific — a genuine bilingual dictionary, not a domain glossary, since a
targeted PSA-domain EN-Kiswahili glossary wasn't found in the time budget available
for this task.

## EN-Dholuo glossary (118 entries)

Transcribed from the Tiba Foundation's **"Basic Luo Phrases for Tiba Staff and
Volunteers"** (a Kenyan medical-volunteer NGO phrasebook):
https://tibafoundation.org/wp-content/uploads/2022/12/Luo-Glossary.pdf
Skews clinical/health-domain (hospital, symptoms, medicine terms) plus greetings,
common phrases, and numbers — coincidentally useful for this project's Health-domain
PSAs. This was the only genuinely bilingual (not Dholuo-monolingual, not
Wikipedia-derived) EN-Dholuo word list findable in the time budget available — Dholuo
is markedly lower-resource online than Kiswahili. **Confirm with the Tiba Foundation
before any redistribution beyond class use** — the underlying glossary data file
itself is not included in this repo for that reason; this document records how it
was sourced and used, not the word list itself.

## What was checked and ruled out

- A GitHub Swahili-word-list project (MIT-licensed, ~16,700 entries):
  Swahili-**monolingual** (word → Swahili definition), not bilingual — not usable as
  an EN→Swahili dictionary-prompt source.
- MUSE ground-truth bilingual dictionaries: Swahili is not among its ~110 covered
  languages; the hosting file server also now returns 403s (project archived 2023).
- `word2word` (pip package, OPUS-derived word alignments, 3,564 language pairs):
  neither Swahili nor Dholuo are in its supported-language list.
