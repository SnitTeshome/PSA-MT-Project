# `src/` — original Week 1 collection/generation pipeline

The scraping → clean → mine-authorities → generate-synthetic → dedup → quality-check
pipeline built for Week 1 (`docs/week_1_report_data_collection.md`), before the
later repository restructure introduced the numbered `data/01_collection/`…
`data/05_translated/` stages. Still runnable (`python3 pipeline.py`, see the root
`README.md` §10) and still the authoritative record of *how* the original synthetic
rows were generated (real-authority mining + hand-authored template filling), even
though day-to-day work since Week 1 has mostly operated on the datasets it produced
rather than re-running it directly.

| File | Role |
|---|---|
| `pipeline.py` | Orchestrates the full run |
| `config.py` | Shared configuration |
| `mine_source.py` | Mines real Kenyan issuing authorities/phrasing from the validated real dataset |
| `templates.py` | Hand-authored PSA templates (9-10 per sub-category) filled with mined authorities |
| `generate.py` | Fills templates → synthetic rows |
| `dedup.py` | Exact + fuzzy deduplication |
| `quality_check.py` | Rule-based quality checks |
| `generation/resources/` | Supporting data for template generation |
