# `docs/` — index

Two independent efforts ran through this project (see the root `README.md` for the
full picture) — this index groups their docs by week so you can follow either one,
or both, top to bottom.

## Week 1 — Data Collection
- [`week_1_report_data_collection.md`](week_1_report_data_collection.md) — collection stats, per-domain source counts, challenges.

## Week 2 — Processing & EDA
- [`week_2_report_EDA_and_data_cleaning.md`](week_2_report_EDA_and_data_cleaning.md) — cleaning pipeline, dataset stats, per-domain length distributions.

## Week 3 — Modeling with Transfer Learning
- [`week_3_report_model_building.md`](week_3_report_model_building.md) — mT5/NLLB fine-tuning results (BLEU/chrF++).
- [`ekegusii_transfer_learning.md`](ekegusii_transfer_learning.md) — the full Ekegusii experiment log (§1-24): fine-tuning attempts, the pivot to dictionary-prompted LLM translation, morphology hints, cross-domain generalization, and a production-regression root-cause + fix.
- [`week3_performance_summary.md`](week3_performance_summary.md) — the rubric-facing summary of the above, backend comparison table.

## Week 4 — Evaluation, Deployment & Documentation
- [`week4_swahili_dholuo_summary.md`](week4_swahili_dholuo_summary.md) — Kiswahili/Somali/Dholuo backend comparison and production translation runs.
- [`results_summary.md`](results_summary.md) — **every metric reported anywhere in this project**, one consolidated reference table across both efforts and all four target languages.

## Methodology deep-dives
- [`translation_qa_methodology.md`](translation_qa_methodology.md) — how team-translated rows were QA'd (round-trip back-translation scoring, what it got wrong).
- [`dedup_methodology.md`](dedup_methodology.md) — near-duplicate detection methodology (two independent approaches, compared).
- [`ekegusii_resource_bibliography.md`](ekegusii_resource_bibliography.md) — every linguistic resource (dictionaries, grammars, papers) consulted, with licensing status noted per source.
- [`week4_glossary_sourcing.md`](week4_glossary_sourcing.md) — where the Kiswahili/Dholuo bilingual glossaries used in prompting came from.

## Figures
`chart_avg_words_per_domain.png`, `chart_psas_per_domain.png`, `Data_Collection_Architecture.png`
