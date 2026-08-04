# `data/processed/` — canonical final dataset

- **`kenyan_psa_multilingual_dataset.csv`** — the single canonical, final dataset
  (29,609 rows). All four target languages — Ekegusii, Kiswahili, Somali, Dholuo —
  are 100% filled. Full column schema, provenance-tag meaning, and acceptability
  rules: `../README.md` (the `data/` root README).
- **`psa_dataset_template.csv`** — reference example row showing the finished
  format's full column set. **For starting a new domain's raw collection CSV, only
  fill the 9 raw-collection fields** documented in `../README.md` — this template
  shows the downstream shape, not the collection-time shape.

See `docs/results_summary.md` for what metrics/quality checks this dataset has been
put through, and `docs/ekegusii_transfer_learning.md` / `docs/week4_swahili_dholuo_summary.md`
for how each language column was actually produced.
