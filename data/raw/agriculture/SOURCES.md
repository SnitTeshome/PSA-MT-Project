# Agriculture domain — source inventory

Week-1 milestone: ≥10 documented reliable sources. Status column reflects reachability checks
run 2026-07-10 from a Hetzner (EU) server — `unreachable (EU)` may still work from a Kenyan
connection/mobile; retest locally before ruling a source out.

Hard constraint: entries must be **true En+Sw parallel pairs from the source itself** — no
self-translated text. Sources that publish in only one language are still useful when the same
agency posts the paired translation on another channel (e.g. website in English, X/Facebook in
Kiswahili) — record both URLs in `Source`.

## Government (primary)

| # | Source | URL | Sub-categories | Languages | Recon 2026-07-10 | Notes |
|---|--------|-----|----------------|-----------|------------------|-------|
| 1 | Ministry of Agriculture & Livestock Development | kilimo.go.ke | all five | En, some Sw | **main site DOWN 2026-07-10 — confirmed unreachable from both EU server and KE connection** | Use Wayback CDX for its press-release history; watch for the site coming back |
| 1b | KAMIS — Kenya Agricultural Market Information System | kamis.kilimo.go.ke | Agribusiness & Market Access | En | **fetch confirmed 2026-07-10 via KE exit** — blocks non-KE IPs; also serves a self-signed cert chain → needs `fetch_url(..., verify_tls=False)` | Market prices/advisories; pair with Sw social posts |
| 2 | KALRO (Kenya Agricultural & Livestock Research Org.) | kalro.org | Crop Production, Livestock, Training | mostly En | robots.txt 200 — check allow rules before scraping | Extension advisories, e-extension app content often bilingual |
| 2b | KAOP — Kenya Agricultural Observatory Platform (KALRO) | kaop.co.ke | Crop Production, Sustainable Farming | En, advisories sometimes Sw | 200 OK from EU server | Ward-level agro-weather advisories for farmers — very PSA-shaped |
| 3 | KEPHIS (plant health) | kephis.go.ke | Crop Production (pest/disease alerts) | En | robots.txt 200 | Pest alerts are classic PSAs (short, directive) |
| 4 | AFA (Agriculture & Food Authority) | agricultureauthority.go.ke | Agribusiness & Market Access | En | 200 OK | Directorates (tea, coffee, horticulture) issue notices |
| 5 | NDMA (National Drought Management Authority) | ndma.go.ke | Sustainable Farming, Livestock | En + county-level Sw versions | robots.txt 200 | Monthly early-warning bulletins per county (PDFs) — livestock/pasture advisories |
| 6 | Kenya Meteorological Dept — agromet advisories | meteo.go.ke | Crop Production, Sustainable Farming | En + Sw (dekadal agromet bulletins) | site up, robots 404 (= no restrictions declared) | Dekadal agro-met bulletins are farmer-directed advisories |
| 7 | County govt agriculture depts (e.g. Kisii, Kakamega, Meru) | *.go.ke county sites | all five | En/Sw mixed | not yet probed | County press offices often post Sw versions on Facebook |
| 7b | KCSAP — Kenya Climate Smart Agriculture Project | kcsap.go.ke | Sustainable Farming, Training | En | 200 OK from EU server | Project bulletins/success stories; check for farmer-facing advisories |

## NGO / verified media

| # | Source | URL | Sub-categories | Languages | Notes |
|---|--------|-----|----------------|-----------|-------|
| 8 | FAO Kenya | fao.org/kenya | Sustainable Farming, Training | En, some Sw materials | Fall armyworm / desert locust campaign material was bilingual |
| 9 | Kenya Red Cross | redcross.or.ke + X | food security, drought alerts | En + Sw social posts | X account frequently posts both languages |
| 10 | Shamba Shape Up / Mediae | shambashapeup.com | Training, Crop, Livestock | En + Sw (show is bilingual) | Leaflets/factsheets exist in both languages |
| 11 | Mkulima Young | mkulimayoung.com + socials | Agribusiness | En/Sw mixed | Verify "official source" bar with team |
| 12 | KBC / Ukulima segments | kbc.co.ke | all five | En + Sw | State broadcaster = credible; short news-style PSAs |

## Official X (Twitter) accounts

@kilimoKE (Ministry), @KALROKenya, @Kephiske, @NDMA_Kenya, @MeteoKenya, @KenyaRedCross —
short bilingual posts are exactly PSA-shaped. Collection options, in order of preference:

1. **Manual copy** (viable: posts are short; log the post URL in `Source`).
2. **twscrape** (github.com/vladkens/twscrape) — async X scraper. Requires real X *accounts*
   (username + password + login email); emails available if needed (iCloud private relay).
   Accounts get rate-limited/banned — use throwaways, never a personal account. See
   `scripts/collect/README.md` for setup/limitations.
3. Wayback Machine snapshots of the account pages (no auth, patchy coverage).

## Known limitations & workarounds

- **kilimo.go.ke main site is down (2026-07-10, from both EU and KE)**; some subdomains
  (KAMIS) work from Kenyan connections only, not from datacenter IPs. Workarounds: collect
  KE-only sources from a local browser, and mine the ministry's history via Wayback CDX:
  `http://web.archive.org/cdx/search/cdx?url=kilimo.go.ke/*&output=json&filter=statuscode:200&collapse=urlkey`
- **Bilingual pairing is the bottleneck**, not volume: prioritise NDMA bulletins, KMD agromet
  bulletins, and X accounts that post both languages; pair website-En with social-Sw where the
  agency published both.
- **PDFs**: extract text with `pymupdf` (already installed). **Image posters**: OCR is
  unreliable on stylized layouts — transcribe manually, note `platform=poster` in Metadata.
- Respect robots.txt (checked per domain in fetchers), rate-limit with randomized sleeps.
- Week-2 note: if the merged dataset grows large, the brief suggests DVC or Git LFS.
