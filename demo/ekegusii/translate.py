"""Dictionary-prompted Ekegusii translation -- the mechanism that produced this
project's best Ekegusii numbers (recall 0.90, chrF 54.8 on the full retrieval bank;
recall 0.878, chrF 49.2 using the agriculture-only training split alone, which is all
that's guaranteed available in a fresh clone of this repo -- see README.md in this
folder for exactly what's shipped vs optional).

Backend: any of the general-purpose LLM backends in `llm_backends.py` (Cohere,
AWS Bedrock, Azure OpenAI, or a custom OpenAI-compatible endpoint) -- bring your own
credentials, nothing hardcoded or shipped in this repo. The validated numbers above
were measured against Cohere's `command-a-03-2025`; the other backends are
functionally equivalent call paths this project also tested, offered as options in
case Cohere's free tier is unavailable to you. `app.py` collects a backend choice +
credentials interactively and passes them into `EkegusiiTranslator.translate()` per
call; this module never reads credentials from the environment directly.

Three data dependencies, all optional except the first:
  - `data/splits/agriculture/ekegusii_train.csv` (repo root) -- 811-row agriculture
    PSA training split. Already committed to this repo; always available.
  - Ekegusii dictionary CSV (`data/dictionaries/` in this folder) -- licensed,
    paid-access material, NOT shipped. Required for dictionary hints; without it,
    `EkegusiiTranslator` can't be constructed (see `lexicon_lookup.MissingDictionaryError`).
  - Bible parallel corpus + extra PSA corpus (`data/optional_corpora/` in this
    folder) -- both usage-restricted at their source (see that folder's README),
    NOT shipped. Widen the retrieval bank beyond agriculture-only phrasing when
    present; silently skipped (with a note surfaced to the caller) when absent.
"""

import csv
import os
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from lexicon_lookup import load_lexicon, is_degenerate
from semantic_fallback import build_lemma_index, find_constraints_with_fallback
from entity_protection import find_protected_entities, format_protected_entities_block
from llm_backends import call_llm, NO_ECHO_INSTRUCTION

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]

TRAIN_CSV = REPO_ROOT / "data" / "splits" / "agriculture" / "ekegusii_train.csv"
BIBLE_CSV = Path(os.environ.get(
    "EKEGUSII_BIBLE_CORPUS_PATH", HERE / "data" / "optional_corpora" / "ekegusii_kjv_aligned.csv"
))
EKEGUSII_CORPUS_CSV = Path(os.environ.get(
    "EKEGUSII_EXTRA_CORPUS_PATH", HERE / "data" / "optional_corpora" / "psa_en_guz_parallel.csv"
))

N_FEWSHOT = 3
N_HINTS = 6
MAX_RETRIES_ON_DEGENERATE = 2


def translate_with_retry(build_messages_fn, english, backend_name, credentials):
    messages = build_messages_fn(english, reinforce=False)
    out = call_llm(backend_name, credentials, messages, temperature=0)
    retries_used = 0
    while is_degenerate(out, en_source=english) and retries_used < MAX_RETRIES_ON_DEGENERATE:
        retries_used += 1
        messages = build_messages_fn(english, reinforce=True)
        out = call_llm(backend_name, credentials, messages, temperature=min(0.4 * retries_used, 1.0))
    return out, retries_used


def load_train_bank():
    if not TRAIN_CSV.is_file():
        raise RuntimeError(
            f"{TRAIN_CSV} not found -- this file ships with the repo; if it's "
            "missing your clone is incomplete."
        )
    with open(TRAIN_CSV, encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["English"].strip() and r["Ekegusii"].strip()]
    return rows


def load_bible_bank():
    if not BIBLE_CSV.is_file():
        return []
    rows = []
    with open(BIBLE_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            en, guz = row["text_en"].strip(), row["text_guz"].strip()
            if en and guz:
                rows.append({"English": en, "Ekegusii": guz})
    return rows


def load_ekegusii_corpus_bank():
    if not EKEGUSII_CORPUS_CSV.is_file():
        return []
    rows = []
    with open(EKEGUSII_CORPUS_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            en, guz = row["en"].strip(), row["guz"].strip()
            if en and guz:
                rows.append({"English": en, "Ekegusii": guz})
    return rows


def build_retriever(rows):
    texts = [r["English"] for r in rows]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(texts)
    return vectorizer, matrix


def retrieve_fewshot(english_sentence, rows, vectorizer, matrix, k=N_FEWSHOT):
    query_vec = vectorizer.transform([english_sentence])
    sims = cosine_similarity(query_vec, matrix)[0]
    top_idx = sims.argsort()[::-1][:k]
    return [(rows[i]["English"], rows[i]["Ekegusii"]) for i in top_idx]


def build_dict_prompted_semantic_messages(english_sentence, lexicon, lemma_index, gloss_synsets,
                                           rows, vectorizer, matrix, reinforce=False):
    fewshot = retrieve_fewshot(english_sentence, rows, vectorizer, matrix)
    exact_hits, fallback_hits = find_constraints_with_fallback(
        english_sentence, lexicon, lemma_index, gloss_synsets, max_constraints=N_HINTS
    )

    sys_parts = [
        "You are translating English into Ekegusii (Ekegusii/Gusii), a Bantu language "
        "spoken in Kisii County, Kenya. You will be given real example translations in "
        "this domain and a glossary of English->Ekegusii word mappings for the specific "
        "sentence you must translate next. " + NO_ECHO_INSTRUCTION,
    ]
    sys_parts.append("\nExamples:")
    for en, guz in fewshot:
        sys_parts.append(f'EN: {en}\nGUZ: {guz}')

    glossary_lines = [f"{gloss} -> {guz_word}" for gloss, guz_word in exact_hits]
    glossary_lines += [f"{gloss} -> {guz_word}" for tier, gloss, guz_word, note in fallback_hits if tier == "lemma"]
    approx_lines = [
        f"{note} (approximately like '{gloss}') -> {guz_word}"
        for tier, gloss, guz_word, note in fallback_hits if tier == "synonym"
    ]
    if glossary_lines:
        sys_parts.append("\nGlossary for the next sentence (English -> Ekegusii):")
        sys_parts.append("; ".join(glossary_lines))
    if approx_lines:
        sys_parts.append(
            "\nApproximate/inferred word matches for the next sentence (lower "
            "confidence -- use your own judgement about whether these fit):"
        )
        sys_parts.append("; ".join(approx_lines))

    protected_entities = find_protected_entities(english_sentence)
    if protected_entities:
        sys_parts.append(format_protected_entities_block(protected_entities))

    user_content = f'Translate to Ekegusii: "{english_sentence}"'
    if reinforce:
        user_content += (
            "\n\n(Your previous attempt was invalid -- it was not a real Ekegusii "
            "sentence, or it repeated the instructions/glossary/English text instead "
            "of translating. Try again. Output ONLY the Ekegusii translation.)"
        )

    messages = [
        {"role": "system", "content": "\n".join(sys_parts)},
        {"role": "user", "content": user_content},
    ]
    return messages, exact_hits, fallback_hits


class EkegusiiTranslator:
    def __init__(self):
        self.lexicon = load_lexicon()
        self.lemma_index, self.gloss_synsets = build_lemma_index(self.lexicon)

        train_rows = load_train_bank()
        bible_rows = load_bible_bank()
        corpus_rows = load_ekegusii_corpus_bank()
        self.retrieval_rows = train_rows + bible_rows + corpus_rows
        self.vectorizer, self.matrix = build_retriever(self.retrieval_rows)

        self.bank_sources = {
            "agriculture_train": len(train_rows),
            "bible_corpus": len(bible_rows),
            "extra_corpus": len(corpus_rows),
        }

    def translate(self, english_sentence, backend_name, credentials):
        english_sentence = english_sentence.strip()
        if not english_sentence:
            return {"translation": "", "hints": [], "fallback_hints": [], "retries_used": 0, "uncertain": False}

        def build_messages(e, reinforce):
            return build_dict_prompted_semantic_messages(
                e, self.lexicon, self.lemma_index, self.gloss_synsets,
                self.retrieval_rows, self.vectorizer, self.matrix, reinforce,
            )[0]

        output, retries_used = translate_with_retry(build_messages, english_sentence, backend_name, credentials)
        constraints, fallback_hits = find_constraints_with_fallback(
            english_sentence, self.lexicon, self.lemma_index, self.gloss_synsets, max_constraints=6
        )
        return {
            "translation": output,
            "hints": constraints,
            "fallback_hints": fallback_hits,
            "retries_used": retries_used,
            "uncertain": is_degenerate(output, en_source=english_sentence),
        }
