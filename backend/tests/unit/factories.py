"""Builders for normalized profiles/opportunities in unit tests.

The demo profile mirrors the assessment's sample candidate; the sample
opportunity mirrors its sample job (J012).
"""

from app.services.normalization import NormalizedOpportunity, NormalizedProfile

SAMPLE_CANDIDATE = NormalizedProfile(
    education_level="bachelors",
    education_field="business",
    experience_years=2.0,
    experience_areas=("business operations", "project support"),
    skills=("excel", "research", "stakeholder communication", "reporting", "project coordination"),
    raw_skills=(
        "Excel",
        "research",
        "stakeholder communication",
        "reporting",
        "project coordination",
    ),
    languages={"Bengali": "native", "English": "professional"},
    preferred_countries=("Germany", "Canada", "Singapore"),
    career_interests=("programme support", "business operations", "project coordination"),
    raw_interests=("Programme support", "business operations", "project coordination"),
    work_authorisation={"Germany": "unknown", "Canada": "unknown", "Singapore": "unknown"},
    citizenship=None,
    currently_enrolled=None,
)


def sample_opportunity(**overrides) -> NormalizedOpportunity:
    """The assessment's sample job (J012) with overridable fields."""
    defaults = dict(
        id="J012",
        title="Local-Hire Project Coordinator",
        organisation="Kestrel Fintech",
        country="Singapore",
        city="Singapore",
        description="",
        employment_type="full_time",
        required_skills=("project coordination", "reporting", "excel"),
        optional_skills=("stakeholder communication",),
        min_years=1.0,
        max_years=3.0,
        experience_areas=("project support",),
        min_education_level="bachelors",
        relevant_fields=("business",),
        languages_required={"English": "professional"},
        career_tracks=("project coordination",),
        local_work_authorization_required=True,
        citizenship_required=(),
        enrollment_required=False,
        strict_language=False,
        strict_education=False,
        strict_experience=False,
    )
    defaults.update(overrides)
    return NormalizedOpportunity(**defaults)


def make_profile(**overrides) -> NormalizedProfile:
    """A copy of the sample candidate with overridable fields."""
    data = {
        "education_level": SAMPLE_CANDIDATE.education_level,
        "education_field": SAMPLE_CANDIDATE.education_field,
        "experience_years": SAMPLE_CANDIDATE.experience_years,
        "experience_areas": SAMPLE_CANDIDATE.experience_areas,
        "skills": SAMPLE_CANDIDATE.skills,
        "raw_skills": SAMPLE_CANDIDATE.raw_skills,
        "languages": dict(SAMPLE_CANDIDATE.languages),
        "preferred_countries": SAMPLE_CANDIDATE.preferred_countries,
        "career_interests": SAMPLE_CANDIDATE.career_interests,
        "raw_interests": SAMPLE_CANDIDATE.raw_interests,
        "work_authorisation": dict(SAMPLE_CANDIDATE.work_authorisation),
        "citizenship": SAMPLE_CANDIDATE.citizenship,
        "currently_enrolled": SAMPLE_CANDIDATE.currently_enrolled,
    }
    data.update(overrides)
    return NormalizedProfile(**data)
