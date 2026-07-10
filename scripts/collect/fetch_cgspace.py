"""Download PDFs from CGSpace (CGIAR repository) by bitstream UUID and extract text.

CGSpace hosts bilingual (English + Kiswahili) farmer-advisory posters and factsheets
from CCAFS / AICCRA / IITA / Alliance-Bioversity-CIAT. Many are true parallel pairs
(same poster in each language) — good, PSA-shaped agricultural material.

IMPORTANT constraints discovered 2026-07-10:
  - CGSpace BLOCKS datacenter IPs entirely — you must route via a residential exit
    (set FETCH_PROXY, e.g. the KE tunnel).
  - Even then it RATE-LIMITS aggressively (HTTP 429). Keep delays long (30-60 s
    between files) or just download manually from a browser for small numbers.
  - The working URL form is the API content endpoint:
      https://cgspace.cgiar.org/server/api/core/bitstreams/<UUID>/content
    The /bitstreams/<UUID>/download and hdl.handle.net forms 404'd for us.
  - Certificate chain is incomplete for the proxied path → verify_tls=False.

Most of the Kiswahili agricultural material on CGSpace is TANZANIA-focused (CCAFS
East Africa worked heavily in Babati, Tanzania). See SOURCES.md "Findings log".

Usage:
    python scripts/collect/fetch_cgspace.py <bitstream_uuid> [<uuid2> ...]
Prints extracted text per UUID. Pair EN+SW UUIDs of the same poster to build rows.
"""

import sys
import time
import random

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fetchlib import fetch_url  # noqa: E402

import fitz  # noqa: E402

API = "https://cgspace.cgiar.org/server/api/core/bitstreams/{}/content"
POLITE_DELAY = (30, 60)  # seconds between files — CGSpace 429s if you go faster


def fetch_text(uuid: str) -> str:
    pdf = fetch_url(API.format(uuid), use_cache=True, verify_tls=False)
    doc = fitz.open(stream=pdf, filetype="pdf")
    return "\n".join(p.get_text() for p in doc)


def main(uuids):
    for i, uuid in enumerate(uuids):
        if i:
            time.sleep(random.uniform(*POLITE_DELAY))
        try:
            txt = fetch_text(uuid)
            print(f"\n===== {uuid} — {len(txt)} chars =====")
            print(txt[:2000])
        except Exception as e:
            print(f"\n===== {uuid} — FAILED: {type(e).__name__}: {str(e)[:120]}")
            print("     (CGSpace 429/refused — retry later with longer delay, "
                  "or download from a browser)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/collect/fetch_cgspace.py <bitstream_uuid> ...")
    main(sys.argv[1:])
