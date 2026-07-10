# Collection tooling

Hybrid collection per the project brief: automate what is scrapeable, curate the rest manually.
Either way, rows end up in your domain CSV and must pass `scripts/validate_psa_csv.py`.

## Scraping websites

Write one `fetch_<source>.py` per source and route all HTTP through
[`fetchlib.fetch_url()`](fetchlib.py) — it handles browser-like headers, robots.txt,
randomized rate-limiting, retries, and response caching (`data_cache/`, gitignored).
Parse with BeautifulSoup/lxml; extract PDFs with `pymupdf` (`fitz`).

Dependencies (all CPU-only, light): `pandas`, `requests`, `beautifulsoup4`, `lxml`,
`pymupdf`, `langdetect` (optional, enables the validator's language check).

## Collecting from X (Twitter)

Official gov/NGO X accounts are a rich PSA source and often post both English and
Kiswahili. The official API is paid, so options in order of preference:

1. **Manual copy** — posts are short; paste text + post URL into the CSV. Fastest for
   tens of PSAs per account.
2. **[twscrape](https://github.com/vladkens/twscrape)** — async scraper that works
   through real X accounts:
   - `pip install twscrape` (pure Python, httpx-based)
   - You must add one or more X accounts: `twscrape add_accounts` then `twscrape login_accounts`
     (username, password, and the login email — accounts need an email that can receive
     verification codes).
   - **Use dedicated throwaway accounts only** — scraping accounts get rate-limited and
     sometimes suspended. Never attach a personal account.
   - Store account credentials in a local `.env`/accounts db — never commit them.
   - X login flows change often; expect breakage and pin a recent twscrape version.
3. **Wayback Machine** snapshots of account pages (no auth; patchy coverage):
   `http://web.archive.org/cdx/search/cdx?url=twitter.com/kilimoKE/status/*&output=json`

## KE-only sources

Some gov sites (e.g. `kamis.kilimo.go.ke`) accept Kenyan residential connections but not
datacenter/foreign IPs. If you're scraping from a server abroad, either collect those
sources manually from a local browser, or route requests through a machine on a Kenyan
connection and point fetchlib at it with `export FETCH_PROXY=socks5h://host:port`
(SOCKS URLs need `pip install "requests[socks]"`; unset = direct connection).

## Ground rules

- Respect robots.txt and rate limits (fetchlib enforces both).
- Record the exact URL in `Source` for every row — mandatory.
- Never invent or paraphrase a translation: if a PSA has no published Kiswahili (or
  English) counterpart, it does not go in the dataset.
- Cache raw fetches; iterate on parsers offline.
