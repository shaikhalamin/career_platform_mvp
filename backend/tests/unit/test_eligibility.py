"""Eligibility engine tests — especially the "unknown never counts as
satisfied" contract and the verification labelling."""

from app.services.eligibility import (
    FAIL,
    NEEDS_VERIFICATION,
    NOT_APPLICABLE,
    PASS,
    STATUS_ELIGIBLE,
    STATUS_INELIGIBLE,
    STATUS_NEEDS_VERIFICATION,
    evaluate_eligibility,
)
from tests.unit.factories import make_profile, sample_opportunity


def check(result, code):
    return next(c for c in result.checks if c.code == code)


def test_unknown_work_authorisation_requires_verification():
    """The core safety property: unknown work authorisation is flagged for
    verification, never treated as authorized, with evidence."""
    result = evaluate_eligibility(make_profile(), sample_opportunity())
    assert result.status == STATUS_NEEDS_VERIFICATION
    work_auth = check(result, "WORK_AUTHORIZATION")
    assert work_auth.status == NEEDS_VERIFICATION
    assert work_auth.requires_verification is True
    assert "unknown" in work_auth.evidence
    assert "verified" in work_auth.evidence
    assert result.status_label == "Requires verification"


def test_authorized_work_authorisation_passes_with_caveat():
    result = evaluate_eligibility(
        make_profile(work_authorisation={"Singapore": "authorized"}), sample_opportunity()
    )
    work_auth = check(result, "WORK_AUTHORIZATION")
    assert work_auth.status == PASS
    assert result.status == STATUS_ELIGIBLE
    # Even a stated authorization is not presented as a legal determination.
    assert "not a legal determination" in work_auth.evidence


def test_not_authorized_work_authorisation_fails():
    result = evaluate_eligibility(
        make_profile(work_authorisation={"Singapore": "not_authorized"}), sample_opportunity()
    )
    work_auth = check(result, "WORK_AUTHORIZATION")
    assert work_auth.status == FAIL
    assert result.status == STATUS_INELIGIBLE


def test_missing_work_authorisation_entry_is_unknown():
    """No entry at all for the country behaves like 'unknown'."""
    result = evaluate_eligibility(make_profile(work_authorisation={}), sample_opportunity())
    assert check(result, "WORK_AUTHORIZATION").status == NEEDS_VERIFICATION


def test_work_auth_check_not_applicable_when_not_required():
    result = evaluate_eligibility(
        make_profile(), sample_opportunity(local_work_authorization_required=False)
    )
    assert check(result, "WORK_AUTHORIZATION").status == NOT_APPLICABLE


def test_strict_language_failure_and_non_strict_gap():
    strict = sample_opportunity(strict_language=True, languages_required={"German": "professional"})
    result = evaluate_eligibility(make_profile(), strict)
    language = check(result, "LANGUAGE_REQUIREMENTS")
    assert language.status == FAIL
    assert "German" in language.evidence
    assert result.status == STATUS_INELIGIBLE

    # Same requirement without the strict flag: not an eligibility matter.
    non_strict = sample_opportunity(languages_required={"German": "professional"})
    result = evaluate_eligibility(make_profile(), non_strict)
    assert check(result, "LANGUAGE_REQUIREMENTS").status == NOT_APPLICABLE


def test_strict_language_pass():
    result = evaluate_eligibility(
        make_profile(work_authorisation={"Singapore": "authorized"}),
        sample_opportunity(
            strict_language=True,
            languages_required={"English": "professional"},
            local_work_authorization_required=True,
        ),
    )
    language = check(result, "LANGUAGE_REQUIREMENTS")
    assert language.status == PASS
    assert result.status == STATUS_ELIGIBLE


def test_strict_education():
    result = evaluate_eligibility(
        make_profile(education_level="bachelors"),
        sample_opportunity(min_education_level="masters", strict_education=True),
    )
    assert check(result, "EDUCATION").status == FAIL
    assert result.status == STATUS_INELIGIBLE

    result = evaluate_eligibility(
        make_profile(education_level="masters"),
        sample_opportunity(min_education_level="bachelors", strict_education=True),
    )
    assert check(result, "EDUCATION").status == PASS


def test_strict_experience_window():
    result = evaluate_eligibility(
        make_profile(experience_years=2.0),
        sample_opportunity(min_years=6.0, max_years=12.0, strict_experience=True),
    )
    experience = check(result, "EXPERIENCE")
    assert experience.status == FAIL
    assert "6 years" in experience.evidence

    # Over the cap is also a strict failure (targets earlier stage).
    result = evaluate_eligibility(
        make_profile(experience_years=9.0),
        sample_opportunity(min_years=1.0, max_years=3.0, strict_experience=True),
    )
    assert check(result, "EXPERIENCE").status == FAIL


def test_citizenship_unknown_requires_verification():
    result = evaluate_eligibility(
        make_profile(citizenship=None), sample_opportunity(citizenship_required=("Canada",))
    )
    citizenship = check(result, "CITIZENSHIP")
    assert citizenship.status == NEEDS_VERIFICATION
    assert citizenship.requires_verification is True

    result = evaluate_eligibility(
        make_profile(citizenship="Canada"), sample_opportunity(citizenship_required=("Canada",))
    )
    assert check(result, "CITIZENSHIP").status == PASS

    result = evaluate_eligibility(
        make_profile(citizenship="Germany"), sample_opportunity(citizenship_required=("Canada",))
    )
    assert check(result, "CITIZENSHIP").status == FAIL


def test_enrollment_unknown_requires_verification():
    result = evaluate_eligibility(
        make_profile(currently_enrolled=None), sample_opportunity(enrollment_required=True)
    )
    enrollment = check(result, "ENROLLMENT")
    assert enrollment.status == NEEDS_VERIFICATION

    result = evaluate_eligibility(
        make_profile(currently_enrolled=True), sample_opportunity(enrollment_required=True)
    )
    assert check(result, "ENROLLMENT").status == PASS

    result = evaluate_eligibility(
        make_profile(currently_enrolled=False), sample_opportunity(enrollment_required=True)
    )
    assert check(result, "ENROLLMENT").status == FAIL


def test_status_precedence_fail_beats_verification():
    result = evaluate_eligibility(
        make_profile(citizenship="Germany"),  # CITIZENSHIP: fail
        sample_opportunity(citizenship_required=("Canada",), enrollment_required=True),
    )
    # ENROLLMENT would be needs_verification, but fail wins.
    assert result.status == STATUS_INELIGIBLE


def test_summary_lists_deciding_evidence():
    result = evaluate_eligibility(make_profile(), sample_opportunity())
    assert "Singapore" in result.summary
    assert "verified" in result.summary
