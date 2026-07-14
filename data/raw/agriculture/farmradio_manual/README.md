# farmradio_manual/ — manual + scripted downloads from Farm Radio / Biovision

Cleaned and reorganized 2026-07-12. See `SOURCES.md` (parent folder) for the full
recon/provenance log. Two distinct source organizations feed this folder — don't
confuse them:

- **Farm Radio International** (`scripts.farmradio.fm`) — `farm_radio_scripts/`
- **Biovision Africa Trust / Infonet-Biovision** (`theorganicfarmer.org`,
  `infonet-biovision.org`) — `confirmed_pairs/`, `tof_magazine_en/`, `mkulima_mbunifu_sw/`

## confirmed_pairs/ — true English+Swahili parallel text (PSA-dataset-ready)

| File | Source | Direct URL |
|---|---|---|
| `tof-issue-no-17-septoct-2006-plant-extract-special-{english,swahili}-version.pdf` | Infonet-Biovision, TOF Magazine issue 17 special edition | https://infonet-biovision.org/tof-issue-no-17-septoct-2006-plant-extract-special-english-version and `-swahili-version` |
| `cgspace-climate-smart-agriculture-{EN,SW}.pdf` | CGSpace (CGIAR) — same poster already logged in `CGSPACE_FETCH_LIST.md` | https://cgspace.cgiar.org/items/62fd7239-9d39-4528-a513-5fb949251490 (EN) / https://cgspace.cgiar.org/items/c4d42102-1c9b-4936-b17b-7e2173964cda (SW) |
| `cgspace-soil-fertility-babati-{EN,SW}.pdf` — **not yet downloaded** (see `CGSPACE_FETCH_LIST.md`, CGSpace 429'd twice 2026-07-12 even via the KE tunnel) | CGSpace, found by searching the discover API for an English twin of a Kiswahili-only item | bitstreams `a8785e00-01cc-43ca-ae3b-9914fb532925` (EN) / `4ff8daa4-34bd-41af-9182-a0be12894492` (SW) at `https://cgspace.cgiar.org/server/api/core/bitstreams/<uuid>/content` — download from a browser |

**Promotion status (2026-07-14):** the TOF plant-extract pair has been promoted — 3 clean
recipe-level pairs (African marigold, sweet potato, tea) extracted into
`agriculture_psas.csv` as `AGRI_001`–`AGRI_003`. The CGSpace climate-smart-agriculture pair
was **not** auto-extracted: it's a multi-column infographic poster, and `pymupdf`'s reading
order fragments/reorders the "10 decisions" text in a way that risks silently mismatched
EN/SW sentence pairs if reflowed programmatically. It's still confirmed dataset-ready
material — just needs a person to read the two PDFs side by side and hand-pick aligned
sentences, rather than trusting an automated extraction.

**Farm Radio candidates QA + promotion status (2026-07-14):** ran
`scripts/qa_azure_language_check.py`-style Azure language detection over all 52 rows of
`_candidates_farmradio.csv` (both `sw_text` and `en_text` columns) as a pre-screen —
**0 flagged**, every row's language matches its column label with high confidence, so the
`fetch_farmradio.py` hreflang-based pairing produced no mislabeled pairs. 2 rows promoted
as a worked example: `AGRI_008`/`AGRI_009`, individual "Radio Spot #1"/"#2" units trimmed
out of row 1's post-harvest-losses script (a script can contain several distinct spots
delimited by `Radio Spot #N:` / `Kidokezo #N:` — extract one spot at a time, don't dump
the whole multi-spot script as one row). Only 1 of the 52 rows was checked for this exact
`Radio Spot #N` delimiter structure — **the other 51 still need a human trimming pass**
(some are interview/dialogue format, not spot format, so the extraction shape differs;
see fetch_farmradio.py's docstring for the article/dialogue HTML structure each came from).

The plant-extract pair is the **strongest find in this whole batch**: page-for-page
parallel, short directive recipes (PSA-shaped), fetched straight from the publisher's own
bilingual special edition (page 1 of the EN copy explicitly states "The Kiswahili version
of this Plant Extract Special has been published in The Organic Farmer..."). Fetched via
`scripts/collect/fetch_infonet_magazines.py` (see below) — robots.txt allows it, no CC
statement found but it's the publisher's own site, not a scrape of a third party.

The `cgspace-*` pair is the same material already recorded in `CGSPACE_FETCH_LIST.md` —
kept here as the actual downloaded PDF (browser download, since CGSpace blocks
datacenter IPs / 429s scripted fetches) rather than a duplicate discovery.

## tof_magazine_en/ — The Organic Farmer, English, monolingual

Started as 21 hand-downloaded issues; **bulk-fetch of the full ~226-issue archive was
kicked off 2026-07-12** via `fetch_infonet_magazines.py` (all TOF + MKM slugs in one run,
logged to a scratch file, not part of this repo). Check current counts with
`ls tof_magazine_en | wc -l` / `ls mkulima_mbunifu_sw | wc -l` — if the counts look
stalled partway through, the fetch either finished, was interrupted by a session/container
restart, or is still running; **re-running the same command is always safe** (fetchlib
caches every successful response in `data_cache/`, so a re-run just skips what's already
fetched and continues from where it stopped):
```
python scripts/collect/fetch_infonet_magazines.py --list tof > /tmp/tof_slugs.txt
python scripts/collect/fetch_infonet_magazines.py --list mkm > /tmp/mkm_slugs.txt
python scripts/collect/fetch_infonet_magazines.py $(cat /tmp/tof_slugs.txt /tmp/mkm_slugs.txt)
```
**Not parallel text** — TOF is English-only; do not pair these with Mkulima Mbunifu by
issue number, they are independently written sister publications, not translations.
Useful only as background/domain-vocabulary material, or if a specific article is later
hand-matched to a genuine Kiswahili equivalent.

Renamed to `tof-issue-<no>-<month><year>.pdf` using the issue number/date printed on each
PDF's own cover page (extracted via `pymupdf`, not guessed). Two numbering discrepancies
found in the **source's own printed text** (not a renaming error on our side) — flagged,
not resolved:
- Issue 229 is printed on both the September 2025 and December 2025 editions.
- Issue 219 is printed on both a Feb–Mar 2024 edition and an Apr–May 2024 edition.

Both issues in each pair are genuinely different content (different cover story, opening
paragraph) despite the shared issue number — likely a publisher-side numbering slip.

Fetchable by script: yes. `theorganicfarmer.org/robots.txt` has no disallow rules; every
issue page embeds a direct PDF link
(`https://theorganicfarmer.org/wp-content/uploads/<year>/<month>/<slug>.pdf`). Full
back-issue index (230 issues since 2005, 5 pages): https://theorganicfarmer.org/tof-magazine-issues/
— **note this is theorganicfarmer.org's own copy of the archive**; `fetch_infonet_magazines.py`
targets the infonet-biovision.org mirror instead (below), not this one directly.

There is also a **mirror archive on infonet-biovision.org** going back to 2005
(`tof-issue-no-<n>-<month>-<year>`, index: https://infonet-biovision.org/tof_magazine_issue)
— that's what `fetch_infonet_magazines.py` targets, and where the confirmed EN/SW pair
above came from.

## mkulima_mbunifu_sw/ — Mkulima Mbunifu, Swahili, monolingual

Started as 1 issue (No. 23, Agosti 2014); same 2026-07-12 bulk-fetch as TOF above covers
the full ~129-issue archive (`fetch_infonet_magazines.py --list mkm`). Tanzania-based
sister magazine, same caveat as TOF above: not a translation of TOF, don't pair by issue
number. Same Tanzania-vs-Kenya register caveat noted elsewhere in `SOURCES.md`.

## farm_radio_scripts/ — Farm Radio International, Swahili (.docx)

3 files, agriculture-relevant subset of what was originally dumped under
`NLP/Project/FarmRadio/` (the other 6 files there were a DRC/Togo health & gender
campaign, wrong language variant and wrong domain — deleted 2026-07-11, see git history/
prior conversation turn for that cleanup).

- `121-Radio-spots-on-agroecological-agriculture-SWAHILI.docx` — confirmed EN original at
  https://scripts.farmradio.fm/radio-script/radio-spots-agroecological-agriculture-tanzania/,
  Swahili at https://scripts.farmradio.fm/sw/mwongozo-wa-redio/matangazo-ya-redio-kuhusu-kilimo-cha-ikolojia-nchini-tanzania/
- `Farmers-adopt-biogas-to-protect-environment-relieve-burden-of-household-chores-Swahili.docx`
  — confirmed EN original (interview script, Rwenjojo/Karagwe, Tanzania, published 2025-04-15)
  at https://scripts.farmradio.fm/radio-script/farmers-adopt-biogas-to-protect-environment-relieve-burden-of-household-chores/,
  Swahili at https://scripts.farmradio.fm/sw/mwongozo-wa-redio/wakulima-kutumia-gesi-vunde-biogas-kulinda-mazingira-kupunguza-uzito-wa-kazi-za-nyumbani/
- `Swahili-Backgrounder-Community-forest-management.docx` — **correction**: the Zambia
  interview guessed earlier was wrong (that one's an interview, this file is a generic
  Backgrounder). Confirmed EN original at
  https://scripts.farmradio.fm/radio-script/community-forest-management/ (case studies from
  Nigeria's Ekuri Initiative and Kenya's Kipepeo Butterfly Project / Arabuko Sokoke Forest —
  the Kenya case study makes this one directly on-topic), Swahili at
  https://scripts.farmradio.fm/sw/mwongozo-wa-redio/taarifa-za-awali-usimamizi-wa-misitu-kwa-kushirikiana-na-jamii/

All 3 `farm_radio_scripts/` files now have confirmed EN+SW URL pairs — none remain unpinned.

**Correction (2026-07-12): Farm Radio IS scriptable.** The "not scriptable" claim below
was based on a bug, not an actual site policy — see the `fetchlib` fix in
`scripts/collect/README.md`. Licensing is still an open question (script pages carry no CC
statement — footer: "© Farm Radio International, All Rights Reserved" — confirm by email
before any redistribution beyond class use), but that's a reuse-rights question, not a
technical scraping block.

`fetch_farmradio.py --fetch-all kilimo` (run 2026-07-12) crawls the Swahili-locale
agriculture hub and follows each article's `hreflang="en-ca"` link to its guaranteed
English twin — every row it writes is a *confirmed* pair, not a guess. **Complete: 52/52
articles fetched, 0 failures.** Output: `../_candidates_farmradio.csv` (gitignored, sibling
to `SOURCES.md`) with columns `sw_url, en_url, sw_title, en_title, sw_text, en_text`. If you
run it again for a different topic (e.g. `afya` for health, `mazingira-na-mabadiliko-ya-
tabianchi` for environment/climate — both linked from the agriculture hub's sidebar, not
yet explored), note it **appends without deduping** — check for repeat `sw_url` values if
you re-run the same topic twice.

These are full script/dialogue-format text, not pre-trimmed PSA-length lines — human
review is required before promoting any row into `agriculture_psas.csv` (per the project's
own "never invent or paraphrase a translation" rule, and because a whole radio script is
usually too long — trim to the actual directive PSA-shaped sentence(s), don't copy the
whole dialogue in).

## Fetch tooling

`scripts/collect/fetch_infonet_magazines.py`:
```
python fetch_infonet_magazines.py --list tof   # print all ~226 TOF slugs
python fetch_infonet_magazines.py --list mkm   # print all ~129 MKM slugs
python fetch_infonet_magazines.py <slug> [<slug2> ...]   # download by slug
```
`scripts/collect/fetch_farmradio.py`:
```
python fetch_farmradio.py --list [topic]        # print SW article URLs (default: kilimo)
python fetch_farmradio.py --fetch-all [topic]   # crawl + pair + append to _candidates_farmradio.csv
```
Both route through `fetchlib.fetch_url()` (robots.txt check, rate limiting, caching) like
the rest of `scripts/collect/`.
