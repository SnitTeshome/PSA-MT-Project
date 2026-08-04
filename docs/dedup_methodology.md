# Deduplication methodology — Option A vs. Option B

## Option B (semantic diff + domain gazetteer), run on 63 near-duplicate pairs

Word-level diff between two similar sentences, checking whether the differing words
include a domain-distinguishing term (disease/pest, crop, livestock,
audience/demographic — a curated gazetteer, not exhaustive); falls back to a
high-overlap check (≥0.9 character ratio with no gazetteer hit → still likely
duplicate), else UNCLEAR.

**Result on the 63 pairs: 26 DISTINCT · 30 UNCLEAR · 7 LIKELY_DUPLICATE**

- **DISTINCT (26)** — confirmed same-template-different-referent (e.g. drought vs.
  pest outbreak, banana vs. sweet potato intercropping, cattle/goat/sheep variants).
  Keep both, no action needed.
- **LIKELY_DUPLICATE (7)** — near-total overlap (ratio 0.90-0.975) with only a stray
  non-distinguishing word differing (a dropped qualifier, a placeholder vs. a real
  name, an identical article opener repeated). These read as genuine redundancy, not
  template variation.
- **UNCLEAR (30)** — meaningful wording differs but no gazetteer term catches it
  (mostly a "Climate-smart agriculture (CSA) is an approach..." cluster, ~10 rows,
  each reworded differently but making the same generic claim — plausibly
  paraphrase-generated rather than independently authored, but a word-diff tool
  can't confirm that alone; needs a human read or a semantic/embedding check).

## Option A (length-scaled threshold), run on 2 pairs flagged earlier

Two pairs, already documented as tolerated "generic boilerplate" and never removed.

Threshold formula tested: `threshold(n) = min(0.95, 1 - 0.4 * min(1, n/30))` (rises
toward ~0.95 for short sentences, relaxes toward a 0.6 baseline at 30+ words).

| Pair | Avg length | Actual ratio | Length-scaled threshold | Verdict |
|---|---|---|---|---|
| Pair 1 | 12 words | 0.632 | 0.840 | **PASS — distinct enough given length** |
| Pair 2 | 10 words | 0.627 | 0.873 | **PASS — distinct enough given length** |

Both pairs fall well below the length-scaled bar — confirms a flat 0.6 threshold
over-triggers on short text exactly as predicted, and validates the original
judgment call (keep both, treat as boilerplate overlap) as correct. Option B run on
the same 2 pairs independently comes back UNCLEAR (the differing words are
action/intervention vocabulary, not disease/crop/animal/audience nouns, so they
aren't in the gazetteer) — Option A and B don't contradict each other here, they just
see different angles of the same evidence: no data change needed for these 2.

## Historical exclusion check

Scanned every commit touching the agriculture domain's raw CSV (10 commits, full
history) for removed English-text rows, not just the two known flagged pairs above.
Found exactly one removal event in the entire history: 3 rows were removed, but on
inspection these were **enrichment replacements under the same PSA ID** (richer, more
complete text replacing a thinner original), not genuinely distinct content that got
discarded. Nothing recoverable found — there is no history of real content being
excluded as a false-positive duplicate.

## Bottom line

- 7 pairs look like genuine duplicates worth removing (one side of each) — a human
  call, not auto-applied.
- 30 pairs are unresolved — the CSA-definition cluster in particular is worth a human
  read, since it's plausibly synthetic/paraphrased content rather than independently
  authored PSAs.
- 26 pairs are confirmed fine as-is.
- The 2 pre-existing flagged pairs are confirmed correctly kept — no change, nothing
  to recover from history.

No dataset file was modified by this analysis pass — it's a findings report, not an
applied fix.
