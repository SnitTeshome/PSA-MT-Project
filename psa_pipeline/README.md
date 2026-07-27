# Kenyan PSA Synthetic Dataset Pipeline

Generates a 70,000-row dataset of realistic, Kenyan Public Service
Announcements (PSAs) in English, for the DSA 4020A multilingual PSA
translation project. Built using your group's scraped CSV as reference
material (mined for real Kenyan authorities and phrasing patterns), not
as a direct source of output rows -- the scraped file mixed genuine PSA
text with noise, truncated fragments, and plain news reporting, so it is
used here purely to seed a template-based generator with realistic,
Kenya-specific vocabulary.

## Output

`output/kenyan_psa_synthetic_70000.csv` -- 70,000 rows, columns:
`PSA_ID, Domain, English`

Ready to hand to your translation step (Kiswahili, Ekegusii, Somali,
Dholuo).

Also produced: `output/quality_report.txt` -- summary of the automated
quality-check pass.

## How it works (modular pipeline)

```
src/config.py          Shared constants: taxonomy (5 domains x 5 sub-
                        categories, matching PSA_Categories_topics.pdf),
                        47 Kenyan counties, contact channels, targets.

src/mine_source.py     Step 1. Filters the noisy scraped CSV down to
                        genuine PSA-like lines, and mines real Kenyan
                        issuing authorities + phrasing patterns per
                        domain. Writes data/mined/*.json.

src/templates.py       Authored PSA sentence templates + topic/action
                        vocab, one set per (Domain, Sub-Category).

src/generate.py        Step 2. Fills templates with mined authorities +
                        counties/months/topics to synthesize unique PSAs,
                        2,800 per sub-category (25 sub-categories x 2,800
                        = 70,000).

src/dedup.py            Step 3. Exact dedup + conservative near-duplicate
                        dedup (rapidfuzz, blocked by Domain/Sub-Category,
                        threshold 99). County/month variation of the same
                        campaign is treated as legitimate diversity, not
                        duplication -- real PSA campaigns really do repeat
                        per county.

src/quality_check.py   Step 4. Rule-based cleanup: fixes double spaces,
                        spacing before punctuation, capitalisation,
                        missing terminal punctuation, a/an. Flags (and
                        drops) any row with an unresolved placeholder or
                        that's too short to be a real PSA.

src/pipeline.py         Orchestrates all of the above end-to-end, and
                        tops up generation automatically if dedup/QC
                        drop the count below 70,000, so the final file
                        always lands on exactly 70,000 rows.
```

## Running it yourself

```bash
cd src
python3 pipeline.py
```

Requires: `pandas`, `numpy`, `rapidfuzz` (`pip install rapidfuzz`).

To re-run an individual step (e.g. after editing templates.py):
```bash
python3 mine_source.py     # only needed if you change data/merged_psa_dataset.csv
python3 generate.py
python3 dedup.py
python3 quality_check.py
```

## Important limitation: grammar checking

This was built in a sandboxed environment with no internet access to
LanguageTool's server and no Java runtime, so a full grammar checker
(`language_tool_python`) could not reliably run here. Since every
sentence is machine-generated from hand-authored, already-grammatical
templates, `quality_check.py` instead does targeted, rule-based checks
for the specific mechanical issues slot-filling can introduce (double
spaces, article agreement, stray placeholders, punctuation/capitalisation).
Two subject-verb agreement bugs found during testing (e.g. "eye and
dental camps is available") were fixed directly in the templates.

If you want a broader LanguageTool pass on top of this, install it in an
environment with internet/Java access and run it over the final CSV --
the data is already clean enough that this should be a fast pass, not a
rewrite:
```bash
pip install language_tool_python
```

## Design notes / things worth knowing before you translate

- Authorities are domain-specific and were mined from your actual scraped
  data (filtered for genuine Kenyan public bodies) plus a curated list of
  well-known real Kenyan authorities per domain, so they should read as
  plausible.
- Every row is unique text (verified: 70,000 unique `English` values,
  70,000 unique `PSA_ID`s, no nulls).
- Domain counts are roughly balanced (~14,000 each across the 5 domains).
- Because generation is combinatorial (template x authority x county x
  month x topic), expect to see the same *sentence structure* reused
  across different counties/months -- this mirrors how real government
  PSA campaigns actually work (same message, rolled out county by
  county), rather than being a flaw.
- `data/mined/reference_lines.json` keeps a small sample of the cleanest
  real PSA-like lines found in your scraped CSV, purely for your own
  sanity-checking of tone -- these were never copied into the final
  dataset.
