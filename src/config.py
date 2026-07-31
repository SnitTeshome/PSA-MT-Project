"""
config.py
---------
Central configuration: file paths, the official Domain/Sub-Category taxonomy
(matching PSA_Categories_topics.pdf exactly), Kenyan counties, contact
shortcodes, and generation targets.

Keeping all of this in one module means every other module (mining,
generation, dedup, quality-check) reads from a single source of truth.
"""

from pathlib import Path

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
MINED_DIR = DATA_DIR / "mined"
OUTPUT_DIR = ROOT_DIR / "output"

RAW_SOURCE_CSV = DATA_DIR /"clean_real_with_quality_labels.csv"
MINED_AUTHORITIES_JSON = MINED_DIR / "authorities.json"
MINED_PHRASES_JSON = MINED_DIR / "phrases.json"
MINED_REFERENCE_JSON = MINED_DIR / "reference_lines.json"

FINAL_CSV = OUTPUT_DIR / "kenyan_psa_synthetic_50000.csv"
QUALITY_REPORT = OUTPUT_DIR / "quality_report.txt"

for d in (DATA_DIR, MINED_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# Official taxonomy (from PSA_Categories_topics.pdf)
# ----------------------------------------------------------------------
TAXONOMY = {
    "Health": [
        "Disease Prevention and Control",
        "Maternal and Child Health",
        "Public Health Campaigns",
        "Mental Health Awareness",
        "Healthcare Access",
    ],
    "Agriculture": [
        "Crop Production",
        "Livestock Management",
        "Agribusiness and Market Access",
        "Sustainable Farming",
        "Agricultural Training",
    ],
    "Education": [
        "Access to Education",
        "Vocational Training",
        "Civic Education",
        "Educational Resources",
        "School Safety and Inclusion",
    ],
    "Security & Safety": [
        "Public Safety Awareness",
        "Crime Prevention",
        "National Security",
        "Gender-Based Violence",
        "Cybersecurity",
    ],
    "Governance": [
        "Anti-Corruption Initiatives",
        "Public Participation",
        "Elections and Voter Education",
        "Public Service Delivery",
        "Devolution and Local Governance",
    ],
}

DOMAIN_PREFIX = {
    "Health": "HEA",
    "Agriculture": "AGR",
    "Education": "EDU",
    "Security & Safety": "SEC",
    "Governance": "GOV",
}

# ----------------------------------------------------------------------
# Generation target
# ----------------------------------------------------------------------
TOTAL_TARGET = 15000
N_DOMAINS = len(TAXONOMY)
N_SUBCATS_PER_DOMAIN = 5
N_SUBCATS_TOTAL = N_DOMAINS * N_SUBCATS_PER_DOMAIN  # 25
PER_SUBCATEGORY_TARGET = TOTAL_TARGET // N_SUBCATS_TOTAL  # 2800

# ----------------------------------------------------------------------
# Kenyan counties (all 47) -- used to localize generated PSAs
# ----------------------------------------------------------------------
COUNTIES = [
    "Mombasa", "Kwale", "Kilifi", "Tana River", "Lamu", "Taita-Taveta",
    "Garissa", "Wajir", "Mandera", "Marsabit", "Isiolo", "Meru",
    "Tharaka-Nithi", "Embu", "Kitui", "Machakos", "Makueni", "Nyandarua",
    "Nyeri", "Kirinyaga", "Murang'a", "Kiambu", "Turkana", "West Pokot",
    "Samburu", "Trans Nzoia", "Uasin Gishu", "Elgeyo-Marakwet", "Nandi",
    "Baringo", "Laikipia", "Nakuru", "Narok", "Kajiado", "Kericho",
    "Bomet", "Kakamega", "Vihiga", "Bungoma", "Busia", "Siaya",
    "Kisumu", "Homa Bay", "Migori", "Kisii", "Nyamira", "Nairobi",
]

# Generic Kenyan-style contact / reporting channels used across PSAs
SMS_SHORTCODES = ["21094", "1195", "1199", "22105", "40015", "356"]
TOLLFREE_LINES = ["1-500-100", "0800-720-627", "0800-721-231", "0800-730-999"]
USSD_CODES = ["*271#", "*544#", "*811#", "*248#"]
WEBSITES = [
    "www.health.go.ke", "www.kilimo.go.ke", "www.education.go.ke",
    "www.ntsa.go.ke", "www.iebc.or.ke", "www.eacc.go.ke",
    "www.ecitizen.go.ke", "www.interior.go.ke",
]

YEARS = [2026]
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
