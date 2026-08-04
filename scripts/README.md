# `scripts/` — collection, cleaning, translation, QA, and eval scripts

Each script documents its own usage/requirements in its module docstring; this is a
map of what each one is for, grouped by pipeline stage. Cloud-API scripts need your
own credentials (env vars documented in each script) — none are included in this
repo.

## Collection & validation
| Script | Purpose |
|---|---|
| `collect/` | Per-source collection scripts — see `collect/README.md` |
| `validate_psa_csv.py` | Validates a domain CSV against the shared schema before committing |
| `append_real_sources.py` | Appends QA-filtered real PSA data on top of the synthetic base, with honest provenance labels |

## Cleaning & EDA
| Script | Purpose |
|---|---|
| `eda.py` | Week 2 EDA over collected PSA dataset(s), domain-agnostic |
| `preprocess.py` | Week 2 preprocessing skeleton — normalization, tokenization, code-switch flagging |
| `build_final_combined_dataset.py` | Builds the final combined dataset, merging per-language production files |
| `build_splits.py` | Builds provenance-stratified train/val/test splits per target language |
| `build_crossdomain_benchmark.py` | Builds the cross-domain (all 5 domains, not just Agriculture) backend-comparison benchmark |

## Translation & QA
| Script | Purpose |
|---|---|
| `translate_and_qa.py` | Fills a missing English/Kiswahili cell via multiple tools, picks the best by round-trip score |
| `qa_azure_language_check.py` | Language-detection QA gate using a cloud text-analytics API |
| `compare_backends.py` | Week 4 Kiswahili/Dholuo backend comparison on the cross-domain benchmark |
| `compare_somali_backends.py` | Somali backend comparison (NLLB-200 vs. cloud translation API) |
| `translate_dholuo_nllb_bulk.py` | Production bulk Dholuo translation (NLLB-200) |
| `translate_kiswahili_cloud_mt_bulk.py` | Production bulk Kiswahili translation (cloud API, NLLB-200 fallback) |
| `fill_remaining_gaps_nllb.py` | Fills every remaining translation gap (Somali/Dholuo/Kiswahili) with NLLB-200 |

## Modeling
| Script | Purpose |
|---|---|
| `finetune_nllb_ekegusii.py` | Fine-tunes NLLB-200 on English→Ekegusii with a new language tag |

## Infrastructure
| Script | Purpose |
|---|---|
| `runtime.py` | Detects hosted-notebook vs. Colab vs. local runtime, dispatches accordingly |

`scrub_vendor_names.py` was a one-off compliance-scrub utility for this
documentation pass (see its own docstring) — kept for now as a record of the scrub
patterns applied, not part of the regular pipeline.
