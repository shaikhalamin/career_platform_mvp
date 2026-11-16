"""Evidence-based eligibility evaluation — deliberately separate from the
100-point match score.

Hard constraints (mandatory languages on strict roles, strict degree or
experience requirements, work authorisation, citizenship, enrollment) are
checked here and reported with explicit evidence strings. Missing
information never silently counts as satisfied: an unknown work-authorisation
or citizenship value yields `needs_verification`, which the API surfaces as
a visible "requires verification" flag — never as a confirmed status.

This engine produces automated guidance only. It is not, and must not be
presented as, a legal determination of visa or work-authorisation
entitlement (see `taxonomy.ELIGIBILITY_DISCLAIMER`).
"""

from dataclasses import dataclass, field

from app.services import taxonomy
from app.services.normalization import NormalizedOpportunity, NormalizedProfile

#: Outcome per check and overall.
PASS = "pass"
FAIL = "fail"
NEEDS_VERIFICATION = "needs_verification"
NOT_APPLICABLE = "not_applicable"

#: Overall statuses (also API enum values).
STATUS_ELIGIBLE = "eligible"
STATUS_NEEDS_VERIFICATION = "needs_verification"
STATUS_INELIGIBLE = "ineligible"

_STATUS_LABELS = {
    STATUS_ELIGIBLE: "Eligible (automated check)",
    STATUS_NEEDS_VERIFICATION: "Requires verification",
    STATUS_INELIGIBLE: "Eligibility concern",
}


@dataclass(slots=True)
class EligibilityCheck:
    """One hard-constraint evaluation with its evidence."""

    # WORK_AUTHORIZATION | LANGUAGE_REQUIREMENTS | EDUCATION | EXPERIENCE |
    # CITIZENSHIP | ENROLLMENT
    code: str
    label: str
    status: str  # pass | fail | needs_verification | not_applicable
    evidence: str
    requires_verification: bool = False


@dataclass(slots=True)
class EligibilityResult:
    """Aggregate eligibility outcome for one (profile, opportunity) pair."""

    status: str  # eligible | needs_verification | ineligible
    checks: list[EligibilityCheck] = field(default_factory=list)

    @property
    def status_label(self) -> str:
        return _STATUS_LABELS[self.status]

    @property
    def is_eligible(self) -> bool:
        return self.status == STATUS_ELIGIBLE

    @property
    def summary(self) -> str:
        """One-line human summary of the deciding evidence."""
        if self.status == STATUS_ELIGIBLE:
            return "All automated hard-constraint checks passed."
        reasons = [
            check.evidence for check in self.checks if check.status in (FAIL, NEEDS_VERIFICATION)
        ]
        return " ".join(reasons) if reasons else "No blocking evidence recorded."


def evaluate_eligibility(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> EligibilityResult:
    """Run every hard-constraint check; precedence fail > needs_verification."""
    checks = [
        _check_work_authorization(profile, opportunity),
        _check_language_requirements(profile, opportunity),
        _check_education(profile, opportunity),
        _check_experience(profile, opportunity),
        _check_citizenship(profile, opportunity),
        _check_enrollment(profile, opportunity),
    ]
    statuses = {check.status for check in checks}
    if FAIL in statuses:
        status = STATUS_INELIGIBLE
    elif NEEDS_VERIFICATION in statuses:
        status = STATUS_NEEDS_VERIFICATION
    else:
        status = STATUS_ELIGIBLE
    return EligibilityResult(status=status, checks=checks)


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------


def _check_work_authorization(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> EligibilityCheck:
    """Local work authorisation for the posting country.

    Stated values map to pass/fail; *unknown or missing* values are flagged
    for verification — never treated as authorized.
    """
    code = "WORK_AUTHORIZATION"
    label = f"Work authorisation — {opportunity.country}"
    if not opportunity.local_work_authorization_required:
        return EligibilityCheck(
            code=code,
            label=label,
            status=NOT_APPLICABLE,
            evidence="This role does not require pre-existing local work authorisation.",
        )
    value = profile.work_authorisation.get(opportunity.country)
    if value == "authorized":
        return EligibilityCheck(
            code=code,
            label=label,
            status=PASS,
            evidence=(
                f"You stated you hold work authorisation for {opportunity.country}. "
                "Scope and validity must still be confirmed with the employer — "
                "this is not a legal determination."
            ),
        )
    if value == "not_authorized":
        return EligibilityCheck(
            code=code,
            label=label,
            status=FAIL,
            evidence=(
                f"You stated you do not hold work authorisation for {opportunity.country}, "
                "which this role requires. Visa sponsorship may be needed — confirm "
                "with the employer."
            ),
        )
    # unknown or missing
    return EligibilityCheck(
        code=code,
        label=label,
        status=NEEDS_VERIFICATION,
        requires_verification=True,
        evidence=(
            f"Your work authorisation for {opportunity.country} is unknown — this "
            "role requires local work authorisation, so your status must be "
            "verified before applying (no inferred or confirmed status is assumed)."
        ),
    )


def _check_language_requirements(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> EligibilityCheck:
    """Mandatory language requirements (roles flagged `strict_language`).

    Non-strict roles surface language gaps through the weighted score
    instead; this check reports not_applicable for them.
    """
    code = "LANGUAGE_REQUIREMENTS"
    label = "Mandatory languages"
    if not opportunity.strict_language or not opportunity.languages_required:
        return EligibilityCheck(
            code=code,
            label=label,
            status=NOT_APPLICABLE,
            evidence="No strictly mandatory language requirements for this role.",
        )
    gaps: list[str] = []
    for language, required_level in sorted(opportunity.languages_required.items()):
        required_rank = taxonomy.LANGUAGE_RANK[required_level]
        user_rank = profile.language_rank(language)
        required_label = taxonomy.LANGUAGE_LEVEL_LABELS[required_level]
        if user_rank < required_rank:
            user_label = taxonomy.LANGUAGE_LEVEL_LABELS[taxonomy.language_level_for_rank(user_rank)]
            gaps.append(f"{language} required at {required_label} level (you: {user_label})")
    if not gaps:
        return EligibilityCheck(
            code=code,
            label=label,
            status=PASS,
            evidence="You meet all mandatory language requirements.",
        )
    return EligibilityCheck(
        code=code,
        label=label,
        status=FAIL,
        evidence="Mandatory language requirement not met: " + "; ".join(gaps) + ".",
    )


def _check_education(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> EligibilityCheck:
    """Strict minimum degree requirement (some roles hard-require it)."""
    code = "EDUCATION"
    label = "Education requirement"
    if not opportunity.strict_education:
        return EligibilityCheck(
            code=code,
            label=label,
            status=NOT_APPLICABLE,
            evidence=(
                "No strict education requirement for this role (relevance is scored, not enforced)."
            ),
        )
    required_rank = taxonomy.DEGREE_RANK[opportunity.min_education_level]
    required_label = taxonomy.DEGREE_LEVEL_LABELS[opportunity.min_education_level]
    if profile.degree_rank >= required_rank:
        return EligibilityCheck(
            code=code,
            label=label,
            status=PASS,
            evidence=f"Your education level meets the strict requirement ({required_label}).",
        )
    user_label = taxonomy.DEGREE_LEVEL_LABELS[taxonomy.degree_level_for_rank(profile.degree_rank)]
    return EligibilityCheck(
        code=code,
        label=label,
        status=FAIL,
        evidence=(f"This role strictly requires {required_label} or above (you: {user_label})."),
    )


def _check_experience(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> EligibilityCheck:
    """Strict experience window (some roles hard-enforce min/max years)."""
    code = "EXPERIENCE"
    label = "Experience requirement"
    if not opportunity.strict_experience:
        return EligibilityCheck(
            code=code,
            label=label,
            status=NOT_APPLICABLE,
            evidence=(
                "No strict experience requirement for this role "
                "(alignment is scored, not enforced)."
            ),
        )
    years = profile.experience_years
    if opportunity.min_years <= years <= opportunity.max_years:
        return EligibilityCheck(
            code=code,
            label=label,
            status=PASS,
            evidence=(
                f"Your {years:g} years of experience is within the required "
                f"{opportunity.min_years:g}-{opportunity.max_years:g} years."
            ),
        )
    if years < opportunity.min_years:
        return EligibilityCheck(
            code=code,
            label=label,
            status=FAIL,
            evidence=(
                f"This role strictly requires at least {opportunity.min_years:g} years "
                f"of experience (you: {years:g})."
            ),
        )
    return EligibilityCheck(
        code=code,
        label=label,
        status=FAIL,
        evidence=(
            f"This role is capped at {opportunity.max_years:g} years of experience "
            f"(you: {years:g}) — it targets an earlier career stage."
        ),
    )


def _check_citizenship(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> EligibilityCheck:
    """Citizenship-restricted roles. Unknown citizenship -> verification."""
    code = "CITIZENSHIP"
    label = "Citizenship requirement"
    if not opportunity.citizenship_required:
        return EligibilityCheck(
            code=code,
            label=label,
            status=NOT_APPLICABLE,
            evidence="No citizenship requirement for this role.",
        )
    allowed = " or ".join(opportunity.citizenship_required)
    if profile.citizenship is None:
        return EligibilityCheck(
            code=code,
            label=label,
            status=NEEDS_VERIFICATION,
            requires_verification=True,
            evidence=(
                f"This role is restricted to {allowed} citizens and your citizenship "
                "is not stated — verify whether you qualify before applying."
            ),
        )
    if profile.citizenship in opportunity.citizenship_required:
        return EligibilityCheck(
            code=code,
            label=label,
            status=PASS,
            evidence=f"You stated {profile.citizenship} citizenship, which this role requires.",
        )
    return EligibilityCheck(
        code=code,
        label=label,
        status=FAIL,
        evidence=(
            f"This role is restricted to {allowed} citizens (you stated {profile.citizenship})."
        ),
    )


def _check_enrollment(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> EligibilityCheck:
    """Enrollment-gated roles (e.g. internships). Unknown -> verification."""
    code = "ENROLLMENT"
    label = "Current enrollment"
    if not opportunity.enrollment_required:
        return EligibilityCheck(
            code=code,
            label=label,
            status=NOT_APPLICABLE,
            evidence="This role does not require current enrollment.",
        )
    if profile.currently_enrolled is None:
        return EligibilityCheck(
            code=code,
            label=label,
            status=NEEDS_VERIFICATION,
            requires_verification=True,
            evidence=(
                "This opportunity is only open to currently enrolled students and "
                "your enrollment status is not stated — verify before applying."
            ),
        )
    if profile.currently_enrolled:
        return EligibilityCheck(
            code=code,
            label=label,
            status=PASS,
            evidence="You stated you are currently enrolled, which this role requires.",
        )
    return EligibilityCheck(
        code=code,
        label=label,
        status=FAIL,
        evidence="This opportunity requires current enrollment, which your profile does not have.",
    )
