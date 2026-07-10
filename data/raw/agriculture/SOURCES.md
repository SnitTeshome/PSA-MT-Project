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
| 2b | KAOP — Kenya Agricultural Observatory Platform (KALRO) | kaop.co.ke | Crop Production, Sustainable Farming | homepage En-only (checked 2026-07-10) | 200 OK from EU server | Ward-level advisories likely behind app/registration — needs a browser look |
| 3 | KEPHIS (plant health) | kephis.go.ke | Crop Production (pest/disease alerts) | En | robots.txt 200 | Pest alerts are classic PSAs (short, directive) |
| 4 | AFA (Agriculture & Food Authority) | agricultureauthority.go.ke | Agribusiness & Market Access | En | 200 OK | Directorates (tea, coffee, horticulture) issue notices |
| 5 | NDMA (National Drought Management Authority) | ndma.go.ke → knowledgeweb.ndma.go.ke | Livestock, Sustainable Farming | **County Early Warning bulletins are English-only** (checked 23 May-2026 county PDFs: multi-page technical reports, not short PSAs). Only NDMA's Service Charter exists as a true En+Kiswahili pair | portal reachable via KE exit but slow; download = DevExpress server-side zip (see note below) | **Downgraded**: good agri context, but not bilingual PSA-shaped text. Mine the Service Charter for directive bilingual sentences; otherwise deprioritise |
| 6 | Kenya Meteorological Dept — agromet advisories | meteo.go.ke | Crop Production, Sustainable Farming | dekadal bulletin PDF is **En-only** (checked Dekad 18/2026); site "Swahili" toggle is JS-based (`/sw/` 404s) — likely a translation widget, which would NOT count as source-published parallel text | reachable from EU; robots 404 | Advisory sections are good PSA raw material *if* an official Sw counterpart exists — check KMD's Kiswahili forecast products (Taarifa) from a browser |
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

## SMS advisory services & bilingual government docs (high-potential lead)

Agencies push short, directive, farmer-facing advisories over **SMS** — these are the most
PSA-shaped agricultural text in Kenya, and several channels operate in both English and
Kiswahili. Delivery is SMS, so the text must be captured where it's **published/archived**,
not scraped off the wire (subscribing needs a phone number and only yields your own region).

| Channel | What | Bilingual? | How to get the text |
|---|---|---|---|
| **iShamba** (ishamba.com; JOIN to 21606) | Weekly weather, market prices, 2 agronomy tips to 500k+ farmers | broadcasts in En + Sw | Ask iShamba/Mediae for sample advisory archives; some appear in their blog/case studies |
| **KAOP SMS** (kaop.co.ke, KALRO) | Ward-level agro-advisories for all 47 counties, portal + SMS | advisories issued in local languages incl. Sw | Portal likely needs login; request advisory archive from KALRO |
| **KALRO/KMD/AICCRA agro-weather advisories** | Seasonal/dekadal advisories to ~471k farmers via SMS + radio | En + Sw + local | AICCRA & Alliance-Bioversity-CIAT **publish advisory examples in reports** (PDFs) — often show the En and Sw text side by side |
| **Shamba Shape Up / iShamba factsheets** (mediae.org) | TV show + downloadable factsheets | show is En + Sw; factsheets in both | Download factsheets from the Mediae/SSU site |

Action: email KALRO (KAOP) and Mediae (iShamba/SSU) requesting sample bilingual advisory
archives for a university NLP project — this is the fastest route to clean, PSA-shaped En+Sw
agricultural pairs. AICCRA/CIAT PDF reports are scrapeable now with `pymupdf`.

**Bilingual government documents** (Bradley's observation, confirmed): agencies publish
Kiswahili editions of official docs. Verified example: NDMA Service Charter exists as a true
En+Kiswahili pair (`NLP/NDMA/NDMA_Service_Charter_2024-_{English,Kiswahili}*.pdf`) — parallel
service-commitment statements. These are directive but are service-standard commitments, so
they fit **Governance / Public Service Delivery** better than Agriculture. Worth harvesting for
that domain. Look for the same En/Sw pairing on other agencies' charters, gazette notices, and
public-education booklets.

## Tanzania sources — high En+Sw volume (CHECK ACCEPTABILITY FIRST)

Tanzania runs government in Kiswahili and mirrors official content in English, so En+Sw
parallel material is far more abundant and cleaner than in Kenya. And these sites do **not**
IP-block foreign connections (no tunnel needed).

**⚠️ Decision needed before collecting:** the project is framed around **Kenyan** PSAs
("making government information more accessible" in Kenya). Using Tanzanian sources for the
En↔Sw pairs is linguistically valid (the schema has no country field; Week-1 is only En+Sw),
but must be cleared with the team / Dr. Ombui. Two caveats to raise:
1. **Dialect:** Tanzanian Kiswahili is more standard/formal (Kiswahili sanifu); Kenyan is more
   code-switched. Could be a benefit (cleaner) or a mismatch (less representative of Kenyan
   register). A mix of both may be ideal.
2. **Target languages stay Kenyan:** Somali/Dholuo/Ekegusii translations come later and are
   Kenya-specific; Tanzania only helps the En+Sw base.

| Source | URL | Bilingual mechanism | Recon 2026-07-10 |
|---|---|---|---|
| **TZ Ministry of Agriculture (Wizara ya Kilimo)** | www.kilimo.go.tz | `/language/sw` ↔ `/language/en` toggle | **200 OK from EU, no block — BUT toggle is UI-only** (verified 2026-07-10): menus translate, **news/press-release bodies stay in the original Swahili** in both states. NOT an article-level parallel source. Still useful as clean **monolingual Swahili**; English press releases may exist as separate (unpaired) items |
| FAO Tanzania | fao.org/tanzania (en + sw) | parallel language sites | robots.txt disallows scraping → manual collection only |
| TARI (Taasisi ya Utafiti wa Kilimo) | tari.go.tz | bilingual site | unreachable from EU 2026-07-10; retry later |
| Tanzania Meteorological Authority (agromet, Kiswahili) | tma.go.tz / meteo.go.tz | Sw advisories | unreachable from EU 2026-07-10 |
| FAOLEX policy PDFs (TZ) | faolex.fao.org | some En + Sw policy docs | long-form policy, not PSAs — low priority |

Also consider regional bilingual bodies: **EAC** (East African Community) and cross-border NGO
campaigns publish En+Sw. Tanzanian media (TBC, Mwananchi/The Citizen sister papers) run
parallel En/Sw agriculture content.

**TSN state papers — strongest TZ parallel lead (recon 2026-07-10).** Tanzania Standard
Newspapers (99% government-owned) publishes **Daily News (English)** and **HabariLEO
(Kiswahili)** — the mandatory-read papers in every ministry, both carrying official ministry
press releases. Same state publisher in both languages ⇒ the same agriculture announcement
often appears in each. Upstream source is **MAELEZO** (Tanzania Information Services Dept, the
govt PR arm both papers draw from). Reachable from EU, no block:
- dailynews.co.tz → 200 · habarileo.co.tz → 200 · epaper.tsn.go.tz → 200 · maelezo.go.tz → 000
Approach: match a Daily News agriculture press-release article to its HabariLEO counterpart by
date/topic (they won't share a URL scheme; align by publication date + subject). Same-publisher
govt releases are often near-verbatim across the two, unlike independent papers. Caveat still:
these are news-desk rewrites, so treat as PSA source **only where an official advisory is
carried verbatim**; otherwise it's parallel-news augmentation (team scope decision). ePaper is
image-PDF (OCR needed) — prefer the HTML article pages.

## Findings log (fetch attempts, 2026-07-10)

**AICCRA / CGIAR CGSpace — bilingual advisory PDFs (partial success).**
CGSpace (cgspace.cgiar.org) hosts real farmer-advisory posters/factsheets in both English
and Kiswahili. Confirmed a **true parallel pair**:
- SW: "Kilimo kinachohimili mabadiliko ya tabianchi: maamuzi kumi muhimu…" — item
  `c4d42102-…`, PDF bitstream `94c0db78-3fb6-4c8a-90d6-7dc22387e201` (4 pp; extracted OK,
  11,416 chars: *"Mabadiliko ya tabianchi na hali ya hewa yanayosababisha mabadiliko ya
  misimu ya kilimo huathiri uzalishaji…"*)
- EN twin: "Climate smart agriculture: top ten decisions to make with weather info" (IITA)
  — item `62fd7239-…`, PDF bitstream `287a1fb1-170c-4359-9bfc-41b7954ac505`
- pymupdf extraction **works**. Tool: `scripts/collect/fetch_cgspace.py`.

Failures / constraints hit (recorded per instruction):
- CGSpace **blocks datacenter IPs** (connection refused) — must use the KE residential exit.
- Even via the exit it **rate-limits hard (HTTP 429)** — the SW poster fetched fine (cached),
  but the EN poster 429'd repeatedly even after a 30 s cooldown. Bulk auto-download is
  throttled; use long delays (30–60 s/file) or **download manually from a browser**.
- `hdl.handle.net/…/bitstreams/…/download` → 404; `/bitstreams/<uuid>/download` → refused.
  Only the API form `…/server/api/core/bitstreams/<uuid>/content` works.
- **Content is Tanzania-focused**: the Kiswahili agricultural material on CGSpace is mostly
  CCAFS/IITA East-Africa work centred on Babati, Tanzania — ties into the Tanzania lead below.

**Mediae / iShamba (recorded).** Landing pages expose no direct factsheet/PDF downloads
(content sits behind the SMS service / deeper nav). Email request is the realistic route —
draft kept by Bradley.

**Parallel press / translated news & e-papers (analysed 2026-07-10).** Yes, some outlets
publish the same story in En and Sw — chiefly broadcaster Swahili services (**BBC Swahili,
DW Swahili, VOA Swahili, Xinhua Swahili**), and paired titles (Taifa Leo/Daily Nation KE;
Mwananchi/The Citizen TZ). Verdict for this project:
- **News ≠ PSA.** The brief explicitly excludes "news story or opinion piece." So parallel
  articles can't enter the PSA dataset *except* where an official advisory/PSA is **quoted
  verbatim** in both a Sw and En article (extract the quoted directive, cite both URLs).
- **Alignment is loose.** These are adaptations, not sentence-aligned translations → would
  need a sentence aligner (LASER/vecalign) to pair, adding noise.
- **E-papers** (Nation/Standard ePaper): paywalled, image-based PDF scans → OCR + licensing
  problems. Poor for automated parallel extraction. Skip.
- **Better path if the team wants news-derived parallel data for the *modeling* stage:** use
  existing public En–Sw parallel corpora that already mined these sources —
  **MAFAND-MT, GlobalVoices, CCAligned, OPUS (incl. Tanzil, JW300 successors)** — rather than
  re-scraping. Keep the hand-collected set strictly PSAs; augment with these at training time
  if scope allows (a team decision).

**Kenya state-media equivalents (recon 2026-07-10).** Ran the same playbook as Tanzania:
- **Kenya News Agency (kenyanews.go.ke)** — the state news agency (closest KE analogue to
  TSN+MAELEZO). Reachable (broken cert → verify_tls=False). **English-only**: sections are
  News/Features/Technology/International, no Swahili desk. So unlike TSN/HabariLEO, Kenya's
  *state* news output has no institutional Swahili twin. Structural gap, not a fetch failure.
- **MyGov (mygov.go.ke)** — govt weekly pullout; reachable, English-led, no Swahili section on
  landing. **KBC (kbc.co.ke)** — reachable; broadcaster runs Sw + En but as separate bulletins,
  not paired text.
- **Daily Nation ePaper** (epaper.nation.africa): **robots.txt disallows** automated access;
  content is paywalled + copyrighted (Nation Media Group). NOT scraped — see note below. Also
  low-value: English-only (Taifa Leo is the Sw sister but independently written, not a
  translation), and it's news, which the brief excludes as PSA material.

- **People Daily ePaper** (epaper.peopledaily.digital): People Daily is a *free* paper, and its
  robots.txt only blocks Googlebot from `/stage/` paths (production reader not disallowed). So
  the robots/paywall objection is milder than Nation's. But it's still: a PageSuite HTML5 reader
  serving **page images** (→ OCR needed), **English-only**, **news** (excluded as PSA), and
  copyrighted (Mediamax). Same verdict: not a fit for the parallel PSA set.

> **Copyright/ToS boundary (applies to all newspaper e-editions):** don't auto-scrape newspaper
> e-editions for this dataset. Nation is paywalled + robots-disallowed; even a free one (People
> Daily) is copyrighted and image-based. The project's final dataset may be released CC-BY, and
> republishing a newspaper's articles under CC-BY would infringe. Legitimate use: a human reading
> an edition may manually transcribe an **official government notice/advisory printed verbatim**
> (public, PSA-shaped) and cite it; bulk article scraping is out of scope. Do not script logins
> to paywalled subscriber editions.

**Absence of a Kenyan equivalent (recorded).** A CGSpace search for Kenyan bilingual advisories
returned mostly **English research papers *about* advisory services** (iShamba bias studies,
GPT advisory evaluations) — not bilingual bulletins. Kenya's actual bilingual advisories go out
by **SMS/KAOP** and are not archived as parallel PDFs. So for clean En+Sw *agricultural* pairs,
the realistic sources are (a) Tanzania gov/CGIAR material, (b) direct requests to KALRO/Mediae
for advisory archives (draft email kept by Bradley). Pure-Kenyan bilingual agri PSAs will lean
on social-media posts (X/Facebook) where agencies post both languages.

**Digitized bilingual archives (recon 2026-07-10).**
- **UCLA Digital Library** (digital.library.ucla.edu, ark:/21198/z1hf19gd): bilingual En+Sw but
  **image-only, pre-2005, individual-image download**, and the site is behind a **bot-wall**
  (blocked our fetcher and WebFetch). Automated use needs a real browser (Selenium/Playwright)
  + OCR (tesseract `eng`+`swa`, not installed here). High effort; historical, not PSAs.
- **IFRA Nairobi Press Archive** (ifrapressarch.nakalona.fr, Omeka on Huma-Num/Nakala):
  reachable, has **PDF downloads + a Nakala API** (nakala.fr/data/…). But it's digitized
  **newspaper clippings** (e.g. "Two years of pain and rejection") — news, mostly English,
  third-party press copyright. Better licensing/access than commercial e-papers, same
  news≠PSA limitation.

## Broadcast (radio/TV) transcription (recon 2026-07-10)

Is there transcribed Kenyan broadcast news? Findings:
- **Kenyan TV/radio news is not published as open text transcripts.** KBC broadcasts En + Sw
  but as audio bulletins, not transcribed corpora. Vernacular stations run ag programmes
  (untranscribed). So there's no ready "transcribed news announcements" text dump to scrape.
- **BUT Farm Radio International (scripts.farmradio.fm)** is the strong lead here: a library of
  farmer **radio scripts and radio *spots*** (spots = short PSA-style announcements) in Swahili
  and English, on agriculture/health/environment. Selective (not full) parallel coverage;
  robots.txt disallows scripted access; licensing not stated on-page (FRI scripts are
  historically Creative Commons — **confirm CC-BY before use**). Route: manual download / email
  FRI for the resource pack. **This is arguably the best PSA-shaped bilingual agri text found.**
- CGIAR + IFPRI + FRI have used **ASR to transcribe Swahili/Hausa farmer voice messages** — a
  possible research dataset; ask FRI/IFPRI if the transcripts are shareable.

## Agricultural NGOs — bilingual announcements/sensitizations (recon 2026-07-10, Kenya priority)

| Org | URL | Why | Bilingual? | Status |
|---|---|---|---|---|
| **Biovision Africa Trust — The Organic Farmer / Mkulima Mbunifu** | biovisionafricatrust.org, infonet-biovision.org | TOF (English) has a Swahili sister magazine **Mkulima Mbunifu**; Infonet-Biovision is a big farmer knowledge base | **Yes — En + Sw parallel magazines** | **Top NGO lead**; back-issues often PDF/CC. Verify parallelism per issue |
| **Access Agriculture** | accessagriculture.org | Farmer training videos + factsheets in many languages | En + Sw factsheets, often CC | Strong; check factsheet licensing/download |
| **KENAFF (Kenya National Farmers' Federation)** | kenaff.org | Umbrella farmer org; member advisories, "The Kenya Farmer" | En, some Sw | Probe site + socials |
| **Ukulima True campaign** (CABI/AgroChem) | — | Pesticide-safety **sensitization** campaign, farmer-facing | En + Sw messaging | Behaviour-change PSAs; find campaign assets |
| **PlantVillage / potato WhatsApp advisory bot** | plantvillage.psu.edu | Advisory bot answers in **En and Sw** | Yes | Bot output, not a public archive — ask for logs |
| Farming Systems Kenya; Uhai Kenya; Biovision GIZ Western Kenya | farmingsystemskenya.org; uhaikenya.org | smallholder extension | mixed | Lower priority; check for Sw material |

**Tanzania NGOs (secondary):** Mkulima Mbunifu is actually Tanzania-based (En/Sw); **SAGCOT**,
**ESAFF Tanzania**, **Farm Africa TZ**, **AGRA** publish farmer material, some bilingual.
Same acceptability caveat as other TZ sources.

## Recommended collection strategy (ranked, after 2026-07-10 recon)

The recon shows clean, **redistributable, bilingual En↔Sw *PSA* pairs are scarce** — most
bilingual material is either news (excluded), image-only (OCR), copyrighted, or IP/bot-walled.
Spend effort here, in order:

1. **Farm Radio International scripts/spots + Biovision (TOF / Mkulima Mbunifu)** — the best
   PSA-shaped bilingual *agricultural* text found; likely CC-licensed. Manual download / email;
   confirm licensing. `radio spots` and magazine tips are short and directive = ideal PSAs.
2. **Official gov/NGO social posts (X, Facebook)** — the main place agencies post the *same*
   PSA in En + Sw. Fits the brief, public, citable. Use warmed-up accounts + `x_collect.py`.
3. **Direct requests to KALRO (KAOP), Mediae (iShamba/SSU), Farm Radio, Biovision** — email
   drafts; fastest route to clean bilingual advisories.
4. **CGIAR CGSpace bilingual advisory PDFs** — CC-licensed, extraction proven; download
   manually (429-throttled). Mostly Tanzania-focused. Fetch list: `CGSPACE_FETCH_LIST.md`.
5. **Tanzania TSN state papers (Daily News + HabariLEO) / MAELEZO** — strongest parallel-*news*
   lead; use only where an official advisory appears verbatim in both. Needs team OK on
   Tanzania sources.
6. **Everything else (e-papers, press archives, UCLA/IFRA)** — do NOT bulk-scrape: copyright /
   OCR / bot-walls / news-not-PSA. Only hand-transcribe official notices printed verbatim.

For the **modeling** stage (not the hand-built PSA set), if the team wants extra En–Sw parallel
volume, use existing public corpora (MAFAND-MT, GlobalVoices, CCAligned, OPUS) rather than
re-scraping news.

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

## NDMA knowledgeweb download mechanism (for anyone trying to automate it)

The bulletin grid (`CountyBulletins.aspx`) has no direct file links. "Download Selected" is a
DevExpress `ASPxGridView` toolbar button whose click sets `e.processOnServer = true` and runs
server-side `docGrid_ToolbarItemClick`, which **zips the selected PDFs from disk**
(`D:\KMSApp\Content\LibraryDocuments\<name>.pdf`) via Telerik `ZipFile.CreateEntryFromFile`
and streams the zip back. Implications:
- There is no stable per-file GET URL to scrape; you must reproduce the ASP.NET postback
  (`__VIEWSTATE` + `__EVENTVALIDATION` + the grid callback for `btnDownload`) — brittle.
- The `Content/LibraryDocuments/` path is **not** web-served directly (tested: 404), it's a
  server filesystem path used by the zip code.
- Some entries are broken on their side (a `FileNotFoundException` for a missing PDF aborts
  the whole zip). Select a small batch and avoid the broken months.
- **Verdict:** since the content is English-only anyway, automating this is low priority.
  If ever needed, Selenium/Playwright driving the grid is more robust than replaying the
  postback. A batch already lives locally at `NLP/NDMA/EW_Bulletins.zip` (23 counties, May 2026).
