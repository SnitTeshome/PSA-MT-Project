"""Kenya-county + institution-acronym entity protection -- closed-vocabulary NER
(not general NER). Getting Kenyan county names and ALL-CAPS institution acronyms
reproduced verbatim is a fixed, enumerable lookup rather than a model-dependent
judgment call, and both appear often in PSA-style sentences.
"""

import re

KENYA_COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita-Taveta", "Garissa",
    "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru", "Tharaka-Nithi", "Embu",
    "Kitui", "Machakos", "Makueni", "Nyandarua", "Nyeri", "Kirinyaga", "Murang'a",
    "Kiambu", "Turkana", "West Pokot", "Samburu", "Trans Nzoia", "Uasin Gishu",
    "Elgeyo-Marakwet", "Nandi", "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado",
    "Kericho", "Bomet", "Kakamega", "Vihiga", "Bungoma", "Busia", "Siaya", "Kisumu",
    "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi",
]
_COUNTY_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(c) for c in sorted(KENYA_COUNTIES, key=len, reverse=True)) + r")\b"
)
_ACRONYM_PATTERN = re.compile(r"\b[A-Z]{2,6}\b")


def find_protected_entities(english_sentence):
    """De-duplicated, order-preserving list of substrings the model should reproduce
    verbatim: Kenyan county names + ALL-CAPS institution acronyms found in the
    sentence."""
    found, seen = [], set()
    for m in _COUNTY_PATTERN.finditer(english_sentence):
        val = m.group(1)
        if val not in seen:
            seen.add(val)
            found.append(val)
    for m in _ACRONYM_PATTERN.finditer(english_sentence):
        val = m.group(0)
        if val not in seen:
            seen.add(val)
            found.append(val)
    return found


def format_protected_entities_block(entities):
    if not entities:
        return ""
    joined = ", ".join(f'"{e}"' for e in entities)
    return (
        f"\n\nThe following names/acronyms must be reproduced EXACTLY as given, "
        f"character-for-character, do not translate, abbreviate, or alter their "
        f"spelling in any way: {joined}."
    )
