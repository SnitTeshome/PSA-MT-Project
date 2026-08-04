# `05_translated/` — final translation stage output

Stage 5 (last) of the restructured pipeline — subfolders hold per-language and
per-notebook translation outputs from the Week 2/3 modeling work
(`docs/week_2_report_EDA_and_data_cleaning.md`, `docs/week_3_report_model_building.md`):

- `ekegusii/`, `kiswahili/` — per-language split outputs.
- `data_processed/` — EDA summary and dev/test/train splits referenced by the Week 3
  modeling notebook (`notebooks/PSA_Week3_Modeling_TransferLearning44.ipynb`).

**This is a different lineage from the canonical `data/processed/kenyan_psa_multilingual_dataset.csv`**
(built on the `data/agriculture`-branch path) — see `data/README.md` for which file
is the single source of truth for the finished, all-languages-filled dataset.
