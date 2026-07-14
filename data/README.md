# Data directory

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
| `Target_Language` | Leave blank for now (filled later) |
| `Source` | URL or source name — **mandatory, no exceptions** |
| `Date` | Date published/collected (`YYYY-MM-DD`) |
| `Metadata` | Tone, platform, urgency notes (e.g. `tone=advisory; platform=X; urgency=medium`) |

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

Start your domain file by copying the template header (delete the `EXAMPLE_000` row):

```bash
cp data/processed/psa_dataset_template.csv data/raw/<yourdomain>/<yourdomain>_psas.csv
```

Validate before committing:

```bash
python scripts/validate_psa_csv.py data/raw/<yourdomain>/<yourdomain>_psas.csv
```
