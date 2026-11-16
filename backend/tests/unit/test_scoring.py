"""Weighted scoring engine tests: dimension math, totals, explainability."""

from app.services.scoring import score_match
from tests.unit.factories import SAMPLE_CANDIDATE, make_profile, sample_opportunity


def by_key(match):
    return {dimension.key: dimension for dimension in match.dimensions}


def test_perfect_match_scores_100():
    """The sample candidate against a perfectly aligned role: every
    dimension maxed, total exactly 100."""
    match = score_match(
        SAMPLE_CANDIDATE,
        sample_opportunity(
            id="T100",
            country="Germany",
            local_work_authorization_required=False,
        ),
    )
    assert match.total == 100.0
    assert match.max_score == 100.0
    dims = by_key(match)
    assert dims["skills"].score == 35.0
    assert dims["experience"].score == 20.0
    assert dims["education"].score == 15.0
    assert dims["location"].score == 15.0
    assert dims["language"].score == 10.0
    assert dims["interests"].score == 5.0


def test_skills_partial_coverage():
    match = score_match(
        SAMPLE_CANDIDATE,
        sample_opportunity(
            required_skills=("project coordination", "python", "sql"),
            optional_skills=(),
        ),
    )
    skills = by_key(match)["skills"]
    # required coverage 1/3, no optional listed (non-restrictive -> 1.0):
    # 35 * (0.8 * 1/3 + 0.2 * 1.0) = 16.3
    assert skills.score == 16.3
    assert skills.missing == ["python", "sql"]
    assert skills.matched == ["project coordination"]


def test_skills_optional_bonus():
    match = score_match(
        SAMPLE_CANDIDATE,
        sample_opportunity(
            required_skills=("project coordination",),
            optional_skills=("stakeholder communication",),
        ),
    )
    # 0.8 * 1.0 + 0.2 * 1.0 -> full marks
    assert by_key(match)["skills"].score == 35.0


def test_experience_below_minimum_prorated():
    match = score_match(
        make_profile(experience_years=1.0, experience_areas=("project support",)),
        sample_opportunity(min_years=4.0, max_years=6.0, experience_areas=("project support",)),
    )
    experience = by_key(match)["experience"]
    # years: 14 * 1/4 = 3.5; areas: 6/6 -> 9.5
    assert experience.score == 9.5


def test_experience_above_window_overqualified():
    match = score_match(
        make_profile(experience_years=10.0, experience_areas=("project support",)),
        sample_opportunity(min_years=1.0, max_years=3.0, experience_areas=("project support",)),
    )
    experience = by_key(match)["experience"]
    # years above window: 14 * 0.75 = 10.5; areas 6 -> 16.5
    assert experience.score == 16.5


def test_education_deficits_and_field_relevance():
    # One level below (associate vs bachelors), field matches: 6 + 5
    match = score_match(
        make_profile(education_level="associate"),
        sample_opportunity(),
    )
    assert by_key(match)["education"].score == 11.0

    # Two levels below, field matches: 2 + 5
    match = score_match(make_profile(education_level="secondary"), sample_opportunity())
    assert by_key(match)["education"].score == 7.0

    # Level met, unrelated field: 10 + 0
    match = score_match(
        make_profile(education_field="nursing"),
        sample_opportunity(),
    )
    assert by_key(match)["education"].score == 10.0


def test_location_exact_region_and_miss():
    exact = score_match(SAMPLE_CANDIDATE, sample_opportunity(country="Canada"))
    assert by_key(exact)["location"].score == 15.0

    # Sweden shares the Europe region with preferred Germany
    region = score_match(SAMPLE_CANDIDATE, sample_opportunity(country="Sweden"))
    assert by_key(region)["location"].score == 8.0

    # Middle East shares no region with any preference -> 0
    miss = score_match(SAMPLE_CANDIDATE, sample_opportunity(country="United Arab Emirates"))
    assert by_key(miss)["location"].score == 0.0


def test_language_ratios():
    # English professional required and held: full marks
    match = score_match(
        SAMPLE_CANDIDATE, sample_opportunity(languages_required={"English": "professional"})
    )
    assert by_key(match)["language"].score == 10.0

    # English fluent required, professional held: ratio 3/4 -> 7.5
    match = score_match(
        SAMPLE_CANDIDATE, sample_opportunity(languages_required={"English": "fluent"})
    )
    assert by_key(match)["language"].score == 7.5

    # German basic required, not spoken: 0
    match = score_match(
        SAMPLE_CANDIDATE, sample_opportunity(languages_required={"German": "basic"})
    )
    assert by_key(match)["language"].score == 0.0

    # Two languages, one met one not: mean(1.0, 0.0) -> 5.0
    match = score_match(
        SAMPLE_CANDIDATE,
        sample_opportunity(
            languages_required={"English": "professional", "German": "conversational"}
        ),
    )
    assert by_key(match)["language"].score == 5.0


def test_interests_overlap():
    match = score_match(
        SAMPLE_CANDIDATE, sample_opportunity(career_tracks=("project coordination",))
    )
    assert by_key(match)["interests"].score == 5.0

    match = score_match(
        SAMPLE_CANDIDATE,
        sample_opportunity(career_tracks=("project coordination", "data analytics")),
    )
    assert by_key(match)["interests"].score == 2.5


def test_explainability_strengths_and_gaps():
    strong = score_match(
        SAMPLE_CANDIDATE,
        sample_opportunity(country="Germany", local_work_authorization_required=False),
    )
    assert strong.strengths  # perfect match: strengths for every dimension
    assert strong.gaps == []

    partial = score_match(
        SAMPLE_CANDIDATE,
        sample_opportunity(
            country="Japan",
            required_skills=("project coordination", "python"),
            languages_required={"Japanese": "conversational"},
        ),
    )
    assert any("python" in gap for gap in partial.gaps)
    assert any("Japan" in gap or "Location" in gap for gap in partial.gaps)
    assert any("Japanese" in gap for gap in partial.gaps)
