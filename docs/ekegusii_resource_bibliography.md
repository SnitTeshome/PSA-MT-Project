# Ekegusii language resource bibliography (amassed 2026-07-29)

Catalogue of every Ekegusii/Gusii linguistic resource identified for this project —
what informed the dictionary-prompted translation mechanism and its morphology hints
(`docs/ekegusii_transfer_learning.md`), with each resource's access/licensing status
noted honestly rather than assumed.

## Dictionaries

- **Enchengeria — EkeGusii Dictionary** (Akama, Mecha, Otieno & Getenga, 2023, ISBN
  978-9966-082-91-6) — the complete trilingual (EkeGusii/Kiswahili/English) dictionary
  powering the dictionary-prompted mechanism; see `data/reference/README.md` for the
  published derived word-list and citation.

## Grammar references

- Whiteley, W.H. (1956), *A Practical Introduction to Gusii*. 69 pages. Developed with
  a Gusii Language Committee. Full noun-class system and a systematic treatment of
  Bantu verb-extension morphology (Statite/stative, Passive, Reciprocal, Reversive,
  Causative, Prepositional/applicative) with paradigms and translation exercises —
  directly informed the morphology-hints ablation in
  `docs/ekegusii_transfer_learning.md` §18.1.
- Nyarigoti, N. & Ntabo, V.O. (2020), *Introduction to the Grammar of EkeGusii*,
  Utafiti Foundation, ISBN 978-9966-26-229-5. 153 pages. Modern, written by native
  EkeGusii-speaking academics. Covers dialects, phonology, morphology, the verb
  system, clause/sentence structure, and a proverbs section. A truncated free preview
  exists at the publisher's site; the full version informed this project.
- Otieno, Peter Nyansera (Kisii University), contribution to Beale-Rivaya's
  *Minority-Minoritized Languages and Cultures Project* (Texas State University),
  2022-2023. 34 pages. Sociolinguistic framing (language-endangerment indicators) plus
  a phonological description with acoustic data (spectrograms/waveforms): 7 vowel
  phonemes with length distinction, a 14-consonant IPA inventory, diphthongs,
  triphthongs, elision rules, tone. Also published as an open web book covering
  several other minoritized languages for comparison.
  **Bibliography drawn from this source's own citation trail** (several of these
  Kenyan-university MA/PhD theses are unpublished and not digitized online — would
  need direct contact with the relevant university library archives to obtain): Basweti,
  Barasa & Michira (2015), "Ekegusii DP and its Sentential Symmetry," *Int'l J. of
  Language and Linguistics* 2(2); Bosire (1993), unpub. MA diss., U. of Nairobi; Mecha
  (2006), unpub. MA thesis, Kenyatta University; Omoke (2012), unpub. MA thesis, U. of
  Nairobi; Otieno (2020), unpub. PhD thesis, Kisii University; Otieno & Mecha (2019),
  *Macrolinguistics* 7(2); Otieno, Mecha & Opande (2020), *Int'l J. of Research and
  Scholarly Communication* 3(1); Ingonga (1991), unpub. masters diss., Kenyatta
  University; Whiteley (1960), East African Institute of Social Research.

## Academic papers

- Nash (2013), "The Morphophonemics of Vowel Compensatory Lengthening in Ekegusii,"
  *IJERN* 1(9), pp.137-151.
- "EkeGusii Morphopragmatics and the Junction with Iconicity," *Macrolinguistics* —
  diminutives/augmentatives as morphopragmatic markers.
- "A Comparative Morphological Analysis of Derivation and Inflection in EkeGusii and
  English: Processes, Functions, and Typological Implications," *Multi-Research
  Journal*.
- Mwita, Leonard Chacha (2008), *Verbal Tone in Kuria*, PhD dissertation, UCLA
  Department of Linguistics. 367 pages. Kuria (Guthrie JE.43) is Gusii's closest Bantu
  relative per Guthrie classification — a genuine comparison point, not Ekegusii
  itself.
- Mariera (preprint, under peer review at time of use), "Gestalt iconicity in
  Ekegusii adjective vowel lengthening" — vowel lengthening in adjectives as
  iconic/correlating with meaning-intensity.
- Hyman, Larry M. & Nyamwaro, Hildah Kemunto (2022), "Grammatical tone mapping in
  Ekegusii," *Phonology* 39(3):503-529, Cambridge University Press, DOI
  10.1017/S0952675723000118. **Open Access (CC BY licence)** — extends Bickmore's
  Tone Patterns I-VI (below) with three more patterns.
- Mariera, Elijah Omwansa; Mecha, Evans Gesura; Anyona, George Morara (Kisii
  University) (2021), "Diagrammatic Iconicity in EkeGusii: A relation between the
  structure of form and meaning," *Macrolinguistics* 9(1), Serial No.14, pp.84-100,
  DOI 10.26478/ja2021.9.14.4. Argues EkeGusii speakers subconsciously cluster sounds
  around related meanings (gestalt/relative iconicity); covers reduplication,
  phonaesthesia, onomatopoeia.
- Bickmore, Lee S. (1999), "High tone spread in Ekegusii revisited: An optimality
  theoretic account," *Lingua* 109:109-153, Elsevier. The seminal foundational paper
  several of the above cite by name (Bickmore's Tone Patterns I-VI). Re-analyzes
  Ekegusii's tonal system within Optimality Theory.

## Vocabulary/conversational resources

- A ~90-item categorized everyday-phrase list (greetings, questions, actions, family
  terms, time, body parts, food/drink, animals, common objects), cross-validated
  against an independent web-sourced phrase list used earlier in the project — every
  greeting appearing in both sources matched exactly, meaningfully stronger evidence
  than either source alone.
- The Ekegusii New Testament corpus (7,930 real English-Ekegusii verse pairs)
  already powers the retrieval bank in `docs/ekegusii_transfer_learning.md`.

## Checked, thin or not relevant

- A small crowdsourced/community Ekegusii dictionary site was found but wasn't a
  structured resource worth building on (~2.7KB of actual content, word list with no
  visible glosses in the static page).
- AfLaT.org's resources directory has no Ekegusii-specific tools/corpora (Ekegusii
  only appears as a taxonomy tag).
- No OPUS/ELAR corpus entry found for Ekegusii specifically.
- Nash, Carlos (2011), *Tone in Ekegusii*, PhD dissertation, UC Santa Barbara — no
  freely accessible copy found.
- Cammenga (2002) phonology monograph — commercially published, no free version
  found.

## What this fed into

1. Two scanned grammar PDFs were OCR'd where needed (one had a real text layer
   already, once checked directly rather than assumed).
2. 19 new verb-paradigm pairs were extracted and added to the morphology-hints
   lookup — retest result: recall 0.922/chrF 51.1/degenerate 0/52 vs. the
   no-morphology control's 0.878/49.2/1/52, a real improvement (full writeup:
   `docs/ekegusii_transfer_learning.md` §18.1).
3. The everyday-phrase list's potential integration into the production retrieval
   bank was identified but not decided in this pass (see `docs/ekegusii_transfer_learning.md`
   §23 for the retrieval-bank expansion that was ultimately implemented instead, using
   the 5-domain parallel corpus).
