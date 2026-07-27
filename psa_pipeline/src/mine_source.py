"""
mine_source.py
---------------
Step 1 of the pipeline.

Your group's scraped CSV (merged_psa_dataset.csv) mixes real PSA-style
sentences with noise: staff biographies, long policy excerpts, truncated
fragments, and plain news reporting. This module does NOT try to output
final PSAs from that file -- it MINES it for two things that make the
synthetic generator realistic:

  1. Real Kenyan issuing authorities actually seen in the data (per domain),
     e.g. "NTSA", "Ministry of Health", "EACC", "IEBC".
  2. Real PSA-style opening/verb phrases actually seen in the data,
     e.g. "wishes to inform the public that", "advises members of the
     public to".

It also keeps a small sample of the cleanest, most PSA-like real lines
purely as a human-readable reference set (data/mined/reference_lines.json)
so you can sanity-check what "real" looked like -- these lines are never
copied into the final synthetic dataset.

Heuristic filtering (why a row is kept/dropped as "PSA-like"):
  - length between 25 and 320 characters (real PSAs are short and punchy;
    the very long rows in the source are policy excerpts / bios / reports)
  - not a biography/CV fragment (regex for "holds a", "born in",
    "career began", "PS ", titles-only strings, etc.)
  - not a mid-sentence fragment (must start with a capital letter/quote
    and end with terminal punctuation)
  - contains at least one directive/informative PSA marker word
    (advise, inform, reminder, notice, warn, urge, campaign, launch, etc.)
"""

import json
import re
from collections import Counter, defaultdict

import pandas as pd

import config

BIO_PATTERNS = re.compile(
    r"\b(holds a|born in|career began|bachelor of|master'?s in|"
    r"PS [A-Z]|principal secretary|flanked by|CBS |welcoming the)\b",
    re.IGNORECASE,
)

PSA_MARKER_WORDS = re.compile(
    r"\b(advis(e|es|ed|ory)|inform(s|ed)?|remind(s|er|ed)?|notice|warn(s|ing)?|"
    r"urge(s|d)?|campaign|launch(es|ed)?|deadline|register(ed|ation)?|"
    r"caution(s|ed)?|alert(s|ed)?|encourage(s|d)?|wishes to|public is|"
    r"members of the public|please note|effective|prohibit(s|ed)?|"
    r"free\b|available|apply|enroll|vaccinat)\b",
    re.IGNORECASE,
)

# Known real Kenyan authority names/acronyms, grouped by the domain they
# actually issue PSAs for. Boosted into the mined list even if the
# automatic capitalised-phrase extractor misses them in the scraped text.
KNOWN_AUTHORITIES = {
    "Health": [
        "Ministry of Health", "SHA (Social Health Authority)", "KEMSA",
        "KEMRI", "Kenya Red Cross", "Nairobi Metropolitan Services Health Dept",
        "Division of Disease Surveillance and Response", "County Department of Health",
        "Kenya Medical Association", "National AIDS Control Council",
        "Ministry of Health - Reproductive Health Unit",
    ],
    "Agriculture": [
        "Ministry of Agriculture and Livestock Development", "KALRO",
        "KEPHIS", "NCPB", "Agriculture and Food Authority (AFA)",
        "County Department of Agriculture", "Kenya Dairy Board",
        "National Farmers Information Service", "Pest Control Products Board",
        "Kenya Plant Health Inspectorate Service",
    ],
    "Education": [
        "Ministry of Education", "TSC", "KUCCPS", "HELB", "KNEC",
        "State Department for Basic Education", "State Department for TVET",
        "Kenya Institute of Curriculum Development", "County Education Office",
        "Universities Fund",
    ],
    "Security & Safety": [
        "NTSA", "National Police Service", "DCI", "Kenya Red Cross",
        "National Disaster Management Unit", "NDMA", "Directorate of Criminal Investigations",
        "County Disaster Management Unit", "Kenya Forest Service",
        "Communications Authority of Kenya",
    ],
    "Governance": [
        "IEBC", "EACC", "ODPP", "Office of the Auditor-General",
        "Judiciary of Kenya", "Council of Governors", "e-Citizen",
        "Huduma Kenya", "Kenya Gazette", "Office of the Registrar of Political Parties",
        "Commission on Administrative Justice (Ombudsman)",
    ],
}


def is_psa_like(text: str) -> bool:
    if not isinstance(text, str):
        return False
    t = text.strip()
    if not (25 <= len(t) <= 320):
        return False
    if BIO_PATTERNS.search(t):
        return False
    if not re.match(r"^[A-Z\"'0-9]", t):
        return False
    if not re.search(r"[.!?]$", t):
        return False
    if not PSA_MARKER_WORDS.search(t):
        return False
    return True


JUNK_ACRONYMS = {
    "SMS", "BILL", "UGX", "ICS", "DL", "USD", "VAT", "CEO", "MP", "AM", "PM",
    "ID", "CS", "PS", "TV", "NB", "ETC", "FAQ", "URL", "PDF", "CBS", "OGW",
    "EGH", "MBS", "HSC", "CV", "GDP", "IT", "HR", "CBD", "NGO", "UN", "US",
    "UK", "EU", "AI", "ICT", "COVID", "TB", "NHS", "NOW", "KMD", "TIMS",
    "UDA", "CBC", "STEM", "KPSEA", "KCSE",
}
GENERIC_PHRASE_WORDS = {
    "world bank group", "the government", "government of kenya",
    "the ministry", "the kenyan", "the commission", "the county government",
    "the ps", "county government", "ol kalou", "ogp local",
}
MEDIA_OUTLET_MARKERS = ("voice", "digital", "star", "nation", "news")


def extract_authorities(text: str) -> list:
    """Pull capitalised multi-word phrases and ALLCAPS acronyms that look
    like issuing authorities, e.g. 'National Transport and Safety Authority'
    or 'NTSA'."""
    found = []
    # ALLCAPS acronyms of 2-6 letters
    found += re.findall(r"\b[A-Z]{2,6}\b", text)
    # Multi-word Title Case sequences of length >= 2 words (candidate org names)
    for m in re.finditer(r"(?:[A-Z][a-zA-Z'&\-]+\s){1,5}[A-Z][a-zA-Z'&\-]+", text):
        phrase = m.group().strip()
        if 2 <= len(phrase.split()) <= 6:
            found.append(phrase)
    return found


def extract_opening_phrase(text: str) -> str:
    """Grab the verb-phrase chunk right after the subject, e.g.
    '... wishes to inform the public that' -- useful as a template
    fragment for the generator."""
    m = PSA_MARKER_WORDS.search(text)
    if not m:
        return ""
    start = max(0, m.start() - 5)
    return text[start : m.end() + 25].strip()


def main():
    print(f"Loading raw source: {config.RAW_SOURCE_CSV}")
    df = pd.read_csv(config.RAW_SOURCE_CSV)
    df["English"] = df["English"].astype(str)

    kept_mask = df["English"].apply(is_psa_like)
    psa_like = df[kept_mask].copy()
    print(f"Rows total: {len(df)} | PSA-like after filtering: {len(psa_like)}")

    authorities_by_domain = defaultdict(Counter)
    phrases_by_domain = defaultdict(Counter)
    reference_lines_by_domain = defaultdict(list)

    for _, row in psa_like.iterrows():
        domain = row.get("Domain", "Unknown")
        text = row["English"]

        for auth in extract_authorities(text):
            # discard overly generic / short noise tokens
            if len(auth) < 2:
                continue
            authorities_by_domain[domain][auth] += 1

        phrase = extract_opening_phrase(text)
        if phrase:
            phrases_by_domain[domain][phrase.lower()] += 1

        if len(reference_lines_by_domain[domain]) < 40:
            reference_lines_by_domain[domain].append(text)

    # keep known real authorities regardless of frequency, then top mined ones
    authorities_out = {}
    for domain in config.TAXONOMY:
        # require mined authority phrases to appear at least 4 times, so
        # one-off scraping artifacts (currency codes, random acronyms,
        # mid-sentence capitalised fragments) don't slip through
        mined_top = [
            a for a, count in authorities_by_domain[domain].most_common(60)
            if count >= 4
        ]
        domain_known = KNOWN_AUTHORITIES.get(domain, [])
        combined = list(dict.fromkeys(domain_known + mined_top))
        # drop junk tokens: stray letters, numbers, stopwords, known
        # non-authority acronyms, and overly generic phrases
        combined = [
            a for a in combined
            if len(a) > 1
            and not a.isdigit()
            and a.upper() not in JUNK_ACRONYMS
            and a.lower() not in {"the", "and", "for", "of", "in", "on", "to", "public"}
            and a.lower() not in GENERIC_PHRASE_WORDS
            and "county" not in a.lower()
            and not any(
                re.search(r"\b" + re.escape(c.lower()) + r"\b", a.lower())
                for c in config.COUNTIES
            )
            and not any(marker in a.lower() for marker in MEDIA_OUTLET_MARKERS)
        ]
        # cap total list length, but always keep every curated known authority
        authorities_out[domain] = combined[:40]

    phrases_out = {
        domain: [p for p, _ in phrases_by_domain[domain].most_common(40)]
        for domain in config.TAXONOMY
    }

    config.MINED_AUTHORITIES_JSON.write_text(json.dumps(authorities_out, indent=2))
    config.MINED_PHRASES_JSON.write_text(json.dumps(phrases_out, indent=2))
    config.MINED_REFERENCE_JSON.write_text(
        json.dumps(reference_lines_by_domain, indent=2)
    )

    print(f"Wrote mined authorities  -> {config.MINED_AUTHORITIES_JSON}")
    print(f"Wrote mined phrases      -> {config.MINED_PHRASES_JSON}")
    print(f"Wrote reference sample   -> {config.MINED_REFERENCE_JSON}")
    for domain in config.TAXONOMY:
        print(f"  {domain}: {len(authorities_out[domain])} authorities mined")


if __name__ == "__main__":
    main()
