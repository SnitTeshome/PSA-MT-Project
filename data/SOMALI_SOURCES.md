# Somali source recon (2026-07-12)

Context: the group has not yet formally chosen the third target language, but
[`language_choice_somali.md`](../../NLP/Project/language_choice_somali.md) (Bradley's
recommendation memo, private workspace doc, not in this repo) argues for Somali on
pretrained-model-coverage grounds (NLLB-200 `som_Latn`). Per that memo, `Target_Language`
stays **blank during Week-1 En+Sw collection regardless** — Somali translations get added
later, bootstrapped from NLLB-200 zero-shot + human verification. This doc is a first pass
at what real bilingual/monolingual Somali material exists, run with the same methodology as
the Kiswahili recon in `raw/agriculture/SOURCES.md`, so that work doesn't start from zero
whenever the group formally decides on the third language.

**Bottom line: nowhere near the volume or ease of the Kiswahili sources.** No exact analogue
of Farm Radio's Swahili-locale hub was found for Somali. The strongest concrete lead is
humanitarian/food-security bulletins (FSNAU, ReliefWeb/OCHA), not agriculture-extension
material — which fits, since Somalia's information ecosystem is much more shaped by
drought/famine response than Kenya's or Tanzania's farmer-extension publishing.

## Checked and ruled out

- **Farm Radio International** (`scripts.farmradio.fm`) — **no Somali-locale hub.**
  `/so/mada/kilimo/` 404s (Swahili's `/sw/` equivalent does not exist for Somali); no
  `/translations/somali/` page either (that URL pattern works for Swahili, Dholuo, Bemba,
  Sidamigna/Sidamo — Somali isn't among the ~26 translated languages the site lists).
  FarmRadio.FM does list 5 partner stations inside Somalia (Mustaqbal Radio, Nation FM
  Somalia, Radio Dalsan, Radio Rajo, Environmental Journalists for Somalia) at
  `https://farmradio.fm/broadcasters/somalia/`, but no script-translation output tied to
  them was found — worth a direct email query the same way `outreach_emails_draft.md` does
  for Kiswahili leads, but nothing to fetch yet.
- **Access Agriculture** — hosts training videos in ~100 languages; general-search
  confirmed no explicit Somali-language listing (their own PR copy names Arabic, Bangla,
  French, Hindi, Portuguese, Spanish, and various African languages, not Somali). Not
  ruled out with certainty — their site wasn't crawled directly (same 404 issue hit last
  session on `/videos-language/swahili` suggests the URL scheme needs discovery first) —
  flag as **unconfirmed, not exhausted**.
- **Somalia Ministry of Agriculture and Irrigation** (`moa.gov.so`) — real, current,
  reachable (HTTP 200). **English-only**, no language toggle found, weekly/monthly/annual
  report pages exist (`/weekly-report/`, `/monthly-report/`, `/press-release-4/`) but the
  one press release checked was English-only. Same pattern as Kenya's own gov agriculture
  sites and Tanzania's `kilimo.go.tz` — official-language sites default to English even
  where the national/majority language is not English.

## Real leads — humanitarian/food-security, not agriculture-extension

- **FSNAU (Food Security and Nutrition Analysis Unit, Somalia)** — historical proof that
  genuine En+So parallel PSA-shaped text gets published: a 2011 "UN Statement on Drought in
  Somalia" existed as two separate PDFs, one per language
  (`fsnau.org/downloads/Statement-on-Drought-in-Somalia-{English,Somali}-Version.pdf`).
  **Those exact 2011 links are now dead** (checked 2026-07-12: connection fails, not just
  404 — the old `fsnau.org/drought-alerts` page is itself a stale cache/snapshot). Worth
  checking FSNAU's current site structure directly rather than trusting that URL.
- **ReliefWeb (UN OCHA)** — recurring monthly "Somalia Humanitarian Bulletin" reports
  tagged **`[EN/SO]`** going back to at least 2018, e.g. `somalia-humanitarian-bulletin-
  january-2021-enso`. Content is drought/food-security/agriculture-adjacent (cereal
  production shortfalls, Desert Locust impact, seasonal rain failure) — same
  "news/situation-report ≠ PSA" caveat the group already applies to Tanzania's TSN papers
  applies here too, but these are UN OCHA situation reports, not press articles, so may sit
  closer to "official advisory" than "news." **Not yet scriptable**: the report pages
  return HTTP 202 with an empty body to a plain fetch (Cloudflare/JS-gate), and ReliefWeb's
  REST API v1 is decommissioned — v2 requires a registered `appname`
  (see `https://apidoc.reliefweb.int/parameters#appname`), which nobody has requested yet.
  **Next step, not done**: register an appname, then hit
  `https://api.reliefweb.int/v2/reports?query[value]=...` for structured bulletin data
  including attached file URLs.
- **FAO Somalia** — confirmed (via search, not directly crawled) that FAO Somalia produced
  COVID-19 infographics in both English and Somali as leaflets/posters — health domain, not
  agriculture, but proof FAO's Somalia office does publish bilingual PSA-shaped material.
  FAO also runs a permanent Desert Locust Monitoring Centre in Qardho (Bari region) — locust
  alerts are exactly PSA-shaped (short, directive, high-stakes) and a plausible source of
  bilingual material; publications page (`fao.org/somalia/resources/publications/en`) is
  JS-rendered and wasn't successfully crawled statically — needs a real browser/Selenium or
  manual browsing, not confirmed either way yet.

## Existing corpora (for model training/eval, not the hand-built PSA set)

Per `language_choice_somali.md`'s own citations — not re-verified here, just carried over so
this doc is a complete starting point:
- **SomaliWeb v1** (BBC Somali scrape, quality-filtered web corpus) — monolingual.
- **MATERIAL / LORELEI Somali representative language pack**, **OPUS**, **Global Voices
  parallel corpus** — these mix domains (news, weblogs), not agriculture/PSA-specific.
- Hugging Face Hub: ~250 Somali-tagged datasets as of Apr 2026 per the memo; none found in
  this pass that are agriculture-domain parallel PSA data specifically — this is a
  fine-tuning/baseline-data resource, not a PSA-collection source.

## Suggested next steps if the group confirms Somali

1. Register a ReliefWeb API `appname` and pull the full `[EN/SO]` Humanitarian Bulletin
   back-catalogue — highest-confidence lead by far, and scriptable once registered.
2. Email Farm Radio (`radio@farmradio.org`) asking whether any of the 5 Somalia partner
   stations have Somali-translated scripts not yet on the public site — mirrors the
   Kiswahili outreach-email approach already drafted for KALRO/Mediae.
3. Manually browse `fao.org/somalia/resources/publications/en` in a real browser (JS-gated,
   not scriptable as-is) for locust/drought bilingual leaflets.
4. Re-check `accessagriculture.org`'s actual language-listing URL scheme (unresolved 404
   from a stale guess) before concluding Somali isn't there.
