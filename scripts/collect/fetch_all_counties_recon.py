"""Recon pass over all 47 Kenya county government websites, checking each for an
agriculture department page and any Swahili/PSA signal.

Domain list sourced from the Council of Governors ("The 47 Counties" page,
cog.go.ke/the-47-counties/) 2026-07-14, cross-checked against the first 10 entries of
parliament.go.ke/the-senate/counties (official Senate source) — matched exactly. One
entry (Nyeri) was a scrape artifact pointing at Mandera's URL in the COG page; fixed by
direct verification (www.nyeri.go.ke, confirmed 200 OK).

Read-only recon — does not write to agriculture_psas.csv. Prints a findings summary.

Usage (set FETCH_PROXY if a proxy is needed):
    python fetch_all_counties_recon.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from fetchlib import fetch_url  # noqa: E402

from bs4 import BeautifulSoup  # noqa: E402

COUNTIES = {
    "Mombasa": "http://www.mombasa.go.ke/",
    "Kwale": "http://www.kwalecountygov.com/",
    "Kilifi": "http://www.kilifi.go.ke/",
    "Tana River": "http://www.tanariver.go.ke/",
    "Lamu": "http://www.lamu.go.ke/",
    "Taita-Taveta": "http://taitataveta.go.ke/",
    "Garissa": "http://www.garissa.go.ke/",
    "Wajir": "http://www.wajir.go.ke/",
    "Mandera": "http://www.mandera.go.ke/",
    "Marsabit": "http://marsabit.go.ke/",
    "Isiolo": "http://www.isiolo.go.ke/",
    "Meru": "http://meru.go.ke/",
    "Tharaka-Nithi": "http://www.tharakanithi.go.ke/",
    "Embu": "http://www.embu.go.ke/",
    "Kitui": "http://www.kitui.go.ke/",
    "Machakos": "http://www.machakosgovernment.com/",
    "Makueni": "http://www.makueni.go.ke/",
    "Nyandarua": "http://www.nyandarua.go.ke/",
    "Nyeri": "http://www.nyeri.go.ke/",  # fixed 2026-07-14, COG page had Mandera's URL here
    "Kirinyaga": "http://www.kirinyaga.go.ke/",
    "Murang'a": "http://muranga.go.ke/",
    "Kiambu": "http://www.kiambu.go.ke/",
    "Turkana": "http://www.turkana.go.ke/",
    "West Pokot": "http://www.westpokot.go.ke/",
    "Samburu": "http://www.samburu.go.ke/",
    "Trans Nzoia": "https://www.transnzoia.go.ke/",
    "Uasin Gishu": "http://uasingishu.go.ke/",
    "Elgeyo-Marakwet": "http://www.elgeyomarakwet.go.ke/",
    "Nandi": "http://nandi.go.ke/",
    "Baringo": "http://www.baringo.go.ke/",
    "Laikipia": "http://www.laikipiacounty.go.ke/",
    "Nakuru": "http://www.nakuru.go.ke/",
    "Narok": "http://www.narok.go.ke/",
    "Kajiado": "https://www.kajiado.go.ke/",
    "Kericho": "http://kericho.go.ke/",
    "Bomet": "http://www.bomet.go.ke/",
    "Kakamega": "http://www.kakamega.go.ke/",
    "Vihiga": "http://vihiga.go.ke/",
    "Bungoma": "http://www.bungoma.go.ke/",
    "Busia": "http://www.busiacounty.go.ke/",
    "Siaya": "http://www.siaya.go.ke/",
    "Kisumu": "http://kisumu.go.ke/",
    "Homa Bay": "http://homabay.go.ke/",
    "Migori": "http://migori.go.ke/",
    "Kisii": "http://www.kisii.go.ke/",
    "Nyamira": "http://www.nyamira.go.ke/",
    "Nairobi": "http://www.nairobi.go.ke/",
}

SW_HINT_RE = re.compile(r"\bkiswahili\b|\bswahili\b|/sw/|lang=sw|hreflang=\"sw", re.I)
AG_LINK_RE = re.compile(r"agri|kilimo|livestock|fisher|mifugo|mazao", re.I)


def probe(county: str, url: str) -> dict:
    result = {"county": county, "homepage_url": url, "reachable": False,
              "ag_page_url": None, "sw_signal": False, "error": None}
    try:
        html = fetch_url(url, verify_tls=False).decode("utf-8", errors="replace")
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)[:150]}"
        return result

    result["reachable"] = True
    if SW_HINT_RE.search(html):
        result["sw_signal"] = True

    soup = BeautifulSoup(html, "html.parser")
    ag_links = [a["href"] for a in soup.find_all("a", href=True)
                if AG_LINK_RE.search(a["href"]) or AG_LINK_RE.search(a.get_text())]
    if not ag_links:
        return result

    ag_url = ag_links[0]
    if ag_url.startswith("/"):
        from urllib.parse import urljoin
        ag_url = urljoin(url, ag_url)
    result["ag_page_url"] = ag_url

    try:
        ag_html = fetch_url(ag_url, verify_tls=False).decode("utf-8", errors="replace")
        if SW_HINT_RE.search(ag_html):
            result["sw_signal"] = True
    except Exception as e:
        result["error"] = f"ag page fetch failed: {type(e).__name__}: {str(e)[:100]}"

    return result


def main():
    results = []
    for i, (county, url) in enumerate(COUNTIES.items(), 1):
        print(f"[{i}/{len(COUNTIES)}] {county} ({url}) ...", file=sys.stderr)
        r = probe(county, url)
        results.append(r)
        status = "OK" if r["reachable"] else f"FAIL: {r['error']}"
        ag = f"ag_page={r['ag_page_url']}" if r["ag_page_url"] else "no ag link found"
        sw = "SWAHILI SIGNAL FOUND" if r["sw_signal"] else "english-only"
        print(f"  -> {status} | {ag} | {sw}", file=sys.stderr)

    reachable = [r for r in results if r["reachable"]]
    unreachable = [r for r in results if not r["reachable"]]
    with_ag = [r for r in reachable if r["ag_page_url"]]
    with_sw = [r for r in results if r["sw_signal"]]

    print("\n" + "=" * 60)
    print(f"SUMMARY: {len(reachable)}/{len(results)} reachable, "
          f"{len(with_ag)} had a findable agriculture link, "
          f"{len(with_sw)} showed any Swahili signal")
    if unreachable:
        print(f"\nUnreachable ({len(unreachable)}):")
        for r in unreachable:
            print(f"  {r['county']}: {r['error']}")
    if with_sw:
        print(f"\nSwahili signal found ({len(with_sw)}):")
        for r in with_sw:
            print(f"  {r['county']}: {r['homepage_url']}")


if __name__ == "__main__":
    main()
