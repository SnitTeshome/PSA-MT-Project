"""Config-driven source list for the Health domain.

Add/edit sources here instead of writing a new fetch_<source>.py per site.
generic_fetch.py reads this list and iterates over every source automatically.

Fields per source:
    name            - short identifier, used in output filenames
    category        - Government / NGO / International Organization / Media / Social Media
    index_url       - the page listing articles (or None if manual-only)
    article_link_re - regex matching internal links to individual articles
                       (relative or absolute) - set to None until you've
                       inspected the page and confirmed the pattern
    title_selector   - CSS-ish tag name to try for the title (e.g. "h1")
    body_selector    - (tag, class-regex) tuple to try for the article body
    manual_only     - True if this source has no reliable scriptable structure
                       yet; generic_fetch.py will skip it and just remind you
                       to collect it by hand
    verify_tls      - set to False ONLY for sites that serve a broken/
                       self-signed certificate chain (confirmed via a real
                       SSLCertVerificationError, not guessed in advance).
                       Defaults to True if the key is omitted.
    notes           - free-text reminders (bilingual quirks, blockers, etc.)

HOW TO ACTIVATE A PLACEHOLDER SOURCE:
  1. Open the index_url in your browser, view source.
  2. Find the pattern used for article links -> fill in article_link_re.
  3. Open one article page, find the title tag and the body container ->
     fill in title_selector / body_selector.
  4. Flip manual_only to False.
  5. Re-run generic_fetch.py --source <name> --list to confirm it now finds links.
"""

SOURCES = [
    {
        "name": "moh_kenya_press_releases",
        "category": "Government",
        "index_url": "https://www.health.go.ke/press-releases",
        # Confirmed 2026-07-13 via --dump-html: this is a Drupal 9 site,
        # individual press releases are served as /node/<id>, NOT as
        # readable slugs like /press-releases/<slug> (that was wrong).
        "article_link_re": r"^/node/\d+$",
        "title_selector": "h1",
        "body_selector": ("div", r"field--name-body|node__content"),
        "manual_only": False,
        "verify_tls": False,
        "notes": "Confirmed SSLCertVerificationError (self-signed cert in "
                 "chain) on 2026-07-13 - same class of issue as "
                 "kamis.kilimo.go.ke. Only safe because this is a public "
                 "read-only page with no sensitive data exchanged. Site has "
                 "an English/Swahili toggle, but not every node has a "
                 "confirmed Swahili twin - verify per article. Only ~7 node "
                 "links appear on the index page (no pagination handling "
                 "yet) - may need to check /press-statements and other "
                 "index pages too for more nodes.",
    },
    {
        "name": "moh_kenya_press_statements",
        "category": "Government",
        "index_url": "https://www.health.go.ke/press-statements",
        "article_link_re": r"^/node/\d+$",
        "title_selector": "h1",
        "body_selector": ("div", r"field--name-body|node__content"),
        "manual_only": False,
        "verify_tls": False,
        "notes": "Same site/structure as press_releases, different index page. "
                 "Same broken cert chain as press_releases - see that entry's note.",
    },
    {
        "name": "moh_kenya_publications",
        "category": "Government",
        "index_url": "https://health.go.ke/publications",
        "article_link_re": None,
        "title_selector": None,
        "body_selector": None,
        "manual_only": True,
        "notes": "PLACEHOLDER - likely PDF downloads, not HTML articles. "
                 "Inspect the page structure before activating; may need "
                 "pymupdf (fitz) for PDF text extraction instead of BeautifulSoup.",
    },
    {
        "name": "who_afro_kenya",
        "category": "International Organization",
        "index_url": "https://www.afro.who.int/countries/kenya",
        "article_link_re": None,
        "title_selector": None,
        "body_selector": None,
        "manual_only": True,
        "notes": "PLACEHOLDER - inspect page structure. WHO content is often "
                 "multi-language by design; check for a Swahili locale path.",
    },
    {
        "name": "who_kenya_twitter",
        "category": "International Organization - Social Media",
        "index_url": "https://x.com/WHOKenya",
        "article_link_re": None,
        "title_selector": None,
        "body_selector": None,
        "manual_only": True,
        "notes": "X/Twitter requires twscrape or manual copy - see project "
                 "README section on collecting from X. Not a plain HTML scrape.",
    },
    {
        "name": "amref_kenya",
        "category": "NGO",
        "index_url": "https://amref.org/kenya/",
        "article_link_re": None,
        "title_selector": None,
        "body_selector": None,
        "manual_only": True,
        "notes": "PLACEHOLDER - prior review suggested weak bilingual digital "
                 "presence; verify before investing scripting time.",
    },
    {
        "name": "amref_twitter",
        "category": "NGO - Social Media",
        "index_url": "https://x.com/amref_worldwide",
        "article_link_re": None,
        "title_selector": None,
        "body_selector": None,
        "manual_only": True,
        "notes": "X/Twitter - manual copy or twscrape, same as who_kenya_twitter.",
    },
    {
        "name": "africa_newsroom_moh",
        "category": "Media/Aggregator",
        "index_url": "https://www.africa-newsroom.com/press/source/ministry-of-health-kenya",
        "article_link_re": None,
        "title_selector": None,
        "body_selector": None,
        "manual_only": True,
        "notes": "PLACEHOLDER - aggregator; check first whether it carries "
                 "any Swahili content at all before activating.",
    },
    {
        "name": "un_kenya_directory",
        "category": "International Organization",
        "index_url": "https://kenya.un.org/en/contact-us",
        "article_link_re": None,
        "title_selector": None,
        "body_selector": None,
        "manual_only": True,
        "notes": "Not a PSA content source itself - used only to locate "
                 "official WHO/UNICEF channels. Do not scrape for dataset rows.",
    },
    {
        "name": "kemri",
        "category": "Government - Research Institute",
        "index_url": "https://www.kemri.go.ke/",
        "article_link_re": None,
        "title_selector": None,
        "body_selector": None,
        "manual_only": True,
        "notes": "PLACEHOLDER - inspect page structure before activating.",
    },
]
