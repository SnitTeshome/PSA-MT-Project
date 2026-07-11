"""Fetch TOF Magazine (English) / Mkulima Mbunifu (Swahili) issues from Infonet-Biovision.

Infonet-biovision.org (Drupal, CC-licensed content, robots.txt allows these paths)
hosts the full back-issue archive of both magazines as one PDF-per-node pages:

  - TOF Magazine (English), index:            https://infonet-biovision.org/tof_magazine_issue
  - Mkulima Mbunifu (Swahili sister mag),
    index:                                    https://infonet-biovision.org/mkm_magazine_issue

Each issue page embeds its PDF as:
  <div class="field field--name-field-document ..."><div class='pdf-reader'>
    <object data="https://infonet-biovision.org/sites/default/files/pdf/<name>.pdf" ...>

IMPORTANT (recorded 2026-07-12): TOF and Mkulima Mbunifu are sister publications,
NOT translations of each other issue-by-issue — do not treat "same issue number" as
a parallel pair. The ONE confirmed genuine English+Swahili pair found in the whole
~230-issue TOF archive is the "plant extract special" (Sept/Oct 2006):
  - EN: tof-issue-no-17-septoct-2006-plant-extract-special-english-version
  - SW: tof-issue-no-17-septoct-2006-plant-extract-special-swahili-version
Everything else in these archives is monolingual background/context material, useful
for domain vocabulary but NOT directly PSA-pair-ready without manual topic-matching.

Usage:
    python fetch_infonet_magazines.py --list tof          # print all TOF slugs
    python fetch_infonet_magazines.py --list mkm          # print all MKM slugs
    python fetch_infonet_magazines.py <slug> [<slug2> ...]  # download by slug
"""

import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fetchlib import fetch_url  # noqa: E402

BASE = "https://infonet-biovision.org"
INDEX_URLS = {
    "tof": f"{BASE}/tof_magazine_issue",
    "mkm": f"{BASE}/mkm_magazine_issue",
}
PDF_RE = re.compile(r'data=\s*"(https://infonet-biovision\.org/sites/default/files/[^"#]+\.pdf)')
SLUG_RE = re.compile(r'href="(/[a-z0-9-]*(?:tof-issue-no-|mkulima-mbunifu-no-)[a-z0-9-]*)"')


def list_slugs(archive: str) -> list:
    html = fetch_url(INDEX_URLS[archive]).decode("utf-8", errors="replace")
    slugs = sorted({m.lstrip("/") for m in SLUG_RE.findall(html)})
    return slugs


def fetch_issue(slug: str, outdir: str) -> str:
    page = fetch_url(f"{BASE}/{slug}").decode("utf-8", errors="replace")
    m = PDF_RE.search(page)
    if not m:
        raise RuntimeError(f"{slug}: no embedded PDF found (page layout changed?)")
    pdf_url = m.group(1)
    pdf_bytes = fetch_url(pdf_url)
    from pathlib import Path
    out = Path(outdir) / (slug + ".pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pdf_bytes)
    return str(out)


def main(argv):
    if argv[:1] == ["--list"]:
        for slug in list_slugs(argv[1]):
            print(slug)
        return
    for slug in argv:
        outdir = "tof_magazine_en" if slug.startswith("tof-issue-no-") else "mkulima_mbunifu_sw"
        try:
            path = fetch_issue(slug, outdir)
            print(f"OK: {slug} -> {path}")
        except Exception as e:
            print(f"FAILED: {slug} — {type(e).__name__}: {str(e)[:150]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python fetch_infonet_magazines.py --list {tof|mkm} | <slug> ...")
    main(sys.argv[1:])
