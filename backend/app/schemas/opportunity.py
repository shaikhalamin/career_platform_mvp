"""Request/response schemas for opportunities."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EmploymentType = Literal["full_time", "internship", "contract", "part_time"]


class SkillRequirements(BaseModel):
    """Required vs nice-to-have skills for a role."""

    required: list[str] = Field(default_factory=list)
    optional: list[str] = Field(default_factory=list)


class ExperienceRequirements(BaseModel):
    """Experience window and areas for a role."""

    min_years: float
    max_years: float
    areas: list[str] = Field(default_factory=list)


class EducationRequirements(BaseModel):
    """Minimum education level and relevant fields of study."""

    min_level: str = Field(examples=["bachelors"], description="DEGREE_RANK key.")
    relevant_fields: list[str] = Field(default_factory=list)


class EligibilityRequirements(BaseModel):
    """Hard-constraint declarations for a role.

    `strict_*` flags promote the corresponding requirement from a scored
    gap to an eligibility check; `citizenship_required` is an allowlist
    (empty = open to all nationalities).
    """

    local_work_authorization_required: bool = False
    citizenship_required: list[str] = Field(default_factory=list)
    enrollment_required: bool = False
    strict_language: bool = False
    strict_education: bool = False
    strict_experience: bool = False


class OpportunityRead(BaseModel):
    """Opportunity representation returned by every endpoint.

    Requirements are grouped (skills/experience/education) to mirror the
    platform's structured job schema; eligibility constraints are nested
    under `eligibility`.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    organisation: str
    country: str
    city: str | None
    description: str
    employment_type: EmploymentType
    skills: SkillRequirements
    experience: ExperienceRequirements
    education: EducationRequirements
    languages_required: dict[str, str] = Field(
        description="Language -> minimum proficiency (LANGUAGE_RANK key)."
    )
    career_tracks: list[str]
    eligibility: EligibilityRequirements
    created_at: datetime

    @classmethod
    def from_orm_opportunity(cls, opp) -> "OpportunityRead":
        """Compose the nested read model from the flat ORM row."""
        return cls(
            id=opp.id,
            title=opp.title,
            organisation=opp.organisation,
            country=opp.country,
            city=opp.city,
            description=opp.description or "",
            employment_type=opp.employment_type,
            skills=SkillRequirements(
                required=list(opp.required_skills or []),
                optional=list(opp.optional_skills or []),
            ),
            experience=ExperienceRequirements(
                min_years=opp.min_years,
                max_years=opp.max_years,
                areas=list(opp.experience_areas or []),
            ),
            education=EducationRequirements(
                min_level=opp.min_education_level,
                relevant_fields=list(opp.relevant_fields or []),
            ),
            languages_required=dict(opp.languages_required or {}),
            career_tracks=list(opp.career_tracks or []),
            eligibility=EligibilityRequirements(
                local_work_authorization_required=bool(opp.local_work_authorization_required),
                citizenship_required=list(opp.citizenship_required or []),
                enrollment_required=bool(opp.enrollment_required),
                strict_language=bool(opp.strict_language),
                strict_education=bool(opp.strict_education),
                strict_experience=bool(opp.strict_experience),
            ),
            created_at=opp.created_at,
        )


class OpportunitySummary(BaseModel):
    """Compact opportunity card for recommendation lists."""

    id: str
    title: str
    organisation: str
    country: str
    city: str | None
    employment_type: EmploymentType
    required_skills: list[str]
    min_years: float
    max_years: float
    min_education_level: str
    languages_required: dict[str, str]
    career_tracks: list[str]
    local_work_authorization_required: bool

    @classmethod
    def from_orm_opportunity(cls, opp) -> "OpportunitySummary":
        return cls(
            id=opp.id,
            title=opp.title,
            organisation=opp.organisation,
            country=opp.country,
            city=opp.city,
            employment_type=opp.employment_type,
            required_skills=list(opp.required_skills or []),
            min_years=opp.min_years,
            max_years=opp.max_years,
            min_education_level=opp.min_education_level,
            languages_required=dict(opp.languages_required or {}),
            career_tracks=list(opp.career_tracks or []),
            local_work_authorization_required=bool(opp.local_work_authorization_required),
        )


class OpportunityListItem(OpportunityRead):
    """OpportunityRead plus the caller's shortlist state (browse lists)."""

    shortlisted: bool = False

    @classmethod
    def from_orm_opportunity(cls, opp, *, shortlisted: bool = False) -> "OpportunityListItem":
        base = OpportunityRead.from_orm_opportunity(opp)
        return cls(**base.model_dump(), shortlisted=shortlisted)
