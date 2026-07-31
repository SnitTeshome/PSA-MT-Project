# Week 4 performance summary — Swahili & Dholuo

Compiled 2026-07-30. Covers the Week 4 "Evaluation" deliverable for Kiswahili
and Dholuo end to end: a genuine multi-backend comparison before committing to
a translation approach (same rigor `docs/week3_performance_summary.md` applied
to Ekegusii), a deliberate decision to **not** use a teammate's existing
Kiswahili submission once a systematic error was found in it, and the full
15,000-row production translation for both languages. The final combined
dataset (`data/processed/kenyan_psa_15000_final.csv`) is done and committed —
see §8 for exact counts.

**Superseded (2026-07-31):** `kenyan_psa_15000_final.csv` has since been folded
into and replaced by `data/processed/kenyan_psa_multilingual_dataset.csv` (now
29,609 rows, Somali added, real-source rows appended, honest Provenance
labels throughout) and removed from the repo — that's the canonical file now.
The counts and analysis below describe the dataset as it existed at this
milestone; kept as-is for the historical record rather than rewritten.

**Headline, up front, for anyone skimming**: Kiswahili was re-translated from
scratch (a cloud translation API, with an automatic NLLB-200 fallback partway through
— see §6) rather than patched from the teammate's (Snit Teshome's) original
submission. This was a **quality decision, not a dismissal of that work** — the
original was a real, good-faith, mostly-accurate contribution; the specific,
concrete reason it wasn't used as the base is in §1.

## 1. Kiswahili: the teammate-submission decision (read this before the numbers)

A teammate (Snit Teshome) pushed a complete Kiswahili translation of all 15,000
rows to `origin/main`@`14513f4` (`psa_pipeline/output/psa_translated_kiswahili_
15000.csv`, column `English_sw`). This was **real, good-faith work** — worth
saying plainly, since the rest of this section explains why it isn't the base
of the final dataset. Re-verified independently this session (not just taken on
faith from an earlier session's note):

- **PSA_ID match: 15,000/15,000 exact**, zero duplicates, zero blank cells.
- **Manual QA read**: 15 rows (3 per domain, all 5 domains) read by eye. Fluent,
  grammatically correct, faithful to numbers/dates/county names/institution
  acronyms (AFA, KTDA, TVET, CDC, KEMSA, KEMRI, DPP, NDMA) in every row but one
  recurring issue: **"Office of the Auditor-General" is mistranslated as "Ofisi
  ya Mhariri Mkuu"** (literally "Office of the Editor-in-Chief") in **181 of the
  200 rows** that mention it (9 rows instead use the closer "Mkurugenzi Mkuu wa
  Ukaguzi"). This is Governance-domain only, one specific institution name — the
  rest of the translation, everywhere this session looked, was accurate.

**First-pass decision (superseded)**: initially this session decided to PASS
the teammate's file with the error flagged rather than silently corrected (see
the now-superseded merge, `psa_pipeline/output/kenyan_psa_ekegusii_kiswahili_
15000_merged.csv`, kept for the record, not used downstream). Reasoning at the
time: the error was narrow (1.2% of rows, one institution name) and easy to
flag rather than fix by guessing.

**Final decision (this is what shipped): re-translate all 15,000 rows via
a cloud translation API instead, and do not use the teammate's file at all.** This
was a deliberate call, made explicitly, not a quiet swap:
- The Week 4 backend comparison (§3 below) already had a clear, independently-
  verified answer for Kiswahili: **a cloud translation API scored chrF 80.7** on a
  160-row, 5-domain benchmark — the best of every backend tested (NLLB 67.7,
  general-purpose LLM backends 33.7–39.8).
- Patching one found error on top of a submission whose overall production
  method is undocumented (`Kiswahili_tool` would have had to be
  `unknown_teammate` — no commit message or metadata records how it was made)
  is a weaker foundation than a translation this project can fully account for
  end to end, tool and QA both, especially once a real, systematic error had
  already turned up in a 15-row spot-check.
- **This is not a comment on the quality of the original effort or an
  overreaction to one bug** — it reflects that a higher-quality, fully-
  traceable alternative was directly available and already validated, and the
  team's own comparison made picking it a mechanical, evidence-based call
  rather than a judgment call about the teammate's work.

See §6 for exactly how the production re-translation was run (a cloud translation API primary,
automatic NLLB-200 fallback partway through) and §8 for final counts.

## 2. Cross-domain comparison benchmark

`data/splits/agriculture/{kiswahili,dholuo}_test.csv` (142 rows) is **Agriculture-
domain only** — this project already documented, for Ekegusii, that a mechanism
validated on Agriculture alone (chrF 45–55) can drop sharply elsewhere (chrF
26–31) on manual retest (`docs/week3_performance_summary.md`). To avoid
repeating that mistake, the deciding comparison here uses a new benchmark built
from `psa_pipeline/data/clean_real_with_quality_labels.csv` (7,156-row real
corpus, all 5 domains): **160 rows per language**, stratified proportionally to
each language's own available-data domain shares (Kiswahili and Dholuo have very
different fill patterns — Dholuo is thin in Health/Agriculture, ~4% each, vs.
Kiswahili's ~12/29%), excluding rows tagged `quality_status=NOT_INCLUDED_IN_
VALIDATION_PASS`. Script: `scripts/build_crossdomain_benchmark.py`. Output:
`data/splits/crossdomain/{kiswahili,dholuo}_benchmark.csv`.

| Domain | Kiswahili benchmark | Dholuo benchmark |
|---|---|---|
| Agriculture | 47 | 6 |
| Security & Safety | 41 | 59 |
| Governance | 28 | 48 |
| Education | 25 | 40 |
| Health | 19 | 7 |

**Provenance caveat, carried forward and re-confirmed, not just assumed**: the
Kiswahili gold in this corpus is majority (3,869/4,029 filled rows, 96%)
genuinely team-collected bilingual pairs, not machine-translated — trustworthy-
ish gold. The Dholuo gold has **no `qa_tool` Metadata tag of any kind** (0/2,404
rows) — unlike the agriculture-only split's Dholuo column, which is at least
tagged `qa_tool_dholuo=nllb_selfcheck` (NLLB grading its own output). Here the
provenance is simply undocumented, not self-graded — still treated as "current
best guess," not verified gold, per the same caution, just a different root
cause.

## 3. Backend comparison — Kiswahili

| Backend | n | chrF | Degenerate | Notes |
|---|---|---|---|---|
| **a cloud translation API** (dedicated NMT) | 160 | **80.7** | 1/160* | Best by a wide margin. *False positive — English proper-noun span correctly left untranslated. |
| **NLLB-200-distilled-600M** (local CPU, free) | 160 | 67.7 | 1/160* | *False positive, same pattern as that service's. |
| Open LLM, remote GPU (A100-class), dict-prompted | 24 | 39.8 | 1/24 | Genuine repetition-loop degenerate on 1 row (see below). |
| Open LLM, remote GPU (A100-class), no dict | 24 | 38.7 | 1/24 | Same genuine degenerate row. |
| Open LLM, remote GPU (L4-class, smaller), no dict | 24 | 34.0 | 0/24 | |
| Open LLM, remote GPU (L4-class, smaller), with dict | 24 | 33.7 | 0/24 | Dictionary made no real difference at this scale. |

Sample size note: the two LLM backends were tested on a bounded n=24 subset (not
the full 160) — same reasoning as Dholuo's bounded sample (§4): Qwen2.5 has no
official Swahili/Dholuo support, so this was a bounded exploratory test, not
the deciding comparison. NLLB/a cloud translation API numbers are on the full 160.

**Manual read** (NLLB, one row per domain):
- Governance: EN "IEBC directs voters who registered before 2012 to enrol
  afresh" → NLLB "IEBC inawaamuru wapiga kura waliojiandikisha kabla ya mwaka
  2012 wajiandikishe tena" — fluent, faithful.
- Health, Security, Agriculture, Education: same pattern — close paraphrases of
  gold, correct entities/numbers, no invented content. One flagged "degenerate"
  row (`SEC_0065`) was a **false positive**: the source sentence itself
  contains an English proper title ("Child-Friendly Technology-Aided Interview
  Room") that NLLB correctly left untranslated — the automatic degeneracy check
  can't distinguish "correctly preserved English proper noun" from "failed to
  translate," a limitation to note, not a real model failure.

**Manual read** (open LLM, remote GPU, no dict): grammatically plausible-looking
Kiswahili that is **semantically drifting** in ways NLLB/a cloud translation API are not — e.g.
"IEBC directs voters who registered before 2012 to enrol afresh" became "IEBC
hukumbusha wachezaji ambao wameandaa kabla ya 2012 kujiandaa tena" ("IEBC
reminds **players** who **prepared**..." — "wachezaji" = players/actors, not
voters; the core meaning is wrong even though the Swahili itself is fluent). One
row degenerated into a multi-thousand-character repetition loop of garbled
Cyrillic-like characters — a genuine, severe failure mode NLLB/a cloud translation API did not
exhibit anywhere in 160 rows each.

## 4. Backend comparison — Dholuo

| Backend | n | chrF | Degenerate | Notes |
|---|---|---|---|---|
| **NLLB-200-distilled-600M** (local CPU, free) | 160 | **53.7** | 4/160* | Best by far. *All 4 are false positives — see below. |
| a cloud translation API | — | **not supported** | — | Confirmed via the live `/languages` API (not docs): 138 languages listed, no `luo` code, no name/native-name match for Dholuo/Luo. |
| Open LLM, remote GPU (A100-class), with dict | 10 | 23.0 | 1/10 | Dictionary halved the degenerate rate vs. no-dict. |
| Open LLM, remote GPU (L4-class), with dict | 10 | 20.1 | 1/10 | |
| Open LLM, remote GPU (L4-class), no dict | 10 | 16.6 | 2/10 | |
| Open LLM, remote GPU (A100-class), no dict | 10 | 16.0 | 4/10 | Worst; most repetition loops. |

Sample size note: **deliberately small (n=10), by design, not an oversight.**
Qwen2.5's own technical report lists ~29 officially-supported languages —
neither Swahili nor Dholuo is among them (unlike NLLB, which is purpose-built
for both, per Meta's own NLLB-200/FLORES-200 documentation). This is a
fundamentally different situation from the Ekegusii comparison, where the LLM
was competing against **no trained model at all**; here it competes against
NLLB, which genuinely was trained on this exact language. Per "targeted, not
wasteful experimentation," Dholuo got a quick sanity check, not an extended
prompt-engineering campaign, once the result was unambiguous (see below).

**Manual read (NLLB)**: genuinely tracks meaning across all 5 domains, e.g. EN
"Build better schools! Support infrastructure projects in ASAL regions." → NLLB
"Gero skunde mabeyo! Siro tije mag gedo e gwenge mag ASAL." — near-identical to
gold bar synonym choice. All 4 automatically-flagged "degenerate" rows were
manually confirmed as **false positives**, and are themselves an honest finding
about the benchmark, not about NLLB: two rows' "English" source column is
actually code-switched Kiswahili/Sheng slang, not English at all (e.g. "Lock
SIM yako kwa *something#! Usiache mtu atumie line yako kufanya maovu.") — NLLB
correctly left it near-unchanged since there was no real English to translate;
one row's English source itself contains garbled repeated text from the
original scrape ("Cabinet Cabinet Secretary for Mining Secretary for Mining");
one is a correctly-preserved English document title.

**Manual read (open LLM, remote GPU, no dict)**: **incoherent** — not merely
lower-quality but frequently not recognizable as Dholuo at all. Concrete
examples: "mar ariyo mar ariyo mar ariyo..." repeated ~20 times; "maro maro
maro..." repeated ~20 times; "maduong' maduong'..." repeated ~15 times; one row
drifted into broken **Kiswahili** instead of Dholuo entirely. This is the
"quick sanity check, stop if incoherent" scenario flagged in advance — found
exactly that, so no further prompt-engineering iteration was spent chasing it.

**Manual read (open LLM, remote GPU, with dict)**: fewer catastrophic repetition
loops, more varied vocabulary, but still not reliably correct or fluent Dholuo
— e.g. "Kwan mar gik mibiro jorit chik mar pin joburay konyruokgo..." trails
back into a repetition loop by the end of the same sentence. The dictionary
measurably reduces (not eliminates) degeneracy and lifts chrF, but doesn't
close anywhere near the gap to NLLB.

## 5. Dictionary sourcing (for the dict-prompted ablation)

Per the explicit ask to match the depth already invested in Ekegusii's
95,418-word dictionary, not settle for the first easy scrape. Full detail and
what was ruled out: `NLP/Project/language_dictionaries_internal/psa_mt_week4_
glossaries/README.md` (private folder, outside this repo — dictionary resources
never go in the shared team repo, matching this project's existing convention
for the Ekegusii/Kalenjin dictionaries).

- **Kiswahili**: combined 2 real sources — the *English-Kiswahili-Kalenjin Nouns
  Pocket Dictionary* (Toweett, 1979, KNLS vtabu paid access, already fetched in
  a prior session for Kalenjin work; its EN↔SW column is real dictionary data,
  2,100 usable entries) + the Peace Corps Kenya *Kiswahili Competency Based
  Manual*'s glossary appendix (public domain, 163 entries). **2,213 unique
  entries** combined.
- **Dholuo**: Asenath Bole Odaga's **English-Dholuo Dictionary** (Lake
  Publishers & Enterprises, 1997) — a real, professionally published dictionary
  found freely available (no paid access needed) on the Internet Archive,
  OCR-text-parsed into **6,664 structured entries**. Confirmed decent coverage
  of PSA-relevant vocabulary (health, drought, hospital, law, vote, election,
  school, cattle, farm, medicine all present). A smaller supplementary find (the
  Tiba Foundation's clinical/greetings phrasebook, 118 entries) was set aside in
  favor of Odaga's much larger, headword-organized dictionary.
- **Checked and ruled out** (see the README for detail on each): `Kalebu/kamusi`
  (Swahili-monolingual, not bilingual), MUSE ground-truth dictionaries (Swahili
  not covered, host now 403s), `word2word` pip package (neither `sw` nor `luo`
  in its 3,564 supported pairs), FreeDict (no `eng-swa`), and the Rechenbach
  *Swahili-English Dictionary* (found on Internet Archive, real and large, but
  its OCR text has two-column-layout interleaving that made reliable automated
  parsing impractical within the time budget — noted as a real find, not
  pursued further).
- **KNLS vtabu catalog** (paid subscription, same account as the Ekegusii
  fetch): logged in successfully (confirmed active subscription), searched the
  live catalog for "Dholuo" and "Kiswahili dictionary" — **0 relevant results**
  either way. Not pursued further per the explicit time-boxing instruction.

## 6. Production run — Kiswahili (a cloud translation API primary, NLLB-200 automatic fallback)

The a cloud translation API resource backing this project is an **F0-tier subscription with a
hard 2,000,000-character-per-month cap** (permanent, not a per-request
throttle) — verified independently before running anything at this scale, not
assumed. Translating all 15,000 rows needs roughly **1.85M input characters,
~93% of the entire monthly cap**, and some of that cap was already spent by
this session's own comparison-stage testing (the 160-row benchmark, earlier
`qa_azure_language_check.py` runs, etc.) — a real risk of running out mid-job,
not a hypothetical one.

**Plan, and what actually happened**: rather than precompute a budget and stop
early, `scripts/translate_kiswahili_azure_bulk.py` calls a cloud translation API for real and
reacts to the actual API response — it keeps going until a cloud translation API itself signals
it can't continue (persistent 429 that doesn't clear after patient exponential
backoff, or any other non-200/429 status), at which point it stops calling
a cloud translation API entirely and routes every remaining untranslated row to NLLB-200 instead
(this project's established best free/open Kiswahili alternative, chrF 67.7 —
not Qwen, which already lost decisively in §3). Every row's `Kiswahili_tool`
is tagged `azure_translator` or `nllb_200` individually — nothing is blended
silently. The NLLB-200 fallback runs on the same remote-GPU-hosted app used
for the Dholuo bulk job (§7), not local CPU, since it was already deployed.

**Real outcome**: a cloud translation API did run out partway through, confirming the quota risk
was real, not overcautious. Final split across all 15,000 rows:

| `Kiswahili_tool` | Rows | Share |
|---|---|---|
| `azure_translator` | 10,330 | 68.9% |
| `nllb_200` | 4,670 | 31.1% |

`Kiswahili_review_flag`: 0/15,000 flagged degenerate by the automated check —
a spot-check of both azure_translator and nllb_200 rows across several domains
found fluent, faithful output in every sample read (see the samples logged
during this run; consistent with both backends' comparison-stage numbers in
§3). Output: `psa_pipeline/output/kenyan_psa_kiswahili_azure_15000_translated
.csv`, checkpointed per-chunk throughout (`.kiswahili_azure_checkpoint.json`)
so the mid-run quota cutoff cost zero progress.

## 7. Production run — Dholuo (NLLB-200 on remote GPU)

NLLB-200-distilled-600M was the unambiguous winner in §4 (chrF 53.7 vs. 16–23
for the general-purpose LLM backends; a cloud translation API has no Dholuo support at all).
Run on a remote GPU purely for speed/reliability over the local-CPU path
already proven in the comparison stage — same model, same decoding config
(beam=4, `no_repeat_ngram_size=3`), not a different backend decision. a remote GPU platform was
used (not a remote GPU platform) since a deploy+spawn app was already live and proven
this session for the comparison stage's GPU testing — reusing that pattern was
more straightforward than standing up a second platform.

`scripts/translate_dholuo_nllb_bulk.py` chunked all 15,000 rows (2,000/chunk)
through the deployed app, checkpointing after every chunk. **Result: 15,000/
15,000 rows translated, zero missing.** `Dholuo_tool` = `nllb_200_distilled_
600m` for all 15,000 rows (no fallback needed — NLLB-200 was already the
primary and only backend used for Dholuo). `Dholuo_review_flag`: 65/15,000
(0.43%) flagged degenerate by the automated check; a manual read of a few
found the same false-positive pattern already documented in §4 (e.g. "Ministry
of Health - Reproductive Health Unit" correctly left untranslated as an
institution name, tripping the English-copy-through heuristic) rather than new
genuine failures — consistent with, not a departure from, the comparison
stage's findings. Output: `psa_pipeline/output/kenyan_psa_dholuo_nllb_15000_
translated.csv`.

## 8. Final combined dataset

`data/processed/kenyan_psa_15000_final.csv` — built by `scripts/
build_final_combined_dataset.py`, which independently re-verifies (not just
assumes) that the Kiswahili and Dholuo production files agree on every shared
column (`Domain`, `English`, `Ekegusii`, `Ekegusii_tool`) before merging, and
asserts zero nulls after the join.

- **15,000 rows, 12 columns**: `PSA_ID, Domain, English, Ekegusii, Ekegusii_
  tool, Ekegusii_review_flag, Kiswahili, Kiswahili_tool, Kiswahili_review_flag,
  Dholuo, Dholuo_tool, Dholuo_review_flag`.
- **Zero nulls** in every column except the three `*_review_flag` columns,
  where null means "nothing flagged" by design (same convention as the
  original Ekegusii column): `Ekegusii_review_flag` 8,138 null / 6,861
  `unvalidated_prior_gemini` / 1 `degenerate`; `Kiswahili_review_flag` 15,000
  null (nothing flagged); `Dholuo_review_flag` 14,935 null / 65 `degenerate`.
- Tool splits: `Ekegusii_tool` — gemini 6,861 / qwen2.5_72b_instruct_awq 6,720 /
  llama3_70b_instruct 1,419 (unchanged, prior session). `Kiswahili_tool` —
  azure_translator 10,330 / nllb_200 4,670 (§6). `Dholuo_tool` —
  nllb_200_distilled_600m 15,000 (§7).

## 9. Content-type check against the PSA framework (post-commit finding)

After the final dataset (§8) was committed, the user shared a 4-step PSA-vs-
Press-Release-vs-Other-Government-Communication classification framework
(`NLP/Project/PSA FRAMEWORK.pdf`, one level up from this repo — private outer
workspace, not part of this shared repo). Its Step 1/2 keyword heuristics were
run against `English` in the committed `data/processed/kenyan_psa_15000_final
.csv` and **independently reproduced here** (not just taken on the coordinator's
word), with a manual spot-check of the matched rows before trusting the
heuristic:

```python
PSA_KEYWORD_RE = r"\b(advise[sd]?|urge[sd]?|warn(s|ed)?|remind[s]?|all Kenyans are requested|public is hereby informed|deadline|alert)\b"
PRESS_KEYWORD_RE = r"\b(launch(ed|es)?|inaugurat(ed|es)|announc(ed|es)|statement by the Cabinet Secretary|official visit|media invited)\b"
LEGAL_KEYWORD_RE = r"\b(Gazette Notice|pursuant to|tender No\.?)\b"
```

- **PSA-style keyword rows: 8,397/15,000 (56%).**
- **Press-release keyword rows with NO PSA keyword: 1,496/15,000 (10%)** —
  reads as a Press Release per the framework's own Step 1 Q2 (describes an
  event/launch/announcement, not an instruction to the public), not a genuine
  PSA. By domain: Education 457, Governance 422, Health 319, Agriculture 154,
  Security & Safety 144.
- **0 rows** hit legal/administrative keywords (Gazette Notice, pursuant to,
  tender No.) — no contamination from that category.
- **5,107 rows (34%)** hit no keyword either way — ambiguous, not necessarily
  wrong, left untouched.

**Manual spot-check** (15 rows, 3 per domain, of the 1,496 flagged):
confirmed every sampled row genuinely reads as an event/program announcement,
not a PSA imperative — e.g. *"Ministry of Health - Reproductive Health Unit
launches a November awareness campaign on diabetes screening across Garissa
County"* and *"COMESA announces a free anthrax vaccination exercise for pigs
in Trans Nzoia County this April"* describe an org doing something, not the
public being told to do something. Looks like a template-generation artifact
from the synthetic-row generator (`psa_pipeline/src/templates.py`), not a
scraping error, given the domain concentration and phrasing consistency.

**This connects to a gap the team's own Week 1 report already flagged as
incomplete**: relevance filtering (PSA vs. non-PSA) was left "in progress" —
624 rows flagged by an LLM classifier, only 54 manually reviewed (see
`week_1_report.md`). This keyword check is an independent, larger-scale signal
on that same underlying gap, not a new problem.

**Decision (user's call): flag, don't exclude.** The Ekegusii/Kiswahili/Dholuo
translation work already done for these 1,496 rows isn't thrown away — a new
`Content_Type_Flag` column (`press_release_style` / blank) makes the framework-
mismatch visible in the dataset instead of leaving it silently implied as
fully validated. This is a **dataset-level content-type signal, separate from**
the per-language `*_review_flag` columns (those are translation QA; this is
"does this row's English even read as a PSA").

**Open**: the 5,107 ambiguous (no-keyword) rows and the framework's Steps 3-4
(beyond the Step 1/2 keyword heuristic reproduced here) haven't been applied —
a fuller relevance-filtering pass against the whole framework is still future
work, same as the Week 1 report's original "in progress" note.

## 10. What's proven vs. what's still open

**Proven**:
- NLLB-200-distilled-600M is a strong, free, local, purpose-built baseline for
  **both** languages here — a fundamentally different situation from Ekegusii,
  where it had zero coverage. chrF 67.7 (Kiswahili) / 53.7 (Dholuo) on a genuine
  5-domain benchmark, with every automatically-flagged "degenerate" row
  manually confirmed as a false positive (benchmark-data artifact, not a model
  failure) in both languages.
- a cloud translation API is meaningfully better than NLLB for Kiswahili specifically
  (chrF 80.7) but has **no Dholuo support at all** — confirmed via the live API,
  not assumed from docs.
- A general-purpose open LLM (not officially trained on either language) is
  clearly the weaker choice for both — chrF 33.7–39.8 (Kiswahili), 16.0–23.0
  (Dholuo) — and for Dholuo specifically produces frequently-incoherent output
  regardless of model scale (72B vs. 32B) tested here.
- Dictionary-prompting (the mechanism that won for Ekegusii) gives a real but
  modest improvement for the open LLM on Dholuo (fewer repetition loops, +4–7
  chrF) and essentially no improvement for Kiswahili — consistent with the
  hypothesis that dictionary-prompting helps most when it's substituting for a
  model's total lack of any training exposure (Ekegusii), and helps much less
  when the real gap is the model's underlying pretraining coverage (here).
- **Both bulk production runs are done.** Kiswahili: 15,000/15,000 via a cloud translation API
  Translator + automatic NLLB-200 fallback once that service's monthly quota ran out
  partway through (§6). Dholuo: 15,000/15,000 via NLLB-200 on remote GPU (§7).
  The final combined dataset is written and committed (§8).
- **The teammate's existing Kiswahili submission was NOT used as the
  production base**, despite being real, good-faith, mostly-accurate work —
  once the systematic Auditor-General→Editor-in-Chief error was found (181/200
  relevant rows) on top of an undocumented production method, the team's own
  independently-verified comparison (a cloud translation API chrF 80.7) gave a clear, fully-
  traceable alternative, so it was re-translated from scratch instead of
  patched. See §1 for the full reasoning, stated plainly rather than left
  implicit in a diff.
- The a cloud translation API F0 tier's 2M-character/month cap was a real, not hypothetical,
  constraint — it was hit mid-job (§6), and the a cloud translation API/NLLB-200 fallback split
  (68.9% / 31.1%) is now transparently recorded per-row via `Kiswahili_tool`,
  not blended silently.

**Open / explicitly deferred, not silently skipped**:
- **1,496/15,000 rows (10%) read as Press Releases, not genuine PSAs**, per an
  independent content-type keyword check against the user-shared PSA
  classification framework (§9) — flagged via `Content_Type_Flag`, not
  excluded (their translation work stays). This is the same relevance-
  filtering gap the Week 1 report already called "in progress," now with a
  concrete, larger-scale, reproduced number attached to it. The 5,107
  ambiguous rows and the framework's Steps 3-4 remain unapplied.
- The Auditor-General mistranslation issue is now **moot for the production
  dataset** (the file it applied to was superseded, not patched) but the
  observation itself — a specific commercially-important governance term this
  teammate's method got wrong most of the time — could still be worth passing
  back to them as feedback on whatever tool/process they used, separate from
  this project's own data.
- The Rechenbach Swahili-English Dictionary (real, large, found on Internet
  Archive) was not parsed due to OCR/layout difficulty — a genuine follow-up if
  a richer Kiswahili dictionary is wanted later (e.g. for a future fine-tuning
  pass).
- **Local, fully-offline model (no cloud/remote-compute dependency) was ruled
  out, not attempted**, for the comparison stage: this container's cgroup
  memory was at 7.77/9.66 GB (only ~1.9 GB headroom) when checked, below what
  a ~4.5–5.5 GB quantized 7B GGUF model plus runtime overhead needs. Noted as
  ruled-out-by-constraint, not silently skipped. (The production runs used
  remote GPU/a cloud translation API instead, per §6-7, so this didn't block the actual bulk
  translation.)
- The 65 automatically-flagged "degenerate" Dholuo rows and the Kiswahili
  spot-checks are believed to be the same false-positive pattern documented in
  §3-4 (institution names/titles correctly left untranslated), but this was a
  sample check, not a full 15,000-row manual read — a genuine larger QA pass
  is future work, not claimed as done here.

## 11. Addendum — in-domain vs. cross-domain sanity check (NLLB)

Run as a secondary data point per the brief: NLLB on the *original*
Agriculture-only 142-row splits (`data/splits/agriculture/{kiswahili,
dholuo}_test.csv`) vs. the same model's cross-domain 160-row result above.

| Language | Agriculture-only (n=142) | Cross-domain, 5 domains (n=160) | Delta |
|---|---|---|---|
| Kiswahili | 66.7 | 67.7 | +1.0 (flat) |
| Dholuo | 64.8 | 53.7 | **-11.1** |

**Finding**: Kiswahili shows no real domain-narrowness effect — NLLB performs
about the same whether tested in-domain or across all 5 domains, consistent
with it being a genuinely general-purpose, well-covered language for this
model. **Dholuo shows the same domain-narrowness pattern already documented for
Ekegusii** — meaningfully better in-domain (Agriculture) than across the full
domain mix, a real (if smaller-magnitude) version of the same effect. This is
a point in favor of not over-trusting even NLLB's Dholuo quality uniformly
across all 5 domains without a domain-aware read — worth keeping in mind if/
when the full bulk run is authorized.
