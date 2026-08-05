# `notebooks/`

| Notebook | Purpose | Executed in this repo? |
|---|---|---|
| `psa_cleaning_EDA.ipynb` | Week 2 EDA and cleaning (`docs/week_2_report_EDA_and_data_cleaning.md`) | — |
| `Merge_Real_Synthetic_PSA_Drive.ipynb` | Merges real + synthetic PSA datasets | — |
| `PSA_Week3_Modeling_TransferLearning44.ipynb` | mT5/NLLB fine-tuning, lighter config: 3 epochs, 4,000-row few-shot subset (`docs/week_3_report_model_building.md`) | **Yes** — outputs in `results_week3/`, `translate_psa.py`, `psa_main_transformed.csv` |
| `full_pipeline/` | mT5/NLLB fine-tuning, full-scale config: 5 epochs, full dataset, domain breakdown, ablation, COMET — see `full_pipeline/README.md` | **Yes** — this is the run `docs/results_summary.md` cites |
| `PSA_Translate_FromDriveToAnyone.ipynb` | Standalone inference demo, downloads pre-trained checkpoints from an external shared folder | **No** — unexecuted; depends on an external link staying live, no fallback documented. `../demo/app.py` is a self-contained alternative. |
| `Translate_Ekegusii_FULL_RUN.ipynb` | Full Ekegusii translation run | — |

The "Executed?" column is called out explicitly because it matters for
reproducibility — see `README.md` §11 ("Known gaps toward full reproducibility") for
the one notebook that still isn't, and why the two mT5/NLLB runs above report
different numbers for the same task.
