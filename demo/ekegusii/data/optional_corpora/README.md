# Optional extra retrieval corpora (not included)

Both files below widen the Ekegusii direction's retrieval bank beyond the
agriculture-only training split already committed to this repo
(`data/splits/agriculture/ekegusii_train.csv`). Neither is required -- without
them, the app still works using agriculture-domain data alone (see the folder
README one level up for what that means for translation quality on
non-agriculture phrasing). Neither is included here because both are
usage-restricted at their source, not because of anything project-specific.

## `ekegusii_kjv_aligned.csv` -- Ekegusii New Testament, aligned to KJV

Sourced from an archive.org scan; no explicit open-reuse license was found for
it. The KJV English side is public domain, but the Ekegusii translation itself
isn't confirmed open. Fine for research/coursework use with citation, not a
green light for bulk redistribution -- so it's kept out of this shared repo.
If you have your own copy, place it here with columns `text_en`, `text_guz`,
or point to it elsewhere via:

```bash
export EKEGUSII_BIBLE_CORPUS_PATH=/path/to/your/ekegusii_kjv_aligned.csv
```

## `psa_en_guz_parallel.csv` -- 5-domain PSA parallel corpus

A real parallel corpus (Education/Health/Agriculture/Security/Governance)
provided directly by the course lecturer for course use. Treated with the same
care as other lecturer-provided course material: fine to use as reference
material, not to be re-published outside the course context without checking
first -- so it isn't bundled in this public-facing folder. If you have your own
copy (e.g. from the course's shared materials), place it here with columns
`Domain`, `PSA_Id`, `en`, `guz`, or point to it elsewhere via:

```bash
export EKEGUSII_EXTRA_CORPUS_PATH=/path/to/your/psa_en_guz_parallel.csv
```
