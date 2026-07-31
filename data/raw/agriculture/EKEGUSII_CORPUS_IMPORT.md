# Ekegusii Corpus import — Agriculture domain

**Source: "Ekegusii Corpus"** — a lecturer-provided dataset (course lecturer, shared via
Google Drive 2026-07-22), citable by that name; the lecturer and group members already
know what it refers to. Full provenance, the rest of its contents (monolingual Ekegusii
text, phonology reference), and processing steps live outside this repo at
`NLP/Data/EkegusiiCorpus/README.md` (private workspace, not part of this clone) — cite
only "Ekegusii Corpus" here, nothing about how/where it was fetched.

## Why this domain, why now

The course has moved from a per-group free choice of third target language to the whole
class targeting **Ekegusii** specifically. This corpus is the first substantial
Ekegusii-labelled dataset available for the project, so its Agriculture-relevant subset is
being ported into this domain's collection now.

## Method

The source corpus is 4,816 English→Ekegusii PSA sentence pairs across 5 domains
(Education, Health, Agriculture, Security, Governance). Its own `Domain` label was **not
trusted** — mislabeling is a known, already-documented issue with this course's other
lecturer-provided reference set (`PSA_KE_Final.csv`, 41% of labeled-Agriculture rows
turned out not to be real PSA content on manual audit). Instead, the full English column
was re-classified with a transparent keyword-based scan (see
`NLP/Project/ekegusii_internal/classify_agriculture.py`, private tooling, not in this repo):

- **925 rows** flagged agriculture-relevant by text content
- vs. **1,007** rows originally labeled `Agriculture` in the source
- **190** originally-labeled-Agriculture rows dropped (classifier found no agriculture
  content — spot-checked: these are mostly research-summary/job-posting/governance-tip
  text, e.g. "AATF is looking for a consultant to develop...", "Good governance is key to
  a successful cooperative" — correctly not PSA-shaped agriculture content)
- **108** rows recovered from other domain labels (mostly mislabeled `Education` rows
  about agricultural training programs, e.g. "Learn farming! Enroll in agricultural
  vocational courses.")

Full report with samples: `NLP/Project/ekegusii_internal/agriculture_classification_report.md`
(private, not in this repo — the report itself references internal tooling paths).

**Known limitation:** this is a first-pass keyword heuristic, not exhaustive — it will
miss agriculture-relevant rows that don't use its specific keyword list (e.g. found on
review: rows about "mushrooms", "sweet potato solar dryers" without the word "crop"/"farm"
nearby were missed). Treat `_candidates_ekegusii_corpus.csv` as a candidate set needing the
same individual-verification pass as any other lecturer-reference-derived source, not a
final import.

## Sub-categories

Derived by keyword scan, matching this domain's existing taxonomy (no new categories
invented): Crop Production (475), Livestock (179), Agribusiness & Market Access (101),
Sustainable Farming (86), Food Security (58), Training (26).

## Output — promoted 2026-07-22

**913 rows merged into `agriculture_psas.csv`** (renumbered `AGRI_191`–`AGRI_1103`,
continuing the existing ID sequence; `Metadata` carries `promoted_from=EKEGUSIICORPUS_###`
for traceability back to the source corpus's own row IDs). Combined file: **1,100 rows**,
passes `validate_psa_csv.py` cleanly (17 soft warnings, same class as pre-existing ones).

**Before merging**, ran the project's standard pairwise fuzzy-similarity dedup check
(`difflib`, threshold 0.6) across the *combined* 1,100-row set — 0 exact duplicates, but
**63 near-duplicate pairs**, overwhelmingly clustered *within* the newly-promoted rows
themselves (not between old and new). Full list: `ekegusii_internal/promotion_dedup_report.md`
(private). This is a genuine finding worth the team's attention, not just boilerplate
recurrence: several clusters look like **templated/paraphrased variations of the same
underlying message** rather than independently-sourced PSAs — e.g. six different
"Climate-smart agriculture (CSA) is an approach that helps..." openers (`AGRI_305`–`310`
range) differing only in a few words, and one clear same-event duplicate with a name typo
(`AGRI_294`/`748`, "Canisius Kanangire... Mithika Linturi" vs "...Mthika Linturi").
**Resolved 2026-07-23** via a second classifier (`ekegusii_internal/dedup_option_b.py`):
word-level diff between each pair, checking whether the differing words are a genuine
distinguishing referent (disease, crop, livestock, audience) or just stray phrasing.
Result: **26 confirmed distinct** (kept), **7 confirmed genuine duplicates** (one side
removed each — `AGRI_753`, `AGRI_306`, `AGRI_369`, `AGRI_425`, `AGRI_437`, `AGRI_499`,
`AGRI_510` — **1,100 → 1,093 rows**), **30 unresolved** (mostly the CSA-definition
cluster — same generic claim reworded ~10 different ways, plausibly paraphrase-generated
rather than independently authored, but not confirmed; left in, flagged for a human read).
Full findings: `ekegusii_internal/dedup_option_ab_findings.md`.

## Kiswahili column — filled, not left blank

This source has no Kiswahili column at all (it's an English→Ekegusii pair). Per the
English-only-source precedent in `data/README.md` (team translation, tagged
`translation=team, source_lang=en`), Kiswahili was generated for all 913 rows — and for
150 pre-existing rows in `agriculture_psas.csv` that already carried that tag, to bring
them up to the same standard — using **`scripts/translate_and_qa.py`** (new, generic,
shared tool): three translation tools compared per row (NLLB-200, OPUS-MT, a cloud translation API
Translator), scored by round-trip back-translation since no gold reference exists, plus
a manual read-through of the lowest-confidence rows that caught and fixed real problems
(truncated outputs, a garbled disease name, address-block contamination) the automated
score alone missed. Full detail: `NLP/Project/ekegusii_internal/translation_qa_report.md`
(private, not in this repo). Every touched row's `Metadata` carries `qa_tool=...;
qa_roundtrip=...` alongside `translation=team` so the actual method is traceable, not
just asserted — **still worth a team read-through before treating as final**, per the
same standard any team-translated row gets.
