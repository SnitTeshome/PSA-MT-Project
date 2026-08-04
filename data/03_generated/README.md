# `03_generated/` — synthetic PSA generation output

Stage 3 of the restructured pipeline: synthetic English PSAs generated to close the
gap toward the project's ≥5,000-sentence-per-domain target after real collection fell
short (see `docs/week_1_report_data_collection.md` for the generation methodology —
mining real Kenyan issuing authorities and phrasing patterns out of the validated
real dataset, then filling hand-authored templates with those authorities plus
counties, months, and topics).

- `kenyan_psa_synthetic_15000.csv` / `kenyan_psa_synthetic_50000.csv` — successive
  batches at increasing target scale as the project's data needs grew.
- `generated_raw.json` — pre-CSV generation output, before dedup/quality-check.

Feeds into `04_quality_checked/`.
