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

## Kiswahili extension items (need English twins matched — mostly Tanzania)

Download from the item page; then search CGSpace for the English equivalent by title.
- Utunzaji wa rutuba ya udongo katika halmashauri ya wilaya ya Babati — item `58c3e488-59b5-42fe-90dd-c5d82c0ff1a4`
- Kilimo bora cha Alizeti (sunflower): Kitabu cha Mkulima Kiongozi na Afisa Ugani — item `58024fc5-f088-4177-a7fd-623b6229748e`
- Mwongozo wa kufundishia kilimo bora cha mpunga (rice) — item `3d7f680c-6f45-47c2-a49b-6d5680abf5b7`
- Usindikaji wa muhogo baada ya kuvuna (cassava) — item `84b3f3c6-4fc1-4696-8fa9-550b1d50bb3f`
- Kilimo bora cha maharage (beans): Kitabu cha Mkulima Kiongozi na Afisa Ugani — item `9ba21694-a609-4a77-9410-1b0e8f48378c`

Item page pattern: `https://cgspace.cgiar.org/items/<UUID>`

## Browse for more (enumerate later)

- CGSpace discover API (works via WebFetch / residential exit):
  `https://cgspace.cgiar.org/server/api/discover/search/objects?query=<terms>&size=20`
  Useful queries: `ushauri wa kilimo hali ya hewa`, `kilimo bora`, `mkulima kiongozi`,
  `advisory Kenya kiswahili`.
- Filter tip: CCAFS / AICCRA / IITA collections hold most of the bilingual farmer material.
