"""Lemmatization + WordNet-synonym fallback for dictionary hint lookup.

`find_source_constraints()` in `lexicon_lookup.py` is exact-substring matching only,
which misses same-word form variants ("to help" in the dictionary vs "help" in the
input) and true synonym gaps ("purchase" when only "buy" is dictionary-covered). This
adds two fallback tiers, tried only for content words the exact match didn't already
cover:

  1. lemma tier: lemmatize the input word and check it against a lemma-indexed
     version of the dictionary's single-word glosses. Pure morphological
     normalization, same confidence as an exact match.
  2. synonym tier: only tried if the lemma tier also misses. Requires the query
     word's top-2 WordNet synsets to overlap with the dictionary gloss word's OWN
     top-2 synsets -- both sides restricted, not just one (naive matching lets
     "help" match "aids" via a shared but non-primary sense, which in this
     PSA-domain dictionary means the HIV/AIDS disease, not "assistance"). Tagged as
     lower-confidence in the prompt.

Scoped to single-word dictionary glosses only.
"""

from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

from lexicon_lookup import STOPWORDS, tokenize_en_simple

_lemmatizer = WordNetLemmatizer()
_WN_POS = ("v", "n", "a", "r")
_TOP_N_SYNSETS = 2


def _lemmas_of(word):
    return {_lemmatizer.lemmatize(word, pos=p) for p in _WN_POS}


def build_lemma_index(lexicon):
    """Returns (lemma_index, gloss_synsets):
      - lemma_index: lemma -> (gloss, guz_word), single-word glosses only.
      - gloss_synsets: [(gloss, guz_word, top-2-synsets-of-gloss), ...] for the
        synonym tier's both-sides-restricted overlap check."""
    lemma_index = {}
    gloss_synsets = []
    seen_gloss_words = set()
    for gloss, guz_word, pos in lexicon:
        if gloss.startswith("to "):
            gloss = gloss[3:]
        if " " in gloss or gloss in STOPWORDS or len(gloss) < 3:
            continue
        for lemma in _lemmas_of(gloss):
            lemma_index.setdefault(lemma, (gloss, guz_word))
        lemma_index.setdefault(gloss, (gloss, guz_word))
        if gloss not in seen_gloss_words:
            seen_gloss_words.add(gloss)
            top2 = set(wn.synsets(gloss)[:_TOP_N_SYNSETS])
            if top2:
                gloss_synsets.append((gloss, guz_word, top2))
    return lemma_index, gloss_synsets


def find_semantic_hint(word, lemma_index, gloss_synsets):
    """Returns (tier, gloss, guz_word, note) or None. tier is "lemma" or "synonym"."""
    word = word.lower()
    for lemma in _lemmas_of(word):
        if lemma in lemma_index:
            gloss, guz_word = lemma_index[lemma]
            return ("lemma", gloss, guz_word, word)

    word_top2 = set(wn.synsets(word)[:_TOP_N_SYNSETS])
    if word_top2:
        for gloss, guz_word, gloss_top2 in gloss_synsets:
            if gloss == word:
                continue
            if word_top2 & gloss_top2:
                return ("synonym", gloss, guz_word, word)
    return None


def find_constraints_with_fallback(english_sentence, lexicon, lemma_index, gloss_synsets, max_constraints=6):
    """Returns (exact_hits, fallback_hits). exact_hits is find_source_constraints()'s
    unchanged (gloss, guz_word) list. fallback_hits is a list of
    (tier, gloss, guz_word, matched_word_or_synonym) for content words the exact
    match left uncovered, up to the remaining max_constraints budget."""
    from lexicon_lookup import find_source_constraints

    exact_hits = find_source_constraints(english_sentence, lexicon, max_constraints)
    seen_glosses = {g for g, _ in exact_hits}
    matched_words = {w for g, _ in exact_hits for w in g.split()}

    remaining = max_constraints - len(exact_hits)
    fallback_hits = []
    if remaining > 0:
        for tok in tokenize_en_simple(english_sentence):
            if len(fallback_hits) >= remaining:
                break
            if tok in STOPWORDS or len(tok) < 3 or tok in matched_words:
                continue
            hit = find_semantic_hint(tok, lemma_index, gloss_synsets)
            if hit and hit[1] not in seen_glosses:
                fallback_hits.append(hit)
                seen_glosses.add(hit[1])
    return exact_hits, fallback_hits
