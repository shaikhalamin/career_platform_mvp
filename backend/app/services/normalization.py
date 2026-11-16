"""Normalization engine: free text and loosely structured profile/job data
in, canonical taxonomy-referenced structures out.

Two entry points:

- `parse_raw_candidate` / helpers — rule-based parsing of prose like
  "2 years in business operations and project support" or
  "Bengali (native), English (professional)". Covered by unit tests;
  the API itself receives the hybrid form's structured fields and
  normalizes those instead.
- `normalize_profile` / `normalize_opportunity` — map already-structured
  input onto the canonical taxonomy (skills aliases, country aliases,
  field aliases, language level aliases). Everything downstream — vectors,
  scoring, eligibility — consumes only the normalized form.
"""

from dataclasses import dataclass

from app.services import taxonomy

_DEGREE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("phd", "doctorate"),
    ("ph.d", "doctorate"),
    ("doctorate", "doctorate"),
    ("doctoral", "doctorate"),
    ("master", "masters"),
    ("mba", "masters"),
    ("m.sc", "masters"),
    ("msc", "masters"),
    ("m.a.", "masters"),
    ("bachelor", "bachelors"),
    ("b.sc", "bachelors"),
    ("bsc", "bachelors"),
    ("b.a.", "bachelors"),
    ("bba", "bachelors"),
    ("undergraduate degree", "bachelors"),
    ("associate", "associate"),
    ("high school", "secondary"),
    ("secondary school", "secondary"),
    ("secondary", "secondary"),
    ("diploma", "diploma"),
    ("gcse", "secondary"),
)


@dataclass(slots=True)
class NormalizedProfile:
    """Canonical candidate representation used by every matching stage."""

    education_level: str  # DEGREE_RANK key ("none" when unknown)
    education_field: str | None  # FIELDS key or None
    experience_years: float
    experience_areas: tuple[str, ...]  # canonical-lowercase area labels
    skills: tuple[str, ...]  # canonical skills (taxonomy keys)
    raw_skills: tuple[str, ...]  # as entered, for display
    languages: dict[str, str]  # language name -> LANGUAGE_RANK key
    preferred_countries: tuple[str, ...]  # canonical country names
    career_interests: tuple[str, ...]  # canonical track keys
    raw_interests: tuple[str, ...]  # as entered, for display
    work_authorisation: dict[str, str]  # country -> authorized|not_authorized|unknown
    citizenship: str | None  # canonical country name or None
    currently_enrolled: bool | None

    @property
    def degree_rank(self) -> int:
        return taxonomy.DEGREE_RANK.get(self.education_level, 0)

    def language_rank(self, language: str) -> int:
        return taxonomy.LANGUAGE_RANK.get(self.languages.get(language, "not_spoken"), 0)


@dataclass(slots=True)
class NormalizedOpportunity:
    """Canonical opportunity representation used by every matching stage."""

    id: str
    title: str
    organisation: str
    country: str
    city: str | None
    description: str
    employment_type: str
    required_skills: tuple[str, ...]
    optional_skills: tuple[str, ...]
    min_years: float
    max_years: float
    experience_areas: tuple[str, ...]
    min_education_level: str
    relevant_fields: tuple[str, ...]
    languages_required: dict[str, str]  # language -> minimum LANGUAGE_RANK key
    career_tracks: tuple[str, ...]
    local_work_authorization_required: bool
    citizenship_required: tuple[str, ...]  # empty = no requirement
    enrollment_required: bool
    strict_language: bool
    strict_education: bool
    strict_experience: bool


# ---------------------------------------------------------------------------
# Small shared helpers
# ---------------------------------------------------------------------------


def _clean_list(items: list[str] | None) -> tuple[str, ...]:
    """Trim, drop empties, dedupe preserving order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items or []:
        cleaned = item.strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            result.append(cleaned)
    return tuple(result)


def _split_list_text(text: str) -> list[str]:
    """Split a prose list on commas / semicolons / newlines / ' and '."""
    import re

    parts = re.split(r"[,;\n]|\band\b", text)
    return [part.strip() for part in parts if part.strip()]


def normalize_skill(skill: str) -> str:
    """Map one free-text skill onto the canonical taxonomy (or lowercase it)."""
    key = skill.strip().lower().rstrip(".")
    for canonical, aliases in taxonomy.SKILL_ALIASES.items():
        if key == canonical or key in aliases:
            return canonical
    return key


def normalize_skills(skills: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (canonical skills, cleaned raw skills) — both deduped, ordered.

    A chip whose canonical form already appeared (e.g. "MS Excel" after
    "Excel") is dropped from both lists so stored chips stay tidy.
    """
    canonical: list[str] = []
    raw: list[str] = []
    seen: set[str] = set()
    for item in _clean_list(skills):
        can = normalize_skill(item)
        if can in seen:
            continue
        seen.add(can)
        canonical.append(can)
        raw.append(item)
    return tuple(canonical), tuple(raw)


def normalize_field(field_text: str | None) -> str | None:
    """Map a study field onto the taxonomy, or None when unknown/blank."""
    if not field_text:
        return None
    key = field_text.strip().lower()
    for canonical, aliases in taxonomy.FIELD_ALIASES.items():
        if key == canonical or any(alias in key for alias in aliases):
            return canonical
    return None


def normalize_country(country: str | None) -> str | None:
    """Map a country name/alias onto the canonical name, or None."""
    if not country:
        return None
    key = country.strip().lower()
    return taxonomy.COUNTRY_ALIASES.get(key, country.strip().title() if key else None)


def normalize_track(interest: str) -> str:
    """Map one career interest onto a canonical track (or lowercase it)."""
    key = interest.strip().lower()
    for canonical, aliases in taxonomy.TRACK_ALIASES.items():
        if key == canonical or key in aliases:
            return canonical
    return key


def normalize_interests(interests: list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (canonical tracks, raw interests) — deduped, ordered."""
    raw = _clean_list(interests)
    canonical: list[str] = []
    seen: set[str] = set()
    for item in raw:
        can = normalize_track(item)
        if can not in seen:
            seen.add(can)
            canonical.append(can)
    return tuple(canonical), raw


def normalize_language_name(name: str) -> str:
    """Title-case a language name ("english" -> "English")."""
    return name.strip().title()


def normalize_language_level(level: str | None) -> str:
    """Map a proficiency synonym onto a LANGUAGE_RANK key (default basic)."""
    if not level:
        return "not_spoken"
    return taxonomy.LANGUAGE_LEVEL_ALIASES.get(level.strip().lower(), "not_spoken")


# ---------------------------------------------------------------------------
# Free-text parsing (raw candidate strings -> structured values)
# ---------------------------------------------------------------------------


def parse_education(text: str | None) -> tuple[str, str | None]:
    """Extract (degree level key, raw field text) from prose.

    "Bachelor's degree in Business Administration" -> ("bachelors", "business administration")
    """
    if not text or not text.strip():
        return "none", None
    lowered = text.lower()
    level = "none"
    for pattern, key in _DEGREE_PATTERNS:
        if pattern in lowered:
            level = key
            break
    field_text: str | None = None
    if " in " in lowered:
        field_text = text.split(" in ", 1)[1].strip(" .")
    return level, field_text


def parse_experience(text: str | None) -> tuple[float, tuple[str, ...]]:
    """Extract (years, areas) from prose.

    "2 years in business operations and project support"
        -> (2.0, ("business operations", "project support"))
    """
    import re

    if not text or not text.strip():
        return 0.0, ()
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+?\s*)?years?", text.lower())
    years = float(match.group(1)) if match else 0.0
    areas: tuple[str, ...] = ()
    if " in " in text.lower():
        area_text = re.split(r"\bin\b", text, flags=re.IGNORECASE, maxsplit=1)[1]
        areas = _clean_list(_split_list_text(area_text))
    return years, areas


def parse_languages(text: str | None) -> dict[str, str]:
    """Extract {language: level key} from prose like
    "Bengali (native), English (professional)"."""
    import re

    if not text or not text.strip():
        return {}
    languages: dict[str, str] = {}
    for match in re.finditer(r"([A-Za-z][A-Za-z ]*?)\s*\(([^)]+)\)", text):
        name = normalize_language_name(match.group(1))
        level = normalize_language_level(match.group(2))
        if name and taxonomy.LANGUAGE_RANK.get(level, 0) > 0:
            languages[name] = level
    return languages


def parse_raw_candidate(raw: dict) -> NormalizedProfile:
    """Normalize the assessment's raw free-text candidate payload."""
    level, field_text = parse_education(raw.get("education"))
    years, areas = parse_experience(raw.get("experience"))
    skills_raw = _split_list_text(raw.get("skills") or "")
    canonical_skills, raw_skills = normalize_skills(list(skills_raw))
    languages = parse_languages(raw.get("languages"))
    preferred = _clean_list([c for c in _split_list_text(raw.get("preferred_locations") or "")])
    interests_raw = _split_list_text(raw.get("career_interests") or "")
    canonical_tracks, raw_interests = normalize_interests(list(interests_raw))
    work_auth = {
        normalize_country(country) or country: status
        for country, status in (raw.get("work_authorisation") or {}).items()
        if status in taxonomy.WORK_AUTH_VALUES
    }
    return NormalizedProfile(
        education_level=level,
        education_field=normalize_field(field_text),
        experience_years=years,
        experience_areas=tuple(normalize_skill_area(a) for a in areas),
        skills=canonical_skills,
        raw_skills=raw_skills,
        languages=languages,
        preferred_countries=tuple(c for c in (normalize_country(p) for p in preferred) if c),
        career_interests=canonical_tracks,
        raw_interests=raw_interests,
        work_authorisation=work_auth,
        citizenship=normalize_country(raw.get("citizenship")),
        currently_enrolled=raw.get("currently_enrolled"),
    )


def normalize_skill_area(area: str) -> str:
    """Experience areas match loosely: canonicalize known skill-ish words."""
    key = area.strip().lower()
    for canonical, aliases in taxonomy.SKILL_ALIASES.items():
        if key == canonical or key in aliases:
            return canonical
    return key


# ---------------------------------------------------------------------------
# Structured input -> normalized forms (used by the API layer)
# ---------------------------------------------------------------------------


def normalize_profile(
    *,
    education_level: str | None,
    education_field: str | None,
    experience_years: float | None,
    experience_areas: list[str] | None,
    skills: list[str],
    languages: dict[str, str],
    preferred_locations: list[str],
    career_interests: list[str],
    work_authorisation: dict[str, str] | None,
    citizenship: str | None,
    currently_enrolled: bool | None,
) -> NormalizedProfile:
    """Normalize the hybrid form's structured payload."""
    canonical_skills, raw_skills = normalize_skills(skills)
    canonical_tracks, raw_interests = normalize_interests(career_interests)
    normalized_languages = {
        normalize_language_name(name): normalize_language_level(level)
        for name, level in (languages or {}).items()
    }
    preferred = _clean_list(
        [c for c in (normalize_country(p) or "" for p in preferred_locations) if c]
    )
    work_auth = {
        (normalize_country(country) or country): status
        for country, status in (work_authorisation or {}).items()
        if status in taxonomy.WORK_AUTH_VALUES
    }
    return NormalizedProfile(
        education_level=education_level or "none",
        education_field=normalize_field(education_field),
        experience_years=float(experience_years or 0.0),
        experience_areas=tuple(normalize_skill_area(a) for a in _clean_list(experience_areas)),
        skills=canonical_skills,
        raw_skills=raw_skills,
        languages=normalized_languages,
        preferred_countries=preferred,
        career_interests=canonical_tracks,
        raw_interests=raw_interests,
        work_authorisation=work_auth,
        citizenship=normalize_country(citizenship),
        currently_enrolled=currently_enrolled,
    )


def normalize_opportunity(opp) -> NormalizedOpportunity:
    """Normalize an `Opportunity` ORM row (already structured seed data —
    mainly canonicalizes skills/areas and validates enums)."""
    return NormalizedOpportunity(
        id=opp.id,
        title=opp.title,
        organisation=opp.organisation,
        country=opp.country,
        city=opp.city,
        description=opp.description or "",
        employment_type=opp.employment_type,
        required_skills=tuple(normalize_skill(s) for s in opp.required_skills or []),
        optional_skills=tuple(normalize_skill(s) for s in opp.optional_skills or []),
        min_years=float(opp.min_years),
        max_years=float(opp.max_years),
        experience_areas=tuple(normalize_skill_area(a) for a in opp.experience_areas or []),
        min_education_level=opp.min_education_level,
        relevant_fields=tuple(normalize_field(f) or f.lower() for f in opp.relevant_fields or []),
        languages_required={
            normalize_language_name(name): normalize_language_level(level)
            for name, level in (opp.languages_required or {}).items()
        },
        career_tracks=tuple(normalize_track(t) for t in opp.career_tracks or []),
        local_work_authorization_required=bool(opp.local_work_authorization_required),
        citizenship_required=tuple(
            c for c in (normalize_country(x) for x in opp.citizenship_required or []) if c
        ),
        enrollment_required=bool(opp.enrollment_required),
        strict_language=bool(opp.strict_language),
        strict_education=bool(opp.strict_education),
        strict_experience=bool(opp.strict_experience),
    )
