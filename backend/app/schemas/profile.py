"""Request/response schemas for user profiles (Pydantic v2).

These are the single source of truth for request validation: field
constraints here decide what reaches the service layer; anything else is
rejected with the standard 422 envelope before business code runs.

Career fields follow the hybrid-form contract: structured enums for degree
level, language proficiencies and work-authorisation states; free-text
chips for skills, interests and experience areas (canonicalized by the
normalization engine at match time).
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user_profile import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH
from app.services import taxonomy

DegreeLevel = Literal[
    "none", "secondary", "diploma", "associate", "bachelors", "masters", "doctorate"
]
LanguageLevel = Literal["not_spoken", "basic", "conversational", "professional", "fluent", "native"]
WorkAuthValue = Literal["authorized", "not_authorized", "unknown"]

MAX_SKILLS = 30
MAX_INTERESTS = 15
MAX_LANGUAGES = 8
MAX_LOCATIONS = 10
MAX_WORK_AUTH_ENTRIES = 20
MAX_AREAS = 10


def _clean_str_list(items: list[str] | None) -> list[str]:
    """Trim chips, drop blanks, dedupe case-insensitively, keep order."""
    if items is None:
        return []
    seen: set[str] = set()
    cleaned: list[str] = []
    for item in items:
        value = item.strip()
        if value and value.lower() not in seen:
            seen.add(value.lower())
            cleaned.append(value)
    return cleaned


def _normalize_language_keys(languages: dict[str, str]) -> dict[str, str]:
    """Title-case language names ("english" -> "English")."""
    return {name.strip().title(): level for name, level in languages.items() if name.strip()}


class CareerProfileBase(BaseModel):
    """Shared career fields + validation for create and update."""

    education_level: DegreeLevel = Field(
        examples=["bachelors"], description="Highest education level."
    )
    education_field: str | None = Field(
        default=None,
        max_length=120,
        examples=["Business Administration"],
        description="Field of study (free text; matched loosely against role fields).",
    )
    experience_years: float = Field(
        ge=0, le=50, examples=[2], description="Total years of work experience."
    )
    experience_areas: list[str] = Field(
        default_factory=list,
        max_length=MAX_AREAS,
        examples=[["business operations", "project support"]],
        description="Experience areas (free-text chips).",
    )
    skills: list[str] = Field(
        min_length=1,
        max_length=MAX_SKILLS,
        examples=[["Excel", "reporting", "stakeholder communication"]],
        description="Skills (free-text chips, canonicalized at match time).",
    )
    languages: dict[str, LanguageLevel] = Field(
        min_length=1,
        max_length=MAX_LANGUAGES,
        examples=[{"English": "professional", "Bengali": "native"}],
        description="Spoken languages mapped to proficiency levels.",
    )
    preferred_locations: list[str] = Field(
        min_length=1,
        max_length=MAX_LOCATIONS,
        examples=[["Germany", "Canada", "Singapore"]],
        description="Preferred countries (validated against the country taxonomy).",
    )
    career_interests: list[str] = Field(
        default_factory=list,
        max_length=MAX_INTERESTS,
        examples=[["Programme support", "business operations"]],
        description="Career interests (free-text chips, matched to career tracks).",
    )
    work_authorisation: dict[str, WorkAuthValue] = Field(
        default_factory=dict,
        max_length=MAX_WORK_AUTH_ENTRIES,
        examples=[{"Germany": "unknown", "Canada": "unknown"}],
        description="Stated work-authorisation status per country. 'unknown' is a "
        "first-class value and always surfaces as 'requires verification'.",
    )
    citizenship: str | None = Field(
        default=None,
        max_length=80,
        examples=["Bangladesh"],
        description="Country of citizenship (null = not stated; drives verification flags).",
    )
    currently_enrolled: bool | None = Field(
        default=None,
        examples=[True],
        description="Whether currently enrolled in study (null = not stated).",
    )

    _clean_areas = field_validator("experience_areas", mode="before")(
        classmethod(lambda cls, v: _clean_str_list(v))
    )
    _clean_skills = field_validator("skills", mode="before")(
        classmethod(lambda cls, v: _clean_str_list(v))
    )
    _clean_interests = field_validator("career_interests", mode="before")(
        classmethod(lambda cls, v: _clean_str_list(v))
    )
    _clean_languages = field_validator("languages", mode="before")(
        classmethod(lambda cls, v: _normalize_language_keys(v))
    )

    @field_validator("education_field")
    @classmethod
    def _strip_field(cls, v: str | None) -> str | None:
        return v.strip() if v else v

    @field_validator("citizenship")
    @classmethod
    def _validate_citizenship(cls, v: str | None) -> str | None:
        """Citizenship may be any country (not just opportunity locations) —
        canonicalize when known, otherwise keep the trimmed title-cased form."""
        if v is None or not v.strip():
            return None
        canonical = taxonomy.normalize_country_key(v)
        return canonical if canonical is not None else v.strip().title()

    @field_validator("preferred_locations", "work_authorisation")
    @classmethod
    def _validate_countries(cls, v: dict[str, Any] | list[str]) -> dict[str, Any] | list[str]:
        """Every country reference must resolve to the canonical taxonomy."""
        if isinstance(v, dict):
            canonical: dict[str, str] = {}
            for country in v:
                resolved = taxonomy.normalize_country_key(country)
                if resolved is None:
                    raise ValueError(f"Unknown country: {country!r}")
                if resolved in canonical:
                    raise ValueError(f"Duplicate country after normalization: {resolved!r}")
                canonical[resolved] = v[country]
            return canonical
        resolved_list: list[str] = []
        for country in v:
            resolved = taxonomy.normalize_country_key(country)
            if resolved is None:
                raise ValueError(f"Unknown country: {country!r}")
            if resolved not in resolved_list:
                resolved_list.append(resolved)
        return resolved_list


class ProfileCreate(CareerProfileBase):
    """Body for `POST /profiles` — identity plus the full career profile."""

    name: str = Field(
        min_length=1,
        max_length=NAME_MAX_LENGTH,
        examples=["Alex Rahman"],
        description="Display name (1-100 characters, trimmed).",
    )
    email: EmailStr = Field(
        max_length=EMAIL_MAX_LENGTH,
        examples=["alex.rahman@example.com"],
        description="Contact email — stored lowercase, unique per profile.",
    )

    @field_validator("name")
    @classmethod
    def _normalize_name(cls, v: str) -> str:
        name = v.strip()
        if not name:
            raise ValueError("name must not be blank (whitespace-only).")
        return name

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: EmailStr) -> EmailStr:
        return v.strip().lower()


class ProfileUpdate(BaseModel):
    """Body for `PATCH /profiles/{id}` — send only changed fields.

    `name`/`email`: an explicit `null` means "no change" (both required).
    Career fields: presence means change — `null` explicitly clears a
    nullable field (citizenship, currently_enrolled, education_field) and
    is rejected for required ones (e.g. `experience_years: null`).
    """

    name: str | None = Field(default=None, min_length=1, max_length=NAME_MAX_LENGTH)
    email: EmailStr | None = Field(default=None, max_length=EMAIL_MAX_LENGTH)
    education_level: DegreeLevel | None = None
    education_field: str | None = None
    experience_years: float | None = Field(default=None, ge=0, le=50)
    experience_areas: list[str] | None = Field(default=None, max_length=MAX_AREAS)
    skills: list[str] | None = Field(default=None, min_length=1, max_length=MAX_SKILLS)
    languages: dict[str, LanguageLevel] | None = Field(
        default=None, min_length=1, max_length=MAX_LANGUAGES
    )
    preferred_locations: list[str] | None = Field(
        default=None, min_length=1, max_length=MAX_LOCATIONS
    )
    career_interests: list[str] | None = Field(default=None, max_length=MAX_INTERESTS)
    work_authorisation: dict[str, WorkAuthValue] | None = Field(
        default=None, max_length=MAX_WORK_AUTH_ENTRIES
    )
    citizenship: str | None = None
    currently_enrolled: bool | None = None

    _clean_areas = field_validator("experience_areas", mode="before")(
        classmethod(lambda cls, v: v if v is None else _clean_str_list(v))
    )
    _clean_skills = field_validator("skills", mode="before")(
        classmethod(lambda cls, v: v if v is None else _clean_str_list(v))
    )
    _clean_interests = field_validator("career_interests", mode="before")(
        classmethod(lambda cls, v: v if v is None else _clean_str_list(v))
    )
    _clean_languages = field_validator("languages", mode="before")(
        classmethod(lambda cls, v: v if v is None else _normalize_language_keys(v))
    )

    @field_validator("name")
    @classmethod
    def _normalize_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        name = v.strip()
        if not name:
            raise ValueError("name must not be blank (whitespace-only).")
        return name

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: EmailStr | None) -> EmailStr | None:
        return None if v is None else v.strip().lower()

    @field_validator("preferred_locations", "work_authorisation")
    @classmethod
    def _validate_countries(cls, v: dict[str, Any] | list[str] | None):
        if v is None:
            return v
        if isinstance(v, dict):
            canonical: dict[str, str] = {}
            for country in v:
                resolved = taxonomy.normalize_country_key(country)
                if resolved is None:
                    raise ValueError(f"Unknown country: {country!r}")
                if resolved in canonical:
                    raise ValueError(f"Duplicate country after normalization: {resolved!r}")
                canonical[resolved] = v[country]
            return canonical
        resolved_list: list[str] = []
        for country in v:
            resolved = taxonomy.normalize_country_key(country)
            if resolved is None:
                raise ValueError(f"Unknown country: {country!r}")
            if resolved not in resolved_list:
                resolved_list.append(resolved)
        return resolved_list


class ProfileRead(BaseModel):
    """Profile representation returned by every endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    education_level: str
    education_field: str | None
    experience_years: float
    experience_areas: list[str]
    skills: list[str]
    languages: dict[str, str]
    preferred_locations: list[str]
    career_interests: list[str]
    work_authorisation: dict[str, str]
    citizenship: str | None
    currently_enrolled: bool | None
    created_at: datetime
    updated_at: datetime
