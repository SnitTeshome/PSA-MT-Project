"""
dedup.py
--------
Step 4 of the pipeline.

Two passes:
  1. EXACT dedup -- normalise whitespace/case and drop identical rows.
     (generate.py already avoids exact repeats within a sub-category via
     its own "seen" set, so this pass mainly guards against duplicates
     that could occur across sub-categories.)

  2. NEAR-duplicate dedup -- catches rows that are near-identical in
     wording (e.g. the same template + vocab word happening to read
     almost the same way twice). Blocked by (Domain, Sub-Category) so
     the comparison is fast and, importantly, so that legitimate
     county/month/authority variation of the SAME underlying PSA is
     NOT treated as a duplicate -- that variation is realistic (real
     Kenyan PSA campaigns really do repeat the same message county by
     county), so it is intentionally preserved.

     Similarity is computed with rapidfuzz's vectorised cdist
     (token_sort_ratio) within each (Domain, Sub-Category) block, and a
     row is dropped only if it is >= NEAR_DUP_THRESHOLD similar to a
     row already kept -- a conservative bar so real diversity survives.
"""

import json
import re

import numpy as np
from rapidfuzz import fuzz, process

import config

NEAR_DUP_THRESHOLD = 99  # very conservative: county/month/authority swaps are
# legitimate distinct PSAs (a real campaign repeated per county is realistic),
# not duplicates -- only near-character-identical collisions are dropped here


def normalize(text: str) -> str:
    t = text.lower().strip()
    return re.sub(r"\s+", " ", t)


def dedup_exact(rows: list) -> list:
    seen = set()
    out = []
    for r in rows:
        key = normalize(r["English"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def dedup_near_within_block(block_rows: list) -> list:
    if len(block_rows) <= 1:
        return block_rows

    texts = [r["English"] for r in block_rows]
    sim_matrix = process.cdist(texts, texts, scorer=fuzz.token_sort_ratio)

    keep_mask = np.ones(len(texts), dtype=bool)
    for i in range(len(texts)):
        if not keep_mask[i]:
            continue
        too_similar = sim_matrix[i, i + 1 :] >= NEAR_DUP_THRESHOLD
        keep_mask[i + 1 :][too_similar] = False

    return [r for r, keep in zip(block_rows, keep_mask) if keep]


def dedup_near(rows: list) -> list:
    blocks = {}
    for r in rows:
        key = (r["Domain"], r.get("_subcategory", ""))
        blocks.setdefault(key, []).append(r)

    kept = []
    for key, block_rows in blocks.items():
        kept.extend(dedup_near_within_block(block_rows))
    return kept


def main():
    raw_path = config.DATA_DIR / "generated_raw.json"
    rows = json.loads(raw_path.read_text())
    print(f"Loaded {len(rows)} generated rows")

    rows = dedup_exact(rows)
    print(f"After exact dedup: {len(rows)}")

    rows = dedup_near(rows)
    print(f"After near-duplicate dedup (threshold={NEAR_DUP_THRESHOLD}): {len(rows)}")

    out_path = config.DATA_DIR / "deduped.json"
    out_path.write_text(json.dumps(rows, indent=2))
    print(f"Wrote deduped rows -> {out_path}")


if __name__ == "__main__":
    main()
