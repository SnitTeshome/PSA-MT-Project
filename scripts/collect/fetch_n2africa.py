"""Fetch extension leaflets/booklets from N2Africa's own catalog (n2africa.org/agem).

N2Africa ("Putting nitrogen fixation to work for smallholder farmers in Africa") runs a
"Guidelines, Training & Extension materials" catalog listing 80+ CC-licensed PDFs by
Code/Date/Title/Country/File. It includes:
  - A genuine EN+Swahili bilingual checklist authored directly (no translation needed):
    "Best practices to maintain high yields and grain quality of soybean" (west Kenya).
  - Swahili-original brochures with no English counterpart (e.g. Tanzania groundnut/cowpea).
  - A "Better [crop] through good agricultural practices" leaflet series repeated per
    country (Ethiopia, Nigeria, Zimbabwe, Rwanda, Tanzania, ...) — these share a heavily
    templated intro/Step-1-7 structure across countries for the same crop; only the
    country-specific passages (regional variety-selection guidance) are worth extracting
    without duplicating content already pulled from another country's edition.

n2africa.org serves an incomplete certificate chain, same as some Kenyan gov sites — this
module always fetches with verify_tls=False, same pattern as fetch_cgspace.py.

Usage:
    python fetch_n2africa.py --list [keyword]   # print Title/Country/File rows, optionally
                                                 # filtered by a case-insensitive keyword
    python fetch_n2africa.py <filename> [<filename2> ...]  # download by exact File column
                                                            # value (as printed by --list)
"""

import re
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fetchlib import fetch_url, confirm_bulk_download  # noqa: E402

CATALOG_URL = "https://www.n2africa.org/agem"
FILES_BASE = "https://www.n2africa.org/sites/default/files/"
EST_MB_PER_FILE = 2.0  # these range from ~100KB checklists to ~6MB scanned booklets

ROW_RE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
PDF_HREF_RE = re.compile(r'href="([^"]+\.pdf)"')


def _clean(html_fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html_fragment)
    return re.sub(r"\s+", " ", text).strip()


def list_catalog(keyword: str = "") -> list:
    html = fetch_url(CATALOG_URL, verify_tls=False).decode("utf-8", errors="replace")
    rows = []
    for tr in ROW_RE.findall(html):
        cells = CELL_RE.findall(tr)
        if len(cells) < 5:
            continue
        title, country = _clean(cells[2]), _clean(cells[3])
        m = PDF_HREF_RE.search(cells[4])
        if not m:
            continue
        pdf_path = m.group(1)
        if keyword and keyword.lower() not in (title + " " + country).lower():
            continue
        rows.append({"title": title, "country": country, "pdf_path": pdf_path})
    return rows


def fetch_by_path(pdf_path: str, outdir: str = ".") -> str:
    from pathlib import Path
    url = pdf_path if pdf_path.startswith("http") else FILES_BASE + pdf_path.lstrip("/")
    data = fetch_url(url, use_cache=True, verify_tls=False)
    fname = pdf_path.rsplit("/", 1)[-1]
    out = Path(outdir) / fname
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    return str(out)


def main(argv):
    if argv[:1] == ["--list"]:
        keyword = argv[1] if len(argv) > 1 else ""
        for row in list_catalog(keyword):
            print(f"{row['country']:<20} | {row['title']:<80} | {row['pdf_path']}")
        return

    if not confirm_bulk_download(len(argv), EST_MB_PER_FILE, "N2Africa (n2africa.org)"):
        return
    for path in argv:
        try:
            out = fetch_by_path(path)
            print(f"OK: {path} -> {out}")
        except Exception as e:
            print(f"FAILED: {path} — {type(e).__name__}: {str(e)[:150]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python fetch_n2africa.py --list [keyword] | <pdf_path> ...")
    main(sys.argv[1:])
