"""
generate.py
-----------
Step 3 of the pipeline.

Combines:
  - authored sentence TEMPLATES (templates.py) per Domain/Sub-Category
  - real Kenyan issuing authorities mined from your scraped CSV +
    curated domain-correct authorities (data/mined/authorities.json)
  - generic slots from config.py (Kenyan counties, months, contact channels)

...into a large pool of unique, realistic-looking synthetic Kenyan PSAs,
targeting PER_SUBCATEGORY_TARGET rows per sub-category (config.py),
~70,000 rows overall across the 25 sub-categories.

Randomised combination + a "seen" set guarantees no exact duplicate
sentence is produced during generation itself (a second, stricter
near-duplicate pass happens later in dedup.py).
"""

import json
import random
import re

import config
from templates import TEMPLATES

random.seed(42)


def load_authorities() -> dict:
    return json.loads(config.MINED_AUTHORITIES_JSON.read_text())


def fill_template(template: str, authority: str, vocab: dict) -> str:
    slots = {
        "authority": authority,
        "county": random.choice(config.COUNTIES),
        "month": random.choice(config.MONTHS),
    }
    # add subcategory-specific vocab slots present in this template
    for key, options in vocab.items():
        if "{" + key + "}" in template:
            slots[key] = random.choice(options)

    text = template.format(**slots)
    text = re.sub(r"\s+", " ", text).strip()
    if not text.endswith((".", "!", "?")):
        text += "."
    return text


def generate_for_subcategory(domain: str, subcat: str, authorities: list, target: int) -> list:
    spec = TEMPLATES[domain][subcat]
    templates = spec["templates"]
    vocab = spec["vocab"]

    seen = set()
    rows = []
    max_attempts = target * 25  # safety valve against infinite loops
    attempts = 0

    while len(rows) < target and attempts < max_attempts:
        attempts += 1
        template = random.choice(templates)
        authority = random.choice(authorities)
        sentence = fill_template(template, authority, vocab)

        key = sentence.lower()
        if key in seen:
            continue
        seen.add(key)
        rows.append(sentence)

    return rows


def main():
    authorities_by_domain = load_authorities()
    all_rows = []
    counters = {domain: 1 for domain in config.TAXONOMY}

    for domain, subcats in config.TAXONOMY.items():
        prefix = config.DOMAIN_PREFIX[domain]
        authorities = authorities_by_domain.get(domain, [])
        if not authorities:
            authorities = ["Government of Kenya"]

        for subcat in subcats:
            rows = generate_for_subcategory(
                domain, subcat, authorities, config.PER_SUBCATEGORY_TARGET
            )
            print(f"{domain} / {subcat}: generated {len(rows)} rows")

            for text in rows:
                psa_id = f"{prefix}_{counters[domain]:05d}"
                counters[domain] += 1
                all_rows.append(
                    {
                        "PSA_ID": psa_id,
                        "Domain": domain,
                        "English": text,
                        "_subcategory": subcat,  # internal only, used for dedup blocking
                    }
                )

    print(f"\nTotal generated (pre-dedup pass): {len(all_rows)}")

    out_path = config.DATA_DIR / "generated_raw.json"
    out_path.write_text(json.dumps(all_rows, indent=2))
    print(f"Wrote raw generated rows -> {out_path}")


if __name__ == "__main__":
    main()
