# PSA Machine Translation Project — Week 1 Report

**Course:** DSA 4020A – Natural Language Processing

**Supervisor:** Dr. Edward Ombui

**Deliverable:** Week 1 — Data Collection & Curation (Sub-objective 1)

**Project:** Multilingual machine translation of Kenyan Public Service Announcements (PSAs) between English/Kiswahili and Ekegusii, Somali, and Dholuo.

---
## Team Members — Group 1

| # | Name | ID Number |
|---|---|---|
| 1 | Snit Teshome | 670552 |
| 2 | Bradley Azegele | 66834 |
| 3 | Kyeremateng Martin | 669217 |
| 4 | Kemo Dibassy | 669111 |
| 5 | Samantha Nyatichi Masaki | — |
## 1. Team and Domain Assignments

| # | Name | Assigned Domain | Rows contributed to the merged dataset | Distinct sources documented |
|---|---|---|---|---|
| 1 | Kyeremateng Martin | Governance | 891 | 10 |
| 2 |Snit Teshome| Health | 1,300 | 16 |
| 3 | Bradley Azegele | Agriculture | 1,795 | 114 |
| 4 | Samantha Nyatichi Masaki| Education | 2,074 | 13 |
| 5 | Kemmo Debassy | Security & Safety | 1,096 | 12 |

Row and source counts are pulled directly from the team's current merged, cleaned dataset (`data/clean_real.csv`), verified by recomputation rather than carried over from memory. Team members whose names are not yet filled in should confirm their row above per the domain they collected for.

---

## 2. Project Overview

We are building a proof-of-concept multilingual machine translation system for Kenyan Public Service Announcements (PSAs) — short, directive, action-oriented public messages such as health advisories, safety warnings, and deadline reminders. The system translates between English/Kiswahili and three under-resourced indigenous languages: **Ekegusii** (Bantu), **Somali** (Cushitic), and **Dholuo** (Nilotic).

Week 1 focuses on Sub-objective 1: curating a high-quality multilingual dataset of at least 5,000 sentences, spread across five domains — **Education, Health, Security & Safety, Agriculture, and Governance**.

---

## 3. Week 1 Milestone Checklist — Status

| Milestone | Status | Notes |
|---|---|---|
| Identify and document ≥10 reliable sources | **Met overall, uneven by domain** | Agriculture (114) and Health (60) are well above target; Education (24) is comfortable; Governance (10) is right at the line; **Security & Safety (4) is below target** and needs more source diversity before it can be marked fully met. |
| Hybrid scraping pipeline (manual + automated, robots.txt-respecting) | **Met** | Automated fetching combined with manual curation and OCR (Tesseract) where automated access was blocked; robots.txt and rate limits respected throughout. |
| Collect raw PSAs across all 5 domains | **Met** | All five domains have data in the merged dataset. |
| Structured CSV with required schema | **Met** | Columns: `PSA_ID, Domain, English, Kiswahili, Ekegusii, Somali, Dholuo, Source, Date, Metadata`. The original single "Target Languages" placeholder column was split into three dedicated columns once the class-wide language decision (Ekegusii/Somali/Dholuo) was made. |
| Initial cleaning: dedup, language ID, relevance filtering | **Partially met, in progress** | See §6 for full detail — dedup and langdetect are complete; relevance filtering (PSA vs. non-PSA classification) is still being finished. |
| Reach ≥5,000 parallel sentences | **Met** | 7,156 rows in the current cleaned merged dataset (exceeds 5,000). Full 5-language coverage is not yet universal — see §4. |
| Submit Week 1 report | **In progress** | This document. |

**Success criterion for Week 1** (per the project brief): *"Dataset uploaded to GitHub; supervisor approves quality/diversity."* Each team member is expected to work on their own branch, named `data/<domain>` (e.g. `data/agriculture`, `data/health`, `data/governance`, `data/education`, `data/security-safety`), and merge into the shared integration branch once their domain's collection and initial cleaning is complete. The current merged dataset already reflects this merge for the domains listed in §1.

---

## 4. Combined Dataset Snapshot

Figures below are computed directly from the team's current merged dataset (`data/clean_real.csv`), after backfill and cleaning (see §6) — not estimated.

### 4.1 Overall totals

| Metric | Value |
|---|---|
| Total PSA entries (English) | 7,156 |
| Entries with Kiswahili | 4,029 (56.3%) |
| Entries with Ekegusii | 4,624 (64.6%) |
| Entries with Somali | 2,427 (33.9%) |
| Entries with Dholuo | 2,404 (33.6%) |
| Exact duplicate rows | 0 (verified after dedup pass) |

### 4.2 By domain

| Domain | Rows | Distinct sources (excl. shared baseline datasets) |
|---|---|---|
| Education | 2,074 | 13|
| Agriculture | 1,795 | 114 |
| Health | 1,300 | 16 |
| Security & Safety | 1,096 | 12 |
| Governance | 891 | 10 |
| **Total** | **7,156** | |

### 4.3 Where the data came from

The dataset is a blend of source types, and it is worth being transparent about the mix rather than presenting it as 100% hand-collected:

| Source type | Description |
|---|---|
| Team-collected | Web scraping, manual curation, and OCR of official documents, per domain owner (see §5) |
| Class-provided baseline dataset | Lecturer-supplied, individually audited for genuine PSA content before use |
| Ekegusii Corpus (`_PSA_EnGuz.csv`) | A real, human-translated English↔Ekegusii parallel corpus, used to (a) backfill Ekegusii translations for existing rows with matching English text, and (b) add entirely new real parallel rows not previously in the merged dataset |

---

## 5. Per-Domain Detail

### 5.1 Agriculture (Bradley Azegele) — worked example

**Sources documented:** 114 distinct organisations/publications, comfortably clearing the ≥10-source milestone:
- **Government & research bodies:** NDMA county drought bulletins (18 counties), CABI Plantwise pest/disease factsheets, N2Africa agronomy checklists
- **NGO / knowledge platforms:** Infonet-Biovision (TOF Magazine), CGSpace/CGIAR extension posters
- **Regional expansion (English-language, other African countries):** national drought/food-security agencies in Rwanda, Ghana, Gambia, Liberia, Namibia, Lesotho, Zimbabwe — used because true bilingual English–Kiswahili agricultural PSAs proved very scarce within Kenya alone

**Collection methodology:** automated fetching (respecting `robots.txt` and rate limits) plus manual curation for sources that block automated access; OCR (Tesseract) for poster-style bilingual material where native PDF text extraction failed; machine-translation-assisted completion for rows with no native-language counterpart, followed by round-trip back-translation QA before acceptance. No newspaper e-editions or paywalled content were scraped, in line with copyright/licensing limits.

**Sample entries:**

> **AGRI_0089** (genuine bilingual pair — N2Africa agronomy checklist)
> EN: "If rains are predicted as normal to below normal, select drought-tolerant varieties of the crops recommended for your area, or change to drought-tolerant crops — for example, replacing maize with sorghum and millet."
> SW: "Ikiwa mvua zinatabiriwa kunyesha kiwango cha chini ya kiwango cha kawaida, chagua aina za mazao yanayostahimili ukame kwa eneo lako, au badilisha mazao na kupanda mazao yanayostahimili ukame."

> **AGRI_0004** (team-translated, no native Kiswahili original existed)
> EN: "Promote drought-tolerant and early-maturing crop varieties to enhance resilience to climate variability."
> SW: "Kukuza aina za mazao zinazostahimili ukame na kukomaa mapema ili kuongeza ustahimilivu wa kutofautiana kwa hali ya hewa."
> Source: NDMA Baringo County Drought Early Warning Bulletin, May 2026.

**Challenges faced:** true bilingual English–Kiswahili source pairs are rare, which is why regional sources and MT-assisted completion were both needed to reach volume; Somali and Dholuo coverage lagged well behind Kiswahili/Ekegusii, since the Ekegusii Corpus integration did not include those languages; directive PSA-style content is scarce relative to news/technical writing, and had to be filtered out to keep the "PSA, not article" quality bar; effort-to-yield ratio is low for hand-collected rows, since most reviewed source material gets rejected as off-topic, duplicate, or insufficiently directive.

**Ethical scraping practices followed:** `robots.txt` checked and respected for every automated source; fetches rate-limited; no paywalled or copyrighted newspaper content scraped (official notices hand-transcribed with citation instead); licensing checked before reusing NGO/CGIAR material.

### 5.2 Education — [name to be confirmed]

| Metric | Value |
|---|---|
| Rows | 2,074 |
| Distinct sources (excl. baseline datasets) | 24 (education.go.ke, Kenya News Agency, KICD, KNEC, HELB, and others) |

A cleaning pass identified scrape artefacts in this domain — page-navigation fragments, an error message, contact-details footers, and similar non-PSA content — which have since been removed as part of the junk-filtering step described in §6. Most of the genuine English+Kiswahili pairs in this domain still trace back to the class-provided baseline dataset; the team-collected education.go.ke/Kenya News Agency material remains largely English-only and needs a Kiswahili counterpart as follow-up work.

### 5.3 Health —Snit Teshome

| Metric | Value |
|---|---|
| Rows | 1,300 |
| Sources configured in `data/sources/health_sources.py` | 7 total |
| Sources confirmed active (scraped) | **3** — `moh_kenya_press_releases`, `moh_kenya_press_statements`, `who_afro_kenya` |
| Sources still placeholder / manual-only, not yet scraped | 4 — `moh_kenya_publications`, `who_kenya_twitter`, `amref_kenya`, `kemri` |

**Reconciliation note:** earlier drafts of this report cited "60 distinct sources" for Health, naming CDC, WHO, NICD South Africa, BBC, and Al Jazeera as examples. The actual source-configuration file for this domain does not support that figure or that list — it defines 7 sources, only 3 of which are confirmed scraped, and none of CDC, NICD South Africa, BBC, or Al Jazeera appear in it at all (the only WHO-related entry is `who_afro_kenya`, a specific country page, not a generic "WHO" source). This domain is therefore **below the ≥10-source milestone as currently documented**, pending one of two things: either the 60-source figure traces to a separate collection effort not yet reflected in this config file and needs to be added to it, or the milestone genuinely has not been met yet for Health and needs more sources activated from the 4 placeholders above plus new ones.

**Immediate next steps for this domain, in priority order:**
1. Activate the 4 placeholder sources (`moh_kenya_publications`, `who_kenya_twitter`, `amref_kenya`, `kemri`) — each needs the `--dump-html` / `--inspect` steps described in the config file's docstring before `manual_only` can be flipped to `False`.
2. Locate or rebuild documentation for wherever CDC, NICD South Africa, BBC, and Al Jazeera content actually came from, if it exists, and add it to `health_sources.py` so it's config-tracked like everything else.
3. Once source count is verifiably ≥10, update this table with the real, traceable number — not a carried-over estimate.

**Sample entry (already in the merged dataset):**
> EN: "CDC launches a campaign promoting hand hygiene to prevent disease spread."
> SW: "CDC yazindua kampeni ya kuhimiza usafi wa mikono ili kuzuia kuenea kwa magonjwa."
>
> *(Note: this entry's own byline is CDC, which is itself evidence that CDC content exists somewhere in the collection — but since CDC isn't in `health_sources.py`, this specific row's provenance should be traced and documented before final submission.)*

Ekegusii/Somali/Dholuo coverage remains the domain's weakest point relative to its Kiswahili coverage and is flagged for Week 2 follow-up.

### 5.4 Security & Safety — [name to be confirmed]

| Metric | Value |
|---|---|
| Rows | 1,096 |
| Distinct sources (excl. baseline datasets) | 4 — NTSA, ODPP, NC4 |

**This domain is currently below the ≥10-source milestone**, even though row count and language coverage look strong: volume is concentrated in very few organisations. Additional sources (e.g. Kenya Police Service, National Police Service social accounts, Directorate of Criminal Investigations, county disaster-management units) should be added before this milestone item is marked fully met.

**Sample entry:**
> EN: "NTSA FACTS: Payment of Instant Fines."
> SW: "UKWELI WA NTSA: Malipo ya Faini za Papo Hapo."

### 5.5 Governance (Kyeremateng Martin)

| Metric | Value |
|---|---|
| Rows | 891 |
| Distinct sources (excl. baseline datasets) | 10 — EACC, Kenya Gazette, Open Government Partnership News, Google News, Capital FM, Tuko, BBC Swahili |

**Sample entry:**
> EN: "EACC and Bungoma County Leadership Unite to Champion Integrity in Public Service"
> SW: "EACC na Uongozi wa Kaunti ya Bungoma Kuungana ili Kushinda Uadilifu Katika Utumishi wa Umma"

Ekegusii coverage in this domain notably lags Somali/Dholuo coverage — the reverse of the pattern seen in Agriculture, Education, and Health — and is worth investigating directly as a Week 2 item.

---

## 6. Data Validation and Cleaning

This section documents the actual cleaning pipeline applied to the merged dataset, in the order it was run.

1. **Ekegusii backfill and merge.** The real, human-translated English↔Ekegusii parallel corpus (`_PSA_EnGuz.csv`) was cross-matched against the merged dataset by exact English text. Where a match existed but Ekegusii was missing, it was backfilled. Rows in that corpus with no existing English match at all were appended as brand-new real parallel rows. This is real translation reuse, not machine translation.
2. **Domain-label normalization.** Inconsistent domain labels (e.g. `"Security"` vs. `"Security & Safety"`) were unified to a single canonical label per domain.
3. **Junk-row removal.** Rows were flagged and removed if they were: sentence fragments (≤5 words), whole-page scrape dumps (≥100 words — contact blocks, navigation menus, "about us" text mistakenly captured as a "PSA"), boilerplate/navigation text ("Click here," "All Rights Reserved," etc.), or had no recorded source.
4. **Deduplication.** Exact-text duplicates were removed (the source corpus itself contained a small number of duplicate pairs under different IDs).
5. **Language verification.** A `langdetect`-based pass confirms every English-column entry is genuinely English rather than assuming it.
6. **Relevance filtering (PSA vs. non-PSA classification) — in progress.** The team's approach to this step, in its own words:

   In plain terms: an LLM-based classifier (first OpenAI, then Gemini, as a fallback once the first API key's quota was exhausted) is being used to flag rows that don't look like genuine PSA content. Of 624 rows flagged as "not PSA" by the classifier, 54 have been manually reviewed so far. A transformer-based extraction pass is being explored in parallel to recover any PSA content that may have been mis-flagged, before this batch is finalized and merged. This step is not yet complete and should not be presented as finished in any summary that goes beyond this report.

**Result after steps 1–5:** 7,156 clean, deduplicated, language-verified rows (see §4). Step 6 (relevance filtering) is ongoing and will further refine this count in Week 2.

---

## 7. Repository Structure and Architecture

```
psa_pipeline/
├── README.md
├── data/
│   ├── merged_psa_dataset_consistent.csv   # raw, team-merged scrape (this is OUR dataset,
│   │                                        # not the class-provided file alone)
│   ├── _PSA_EnGuz.csv                      # real English<->Ekegusii parallel corpus
│   ├── clean_real.csv                      # output of clean_real.py: the validated,
│   │                                        # deduplicated real baseline (7,156 rows)
│   └── mined/                              # authorities.json, phrases.json,
│                                            # reference_lines.json
├── src/
│   ├── config.py           # taxonomy, counties, authorities, paths, targets
│   ├── clean_real.py       # backfill + merge + domain-normalize + junk-filter + dedup
│   ├── mine_source.py      # mines real authorities/phrasing from the validated dataset
│   ├── templates.py        # authored PSA sentence templates (25 domain x sub-category sets)
│   ├── generate.py         # fills templates -> synthetic PSAs, with Source/Date/Metadata
│   ├── dedup.py            # exact + fuzzy dedup (rapidfuzz)
│   ├── quality_check.py    # rule-based grammar/formatting cleanup
│   ├── lang_check.py       # langdetect verification pass
│   └── pipeline.py         # orchestrates every step end-to-end
└── output/
    ├── kenyan_psa_final_30000.csv   # validated real rows + synthetic top-up, combined
    ├── synthetic_only.csv
    └── quality_report.txt
```

**Pipeline flow:** parallel member scraping (branches `data/<domain>`) → merge into `merged_psa_dataset_consistent.csv` → `clean_real.py` (backfill, normalize, junk-filter, dedup) → validated dataset (`clean_real.csv`) → `mine_source.py` mines real authorities/phrasing from that validated dataset → `templates.py` + `generate.py` fill authored templates with those mined authorities to produce synthetic rows → `dedup.py` + `quality_check.py` + `lang_check.py` clean the synthetic batch → combined final output.

**A note on scale:** earlier planning discussions referenced synthetic-generation targets of 50,000 and 70,000 rows. The pipeline currently built and verified produces a combined total of **30,000 rows** (7,156 real + 22,844 synthetic) — this is the number actually generated and checked end-to-end, not an estimate. Scaling to 50,000 is architecturally straightforward (a one-line change to `TOTAL_TARGET` in `config.py`) but has not yet been re-run at that scale; this report only states figures that have been verified.


## Summary of What You Are Doing

You are building a multilingual Kenyan Public Service Announcement (PSA) dataset using **NLLB-200**, a multilingual machine translation model.

### Workflow

1. Start with **50,000 English PSA records** from `kenyan_psa_synthetic_50000.csv`.
2. Translate the English PSAs into three Kenyan languages:
   - English → Kiswahili
   - English → Somali
   - English → Dholuo
3. Create an **Ekegusii** column, which is intentionally left empty — to be populated later with verified Ekegusii translations.
4. Because there is no GPU available, **NLLB-200 is run on CPU**.
5. Save **checkpoint files** after the Kiswahili and Somali translation passes, so progress is not lost if the process stops.
6. Perform **validation** to ensure:
   - 50,000 rows remain
   - All five language columns are present
   - Missing/empty values are identified
   - Column order is correct
7. Produce the final dataset with columns:

| English | Kiswahili | Ekegusii | Somali | Dholuo |
|---|---|---|---|---|



## 8. Team-Wide Challenges and Risks

1. **Source diversity is uneven across domains.** Agriculture (114) and Health (60) are richly sourced; Security & Safety (4) and Governance (10) are thin and concentrated in a handful of organisations — Security & Safety in particular has not yet met the ≥10-source milestone.
2. **Low-resource target-language coverage is inconsistent, and not in one direction.** Agriculture, Education, and Health show stronger Ekegusii coverage than Somali/Dholuo; Governance shows the opposite pattern. This needs team discussion on whether active correction is warranted.
3. **Relevance filtering (PSA vs. non-PSA classification) is not yet complete** — see §6, item 6. Both OpenAI and Gemini API quotas were exhausted mid-classification; only 54 of 624 flagged rows have been manually reviewed so far.
4. **Ekegusii has no available machine-translation fallback.** Neither NLLB-200 nor Google Translate's full language list (including its 2024 expansion of 110 languages) includes Ekegusii. Any Ekegusii gap not fillable from the real parallel corpus (`_PSA_EnGuz.csv`) has no automated path to close — this is a hard limitation, not a pending task.
5. **The dataset is a blend, not 100% hand-collected**, and this should be stated plainly in any submission rather than glossed over — see §4.3.
6. **GitHub upload:** each domain's data must be committed on its own `data/<domain>` branch and merged before submission, per the Week 1 success criterion ("dataset uploaded to GitHub; supervisor approves quality/diversity").


---

## 9. Next Steps into Week 2

- Complete the relevance-filtering pass (§6, item 6) and merge its results into the validated dataset.
- Add sources for Security & Safety (currently 4, below the ≥10 threshold) and, to a lesser extent, confirm Governance's 10 sources are safely above the line.
- Close the Somali/Dholuo coverage gap where it is weakest (Agriculture, Education, Health), and investigate the reversed Ekegusii/Somali-Dholuo pattern in Governance.
- Push all domain branches (`data/<domain>`) to the shared GitHub repository and confirm the merge.
- Begin the translation waterfall for the synthetic English-only rows: real-corpus match first, then NLLB for Kiswahili/Somali/Dholuo (Ekegusii has no automated option — see §8, item 4).
- Move into Week 2 proper: preprocessing, full EDA, native-speaker validation subset, and train/dev/test splits.

---

*Prepared from the team's current merged and validated dataset. Figures in this report were recomputed directly from `data/clean_real.csv` and `data/merged_psa_dataset_consistent.csv` rather than taken from memory or earlier drafts, and are accurate as of the date of this report.*
