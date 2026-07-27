# Data directory

**Pivot (2026-07-22, lecturer-asserted): the whole class now targets Ekegusii, not a
per-group variable third language.** The schema's target-language column is now named
`Ekegusii` directly (renamed from `Target_Language`) to reflect that. See
`data/raw/agriculture/EKEGUSII_CORPUS_IMPORT.md` for the first Ekegusii-labelled data
brought into this domain and `docs/ekegusii_transfer_learning.md` for transfer-learning
planning now that the target is fixed.

Layout agreed in the group instructions:

```
data/
├── raw/                 # one folder per domain — put your collected PSAs here
│   ├── health/
│   ├── agriculture/
│   ├── education/
│   ├── security/
│   └── governance/
└── processed/
    └── psa_dataset_template.csv   # shared CSV template — copy this to start your domain file
```

## Schema — every field must be filled

| Field | Must include |
|---|---|
| `PSA_ID` | Unique ID, `<DOMAIN>_###` (e.g. `AGRI_001`, `HEALTH_001`) |
| `Domain` | Your assigned domain |
| `Sub_Category` | Specific sub-topic (e.g. Crop Production, Disease Prevention) |
| `English` | Exact English text as published |
| `Kiswahili` | Exact Kiswahili text as published (true parallel of the English) |
| `Ekegusii` | Leave blank for now (filled later), unless sourced/verified Ekegusii text is already on hand |
| `Source` | URL or source name — **mandatory, no exceptions** |
| `Date` | Date published/collected (`YYYY-MM-DD`) |
| `Metadata` | Tone, platform, urgency notes (e.g. `tone=advisory; platform=X; urgency=medium`) |

**Agriculture-domain extension (2026-07-27, not (yet) a team-wide decision):** the
Agriculture branch's `agriculture_psas.csv` additionally carries `Somali` and `Dholuo`
columns, both machine-translated via NLLB-200 and QA'd (Azure Translator as an
independent second opinion for Somali). This was Bradley's own call for his domain,
reasoning that both languages have real pretrained MT coverage unlike Ekegusii — **it
has not been proposed to or agreed by the rest of the team**, and `validate_psa_csv.py`
on the `data/agriculture` branch now hard-requires these two columns as a side effect.
If this script's changes ever get merged into `main` or another domain branch, that
requirement would incorrectly apply to health/education/security/governance CSVs too,
which don't have these columns — **flag this in any PR before merging**, don't let it
merge silently.

## Acceptability rules (from the group instructions)

- **Bilingual preferred**: the same PSA in both English and Kiswahili — a true parallel pair,
  not two unrelated messages.
- **Short and action-oriented**: instructs, warns, or advises the public.
- **Credible official source**: government agency, NGO, or verified media.
- **Not acceptable**: unsourced entries, long-form articles (news stories, technical reports).
- Aim for **diverse sub-categories** within your domain.

**Update (2026-07-14, lecturer-approved):** a single-language **English** source is now
acceptable when it is a certain, verifiable Kenyan PSA (official government advisory —
short, directive, public-facing — not a news story). Bilingual source pairs are still
**preferred and should be prioritised first**; English-only is the fallback for a source
that's clearly good enough to be worth including despite having no published Kiswahili twin.
For these rows, the Kiswahili column is filled with a **team translation** (not sourced from
the publisher) — mark this explicitly in `Metadata` (e.g. `translation=team, source_lang=en`)
so it's never confused with a source-published parallel pair.

**New (2026-07-22): `scripts/translate_and_qa.py`** does the team-translation step for you —
compares NLLB-200, OPUS-MT, and Azure Translator per row, picks whichever back-translates
closest to the original (no gold reference exists, so this is a heuristic proxy, not a
BLEU claim), and tags `Metadata` with `translation=team; qa_tool=...; qa_roundtrip=...`.
**Still read a sample of the output yourself** before treating it as final — this
automates the *first pass*, not the human check. Needs your own Azure Translator resource
(free F0 tier is enough — see the script's docstring for setup). Run it on any domain's
CSV, or add `--recheck-team` to re-validate rows someone already hand-translated.

Start your domain file by copying the template header (delete the `EXAMPLE_000` row):

```bash
cp data/processed/psa_dataset_template.csv data/raw/<yourdomain>/<yourdomain>_psas.csv
```

Validate before committing:

```bash
python scripts/validate_psa_csv.py data/raw/<yourdomain>/<yourdomain>_psas.csv
```
