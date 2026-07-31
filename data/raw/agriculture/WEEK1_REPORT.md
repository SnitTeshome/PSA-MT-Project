# Week 1 Report — Agriculture Domain

Submitted for: Week 1 (Data Collection & Curation), DSA4020A Semester Project.
Covers the Agriculture domain only (this contributor's assigned domain within the
5-domain team split: Education, Health, Security, Agriculture, Governance).

## 1. Dataset summary statistics

| Metric | Value |
|---|---|
| Rows (validated PSAs) | 187 |
| English sentences (approx., punctuation-split) | 232 |
| Kiswahili sentences (approx., punctuation-split) | 235 |
| English vocabulary (unique whitespace tokens) | 2,127 |
| Kiswahili vocabulary (unique whitespace tokens) | 2,073 |
| English length (words) | min 6, median 33, mean 33.1, max 97 |
| Kiswahili length (words) | min 8, median 35, mean 36.3, max 82 |
| Genuine bilingual source pairs | 27 (14.4%) |
| Team-translated (one language sourced, other translated in-house) | 160 (85.6%) |
| Non-English/Kiswahili-original rows | 2 (Chichewa, Malawi source — flagged for native-speaker check) |
| Hard validation failures | 0 |
| a cloud translation API Text Analytics language-QA flags | 0 |

Sub-category distribution:

| Sub-category | Rows |
|---|---|
| Crop Production | 109 |
| Livestock | 39 |
| Sustainable Farming | 31 |
| Agribusiness | 8 |

Pipeline: every row passed `validate_psa_csv.py` (schema/structure) →
`qa_azure_language_check.py` (a cloud translation API-confidence-scored language ID on both columns) →
a pairwise `difflib` near-duplicate check, in that order, with zero exceptions.

## 2. Sample entries

**AGRI_001** (Crop Production, genuine source pair):
> EN: "African marigold (Tagetes erecta) – mbangimwitu. Use against: bacteria, fungi,
> nematodes, insects... Preparation: crush 100-200g of the leaves, roots or flowers,
> pour on..."
> SW: "African marigold / Mbangimwitu (Tagetes erecta). Inazuia: bacteria, fungi,
> nematodes, wadudu... Kutayarisha: ponda gramu 100-200 ya matawi, mizizi na maua;
> mwaga..."
> Source: Infonet-Biovision, TOF Magazine Issue 17 (EN+SW original pair)

**AGRI_004** (Sustainable Farming, team-translated):
> EN: "Promote drought-tolerant and early-maturing crop varieties to enhance
> resilience to climate variability."
> SW: "Kuza matumizi ya aina za mbegu zinazostahimili ukame na zinazokomaa mapema ili
> kuongeza uwezo wa kukabiliana na mabadiliko ya hali ya hewa."
> Source: NDMA Baringo County Drought Early Warning Bulletin, May 2026

**AGRI_005** (Livestock, team-translated):
> EN: "Strengthen livestock disease surveillance, vaccination, and treatment
> programmes to prevent disease outbreaks."
> SW: "Imarisha ufuatiliaji wa magonjwa ya mifugo, chanjo, na mipango ya matibabu ili
> kuzuia mlipuko wa magonjwa."
> Source: NDMA Baringo County Drought Early Warning Bulletin, May 2026

**AGRI_033** (Agribusiness, team-translated):
> EN: "Encourage mindset change among farmers to stock more of their harvest and sell
> less."
> SW: "Himiza mabadiliko ya mtazamo miongoni mwa wakulima ili wahifadhi sehemu kubwa
> ya mavuno yao na kuuza kidogo."
> Source: NDMA Tharaka-Nithi County Drought Early Warning Bulletin, May 2026

Every row above is quoted verbatim from `agriculture_psas.csv`; full provenance for
each (exact URL, retrieval date, licensing note) is in `SOURCES.md`.

## 3. Challenges faced

### 3.1 Coverage: 1 of 5 domains complete, well under the sentence target

The brief's Week 1 success criterion is **≥5,000 parallel sentences team-wide**. With
5 assigned domains, an even split implies a rough working target of **~1,000
sentences per domain** — not an official sub-target the team has agreed on, but a
reasonable planning yardstick given no domain weighting has been discussed. Against
that yardstick:

- **Domains with committed data: 1 of 5 (20%)** — checked `origin/data/health` and
  `origin/data/security` directly; both have zero rows committed. Education and
  Governance don't have branches yet. Agriculture is currently the team's entire
  dataset.
- **Agriculture reached 232 English sentences against the ~1,000 yardstick — 23.2%
  of the per-domain target, 4.6% of the full 5,000-sentence team target.**

This is the headline number for Week 1: not that the pipeline or process failed (0
hard validation failures, 0 QA flags, all rows independently verified against a real
source), but that **volume is far short of where the brief expects the team to be**,
and currently only one team member's domain has any data to show for it at all.

### 3.2 Storage cost vs. dataset yield

To make the shortfall concrete rather than just citing a row count, here is what it
actually cost in raw material to produce the 187 validated rows:

| | Size |
|---|---|
| Raw source material downloaded/cached to search for usable content | **~771 MB** (751 MB of manually-fetched magazine back-issue archives — TOF Magazine + Mkulima Mbunifu — plus 6.6 MB of confirmed-pair PDFs/scripts, and 14 MB of cached automated fetches across ~356 files from government, NGO, and repository sources) |
| Validated deliverable produced from it | **148 KB** (`agriculture_psas.csv`, 187 rows) |
| **Yield ratio** | **0.019%** by size — roughly **3.3 MB of raw material scanned per usable English sentence**, or **4.1 MB per usable row** |

This is the real bottleneck, and it is a storage/throughput problem as much as a
time problem: producing each additional validated PSA pair requires scanning
megabytes of source material that mostly gets rejected — because it's news framing
rather than a directive, unsourced, a duplicate, off-topic, or (for magazine
archives) simply doesn't mention agriculture at all on that page. The 771 MB already
processed is not a small effort — it represents two full magazine back-catalogs
narrow-lexicon-scanned end to end, ~356 individually cached fetches, and the Farm
Radio English hub (940 articles across 94 pages) fully indexed — and it returned 187
rows.

### 3.3 What reaching 1,000 sentences would actually take

Extrapolating the current yield rate linearly: reaching the ~1,000-sentence
per-domain yardstick (currently at 232) would require roughly **4.3× the raw
material already processed — about 3.25 GB**, versus the 771 MB processed so far.

That linear projection is optimistic, though, and probably understates the real
cost. The yield rate is not constant — it degrades as the cheapest, highest-density
sources get exhausted:

- The easiest source (Farm Radio's hand-paired bilingual scripts) is already fully
  mined: 13 of 52 candidate pairs promoted, nothing left there.
- The next-easiest source (Farm Radio's English hub, 940 articles) is only
  spot-checked so far (~10 of 940) — the remaining ~858 are a real lead but each one
  needs individual triage, not bulk extraction.
- Several large sources are **closed off entirely**, not just harder: CABI's 52
  Kiswahili "Pest Management Decision Guides" are Cloudflare-Turnstile-blocked (even
  headless-browser automation gets stuck on the proof-of-work challenge); Facebook
  county Pages need a real logged-in human session (automated fetches hang
  indefinitely or are robots.txt-disallowed); CGSpace rate-limits/blocks datacenter
  IPs outright on two specific bilingual PDFs still needed.
- The remaining ~29-of-hundreds CABI Plantwise factsheets checked and the
  Africa-wide government bulletin approach (10 countries mined so far via OCHA) are
  both still-open leads, but each additional country or agency is a fresh
  reconnaissance pass, not a repeat of a known-good pattern.

So the realistic cost curve to close the gap is **worse than linear** — each
additional 1,000 raw-material MB likely returns fewer usable sentences than the
last, not the same 3.3 MB/sentence rate, because what's left is disproportionately
the hard-to-reach material (blocked, requires a human session, or requires
per-item manual verification rather than pattern-matched bulk extraction).

### 3.4 Source scarcity and incompleteness (structural, not just effort)

Beyond volume, the sources themselves are structurally limited for this task:

- **True bilingual EN+SW source pairs are rare** — only 14.4% of collected rows are
  genuine source pairs; the other 85.6% required team translation because no
  Kiswahili-published twin existed, which is itself a finding about how little
  bilingual Kenyan agricultural PSA content is publicly available in the first
  place.
- **The one available large supplementary resource is schema-incompatible and
  noisy**: the class lab dataset `PSA_KE_Final.csv` (2,903 rows, lecturer-approved
  as a complementary lead source) has no Source or Date column at all, and a
  structural audit found **~41% of its Agriculture rows are scrape fragments or
  citations, not real PSAs** — it can only be used as an individually-verified lead
  generator, not a bulk supplement, which sharply limits how much it can close the
  gap.
- **Directive content itself is scarce relative to news/research content** about
  agriculture — most government and NGO material found during collection was
  reporting or technical guidance, not short actionable public advisories; the
  "news ≠ PSA" filter that keeps dataset quality high is the same filter that keeps
  volume low.
- **One source turned out to be in a fourth language** (Chichewa, from a Malawi
  government article) — a reminder that even "Africa-wide" scope surfaces content
  outside the two working languages, adding a verification step (native-speaker
  check) rather than a straightforward row.

### 3.5 Recommendation

Raise the domain-completion and volume gap with the team and Dr. Ombui before Week 2
begins: either the other four domains need to start collecting in parallel with
Week 2 prep work, or the team-wide target/timeline needs revisiting given the
measured yield rate above. The agriculture domain's pipeline and quality bar are
solid and reusable as-is for the other domains (`scripts/collect/fetchlib.py`,
`validate_psa_csv.py`, `qa_azure_language_check.py` are all domain-agnostic already)
— the gap is in raw source coverage and elapsed effort, not tooling.
