# Dictionary data (not included)

Required for the Ekegusii direction. Not included in this repo because it's
licensed, paid-access material: *Enchengeria -- EkeGusii Dictionary* (Ekegusii/
Kiswahili/English), Akama, Mecha, Otieno & Getenga, Kisii University, 2023,
ISBN 9789966082916 -- a personal paid-access download from the Kenya National
Library Service's digital library (`vtabu.knls.ac.ke`), not a free/open resource
despite some 2023 news coverage suggesting otherwise.

If you have your own access to this dictionary, place the CSV here as:

```
enchengeria_en_guz_lexicon.csv
```

with columns `english_gloss`, `word`, `english_pos` (gloss text, the Ekegusii
word, and its English part of speech).

If your copy lives somewhere else, point `lexicon_lookup.py` at it instead of
moving the file, by setting:

```bash
export EKEGUSII_LEXICON_PATH=/path/to/your/enchengeria_en_guz_lexicon.csv
```

Without this file, `EkegusiiTranslator()` raises `MissingDictionaryError` and
the app hides the Ekegusii direction rather than running without it -- see
`../../README.md` for why there's no degraded fallback mode for this specific
mechanism.
