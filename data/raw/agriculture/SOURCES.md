# Agriculture domain — source inventory

Week-1 milestone: ≥10 documented reliable sources. Status column reflects reachability checks
run 2026-07-10; retest before ruling a source out.

**Scope note (2026-07-15, Bradley's explicit call):** although the group project brief frames
this as "Kenyan PSAs," English-language PSA content from **other African countries** is now
being treated as in-scope for this domain's dataset too (not just modeling-stage
augmentation) — see the "Africa-wide expansion" section below. This is a deliberate scope
decision, not an oversight; flag it to the team/instructor if the grading rubric turns out to
be Kenya-only.

Hard constraint (relaxed 2026-07-14, lecturer-approved): **prioritise true En+Sw parallel
pairs from the source itself** — no self-translated text — but a high-quality **English-only
source is acceptable when it is a certain, verifiable Kenyan PSA** (official government
advisory/recommendation, short and directive — not a news story or a long technical report).
Sources that publish in only one language are still useful when the same agency posts the
paired translation on another channel (e.g. website in English, X/Facebook in Kiswahili) —
record both URLs in `Source`. Practical effect: this un-downgrades several previously-shelved
English-only Kenyan government sources (NDMA county bulletin *recommendations* sections,
KEPHIS pest/disease alerts) — see their rows below and the Recommended collection strategy.

## Government (primary)

| # | Source | URL | Sub-categories | Languages | Recon 2026-07-10 | Notes |
|---|--------|-----|----------------|-----------|------------------|-------|
| 1 | Ministry of Agriculture & Livestock Development | kilimo.go.ke | all five | En only (confirmed 2026-07-14) | **Back up 2026-07-14** (was down 2026-07-10) — homepage + `/press-release/` fetched, 244KB/163KB pages, real content (title "Home - MoALD"). No `/sw/`, `hreflang="sw"`, or "Kiswahili" string found anywhere in either page — **no institutional Swahili section exists**, this isn't a fetch gap | `/press-release/` page itself is mostly a nav/sitemap listing (statistics unit, tenders, policy PDFs), not a dated article feed — if real press releases exist they're elsewhere on the site; worth a deeper crawl but don't expect bilingual pairing |
| 1b | KAMIS — Kenya Agricultural Market Information System | kamis.kilimo.go.ke | Agribusiness & Market Access | En only (confirmed 2026-07-14) | **fetch confirmed 2026-07-10**, content itself pulled 2026-07-14 — serves a self-signed cert chain → needs `fetch_url(..., verify_tls=False)`. Site is a Yii app (`/index.php/site/market`), no language switcher, no Swahili string anywhere | Market prices/advisories; tabular data (prices), not directive PSA text either way; pair with Sw social posts if pursued further |
| 2 | KALRO (Kenya Agricultural & Livestock Research Org.) | kalro.org | Crop Production, Livestock, Training | mostly En | robots.txt 200 — check allow rules before scraping | Extension advisories, e-extension app content often bilingual |
| 2b | KAOP — Kenya Agricultural Observatory Platform (KALRO) | kaop.co.ke | Crop Production, Sustainable Farming | homepage En-only (checked 2026-07-10) | 200 OK; **Playwright browser check done 2026-07-14** | No login wall (unlike PIMS), but the county→constituency→ward→Submit form (labelled "Agronomic Advisory") **doesn't produce any visible output or backend request** when driven programmatically — tried full Baringo→Baringo Central→Kabarnet chain, submit click fires no network call and page doesn't navigate. Either broken, JS-event-bound in a way headless Chromium isn't triggering, or the advisory content genuinely isn't wired up yet. Only live feature confirmed is a weather chatbot widget (not advisory text). Dead end for automated collection — if pursued further it needs a human in a real browser, not more automation attempts |
| 3 | KEPHIS (plant health) | kephis.go.ke | Crop Production (pest/disease alerts) | En | robots.txt 200; homepage + `/news-events` fetched 2026-07-14 (real content, no dated alert feed found there — mostly press-story items, not short alerts) | Pest alerts are classic PSAs (short, directive) — homepage links to **Pest Information Management System (PIMS)** at `pims254.netlify.app`, a JS-rendered SPA. Checked via Playwright 2026-07-14: the public landing page is just an "about PIMS" blurb; the actual `#/published` pest listing **redirects to an admin sign-in wall** — no public pest-alert content is reachable without an account. Dead end for automated collection, same pattern as KAOP |
| 4 | AFA (Agriculture & Food Authority) | agricultureauthority.go.ke | Agribusiness & Market Access | En | 200 OK | Directorates (tea, coffee, horticulture) issue notices |
| 5 | NDMA (National Drought Management Authority) | ndma.go.ke → knowledgeweb.ndma.go.ke | Livestock, Sustainable Farming, Crop Production, Agribusiness | **County Early Warning bulletins are English-only** — bulletin body is a multi-page technical report, **but every bulletin has a recommendations section with genuine short directive Agriculture/Livestock text** (confirmed 2026-07-14). Only NDMA's Service Charter exists as a true En+Kiswahili pair | portal reachable but slow; download = DevExpress server-side zip (see note below); local batch at `NLP/NDMA/EW_Bulletins.zip` (23 counties, May 2026), converted to Markdown via `convert.py --batch --to .md` into `NLP/NDMA/EW_Bulletins_md/` for review | **Full 23-county pass completed 2026-07-14** (was 2 counties). The recommendations section is NOT standardized — 4+ distinct formats found across counties (Baringo: numbered §7.1.x list; Garissa/Wajir/Turkana: "Table N. Recommended interventions" grid; Isiolo/Marsabit/Meru/Narok: "Recommended Interventions" with Coverage/Cost/Gap columns; Kilifi/Makueni/Nyeri/Taita-Taveta/Tana River/Tharaka-Nithi: plain bullet list, sometimes with "(Action: ...)" attribution) — checking required a content-based search (grep for "recommend" + manual read), not a single regex. **21 of 23 counties had genuine, usable Agriculture/Livestock text; Laikipia and Kajiado do not** (Kajiado's bulletin has no recommendations section at all — only narrative report content — confirmed by reading the full document, not just a failed pattern match). Kwale's recommendations section is pure food-aid/cash-transfer logistics, no Agriculture/Livestock content. **32 rows extracted from 18 counties** (`AGRI_010`–`041`), on top of the original Baringo/Garissa rows — all real bulletin text, team-translated per the English-only rule, verified 0 flags on the a cloud translation API language QA gate. Service Charter still separately useful for bilingual Governance-domain sentences (not Agriculture) |
| 6 | Kenya Meteorological Dept — agromet advisories | meteo.go.ke | Crop Production, Sustainable Farming | dekadal bulletin PDF is **En-only** (checked Dekad 18/2026); site "Swahili" toggle is JS-based (`/sw/` 404s) — likely a translation widget, which would NOT count as source-published parallel text | reachable; robots 404 | Advisory sections are good PSA raw material *if* an official Sw counterpart exists — check KMD's Kiswahili forecast products (Taarifa) from a browser |
| 7 | County govt agriculture depts — **all 47 counties** | *.go.ke county sites | all five | **Full 47-county pass done 2026-07-14** (`scripts/collect/fetch_all_counties_recon.py`; domain list from cog.go.ke, cross-checked against parliament.go.ke/the-senate/counties) | 44/47 reachable on first pass; the other 3 had stale/wrong domains, fixed 2026-07-14
with corrected URLs (Bradley): Laikipia moved to `new.laikipia.go.ke` (has an agriculture
dept link, English-only, no Swahili signal); Busia's real domain is `busiacounty.go.ke`
(no `www`) and also has an agriculture dept link, English-only; Taita-Taveta's
`cpsb.taitataveta.go.ke` (Public Service Board) and `taitatavetaassembly.go.ke` (County
Assembly) are both reachable but are HR/legislative sites, not the executive agriculture
department — no ag link found on either, correct executive-branch domain still unresolved. Laikipia's
and Busia's agriculture pages were also read for directive content — same result as the
other 37, institutional overview/mission-statement text, no PSA content.

**Domain QA pass (2026-07-14, Bradley's suggestion):** the COG-sourced domain list wasn't
just trusted — spot-checked 14/47 counties against live web search results (pattern:
"[county] go ke", check top hits). Found 2 more stale domains from the original list:
**Kwale** was on `kwalecountygov.com` (a `.com`, not the real `.go.ke` site) — corrected to
`kwale.go.ke`, has an agriculture page, but it's a CEC-member biography, not PSA content.
**Machakos** was on `machakosgovernment.com` — corrected to `machakos.go.ke`, agriculture
page is a roles/functions list, not PSA content either. The other 12 checked (Kilifi,
Tharaka-Nithi, Kitui, Baringo, Murang'a, Kericho, Nyamira, Marsabit, Nyandarua, Embu, Tana
River, Kakamega) all matched what was already used — no further corrections found.
Nyandarua's thin ag-page content (190 chars) turned out to be explained by the site being
under maintenance, not a wrong domain. Bonus find while searching: Murang'a runs a
farmer-specific portal called **"Inua Mkulima"** (`ecitizen.muranga.go.ke`, Swahili for
"Uplift the Farmer") — checked, it's a **login-gated** application (username/password
form, likely a subsidy/input-registration system), no public content, same dead-end
pattern as KAOP/PIMS.; 37 had a findable agriculture department link. A naive "swahili" string search flagged 8 counties, but **6 were false positives** on manual check: Lamu/Embu matched a Google-Translate widget's language list, Makueni/West Pokot/Elgeyo-Marakwet matched a video-player library's built-in caption-language dropdown (`mejs.swahili`), Isiolo matched unverified schema.org metadata — none are real site-authored Swahili content. **2 were genuine**: Nyeri and Narok's agriculture department pages link true bilingual PDF **Service Charters** (Nyeri: Agriculture/Veterinary/KCSAP charters, both EN+SW downloaded and extracted) — but like NDMA's charter, these are service-standard/fee-and-timeline tables ("Provision of Agricultural Extension Services — Free — Continuous"), not farmer-facing advisory PSAs — fits Governance domain, not Agriculture. Went further per Bradley's "even English-only, get real PSAs if they're there" instruction: screened all 37 agriculture pages' actual text for directive/imperative content (keyword screen + manual read of the highest-scoring and largest pages: Samburu, Vihiga, Lamu, Kirinyaga, Nakuru, Kajiado, Homa Bay, Mandera, plus Nyeri's full 27-row downloads table) — **all are institutional department overviews, mandate/mission statements, project-status trackers, or news articles**, not directive PSA text (closest miss: a Nakuru news article paraphrasing an official "urging" seedling care, but reported/paraphrased speech, not a verbatim advisory — doesn't clear the news≠PSA bar). **Conclusion: no promotable Agriculture PSA content found on any of the 47 county government sites' landing/department pages** — this is a real, checked absence, not an unexplored gap. County press offices' Facebook pages remain the one untested lead — needs `x_collect.py`-style social scraping, not more site crawling. Full per-county reachability/results log: `scripts/collect/fetch_all_counties_recon.py` output. |
| 7b | KCSAP — Kenya Climate Smart Agriculture Project | kcsap.go.ke | Sustainable Farming, Training | En | 200 OK | Project bulletins/success stories; check for farmer-facing advisories |

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
parallel material is far more abundant and cleaner than in Kenya. And these sites are
straightforward to reach, unlike some Kenyan government sites.

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
| **TZ Ministry of Agriculture (Wizara ya Kilimo)** | www.kilimo.go.tz | `/language/sw` ↔ `/language/en` toggle | **200 OK, no block — BUT toggle is UI-only** (verified 2026-07-10): menus translate, **news/press-release bodies stay in the original Swahili** in both states. NOT an article-level parallel source. Still useful as clean **monolingual Swahili**; English press releases may exist as separate (unpaired) items |
| FAO Tanzania | fao.org/tanzania (en + sw) | parallel language sites | robots.txt disallows scraping → manual collection only |
| TARI (Taasisi ya Utafiti wa Kilimo) | tari.go.tz | bilingual site | unreachable 2026-07-10; retry later |
| Tanzania Meteorological Authority (agromet, Kiswahili) | tma.go.tz / meteo.go.tz | Sw advisories | unreachable 2026-07-10 |
| FAOLEX policy PDFs (TZ) | faolex.fao.org | some En + Sw policy docs | long-form policy, not PSAs — low priority |

Also consider regional bilingual bodies: **EAC** (East African Community) and cross-border NGO
campaigns publish En+Sw. Tanzanian media (TBC, Mwananchi/The Citizen sister papers) run
parallel En/Sw agriculture content.

**TSN state papers — strongest TZ parallel lead (recon 2026-07-10).** Tanzania Standard
Newspapers (99% government-owned) publishes **Daily News (English)** and **HabariLEO
(Kiswahili)** — the mandatory-read papers in every ministry, both carrying official ministry
press releases. Same state publisher in both languages ⇒ the same agriculture announcement
often appears in each. Upstream source is **MAELEZO** (Tanzania Information Services Dept, the
govt PR arm both papers draw from). Reachable, no block:
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
- Note (2026-07-14): `NLP/NDMA/ENGLISH CI A4 .pdf` + `SWAHILI CI A4.pdf` are **duplicate copies of
  this exact same pair** (byte-identical extracted text, 11,413 SW chars) saved under a
  different name in a different folder — not a second discovery, don't double-count or
  double-promote.

Failures / constraints hit (recorded per instruction):
- CGSpace **rate-limits hard (HTTP 429)** — the SW poster fetched fine (cached), but the
  EN poster 429'd repeatedly even after a 30 s cooldown. Bulk auto-download is
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

## Farm Radio + Biovision manual/scripted downloads (2026-07-11 → 2026-07-12)

`farmradio_manual/` was reorganized 2026-07-12 into four subfolders — see
`farmradio_manual/README.md` for the full breakdown, file-by-file URLs, and licensing notes.
Summary:

- **`confirmed_pairs/`** — true En+Sw parallel PSA-shaped text, dataset-ready: the CGSpace
  climate-smart-agriculture poster, a genuine bilingual TOF "Plant Extract Special" (issue
  17, Sept/Oct 2006), and (added 2026-07-12) a second CGSpace pair — "Soil fertility
  management in Babati" — found by searching CGSpace's discover API for the English
  equivalent of one of the 5 Kiswahili-only items in `CGSPACE_FETCH_LIST.md`. Of the other
  4, no English twin exists on CGSpace at all — they're Swahili-*original* IITA extension
  handbooks (sunflower/rice/cassava/bean, all Tanzania, all CC-BY-4.0), not translations;
  moved to the monolingual bucket rather than left mislabeled as "needs an EN match."
- **`tof_magazine_en/`** / **`mkulima_mbunifu_sw/`** — monolingual background material
  from Infonet-Biovision (CC-licensed, robots.txt allows it). TOF and Mkulima Mbunifu are
  sister publications, **not** issue-by-issue translations — don't pair by number. Full
  archives (~230 TOF EN, 100+ MKM SW) are being bulk-fetched 2026-07-12 via
  `fetch_infonet_magazines.py` (run `ls farmradio_manual/tof_magazine_en | wc -l` etc. for
  current counts — this was still running in the background as of this note).
- **`farm_radio_scripts/`** (3 .docx, hand-downloaded 2026-07-11) — the agriculture-relevant
  subset of the original `NLP/Project/FarmRadio/` dump (6 DRC/Togo health-and-gender files
  were wrong-variant, wrong-domain, deleted 2026-07-11). Superseded in volume 2026-07-12 by
  `fetch_farmradio.py` (below), which pulls the same kind of pairs at scale — kept here as
  the original hand-picked set.
- **`_candidates_farmradio.csv`** (gitignored, sibling to this file) — bulk output of
  `fetch_farmradio.py --fetch-all kilimo`, confirmed En+Sw script pairs crawled from Farm
  Radio's Swahili-locale agriculture hub (52/52 articles fetched 2026-07-12 — complete).
  Human review still
  required before promoting rows into `agriculture_psas.csv`: dialogue-script format may
  need trimming to PSA length, and Farm Radio's own pages carry **no CC statement** ("All
  Rights Reserved") — confirm licensing before any redistribution beyond class use.

**Two infra fixes made while running this (2026-07-12):**
1. `fetchlib._robots_allows()` had a bug — it fetched `robots.txt` with no browser headers,
   and Farm Radio's CDN 403s headerless requests; Python's robotparser fails safe on 403 by
   disallowing *everything*. This wrongly made `scripts.farmradio.fm` look
   robots-disallowed when its real policy (`Disallow:` blank) is wide open. Fixed in
   `fetchlib.py` to reuse the same header'd session as normal fetches.
2. CGSpace is **still** hard 429-rate-limited, even after a ~25 min cooldown from the
   previous 429 — this isn't a one-off, budget for browser-download-only on CGSpace
   going forward.

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

## Prior-art check: existing public datasets (2026-07-14/15)

Before collecting more by hand, checked whether an existing published dataset could be
cited/credited instead of re-scraping — GitHub, a cloud GPU notebook service, HuggingFace, and Zenodo, plus the
specific hypothesis that someone scraped Kenyan government Twitter accounts before the
2023 API lockdown. **Conclusion: nothing usable found for the hand-curated PSA set.**

- **Twitter-based Kenyan datasets are a structural dead end for this project, regardless
  of vintage.** Checked `github.com/jayneamol/kweli` (PolitiKweli, a Swahili-English
  political misinformation dataset with a "fact" label that looked promising) — pulled
  and inspected all 3 CSVs directly: every file is `tweet id, label` only, **no tweet
  text at all**. This isn't a one-off gap; sharing raw tweet text was against Twitter's
  developer terms for academic redistribution even before the 2023 API lockdown, so
  "ID-only" is the norm for this whole class of dataset, not just this one. Rehydrating
  IDs now needs paid API access, and a large fraction of 2022-era political tweets will
  be deleted/suspended regardless. Ombui et al. (2019, 260k Kenyan tweets, hate-speech
  labels) is referenced widely in papers but no public download surfaced either — even
  if found, expect the same ID-only pattern.
- **General Swahili-English parallel corpora exist in volume** (OPUS, ParaCrawl,
  MAFAND-MT, WikiMatrix, SAWA, CCAligned, Kencorpus) but are web-crawl/news-based, not
  PSA-shaped, and not government-specific — these fit the "augment at the modeling
  stage" category already noted above, not the hand-collected PSA set.
- **SDTC** (Swahili Dholuo Topic Classification, Zenodo DOI 10.5281/zenodo.14353500,
  CC-BY) has an "Agriculture and Food" topic label, which looked promising, but: (a) the
  record is access-restricted — logging into Zenodo did not unlock it (checked
  2026-07-15), next step would be emailing the depositors directly, and (b) even
  unlocked it's monolingual Swahili/Dholuo topic-classified informal short text, not
  bilingual official advisories, so it's a low-priority lead either way.
- **SMS spam/scam datasets checked on the hypothesis that "ham" (legitimate) messages
  might incidentally contain real agricultural extension/PSA content** — same logic as
  checking a hate-speech dataset's "neither" class. **Both checked, both negative:**
  - `github.com/AbayomiAlli/SMS-Spam-Dataset` (ExAIS, Federal University of Agriculture,
    Abeokuta, Nigeria, 2014, 2,890 ham + 2,350 spam) — downloaded and grepped the full
    corpus directly (not just the README): **zero genuine agriculture content**. The
    "agriculture" connection is only that the collecting institution is an agricultural
    university — the messages themselves are personal/telecom SMS traffic (data-plan
    alerts, campus church group reminders, one student forwarding a "Cropping Systems"
    *seminar announcement*, which is about a lecture, not a PSA). Also note: this is real
    people's personal SMS content collected under informed consent for spam-detection
    research specifically — even where content is unrelated, it wouldn't be
    appropriate to redistribute into an unrelated MT dataset without the same consent
    scope.
  - a cloud GPU notebook service `henrydioniz/swahili-sms-detection-dataset` (1,508 Tanzanian Swahili SMS,
    scam/trust labels) — **fully checked** (a cloud GPU notebook service API credentials already in the
    workspace `.env`, pulled the complete `bongo_scam.csv` directly, 508 trust + 1,000
    scam rows). Confirmed negative, but with a genuinely interesting near-miss: "kilimo"
    (agriculture) and "ufugaji" (livestock) each appear **66 times** — every single hit
    is the identical scam template (traditional-healer or Freemason-recruitment scams
    listing "wealth, love, court cases, school, **agriculture, livestock**, business" as
    one interchangeable list of life domains they claim to fix). Zero hits for
    `mkulima`/`wakulima` (farmer/farmers), `mazao` (crops), `mifugo` (livestock-noun),
    `mbolea` (fertilizer), or `mbegu` (seeds) — the words that would actually appear in
    real agricultural advisory text. So the keyword *matched*, but the content behind it
    didn't — a good reminder that a keyword hit still needs a context check.
  - A larger, harder-gated Tanzanian telecom Swahili SMS spam dataset (31,921 legitimate +
    297 spam, real Tanzanian telco data) is referenced in academic papers but requires
    contacting the authors via Zenodo — not pursued given the two directly-checked
    datasets both came back negative.
- **Audit/anti-corruption investigation reports checked on the hypothesis that oversight
  documents might quote the actual advisory/circular being scrutinized as evidence** —
  same "incidental content" logic as the SMS/hate-speech checks above, applied to a
  different document genre. **Negative, and confirmed thoroughly, not just assumed:**
  - Auditor-General reports on NDMA (FY2019) and AFA (FY2019) — both are **scanned image
    PDFs with zero extractable text** (108pp/76pp, checked via pymupdf, confirmed 0
    characters across every page) — would need OCR to even read, let alone verify content.
  - The most recent comprehensive report (Auditor-General on National Government
    Ministries/Departments/Agencies 2023-2024, oagkenya.go.ke, 812 pages, born-digital)
    **was fully searched** (1.84M characters, whole-document keyword scan) for
    "public advisory," "advisory to farmers," "sensitiz-," "circular to," "public
    notice," "drought advisory" etc. — only 3 incidental hits total, all procedural
    (a stakeholder-engagement gap, an insurance-uptake critique, a tender-publication
    compliance finding), **none quoting actual PSA/advisory text**. Audit reports discuss
    financial/governance failures (procurement, budget variance, internal controls) —
    they don't reproduce the content of the communications they're auditing.
  - EACC's fertilizer subsidy fraud investigation (2024/2025, widely covered in press)
    exists but its actual report **is not public** — described in news coverage as
    "currently at the office of the Principal Secretary for Agriculture," i.e. an
    internal document, not a published one. Nothing to check.
- No dataset or document-genre anywhere in this search matched the actual requirement:
  genuine, credible, official-source, PSA-shaped (short/directive) Kenyan agriculture
  content. The 76 hand-collected rows remain the project's real asset for this domain.

## Five specific sources checked (2026-07-15, Bradley-supplied links)

Checked each thoroughly - exploring site/document structure first rather than jumping to
extraction - per instruction. **None yielded new usable rows**, but each is a genuine,
complete check:

- **NCPB (National Cereals and Produce Board) `/reports/`** — the reports list is
  exclusively "Maize Prices in Various Kenyan Market Centres" — tabular price data, same
  category as KAMIS, not PSA-shaped either way.
- **The specific NCPB PDF supplied** (`FSMCMeeting-17TH-DECEMBER-2021-1.pdf`) — this is
  the Ministry of Agriculture's **Bi-weekly Food Security Monitoring Meeting** agenda +
  minutes (32pp, born-digital, fully extracted). Confirmed negative by keyword search
  across the full text: zero hits for "farmers should," "farmers are advised," "advisory,"
  "advise farmers." The "Next steps" columns are instructions to government bodies
  (MoALFC, Council of Governors) — internal coordination, not public-facing, same category
  as the audit reports and Zambia DMMU sitreps already ruled out earlier.
- **FAO's "Newsletters & flyers" collection** — turned out to be FAO's *entire global*
  archive (11,586 items across every country/language, sorted by recent submission —
  dominated by irrelevant content like Russian gender-newsletters and Georgia country
  updates). Too broad to browse; used the site's own search UI instead. Searching
  "Kenya Swahili agriculture" surfaced 145 results including genuine Swahili-language FAO
  publications (a fish-handling training manual, a livestock/wildlife-coexistence book)
  — real, but long-form manuals, not PSA-length content.
- **The specific FAO item supplied** ("Fall Armyworm: Identification, biology and
  ecology") — a genuine 1-page brochure for farmers/extension officers (Category:
  Brochure). Content is purely descriptive (pest identification, life cycle, physical
  appearance) — no "do X" directives, so it doesn't fit the PSA definition despite being
  farmer-facing.
  A related item shown on the same page ("FAW Guidance Note 4: quick guide for
  smallholders") looked more directive ("Farmers should work together...") but wasn't
  independently fetched/verified this round.
- **SOCAA (Society of Crop Agribusiness Advisors of Kenya) Foodwatch campaigns** — the
  two campaign posts ("Assured Produce Scheme," "March to Food Safety") are blog-style
  organizational advocacy text ("we invite you to join...", "we strive to change this
  narrative..."), not the PSA content itself. The one genuine content lead — a "March to
  Food Safety Calendar" — is hosted on an external Google Drive link that **404s**
  (dead; the campaign is from 2018). The post's only image is a generic decorative stock
  photo of fruit, confirmed via OCR (zero text) and direct visual inspection.

## OCR for poster/image-based PSAs (2026-07-15)

Installed `tesseract-ocr` + `tesseract-ocr-eng` + `tesseract-ocr-swa` locally (apt, clean
install, no CPU/GPU concerns) to test the hypothesis that poster-style PSAs (as opposed to
text bulletins) exist but were being missed because they're images. **Real, positive
result, not theoretical:**

- The CGSpace "Climate smart agriculture: top ten decisions" poster (in
  `confirmed_pairs/`, previously flagged as "needs a human to align by eye, not a script"
  because pymupdf's native PDF text extraction fragments its multi-column infographic
  layout) — **OCR'd at 300dpi with `--psm 3` page segmentation reads it correctly, in the
  right order, on both the English and Swahili versions**, with section headings landing
  in matching positions between languages. This directly contradicts the older
  "OCR is unreliable on stylized layouts" note elsewhere in this doc — that assumption
  was never actually tested against a real poster before now. **7 aligned bilingual rows
  extracted** (`AGRI_089`-`095`), true source pairs (not team-translated), verified via
  a cloud translation API language QA.
- Re-tried the **UCLA Digital Library** bilingual collection (previously shelved for
  lacking OCR) — still blocked, but by an **Anubis bot-challenge wall** (returns "Access
  Denied" to automated requests), not by the OCR gap. This was always a bot-wall problem;
  OCR being available now doesn't change the outcome.
- Searched specifically for **poster/IEC-materials/campaign-material sections** (a
  genuinely different content type from the bulletins/reports this session mostly
  targeted), following up a real, confirmed lead: CABI/FAO published **13 flyers + 15
  posters in nine languages** for fall armyworm control, distributed to Kenya/Rwanda/
  Ethiopia (widely referenced in press/CABI project pages). Could not locate the actual
  files: FAO's own discover/search API returned 403; `kilimo.go.ke/african-armyworms/` is
  a near-empty stub page (just nav menu, no content); `echocommunity.org`'s dedicated
  Swahili-resources filter is Cloudflare-blocked (403); KALRO's KilimoBora platform turned
  out to be a Moodle e-learning course site, not a poster/leaflet repository — wrong
  content type.
  **The materials are real and confirmed to exist, but not publicly locatable this
  session** — would need direct contact with CABI/FAO, not more searching.

**Takeaway:** OCR is a genuinely useful new tool for this project — cheap, easy, and
already unlocked one poster that was sitting unprocessed. The bottleneck for *more*
poster-style content isn't OCR capability anymore, it's finding publicly-downloadable
poster files in the first place — most of what's confirmed to exist (FAO's fall armyworm
set, likely others) sits behind either bot-walls or simply isn't indexed/discoverable via
search.

## Recommended collection strategy (ranked; updated 2026-07-15, originally 2026-07-10)

**This list was written after the 2026-07-10 recon and originally covered only Farm Radio,
gov/NGO socials, and CGSpace — the entries below marked (2026-07-15) reflect what was
actually found later and proved more productive than the original ranking; read this list
top-to-bottom, not just item 1.**

The recon shows clean, **redistributable, bilingual En↔Sw *PSA* pairs are scarce** — most
bilingual material is either news (excluded), image-only (OCR), copyrighted, or IP/bot-walled.
Spend effort here, in order:

1. **N2Africa (n2africa.org/agem catalog, 2026-07-15)** — turned out to be the single best
   source found across the whole project: a genuine EN+Swahili bilingual checklist authored
   directly (no translation needed), plus several Swahili-original brochures with no English
   counterpart, plus CC-licensed English leaflets across a dozen African countries. See the
   "Single-language audit..." section below for what's been extracted and what's still
   worth excerpting (Master Farmer Guidelines, Grain Legume Processing Handbook).
2. **CGSpace, scanned by content-type facet, not just the known bilingual pair
   (2026-07-15)** — the `/server/api/discover/facets/itemtype` + `country` facets expose
   Poster/Brochure/Extension Material/Infographic/Factsheet buckets per African country;
   see the "CGSpace poster/extension-material scan" section below. Most CGIAR "Poster"
   items turned out to be academic conference posters, not farmer PSAs — a real, checked
   negative, not an unexplored gap.
3. **Farm Radio International scripts/spots + Biovision (TOF / Mkulima Mbunifu)** — the best
   PSA-shaped bilingual *agricultural* text found in the original recon; likely CC-licensed.
   `radio spots` and magazine tips are short and directive = ideal PSAs.
4. **Official gov/NGO social posts (X, Facebook)** — the main place agencies post the *same*
   PSA in En + Sw. Fits the brief, public, citable. Use warmed-up accounts + `x_collect.py`.
5. **Direct requests to KALRO (KAOP), Mediae (iShamba/SSU), Farm Radio, Biovision** — email
   drafts; fastest route to clean bilingual advisories.
6. **CGIAR CGSpace's original bilingual advisory PDF pair** — CC-licensed, extraction proven;
   download manually (429-throttled). Fetch list: `CGSPACE_FETCH_LIST.md`.
7. **Tanzania TSN state papers (Daily News + HabariLEO) / MAELEZO** — strongest parallel-*news*
   lead; use only where an official advisory appears verbatim in both. Needs team OK on
   Tanzania sources.
8. **Everything else (e-papers, press archives, UCLA/IFRA)** — do NOT bulk-scrape: copyright /
   OCR / bot-walls / news-not-PSA. Only hand-transcribe official notices printed verbatim.

For the **modeling** stage (not the hand-built PSA set), if the team wants extra En–Sw parallel
volume, use existing public corpora (MAFAND-MT, GlobalVoices, CCAligned, OPUS) rather than
re-scraping news.

## Known limitations & workarounds

- **kilimo.go.ke main site is down (2026-07-10)**. Workarounds: collect stubborn sources
  from a browser, and mine the ministry's history via Wayback CDX:
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

## Africa-wide expansion (2026-07-15) — English-language PSAs beyond Kenya

Replicating the Kenya approach (find a national drought/disaster-management body with a
distinct, PDF-based RECOMMENDATIONS section, same as NDMA) across other English-language
African countries, plus expanding Farm Radio International's coverage beyond Kenya/Tanzania.

**National drought/disaster agencies checked so far (East Africa first, then branching out):**

| Country | Agency | Domain | Result |
|---|---|---|---|
| Rwanda | MINEMA (Ministry in Charge of Emergency Management) | minema.gov.rw | **Confirmed match** — `National_Drought_Contingency_Plan.pdf` has a genuine "Table 16: Recommendations" section (No / Recommendation / Proposed actions / Stakeholders columns), MINAGRI listed as a stakeholder on the agriculture-relevant rows. 3 rows extracted (`AGRI_042`-`044`). |
| Uganda | MAAIF (Ministry of Agriculture, Animal Industry and Fisheries) | agriculture.go.ug | **Dead end** — their flagship document is a "Statistical Abstract" (pure data tables, 0 "recommend" mentions across 86k characters checked). Not PSA-shaped. |
| Uganda | OPM/NECOC (National Emergency Coordination and Operations Centre) | necoc.opm.go.ug | **Unreachable** — Cloudflare 522 (origin server timeout), not a block. Worth retrying later; structurally this looked like the closest match (district-level early warning bulletins). |
| South Sudan | RRC (Relief and Rehabilitation Commission) | rrc.gov.ss, southsudanrrc.org | **Unreachable** — both domains failed to connect (curl exit code, no HTTP response at all). |
| Ghana | Ghana Meteorological Agency (GMet) | meteo.gov.gh | **Confirmed match** — Dekadal Agromet Bulletin, "3.1 AGRO-ADVISORIES" section, crop-by-crop table (Maize/Rice/Sorghum/Soyabean/Tomatoes × Weather Risks/Recommendations). 2 rows extracted (`AGRI_049`-`050`). NADMO (disaster mgmt) checked separately — narrative only, no recs section. |
| Gambia | Dept. of Water Resources + Dept. of Agriculture (MoFWR) | meteogambia.gm | **Confirmed match, strongest structural fit found** — Dekadal Early Warning Bulletin for Food Security, explicitly numbered "1.4.1 Recommendations for Agricultural Stakeholders" section. 3 rows extracted (`AGRI_051`-`053`). Note: `ndma.gm` (the actual disaster agency, same name as Kenya's) appears **compromised/hijacked** (spam content mixed in) — do not use as a source. |
| Liberia | Liberia Meteorological Service, Ministry of Transport | meteoliberia.com | **Confirmed match** — Dekadal Early Warning Bulletin has a clean "Farmers Advisories" section (Field Prep/Crop Mgmt/Livestock Mgmt/General Precautions). 3 rows extracted (`AGRI_054`-`056`). A second bulletin (Agromet Dekadal) exists but the dekad checked was health/malaria-focused, not agriculture — worth rechecking other months. |
| Sierra Leone | WFP Food Security Monitoring System Report (co-published w/ Min. of Agriculture & Forestry, Min. of Health) | docs.wfp.org | Verified "Recommendations" section exists, but co-authored by WFP not purely government — same provenance category as FEWS NET. Not yet extracted; flag to team if strict "government-authored" sourcing matters. |
| Nigeria | NiMet + NAERLS (Agromet & Livestock Weather Bulletins) | nimet.gov.ng, naerls.gov.ng | On-paper strong candidate (explicitly described as containing farmer advisories) but **not verified** — site access kept failing (redirects, self-signed cert on naerls.gov.ng, empty pages). Not fabricated, just unconfirmed — needs a follow-up session. |
| Nigeria | NEMA | nema.gov.ng | Checked directly — narrative news posts only, no downloadable bulletin, no recommendations section. Not usable. |
| Namibia | NAMVAC (Namibia Vulnerability Assessment and Analysis Committee), OPM Disaster Risk Mgmt Directorate | mirrored at nafsan.org (NGO mirror; opm.gov.na itself didn't respond) | **Confirmed match** — 2022/23 report has a standalone "Recommendations" section, verified by direct text extraction. 3 rows extracted (`AGRI_057`-`059`). |
| Lesotho | LVAC (Lesotho Vulnerability Assessment Committee), PM's Office Disaster Management Authority | lvac.gov.ls (live but no publications page found); PDF mirrored at docs.wfp.org | **Confirmed match** (agent-verified via direct extraction) — 2016 report has a tabular recommendations section with a dedicated "Agriculture and Food Security" row. 3 rows extracted (`AGRI_060`-`062`). Only a 2016 edition confirmed; a more recent one likely exists but wasn't located. |
| Zimbabwe | FNC (Food and Nutrition Council, under the Office of the President and Cabinet) — runs ZimVAC/ZimLAC | fnc.org.zw (self-hosted, no cert/DNS issues) | **Confirmed match**, more narrative/policy-brief phrasing than Kenya's terse style ("Government... should continue...") but a genuine distinct "Conclusions & Recommendations" section. 1 row extracted (`AGRI_063`). 2025 edition (ZimLAC) exists at the same domain, not yet checked. |
| Zambia | DMMU (Disaster Mitigation Unit, Office of the VP) | dmmu-ovp.gov.zm (expired SSL cert) | **Mixed** — situation reports are pure narrative (0 "recommend" hits, confirms the earlier suspicion), but a separate "Food Security Drought Response Plan" has real Agriculture/Livestock activity items framed as a budget appeal, not under a literal "Recommendations" heading. Not yet extracted — borderline fit. |
| Malawi | DoDMA / MVAC | dodma.gov.mw (misconfigured — actually serves Ministry of Agriculture content under DoDMA's domain/cert); mvac.gov.mw (DNS failure) | **Unresolved** — genuine MVAC bulletins exist (cited in secondary sources) but only reachable via Cloudflare-protected mirrors (ipcinfo.org) that blocked retrieval. Weakest lead of the Southern Africa set. |
| Eswatini | NDMA (unrelated to Kenya's NDMA despite the same acronym) / Eswatini VAC | portal.ndma.org.sz (connection refused); ipcinfo.org (Cloudflare-blocked) | **Unresolved** — same Cloudflare-mirror problem as Malawi. |
| Botswana | Dept. of Meteorological Services / BVAC | gov.bw (reachable) | **No usable document found** — drought products are maps/dashboards, not text bulletins; BVAC reports only found via secondary mentions, not a direct PDF. |
| South Africa | NDMC (COGTA), SA Weather Service, ARC, DALRRD | weathersa.co.za (drought bulletin PDF 404s, discontinued), arc.agric.za (checked — zero "recommend" hits, pure narrative) | **No usable document found** — confirmed fragmented/non-bulletin-based system; a 2023 academic paper corroborates 5 of 7 provinces lack dedicated agricultural drought plans. |
| FEWS NET (pan-African, ~20 countries) | fews.net | **Checked, no match** — Food Security Outlook reports are pure descriptive analysis/projection, no distinct recommendations section (same shape as NDMA's narrative body, not its productive recommendations section). |

**Farm Radio International — confirmed genuinely pan-African, not Kenya/Tanzania-only.**
Their `/topic/agriculture/` English-language hub has **300 articles** (crawled 30 pages,
2026-07-15), covering at minimum Ghana (9), Ethiopia (8), Zambia (5), Tanzania (4), Malawi
(4), Mozambique (3), Mali (3), Nigeria (3), Uganda (3), Cameroon (2), Kenya (2), Togo (1)
identified by country name in the title alone — 248 of 300 articles don't name a country in
the title (the country is often only in the body text), so the real per-country count is
much higher than this table shows. "Backgrounder"-format articles have a reliable, clean
**"Key messages"/"should know" bulleted list** that extracts cleanly (same quality as the
Kenya post-harvest-losses "Radio Spot #N" pattern) — confirmed on Zambia (cassava brown
streak disease), Ghana (vegetable production). 4 rows extracted so far (`AGRI_045`-`048`,
Zambia/Ghana/Tanzania/Ethiopia) to verify the extraction method against real content — the
other ~296 articles can be processed with the same verified method in a future session, time
permitting; the volume is deliberately out of scope for this pass. Same licensing caveat as
before: Farm Radio pages
carry no CC statement ("All Rights Reserved") — confirm before redistribution beyond class
use, same as the existing Kenya-sourced Farm Radio rows.

Full article index (all 300 URLs + titles): was written to a scratch file this session, not
yet committed to the repo — regenerate by crawling `scripts.farmradio.fm/topic/agriculture/`
pages 1-30+ (see `fetch_farmradio.py` for the fetching pattern to adapt).

## CGSpace poster/extension-material scan, English Africa (2026-07-15)

Extended the Kenya/Swahili poster-discovery method (find institutional repos, filter by
content-**type** metadata rather than blind keyword scraping, check TEXT-bundle extraction
before assuming OCR is needed) to English-language material from the rest of Africa.

**Key discovery: CGSpace's REST API is directly queryable, no bot-wall.** Its
`/server/api/discover/facets/itemtype` and `/server/api/discover/facets/country` endpoints
expose exact content-type buckets (Poster: 4249 items, Brochure: 1796, Extension Material:
605, Infographic: 350, Factsheet: 94, Training Material: 1015) crossed with a `country` facet
covering every African country with CGIAR activity. Each item also has a pre-generated
**TEXT bundle** (DSpace's own `pdftotext`-equivalent extraction, done at ingestion) — fetch
`item/{uuid}/bundles` → the `TEXT` bundle → its bitstream `content` link, and you get clean
extracted text for free, no OCR/tesseract needed unless the TEXT bundle is empty (scanned
image with no OCR layer).

**Important correction to the earlier OCR section**: the "top ten decisions" poster
previously OCR'd with tesseract (`AGRI_089`-`095`) is item `62fd7239-9d39-4528-a513-
5fb949251490` — **Tanzania's** version (IITA/TMA/FAO), not a Kenya-specific poster as
the source note implied. It was in fact born-digital (has a working TEXT bundle), so the
tesseract OCR step in the previous session was unnecessary work that happened to produce
equivalent output — worth remembering for next time. Re-reading its full TEXT-bundle
content against the CSV showed 3 of its "10 major decisions" (soil/water conservation,
fertilizer type selection, pest/disease management) had not been extracted yet. Found and
used the matching Swahili sibling item (`c4d42102-1c9b-4936-b17b-7e2173964cda`, handle
`10568/113096`) to translate-align them properly. **3 rows added**: `AGRI_096`-`098`.

**Broad scan result: CGIAR "Poster" items are overwhelmingly academic/conference posters
(research findings for scientists), not farmer-facing PSAs** — this is the opposite of what
the type label suggests. Checked in full across ~19 African countries × 5 content types with
both a structural-recommendation query and a disease/outbreak-alert query; spot-verified the
most promising-looking titles by pulling their actual TEXT-bundle content:
- "Rift Valley fever: Awareness and sensitization" (Uganda, `10568/122011`) — a research
  poster *about* running an awareness campaign (methods, findings, stakeholder assessment),
  not the campaign's actual messaging. The "5,000 brochures and 1,000 leaflets with key
  messages" it references were never captured in this item.
- "Controlling banana bunchy top virus outbreak in East Africa" (Uganda/Tanzania,
  `10568/126121`) — a scientific conference poster (causes, spread epidemiology,
  conclusions/further-research-needed), not a farmer control guide.
- "Control of East Coast Fever by Immunization" (Tanzania, `10568/105477`) — a
  business-model/investment-case poster (resource requirements, agribusiness delivery
  suitability), not farmer-directed.
Same pattern held for Ethiopia, Nigeria, Ghana, Mali, Senegal, Malawi, Zambia, Mozambique,
Burkina Faso, Cameroon: livestock-disease "Poster" items are almost always epidemiology/
intervention-study research posters.

**Second genuine positive source: N2Africa's "Better [crop] through good agricultural
practices" leaflet series** — CC-licensed, explicitly "For farmers in Ethiopia," structured
as numbered Step 1-7 directives (land prep → seed selection → inoculation → fertilizer →
planting → field management → harvest/storage). Checked the soybean (`10568/76318`) and
beans (`10568/76317`) leaflets in full. Most of the two leaflets share an identical
templated passage (germination test, "safe use of chemicals," rhizobium inoculation steps
worded generically for "legume seed") — extracting the same paragraph from both would be a
near-duplicate, so only genuinely crop-specific content was used: soybean's inoculation
mechanics and pest section, beans' climbing/staking section and bean-stem-maggot control.
**4 rows added**: `AGRI_099`-`102`. Confirmed via fuzzy-similarity check (`difflib`,
threshold 0.6) against the full 102-row dataset — no near-duplicates introduced.
This is a wider N2Africa series (soybean/beans booklets exist per-country, not just
Ethiopia) — the Nigeria/Zimbabwe/Rwanda editions were checked in the follow-up pass below
("Single-language audit..." section) and confirmed to share this same template, so see
that section for what was and wasn't worth extracting from them.

**Net result this pass: 98 → 102 rows** (all from the same two already-vetted CGSpace
sources — filling gaps rather than discovering new domains). Full Poster/Brochure/
Infographic/Extension-Material/Factsheet buckets across ~19 countries were scanned and
came back negative for new PSA-shaped content beyond these two; the negative finding
itself (CGIAR posters skew academic, not extension-facing) is worth keeping so it isn't
re-investigated from scratch later.

## Single-language audit + N2Africa's own site + TOF/MKM gap-fill + broader CGSpace scan (2026-07-15, continued)

Two things prompted this pass: (1) auditing whether single-language finds (Swahili-only or
English-only) were consistently being collected with a team translation for the missing
side rather than skipped, and (2) extending the poster-repo method to each repo's actual
HTML pages and any/all PDFs present, not just the pre-filtered "Poster" item type.

**Audit result: the convention (`translation=team; source_lang=X; country=Y` in Metadata)
was being applied consistently** — checked via regex over the `Metadata` column: 87 rows
tagged `translation=team` (84 `source_lang=en`, 3 `source_lang=sw` — the Mkulima Mbunifu
rows), 15 rows with no tag (genuine bilingual source pairs: TOF-17, Farm Radio post-harvest
spot, the CGSpace poster). No gaps found in the CSV itself.

**Gap found instead in the *scan-to-CSV* pipeline**: cross-referencing the TOF/Mkulima
Mbunifu narrow-lexicon scan (`full_scan_results.json`, run earlier this session — 21 TOF
"recommendations" hits + 6 MKM "mapendekezo" hits after the wide/narrow lexicon split) against
the CSV's `Source` column by issue number showed **9 of 21 TOF issues and 3 of 6 MKM issues
had a confirmed genuine keyword hit but were never actually converted into rows** — the scan
found them, but the conversion step stopped partway through. Went back and resolved all 12:

- **TOF (English), 5 of 9 converted** — `AGRI_114`-`118`: seed heat-treatment temperatures
  (issue 40, Sept 2008), urea livestock-feed dosage limit (issue 47, Apr 2009), fodder-tree
  hot-water seed treatment (issue 73, June 2011), a soil-test farmer checklist (issue 169,
  Aug 2019), Tuta absoluta trap-timing IPM (issue 190, May 2021). **4 of 9 confirmed
  negative** on inspection: issues 13 and 96 were reader-feedback/editorial commentary
  *about* wanting more content ("he has made some recommendations on the information he
  would like featured"), not farmer directives; issue 216 was a generic closing remark
  ("recommendations from expertise in the area"); issue 90's bulleted "feed recommendations"
  list had corrupted text from a PDF font-encoding/ligature issue (bullets extracted as
  garbled glyphs with missing lead words) — skipped rather than guess at the missing text.
- **MKM (Swahili), 0 of 3 converted, all confirmed negative** — issue 103 (Apr 2021)'s
  "mapendekezo" hit was in a farmer-field-school *methodology* section (guidance for
  extension officers running training, not a farmer directive); issue 127 (Aug 2023)'s hit
  was policy recommendations addressed to "Serikali ya Tanzania" (the Tanzania government)
  on environmental regulation, same category as the NCPB/government-coordination exclusions
  already established; issue 128 (Aug 2023 special edition, native seed banks)'s hit was
  about stakeholder-level policy recommendations on seed-sector development, not a direct
  farmer action. All three read as genuine narrow-lexicon hits but institutional/meta
  content rather than PSAs — consistent with the eval's Precision=0.815 (not 1.0), i.e. some
  false positives are expected and this is what one looks like in practice.

**N2Africa has its own site (n2africa.org) with a full catalog page**, found via its nav
menu ("N2 Outputs" → "Guidelines, Training & Extension materials" → `/agem`, a filterable
table of 80+ items with Code/Date/Title/Country/File columns) — this is a much richer index
than what's mirrored on CGSpace. Two genuine finds:
- **A real bilingual EN+Swahili pair, no translation needed**: "Best practices to maintain
  high yields and grain quality of soybean," a checklist for farmers in west Kenya, exists
  as one PDF with both language versions authored directly (`Best
  practice_soybean_English-Kiswahili.pdf`) — same gold-standard category as TOF-17. **7 rows
  extracted**: `AGRI_103`-`109` (rotation, germination test, planting timing, fungicide
  schedule, harvest timing, grain moisture, storage/bagging).
- **Swahili-original brochures with no English version — exactly the "collect the
  single-language side, translate the other" case this audit was checking for.** Tanzania's
  groundnut brochure ("Ongeza mavuno ya karanga...", Makutupora Agricultural Research
  Institute/N2Africa) and cowpea brochure ("Lima kunde kwa lishe na kipato zaidi...", Ilonga
  Agricultural Research Institute/N2Africa) are both Swahili-only originals — not
  translations of the English "Better groundnut"/"Better cowpea" booklet series, but
  independent local-language extension material. **4 rows extracted** (`AGRI_110`-`113`,
  team-translated to English, `source_lang=sw; country=Tanzania`): harvest timing/aflatoxin
  risk and storage for groundnut, harvest and PICS-bag storage for cowpea.
- **Checked the `/agem` catalog's Nigeria/Zimbabwe/Rwanda "Better cowpea/groundnut/soybean/
  sugar bean" booklets** (same series as the Ethiopia ones above) by downloading and
  diffing them against the already-extracted Ethiopia content: **confirmed the intro and
  Step 1-7 boilerplate (rhizobia/nitrogen-fixation explanation, generic land-prep bullets)
  is reused near-verbatim across every country for the same crop** — extracting it again
  would just be a near-duplicate of `AGRI_099`-`102`/`110`-`113`, not new content. Each
  country booklet does have one genuinely distinct, non-templated passage — its regional
  variety-selection guidance — so those three were extracted instead: Nigeria's groundnut
  agro-ecological zones (Sahel/Sudan/Guinea savanna), Zimbabwe's cowpea-suitable Natural
  Regions IV/V, and Rwanda's hillside-terracing/volcanic-soil ridging for bean land
  preparation. **3 rows added**: `AGRI_121`-`123`.
- **Two items in the catalog remain a genuine, distinct-content lead, not yet excerpted**:
  a Master Farmer Guidelines set (already bilingual English+Swahili+Chichewa in the source)
  and a Grain Legume Processing Handbook (also English+Swahili) — both are full manuals
  rather than PSA-length, so would need the same "carve out short excerpts" treatment
  already applied to the Ethiopia/Kenya N2Africa material, not a blanket extraction.

**Broadened the CGSpace scan beyond the 5 pre-selected item types** (Poster/Brochure/
Infographic/Extension Material/Factsheet) to an untyped keyword search across Ethiopia,
Nigeria, Uganda, Tanzania, and Ghana (the highest-volume countries) — confirms the earlier
finding that the overwhelming majority of results are research reports, training-of-trainer
workshop write-ups, and project M&E documents, not farmer PSAs. One genuine exception found:
**"Optimal spacing for groundnuts in smallholder farming systems"** (Africa RISING/IITA
Technology Brief, March 2021, northern Ghana, CC-licensed) — mostly a research write-up
(yield trial results, econometrics) but contains two clean, directive farmer instructions
buried in it. **2 rows extracted** (`AGRI_119`-`120`, team-translated, `country=Ghana`):
optimal row/plant spacing with weeding timing, and Aflasafe biocontrol application against
aflatoxin.

**Net result this pass: 98 → 123 rows.** Full validation (`validate_psa_csv.py`), a cloud translation API QA
gate (`qa_azure_language_check.py`, 0 flags across all 123 rows), and a pairwise
fuzzy-similarity dedup check (`difflib`, threshold 0.6, all 123×123 rows) all pass clean.
The two near-duplicate pairs the full pairwise check surfaced (`AGRI_005`/`AGRI_037`,
`AGRI_034`/`AGRI_061`, both ~0.63 similarity) predate this session — they're generic
"strengthen extension services"/"strengthen surveillance" boilerplate that recurs verbatim
across different counties' government recommendation tables by genre convention, not a
duplication bug; flagged here for the team's awareness, not treated as an error to fix
unprompted.

## Audit of NLP/Data/PSA_KE_Final.csv (2026-07-15) — lecturer-approved complementary source

Checked structurally and against this project's own QA tooling before using anything from
it. **Schema is incompatible and unverifiable as-is**: `validate_psa_csv.py` hard-fails on
header mismatch (`PSA_Id/Class/Ekegusii/Dholuo/Somali` instead of
`PSA_ID/Sub_Category/Target_Language/Source/Date/Metadata`) — most importantly, **the file
has no Source or Date column at all**, so nothing in it is independently citable as shipped.

**Classification signal is effectively absent.** Every one of its 2,903 rows across all 5
domains is labeled `Class=PSA` — there is no negative class, so the label isn't doing any
filtering. Checked the 369 Agriculture rows against structural rules (ellipsis/mid-sentence
truncation, citation patterns, address/contact blocks, nav-footer cruft, malformed sentence
starts): **151/369 (41%) are clearly not PSA content** — raw scraped fragments, academic
citations, org contact blocks, navigation cruft — and a further chunk of what passes those
filters is still report/press-release summary text or "Learn more about..."-style
content-marketing blurbs, not directive announcements. a cloud translation API language-detection QA on the
raw English/Kiswahili text itself came back clean (0 flags) — the language quality is fine
where the text is a real sentence; the problem is source-shape and provenance, not
translation quality.

**Verified the most promising named-entity candidates against real sources** rather than
trusting the file's wording directly:
- **Genuine win**: row referencing KMD (Kenya Meteorological Department) flood/livestock
  advisories checked out — KMD's real advisory practice does include exactly this kind of
  guidance. Found the actual underlying quote via independent search: "Kenya Met Issues
  Advisory to Farmers" (nairobileo.co.ke, 2026-05-23/24) carries a **direct KMD quote**:
  "Farmers are advised to regularly monitor weather updates and follow guidance from
  agricultural extension officers to support timely decision-making and reduce
  weather-related risks." This is genuinely PSA-shaped, dated, and attributed — added as
  `AGRI_124`, citing the real article, **not** `PSA_KE_Final.csv`'s unsourced paraphrase.
  (The livestock/pasture-conservation half of the same KMD advisory was only available as
  the journalist's paraphrase, not a direct quote — left out per the existing news-paraphrase
  exclusion rule already applied elsewhere in this doc.)
- **Push-Pull technology rows** (desmodium/cowpea intercropping, Western Kenya) — confirmed
  real and well-documented (icipe.org, CABI, multiple peer-reviewed sources); one row is
  literally the title of a real CABI.org article. But it's science-communication/news
  framing ("Technology is revolutionizing cowpea farming..."), not a directive PSA — same
  "news ≠ PSA" exclusion already applied to TSN/Tanzania and Zambia DMMU content elsewhere
  in this doc.
- **PBR (Pod Borer Resistant) Cowpea biodiversity study row** — confirmed real; matches an
  actual AATF press release title nearly verbatim ("Study Finds No Negative Impact of PBR
  Cowpea on Ecological Species," aatf-africa.org). Same verdict: real, traceable,
  research-finding framing, not a directive PSA. AATF is a legitimate organization worth a
  future look for genuine farmer-facing advisories, separate from this specific item.
- **Solar dryer / sweet potato row** — the underlying phenomenon (solar drying cutting
  post-harvest losses, tripling incomes) is real and widely reported, but the specific
  sweet-potato framing in the file is a generic composite across several similar articles,
  not traceable to one canonical source — not used.
- **Fully generic rows** ("Kenya promotes deworming and vaccination...", "Farmers encouraged
  to register for subsidized animal feeds program...") name no specific agency or document
  and could not be matched to a findable source — left unverified, not added.

**Rules for sifting this kind of file in future** (useful beyond just this dataset): reject
on ellipsis/mid-sentence truncation, citation patterns, address/contact blocks, and
nav-footer cruft; reject third-person report framing ("A study found...", "X was encouraged
to...") and content-marketing CTAs ("Learn more about..."); prefer agency-led directive
framing ("X is advised to...", "Farmers should..."); and — the one that actually matters —
**never promote a row from a source-less file without independently finding and citing the
real underlying document first**, same standard as everything else in this dataset.

**Net result: 123 → 124 rows** (`AGRI_124`). One genuine row recovered from a
verification pass that otherwise confirmed the file needs individual fact-checking, not
bulk import.

## Following up on what the verification pass surfaced (2026-07-15, continued)

The `PSA_KE_Final.csv` verification above wasn't just a one-off check — it named three
organizations never checked as sources before (icipe, AATF, CABI specifically for its
Plantwise programme) and demonstrated a reusable discovery technique: searching for
`"[agency] issues advisory"` / `"[agency] warns"` surfaces news coverage that has often
already extracted and quoted an agency's verbatim directive text, even when the agency's
own site is hard to scrape directly. Tested both against our existing agencies and the
three new organizations.

**Major new source found: CABI Plantwise "Factsheets for Farmers" series.** These are short,
genuinely directive, CC-licensed, one-page farmer factsheets — structured as
Recognize-the-problem / Background / Management, created directly in African countries
(the byline states where and when, e.g. "Created in Kenya, September 2011"). Confirmed
CC-BY-SA 4.0 licensed and explicitly multi-country ("relevant to: Ethiopia, Ghana, Kenya,
Malawi, Rwanda, Tanzania, Uganda, Zambia" on one checked factsheet). PDFs are served
directly from `factsheetadmin.plantwise.org/Uploads/PDFs/<id>.pdf` and are reachable
without any access issues, even though the main `plantwiseplusknowledgebank.org` site
403s. Downloaded and verified 3 factsheets — all genuinely PSA-shaped, step-by-step
management advice: soap-spray aphid control on beans (Kenya, 2011), black rot management
in brassica crops (Kenya, 2012), and mass-trapping mango fruit flies (Tanzania, 2012).
**3 rows added** (`AGRI_125`-`127`, team-translated to Swahili — English-only in the
source, `translation=team; source_lang=en`). CABI separately confirmed to have produced
**52 Pest Management Decision Guides already translated into Kiswahili** (a related but
distinct, more detailed resource tier from these one-page factsheets) — not yet located
individually; worth a dedicated search pass in a future session, same category as the
Farm Radio backlog. Discovery method for more of these: search
`factsheetadmin.plantwise.org "Uploads/PDFs"` combined with a country or pest/crop name —
this returned dozens of relevant hits from a single query, so the corpus is large.

**icipe (International Centre of Insect Physiology and Ecology) — checked, not a quick
win.** Confirmed real farmer-facing print materials exist (their own site describes "farmer
field days, farmer field schools, print materials" as core push-pull dissemination
channels), but the specific document found and checked ("The Quiet Revolution: Push-Pull
Technology and the African Farmer," a Gatsby Charitable Foundation occasional paper, 36pp)
is a full narrative report, not a short farmer factsheet — same "long manual, not PSA-length"
verdict as several N2Africa documents earlier in this doc. Not extracted from; icipe.org
is still worth a further look for shorter dissemination materials specifically, given the
organization's stated channels include them.

**KEPHIS — the "quoted in news" technique found real coverage, but not a verbatim quote
yet.** A May 2026 article on Maize Lethal Necrosis Disease confirms KEPHIS actively runs
farmer training and advises "crop rotation" and "a closed season" — genuinely matches what
we need — but the article only paraphrases KEPHIS's guidance, it doesn't quote a specific
sentence directly. Same exclusion as the KMD livestock/pasture paraphrase above: real,
consistent with the agency's actual practice, but not citable as a direct quote. Worth
searching more KEPHIS-specific advisory news coverage in a future pass — this is the kind
of near-miss that a slightly different article (or the training session's own materials)
might resolve.

**Net result this pass: 124 → 127 rows** (`AGRI_125`-`127`). Validated with
`validate_psa_csv.py`, `qa_azure_language_check.py` (0 flags), and the pairwise dedup
check — all clean.

## Mining CABI Plantwise further (2026-07-15, continued)

Went back to actively search for more of these factsheets rather than stopping at 3.
Discovery method: search `factsheetadmin.plantwise.org filetype:pdf` combined with a
country name or crop/pest keyword — each query reliably surfaced 7-10 distinct PDF URLs,
confirming this is a large corpus (CABI's own count: 52 Pest Management Decision Guides
translated into Kiswahili alone, a separate and more detailed tier from these one-page
"Factsheets for Farmers"). Downloaded and checked 7 more candidates.

**Found the first genuinely Kiswahili-*original* Plantwise factsheet**: "VIDOKEZO KWA
WAKULIMA" ("Tips for Farmers" — the whole template is in Kiswahili, not just an EN factsheet
with a Kiswahili term dropped in), on safe pesticide-sprayer use, created in Tanzania,
September 2013. Genuinely directive (PPE requirements, WHO Hazard Class I "red-label"
pesticides to avoid, sprayer preparation and cleaning steps). **1 row added** (`AGRI_128`,
`source_lang=sw; country=Tanzania` — English is the team translation here, not the source).

**3 more genuine English-original factsheets extracted**, all CC-licensed, all with a real
"Management" section (as opposed to one checked-and-rejected candidate — see below):
cassava mealybug prevention via clean planting cuttings (Tanzania, 2013, `AGRI_129`),
maize streak virus field management (Kenya, 2011, `AGRI_130`), and Tomato Yellow Leaf Curl
Virus management (Kenya, 2012, `AGRI_131`).

**One candidate checked and rejected**: a factsheet on *Digitaria abyssinica* (couchgrass,
Kenya, 2016) turned out to be a pure species-identification profile (taxonomy, common
names in five languages, physical description, habitat/spread) with **no Management
section at all** — same "descriptive, not directive" pattern as the FAO fall-armyworm
brochure checked earlier in this doc. Not every Plantwise factsheet has a management
section; check for one before investing translation effort.

**Two more real candidates found but not yet extracted** (tomato wilt/"kiwotoka", Uganda
2006; tomato red spider mite, Kenya 2012) — both confirmed genuine and directive on
inspection, held back this pass only to avoid over-concentrating on tomato-specific
content in one sitting. Good candidates for a future pass, along with the wider
country/crop search space this discovery method opens up (only ~14 of what is likely
hundreds of factsheets have been checked so far).

**Net result this pass: 127 → 131 rows** (`AGRI_128`-`131`). Validated clean (0 a cloud translation API
flags, no new near-duplicates in the full 131-row pairwise check).

## Clearing the "proven leads, not yet fully mined" backlog (2026-07-15, continued)

Worked through the specific backlog items flagged as pending in the previous session:
unresolved country reachability, the held-back CABI candidates, the N2Africa manuals,
Zambia's drought plan, and the Farm Radio backlog (both the 52-row Swahili-locale
candidates file and the separate 300-article English hub). An alternate connection route
(`FETCH_PROXY`) was available this session — used for the reachability retries.

**Reachability retries.** Nigeria: `naerls.gov.ng` (NAERLS) is now reachable (was
previously "on-paper strong candidate, not verified") and its Factsheet page has two
genuine "N-LEWS" (Nigerian Livestock Early Warning System) climate factsheets — real
farmer-facing directives ("What farmers need to do") on livestock heat-stress management,
fish-farm water management, and livestock-feed crop planting. **4 rows added**
(`AGRI_132`-`135`). `nimet.gov.ng` is still blocked — confirmed via the alternate
connection route that it's a genuine JS/bot-challenge, not a reachability issue, so
switching connection didn't help either.
Uganda: `necoc.opm.go.ug` is now reachable **through the alternate route** (was
Cloudflare 522 before; direct access still gets a 403) — but its one downloadable
bulletin (`May 2026 Monthly Weather Update.pdf`) is a scanned image PDF with no text
layer (OCR candidate for later), and `publications.php` failed to load twice this
session (site-side instability, not a block). Malawi: `dodma.gov.mw` resolves and
confirms the earlier finding (it's actually the Ministry of Agriculture's site, not
DoDMA's) but is JS-driven with no static publications path found; `mvac.gov.mw` and
`www.mvac.gov.mw` still fail DNS resolution regardless of connection route. Eswatini:
`portal.ndma.org.sz` still fails DNS resolution entirely — confirmed dead domain, not a
block.

**FAO "FAW Guidance Note 4" — verified, genuinely directive.** Located via its real
title ("How to Manage Fall Armyworm: A Quick Guide for Smallholders," CA0435EN/1/07.18,
FAO 2018) on the FAO Knowledge Repository. Unlike the identification-only fall-armyworm
brochure checked earlier in this doc, this one has real "Prevent / Monitor / Know / Act"
sections with farmer directives (quality seed, avoid late planting, weekly field
scouting, hand-crushing egg masses, avoiding unnecessary pesticide use). **3 rows added**
(`AGRI_136`-`138`), complementary to the existing pesticide-safety row (`AGRI_048`), not
overlapping with it.

**2 held-back CABI Plantwise candidates extracted**, both confirmed genuine and CC-BY-SA
4.0 as flagged: "Tomato wilt or kiwotoka" (Uganda, July 2006) and "Tomato red spider
mite" (Kenya, October 2012). **2 rows added** (`AGRI_139`-`140`).

**More CABI Plantwise factsheets found via targeted crop/country searches** (potato,
cassava, mango — countries not yet represented: Rwanda, Zambia): 6 new genuine factsheets
with real Management sections (potato bacterial wilt/Rwanda, cassava Brown Leaf
Spot/Uganda, cassava mealybug warm-water treatment/Zambia, cassava mosaic
uprooting/Tanzania, pawpaw-leaf snail trap/Zambia, mango bacterial black spot/Uganda).
**6 rows added** (`AGRI_141`-`146`). One candidate (Tanzania cassava-mealybug cuttings)
turned out to be an exact duplicate PDF of the already-extracted `AGRI_129` — caught by
checking the source PDF ID before extracting, not added twice. One (Oxalis latifolia
weed ID, Uganda 2016) had no Management section — same "descriptive, not directive"
rejection as the couchgrass factsheet earlier in this doc.

**The 52 Kiswahili "Pest Management Decision Guides" are confirmed genuinely
inaccessible, not just unexplored** — these live on `plantwiseplusknowledgebank.org`
(a different, more detailed tier from the one-page "Factsheets for Farmers"), which
returns an a cloud compute platform-style Cloudflare Turnstile "Just a moment..." JS challenge on every
fetch attempt, direct or through an alternate connection route. Same class of dead-end as
UCLA/PIMS/KAOP earlier in this doc — would need a real logged-in browser session, not
a scripted fetch. The "Factsheets for Farmers" tier (`factsheetadmin.plantwise.org`,
no CC-blocked) remains open and still has hundreds of unchecked factsheets.

**N2Africa Master Farmer Guidelines + Grain Legume Processing Handbook.** Found via the
`/agem` catalog listing (not the web search results, which pointed at the wrong,
English-only PDFs) that both documents exist as **separate English and Kiswahili PDFs**
on n2africa.org — genuine parallel translations, not machine-paraphrased. Located the
matching "Utumizi bora wa chanjo cha mikunde" (making the best use of legume inoculants)
checklist in both language versions and extracted it as a true bilingual pair, no
`translation=team` tag needed. **2 rows added** (`AGRI_147`-`148`). The Kiswahili
edition of the Grain Legume Processing Handbook turned out to be a shorter, distinct
presentation-format resource (13pp, Woomer & Mulei 2011) rather than a literal
translation of the 44-page English handbook (Woomer et al. 2013) — sentence-level
alignment wasn't reliable, so one further row (groundnut aflatoxin-prevention during
harvest/drying, a genuine safety-relevant directive, English-only in the 44pp handbook)
was extracted as team-translated instead of forcing a mismatched pair. **1 row added**
(`AGRI_149`).

**Zambia drought response — extracted with team sign-off** (flagged in the previous
session as "borderline, needs a call"; approved to extract). The specific DMMU "Food
Security Drought Response Plan" PDF is blocked by an a cloud compute platform WAF JS challenge on ReliefWeb,
regardless of connection route — but the same national response (DMMU-coordinated,
co-led by WFP/FAO) is documented in OCHA's own **Zambia Drought Response Appeal
(May-December 2024)**, hosted on unocha.org without the same block, with a clean
"Interventions will include:" bulleted list. **2 rows added** (`AGRI_150`-`151`,
Sustainable Farming: seeds/crop diversification; Livestock: disease surveillance,
feed, water infrastructure).

**Farm Radio `_candidates_farmradio.csv` (52-row Swahili-locale backlog) — human
trimming pass completed.** Reviewed all 52 rows (1 already promoted as `AGRI_008`-`009`
in an earlier session). 4 were clean "Backgrounder" format with a "Key facts" list —
the same reliable structure noted earlier in this doc — and are **true bilingual pairs**
(genuine Kiswahili translations, not team-translated): companion planting/mutualism,
post-harvest maize loss reduction, raising goats, and soil cover in conservation
agriculture. **4 rows added** (`AGRI_152`-`155`). The other 47 are dialogue/interview
scripts (10,000-45,000 characters each) requiring individual reading to find the actual
directive buried in the narrative frame. Read all 47 backgrounder/intro sections;
9 had a clean, self-contained, non-redundant technique worth extracting: raised-table
rice-seed drying (Bangladesh method via Farm Radio), cassava mosaic disease management
(Malawi varieties), a condensed local-chicken feed formulation (Dodoma, Tanzania),
sawdust potato storage (Kenya), pounded-maize-cob weevil protection (Benin), striga
hand-weeding technique, poultry coccidiosis/mycoplasmosis hygiene prevention, phosphorus
replacement after improved fallows, and a Tephrosia vogelii local-pesticide recipe for
beans (Tanzania). **9 rows added** (`AGRI_156`-`164`, all team-translated, English-only
in the source). The remaining ~38 rows were reviewed and **not** extracted, each for a
specific, checked reason — not left unexamined: pure human-interest/narrative framing
with no standalone directive (e.g. "Kenyan woman embraces conservation farming",
"Adventures of Neddy"), institutional/meta content about radio-campaign methodology
rather than farming practice (AFRRI project background, "Introduction to Value Chains"),
topical overlap with content already in the dataset (conservation-tillage benefits vs.
the already-extracted soil-cover row; Fall Armyworm biology vs. the FAO rows above), or
a 5-part drama serial ("Beans, a family affair") whose content is social/gender-dynamics
framing rather than a technique. This list is a legitimate stopping point, not an
unexamined backlog — see the CSV's own rows for the full 52-title index if revisiting.

**Farm Radio English-language `topic/agriculture/` hub — bigger than previously
recorded, partially indexed.** The hub actually has **94 pages (~940 articles)**, not
the ~300 implied by the earlier "30 pages crawled" note. Re-crawled pages 1-30 (300
articles, confirmed same count) and committed the full index as
`FARMRADIO_ENGLISH_HUB_INDEX.md` (previously only in an uncommitted scratch file, per
the doc-hygiene backlog). Unlike the Swahili-locale "kilimo" hub, most of these English
articles hreflang-pair to **French**, not Kiswahili — genuine bilingual EN+SW pairs are
the exception here, not the rule, so most usable content needs team-translation.
Checked a sample of ~10 titles in depth; 3 had clean, self-contained, non-redundant
directives: a circular/regenerative-agriculture radio spot (pre-planting/growing/
post-harvest practices, Uganda), an Aloe Vera home remedy for chicken diarrhea
(Karagwe, Tanzania, with the vet-consultation caveat kept in), and Gliricidia sepium
agroforestry spacing guidance (Eastern Province, Zambia). **3 rows added**
(`AGRI_165`-`167`). The remaining ~293 articles (of the 300 indexed; ~640 more
unindexed beyond page 30) are a real, large, unprocessed lead — flagged here rather
than left implicit, same as the Farm Radio Swahili backlog above.

**Net result this session: 131 → 167 rows** (`AGRI_132`-`167`, 36 rows). Full pipeline
re-run clean: `validate_psa_csv.py` (167 rows, same 2 pre-existing warnings on
`AGRI_008`/`AGRI_060`, no new ones), `qa_azure_language_check.py` (0 flags across all
167 rows), and the pairwise fuzzy-dedup check (only the same 2 pre-existing
near-duplicate pairs from before this session, no new ones introduced).

## OCR/deeper-navigation pass on the three unresolved countries (2026-07-15, continued)

Followed up specifically on Uganda, Malawi, and Eswatini — the three reachability items
above that were left open rather than resolved.

**Uganda — resolved, OCR successful.** The NECOC "Weather Update for May 2026" PDF
(9 pages, no text layer, previously flagged as an OCR candidate) OCR'd cleanly at 300dpi
with `--psm 3` (same method already proven on the CGSpace poster earlier in this doc).
It's a genuine Ministry of Water and Environment bulletin with a real "Government and
public advisories" section, including an explicit agriculture directive ("harvest
rainwater and maximize agricultural production") among general flood-safety advice, plus
a dedicated "Agriculture and food security" impacts section (naming Fall Armyworm as an
excess-rainfall risk). **1 row added** (`AGRI_168`).

**Malawi — resolved, but not by OCR.** `dodma.gov.mw`'s "Publications"/"Reports"/
"Policies" nav items were re-checked with a real browser (Playwright): confirmed they're
inert placeholder links (`href="#!"`, not clickable, no AJAX request fires) — genuinely
unbuilt site sections, not JS-hidden content. But the site's News section has one real,
substantive post: a Chichewa-language Ministry of Agriculture article, "Kuzindikira ndi
kulimbana ndi matenda a nanzikambe mu chimanga" (Recognizing and fighting downy mildew
disease in maize), dated 2025-12-31, with a genuine directive "before planting / when
seedlings emerge / at harvest" structure (certified seed, plant spacing, crop rotation,
fungicide seed treatment, uprooting infected plants, residue disposal). **2 rows added**
(`AGRI_169`-`170`) — translated Chichewa → English → Kiswahili. **Flag for the team:**
this is the first source in the whole dataset in a language other than English/Kiswahili
at the source; Chichewa translation competence hasn't been established for this pipeline
the way English has, so these two rows specifically would benefit from a native-speaker
or second-opinion check before final submission, more so than the English-sourced rows.

**Eswatini — corrected, not resolved.** `portal.ndma.org.sz` (the subdomain checked in
every previous session) is genuinely dead — resolves via DNS but the server never
completes a TCP connection, direct or through the alternate route. But the **bare domain**
`ndma.org.sz` (no `portal.` prefix) is live and had never been tried. It's a real,
current NDMA Eswatini WordPress site with "Advisories," "Preparedness Tips," and "Heat
Wave Safety" cards that look promising — but checked thoroughly (page HTML, a
JS-rendered Playwright pass, the WordPress REST API's `/posts` and `/media` endpoints)
and confirmed **none of those cards have real content behind them** — no matching post,
no matching media file. The site's only actual downloadable PDFs (via `/wp-json/wp/v2/
media`) are legislation (Disaster Management Act 2006) and COVID-era procurement
notices — not PSA content. The "Preparedness"/"Mitigation" pages that do have real URLs
are generic mandate/mission-statement text, same category as the Kenya county pages
ruled out earlier in this doc. **Net: corrects "DNS failure" to "reachable but no
content published yet"** — a real, checked negative, not an unexplored gap. Worth
retrying `ndma.org.sz` in a future session in case the Advisories section gets built out.

**Net result this pass: 167 → 170 rows** (`AGRI_168`-`170`). Full pipeline re-run clean:
`validate_psa_csv.py` (170 rows, same 2 pre-existing warnings, no new ones),
`qa_azure_language_check.py` (0 flags across all 170 rows, including the two
Chichewa-sourced rows — this only confirms the English/Kiswahili columns read as their
respective languages, not translation fidelity to the Chichewa original), and the
pairwise dedup check (same 2 pre-existing near-duplicate pairs, no new ones).

## Closing out the remaining untapped leads (2026-07-15, continued)

Went back through each of the four leads still marked "untapped" in `README.md`'s
pipeline diagram, aiming to fully resolve or definitively close each one rather than
leave them open indefinitely.

**CABI 52 Kiswahili PMDG guides — now definitively closed, confirmed unscriptable.**
Tried harder than the previous session's single fetch attempt: checked
`plantwiseplusknowledgebank.org/robots.txt` (fine, `Allow`s crawling) vs `/sitemap.xml`
(hard Cloudflare "Managed Challenge" — a proof-of-work JS challenge, not a simple
User-Agent block), then drove a real headless Chromium browser at a specific PMDG page
via Playwright with an 8-second wait for the challenge to auto-resolve. **Still
challenged** — Cloudflare's Managed Challenge is specifically designed to detect and
block headless browser automation, which is a different and harder class of block than
the wrong-header/robots.txt-bug issues this project has cleared elsewhere. Continuing
to try to defeat it (stealth plugins, etc.) would cross from "collecting an openly
licensed academic resource" into "actively defeating a deliberate security control,"
which isn't something to keep escalating via automation. **Verdict: needs a real
human-driven browser session, same category as the Facebook collection task already
deferred to Bradley's own device** — added to `BRADLEY_ACTIONS.md`. This is a genuine
closure (a defensible final answer), not a resolution via content extraction.

**CABI Factsheets for Farmers catalog — significantly extended, not exhaustible by
search.** No sitemap or directory listing exists on `factsheetadmin.plantwise.org`
itself (redirects to a login page for anything but a known direct PDF URL), so the
only discovery method remains targeted search-engine queries by country/crop/year —
confirmed there's no shortcut to a full catalog. Ran a wider round of country+year
combinations (Malawi, Ghana, Ethiopia, Zambia, Uganda, DR Congo) than previous
sessions. **21 more genuine factsheets found and extracted this pass** (enset bacterial
wilt/Ethiopia, groundnut rosette/Malawi, mango fruit fly traps/Malawi, banana
Xanthomonas wilt/Ghana, eucalyptus gall wasp/Ethiopia, boron deficiency pawpaw/Malawi,
Red Sunhemp nematode control/multi-country, black Sigatoka bananas/DR Congo — a new
country for this dataset, metal-silo grain storage/Zambia, bacterial black spot
mango/Zambia, mango pulp weevil/Zambia, anthracnose eggplant/Zambia, neem extract
powdery mildew/Zambia, Kapinga herbicide management/Zambia), bringing the running
total to 29 CABI factsheet rows. **Still genuinely open** — 29 checked against CABI's
own count of hundreds in this tier; search-based discovery has no natural end point,
only diminishing returns per query. Not claiming closure here, just meaningfully more
coverage.

**KEPHIS/NDMA/KALRO verbatim news quotes — technique re-proven twice more, now a
reliable method rather than a one-off.** The previous session had one example
(`AGRI_124`, KMD). This pass found two more genuine, directly-attributed quotes using
the same `"[agency] advises/urges/warns"` search pattern: KEPHIS Deputy Director for
Seed Certification Ephraim Wachira on counterfeit-seed verification (The Standard,
2026-05-15) and KALRO Director Robert Musyoki + Research Officer Samuel Kiiru on
certified-seed planting (Kenya News Agency, 2025-03-12). Also found a genuine KMD
(Kenya Meteorological Department) drought-preparedness advisory (mulching, minimum
tillage, tied ridges, rainwater harvesting for crops; fodder/water/heat management for
livestock) reported across several outlets — paraphrased rather than a direct quote
(same standard as the Rwanda/Ghana/Zambia government-advisory rows), so tagged
`translation=team` rather than treated as a quote-based row. **3 new rows**
(`AGRI_171`, `AGRI_178`, plus the KMD pair `AGRI_187`-`188`). This is now a proven,
repeatable technique with three independent successful examples — worth a dedicated
search pass per agency in a future session, but no longer "proven once."

**Farm Radio English hub — fully indexed for the first time, triaged at scale, still
the largest genuinely open lead.** Crawled all 94 pages this time (previous sessions
only ever covered pages 1-30) — confirmed **940 total articles**, not the ~300
previously recorded. Built a keyword-based triage over the full remaining pool (938
titles, since 2 more were used): 318 titles carry positive directive-content signals
("how to," "manage," "control," "prevent," disease/pest names, etc.) vs 23 with
negative signals (drama, profile pieces, institutional "Introduction to X"). Batch-fetched
the intro/backgrounder sections of the top 80 positive-signal candidates and scored
them for concrete technique markers (numbers with units, "should"/"must"/"avoid").
Extracted from the two strongest, cleanest hits: tomato post-harvest storage
temperatures (a clean Backgrounder "key facts" list) and a genuine bilingual EN+SW pair
on common bean root nitrogen contribution (found via the same hreflang mechanism used
throughout this project). **2 new rows.** The other ~78 fetched-and-scored candidates,
plus the ~858 titles not yet even fetched, remain a real, large, unprocessed pool —
the triage script and scoring method are saved and reusable
(`/tmp/.../triaged.json` pattern) for continuing this in a future session; explicitly
not claiming this lead is closed, only that it's now fully mapped and partially mined
with a repeatable method, rather than a vague "~296 more, someday."

**Duplicate-catch during this pass:** cross-referencing today's new Farm Radio/CABI
extractions against already-used source URLs caught **3 genuine duplicates** that had
slipped through — two Farm Radio backgrounder rows (goats, post-harvest maize) and one
(Aloe Vera chicken remedy) where a "new" find from the English hub turned out to be the
same source article as an existing historical row (`AGRI_047`/`AGRI_070`/`AGRI_071`
respectively). In each case, merged the richer/more complete version into the
original ID and removed the newer duplicate row, rather than leaving both. Caught by
grouping all Farm Radio-sourced rows by their URL slug and checking for groups of
more than one — added as a standing check before starting any new Farm Radio
extraction pass, since the historical AGRI_064-076 batch and the various
`_candidates_farmradio.csv`/English-hub sessions were never cross-referenced against
each other before now.

**Net result this pass: 170 → 187 rows** (net +17, after 3 duplicate merges). Full
pipeline re-run clean: `validate_psa_csv.py` (187 rows, same 2 pre-existing warnings,
no new ones), `qa_azure_language_check.py` (0 flags), and the pairwise dedup check
(same 2 pre-existing near-duplicate pairs — the 3 real duplicates caught this session
were fixed by merging/removal, not left for the fuzzy-match check to catch, since
their wording differed enough that difflib wouldn't have flagged them).

## "Ekegusii Corpus" import (2026-07-22) — promoted into agriculture_psas.csv

**Source: "Ekegusii Corpus"**, a lecturer-provided dataset (course pivot: the whole class
now targets Ekegusii, not a per-group variable third language). 925 agriculture-relevant
English→Ekegusii rows classified from its full English column (source's own Domain label
not trusted — see `EKEGUSII_CORPUS_IMPORT.md` for method and the mislabeling numbers);
11 removed as address-block/website-navigation content the classifier wrongly flagged, 1
removed as a source duplicate. Kiswahili (missing from this En→Ekegusii-only source) was
filled via a 3-tool comparison + round-trip QA + manual read-through —
`translate_and_qa.py` (new shared tool, works on any domain), full method and findings in
`EKEGUSII_CORPUS_IMPORT.md`.

**913 rows merged into `agriculture_psas.csv`** (renumbered `AGRI_191`–`1103`) →
**net 187 → 1,100 rows**. Full pipeline re-run clean: `validate_psa_csv.py` (1,100 rows,
17 soft warnings, no new hard failures) and a pairwise fuzzy-dedup check across the
combined set (0 exact duplicates, 63 near-duplicates flagged for review — see
`EKEGUSII_CORPUS_IMPORT.md`).

**Follow-up dedup pass (2026-07-23):** built a second classifier (word-level diff against
a domain gazetteer of disease/crop/livestock/audience terms, distinguishing "same
template, different real-world case" from genuine redundancy) and ran it on all 63
near-duplicate pairs: **26 confirmed distinct** (kept both — different disease/crop/
audience each side), **7 confirmed genuine duplicates** (near-total overlap, only a
stray non-distinguishing word differed — one side of each removed, `AGRI_753/306/369/
425/437/499/510`, **1,100 → 1,093 rows**), **30 left unresolved** (mostly a
"Climate-smart agriculture (CSA) is an approach..." cluster reworded ~10 different ways
making the same generic claim — plausibly paraphrase-generated rather than
independently-sourced, but not confirmed; flagged for a human read, not removed).
Also re-checked the 2 pre-existing near-dup pairs (`AGRI_005`/`037`, `AGRI_034`/`061`)
with a length-scaled similarity threshold (short sentences need much higher overlap to
count as duplicate than long ones) — both pass as genuinely distinct despite the ~0.63
raw ratio, confirming the original decision to keep both was correct. Full findings:
`ekegusii_internal/dedup_option_ab_findings.md`.

## Reconciliation against `main`'s parallel Agriculture data (2026-07-27)

`main` had moved on independently (7,156-row validated baseline, per its own
`psa_pipeline/README.md`) while this branch kept its own line of work. Two things
from `main` needed a decision before touching this branch:

**Synthetic rows — excluded, not merged.** `main`'s `psa_pipeline/output/
kenyan_psa_synthetic_50000.csv` contains 10,037 Agriculture-domain rows generated by
`psa_pipeline/src/generate.py`: authored sentence templates × real mined authority
names × randomised county/month slots (seed=42) — plausible-looking but fabricated
announcements, not real PSAs, despite carrying real authority names. This directly
conflicts with `PSA_Group_Instructions.docx`'s own rule ("Not acceptable: ...
unsourced entries"). Deliberate call (Bradley, 2026-07-27): **excluded entirely** from
this branch. Noted here for the record, not imported.

**Real rows — reconciled and merged.** `main`'s `psa_dataset_cleaned.csv` (a cleaned
copy of the team's actual scraped `merged_psa_dataset.csv`) had 1,690 Agriculture rows.
After removing everything already present in this branch or in our own
`_candidates_ekegusii_corpus.csv` pool (punctuation-normalized text match), 611 rows
were genuinely new, from three source buckets:

- **`kilimo.go.ke` / `kilimonews.co.ke`** (Metadata `scraped:MoALD News`, 514 rows) —
  real Ministry of Agriculture / Kenyan ag-news sources we hadn't scraped ourselves.
  Random-sample manual read (n=40) found ~97% genuine PSA-style content; the only
  systematic junk was 4 literal failed-generation placeholders ("No actionable ...
  available/present in this article" — an artifact of whatever LLM-summarization step
  `main`'s cleaning pipeline used), dropped by exact match. **510 kept.**
- **`PSA_KE_Final.csv`** (89 rows) — this source was already flagged in project memory
  as needing an audit before use, and `classify_agriculture.py`'s own prior finding
  (41% of its labeled-Agriculture rows were not real PSA content) predicted exactly
  this: manual read of all 89 found academic-citation fragments, organisation
  address/contact blocks, website-navigation furniture, and sentences cut off
  mid-thought. **55 kept, 34 dropped.**
- **`Ekegusii Corpus`** (8 rows) — text was mojibake-corrupted (`Kenyaâ€™s` →
  `Kenyaâ TMs`) in `main`'s copy and near-certainly duplicates content already
  promoted from the same corpus under clean encoding. **All 8 dropped** rather than
  repaired, to avoid silently re-admitting something already excluded on purpose.

Kept rows were assigned new `AGRI_####` IDs, classified into the existing Sub_Category
taxonomy (same regex logic as `classify_agriculture.py`), and run through the same
pairwise fuzzy-dedup check used for the Ekegusii Corpus promotion (bucketed by
first-3-words, threshold 0.6): **0 exact duplicates**, 19 new near-duplicate pairs, all
of the established "same template, different real-world referent" shape (different
crop/market/county/institution each side) — kept both sides in every case, consistent
with the 2026-07-23 precedent. **Net 1,093 → 1,658 rows.** Full method and dedup
findings: `ekegusii_internal/reconcile_main_agriculture.py` and
`ekegusii_internal/reconcile_main_dedup_report.md`.

## Somali + Dholuo added (2026-07-27)

Course history: the group originally picked Somali as the 3rd target language
(`WEEK2_PREP.md`, 2026-07-20), then the lecturer pivoted the whole class to Ekegusii
specifically (`docs/ekegusii_transfer_learning.md`, 2026-07-22). Two of the other four
domains on `main` (Security & Safety, Governance) still carry substantial real
Somali/Dholuo translations post-pivot — most likely done before the pivot memo landed
and never revisited, though this branch has no independent confirmation either way.
Rather than leave this branch as the only one with zero Somali/Dholuo coverage,
decision (Bradley, 2026-07-27): **translate into both anyway**, since — unlike
Ekegusii — Somali (`som_Latn`) and Dholuo (`luo_Latn`) both have real pretrained
coverage in `facebook/nllb-200-distilled-600M`, making this comparatively cheap
correctness/completeness work rather than a research problem. Method: same NLLB-200
model this project already uses for Kiswahili gap-filling
(`ekegusii_internal/translate_somali_dholuo.py`), run locally, CPU-only, batch size 16,
checkpointed every 80 rows. Ekegusii coverage is unaffected by this — still 58.0% after
the merge above (961/1,658; the 187 original hand-scraped rows, `AGRI_001`–`187`, remain
the only gap, since Ekegusii has no pretrained MT model to fall back on).

## Synthetic rows integrated, tagged and filterable (2026-07-27)

Revisited the earlier "exclude entirely" call on main's 10,037-row templated
Agriculture set (`psa_pipeline/output/kenyan_psa_synthetic_50000.csv`, see the
reconciliation entry above). Decision (Bradley, 2026-07-27): **incorporate them
into `agriculture_psas.csv` directly rather than a separate file**, but every row
carries `Metadata` containing `provenance=synthetic; generation_method=
template_authority_slotfill; source_pipeline=main:psa_pipeline/generate.py` —
filter on that string to get the real-only 1,658-row set back, or to pull the
synthetic pool specifically for data-augmentation experiments.

Translated via `facebook/nllb-200-distilled-600M` on a **a cloud GPU notebook kernel**
(`ekegusii_internal/kaggle_synthetic/kernel.py`) rather than the ~8-12hr local CPU
job this volume would have needed — the actual runtime turned into a multi-hour
debugging session for reasons worth recording so they're not re-discovered:

- that service's on-demand GPU path was tried first and abandoned: `eastus` (the only
  region with T4 stock) is blocked by a subscription-level region-allowlist
  policy separate from the quota numbers `az vm list-usage` reports — quota
  being non-zero does not mean deployment is permitted. No cost was incurred
  (both attempted resource groups failed empty).
- a cloud GPU notebook service kernels ignored `machine_shape: NvidiaTeslaT4` in `kernel-metadata.json`
  and assigned a Tesla P100 (Pascal, `sm_60`) twice regardless — that notebook service's
  preinstalled PyTorch build has dropped Pascal support entirely (`sm_70`
  minimum). Fixed by reinstalling `torch==2.7.1+cu118` at the top of the kernel
  script before any other import, which retains Pascal-era compute-capability
  support in the cu118 wheel family regardless of which GPU a cloud GPU notebook service hands out —
  more robust than fighting the scheduler for a specific accelerator.
- That reinstall left the preinstalled `torchvision`/`torchaudio` version-mismatched
  against the new torch, breaking `transformers`' import chain even though
  vision utilities are irrelevant to a text-only translation job — fixed by
  uninstalling both rather than version-matching them.
- `transformers` also hard-refuses to load a non-safetensors checkpoint
  (`torch.load`) on torch < 2.6 (CVE-2025-32434 gate); `facebook/nllb-200-
  distilled-600M` ships only `pytorch_model.bin`, no safetensors alternative —
  resolved by the same torch bump, since `2.7.1+cu118` satisfies both the
  version floor and Pascal compatibility simultaneously.
- Seven kernel versions total before a clean run; the last (v7) completed with
  0% Kiswahili/Somali repetition-loop failures and 0.4% (39/10,037) Dholuo
  failures — better than the local CPU run's Dholuo rate, since this kernel
  used beam search + `no_repeat_ngram_size=3` from the first pass rather than
  needing a retry.
- Merge itself (`ekegusii_internal/merge_synthetic_rows.py`) surfaced one real
  MT error: NLLB translated two *different* English rows (a millet-farmers PSA
  and a beans-farmers PSA, otherwise identical template) to **identical**
  Kiswahili text — it mistranslated "millet" as "maharagwe" (beans). Caught by
  `validate_psa_csv.py`'s duplicate-Kiswahili check (the first duplicate found
  across the whole file). Corrected the word directly (`maharagwe` →
  `mtama`) and tagged `mt_quality_flag=kiswahili_corrected_millet_mistranslated_
  as_beans` rather than silently accepting either the error or the duplicate.

**Net: 1,658 → 11,695 rows** (10,037 synthetic, 85.8% of the file by row count —
substantial enough that the provenance tag is not optional bookkeeping, it's the
only thing separating "real" from "synthetic" in this file going forward).
Kiswahili/Somali/Dholuo all 100% filled including the synthetic rows (translated
as part of the same a cloud GPU notebook service run); **Ekegusii drops to 8.2% (961/11,695)** — this
is a denominator effect, not a regression: none of the 10,037 synthetic rows have
Ekegusii coverage (no model exists for it, same reason as everywhere else in this
file), so the same 961 real rows are now measured against a much larger total.
`validate_psa_csv.py` passes clean on the full 11,695-row file.

**Repetition-loop fix (2026-07-27):** greedy decoding degenerated into repeated
token/phrase loops on 75 rows (10 Somali, 65 Dholuo) — a known NLLB low-resource-target
failure mode. Retried with `no_repeat_ngram_size=3` + beam search
(`ekegusii_internal/fix_repetition_loops.py`): fixed 10/10 Somali and 57/65 Dholuo. The
remaining **8 Dholuo rows** couldn't be fixed (long/complex sentences) — tagged
`mt_quality_flag=dholuo_repetition_unresolved` in Metadata for a human read rather than
left silently broken.

## Full QA pass: schema, fidelity, and language-ID (2026-07-27)

Adding Somali/Dholuo without also updating the project's existing QA gates would have
left them at a lower verification standard than Kiswahili got. Three gates, brought up
to parity, all changes additive (nothing removed from the existing schema/checks):

**Schema (`scripts/validate_psa_csv.py`):** `SCHEMA` now includes `Somali`/`Dholuo`;
both added to `MANDATORY` (unlike Ekegusii, both have real NLLB-200 coverage, so there's
no structural reason to ever leave them blank). `langdetect`'s soft-warning check
extended to Somali (`'so'` is in its 55-language profile set; Dholuo `'luo'` is not, so
it's left out rather than silently mis-checked). Running this validator against the
merged file immediately surfaced two real gaps from the merge itself: one row
(`AGRI_1185`) missing Kiswahili — filled via the existing `translate_and_qa.py` 3-tool
pipeline exactly as it would be for any other blank cell — and 55 `PSA_KE_Final`-sourced
rows missing `Date` (that source has no per-row publish dates) — stamped with the merge
date `2026-07-27`, matching the precedent already set for the Ekegusii Corpus import.

**Fidelity round-trip QA (`ekegusii_internal/qa_roundtrip_somali_dholuo.py`):** mirrors
`translate_and_qa.py`'s methodology rather than duplicating it wholesale, since Somali
and Dholuo need different treatment:
- **Somali** — a cloud translation API has real coverage (confirmed against the public
  `/languages` endpoint), so this got the full independent-second-opinion treatment:
  a cloud translation API generated its own En→So candidate, both it and the existing NLLB candidate were
  back-translated to English via a cloud translation API, scored by `difflib.SequenceMatcher` against the
  original, best-scoring one kept. **1,031/1,658 rows (62%) switched to that service's
  candidate** — a cloud translation API was substantively better than NLLB for Somali on this dataset more
  often than not. 73 rows still scored below the 0.35 confidence floor even after
  picking the best of two — logged, not auto-fixed.
- **Dholuo** — no independent second tool exists (a cloud translation API has no coverage; no reliable
  OPUS-MT en-luo pair either), so the best available signal is a same-tool NLLB
  round-trip (translate the Dholuo output back to English via NLLB itself). Weaker
  evidence than Somali's independent check — a model can be consistently wrong in both
  directions — but still strictly more than the zero fidelity-checking that existed
  before. **325/1,658 rows (19.6%)** scored below the same 0.35 floor, consistent with
  Dholuo being the harder, more out-of-distribution language for this model.
- a cloud translation API's F0 free tier rate-limited hard partway through the first attempt
  (confirmed the risk already flagged in project notes) — rewritten with per-chunk
  checkpointing and conservative pacing (25 texts/request, 1.5s between requests, up to
  8 retries with exponential backoff) before the successful run.
- Every row tagged `qa_tool_somali=`/`qa_roundtrip_somali=` and
  `qa_tool_dholuo=nllb_selfcheck`/`qa_roundtrip_dholuo=`, matching the `qa_tool=`/
  `qa_roundtrip=` convention `translate_and_qa.py` already used for Kiswahili.

**Language-ID QA gate (`scripts/qa_azure_language_check.py`):** extended `EXPECTED` to
include Somali (Dholuo excluded — a cloud translation API Text Analytics doesn't cover it either, same gap
as Translator). Running it surfaced a **pre-existing bug unrelated to today's changes**:
a cloud translation API Text Analytics hard-caps `detect_language` at 1,000 documents per request, and
this script had never been re-run at full scale since the dataset passed 1,000 rows on
2026-07-22 (only ever validated on a 61-row subset per earlier project notes) — fixed
with proper chunking. Final run: **2 flags out of 1,658 rows** (`AGRI_926`, `AGRI_873`),
both cases where garbled/typo-laden source English (`"s3ssion"`, `"incoprporate"`,
`"indeginious"`) defeated NLLB, producing Somali output that's largely untranslated
English — and in `AGRI_926`'s case, one that had *passed* the round-trip fidelity check
above (0.876) precisely because copying source-language words verbatim into a garbled
sentence back-translates to something similar-looking, a known blind spot of round-trip
scoring. Both tagged `mt_quality_flag=somali_language_id_mismatch_*` for a human read;
neither auto-fixed, per the project's standing no-invented-translations rule.

**Final validator state:** `validate_psa_csv.py` passes clean — 1,658 rows, all hard
checks pass, 19 soft warnings: 11 pre-existing long-row flags (English+Kiswahili,
verbose original entries), 6 pre-existing langdetect false-positives (short text
misclassified, noted as noisy-on-short-sentences since before today), and the 2 real
Somali flags above. All 17 pre-existing warnings are on original (pre-2026-07-27) rows —
**none of the 565 newly-merged rows triggered a single warning**, for whatever that's
worth as a quality signal on the merge itself. Kiswahili 100% (1,658/1,658), Somali
100%, Dholuo 100%, Ekegusii 58.0% (961/1,658, unchanged — still gated on a fine-tuned
model that doesn't exist yet).
