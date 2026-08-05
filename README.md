# DSA4020_PSA_Project_G1
## Kenyan Multilingual PSA Machine Translation

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Languages](https://img.shields.io/badge/languages-EN%20%C2%B7%20SW%20%C2%B7%20Ekegusii%20%C2%B7%20Somali%20%C2%B7%20Dholuo-informational)
![Status](https://img.shields.io/badge/status-Week%204%20complete-success)
![Docs](https://img.shields.io/badge/docs-comprehensive-brightgreen)

**DSA 4020A — Natural Language Processing | Semester Project**

- Prepared under the supervision of Dr. Edward Ombui

A proof-of-concept multilingual machine translation (MT) system for Kenyan Public Service Announcements (PSAs) — translating between English/Kiswahili and selected under-resourced indigenous languages, and deploying the result as a working demo.

> **The group tried multiple modeling approaches in parallel and tracks all of them in full, not just the "winning" one** — pretrained-model fine-tuning (mT5/NLLB) and dictionary-prompted LLM translation. See [§8](#8-week-3--modeling-with-transfer-learning) and [`docs/results_summary.md`](docs/results_summary.md) for every metric reported, on a shared BLEU basis wherever the raw outputs allowed recomputing it.

### Quick navigation

| Want to... | Go to |
|---|---|
| See every result, every metric, both approaches | [`docs/results_summary.md`](docs/results_summary.md) |
| Read the full experiment log (24 sections, warts and all) | [`docs/ekegusii_transfer_learning.md`](docs/ekegusii_transfer_learning.md) |
| Browse all documentation by week | [`docs/README.md`](docs/README.md) |
| Understand the dataset / reproduce it | [`data/README.md`](data/README.md) |
| Run something yourself | [§10 below](#10-running-the-pipeline) |
| See what's honestly still incomplete | [§11 below](#11-known-gaps-toward-full-reproducibility) |

Every folder in this repo (`data/`, `docs/`, `scripts/`, `notebooks/`, `experiments/`,
`src/`) has its own `README.md` — open any of them on GitHub and you'll land on an
explanation of what's inside and how it connects to the rest, not a bare file list.

## Team Members — Group 1

| # | Name | ID Number |
|---|---|---|
| 1 | Snit Teshome | 670552 |
| 2 | Bradley Azegele | 668341 |
| 3 | Kyeremateng Martin | 669217 |
| 4 | Kemo Dibassy | 669111 |
| 5 | Samantha Nyatichi Masaki | 670455 |
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

```
PSA-MT-Project/
├── data/
│   ├── raw/<domain>/            # per-domain raw collection (Bradley's data/agriculture convention)
│   ├── 01_collection/ … 05_translated/   # numbered pipeline stages (Snit's restructure)
│   ├── processed/kenyan_psa_multilingual_dataset.csv   # canonical final dataset — see data/README.md
│   ├── splits/                  # train/dev/test splits
│   └── README.md                # full schema, provenance-tag meaning, acceptability rules
├── docs/                        # week-by-week reports + results (see §6-9 below)
├── notebooks/                   # EDA, modeling, translation-demo notebooks
│   └── full_pipeline/           # full-scale NLLB/mT5 training run (5 epochs, full dataset) + results
├── demo/                        # standalone Gradio translation demo (app.py + translate_psa.py)
├── scripts/                     # collection, cleaning, translation, QA, eval scripts
├── src/                         # original Week-1 scraping/generation pipeline (pre-restructure)
├── experiments/                 # fine-tuning experiment scripts
└── LICENSE                      # MIT
```

**Note on the two `data/` layouts**: this repo is the product of two branches merging —
`data/raw/…` + `data/processed/…` (built out on the `data/agriculture` branch) and
`data/01_collection/…05_translated/` (introduced by a later repository restructure on
`main`). Both now coexist after the merge. **`data/processed/kenyan_psa_multilingual_dataset.csv`
is the single canonical, final dataset** (29,609 rows, all four target languages —
Ekegusii, Kiswahili, Somali, Dholuo — 100% filled); the numbered `01_collection`…
`05_translated` stages document the restructured team's own processing path toward a
differently-shaped intermediate (`psa_main_transformed.csv`, referenced by
`docs/week_2_report_EDA_and_data_cleaning.md` and `docs/week_3_report_model_building.md`,
now present at `notebooks/psa_main_transformed.csv` alongside the executed Week 3 notebook).

## 6. Week 1 — Data Collection & Curation

Two independent Week 1 collection efforts exist in this repo's history: the original
merged/scraped dataset (7,156 rows, `docs/week_1_report_data_collection.md`) and a
later reprocessing pass (19,795 rows after cleaning, `docs/week_2_report_EDA_and_data_cleaning.md`
§1). See `data/README.md` for the schema and acceptability rules that governed
collection, and `docs/week_1_report_data_collection.md` for the full stats, per-domain
source counts, and documented challenges (uneven source diversity, encoding bugs,
missing dates).

## 7. Week 2 — Data Processing & EDA

`docs/week_2_report_EDA_and_data_cleaning.md`: 19,795-row cleaned dataset after
Unicode normalization, URL/handle/emoji stripping, dedup, and language-detection
filtering — 24.2% real-collected / 75.8% synthetic-generated, across 5 domains.

## 8. Week 3 — Modeling with Transfer Learning

Two modeling approaches were run by the group in parallel:
- **Fine-tuning**: mT5-small and NLLB-200-distilled-600M, English↔Kiswahili and English→Ekegusii, at two different scales:
  - `notebooks/PSA_Week3_Modeling_TransferLearning44.ipynb` (`docs/week_3_report_model_building.md`): lighter config, 3 epochs on a 4,000-row few-shot subset. Now executed with real, reproducible outputs (`notebooks/results_week3/`).
  - `notebooks/full_pipeline/` (`notebooks/full_pipeline/README.md`): the full-scale run, 5 epochs on the complete dataset, plus a per-domain breakdown, a freeze-vs-full-finetune ablation, and COMET scoring. Best result: mT5 few-shot fine-tune, 68.08 BLEU / 78.38 chrF++ (En→Kiswahili). This is the run cited in `docs/results_summary.md` — the lighter run's numbers are lower on the same task (see the full pipeline's README for the side-by-side and why).
- **Dictionary-prompted LLM, no fine-tuning** (`docs/ekegusii_transfer_learning.md`, `docs/week3_performance_summary.md`): outperformed every fine-tuned configuration tried, on Ekegusii specifically — 33.96 BLEU / 54.8 chrF at best (BLEU computed retroactively via `sacrebleu` on the saved outputs, same tool/method as the fine-tuning work, for a direct comparison), vs. mT5's 5.81 BLEU / 26.15 chrF++ on the same language. Corroborated independently by a teammate's own fine-tuning attempt on Kiswahili, which found the same fine-tuning-underperforms-zero-shot pattern.

**Full multi-metric results across every language and both efforts: `docs/results_summary.md`.**

## 9. Week 4 — Evaluation, Deployment & Documentation

- **Kiswahili/Dholuo/Somali production translation**: `docs/week4_swahili_dholuo_summary.md` — NLLB-200 wins for Somali (chrF 83.1) and Dholuo (chrF 53.7); a cloud translation API wins for Kiswahili (chrF 80.7) with NLLB-200 as an automatic fallback when the API's quota runs out.
- **Ekegusii cross-domain generalization**: `docs/ekegusii_transfer_learning.md` §22-23 — the dictionary-prompted mechanism was validated on Agriculture only (chrF 45-55); retested outside Agriculture it dropped to chrF 26.6, root-caused to a too-narrow retrieval bank, and partially fixed by widening it (chrF 38.6, still below the agriculture range — an open, quantified gap, not closed). **Why performance varies by domain**, broken out per-domain with real retrieval-bank row counts: `docs/results_summary.md`'s "Why cross-domain performance varies by domain" section.
- **Ekegusii production-run regression, root-caused and fixed**: `docs/ekegusii_transfer_learning.md` §24 — 3.9% of a 10,169-row batch came back degenerate after reusing a simplified prompt path under a compute constraint; root-caused (missing few-shot grounding) and 96.9% repaired with the full mechanism.
- **Deployment**: a working Streamlit translation demo exists for the dictionary-prompted Ekegusii mechanism (narrative and known limitations in `docs/ekegusii_transfer_learning.md` §19), plus a standalone Gradio demo for the mT5/NLLB fine-tuned models (`demo/`). Run-it-yourself instructions and current constraints for both: §10 below.
- **COMET**: now computed for both approaches — dictionary-prompted (72.20 general-vocab / 67.99 agriculture / 59.76 crossdomain) and mT5/NLLB (`notebooks/full_pipeline/results/*comet*.csv`). Scored human/native-speaker evaluation (also named in this project's rubric) is still not run by either effort — see `docs/results_summary.md` for exactly what is and isn't covered.

## 10. Running the pipeline

No single consolidated `requirements.txt` existed until this documentation pass;
one now exists at the repo root covering the union of what `scripts/`, `notebooks/`,
and `experiments/` actually import — see `requirements.txt`. Install with:

```bash
pip install -r requirements.txt
```

**Original Week 1 collection/generation pipeline** (`src/pipeline.py` — scrape → clean
→ mine authorities/phrasing → generate synthetic rows → dedup → quality-check →
language-check):

```bash
cd src
python3 pipeline.py
```

**Per-domain collection validation** (current convention, see `data/README.md`):

```bash
python scripts/validate_psa_csv.py data/raw/<yourdomain>/<yourdomain>_psas.csv
```

**Translation/QA scripts** (`scripts/`) each document their own required
credentials/environment variables in their module docstring — e.g.
`scripts/translate_and_qa.py`, `scripts/qa_azure_language_check.py`,
`scripts/compare_somali_backends.py`. None of the cloud translation/LLM API
credentials needed to *run* these scripts are included in this repo; you will
need your own.

**Running the demos.** Two interactive demos exist; neither has a single
top-level "get started" script, so use the instructions below rather than
searching for one.

- *Fine-tuned mT5/NLLB demo* (`demo/`) — fully self-contained, documented in
  `demo/README.md`:
  ```bash
  pip install -r demo/requirements-deploy.txt
  python demo/app.py
  ```
  Needs the fine-tuned model checkpoints (multiple GB, not committed to this
  repo) at `PSA-MT-Outputs/models/fine_tuned/mt5/` and
  `PSA-MT-Outputs-v2/models/fine_tuned/nllb/`; produce them by running the
  notebooks in `notebooks/full_pipeline/`, or point the path constants near
  the top of `demo/app.py`/`demo/translate_psa.py` at your own checkpoint
  directory.

- *Dictionary-prompted Ekegusii demo* (`docs/ekegusii_transfer_learning.md`
  §19) — the mechanism behind this project's best Ekegusii numbers (chrF
  54.8, recall 0.90). **Not runnable from this repo as committed.** Its code
  and dictionary data live in a private `ekegusii_internal/` folder that was
  deliberately never pushed here: the dictionary CSVs it depends on are
  paid, licensed personal-access material, not redistributable into a team
  repo (see §19's licensing note). Making this demo team-runnable needs an
  explicit decision first — either a smaller, redistributable dictionary
  subset, or each user obtaining their own access to the source dictionary.
  This is an open item, not a documentation gap — if you're looking for a
  setup script for this specific demo, that's why you won't find one yet.

## 11. Known gaps toward full reproducibility

Tracked honestly rather than glossed over — see `docs/results_summary.md` for the
full detail:

- ~~The Week 3 fine-tuning notebook committed to this repo has never been executed~~ — resolved: both `notebooks/PSA_Week3_Modeling_TransferLearning44.ipynb` (lighter config) and `notebooks/full_pipeline/` (full-scale) are now executed, with real outputs committed alongside each.
- The demo notebook (`notebooks/PSA_Translate_FromDriveToAnyone.ipynb`) depends on a specific external shared-folder link staying live, with no documented fallback. `demo/app.py` is a self-contained alternative that doesn't have this dependency, provided you have the model checkpoints locally (see `demo/README.md`).
- ~~`psa_main_transformed.csv`, the stated input to the Week 2/3 pipeline stages, isn't present in the repo under that name~~ — resolved, now at `notebooks/psa_main_transformed.csv`.
- ~~COMET ... haven't been run~~ — resolved for both approaches (§9 above). **Human/native-speaker evaluation** (also in this project's Week 4 rubric) is still not run by either effort — both sides currently substitute targeted manual spot-checks of small samples instead of a scored pass at 100+ sentences.
- The Ekegusii mechanism's cross-domain generalization fix narrows but does not close the quality gap vs. Agriculture (§9 above) — root-caused per-domain, not just observed, in `docs/results_summary.md`.
- A live-generation check on the full-finetune mT5 ablation checkpoint (`notebooks/full_pipeline/results/freeze_vs_full_ablation.csv`) found degenerate, repeating output on a real sentence despite a clean-looking automated score — see `notebooks/full_pipeline/README.md` for detail. Only one sample checked; not yet quantified how widespread this is.

## License

MIT — see [LICENSE](LICENSE).
