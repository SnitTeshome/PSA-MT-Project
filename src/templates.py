"""
templates.py
------------
Step 2 building block: authored PSA sentence templates and slot-filling
vocabularies, one set per (Domain, Sub-Category) pair from the official
taxonomy in config.py.

Design notes
------------
- Each subcategory has multiple TEMPLATE strings with {placeholders}.
- Each placeholder is resolved from a vocabulary list specific to that
  subcategory (e.g. {disease}, {crop}, {exam}, {crime}, {right}), plus
  shared generic slots from config.py (county, date, contact channel,
  authority -- authority is injected at generation time from the mined
  + curated authority lists so it can vary independently of templates).
- Templates are phrased the way real Kenyan PSAs read: short, directive,
  advisory tone, sometimes with a call-to-action / contact channel.
- Generation combines: template x authority x topic-slot x county/date/
  contact -> the combinatorial space per subcategory is large enough to
  reach ~2,800 unique sentences without ever repeating a scraped sentence
  verbatim.
"""

TEMPLATES = {
    # ------------------------------------------------------------------
    "Health": {
        "Disease Prevention and Control": {
            "vocab": {
                "disease": [
                    "cholera", "malaria", "measles", "tuberculosis", "typhoid",
                    "HIV/AIDS", "cyclosporiasis", "Rift Valley Fever", "dengue fever",
                    "meningitis",
                ],
                "action": [
                    "seek immediate testing at the nearest health facility",
                    "complete the full recommended vaccination dose",
                    "report any suspected cases to community health volunteers",
                    "avoid contact with contaminated water sources",
                    "use insecticide-treated mosquito nets every night",
                ],
            },
            "templates": [
                "{authority} urges residents of {county} County to {action} following a rise in reported {disease} cases.",
                "{authority} reminds the public that free {disease} screening is available at all public health centres in {county} County this {month}.",
                "Notice: {authority} confirms a {disease} outbreak alert for {county} County. Residents are advised to {action}.",
                "{authority} calls on parents in {county} County to have children under five screened for {disease} during the {month} outreach.",
                "Public health advisory: {authority} warns of increased {disease} risk in {county} County and advises the public to {action}.",
            ],
        },
        "Maternal and Child Health": {
            "vocab": {
                "service": [
                    "free antenatal care", "childhood immunization", "skilled birth attendance",
                    "postnatal check-ups", "nutrition supplementation for infants",
                    "family planning counselling",
                ],
                "action": [
                    "visit their nearest maternity wing",
                    "register for the mother-and-child health card",
                    "attend the scheduled clinic day",
                    "bring their child for growth monitoring",
                ],
            },
            "templates": [
                "{authority} reminds expectant mothers in {county} County that access to {service} is free of charge at all public facilities.",
                "{authority} encourages mothers in {county} County to {action} to safeguard their child's health.",
                "Notice from {authority}: {service} clinics will run every {month} at designated health centres in {county} County.",
                "{authority} appeals to caregivers in {county} County to {action} as part of the {month} maternal health drive.",
            ],
        },
        "Public Health Campaigns": {
            "vocab": {
                "topic": [
                    "hand hygiene", "safe water storage", "proper sanitation",
                    "diabetes screening", "hypertension awareness", "tobacco control",
                    "food safety",
                ],
                "action": [
                    "wash hands with soap and clean water regularly",
                    "boil drinking water before use",
                    "attend the free community health screening",
                    "reduce salt and sugar intake",
                ],
            },
            "templates": [
                "{authority} launches a {month} awareness campaign on {topic} across {county} County.",
                "{authority} advises residents of {county} County to {action} to prevent the spread of preventable illness.",
                "Public notice: {authority} will host a free {topic} outreach in {county} County this {month}.",
                "{authority} reminds the public in {county} County about the importance of {topic} for household wellbeing.",
            ],
        },
        "Mental Health Awareness": {
            "vocab": {
                "topic": [
                    "stress management", "suicide prevention", "depression awareness",
                    "substance abuse recovery", "trauma counselling", "youth mental wellness",
                ],
                "action": [
                    "reach out to a trained counsellor",
                    "call the toll-free mental health helpline",
                    "attend a free community counselling session",
                    "encourage a friend in distress to seek help",
                ],
            },
            "templates": [
                "{authority} reminds the public that free {topic} support is available through county health facilities in {county} County.",
                "{authority} urges anyone struggling with their mental health in {county} County to {action}.",
                "Notice: {authority} will hold a {topic} forum in {county} County this {month}. All are welcome.",
                "{authority} encourages residents of {county} County not to suffer in silence and to {action}.",
            ],
        },
        "Healthcare Access": {
            "vocab": {
                "service": [
                    "SHA registration", "free medical camps", "NHIF/SHA claims support",
                    "outpatient services", "subsidised dialysis", "eye and dental camps",
                ],
                "action": [
                    "register for their health insurance cover",
                    "visit the nearest Huduma Centre for assistance",
                    "carry a valid national ID when seeking treatment",
                    "confirm their facility is accredited before visiting",
                ],
            },
            "templates": [
                "{authority} announces {service} for residents of {county} County starting this {month}.",
                "{authority} advises residents of {county} County to {action} to access subsidised healthcare.",
                "Notice: a free medical camp organised by {authority} will be held in {county} County this {month}.",
                "{authority} reminds the public in {county} County that access to {service} is now available at designated centres.",
            ],
        },
    },
    # ------------------------------------------------------------------
    "Agriculture": {
        "Crop Production": {
            "vocab": {
                "crop": [
                    "maize", "beans", "sorghum", "millet", "cassava", "sweet potatoes",
                    "coffee", "tea", "wheat", "rice",
                ],
                "action": [
                    "adopt certified drought-resistant seed varieties",
                    "apply recommended fertiliser rates before the rains",
                    "control fall armyworm early using approved pesticides",
                    "practice crop rotation to restore soil fertility",
                ],
            },
            "templates": [
                "{authority} advises farmers in {county} County to {action} ahead of the {month} planting season.",
                "{authority} warns {crop} farmers in {county} County of pest outbreaks and recommends timely intervention.",
                "Notice: {authority} will distribute certified {crop} seed to farmers in {county} County this {month}.",
                "{authority} urges {crop} growers in {county} County to {action} to improve yields this season.",
            ],
        },
        "Livestock Management": {
            "vocab": {
                "livestock": ["cattle", "goats", "sheep", "poultry", "dairy cows", "pigs"],
                "disease": ["foot and mouth disease", "Newcastle disease", "anthrax", "rabies", "lumpy skin disease"],
                "action": [
                    "vaccinate their animals at designated crush points",
                    "report sick animals to the nearest veterinary office",
                    "avoid moving livestock across county lines without a permit",
                ],
            },
            "templates": [
                "{authority} announces a free {disease} vaccination exercise for {livestock} in {county} County this {month}.",
                "{authority} urges {livestock} farmers in {county} County to {action} following reported {disease} cases.",
                "Notice: {authority} restricts movement of {livestock} in {county} County due to a {disease} outbreak.",
                "{authority} reminds livestock keepers in {county} County to {action} to protect herd health.",
            ],
        },
        "Agribusiness and Market Access": {
            "vocab": {
                "product": ["maize", "milk", "coffee", "avocado", "horticultural produce", "tea", "fish"],
                "action": [
                    "register with a certified cooperative society",
                    "sell produce only through licensed buyers",
                    "take advantage of the guaranteed minimum price",
                    "attend the upcoming farmers' market day",
                ],
            },
            "templates": [
                "{authority} informs {product} farmers in {county} County of new market linkage opportunities this {month}.",
                "{authority} encourages farmers in {county} County to {action} to secure better prices for {product}.",
                "Notice: {authority} will open a {product} collection centre in {county} County this {month}.",
                "{authority} advises {product} producers in {county} County to {action} ahead of the harvest season.",
            ],
        },
        "Sustainable Farming": {
            "vocab": {
                "practice": [
                    "organic farming", "soil conservation", "water harvesting",
                    "agroforestry", "terracing", "conservation tillage",
                ],
                "action": [
                    "attend the free training on climate-smart agriculture",
                    "adopt water-harvesting structures on their farms",
                    "plant cover crops to reduce soil erosion",
                ],
            },
            "templates": [
                "{authority} promotes {practice} among farmers in {county} County as part of the {month} climate resilience drive.",
                "{authority} urges farmers in {county} County to {action} to cope with changing rainfall patterns.",
                "Notice: {authority} will train farmers in {county} County on {practice} this {month}.",
                "{authority} reminds residents of {county} County that {practice} improves long-term farm productivity.",
            ],
        },
        "Agricultural Training": {
            "vocab": {
                "topic": [
                    "modern irrigation techniques", "post-harvest handling", "greenhouse farming",
                    "fertiliser application", "pest and disease management", "record keeping for farmers",
                ],
                "action": [
                    "register for the free training session",
                    "bring their farmer registration number",
                    "attend with a valid national ID",
                ],
            },
            "templates": [
                "{authority} invites farmers in {county} County to a free training on {topic} this {month}.",
                "{authority} advises farmers in {county} County to {action} to attend the upcoming agricultural training.",
                "Notice: {authority} will conduct a {topic} workshop for farmers in {county} County this {month}.",
                "{authority} reminds farmers in {county} County of the ongoing {topic} training programme.",
            ],
        },
    },
    # ------------------------------------------------------------------
    "Education": {
        "Access to Education": {
            "vocab": {
                "programme": [
                    "free primary education", "free day secondary education",
                    "adult literacy classes", "bursary allocation", "school feeding programme",
                ],
                "action": [
                    "register their children at the nearest public school",
                    "apply for the bursary before the deadline",
                    "enroll in the adult literacy programme",
                ],
            },
            "templates": [
                "{authority} reminds parents in {county} County that {programme} registration is open this {month}.",
                "{authority} urges residents of {county} County to {action} to benefit from {programme}.",
                "Notice: {authority} announces {programme} enrollment dates for schools in {county} County.",
                "{authority} encourages out-of-school children in {county} County to {action} under {programme}.",
            ],
        },
        "Vocational Training": {
            "vocab": {
                "course": [
                    "electrical installation", "tailoring and design", "catering and hospitality",
                    "motor vehicle mechanics", "ICT skills", "welding and fabrication",
                ],
                "action": [
                    "apply for TVET placement through KUCCPS",
                    "visit the nearest vocational training centre",
                    "register before the intake closes",
                ],
            },
            "templates": [
                "{authority} invites youth in {county} County to enroll for {course} training this {month}.",
                "{authority} advises applicants in {county} County to {action} for the upcoming intake.",
                "Notice: {authority} opens a new {course} programme at the vocational centre in {county} County.",
                "{authority} reminds youth in {county} County that HELB funding is available for {course} training.",
            ],
        },
        "Civic Education": {
            "vocab": {
                "topic": [
                    "voter registration", "constitutional rights", "devolution",
                    "public participation in county budgets", "the role of the ombudsman",
                ],
                "action": [
                    "attend the civic education forum",
                    "verify their voter registration details",
                    "participate in the county public forum",
                ],
            },
            "templates": [
                "{authority} conducts a civic education forum on {topic} in {county} County this {month}.",
                "{authority} encourages residents of {county} County to {action} to stay informed on {topic}.",
                "Notice: {authority} reminds citizens in {county} County about their rights regarding {topic}.",
                "{authority} urges youth in {county} County to {action} ahead of upcoming civic activities.",
            ],
        },
        "Educational Resources": {
            "vocab": {
                "resource": [
                    "free digital learning content", "textbooks and learning materials",
                    "scholarships for needy students", "school laptops under the digital literacy programme",
                    "revision guides",
                ],
                "action": [
                    "apply through the online scholarship portal",
                    "collect materials from the county education office",
                    "register early to secure allocation",
                ],
            },
            "templates": [
                "{authority} announces distribution of {resource} to schools in {county} County this {month}.",
                "{authority} advises students in {county} County to {action} to access {resource}.",
                "Notice: {authority} opens applications for {resource} for learners in {county} County.",
                "{authority} reminds needy students in {county} County that {resource} applications close soon.",
            ],
        },
        "School Safety and Inclusion": {
            "vocab": {
                "topic": [
                    "anti-bullying measures", "inclusion of learners with disabilities",
                    "school infrastructure safety", "child protection in schools",
                    "guidance and counselling services",
                ],
                "action": [
                    "report any safety concerns to the school administration",
                    "reach out to the child helpline 116",
                    "support inclusive learning environments",
                ],
            },
            "templates": [
                "{authority} reminds schools in {county} County to strengthen {topic} this {month}.",
                "{authority} urges parents and teachers in {county} County to {action}.",
                "Notice: {authority} launches a {topic} programme in schools across {county} County.",
                "{authority} calls on the community in {county} County to {action} to keep schools safe.",
            ],
        },
    },
    # ------------------------------------------------------------------
    "Security & Safety": {
        "Public Safety Awareness": {
            "vocab": {
                "hazard": ["flooding", "drought", "road accidents", "fire outbreaks", "landslides"],
                "action": [
                    "avoid crossing flooded bridges and rivers",
                    "observe speed limits and use designated pedestrian crossings",
                    "install and maintain fire extinguishers at home and work",
                    "heed evacuation orders issued by local administrators",
                ],
            },
            "templates": [
                "{authority} warns residents of {county} County to prepare for possible {hazard} this {month}.",
                "{authority} urges motorists and pedestrians in {county} County to {action} to prevent {hazard}-related incidents.",
                "Notice: {authority} activates an emergency response plan for {hazard} in {county} County.",
                "{authority} reminds residents of {county} County to {action} during this {hazard} season.",
            ],
        },
        "Crime Prevention": {
            "vocab": {
                "crime": ["theft", "burglary", "carjacking", "cattle rustling", "fraud"],
                "action": [
                    "report suspicious activity to the nearest police station",
                    "join community policing (Nyumba Kumi) initiatives",
                    "avoid sharing personal security details with strangers",
                ],
            },
            "templates": [
                "{authority} alerts residents of {county} County to a rise in {crime} cases and advises the public to {action}.",
                "{authority} urges the community in {county} County to {action} to curb {crime}.",
                "Notice: {authority} launches a {crime} prevention campaign in {county} County this {month}.",
                "{authority} reminds residents of {county} County that reporting {crime} promptly helps keep neighbourhoods safe.",
            ],
        },
        "National Security": [],
        "Gender-Based Violence": {
            "vocab": {
                "service": [
                    "free legal aid", "safe shelter referrals", "the GBV toll-free helpline",
                    "post-violence medical care", "psychosocial support",
                ],
                "action": [
                    "call the toll-free GBV helpline 1195",
                    "report cases to the nearest gender desk at a police station",
                    "seek support from the nearest safe house",
                ],
            },
            "templates": [
                "{authority} reminds survivors of gender-based violence in {county} County that access to {service} is available free of charge.",
                "{authority} urges anyone experiencing abuse in {county} County to {action}.",
                "Notice: {authority} opens a gender desk offering {service} in {county} County.",
                "{authority} calls on the community in {county} County to speak out against gender-based violence and {action}.",
            ],
        },
        "Cybersecurity": {
            "vocab": {
                "threat": ["SIM-swap fraud", "mobile money scams", "phishing messages", "fake investment schemes", "identity theft"],
                "action": [
                    "never share their M-Pesa PIN with anyone",
                    "verify requests through official channels before acting",
                    "report suspicious messages to their service provider",
                ],
            },
            "templates": [
                "{authority} warns residents of {county} County about a rise in {threat} and advises the public to {action}.",
                "{authority} reminds mobile money users in {county} County to {action} to avoid {threat}.",
                "Notice: {authority} issues a cybersecurity alert on {threat} affecting residents of {county} County.",
                "{authority} urges the public in {county} County to {action} following reported cases of {threat}.",
            ],
        },
    },
    # ------------------------------------------------------------------
    "Governance": {
        "Anti-Corruption Initiatives": {
            "vocab": {
                "topic": ["bribery in public offices", "procurement fraud", "abuse of office", "embezzlement of public funds"],
                "action": [
                    "report corruption cases via the toll-free EACC hotline",
                    "demand service delivery without paying bribes",
                    "use the online reporting portal to file a complaint",
                ],
            },
            "templates": [
                "{authority} urges residents of {county} County to {action} to fight {topic}.",
                "{authority} reminds the public in {county} County that reporting {topic} is free, safe, and confidential.",
                "Notice: {authority} launches an anti-corruption awareness drive in {county} County this {month}.",
                "{authority} warns public officers in {county} County against {topic}.",
            ],
        },
        "Public Participation": {
            "vocab": {
                "topic": ["the county budget process", "development planning forums", "the annual performance review", "public policy consultations"],
                "action": [
                    "attend the public participation forum",
                    "submit written memoranda before the deadline",
                    "engage through the county's online participation portal",
                ],
            },
            "templates": [
                "{authority} invites residents of {county} County to {action} regarding {topic}.",
                "{authority} reminds the public in {county} County that input on {topic} is welcome this {month}.",
                "Notice: {authority} will hold a public participation forum on {topic} in {county} County.",
                "{authority} urges residents of {county} County to {action} to shape {topic}.",
            ],
        },
        "Elections and Voter Education": {
            "vocab": {
                "topic": ["voter registration", "the electoral calendar", "voter education", "polling procedures"],
                "action": [
                    "verify their details via SMS to 70000",
                    "visit the nearest IEBC registration centre",
                    "carry a valid national ID or passport on voting day",
                ],
            },
            "templates": [
                "{authority} reminds voters in {county} County to {action} ahead of {topic}.",
                "{authority} urges eligible citizens in {county} County to participate in {topic}.",
                "Notice: {authority} opens {topic} centres in {county} County this {month}.",
                "{authority} encourages first-time voters in {county} County to {action}.",
            ],
        },
        "Public Service Delivery": {
            "vocab": {
                "service": ["national ID applications", "passport services", "e-Citizen registration", "birth certificate processing"],
                "action": [
                    "apply online via the e-Citizen portal",
                    "visit the nearest Huduma Centre",
                    "carry all required documents to avoid delays",
                ],
            },
            "templates": [
                "{authority} announces improved turnaround times for {service} in {county} County.",
                "{authority} advises residents of {county} County to {action} when seeking {service}.",
                "Notice: {authority} opens a new service point for {service} in {county} County.",
                "{authority} reminds residents of {county} County that access to {service} is now easier through official service channels.",
            ],
        },
        "Devolution and Local Governance": {
            "vocab": {
                "topic": ["county development projects", "ward-level service delivery", "the county integrated development plan", "community-based development programmes"],
                "action": [
                    "engage their local ward administrator",
                    "attend the county assembly public session",
                    "track project progress through the county website",
                ],
            },
            "templates": [
                "{authority} updates residents of {county} County on progress of {topic} this {month}.",
                "{authority} urges residents of {county} County to {action} to stay informed on {topic}.",
                "Notice: {authority} launches {topic} in {county} County.",
                "{authority} reminds residents of {county} County that {action} strengthens local governance.",
            ],
        },
    },
}

# "National Security" needs real content (was left as [] placeholder above by mistake)
TEMPLATES["Security & Safety"]["National Security"] = {
    "vocab": {
        "topic": ["counter-terrorism vigilance", "border security", "national peace-building", "community early-warning systems"],
        "action": [
            "report unusual activity along border areas to security agencies",
            "cooperate with security screening at public venues",
            "support local peace-building committees",
        ],
    },
    "templates": [
        "{authority} calls on residents of {county} County to {action} in support of {topic}.",
        "{authority} reminds the public in {county} County to remain vigilant on {topic}.",
        "Notice: {authority} conducts a community briefing on {topic} in {county} County this {month}.",
        "{authority} urges residents of {county} County to {action} amid heightened attention to {topic}.",
    ],
}
