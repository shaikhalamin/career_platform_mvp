"""Normalization engine tests: free-text parsing + taxonomy mapping."""

from app.services.normalization import (
    normalize_country,
    normalize_field,
    normalize_interests,
    normalize_language_level,
    normalize_skill,
    normalize_skills,
    parse_education,
    parse_experience,
    parse_languages,
    parse_raw_candidate,
)

#: The assessment's raw candidate payload, verbatim.
RAW_CANDIDATE = {
    "education": "Bachelor's degree in Business Administration",
    "experience": "2 years in business operations and project support",
    "skills": "Excel, research, stakeholder communication, reporting, project coordination",
    "languages": "Bengali (native), English (professional)",
    "preferred_locations": "Germany, Canada, Singapore",
    "career_interests": "Programme support, business operations, project coordination",
    "work_authorisation": {"Germany": "unknown", "Canada": "unknown", "Singapore": "unknown"},
    "citizenship": None,
    "currently_enrolled": None,
}


def test_parse_raw_candidate_sample_payload():
    profile = parse_raw_candidate(RAW_CANDIDATE)
    assert profile.education_level == "bachelors"
    assert profile.education_field == "business"
    assert profile.experience_years == 2.0
    assert profile.experience_areas == ("business operations", "project support")
    assert profile.skills == (
        "excel",
        "research",
        "stakeholder communication",
        "reporting",
        "project coordination",
    )
    assert profile.languages == {"Bengali": "native", "English": "professional"}
    assert profile.preferred_countries == ("Germany", "Canada", "Singapore")
    assert profile.career_interests == (
        "programme support",
        "business operations",
        "project coordination",
    )
    assert profile.work_authorisation == {
        "Germany": "unknown",
        "Canada": "unknown",
        "Singapore": "unknown",
    }
    assert profile.degree_rank == 4
    assert profile.language_rank("English") == 3


def test_parse_education_variants():
    assert parse_education("Master's degree in Data Science") == ("masters", "Data Science")
    assert parse_education("PhD in Physics") == ("doctorate", "Physics")
    assert parse_education("High school diploma") == ("secondary", None)
    assert parse_education(None) == ("none", None)
    assert parse_education("") == ("none", None)


def test_parse_experience_variants():
    assert parse_experience("5 years in marketing") == (5.0, ("marketing",))
    assert parse_experience("6 months") == (0.0, ())
    assert parse_experience("3+ years in sales and business development") == (
        3.0,
        ("sales", "business development"),
    )
    assert parse_experience(None) == (0.0, ())


def test_parse_languages_variants():
    assert parse_languages("German (native), English (fluent)") == {
        "German": "native",
        "English": "fluent",
    }
    assert parse_languages("French (advanced)") == {"French": "professional"}
    assert parse_languages("Spanish (intermediate)") == {"Spanish": "conversational"}
    assert parse_languages("") == {}


def test_normalize_skill_aliases():
    assert normalize_skill("MS Excel") == "excel"
    assert normalize_skill("Microsoft Excel") == "excel"
    assert normalize_skill("Stakeholder Management") == "stakeholder communication"
    assert normalize_skill("scrum") == "agile methodologies"
    assert normalize_skill("Nostril Tuning") == "nostril tuning"  # unknown -> lowercased


def test_normalize_skills_dedupes_after_canonicalization():
    canonical, raw = normalize_skills(["Excel", "MS Excel", "reporting"])
    assert canonical == ("excel", "reporting")
    assert raw == ("Excel", "reporting")  # second alias dropped as duplicate


def test_normalize_field():
    assert normalize_field("Business Administration") == "business"
    assert normalize_field("computer science") == "computer science"
    assert normalize_field("Fine Arts") == "design"
    assert normalize_field(None) is None
    assert normalize_field("astrology") is None


def test_normalize_country():
    assert normalize_country("USA") == "United States"
    assert normalize_country("u.k.") == "United Kingdom"
    assert normalize_country("Holland") == "Netherlands"
    assert normalize_country("Singapore") == "Singapore"
    assert normalize_country(None) is None


def test_normalize_interests_to_tracks():
    canonical, raw = normalize_interests(["Programme support", "data science", "hr"])
    assert canonical == ("programme support", "data analytics", "human resources")
    assert raw == ("Programme support", "data science", "hr")


def test_normalize_language_level_synonyms():
    assert normalize_language_level("mother tongue") == "native"
    assert normalize_language_level("working knowledge") == "professional"
    assert normalize_language_level("beginner") == "basic"
    assert normalize_language_level(None) == "not_spoken"
