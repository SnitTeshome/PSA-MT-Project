"""Recon pass over Kenyan government agriculture sites via the KE residential exit.

Re-checks sites SOURCES.md flagged as down/unreachable/unprobed as of 2026-07-10:
kilimo.go.ke (main ministry site was down), KAMIS (confirmed reachable but content
never pulled), and county agriculture depts (never probed at all). Read-only recon —
does not write to agriculture_psas.csv. Prints a findings summary to update SOURCES.md
by hand after review.

Usage (needs FETCH_PROXY=socks5h://<ke-exit> set, see proxy_notes_private.md):
    python fetch_kenya_gov_recon.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fetchlib import fetch_url  # noqa: E402

from bs4 import BeautifulSoup  # noqa: E402

SITES = {
    "kilimo.go.ke (main ministry)": "https://kilimo.go.ke/",
    "kilimo.go.ke/press-release/": "https://kilimo.go.ke/press-release/",
    "KAMIS market info": "https://kamis.kilimo.go.ke/",
    "Kakamega county": "https://kakamega.go.ke/",
    "Meru county": "https://meru.go.ke/",
}

SW_HINT_RE = re.compile(r"\bkiswahili\b|\bswahili\b|/sw/|lang=sw|hreflang=\"sw", re.I)


def probe(label: str, url: str) -> None:
    print(f"\n=== {label} — {url} ===")
    try:
        html = fetch_url(url, verify_tls=False).decode("utf-8", errors="replace")
    except Exception as e:
        print(f"UNREACHABLE: {type(e).__name__}: {str(e)[:200]}")
        return

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "(no title)"
    print(f"REACHABLE — title: {title!r}, body size: {len(html)} chars")

    sw_hits = SW_HINT_RE.findall(html)
    print(f"Swahili/language-switch signal: {'YES (' + str(len(sw_hits)) + ' hits)' if sw_hits else 'none found'}")

    ag_links = sorted({
        a["href"] for a in soup.find_all("a", href=True)
        if re.search(r"kilimo|agri|ag(ric)?ulture|mazao|wakulima", a["href"], re.I)
        or re.search(r"kilimo|agri|ag(ric)?ulture|mazao|wakulima", a.get_text(), re.I)
    })
    if ag_links:
        print(f"Agriculture-related links ({len(ag_links)}), sample:")
        for link in list(ag_links)[:8]:
            print(f"  {link}")


def main():
    for label, url in SITES.items():
        probe(label, url)


if __name__ == "__main__":
    main()
