"""Reference taxonomy for the normalization, retrieval, scoring and
eligibility engines.

Everything the matching pipeline knows about the shape of a career profile
lives here: ranked education levels, ranked language proficiencies, work
authorisation values, the curated skills taxonomy (canonical names plus
aliases), study fields, countries with their regions, and career tracks.

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

COUNTRY_REGIONS: dict[str, str] = {
    "Germany": "Europe",
    "United Kingdom": "Europe",
    "Netherlands": "Europe",
    "Sweden": "Europe",
    "France": "Europe",
    "Switzerland": "Europe",
    "Canada": "North America",
    "United States": "North America",
    "Singapore": "Asia-Pacific",
    "Japan": "Asia-Pacific",
    "Australia": "Asia-Pacific",
    "India": "Asia-Pacific",
    "United Arab Emirates": "Middle East",
    "Qatar": "Middle East",
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


COUNTRY_ALIASES: dict[str, str] = {
    "germany": "Germany",
    "deutschland": "Germany",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "united kingdom of great britain and northern ireland": "United Kingdom",
    "netherlands": "Netherlands",
    "the netherlands": "Netherlands",
    "holland": "Netherlands",
    "sweden": "Sweden",
    "france": "France",
    "switzerland": "Switzerland",
    "canada": "Canada",
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a.": "United States",
    "united states of america": "United States",
    "america": "United States",
    "singapore": "Singapore",
    "japan": "Japan",
    "australia": "Australia",
    "india": "India",
    "uae": "United Arab Emirates",
    "u.a.e.": "United Arab Emirates",
    "emirates": "United Arab Emirates",
    "qatar": "Qatar",
}

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
