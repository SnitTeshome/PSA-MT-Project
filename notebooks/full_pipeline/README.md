# `notebooks/full_pipeline/`

The full NLLB/mT5 training pipeline: 5 epochs, full dataset, all four
Ekegusii-involving directions, plus a domain breakdown and a freeze-vs-full
fine-tuning ablation. This is a **different, heavier run** from
`notebooks/PSA_Week3_Modeling_TransferLearning44.ipynb` one directory up —
see "Two mT5/NLLB runs exist in this repo" below for why the numbers differ
and which one to cite.

## Contents

| File | What it does |
|---|---|
| `PSA_Dataset_EDA_modeling.ipynb` | Modeling-focused EDA — vocabulary/morphological complexity (informs `MAX_LEN`), duplicate/conflict checks, and a check for whether the train/dev/test split accidentally imbalances any domain. Complementary to `notebooks/psa_cleaning_EDA.ipynb` (general cleaning EDA), not a duplicate of it. |
| `01_NLLB_Transfer_Learning.ipynb` | NLLB-200-distilled-600M fine-tuning, English→Ekegusii and Kiswahili→Ekegusii, 5 epochs, full dataset. Executed, real outputs. |
| `02_mT5_Transfer_Learning.ipynb` | mT5-small fine-tuning: per-direction (frozen encoder), combined multi-directional, a domain-adaptation breakdown for both, and a freeze-vs-full-finetune ablation. 5 epochs, full dataset. Executed, real outputs. |
| `error_analysis.py` | Error-analysis script for model outputs. |
| `human_eval.py` | Human-evaluation scaffolding. |
| `requirements.txt` | Training dependencies (transformers, datasets, accelerate, mlflow, etc.). |
| `requirements-comet.txt` | `unbabel-comet` kept in a separate install on purpose — its pinned `pytorch-lightning`/`pandas` deps conflict with `requirements.txt` when resolved together. Install only when running the COMET cells, in its own `pip install -r requirements-comet.txt`. |
| `results/` | The small CSV results these notebooks produced — see below. |

## `results/`

| File | Contents |
|---|---|
| `master_results_table.csv` | Zero-shot vs. fine-tuned BLEU/chrF, NLLB and mT5, both Ekegusii directions |
| `nllb_complete_evaluation.csv` | NLLB 5-epoch run config + BLEU/chrF/COMET |
| `nllb_comet.csv` | NLLB COMET scores, 2 directions |
| `epoch_metrics.csv` | Real 5-epoch training curve, mT5 combined model |
| `mt5_selected_directions_final.csv` | mT5 frozen-encoder per-direction results (the "frozen" side of the ablation) |
| `mt5_combined_final.csv` | Combined multi-directional mT5 model, 3 directions |
| `mt5_perdirection_comet.csv` | mT5 COMET scores, 4 directions |
| `freeze_vs_full_ablation.csv` | mT5 full-finetune result, English→Ekegusii (see the quality caveat below) |
| `domain_ablation_table.csv` | NLLB + mT5 BLEU/chrF by domain, per-direction models |
| `mt5_domain_adaptation_per_direction.csv` | Same per-direction domain breakdown as above, mT5 only |
| `mt5_domain_adaptation_combined.csv` | Domain breakdown for the **combined** multi-directional mT5 model, including Ekegusii→Kiswahili — a direction not covered by the per-direction breakdown |

## Two mT5/NLLB runs exist in this repo

`notebooks/PSA_Week3_Modeling_TransferLearning44.ipynb` (one directory up)
and this folder both fine-tune mT5/NLLB on the same task, but at very
different scale, and they report different numbers as a result:

| | `../PSA_Week3_Modeling_TransferLearning44.ipynb` | This folder |
|---|---|---|
| Epochs | 3 | 5 |
| Training data | 4,000-row few-shot subset | Full dataset (46,832 rows for the English→Ekegusii direction alone) |
| mT5 En→Ekegusii result | 3.68 BLEU / 21.43 chrF | 13.85–15.42 BLEU / 36.36–38.01 chrF (per-direction / combined) |
| Domain breakdown, ablation, COMET | No | Yes |
| Training wall-clock (single A100) | ~23 min | ~170 min for the combined-model pass alone, more for per-direction + ablation |

The lighter run stayed in the repo as a documented, cheaper reproduction
path; this folder is the one to cite for the project's actual best mT5/NLLB
numbers, and the one `docs/results_summary.md` and `README.md` point to.

## A real quality caveat on the full-finetune ablation

`freeze_vs_full_ablation.csv` reports BLEU 12.93 / chrF 34.99 for the
full-finetune (not frozen-encoder) English→Ekegusii model — a real, clean
automated score. But a live demo-generation check on that exact checkpoint
(the same one the notebook's own test cell exercises) produced degenerate,
repeating garbage output instead of Ekegusii text, on a real held-out
sentence. Only one sample was checked, so the extent of the problem isn't
quantified — flagged rather than silently trusted, consistent with how this
project's other docs (`docs/results_summary.md`, `docs/ekegusii_transfer_learning.md`)
handle metric/output mismatches elsewhere. Don't cite this specific ablation
number as production-ready without a broader manual check first.

## Model checkpoints are not included

The trained model weights these notebooks produce (multiple GB across NLLB
and mT5, per-direction and combined) are not committed here — standard
practice for a git repo, and well beyond what's practical to version this
way. `demo/app.py` and `demo/translate_psa.py` (repo root) expect them at
`PSA-MT-Outputs/models/fine_tuned/` and `PSA-MT-Outputs-v2/models/fine_tuned/`
relative to wherever these notebooks are run — re-run the notebooks in this
folder to regenerate them, or point the demo scripts at your own checkpoint
directory.
