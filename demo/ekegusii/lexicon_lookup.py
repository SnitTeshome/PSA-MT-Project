"""EN->GUZ dictionary lookup + morphology-tolerant matching.

The dictionary CSV itself is NOT shipped in this repo -- it's licensed, paid-access
material (see `data/dictionaries/README.md`). This module only ships the lookup code;
`load_lexicon()` raises `MissingDictionaryError` with setup instructions if the file
isn't found, rather than a bare FileNotFoundError, so callers (the Streamlit app) can
catch it and show a clear setup screen instead of crashing.
"""

import csv
import os
import re
from collections import Counter
from pathlib import Path

DEFAULT_LEXICON_PATH = Path(__file__).resolve().parent / "data" / "dictionaries" / "enchengeria_en_guz_lexicon.csv"
LEXICON_PATH = Path(os.environ.get("EKEGUSII_LEXICON_PATH", DEFAULT_LEXICON_PATH))

PREFIXES = sorted([
    "aba", "omo", "eme", "ama", "eri", "ebi", "eke", "obo", "ase", "ere",
    "chi", "aka", "oko", "ogo", "ago", "en", "aga", "ente", "ege", "aina",
    "ino", "aho", "aro",
], key=len, reverse=True)

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with",
    "is", "are", "was", "were", "be", "been", "by", "at", "as", "it", "its",
    "this", "that", "these", "those", "their", "his", "her", "our", "your",
}


class MissingDictionaryError(RuntimeError):
    pass


def strip_prefix(word):
    for p in PREFIXES:
        if word.startswith(p) and len(word) - len(p) >= 3:
            return word[len(p):]
    return word


def load_lexicon(path=None):
    """english_gloss (lowercased) -> list of (guz_word, english_pos), longest gloss
    first so phrase matches are tried before single-word ones."""
    path = Path(path) if path else LEXICON_PATH
    if not path.is_file():
        raise MissingDictionaryError(
            f"Ekegusii dictionary not found at {path}. This file is licensed, "
            "paid-access material and isn't included in this repo -- see "
            "data/dictionaries/README.md for how to obtain your own copy and where "
            "to place it (or set the EKEGUSII_LEXICON_PATH environment variable to "
            "point elsewhere)."
        )
    entries = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            gloss = row["english_gloss"].strip().lower()
            word = row["word"].strip().lower().strip(".,;:!?")
            if gloss and word and "|" not in word:
                entries.append((gloss, word, row["english_pos"].strip()))
    entries.sort(key=lambda e: len(e[0]), reverse=True)
    return entries


def find_source_constraints(english_sentence, lexicon, max_constraints=6):
    """Greedy longest-match-first scan of the English sentence against dictionary
    glosses. Returns a list of (matched_english_span, guz_word) pairs, skipping
    stopword-only glosses and not double-covering the same span twice."""
    text = english_sentence.lower()
    covered = [False] * len(text)
    found = []
    for gloss, guz_word, pos in lexicon:
        if gloss in STOPWORDS or len(gloss) < 3:
            continue
        start = 0
        while True:
            idx = text.find(gloss, start)
            if idx == -1:
                break
            end = idx + len(gloss)
            left_ok = idx == 0 or not text[idx - 1].isalpha()
            right_ok = end == len(text) or not text[end].isalpha()
            if left_ok and right_ok and not any(covered[idx:end]):
                found.append((gloss, guz_word))
                for i in range(idx, end):
                    covered[i] = True
                break
            start = idx + 1
        if len(found) >= max_constraints:
            break
    return found


def tokenize_guz(text):
    text = text.lower()
    return re.findall(r"[a-z][a-z']*[a-z]|[a-z]", text)


def tokenize_en_simple(text):
    return re.findall(r"[a-z][a-z'-]*", text.lower())


def _char_trigrams(text):
    t = re.sub(r"\s+", " ", text.lower())
    return [t[i:i + 3] for i in range(len(t) - 2)]


def is_degenerate(text, en_source=None, min_type_token_ratio=0.45,
                   max_trigram_repeat_ratio=0.35, max_en_copy_ratio=0.5,
                   max_prefix_collapse_ratio=0.30):
    """Degeneration/failure detector: (1) near-repeat gibberish via character-trigram
    repetition, (2) mode-collapse onto similar-but-not-identical fragments sharing a
    short prefix, (3) the model copying the English source through almost unchanged
    instead of translating."""
    tokens = tokenize_guz(text)
    if len(tokens) >= 4 and len(set(tokens)) / len(tokens) < min_type_token_ratio:
        return True

    trigrams = _char_trigrams(text)
    if len(trigrams) >= 12:
        counts = Counter(trigrams)
        most_common = counts.most_common(1)[0][1]
        if most_common / len(trigrams) > max_trigram_repeat_ratio:
            return True

    long_tokens = [t for t in tokens if len(t) >= 4]
    if len(long_tokens) >= 5:
        prefix_counts = Counter(t[:4] for t in long_tokens)
        if prefix_counts.most_common(1)[0][1] / len(long_tokens) > max_prefix_collapse_ratio:
            return True

    if en_source:
        en_words = set(tokenize_en_simple(en_source))
        out_words = set(tokenize_en_simple(text))
        if en_words and len(out_words & en_words) / len(en_words) > max_en_copy_ratio:
            return True

    return False


def content_word_recall(generated_or_reference_text, expected_guz_words):
    """Root-stripped presence check: of the expected GUZ words, how many appear --
    exactly or via shared root after prefix-stripping -- anywhere in the given
    Ekegusii text."""
    if not expected_guz_words:
        return None, 0, 0
    tokens = set(tokenize_guz(generated_or_reference_text))
    token_roots = {strip_prefix(t) for t in tokens}
    hit = 0
    for w in expected_guz_words:
        w_root = strip_prefix(w)
        if w in tokens or w_root in token_roots or any(w_root in t or t in w for t in tokens if len(t) > 3):
            hit += 1
    return hit / len(expected_guz_words), hit, len(expected_guz_words)
