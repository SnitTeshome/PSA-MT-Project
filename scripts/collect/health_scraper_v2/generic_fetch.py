"""Generic, config-driven fetcher for all Health domain sources.

Instead of writing one fetch_<source>.py per site, every source is described
as a config entry in sources_config.py. This script iterates over that list
and applies the same logic to each: list article links, fetch + extract
title/body, print for manual bilingual review.

Sources marked manual_only=True (i.e. not yet configured, or genuinely not
scriptable - e.g. X/Twitter, PDFs, unverified structure) are skipped with a
clear reminder instead of erroring out.

Usage:
    python generic_fetch.py --list-sources
        -> shows every configured source, its category, and whether it's
           active or a manual-only placeholder

    python generic_fetch.py --source moh_kenya_press_releases --list
        -> lists article links found on that one source's index page

    python generic_fetch.py --all --list
        -> runs --list for every active (non-manual_only) source in one go

    python generic_fetch.py --source moh_kenya_press_releases --fetch <url>
        -> fetches one specific article and prints title/body for review
"""

import argparse
import re
import sys

from bs4 import BeautifulSoup

from fetchlib import fetch_url
from sources_config import SOURCES

BY_NAME = {s["name"]: s for s in SOURCES}


def list_sources():
    print(f"{'NAME':30} {'CATEGORY':35} {'STATUS'}")
    print("-" * 90)
    for s in SOURCES:
        status = "MANUAL ONLY (placeholder)" if s["manual_only"] else "ACTIVE - scriptable"
        print(f"{s['name']:30} {s['category']:35} {status}")
        if s["notes"]:
            print(f"    note: {s['notes']}")


def list_articles(source: dict) -> list:
    if source["manual_only"] or not source["article_link_re"]:
        print(f"'{source['name']}' is manual_only - no automated link listing. "
              f"Open {source['index_url']} in a browser and collect by hand.")
        return []

    pattern = re.compile(source["article_link_re"])
    verify_tls = source.get("verify_tls", True)
    if not verify_tls:
        print(f"NOTE: TLS verification disabled for '{source['name']}' "
              f"(broken gov cert chain, see sources_config.py note)")
    html = fetch_url(source["index_url"], verify_tls=verify_tls).decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    base = re.match(r"^(https?://[^/]+)", source["index_url"]).group(1)
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if pattern.match(href):
            links.add(href if href.startswith("http") else base + href)
    return sorted(links)


def fetch_article(source: dict, url: str) -> dict:
    if source["manual_only"]:
        raise RuntimeError(
            f"'{source['name']}' is manual_only - fill in title_selector / "
            f"body_selector in sources_config.py and flip manual_only to "
            f"False before fetching articles automatically."
        )

    verify_tls = source.get("verify_tls", True)
    html = fetch_url(url, verify_tls=verify_tls).decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find(source["title_selector"]) if source["title_selector"] else None
    title = title_tag.get_text(strip=True) if title_tag else "(no title found - check title_selector)"

    body = "(no body found - check body_selector)"
    if source["body_selector"]:
        tag, class_re = source["body_selector"]
        body_div = soup.find(tag, class_=re.compile(class_re))
        if body_div:
            body = body_div.get_text(" ", strip=True)

    return {"url": url, "title": title, "body": body}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--list-sources", action="store_true", help="show all configured sources and their status")
    p.add_argument("--source", help="source name from sources_config.py")
    p.add_argument("--all", action="store_true", help="apply --list across every active source")
    p.add_argument("--list", action="store_true", help="list article links for --source (or --all)")
    p.add_argument("--fetch", metavar="URL", help="fetch and print one article's title/body")
    p.add_argument("--dump-html", action="store_true",
                    help="fetch --source's index_url and print the first 3000 chars of "
                         "raw HTML plus every <a href> found - use this when --list "
                         "returns nothing, to see the site's real link structure")
    p.add_argument("--inspect", metavar="URL",
                    help="fetch this article URL and print every h1/h2/title tag plus "
                         "every div whose class looks content-related (contains "
                         "'field', 'body', 'content', or 'node') with a text preview - "
                         "use this to find the real title_selector/body_selector "
                         "when --fetch extracts the wrong text")
    args = p.parse_args()

    if args.list_sources:
        list_sources()
        return

    if args.all and args.list:
        for s in SOURCES:
            if s["manual_only"]:
                continue
            print(f"\n=== {s['name']} ({s['category']}) ===")
            try:
                for link in list_articles(s):
                    print(link)
            except Exception as e:
                print(f"FAILED: {type(e).__name__}: {str(e)[:200]}")
        return

    if not args.source:
        sys.exit("specify --source <name> (see --list-sources for valid names), or use --all --list")

    source = BY_NAME.get(args.source)
    if not source:
        sys.exit(f"unknown source '{args.source}'. Run --list-sources to see valid names.")

    if args.inspect:
        verify_tls = source.get("verify_tls", True)
        html = fetch_url(args.inspect, verify_tls=verify_tls).decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        print("=== <title> tag ===")
        print(soup.title.get_text(strip=True) if soup.title else "(none)")

        print("\n=== h1 / h2 tags ===")
        for tag_name in ("h1", "h2"):
            for tag in soup.find_all(tag_name):
                text = tag.get_text(strip=True)
                cls = tag.get("class", [])
                if text:
                    print(f"<{tag_name} class={cls}>: {text[:120]}")

        print("\n=== divs with content-like class names ===")
        import re as _re
        content_re = _re.compile(r"field|body|content|node|article|main", _re.IGNORECASE)
        seen = set()
        for div in soup.find_all("div", class_=True):
            classes = " ".join(div.get("class", []))
            if content_re.search(classes) and classes not in seen:
                seen.add(classes)
                text = div.get_text(" ", strip=True)
                print(f"\nclass=\"{classes}\"  (text length: {len(text)})")
                print(f"  preview: {text[:150]}")
        return

    if args.dump_html:
        verify_tls = source.get("verify_tls", True)
        html = fetch_url(source["index_url"], verify_tls=verify_tls).decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")
        print("=== first 3000 chars of raw HTML ===")
        print(html[:3000])
        print("\n=== every <a href=...> found on the page ===")
        hrefs = sorted({a["href"] for a in soup.find_all("a", href=True)})
        for h in hrefs:
            print(h)
        print(f"\nTotal unique links found: {len(hrefs)}")
        return

    if args.list:
        for link in list_articles(source):
            print(link)
        return

    if args.fetch:
        try:
            result = fetch_article(source, args.fetch)
            print(f"\n--- {result['url']} ---")
            print("TITLE:", result["title"])
            print("BODY:", result["body"][:500], "...")
            print("\n>>> Manually confirm a Swahili version exists before adding to the dataset.")
        except Exception as e:
            print(f"FAILED: {type(e).__name__}: {str(e)[:200]}")
        return

    sys.exit("nothing to do - pass --list or --fetch <url> (see --help)")


if __name__ == "__main__":
    main()