# `02_preprocessed/` — cleaned and partially-translated intermediates

Stage 2 of the restructured pipeline. Contains cleaning outputs
(`clean_real_with_quality_labels.csv`, `validated_psas.csv`, `merged_psa_dataset.csv`)
and per-language production-translation intermediates produced later in the project
(`kenyan_psa_dholuo_nllb_15000_translated.csv`, `kenyan_psa_kiswahili_cloud_mt_15000_translated.csv`,
`kenyan_psa_ekegusii_kiswahili_15000_merged.csv`) — see
`docs/week4_swahili_dholuo_summary.md` for the methodology behind the translation
runs that produced these files.

Checkpoint files (`.{stage}_checkpoint.json`, hidden/dotfiles) let long-running
translation jobs resume after interruption without re-spending API quota — see the
corresponding script in `scripts/` for each (`translate_dholuo_nllb_bulk.py`,
`translate_kiswahili_cloud_mt_bulk.py`).

**The single canonical, final merged dataset lives in `data/processed/`, not here**
— these are working intermediates from the path that produced it.
