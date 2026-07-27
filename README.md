# DSA4020_PSA_Project_G1
## Kenyan Multilingual PSA Machine Translation

**DSA 4020A — Natural Language Processing | Semester Project**

- Prepared under the supervision of Dr. Edward Ombui

A proof-of-concept multilingual machine translation (MT) system for Kenyan Public Service Announcements (PSAs) — translating between English/Kiswahili and selected under-resourced indigenous languages, and deploying the result as a working demo.

## Team Members — Group 1

| # | Name | ID Number |
|---|---|---|
| 1 | Snit Teshome | 670552 |
| 2 | Bradley Azegele | 66834 |
| 3 | Kyeremateng Martin | 669217 |
| 4 | Kemo Dibassy | 669111 |
| 5 | Samantha Nyatichi Masaki | — |
## 1. Project Overview

**Goal:** build a deployable digital public good that translates PSAs between English/Kiswahili and under-resourced Kenyan languages — Ekegusii (Bantu), Dholuo (Nilotic), and Somali (Cushitic) — demonstrating few-shot cross-lingual transfer learning on a curated, domain-specific PSA dataset.

**What is a PSA?**
A Public Service Announcement is a short, clear, action-oriented — and sometimes urgent — message that informs, warns, or guides the public about something they should do (health measures, safety advisories, deadlines, disaster alerts). Tone is typically directive or advisory, and PSAs are usually produced without commercial intent by government agencies, NGOs, or media outlets.

Examples:
- "IEBC reminds voters to verify their details via SMS."
- "Ministry of Health: Avoid unnecessary travel to Ebola hotspots."

**Team & Tools**
- Team size: 5 students
- Duration: 4 weeks
- Stack: Python (Hugging Face, pandas, BeautifulSoup, Selenium), MT evaluation libraries (BLEU/chrF/COMET/SacreBLEU), Streamlit/Gradio for deployment.

## 2. Sub-Objectives

| # | Sub-objective | Points |
|---|---|---|
| 1 | Curate a high-quality multilingual dataset (≥5,000 sentences per language pair) | 25 |
| 2 | Explore few-shot cross-lingual transfer using pre-trained models (mT5, NLLB, mBART, etc.) | 30 |
| 3 | Evaluate the model for accuracy and cultural appropriateness | 20 |
| 4 | Deploy the model as a digital public good | 15 |
| — | Overall quality, documentation & presentation | 10 |

## 3. Timeline & Milestones

**Week 1 — Data Collection & Curation (Sub-objective 1) — status: see §6**
- Identify and document ≥10 reliable sources (gov sites, X/Twitter, media archives, NGOs).
- Hybrid scraping pipeline (manual + automated; BeautifulSoup/Selenium; robots.txt & rate limits respected).
- Collect raw PSAs across Education, Health, Security, Agriculture, Governance.
- Structured dataset with columns: `PSA_ID, Domain, English, Kiswahili, Ekegusii, Somali, Dholuo, Source, Date, Metadata`.
- Initial cleaning: deduplication, language detection, relevance filtering.
- Reach ≥5,000 parallel sentences with basic validation.
- Submit Week 1 report (dataset summary stats, sample entries, challenges).

**Week 2 — Data Processing & EDA (Sub-objectives 1 & 2)**
- Preprocessing pipeline (tokenization, normalization, code-switching handling, cultural-term glossary).
- Full EDA: domain distribution, text length histograms, vocabulary size, language-pair stats.
- Native-speaker validation subset (~500 sentences) + feedback.
- Version-controlled cleaned dataset; train/dev/test splits.

**Week 3 — Modeling with Transfer Learning (Sub-objective 2)**
- Experiment tracking (Weights & Biases / MLflow).
- ≥2 pre-trained models fine-tuned few-shot (e.g. mT5-small, NLLB-200 distilled, mBART).
- Low-resource training techniques (layer freezing, data augmentation); ablations (zero-shot vs. few-shot, domain adaptation).
- Inference script + preliminary performance summary.

**Week 4 — Evaluation, Deployment & Documentation (Sub-objectives 3 & 4)**
- Automatic metrics (BLEU, chrF, COMET, SacreBLEU) + human evaluation (fluency, adequacy, cultural accuracy) on 100+ sentences.
- Error analysis and documented limitations.
- Web app deployment (Streamlit/Gradio): input PSA → select target language → output translation, with confidence scores and a feedback form.
- Final GitHub repo (code, dataset/link, notebooks, README, license) + final report + demo day.

## 4. PSA Domain Taxonomy

Every PSA is labeled with one of 5 domains and one of 5 sub-categories each (25 combinations total):

| Domain | Sub-Categories |
|---|---|
| Health | Disease Prevention & Control · Maternal & Child Health · Public Health Campaigns · Mental Health Awareness · Healthcare Access |
| Agriculture | Crop Production · Livestock Management · Agribusiness & Market Access · Sustainable Farming · Agricultural Training |
| Education | Access to Education · Vocational Training · Civic Education · Educational Resources · School Safety & Inclusion |
| Security & Safety | Public Safety Awareness · Crime Prevention · National Security · Gender-Based Violence · Cybersecurity |
| Governance | Anti-Corruption Initiatives · Public Participation · Elections & Voter Education · Public Service Delivery · Devolution & Local Governance |

## 5. Repository Structure
## 6. Current Status: Week 1

Individual scraping efforts fell short of the 5,000-sentence target on their own, so the team combined every member's output into one merged scraped dataset, backfilled it with a real Ekegusii parallel corpus, cleaned it, and built a pipeline that mines that validated data for real Kenyan authorities and phrasing to generate additional synthetic rows grounded in real-world material.

**Merged, Validated Dataset (`data/clean_real.csv`)**
- 7,156 rows, columns: `PSA_ID, Domain, English, Kiswahili, Ekegusii, Somali, Dholuo, Source, Date, Metadata`
- Domain split: Education 2,074 · Agriculture 1,795 · Health 1,300 · Security & Safety 1,096 · Governance 891
- Kiswahili filled for 56.3%, Ekegusii for 64.6%, Somali for 33.9%, Dholuo for 33.6% of rows
- Source documentation is uneven and still being finalized per domain — see `data/sources/` for the config-driven source lists (Health's config currently has 7 sources defined, 3 confirmed active)

**Final Combined Dataset (`output/kenyan_psa_final_30000.csv`)**
- 30,000 rows total: 7,156 real + 22,844 synthetic
- Synthetic rows: columns `PSA_ID, Domain, English, Source, Date, Metadata` (translation pending), balanced ~4,500–4,700 per domain
- 100% unique English text and PSA_ID across the combined file; zero nulls in PSA_ID/Domain/English
- Synthetic rows generated by mining real Kenyan issuing authorities and PSA phrasing patterns out of the validated real dataset, then filling hand-authored templates (9–10 per sub-category) with those authorities plus counties, months, and topics — followed by dedup, rule-based quality checks, and language verification

**Pipeline Architecture**

Parallel member scraping (branch per domain: `data/<domain>`) → merge → backfill/clean/validate → mine real authorities/phrasing → fill authored templates → generate → dedup (exact + fuzzy) → rule-based quality check → language verification → final combined dataset. The pipeline automatically tops up generation if dedup/QC drop the synthetic count below target.

Full details, summary statistics, sample entries, and challenges are in the Week 1 Report.

## 7. Running the Pipeline

```bash
cd src
pip install rapidfuzz langdetect pandas
python3 pipeline.py
```

To re-run an individual step:
```bash
python3 clean_real.py      # only needed if the raw merged CSV changes
python3 mine_source.py     # only needed if clean_real.csv changes
python3 generate.py
python3 dedup.py
python3 quality_check.py
python3 lang_check.py
```

## 8. Next Steps

- Reconcile documented source counts per domain against the actual `data/sources/*.py` config files (Health currently shows a gap between claimed and confirmed-active sources).
- Complete relevance filtering (LLM-based PSA/non-PSA classification, in progress).
- Translate the synthetic English PSAs into Kiswahili, Somali, and Dholuo (NLLB); Ekegusii has no automated MT option and depends on the real parallel corpus only.
- Move into Week 2: preprocessing, EDA, and train/dev/test splits.

## License
