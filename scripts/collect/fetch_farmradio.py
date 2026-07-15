"""Fetch confirmed English+Kiswahili script pairs from Farm Radio International.

scripts.farmradio.fm robots.txt is `Disallow:` (blank) with `Crawl-delay: 10` — i.e.
fully scriptable, contrary to an earlier (wrong) recon note that called it
robots-disallowed. The one real constraint is licensing: script pages carry no CC
statement ("(c) Farm Radio International, All Rights Reserved") — usable for
hand-inspection / dataset-building for a class project, confirm with FRI before any
redistribution.

Pairing mechanism (reliable, found 2026-07-12): every script page emits WPML
hreflang alternate links in its <head>, e.g.:
    <link rel="alternate" hreflang="en-ca" href=".../radio-script/<slug>/">
    <link rel="alternate" hreflang="sw-cg" href=".../sw/mwongozo-wa-redio/<slug>/">
So instead of crawling the ~94-page English agriculture hub and checking each of
~940 articles for a translation, crawl the much smaller Swahili-locale hub
(https://scripts.farmradio.fm/sw/mada/kilimo/, 6 pages, ~60 articles) — every item
listed there already has a Swahili translation. For each, hreflang gives the exact
English twin: a true pair, not a guess.

Article body = <div class="entry-content"> (intro/backgrounder) + all sibling
<div class="dialogue"> (script lines, present on interview/spot formats) inside
<article>, in document order. Backgrounder-only pages (no dialogue) still work —
there just won't be any .dialogue divs.

Usage:
    python fetch_farmradio.py --list [<topic-slug>]     # print SW article URLs (default: kilimo)
    python fetch_farmradio.py --fetch-all [<topic-slug>]  # crawl + pair + write candidates CSV
"""

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fetchlib import fetch_url, confirm_bulk_download  # noqa: E402

from bs4 import BeautifulSoup  # noqa: E402

BASE = "https://scripts.farmradio.fm"
EST_MB_PER_PAIR = 0.1  # two HTML article pages (EN+SW), no PDFs
OUT_CSV = (Path(__file__).resolve().parents[2]
           / "data/raw/agriculture/_candidates_farmradio.csv")

HREFLANG_RE = re.compile(
    r'<link rel="alternate" hreflang="([a-z-]+)" href="([^"]+)"'
)
ARTICLE_LINK_RE = re.compile(
    r'itemid="(https://scripts\.farmradio\.fm/sw/mwongozo-wa-redio/[^"]+)"'
)


def list_sw_articles(topic_slug: str = "kilimo") -> list:
    urls = set()
    page = 1
    while True:
        page_url = (f"{BASE}/sw/mada/{topic_slug}/"
                    if page == 1 else f"{BASE}/sw/mada/{topic_slug}/page/{page}/")
        try:
            html = fetch_url(page_url).decode("utf-8", errors="replace")
        except Exception as e:
            if page == 1:
                raise
            break  # ran past the last page
        found = set(ARTICLE_LINK_RE.findall(html))
        if not found:
            break
        urls |= found
        page += 1
    return sorted(urls)


def _extract_text(html: str) -> tuple:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    title = h1.get_text(strip=True) if h1 else ""
    art = soup.select_one("article")
    if not art:
        return title, ""
    parts = []
    entry = art.select_one("div.entry-content")
    if entry:
        parts.append(entry.get_text("\n", strip=True))
    for d in art.select("div.dialogue"):
        parts.append(d.get_text("\n", strip=True))
    return title, "\n".join(p for p in parts if p)


def _hreflang_map(html: str) -> dict:
    return dict(HREFLANG_RE.findall(html))


def fetch_pair(sw_url: str) -> dict:
    sw_html = fetch_url(sw_url).decode("utf-8", errors="replace")
    langs = _hreflang_map(sw_html)
    en_url = langs.get("en-ca")
    if not en_url:
        raise RuntimeError(f"{sw_url}: no en-ca hreflang alternate found")
    sw_title, sw_text = _extract_text(sw_html)

    en_html = fetch_url(en_url).decode("utf-8", errors="replace")
    en_title, en_text = _extract_text(en_html)

    return {
        "sw_url": sw_url, "en_url": en_url,
        "sw_title": sw_title, "en_title": en_title,
        "sw_text": sw_text, "en_text": en_text,
    }


def main(argv):
    if argv[:1] == ["--list"]:
        topic = argv[1] if len(argv) > 1 else "kilimo"
        for u in list_sw_articles(topic):
            print(u)
        return

    if argv[:1] == ["--fetch-all"]:
        topic = argv[1] if len(argv) > 1 else "kilimo"
        urls = list_sw_articles(topic)
        print(f"{len(urls)} Swahili article(s) found under topic '{topic}'")
        if not confirm_bulk_download(len(urls), EST_MB_PER_PAIR, "Farm Radio International"):
            return
        OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        write_header = not OUT_CSV.exists()
        with OUT_CSV.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "sw_url", "en_url", "sw_title", "en_title", "sw_text", "en_text"])
            if write_header:
                w.writeheader()
            ok, failed = 0, 0
            for u in urls:
                try:
                    row = fetch_pair(u)
                    w.writerow(row)
                    f.flush()
                    print(f"OK: {row['en_title']!r} <-> {row['sw_title']!r}")
                    ok += 1
                except Exception as e:
                    print(f"FAILED: {u} — {type(e).__name__}: {str(e)[:150]}")
                    failed += 1
        print(f"\n{ok} pair(s) written to {OUT_CSV}, {failed} failure(s)")
        return

    sys.exit("usage: python fetch_farmradio.py --list [topic] | --fetch-all [topic]")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python fetch_farmradio.py --list [topic] | --fetch-all [topic]")
    main(sys.argv[1:])
