"""Language-detection QA gate for a domain PSA CSV, using Azure Text Analytics.

Complements validate_psa_csv.py's structural checks (schema, IDs, duplicates) with a
confidence-scored language check on the actual English/Kiswahili text — catching rows
where the "Kiswahili" column is actually code-switched, mislabeled, or not Swahili at
all before they're promoted/committed. This is a QA/verification step only: it never
generates or fills in translation text (the project's hard rule is no invented
translations) — it only flags mismatches for a human to look at.

Requires an Azure Cognitive Services / Text Analytics resource (any tier, including the
free F0 tier). Set these two environment variables before running — get them from your
own Azure resource (portal.azure.com -> Cognitive Services -> Keys and Endpoint):

    export AZURE_TEXT_ANALYTICS_KEY=...
    export AZURE_TEXT_ANALYTICS_ENDPOINT=...

Usage:
    python scripts/qa_azure_language_check.py data/raw/agriculture/agriculture_psas.csv
"""

import os
import sys

import pandas as pd

try:
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
except ImportError:
    sys.exit("azure-ai-textanalytics not installed — pip install azure-ai-textanalytics")

EXPECTED = {"English": "en", "Kiswahili": "sw"}
CONFIDENCE_FLOOR = 0.80  # below this, flag even a "correct" language call for a human look


def get_client() -> "TextAnalyticsClient":
    key = os.environ.get("AZURE_TEXT_ANALYTICS_KEY")
    endpoint = os.environ.get("AZURE_TEXT_ANALYTICS_ENDPOINT")
    if not key or not endpoint:
        sys.exit("Set AZURE_TEXT_ANALYTICS_KEY and AZURE_TEXT_ANALYTICS_ENDPOINT "
                 "(see this script's docstring) — no fallback, this check needs real credentials")
    return TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def main(path: str) -> None:
    df = pd.read_csv(path, dtype=str)
    client = get_client()

    flagged = 0
    for col, expected_code in EXPECTED.items():
        texts = df[col].fillna("")
        # rows with blank Kiswahili are English-only-source PSAs (lecturer-approved
        # 2026-07-14, see data/README.md) — nothing to language-check there
        mask = texts.str.strip() != ""
        if not mask.any():
            continue
        rows = df[mask]
        results = client.detect_language(documents=rows[col].tolist())
        for (_, row), result in zip(rows.iterrows(), results):
            if result.is_error:
                print(f"FLAG {row['PSA_ID']} [{col}]: Azure error — {result.error.message}")
                flagged += 1
                continue
            lang = result.primary_language
            if lang.iso6391_name != expected_code:
                print(f"FLAG {row['PSA_ID']} [{col}]: detected '{lang.iso6391_name}' "
                      f"(conf={lang.confidence_score:.2f}), expected '{expected_code}' — {row[col][:80]!r}")
                flagged += 1
            elif lang.confidence_score < CONFIDENCE_FLOOR:
                print(f"FLAG {row['PSA_ID']} [{col}]: low confidence ({lang.confidence_score:.2f}) "
                      f"for expected '{expected_code}' — {row[col][:80]!r}")
                flagged += 1

    print(f"\n{len(df)} rows checked, {flagged} flag(s)")
    if flagged == 0:
        print("OK: every row's English/Kiswahili text matches its expected language with high confidence")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/qa_azure_language_check.py <path-to-domain-csv>")
    main(sys.argv[1])
