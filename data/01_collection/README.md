# `01_collection/` — raw per-domain collection

Stage 1 of the restructured (`main`-branch) pipeline: raw scraped/collected PSAs per
domain, before cleaning. Roughly mirrors `data/raw/<domain>/`'s role in the
`data/agriculture`-branch convention (see `data/README.md`) — this is the same kind
of material, organized under the later repository restructure's naming instead.

Files here are per-domain exports at various stages of manual cleanup (e.g.
`Education_psas.csv` → `education_psas_clean.csv` → `ed_psas_clean.csv`) rather than
a single canonical file per domain — treat the most recently modified / most-cleaned
variant per domain as authoritative, and see `docs/week_1_report_data_collection.md`
and `docs/week_2_report_EDA_and_data_cleaning.md` for which counts/files the
week-by-week reports actually cite.

Feeds into `02_preprocessed/`.
