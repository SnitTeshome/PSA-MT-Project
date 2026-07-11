# CGSpace (CGIAR) bilingual advisory — fetch list

CGIAR farmer-advisory posters/factsheets, CC-licensed, PSA-shaped. Access notes:
- CGSpace **blocks datacenter IPs** and **429-rate-limits** the residential exit → easiest to
  **download the PDFs from a browser** on the item pages below. For scripted use,
  `scripts/collect/fetch_cgspace.py <bitstream_uuid>` via a residential exit with long delays.
- Most of this material is **Tanzania-focused** (CCAFS/IITA East Africa) — see the Tanzania
  acceptability caveat in SOURCES.md.

## Confirmed English + Kiswahili parallel pair (verified 2026-07-10)

| Lang | Title | Item page | PDF bitstream UUID |
|---|---|---|---|
| SW | Kilimo kinachohimili mabadiliko ya tabianchi: maamuzi kumi muhimu… | https://cgspace.cgiar.org/items/c4d42102-1c9b-4936-b17b-7e2173964cda | 94c0db78-3fb6-4c8a-90d6-7dc22387e201 |
| EN | Climate smart agriculture: top ten decisions to make with weather info | https://cgspace.cgiar.org/items/62fd7239-9d39-4528-a513-5fb949251490 | 287a1fb1-170c-4359-9bfc-41b7954ac505 |

Script-fetch (via residential exit):
`python scripts/collect/fetch_cgspace.py 94c0db78-3fb6-4c8a-90d6-7dc22387e201 287a1fb1-170c-4359-9bfc-41b7954ac505`

## Kiswahili extension items — resolved 2026-07-12

Searched CGSpace's discover API (`/server/api/discover/search/objects?query=...`, works
fine over plain WebFetch even though direct/proxied fetches of the item pages 429) for an
English twin of each. Result: **one has a genuine EN twin, the other four are Swahili-original
extension handbooks with no English counterpart on CGSpace at all** — don't keep treating
those four as "needs matching," they're monolingual by nature, not an unfinished search.

**Now a confirmed pair** (moved to `farmradio_manual/confirmed_pairs/` 2026-07-12):
- SW: Utunzaji wa rutuba ya udongo katika halmashauri ya wilaya ya Babati — item
  `58c3e488-59b5-42fe-90dd-c5d82c0ff1a4`, bitstream `4ff8daa4-34bd-41af-9182-a0be12894492`
- EN: "Soil fertility management in Babati: A practical guide on good agricultural
  management practices in smallholder farming systems" (Kihara, Bolo & Kinyua, 2019) — item
  `ffcd4004-0069-422a-a1da-93cb4370f47c` (handle `10568/107779`), bitstream
  `a8785e00-01cc-43ca-ae3b-9914fb532925`. License on this one specifically is "Open Access
  (Other usage rights)", not explicit CC-BY-4.0 like the four below — check before reuse
  beyond class work.
- PDF bytes not yet downloaded (CGSpace 429'd both the initial discover-API call and a
  retry ~25 min later, via the KE tunnel) — download both bitstream URLs
  (`https://cgspace.cgiar.org/server/api/core/bitstreams/<uuid>/content`) from a browser.

**Confirmed Swahili-original, no English twin exists** (monolingual — useful as
domain-vocabulary background material, not a PSA pair; all CC-BY-4.0, all IITA/Tanzania):
- Kilimo bora cha Alizeti (sunflower): Kitabu cha Mkulima Kiongozi na Afisa Ugani — item
  `58024fc5-f088-4177-a7fd-623b6229748e`, bitstream `4c4f5768-bf6d-494e-bc82-52132cb411ee`
  (Nov 2023)
- Mwongozo wa kufundishia kilimo bora cha mpunga (rice) — item
  `3d7f680c-6f45-47c2-a49b-6d5680abf5b7`, bitstream `2a8234c4-7390-4bd8-b134-fa90022a41bb`
  (Oct 2020)
- Usindikaji wa muhogo baada ya kuvuna (cassava) — item
  `84b3f3c6-4fc1-4696-8fa9-550b1d50bb3f`, bitstream `31167634-f972-4e39-ba51-2ff13b530d32`
  (Nov 2023)
- Kilimo bora cha maharage (beans): Kitabu cha Mkulima Kiongozi na Afisa Ugani — item
  `9ba21694-a609-4a77-9410-1b0e8f48378c`, bitstream `01664273-0a10-4b51-a776-7b9ab8a51aac`
  (Nov 2023)

Item page pattern: `https://cgspace.cgiar.org/items/<UUID>`. Bitstream UUIDs above were read
off each item's own page via WebFetch (not the rate-limited discover API), so no further
API calls are needed to act on this list — go straight to browser download.

## Browse for more (enumerate later)

- CGSpace discover API (works via WebFetch / residential exit):
  `https://cgspace.cgiar.org/server/api/discover/search/objects?query=<terms>&size=20`
  Useful queries: `ushauri wa kilimo hali ya hewa`, `kilimo bora`, `mkulima kiongozi`,
  `advisory Kenya kiswahili`.
- Filter tip: CCAFS / AICCRA / IITA collections hold most of the bilingual farmer material.
