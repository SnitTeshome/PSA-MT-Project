"""Run this on your own device — the two things left in BRADLEY_ACTIONS.md that a
script can actually help with, but that need a real, logged-in browser session:

1. Facebook county government Pages — scraping without a logged-in session hits
   Facebook's anti-automation wall (the page hangs forever on the loading splash
   screen, confirmed 2026-07-14) and the lightweight mbasic/m.facebook.com endpoints
   are robots.txt disallowed outright. Running this on your own device, logged into
   your own Facebook account in a real browser, is the only approach left that isn't
   fighting both a technical block and Facebook's stated policy at once.

2. The 2 still-missing CGSpace Babati soil-fertility PDFs — CGSpace rate-limits
   aggressively (confirmed repeatedly). Worth one more try before falling back to a
   manual browser download.

Everything else in BRADLEY_ACTIONS.md (X account creation/warm-up, sending outreach
emails, transcribing a printed newspaper notice, raising team decisions) is inherently
manual — account creation and human judgment calls aren't things a script can do, so
they're not included here.

Setup (once):
    pip install playwright requests
    # NOT "playwright install chromium" — this script drives your installed Brave
    # browser instead (BRAVE_PATH below), so no extra ~300MB browser download needed.

Usage:
    # Step 1 — one-time interactive login. Opens a real, visible Brave window (a fresh
    # one, using its own dedicated profile dir — does not touch your regular Brave
    # session/tabs/cookies). Log into Facebook normally in it (handles 2FA/checkpoints
    # yourself), then press Enter in the terminal once you're logged in and on your own
    # feed. This saves the session to ~/.psa_mt_fb_profile so future runs are already
    # logged in — you only do this once.
    python local_collect_facebook_cgspace.py login

    # Step 2 — scrape the county Pages (uses the saved login from step 1)
    python local_collect_facebook_cgspace.py facebook

    # Step 3 — try the CGSpace Babati PDFs (public/open-access, no account needed —
    # the earlier failure was rate-limiting, not a login wall)
    python local_collect_facebook_cgspace.py cgspace

Each step writes local files (fb_results.json / cgspace_*.pdf) in whatever directory you
run the script from. Both 'facebook' and 'cgspace' print an estimated data size and ask
for confirmation before downloading anything. Set PSA_AUTO_CONFIRM=1 to skip that prompt.

Copy the output files into the project's data folder afterwards (e.g. via a file sync
tool, USB, or whatever you normally use to move files onto this machine).
"""

import json
import shutil
import sys
import time
from pathlib import Path

PROFILE_DIR = str(Path.home() / ".psa_mt_fb_profile")
OUT_FILE = Path("fb_results.json")

# Brave's default install path on macOS. Override with BRAVE_PATH env var if yours
# differs, or if you're not on macOS.
import os
BRAVE_PATH = os.environ.get(
    "BRAVE_PATH", "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
)
if not Path(BRAVE_PATH).exists():
    sys.exit(f"Brave not found at {BRAVE_PATH} — set BRAVE_PATH env var to its actual "
              f"location, e.g. export BRAVE_PATH='/path/to/Brave Browser'")

# County government Facebook Pages found 2026-07-14 by grepping each county's official
# .go.ke homepage for a facebook.com link — see SOURCES.md section 7 for the domain list
# this was derived from. Add/replace URLs freely; this is just where the recon left off.
COUNTY_PAGES = {
    "Mombasa": "https://www.facebook.com/MombasaCountyKe",
    "Kilifi": "https://www.facebook.com/KilifiGovt",
    "Tana River": "https://www.facebook.com/TRCGpress",
    "Garissa": "https://www.facebook.com/GarissaCountyKE",
    "Wajir": "https://www.facebook.com/WajirKE",
    "Mandera": "https://www.facebook.com/manderacountygov1",
    "Marsabit": "https://www.facebook.com/marsabitcountyg",
    "Isiolo": "https://www.facebook.com/IsioloCounty",
    "Meru": "https://www.facebook.com/merucounty012",
    "Tharaka-Nithi": "https://www.facebook.com/TharakaNithiCounty",
    "Embu": "https://www.facebook.com/EmbuCountyGov",
    "Makueni": "https://www.facebook.com/makuenigovt",
    "Nyeri": "https://www.facebook.com/County19Nyeri",
    "Kirinyaga": "https://www.facebook.com/CountyGovermentOfKirinyaga",
    "Kiambu": "https://www.facebook.com/kiambucountygov",
    "Turkana": "https://www.facebook.com/TurkanaCountyGov",
    "Samburu": "https://www.facebook.com/SamburuCounty025",
    "Trans Nzoia": "https://www.facebook.com/countygovernmentoftransnzoia",
    "Elgeyo-Marakwet": "https://www.facebook.com/elgeyomarakwetcounty",
    "Baringo": "https://www.facebook.com/CountyGovernmentofBaringo",
    "Kajiado": "https://www.facebook.com/KajiadoCountyGovernment",
    "Kericho": "https://www.facebook.com/kerichocounty.go.ke",
    "Vihiga": "https://www.facebook.com/vihigacountygov",
    "Kisumu": "https://www.facebook.com/kisumucountyke",
    "Migori": "https://www.facebook.com/MigoriCountyGovernment",
}

CGSPACE_TARGETS = {
    "babati_soil_fertility_EN": "a8785e00-01cc-43ca-ae3b-9914fb532925",
    "babati_soil_fertility_SW": "4ff8daa4-34bd-41af-9182-a0be12894492",
}


def confirm_download(item_count: int, est_mb_per_item: float, source_name: str) -> bool:
    """Print an estimated download size and require explicit confirmation before
    fetching anything, since results get saved to this machine's local disk. Set
    PSA_AUTO_CONFIRM=1 to skip the prompt."""
    est_total_mb = item_count * est_mb_per_item
    print(f"\nAbout to fetch {item_count} item(s) from {source_name} — "
          f"roughly {est_total_mb:.0f} MB total (~{est_mb_per_item:.1f} MB/item).")
    if os.environ.get("PSA_AUTO_CONFIRM") == "1":
        print("PSA_AUTO_CONFIRM=1 set — continuing without prompt.")
        return True
    reply = input("Continue? [y/N]: ").strip().lower()
    if reply != "y":
        print("Aborted — nothing downloaded.")
        return False
    return True


def login():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE_DIR, headless=False, executable_path=BRAVE_PATH
        )
        page = ctx.new_page()
        page.goto("https://www.facebook.com/")
        input("Log into Facebook in the window that opened, then press Enter here once "
              "you're on your own feed... ")
        ctx.close()
    print(f"Session saved to {PROFILE_DIR}. Run 'facebook' next.")


def scrape_facebook():
    from playwright.sync_api import sync_playwright

    if not Path(PROFILE_DIR).exists():
        sys.exit("No saved session found — run 'login' first.")

    if not confirm_download(len(COUNTY_PAGES), 0.5, "Facebook (county government Pages)"):
        return

    results = {}
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROFILE_DIR, headless=False, executable_path=BRAVE_PATH
        )
        page = ctx.new_page()
        for county, url in COUNTY_PAGES.items():
            print(f"Fetching {county} ({url})...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(4000)
                for _ in range(3):  # scroll to load a few recent posts
                    page.mouse.wheel(0, 2000)
                    page.wait_for_timeout(2000)
                text = page.evaluate("document.body.innerText")
                results[county] = {"url": url, "text_len": len(text), "text": text}
                print(f"  -> got {len(text)} chars")
            except Exception as e:
                results[county] = {"url": url, "error": str(e)}
                print(f"  -> FAILED: {e}")
        ctx.close()

    OUT_FILE.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nWrote {OUT_FILE.resolve()} — paste its contents back into the chat, "
          f"or attach the file directly.")


def download_cgspace():
    import requests

    if not confirm_download(len(CGSPACE_TARGETS), 2.0, "CGSpace (CGIAR repository)"):
        return

    for label, uuid in CGSPACE_TARGETS.items():
        url = f"https://cgspace.cgiar.org/server/api/core/bitstreams/{uuid}/content"
        out = Path(f"cgspace_{label}.pdf")
        print(f"Downloading {label}...")
        try:
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            })
            resp.raise_for_status()
            out.write_bytes(resp.content)
            print(f"  -> saved {out.resolve()} ({len(resp.content)} bytes)")
        except Exception as e:
            print(f"  -> FAILED: {e} — fall back to downloading it from a browser: "
                  f"https://cgspace.cgiar.org/server/api/core/bitstreams/{uuid}/content")
        time.sleep(5)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("login", "facebook", "cgspace"):
        sys.exit("usage: python local_collect_facebook_cgspace.py [login|facebook|cgspace]")
    {"login": login, "facebook": scrape_facebook, "cgspace": download_cgspace}[sys.argv[1]]()
