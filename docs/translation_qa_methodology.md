# Translation QA methodology — team-translated and corpus-candidate rows

Generated 2026-07-22. Covers every Agriculture-domain row needing a team-produced
translation rather than a genuinely bilingual sourced pair: English present but
Kiswahili missing/weak, or Kiswahili present but English missing/weak, plus a batch
of new corpus-derived candidate rows.

## Scope

- **925 new corpus-derived candidate rows** — English + Ekegusii present from source,
  Kiswahili missing entirely (no Kiswahili column existed in the source).
- **150 existing `agriculture_psas.csv` rows** tagged `translation=team; source_lang=en`
  — re-ran the same 3-tool comparison to bring them up to the same standard as the new
  rows.
- **8 existing rows** tagged `source_lang=sw` — Kiswahili was the real source, English
  was team-translated; re-generated English the same way.
- **Excluded**: 27 genuine bilingual source pairs (untouched), 2 rows translated from
  Chichewa (`source_lang=ny`, flagged separately for native-speaker review — none of
  the tools used here are validated for Chichewa).

## Method

Three tools compared per row: **NLLB-200-distilled-600M** (local), **Helsinki-NLP
OPUS-MT en-sw** (local, en→sw only — no reliable sw→en counterpart exists), and a
**cloud translation API** (free tier). No gold Kiswahili/English reference exists for
these rows, so quality was scored by **round-trip back-translation**: each candidate
was translated back to the source language via the cloud API (independent of whichever
tool produced it, to avoid a tool grading its own output) and compared to the original
text with `difflib.SequenceMatcher`. Highest-scoring tool's output was selected per
row.

**Tool win counts (Group A, en→sw, 1,075 rows before manual fixes):** NLLB 234 ·
OPUS-MT 98 · cloud API 743.
**Group B (sw→en, 8 rows):** NLLB 3 · cloud API 5.

## Manual read-through — what the automated score got wrong

The round-trip proxy is a heuristic, not a quality guarantee. Manual reading of the
lowest-scoring rows (and a random sample of the rest) found real problems, both caught
and missed by the automated score:

1. **Truncation (13 rows fixed).** OPUS-MT silently truncates output on longer or
   unusually-punctuated input — 6 rows caught by an English-vs-Kiswahili length-ratio
   check, 7 more caught by comparing OPUS-MT's output length against the other two
   tools' (OPUS-MT was picked as "best" by round-trip score on all 13 despite missing
   up to half the sentence). All 13 re-decided between NLLB (re-run at
   `max_length=256`) and the cloud API, excluding the truncated OPUS-MT candidate
   entirely.
2. **Terminology garbling missed by the score (2 rows fixed).** One row ("Tomato
   Yellow Leaf Curl Virus") — NLLB produced a nonsense repetition ("Virusi vya Kijani
   cha Kijani cha Kijani"), OPUS-MT produced a broken partial-English fragment, and
   **the cloud API alone got it right** ("Virusi vya Majani ya Njano ya Nyanya") — yet
   it scored *lowest* of the three on round-trip (0.034). A second row (a groundnut
   variety) similarly: OPUS-MT dropped "groundnut" entirely and was still the
   round-trip "winner." This is the clearest evidence the automated score alone isn't
   sufficient — it can pick the worst candidate when back-translation coincidentally
   drifts less for a wrong answer.
3. **Degenerate repetition (1 row, part of the 13 above).** NLLB entered a decoding
   loop and repeated "wa udongo" (of soil) dozens of times on unusually punctuated
   input; the cloud API's output was used instead.
4. **Address blocks and website navigation chrome misclassified as PSA content (11
   rows removed entirely).** The relevance keyword classifier that built this
   candidate set flagged several rows that are not PSA content at all — an
   organisation's office address repeated with minor formatting differences, and
   blog-navigation fragments ("Latest Opinions & Insights", "Image Download," an
   author bio). This is the same failure mode found in other restricted reference
   material used for calibration elsewhere in this project. Removed, not translated.
5. **Duplicate source rows (1 pair, 1 removed).** Two candidate rows were the same
   English sentence with two slightly different Ekegusii translations already present
   in the source — caught by `validate_psa_csv.py`'s duplicate-English check, not by
   translation QA. Kept one, dropped the other.
6. **Proper-noun/acronym garbling (known limitation, not fixed row-by-row).** Random
   sampling of "clean" OPUS-MT wins found Kenyan personal/institution names mangled
   by letter substitution (e.g. a public official's name rendered with a dropped
   letter, another with a doubled vowel; a government programme name left
   semi-untranslated with typos). The advisory content itself remains usable; only
   specific proper nouns are affected. Not corrected at scale — flagged here as a
   known, documented gap rather than silently accepted or overclaimed as fixed.
7. **Long-form article content, not PSA-shaped (5 rows flagged, not removed).** Five
   rows are 81-109-word blog-style paragraphs, exceeding `validate_psa_csv.py`'s
   80-word PSA-length norm. Not removed unilaterally — this is a content-inclusion
   policy call for the team, not a translation-quality issue; flagged via the
   validator's existing WARNING mechanism, same as precedent elsewhere in the dataset.

## Final state

- **913 candidate rows** (from 925: -11 cruft, -1 duplicate), all pass
  `validate_psa_csv.py` hard checks, with 14 soft warnings (5 long-form-length, 4
  false-positive language-detection flags on short/technical/proper-noun sentences —
  same pattern as other pre-existing accepted warnings in the dataset).
- **187 previously-verified rows** unchanged in count; 150 Kiswahili + 8 English
  cells replaced with the vetted translation, all still pass validation cleanly (same
  pre-existing warnings as before this pass, nothing new).
- Every touched row's `Metadata` carries `qa_tool=<nllb|nllb_256|opus|cloud_api>;
  qa_roundtrip=<score>` alongside the existing `translation=team; source_lang=...`
  tags, so the actual tool/confidence is traceable per row, not just asserted.

## What this QA process did NOT do

- Did not re-verify all ~1,075 rows individually by hand — spot-checked the
  lowest-scoring rows exhaustively, sampled the remainder. A systemic issue affecting
  a large fraction of rows would likely have surfaced in the sample; an isolated
  one-off might not have.
- Did not attempt Chichewa-language QA (2 rows, flagged separately).
- Did not fix proper-noun garbling row-by-row (documented as a known limitation
  instead).
