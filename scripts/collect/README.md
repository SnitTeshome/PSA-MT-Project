# Collection tooling

Hybrid collection per the project brief: automate what is scrapeable, curate the rest manually.
Either way, rows end up in your domain CSV and must pass `scripts/validate_psa_csv.py`.

## Scraping websites

Write one `fetch_<source>.py` per source and route all HTTP through
[`fetchlib.fetch_url()`](fetchlib.py) — it handles browser-like headers, robots.txt,
randomized rate-limiting, retries, and response caching (`data_cache/`, gitignored).
Parse with BeautifulSoup/lxml; extract PDFs with `pymupdf` (`fitz`).

- [`fetch_n2africa.py`](fetch_n2africa.py) — N2Africa's own extension-materials catalog
  (n2africa.org/agem, 80+ CC-licensed PDFs). Best source found so far: a genuine EN+Swahili
  bilingual checklist authored directly (no translation needed), Swahili-original brochures
  with no English counterpart, and a "Better [crop] through good agricultural practices"
  leaflet series repeated per country — that series shares a heavily templated intro/Step
  1-7 structure across countries for the same crop, so only country-specific passages
  (regional variety-selection guidance) are worth extracting per country, not the whole
  leaflet again. `--list [keyword]` prints the catalog filtered by title/country; pass a
  File-column value to download. Serves an incomplete cert chain, same as some Kenyan gov
  sites — fetches with `verify_tls=False`.
- [`fetch_cgspace.py`](fetch_cgspace.py) — CGSpace (CGIAR) bilingual advisory PDFs by
  bitstream UUID. Rate-limits hard and repeatedly (retested 2026-07-12, ~25 min after the
  prior 429 — same result) — treat every CGSpace file as a manual browser download for
  now, script only for text-extraction convenience once you have the bytes.
- [`fetch_infonet_magazines.py`](fetch_infonet_magazines.py) — TOF Magazine (English) /
  Mkulima Mbunifu (Swahili) back issues from Infonet-Biovision, CC-licensed, robots.txt
  allows it. `--list {tof|mkm}` prints all slugs; pass slugs to download. Output goes to
  `data/raw/agriculture/farmradio_manual/{tof_magazine_en,mkulima_mbunifu_sw}/` — see that
  folder's README for the confirmed En+Sw pairs found so far.
- [`fetch_farmradio.py`](fetch_farmradio.py) — Farm Radio International script pairs.
  robots.txt is actually wide open (`Disallow:` blank, `Crawl-delay: 10`) — see the
  `_robots_allows()` fix below, an earlier recon note calling this site
  robots-disallowed was wrong. Pairing trick: every script page emits a WPML
  `hreflang="en-ca"` alternate-language link, so crawl the *Swahili*-locale topic hub
  (`/sw/mada/<topic>/`, e.g. `kilimo` for agriculture — 6 pages, ~50 articles) instead of
  the ~94-page English hub, and follow hreflang to the guaranteed English twin. `--list
  [topic]` / `--fetch-all [topic]` (default topic `kilimo`). Writes a **candidate review
  CSV** (`data/raw/agriculture/_candidates_farmradio.csv`, gitignored) — same
  human-confirms-before-schema convention as `x_collect.py`.

**`fetchlib._robots_allows()` bug fixed 2026-07-12**: it used to fetch `robots.txt` with
bare `urllib.robotparser` (no headers), and some CDNs 403 headerless requests — Python's
robotparser fails safe on 401/403 by disallowing *everything*, which wrongly blocked
sites (Farm Radio) whose real robots.txt is wide open. Fixed to fetch robots.txt through
the same browser-header session as every other request.

Dependencies (all CPU-only, light): `pandas`, `requests`, `beautifulsoup4`, `lxml`,
`pymupdf`, `langdetect` (optional, enables the validator's language check).

## Collecting from X (Twitter)

Official gov/NGO X accounts are a rich PSA source and often post both English and
Kiswahili. The official API is paid, so options in order of preference:

1. **Manual copy** — posts are short; paste text + post URL into the CSV. Fastest for
   tens of PSAs per account.
2. **[twscrape](https://github.com/vladkens/twscrape)** via
   [`x_collect.py`](x_collect.py) — async scraper that works through real X accounts:
   - `pip install twscrape` (pure Python, httpx-based)
   - You must add one or more X accounts: `twscrape add_accounts` then `twscrape login_accounts`
     (username, password, and the login email — accounts need an email that can receive
     verification codes).
   - **Use dedicated throwaway accounts only** — scraping accounts get rate-limited and
     sometimes suspended. Never attach a personal account. **Warm the account up** (a week or
     two of light manual use) before pointing the scraper at it.
   - Store account credentials in a local `.env`/accounts db — never commit them.
   - X login flows change often; expect breakage and pin a recent twscrape version.
   - `x_collect.py` builds in human-like traffic: randomized think-time (right-skewed),
     occasional longer "reading" dwells, randomized account/action order, per-session time
     and post caps, and periodic long breaks. Set `FETCH_PROXY` if a proxy is needed.
     Verify the pacing logic with `python scripts/collect/x_collect.py
     --dry-run` (no network/accounts needed). Output is a **candidate review CSV**
     (`_candidates_x.csv`, gitignored) — a human confirms true En+Sw pairs before they enter
     the schema file; the script never invents pairings.
3. **Wayback Machine** snapshots of account pages (no auth; patchy coverage):
   `http://web.archive.org/cdx/search/cdx?url=twitter.com/kilimoKE/status/*&output=json`

## Sites that are strict about rate limits or connection type

A few gov sites (e.g. `kamis.kilimo.go.ke`) are picky about connection type or rate-limit
hard. If a fetch keeps failing, either collect that source manually from a browser, or set
`FETCH_PROXY=socks5h://host:port` to route through a different connection
(SOCKS URLs need `pip install "requests[socks]"`; unset = direct connection).

## Ground rules

- Respect robots.txt and rate limits (fetchlib enforces both).
- Record the exact URL in `Source` for every row — mandatory.
- Never invent or paraphrase a translation: if a PSA has no published Kiswahili (or
  English) counterpart, it does not go in the dataset.
- Cache raw fetches; iterate on parsers offline.
