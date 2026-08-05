"""Ekegusii translation demo -- also the setup/onboarding UI for this folder.

Rather than a separate shell setup script, this app itself tells you what's
installed, what's missing, and what your options are, then asks for explicit
confirmation before it ever sends a credential anywhere. See README.md for the
one-time `pip install` step this can't do for itself.
"""

from pathlib import Path

import streamlit as st

from lexicon_lookup import LEXICON_PATH, MissingDictionaryError
from llm_backends import BACKENDS
from kaggle_fetch import fetch_dataset, KaggleFetchError

KAGGLE_TARGETS = {
    "Dictionary (data/dictionaries/)": LEXICON_PATH.parent,
    "Bible parallel corpus (data/optional_corpora/)": Path(__file__).resolve().parent / "data" / "optional_corpora",
    "Extra PSA corpus (data/optional_corpora/)": Path(__file__).resolve().parent / "data" / "optional_corpora",
}

st.set_page_config(page_title="Kenyan PSA Translator", page_icon="\U0001F30D")

NLLB_DIRECTIONS = {
    "English -> Kiswahili  (chrF 74.7 -- NLLB-200 zero-shot)": {
        "src": "English", "tgt": "Kiswahili", "src_code": "eng_Latn", "tgt_code": "swh_Latn",
    },
    "Kiswahili -> English  (chrF 67.8, BLEU 46.4 -- NLLB-200 zero-shot)": {
        "src": "Kiswahili", "tgt": "English", "src_code": "swh_Latn", "tgt_code": "eng_Latn",
    },
    "English -> Somali  (chrF 83.1 -- NLLB-200, best backend tested)": {
        "src": "English", "tgt": "Somali", "src_code": "eng_Latn", "tgt_code": "som_Latn",
    },
    "English -> Dholuo  (chrF 53.7 -- NLLB-200, unambiguous winner)": {
        "src": "English", "tgt": "Dholuo", "src_code": "eng_Latn", "tgt_code": "luo_Latn",
    },
}
EKEGUSII_DIRECTION = "English -> Ekegusii  (chrF 54.8, recall 0.90 -- dictionary-prompted)"

NLLB_MODEL_NAME = "facebook/nllb-200-distilled-600M"


@st.cache_resource
def get_nllb_model():
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(NLLB_MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(NLLB_MODEL_NAME)
    return tokenizer, model


def translate_nllb(text, src_code, tgt_code):
    tokenizer, model = get_nllb_model()
    tokenizer.src_lang = src_code
    forced_bos = tokenizer.convert_tokens_to_ids(tgt_code)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    generated = model.generate(
        **inputs, forced_bos_token_id=forced_bos, max_length=128,
        no_repeat_ngram_size=3, num_beams=4,
    )
    return tokenizer.batch_decode(generated, skip_special_tokens=True)[0]


@st.cache_resource
def get_ekegusii_translator():
    from translate import EkegusiiTranslator
    return EkegusiiTranslator()


def dictionary_available():
    return LEXICON_PATH.is_file()


st.title("Kenyan PSA Translator")

if "kaggle_fetch_result" in st.session_state:
    st.success(st.session_state.pop("kaggle_fetch_result"))

st.caption(
    "PSA-MT Project demo. Only translation directions with a validated result in "
    "this project's own evaluation are offered -- not a full language matrix. See "
    "docs/results_summary.md in the repo root for the full comparison."
)

with st.expander("Setup -- what this needs and what it installs", expanded="ekegusii_backend" not in st.session_state):
    st.markdown(
        "**Packages installed by `pip install -r requirements.txt`** in this folder: "
        "`streamlit`, `scikit-learn`, `nltk`, `requests` (dictionary-prompted "
        "Ekegusii mechanism), `torch` (CPU build) + `transformers` + `sentencepiece` "
        "(NLLB-200, for the other four directions). Nothing exotic, no GPU packages."
    )

    st.markdown("---")
    st.markdown("**Ekegusii dictionary data**")
    if dictionary_available():
        st.success(f"Found at `{LEXICON_PATH}`.")
    else:
        st.warning(
            "Not found. This is licensed, paid-access material and isn't included "
            "in this repo -- see `data/dictionaries/README.md` for how to obtain "
            "your own copy and where to place it. **Without it, the Ekegusii "
            "direction is unavailable** (there's no lower-quality fallback mode for "
            "this specific mechanism -- the dictionary hints are the mechanism); "
            "the other four directions below don't need it and work regardless."
        )

    with st.expander("Have your own copy in a private Kaggle dataset? Fetch it from there instead"):
        st.caption(
            "Bring-your-own-credential, same as the LLM backend below -- your Kaggle "
            "username/key are set as environment variables for this process only, "
            "never written to disk."
        )
        with st.form("kaggle_fetch_form"):
            kaggle_target_label = st.selectbox("What are you fetching", list(KAGGLE_TARGETS.keys()))
            kaggle_username = st.text_input("Kaggle username")
            kaggle_key = st.text_input("Kaggle API key", type="password")
            kaggle_dataset = st.text_input(
                "Dataset identifier", placeholder="yourname/your-dataset-slug",
                help="From the dataset's Kaggle URL: kaggle.com/datasets/<this part>",
            )
            kaggle_consent = st.checkbox(
                "I understand this credential will be sent only to Kaggle's API to "
                "download this dataset, for this session only."
            )
            kaggle_submitted = st.form_submit_button("Fetch and continue")

        if kaggle_submitted:
            if not kaggle_consent:
                st.error("Please check the consent box before fetching.")
            else:
                target_dir = KAGGLE_TARGETS[kaggle_target_label]
                try:
                    with st.spinner(f"Downloading {kaggle_dataset!r} from Kaggle..."):
                        files = fetch_dataset(kaggle_username, kaggle_key, kaggle_dataset, target_dir)
                except KaggleFetchError as e:
                    st.error(str(e))
                else:
                    st.session_state["kaggle_fetch_result"] = (
                        f"Downloaded. Files now in `{target_dir}`: {', '.join(files) or '(none found)'}"
                    )
                    st.rerun()

    st.markdown("---")
    st.markdown("**LLM backend for the Ekegusii direction only** (the other four directions run "
                "entirely local, no API key needed)")
    st.caption(
        "Bring your own credentials -- nothing is stored to disk, only kept in this "
        "browser session's memory, and only sent to the provider you pick below."
    )

    backend_options = list(BACKENDS.keys())
    backend_labels = {k: v["label"] for k, v in BACKENDS.items()}
    chosen_backend = st.selectbox(
        "Backend", backend_options, format_func=lambda k: backend_labels[k],
        index=backend_options.index(st.session_state.get("ekegusii_backend", backend_options[0])),
    )
    st.info(BACKENDS[chosen_backend]["help"])
    if "warning" in BACKENDS[chosen_backend]:
        st.warning(BACKENDS[chosen_backend]["warning"])

    creds = {}
    backend_defaults = BACKENDS[chosen_backend].get("defaults", {})
    with st.form("credentials_form"):
        for field_key, field_label, required in BACKENDS[chosen_backend]["fields"]:
            is_secret = "key" in field_key or "secret" in field_key
            default_value = st.session_state.get(
                f"ekegusii_cred_{chosen_backend}_{field_key}", backend_defaults.get(field_key, "")
            )
            creds[field_key] = st.text_input(
                field_label + (" *" if required else " (optional)"),
                type="password" if is_secret else "default",
                value=default_value,
            )
        consent = st.checkbox(
            f"I understand this credential will be sent only to {BACKENDS[chosen_backend]['label']} "
            "to perform translation requests, for this session only."
        )
        submitted = st.form_submit_button("Save and use this backend")

    if submitted:
        missing = [lbl for key, lbl, req in BACKENDS[chosen_backend]["fields"] if req and not creds.get(key)]
        if missing:
            st.error(f"Missing required field(s): {', '.join(missing)}.")
        elif not consent:
            st.error("Please check the consent box before saving -- this app won't send a credential anywhere without it.")
        else:
            st.session_state["ekegusii_backend"] = chosen_backend
            st.session_state["ekegusii_credentials"] = creds
            for k, v in creds.items():
                st.session_state[f"ekegusii_cred_{chosen_backend}_{k}"] = v
            st.success("Saved for this session.")

backend_ready = "ekegusii_backend" in st.session_state and "ekegusii_credentials" in st.session_state
ekegusii_ready = backend_ready and dictionary_available()

direction_options = list(NLLB_DIRECTIONS.keys())
if ekegusii_ready:
    direction_options = [EKEGUSII_DIRECTION] + direction_options
elif not dictionary_available():
    st.info("Ekegusii direction hidden until a dictionary file is found (see Setup above).")
elif not backend_ready:
    st.info("Ekegusii direction hidden until you save an LLM backend + credentials (see Setup above).")

direction_label = st.selectbox("Translation direction", direction_options)

if direction_label == EKEGUSII_DIRECTION:
    src, tgt = "English", "Ekegusii"
else:
    direction = NLLB_DIRECTIONS[direction_label]
    src, tgt = direction["src"], direction["tgt"]

text = st.text_area(
    f"{src} sentence", height=100, placeholder=f"Type a {src} sentence to translate...",
)

if st.button("Translate", type="primary"):
    if not text.strip():
        st.warning("Enter a sentence first.")
    elif direction_label == EKEGUSII_DIRECTION:
        try:
            with st.spinner("Translating..."):
                translator = get_ekegusii_translator()
                result = translator.translate(
                    text, st.session_state["ekegusii_backend"], st.session_state["ekegusii_credentials"]
                )
        except MissingDictionaryError as e:
            st.error(str(e))
        else:
            st.subheader(f"{tgt} translation")
            st.write(result["translation"])

            if result["uncertain"]:
                st.warning("This output may be unreliable (failed the automatic quality check even after retries).")

            if result["hints"]:
                with st.expander(f"Dictionary words used ({len(result['hints'])})"):
                    for gloss, guz_word in result["hints"]:
                        st.write(f"- **{gloss}** -> {guz_word}")

            if result["fallback_hints"]:
                with st.expander(f"Inferred word matches ({len(result['fallback_hints'])})"):
                    for tier, gloss, guz_word, note in result["fallback_hints"]:
                        if tier == "lemma":
                            st.write(f"- **{note}** -> {guz_word} (same word, different form)")
                        else:
                            st.write(f"- **{note}** ~ *{gloss}* -> {guz_word} (approximate match)")
    else:
        with st.spinner("Translating (NLLB-200, local CPU inference -- may take a few seconds)..."):
            translation = translate_nllb(text, direction["src_code"], direction["tgt_code"])
        st.subheader(f"{tgt} translation")
        st.write(translation)
