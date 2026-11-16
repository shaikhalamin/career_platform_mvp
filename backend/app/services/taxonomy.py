"""Reference taxonomy for the normalization, retrieval, scoring and
eligibility engines.

Everything the matching pipeline knows about the shape of a career profile
lives here: ranked education levels, ranked language proficiencies, work
authorisation values, the curated skills taxonomy (canonical names plus
aliases), study fields, every valid country with its region and ISO-code
aliases, and career tracks.

These constants are also served to the frontend via `GET /meta/taxonomy`
so the profile form dropdowns and the display labels never drift from what
the backend actually matches on.
"""

# ---------------------------------------------------------------------------
# Ranked enums (from the platform's matching specification)
# ---------------------------------------------------------------------------

#: Higher rank = higher education level. Order is contractual: education
#: scoring and strict-education eligibility both diff these ranks.
DEGREE_RANK: dict[str, int] = {
    "none": 0,
    "secondary": 1,
    "diploma": 2,
    "associate": 3,
    "bachelors": 4,
    "masters": 5,
    "doctorate": 6,
}

#: Higher rank = stronger proficiency. Language scoring compares the
#: candidate's rank against a role's required rank per language.
LANGUAGE_RANK: dict[str, int] = {
    "not_spoken": 0,
    "basic": 1,
    "conversational": 2,
    "professional": 3,
    "fluent": 4,
    "native": 5,
}

#: The only accepted work-authorisation states. "unknown" is a first-class
#: value: it must never be treated as authorized, and it drives the
#: "requires verification" eligibility outcome.
WORK_AUTH_VALUES: frozenset[str] = frozenset({"authorized", "not_authorized", "unknown"})

#: Fixed six-part weighted score, totalling 100 points.
WEIGHTS: dict[str, int] = {
    "skills": 35,
    "experience": 20,
    "education": 15,
    "location": 15,
    "language": 10,
    "interests": 5,
}

# ---------------------------------------------------------------------------
# Skills taxonomy
# ---------------------------------------------------------------------------

#: Canonical skill -> aliases (lowercase). Matching canonicalizes both the
#: candidate's free-text chips and the role requirements through this map,
#: so "MS Excel" and "Excel" are the same skill. A chip that matches no
#: alias is kept as its own lowercased skill (no match, but still listed).
SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "excel": ("ms excel", "microsoft excel", "spreadsheets", "google sheets"),
    "sql": (
        "mysql",
        "postgresql",
        "postgres",
    ),
    "python": ("python 3",),
    "r": ("r language", "rstudio"),
    "tableau": (),
    "power bi": ("powerbi",),
    "data analysis": (
        "data analytics",
        "analytics",
    ),
    "data visualization": ("data viz",),
    "statistical analysis": ("statistics",),
    "reporting": (
        "report writing",
        "report preparation",
    ),
    "research": (
        "desk research",
        "research skills",
    ),
    "financial modeling": ("financial modelling",),
    "accounting": ("bookkeeping",),
    "auditing": ("audit",),
    "tax compliance": ("taxation",),
    "project coordination": ("project support coordination",),
    "project management": ("project planning",),
    "programme management": ("program management",),
    "agile methodologies": (
        "agile",
        "scrum",
        "kanban",
    ),
    "stakeholder communication": (
        "stakeholder management",
        "stakeholder engagement",
        "stakeholder relations",
    ),
    "business operations": (
        "business ops",
        "operations management",
    ),
    "process improvement": (
        "process optimization",
        "business process improvement",
    ),
    "supply chain management": ("supply chain",),
    "procurement": ("purchasing",),
    "logistics coordination": ("logistics",),
    "inventory management": ("inventory",),
    "market research": ("market analysis",),
    "digital marketing": ("online marketing",),
    "content writing": (
        "copywriting",
        "writing",
    ),
    "seo": ("search engine optimization",),
    "sales": ("sales execution",),
    "business development": (
        "bd",
        "partnerships",
    ),
    "customer support": (
        "customer service",
        "client support",
    ),
    "customer relationship management": ("crm", "crm systems", "salesforce"),
    "recruitment": (
        "talent acquisition",
        "hiring",
    ),
    "hr administration": (
        "hr ops",
        "human resources administration",
    ),
    "payroll": ("payroll administration",),
    "training delivery": (
        "training",
        "workshop facilitation",
    ),
    "grant writing": ("grant proposals",),
    "policy analysis": ("public policy",),
    "erp systems": (
        "sap",
        "oracle",
        "erp",
    ),
    "quality assurance": ("qa",),
    "mechanical design": (
        "cad",
        "autocad",
        "solidworks",
    ),
    "programming": (
        "javascript",
        "java",
        "typescript",
        "software development",
    ),
    "clinical protocols": ("clinical research",),
    "nursing care": ("patient care",),
    "laboratory analysis": (
        "lab analysis",
        "lab techniques",
    ),
    "curriculum design": (
        "curriculum development",
        "instructional design",
    ),
    "teaching": ("tutoring",),
    "graphic design": ("visual design",),
    "ui/ux design": (
        "ux design",
        "ui design",
        "figma",
    ),
    "event coordination": ("event management",),
    "data entry": (),
}

#: Canonical skills in stable display order (drives vector slots + UI lists).
SKILLS: tuple[str, ...] = tuple(SKILL_ALIASES.keys())

# ---------------------------------------------------------------------------
# Study fields (education relevance matching)
# ---------------------------------------------------------------------------

FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "business": (
        "business administration",
        "business management",
        "business studies",
        "commerce",
        "management",
        "mba",
        "bba",
    ),
    "finance": ("finance", "banking", "investment"),
    "accounting": ("accounting", "accountancy"),
    "economics": ("economics", "econometrics"),
    "marketing": ("marketing", "branding"),
    "communications": ("communications", "public relations", "media studies", "journalism"),
    "human resources": ("human resources", "hr management", "people management"),
    "computer science": ("computer science", "computing", "software engineering", "informatics"),
    "data science": ("data science", "data analytics", "statistics"),
    "engineering": (
        "engineering",
        "mechanical engineering",
        "electrical engineering",
        "industrial engineering",
    ),
    "sciences": (
        "biology",
        "chemistry",
        "physics",
        "biochemistry",
        "environmental science",
        "mathematics",
    ),
    "healthcare": ("nursing", "public health", "medicine", "pharmacy", "health sciences"),
    "education": ("education", "educational studies", "teaching"),
    "design": ("design", "graphic design", "industrial design", "fine arts"),
    "law": ("law", "legal studies", "llb"),
    "supply chain": ("supply chain", "logistics", "operations management"),
    "social sciences": (
        "international relations",
        "political science",
        "sociology",
        "development studies",
        "psychology",
    ),
}

FIELDS: tuple[str, ...] = tuple(FIELD_ALIASES.keys())

# ---------------------------------------------------------------------------
# Countries and regions (location scoring)
# ---------------------------------------------------------------------------

#: Master country list — every widely-recognised sovereign state (the 193 UN
#: members plus Vatican City and Palestine) plus Taiwan, grouped by region
#: and alphabetical within each region. Each row is
#: (canonical name, region, ISO 3166-1 alpha-2, alpha-3, extra aliases);
#: the ISO codes are seeded into COUNTRY_ALIASES automatically, so "bd",
#: "bgd" and "bangladesh" all resolve to Bangladesh.
_CountrySpec = tuple[str, str, str, str, tuple[str, ...]]

COUNTRY_DATA: tuple[_CountrySpec, ...] = (
    # -- Europe ---------------------------------------------------------------
    ("Albania", "Europe", "al", "alb", ()),
    ("Andorra", "Europe", "ad", "and", ()),
    ("Austria", "Europe", "at", "aut", ()),
    ("Belarus", "Europe", "by", "blr", ()),
    ("Belgium", "Europe", "be", "bel", ()),
    ("Bosnia and Herzegovina", "Europe", "ba", "bih", ("bosnia",)),
    ("Bulgaria", "Europe", "bg", "bgr", ()),
    ("Croatia", "Europe", "hr", "hrv", ()),
    ("Cyprus", "Europe", "cy", "cyp", ()),
    ("Czechia", "Europe", "cz", "cze", ("czech republic",)),
    ("Denmark", "Europe", "dk", "dnk", ()),
    ("Estonia", "Europe", "ee", "est", ()),
    ("Finland", "Europe", "fi", "fin", ()),
    ("France", "Europe", "fr", "fra", ()),
    ("Germany", "Europe", "de", "deu", ("deutschland",)),
    ("Greece", "Europe", "gr", "grc", ()),
    ("Hungary", "Europe", "hu", "hun", ()),
    ("Iceland", "Europe", "is", "isl", ()),
    ("Ireland", "Europe", "ie", "irl", ("republic of ireland",)),
    ("Italy", "Europe", "it", "ita", ()),
    ("Latvia", "Europe", "lv", "lva", ()),
    ("Liechtenstein", "Europe", "li", "lie", ()),
    ("Lithuania", "Europe", "lt", "ltu", ()),
    ("Luxembourg", "Europe", "lu", "lux", ()),
    ("Malta", "Europe", "mt", "mlt", ()),
    ("Moldova", "Europe", "md", "mda", ("republic of moldova",)),
    ("Monaco", "Europe", "mc", "mco", ()),
    ("Montenegro", "Europe", "me", "mne", ()),
    ("Netherlands", "Europe", "nl", "nld", ("the netherlands", "holland")),
    ("North Macedonia", "Europe", "mk", "mkd", ("macedonia",)),
    ("Norway", "Europe", "no", "nor", ()),
    ("Poland", "Europe", "pl", "pol", ()),
    ("Portugal", "Europe", "pt", "prt", ()),
    ("Romania", "Europe", "ro", "rou", ()),
    ("Russia", "Europe", "ru", "rus", ("russian federation",)),
    ("San Marino", "Europe", "sm", "smr", ()),
    ("Serbia", "Europe", "rs", "srb", ()),
    ("Slovakia", "Europe", "sk", "svk", ()),
    ("Slovenia", "Europe", "si", "svn", ()),
    ("Spain", "Europe", "es", "esp", ()),
    ("Sweden", "Europe", "se", "swe", ()),
    ("Switzerland", "Europe", "ch", "che", ()),
    ("Ukraine", "Europe", "ua", "ukr", ()),
    (
        "United Kingdom",
        "Europe",
        "gb",
        "gbr",
        (
            "uk",
            "u.k.",
            "britain",
            "great britain",
            "england",
            "united kingdom of great britain and northern ireland",
        ),
    ),
    ("Vatican City", "Europe", "va", "vat", ("holy see", "vatican")),
    # -- Middle East ----------------------------------------------------------
    ("Bahrain", "Middle East", "bh", "bhr", ()),
    ("Iran", "Middle East", "ir", "irn", ("islamic republic of iran",)),
    ("Iraq", "Middle East", "iq", "irq", ()),
    ("Israel", "Middle East", "il", "isr", ()),
    ("Jordan", "Middle East", "jo", "jor", ()),
    ("Kuwait", "Middle East", "kw", "kwt", ()),
    ("Lebanon", "Middle East", "lb", "lbn", ()),
    ("Oman", "Middle East", "om", "omn", ()),
    ("Palestine", "Middle East", "ps", "pse", ("state of palestine",)),
    ("Qatar", "Middle East", "qa", "qat", ()),
    ("Saudi Arabia", "Middle East", "sa", "sau", ("ksa",)),
    ("Syria", "Middle East", "sy", "syr", ("syrian arab republic",)),
    ("Türkiye", "Middle East", "tr", "tur", ("turkey",)),
    ("United Arab Emirates", "Middle East", "ae", "are", ("uae", "u.a.e.", "emirates")),
    ("Yemen", "Middle East", "ye", "yem", ()),
    # -- Africa ---------------------------------------------------------------
    ("Algeria", "Africa", "dz", "dza", ()),
    ("Angola", "Africa", "ao", "ago", ()),
    ("Benin", "Africa", "bj", "ben", ()),
    ("Botswana", "Africa", "bw", "bwa", ()),
    ("Burkina Faso", "Africa", "bf", "bfa", ()),
    ("Burundi", "Africa", "bi", "bdi", ()),
    ("Cabo Verde", "Africa", "cv", "cpv", ("cape verde",)),
    ("Cameroon", "Africa", "cm", "cmr", ()),
    ("Central African Republic", "Africa", "cf", "caf", ()),
    ("Chad", "Africa", "td", "tcd", ()),
    ("Comoros", "Africa", "km", "com", ()),
    (
        "Republic of the Congo",
        "Africa",
        "cg",
        "cog",
        ("congo", "congo-brazzaville", "congo brazzaville"),
    ),
    (
        "Democratic Republic of the Congo",
        "Africa",
        "cd",
        "cod",
        (
            "drc",
            "dr congo",
            "democratic republic of congo",
            "congo-kinshasa",
            "congo kinshasa",
            "zaire",
        ),
    ),
    (
        "Côte d'Ivoire",
        "Africa",
        "ci",
        "civ",
        ("ivory coast", "cote d'ivoire", "cote divoire"),
    ),
    ("Djibouti", "Africa", "dj", "dji", ()),
    ("Egypt", "Africa", "eg", "egy", ()),
    ("Equatorial Guinea", "Africa", "gq", "gnq", ()),
    ("Eritrea", "Africa", "er", "eri", ()),
    ("Eswatini", "Africa", "sz", "swz", ("swaziland",)),
    ("Ethiopia", "Africa", "et", "eth", ()),
    ("Gabon", "Africa", "ga", "gab", ()),
    ("Gambia", "Africa", "gm", "gmb", ("the gambia",)),
    ("Ghana", "Africa", "gh", "gha", ()),
    ("Guinea", "Africa", "gn", "gin", ()),
    ("Guinea-Bissau", "Africa", "gw", "gnb", ()),
    ("Kenya", "Africa", "ke", "ken", ()),
    ("Lesotho", "Africa", "ls", "lso", ()),
    ("Liberia", "Africa", "lr", "lbr", ()),
    ("Libya", "Africa", "ly", "lby", ()),
    ("Madagascar", "Africa", "mg", "mdg", ()),
    ("Malawi", "Africa", "mw", "mwi", ()),
    ("Mali", "Africa", "ml", "mli", ()),
    ("Mauritania", "Africa", "mr", "mrt", ()),
    ("Mauritius", "Africa", "mu", "mus", ()),
    ("Morocco", "Africa", "ma", "mar", ()),
    ("Mozambique", "Africa", "mz", "moz", ()),
    ("Namibia", "Africa", "na", "nam", ()),
    ("Niger", "Africa", "ne", "ner", ()),
    ("Nigeria", "Africa", "ng", "nga", ()),
    ("Rwanda", "Africa", "rw", "rwa", ()),
    ("Sao Tome and Principe", "Africa", "st", "stp", ("são tomé and príncipe",)),
    ("Senegal", "Africa", "sn", "sen", ()),
    ("Seychelles", "Africa", "sc", "syc", ()),
    ("Sierra Leone", "Africa", "sl", "sle", ()),
    ("Somalia", "Africa", "so", "som", ()),
    ("South Africa", "Africa", "za", "zaf", ("rsa",)),
    ("South Sudan", "Africa", "ss", "ssd", ()),
    ("Sudan", "Africa", "sd", "sdn", ()),
    ("Tanzania", "Africa", "tz", "tza", ("united republic of tanzania",)),
    ("Togo", "Africa", "tg", "tgo", ()),
    ("Tunisia", "Africa", "tn", "tun", ()),
    ("Uganda", "Africa", "ug", "uga", ()),
    ("Zambia", "Africa", "zm", "zmb", ()),
    ("Zimbabwe", "Africa", "zw", "zwe", ()),
    # -- Asia-Pacific ---------------------------------------------------------
    ("Afghanistan", "Asia-Pacific", "af", "afg", ()),
    ("Armenia", "Asia-Pacific", "am", "arm", ()),
    ("Azerbaijan", "Asia-Pacific", "az", "aze", ()),
    ("Bangladesh", "Asia-Pacific", "bd", "bgd", ()),
    ("Bhutan", "Asia-Pacific", "bt", "btn", ()),
    ("Brunei", "Asia-Pacific", "bn", "brn", ("brunei darussalam",)),
    ("Cambodia", "Asia-Pacific", "kh", "khm", ()),
    ("China", "Asia-Pacific", "cn", "chn", ("people's republic of china", "prc")),
    ("Georgia", "Asia-Pacific", "ge", "geo", ()),
    ("India", "Asia-Pacific", "in", "ind", ()),
    ("Indonesia", "Asia-Pacific", "id", "idn", ()),
    ("Japan", "Asia-Pacific", "jp", "jpn", ()),
    ("Kazakhstan", "Asia-Pacific", "kz", "kaz", ()),
    ("Kyrgyzstan", "Asia-Pacific", "kg", "kgz", ()),
    ("Laos", "Asia-Pacific", "la", "lao", ()),
    ("Malaysia", "Asia-Pacific", "my", "mys", ()),
    ("Maldives", "Asia-Pacific", "mv", "mdv", ()),
    ("Mongolia", "Asia-Pacific", "mn", "mng", ()),
    ("Myanmar", "Asia-Pacific", "mm", "mmr", ("burma",)),
    ("Nepal", "Asia-Pacific", "np", "npl", ()),
    (
        "North Korea",
        "Asia-Pacific",
        "kp",
        "prk",
        ("dprk", "democratic people's republic of korea"),
    ),
    ("Pakistan", "Asia-Pacific", "pk", "pak", ()),
    ("Philippines", "Asia-Pacific", "ph", "phl", ("the philippines",)),
    ("Singapore", "Asia-Pacific", "sg", "sgp", ()),
    ("South Korea", "Asia-Pacific", "kr", "kor", ("republic of korea",)),
    ("Sri Lanka", "Asia-Pacific", "lk", "lka", ()),
    ("Taiwan", "Asia-Pacific", "tw", "twn", ()),
    ("Tajikistan", "Asia-Pacific", "tj", "tjk", ()),
    ("Thailand", "Asia-Pacific", "th", "tha", ()),
    ("Timor-Leste", "Asia-Pacific", "tl", "tls", ("east timor",)),
    ("Turkmenistan", "Asia-Pacific", "tm", "tkm", ()),
    ("Uzbekistan", "Asia-Pacific", "uz", "uzb", ()),
    ("Vietnam", "Asia-Pacific", "vn", "vnm", ("viet nam",)),
    # -- Oceania --------------------------------------------------------------
    ("Australia", "Oceania", "au", "aus", ()),
    ("Fiji", "Oceania", "fj", "fji", ()),
    ("Kiribati", "Oceania", "ki", "kir", ()),
    ("Marshall Islands", "Oceania", "mh", "mhl", ()),
    ("Micronesia", "Oceania", "fm", "fsm", ("federated states of micronesia",)),
    ("Nauru", "Oceania", "nr", "nru", ()),
    ("New Zealand", "Oceania", "nz", "nzl", ("aotearoa",)),
    ("Palau", "Oceania", "pw", "plw", ()),
    ("Papua New Guinea", "Oceania", "pg", "png", ()),
    ("Samoa", "Oceania", "ws", "wsm", ()),
    ("Solomon Islands", "Oceania", "sb", "slb", ()),
    ("Tonga", "Oceania", "to", "ton", ()),
    ("Tuvalu", "Oceania", "tv", "tuv", ()),
    ("Vanuatu", "Oceania", "vu", "vut", ()),
    # -- North America --------------------------------------------------------
    ("Canada", "North America", "ca", "can", ()),
    ("Mexico", "North America", "mx", "mex", ()),
    (
        "United States",
        "North America",
        "us",
        "usa",
        ("u.s.", "u.s.a.", "united states of america", "america"),
    ),
    # -- Central America & Caribbean -------------------------------------------
    ("Antigua and Barbuda", "Central America & Caribbean", "ag", "atg", ("antigua",)),
    ("Bahamas", "Central America & Caribbean", "bs", "bhs", ("the bahamas",)),
    ("Barbados", "Central America & Caribbean", "bb", "brb", ()),
    ("Belize", "Central America & Caribbean", "bz", "blz", ()),
    ("Costa Rica", "Central America & Caribbean", "cr", "cri", ()),
    ("Cuba", "Central America & Caribbean", "cu", "cub", ()),
    ("Dominica", "Central America & Caribbean", "dm", "dma", ()),
    ("Dominican Republic", "Central America & Caribbean", "do", "dom", ()),
    ("El Salvador", "Central America & Caribbean", "sv", "slv", ()),
    ("Grenada", "Central America & Caribbean", "gd", "grd", ()),
    ("Guatemala", "Central America & Caribbean", "gt", "gtm", ()),
    ("Haiti", "Central America & Caribbean", "ht", "hti", ()),
    ("Honduras", "Central America & Caribbean", "hn", "hnd", ()),
    ("Jamaica", "Central America & Caribbean", "jm", "jam", ()),
    ("Nicaragua", "Central America & Caribbean", "ni", "nic", ()),
    ("Panama", "Central America & Caribbean", "pa", "pan", ()),
    (
        "Saint Kitts and Nevis",
        "Central America & Caribbean",
        "kn",
        "kna",
        ("st kitts and nevis",),
    ),
    ("Saint Lucia", "Central America & Caribbean", "lc", "lca", ("st lucia",)),
    (
        "Saint Vincent and the Grenadines",
        "Central America & Caribbean",
        "vc",
        "vct",
        ("st vincent and the grenadines",),
    ),
    (
        "Trinidad and Tobago",
        "Central America & Caribbean",
        "tt",
        "tto",
        ("trinidad",),
    ),
    # -- South America ----------------------------------------------------------
    ("Argentina", "South America", "ar", "arg", ()),
    ("Bolivia", "South America", "bo", "bol", ()),
    ("Brazil", "South America", "br", "bra", ("brasil",)),
    ("Chile", "South America", "cl", "chl", ()),
    ("Colombia", "South America", "co", "col", ()),
    ("Ecuador", "South America", "ec", "ecu", ()),
    ("Guyana", "South America", "gy", "guy", ()),
    ("Paraguay", "South America", "py", "pry", ()),
    ("Peru", "South America", "pe", "per", ()),
    ("Suriname", "South America", "sr", "sur", ()),
    ("Uruguay", "South America", "uy", "ury", ()),
    ("Venezuela", "South America", "ve", "ven", ()),
)

#: Canonical country -> region (location scoring gives partial credit to
#: roles in the same region as a preferred country).
COUNTRY_REGIONS: dict[str, str] = {name: region for name, region, _, _, _ in COUNTRY_DATA}

#: Lowercase alias -> canonical name. Seeded from the ISO alpha-2/alpha-3
#: codes plus the curated extra aliases in COUNTRY_DATA; a canonical name in
#: any casing resolves without needing an explicit alias.
COUNTRY_ALIASES: dict[str, str] = {
    alias: name for name, _, iso2, iso3, extras in COUNTRY_DATA for alias in (iso2, iso3, *extras)
}

COUNTRIES: tuple[str, ...] = tuple(COUNTRY_REGIONS.keys())
REGIONS: tuple[str, ...] = tuple(dict.fromkeys(COUNTRY_REGIONS.values()))


def normalize_country_key(country: str | None) -> str | None:
    """Strict country resolution: canonical name or None (validation-grade).

    Unlike the lenient matching-time `normalization.normalize_country`,
    this rejects unknown names so bad input surfaces as a 422 at the API
    boundary instead of silently becoming an unmatched location.
    """
    if not country or not country.strip():
        return None
    key = country.strip().lower()
    canonical = COUNTRY_ALIASES.get(key)
    if canonical is not None:
        return canonical
    # Accept an exact canonical name in any casing ("germany" -> "Germany").
    for name in COUNTRIES:
        if name.lower() == key:
            return name
    return None


# ---------------------------------------------------------------------------
# Career tracks (interest matching + retrieval)
# ---------------------------------------------------------------------------

TRACK_ALIASES: dict[str, tuple[str, ...]] = {
    "business operations": ("operations", "business ops", "operations management"),
    "project coordination": ("project support", "project coordination & support"),
    "programme support": (
        "programme management",
        "program support",
        "programme management & support",
    ),
    "data analytics": ("data science", "analytics", "business intelligence"),
    "finance & accounting": ("finance", "accounting", "financial operations"),
    "marketing & communications": ("marketing", "communications", "digital marketing"),
    "human resources": ("hr", "people operations", "talent"),
    "supply chain & logistics": ("supply chain", "logistics", "procurement"),
    "engineering": ("engineering & design", "mechanical engineering", "software engineering"),
    "research & policy": ("research", "policy", "research & analysis"),
    "design": ("product design", "graphic design", "ui/ux"),
    "sales & business development": ("sales", "business development", "partnerships"),
    "healthcare": ("health", "nursing", "clinical work"),
    "education": ("teaching", "training & education", "learning & development"),
}

TRACKS: tuple[str, ...] = tuple(TRACK_ALIASES.keys())

# ---------------------------------------------------------------------------
# Languages known to the system (vector slots + form dropdowns)
# ---------------------------------------------------------------------------

LANGUAGES: tuple[str, ...] = (
    "English",
    "German",
    "French",
    "Spanish",
    "Mandarin",
    "Japanese",
    "Bengali",
    "Hindi",
    "Arabic",
    "Dutch",
    "Swedish",
    "Korean",
)

#: Spoken proficiency synonyms -> canonical LANGUAGE_RANK key.
LANGUAGE_LEVEL_ALIASES: dict[str, str] = {
    "none": "not_spoken",
    "not spoken": "not_spoken",
    "beginner": "basic",
    "elementary": "basic",
    "a2": "basic",
    "intermediate": "conversational",
    "b1": "conversational",
    "conversational": "conversational",
    "working proficiency": "professional",
    "working knowledge": "professional",
    "advanced": "professional",
    "b2": "professional",
    "c1": "professional",
    "professional": "professional",
    "professional proficiency": "professional",
    "business fluent": "professional",
    "fluent": "fluent",
    "c2": "fluent",
    "fluent speaker": "fluent",
    "native": "native",
    "native speaker": "native",
    "mother tongue": "native",
    "bilingual": "native",
}

#: Human-readable labels for level keys (API + UI).
LANGUAGE_LEVEL_LABELS: dict[str, str] = {
    "not_spoken": "Not spoken",
    "basic": "Basic",
    "conversational": "Conversational",
    "professional": "Professional",
    "fluent": "Fluent",
    "native": "Native",
}

DEGREE_LEVEL_LABELS: dict[str, str] = {
    "none": "No formal education",
    "secondary": "Secondary school",
    "diploma": "Diploma",
    "associate": "Associate degree",
    "bachelors": "Bachelor's degree",
    "masters": "Master's degree",
    "doctorate": "Doctorate (PhD)",
}


def language_level_for_rank(rank: int) -> str:
    """Inverse of LANGUAGE_RANK — the level key for a rank (nearest below)."""
    best = "not_spoken"
    for level, level_rank in LANGUAGE_RANK.items():
        if level_rank <= max(rank, 0):
            best = level
    return best


def degree_level_for_rank(rank: int) -> str:
    """Inverse of DEGREE_RANK — the level key for a rank (nearest below)."""
    best = "none"
    for level, level_rank in DEGREE_RANK.items():
        if level_rank <= max(rank, 0):
            best = level
    return best


#: Standard disclaimer attached to every recommendation payload. The
#: eligibility engine is guidance, not a legal determination.
ELIGIBILITY_DISCLAIMER = (
    "Recommendations and eligibility notes are automated guidance based on the "
    "profile provided. They are not a legal determination of visa or "
    "work-authorisation entitlement. Items marked 'requires verification' must "
    "be confirmed with the employer or the relevant authorities before applying."
)
