"""Shared helpers for polite, robust fetching of PSA sources.

Every per-source fetcher (fetch_<source>.py) should go through fetch_url()
so all requests get the same behaviour:

  - realistic browser User-Agent rotated per request (several Kenyan gov and
    media sites sit behind CDN bot protection that rejects default python UAs)
  - robots.txt checked once per domain before the first request
  - randomized sleep between requests to the same domain (rate limiting)
  - retries with backoff on 429/5xx
  - responses cached to data_cache/ so re-running a parser never re-hits
    the source
  - failures raise immediately with a descriptive message (source, status,
    suspected cause) - never return empty results silently
"""

import hashlib
import os
import random
import time
import urllib.robotparser
from pathlib import Path
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CACHE_DIR = Path(__file__).resolve().parent / "data_cache"

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

SLEEP_BASE_S = 5.0    # polite delay between requests to the same domain
SLEEP_JITTER_S = 3.0  # +/- randomization so requests don't look mechanical

_session = None
_robots = {}
_last_hit = {}


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        retry = Retry(total=3, backoff_factor=2,
                       status_forcelist=[429, 500, 502, 503, 504])
        _session.mount("https://", HTTPAdapter(max_retries=retry))
        _session.mount("http://", HTTPAdapter(max_retries=retry))
        proxy = os.environ.get("FETCH_PROXY")
        if proxy:
            _session.proxies = {"http": proxy, "https": proxy}
            print(f"fetchlib: routing all requests via FETCH_PROXY={proxy}")
    return _session


def _headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,sw;q=0.8",
        "Connection": "keep-alive",
    }


def _robots_allows(url: str) -> bool:
    domain = urlparse(url).netloc
    if domain not in _robots:
        rp = urllib.robotparser.RobotFileParser()
        try:
            # Fetch robots.txt through the SAME session/headers as everything
            # else - a bare urlopen() with no headers gets 403'd by some CDNs,
            # and robotparser fails "safe" on 401/403 by disallowing everything.
            resp = _get_session().get(f"https://{domain}/robots.txt",
                                       headers=_headers(), timeout=15)
            if resp.status_code in (401, 403):
                rp = None  # can't read it -> treat as no restrictions declared
            else:
                rp.parse(resp.text.splitlines())
        except Exception:
            rp = None  # robots.txt unreachable -> treat as no restrictions declared
        _robots[domain] = rp
    rp = _robots[domain]
    return rp is None or rp.can_fetch("*", url)


def _rate_limit(url: str) -> None:
    domain = urlparse(url).netloc
    elapsed = time.time() - _last_hit.get(domain, 0)
    wait = SLEEP_BASE_S + random.uniform(-SLEEP_JITTER_S, SLEEP_JITTER_S) - elapsed
    if wait > 0:
        time.sleep(wait)
    _last_hit[domain] = time.time()


def fetch_url(url: str, use_cache: bool = True, verify_tls: bool = True) -> bytes:
    """Fetch a URL politely; return response body bytes. Raises on any failure."""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / hashlib.sha256(url.encode()).hexdigest()[:24]
    if use_cache and cache_file.exists():
        return cache_file.read_bytes()

    if not _robots_allows(url):
        raise PermissionError(f"robots.txt disallows fetching {url} - pick another "
                              f"source or collect this one manually")

    _rate_limit(url)
    resp = _get_session().get(url, headers=_headers(), timeout=30, verify=verify_tls)

    if resp.status_code == 403:
        raise RuntimeError(f"{url} returned 403 - likely CDN bot block; try again "
                           f"later, adjust headers, or collect manually")
    resp.raise_for_status()
    if not resp.content:
        raise RuntimeError(f"{url} returned HTTP {resp.status_code} with an EMPTY "
                           f"body - possible soft block")

    if use_cache:
        cache_file.write_bytes(resp.content)
        (CACHE_DIR / (cache_file.name + ".url")).write_text(url)
    return resp.content
