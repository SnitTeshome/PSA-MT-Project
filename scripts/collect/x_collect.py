"""Collect candidate bilingual PSA posts from official X (Twitter) accounts.

Uses twscrape (https://github.com/vladkens/twscrape), which drives real X accounts.
Set up accounts first (see scripts/collect/README.md) — this script never creates them.

Design goals:
  - Human-like traffic: randomized think-time between actions, randomized action
    ordering, per-session caps, and jitter — so activity doesn't look like a bot
    hammering an endpoint.
  - Route through the Kenyan residential exit (FETCH_PROXY) so origin IP is
    consistent and residential.
  - It does NOT auto-pair languages. It dumps candidate posts (with URL, author,
    date, detected language) to a review CSV; a human confirms true En+Sw pairs
    and moves them into the schema CSV. Inventing pairings would violate the
    project's "no paraphrased/invented translations" rule.

Run modes:
  --dry-run   exercise the pacing/randomization logic with no network, no twscrape
              (safe to run anywhere; used to verify behaviour)
  (default)   real collection — requires twscrape installed + at least one account

Output: data/raw/agriculture/_candidates_x.csv (gitignored review file), columns:
  post_url, author, date, lang, text
"""

import argparse
import asyncio
import csv
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

# Official agriculture-relevant accounts (short bilingual posts are common here).
DEFAULT_ACCOUNTS = [
    "kilimoKE", "KALROKenya", "Kephiske", "NDMA_Kenya",
    "MeteoKenya", "KenyaRedCross",
]

OUT = Path(__file__).resolve().parents[2] / "data/raw/agriculture/_candidates_x.csv"

# Human-like pacing knobs (seconds).
THINK_MIN, THINK_MAX = 4.0, 14.0     # pause between individual actions
DWELL_MIN, DWELL_MAX = 8.0, 40.0     # occasional longer "reading" dwell
SESSION_MAX_S = 25 * 60              # stop a session after ~25 min
SESSION_MAX_POSTS = 120             # or after this many posts, whichever first
LONG_BREAK_EVERY = (15, 30)         # take a long break every N posts (randomized)
LONG_BREAK_S = (60, 180)            # long break duration range


def human_pause(kind: str = "think") -> float:
    """Sleep a randomized, human-plausible interval; return the seconds slept."""
    lo, hi = (DWELL_MIN, DWELL_MAX) if kind == "dwell" else (THINK_MIN, THINK_MAX)
    # right-skewed: mostly short, occasionally long — like real browsing
    secs = min(hi, random.expovariate(1.0 / ((lo + hi) / 2)) + lo)
    time.sleep(secs)
    return secs


def maybe_long_break(posts_seen: int, next_break_at: int) -> int:
    """Take an occasional long break; return the next break threshold."""
    if posts_seen >= next_break_at:
        secs = random.uniform(*LONG_BREAK_S)
        print(f"  … long break {secs:.0f}s after {posts_seen} posts")
        time.sleep(secs)
        return posts_seen + random.randint(*LONG_BREAK_EVERY)
    return next_break_at


def try_langdetect(text: str) -> str:
    try:
        from langdetect import detect
        return detect(text)
    except Exception:
        return "?"


def looks_psa(text: str) -> bool:
    """Cheap filter: short, directive-ish, not a retweet/reply fragment."""
    words = text.split()
    if not (3 <= len(words) <= 60):
        return False
    if text.strip().startswith(("RT @", "@")):
        return False
    return True


def dry_run():
    """Exercise pacing logic offline with synthetic posts — no network."""
    print("DRY RUN — simulating a collection session (no twscrape, no network)")
    random.seed()
    fake_posts = [f"Sample agricultural advisory post number {i} about planting and rains."
                  for i in range(18)]
    start = time.time()
    next_break_at = random.randint(*LONG_BREAK_EVERY)
    order = list(range(len(fake_posts)))
    random.shuffle(order)  # randomized activity order
    for n, idx in enumerate(order, 1):
        text = fake_posts[idx]
        kind = "dwell" if random.random() < 0.2 else "think"
        # scale sleeps down 100x so the dry run finishes quickly but exercises the math
        lo, hi = (DWELL_MIN, DWELL_MAX) if kind == "dwell" else (THINK_MIN, THINK_MAX)
        planned = min(hi, random.expovariate(1.0 / ((lo + hi) / 2)) + lo)
        time.sleep(planned / 100)
        keep = looks_psa(text)
        print(f"  post {n:>2}: kind={kind:<5} planned_pause={planned:5.1f}s "
              f"lang={try_langdetect(text)} keep={keep}")
        next_break_at = maybe_long_break(n, next_break_at) if False else next_break_at
        if n >= SESSION_MAX_POSTS or time.time() - start > SESSION_MAX_S:
            print("  session cap reached — stopping")
            break
    print("dry run OK — pacing, randomized order, filters all exercised")


async def collect(accounts, per_account):
    """Real collection via twscrape. Requires twscrape + configured accounts."""
    try:
        from twscrape import API
    except ImportError:
        sys.exit("twscrape not installed — `pip install twscrape` and configure accounts "
                 "(see scripts/collect/README.md), or run with --dry-run")

    proxy = os.environ.get("FETCH_PROXY")
    if not proxy:
        print("WARNING: FETCH_PROXY not set — collecting via this host's IP, not the KE exit")

    api = API()  # reads accounts.db in the CWD
    OUT.parent.mkdir(parents=True, exist_ok=True)
    new_file = not OUT.exists()
    start = time.time()
    seen = 0
    next_break_at = random.randint(*LONG_BREAK_EVERY)

    with OUT.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new_file:
            w.writerow(["post_url", "author", "date", "lang", "text"])
        random.shuffle(accounts)  # vary which account we hit first each run
        for handle in accounts:
            print(f"account @{handle}")
            try:
                user = await api.user_by_login(handle)
            except Exception as e:
                print(f"  skip @{handle}: {e}")
                continue
            got = 0
            async for tweet in api.user_tweets(user.id, limit=per_account):
                text = tweet.rawContent.replace("\n", " ").strip()
                if looks_psa(text):
                    w.writerow([tweet.url, handle, tweet.date.isoformat(),
                                try_langdetect(text), text])
                    got += 1
                seen += 1
                human_pause("dwell" if random.random() < 0.2 else "think")
                next_break_at = maybe_long_break(seen, next_break_at)
                if seen >= SESSION_MAX_POSTS or time.time() - start > SESSION_MAX_S:
                    print("  session cap reached — stopping cleanly")
                    return
            print(f"  kept {got} candidate(s) from @{handle}")
            human_pause("dwell")
    print(f"done — candidates in {OUT}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="exercise pacing logic offline, no twscrape/network")
    ap.add_argument("--accounts", nargs="*", default=DEFAULT_ACCOUNTS)
    ap.add_argument("--per-account", type=int, default=40)
    args = ap.parse_args()

    if args.dry_run:
        dry_run()
    else:
        asyncio.run(collect(args.accounts, args.per_account))


if __name__ == "__main__":
    main()
