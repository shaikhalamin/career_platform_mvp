"""Fixed six-part weighted scoring engine (100 points total).

    Skills 35 + Experience 20 + Education 15 + Location 15 + Language 10
    + Interests 5

Every dimension returns a `DimensionScore` carrying the points awarded, the
maximum, matched/missing items and plain-language notes — so any
recommendation's total can be reconstructed and explained point by point.
Scores are independent of eligibility: a role can score highly and still
carry a hard-constraint flag (eligibility.py owns that judgement).

Within-dimension rules (documented per function):
- Skills: 80% required-skill coverage + 20% optional-skill coverage.
- Experience: 14 pts years alignment (in-range full, below-min pro-rata,
  above-max 75% "overqualified but capable") + 6 pts area overlap.
- Education: 10 pts level (met full / one level below 6 / further below 2)
  + 5 pts field relevance.
- Location: preferred country 15 / same region as a preference 8 / else 0.
- Language: mean per-language ratio of your rank to the required rank.
- Interests: overlap of stated interests with the role's career tracks.
"""

from dataclasses import dataclass, field

from app.services import taxonomy
from app.services.normalization import NormalizedOpportunity, NormalizedProfile

#: Strength/gap thresholds on a dimension's percentage (0-100).
STRENGTH_THRESHOLD = 80.0


@dataclass(slots=True)
class DimensionScore:
    """Points awarded for one dimension, with its evidence."""

    key: str  # skills | experience | education | location | language | interests
    label: str
    score: float
    max_points: float
    matched: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        return round(self.score / self.max_points * 100, 1) if self.max_points else 0.0


@dataclass(slots=True)
class MatchScore:
    """Aggregate six-part score for one (profile, opportunity) pair."""

    total: float
    max_score: float
    dimensions: list[DimensionScore]

    @property
    def by_key(self) -> dict[str, DimensionScore]:
        return {dimension.key: dimension for dimension in self.dimensions}

    @property
    def strengths(self) -> list[str]:
        """Dimension-level strengths: strong dimensions with evidence."""
        strengths = []
        for dimension in self.dimensions:
            if dimension.percentage >= STRENGTH_THRESHOLD and dimension.max_points > 0:
                detail = ""
                if dimension.matched:
                    shown = ", ".join(dimension.matched[:3])
                    more = len(dimension.matched) - 3
                    detail = f" ({shown}" + (f" +{more} more" if more > 0 else "") + ")"
                strengths.append(f"{dimension.label}: {dimension.percentage:.0f}%{detail}")
        return strengths

    @property
    def gaps(self) -> list[str]:
        """Dimension-level gaps: missing items and notes for weak dimensions.

        Notes from strong dimensions (e.g. "2 yrs is within the window")
        belong to the explanation, not the gap list.
        """
        gaps = []
        for dimension in self.dimensions:
            if dimension.missing:
                shown = ", ".join(dimension.missing[:3])
                more = len(dimension.missing) - 3
                gaps.append(
                    f"{dimension.label}: missing {shown}" + (f" +{more} more" if more > 0 else "")
                )
            elif dimension.percentage < STRENGTH_THRESHOLD and dimension.max_points >= 10:
                gaps.append(f"{dimension.label}: {dimension.percentage:.0f}% of maximum")
            if dimension.percentage < STRENGTH_THRESHOLD:
                gaps.extend(dimension.notes)
        return gaps

    @property
    def notes(self) -> list[str]:
        return [note for dimension in self.dimensions for note in dimension.notes]


def score_match(profile: NormalizedProfile, opportunity: NormalizedOpportunity) -> MatchScore:
    """Compute the full six-part score for one (profile, opportunity) pair."""
    dimensions = [
        _score_skills(profile, opportunity),
        _score_experience(profile, opportunity),
        _score_education(profile, opportunity),
        _score_location(profile, opportunity),
        _score_language(profile, opportunity),
        _score_interests(profile, opportunity),
    ]
    total = round(sum(dimension.score for dimension in dimensions), 1)
    return MatchScore(
        total=total, max_score=float(sum(taxonomy.WEIGHTS.values())), dimensions=dimensions
    )


# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------


def _score_skills(profile: NormalizedProfile, opportunity: NormalizedOpportunity) -> DimensionScore:
    """Skills (35): 0.8 x required coverage + 0.2 x optional coverage."""
    weight = taxonomy.WEIGHTS["skills"]
    user_skills = set(profile.skills)
    required = list(opportunity.required_skills)
    optional = list(opportunity.optional_skills)

    matched_required = [skill for skill in required if skill in user_skills]
    missing_required = [skill for skill in required if skill not in user_skills]
    matched_optional = [skill for skill in optional if skill in user_skills]

    required_coverage = len(matched_required) / len(required) if required else 1.0
    optional_coverage = len(matched_optional) / len(optional) if optional else 1.0
    score = round(weight * (0.8 * required_coverage + 0.2 * optional_coverage), 1)

    notes = []
    if not required:
        notes.append("Role lists no hard required skills — full skills credit.")
    return DimensionScore(
        key="skills",
        label="Skills",
        score=score,
        max_points=weight,
        matched=matched_required + matched_optional,
        missing=missing_required,
        notes=notes,
    )


def _score_experience(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> DimensionScore:
    """Experience (20): 14 pts years window + 6 pts area overlap."""
    years = profile.experience_years
    min_years, max_years = opportunity.min_years, opportunity.max_years

    years_notes: list[str] = []
    if min_years <= years <= max_years:
        years_score = 14.0
        # In-range is not a gap; a positive note here would leak into the
        # gap list when area misses drag the dimension below threshold.
    elif years < min_years:
        years_score = round(14.0 * (years / min_years), 1) if min_years > 0 else 14.0
        years_notes.append(f"{years:g} yrs is below the required {min_years:g} yrs.")
    else:
        years_score = 10.5  # over the window but demonstrably capable
        years_notes.append(
            f"{years:g} yrs exceeds the {min_years:g}-{max_years:g} yr window (seniority mismatch)."
        )

    job_areas = list(opportunity.experience_areas)
    if job_areas:
        user_areas = set(profile.experience_areas) | set(profile.skills)
        matched_areas = [area for area in job_areas if area in user_areas]
        missing_areas = [area for area in job_areas if area not in user_areas]
        area_score = round(6.0 * len(matched_areas) / len(job_areas), 1)
    else:
        matched_areas, missing_areas = [], []
        area_score = 6.0  # no stated areas → not restrictive

    return DimensionScore(
        key="experience",
        label="Experience",
        score=round(years_score + area_score, 1),
        max_points=taxonomy.WEIGHTS["experience"],
        matched=matched_areas,
        missing=missing_areas,
        notes=years_notes,
    )


def _score_education(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> DimensionScore:
    """Education (15): 10 pts level alignment + 5 pts field relevance."""
    required_rank = taxonomy.DEGREE_RANK[opportunity.min_education_level]
    user_rank = profile.degree_rank
    required_label = taxonomy.DEGREE_LEVEL_LABELS[opportunity.min_education_level]

    deficit = required_rank - user_rank
    if deficit <= 0:
        level_score = 10.0
        note = f"Education meets the {required_label} requirement."
    elif deficit == 1:
        level_score = 6.0
        note = f"Education is one level below the {required_label} requirement."
    else:
        level_score = 2.0
        note = f"Education is well below the {required_label} requirement."

    fields = list(opportunity.relevant_fields)
    if not fields:
        field_score = 5.0
        field_matched: list[str] = []
        note += " No specific field of study required."
    elif profile.education_field and profile.education_field in fields:
        field_score = 5.0
        field_matched = [profile.education_field]
    else:
        field_score = 0.0
        field_matched = []
        stated = profile.education_field or "unstated"
        note += f" Field relevance unclear (yours: {stated}; role wants: {', '.join(fields)})."

    return DimensionScore(
        key="education",
        label="Education",
        score=round(level_score + field_score, 1),
        max_points=taxonomy.WEIGHTS["education"],
        matched=field_matched,
        missing=[],
        notes=[note],
    )


def _score_location(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> DimensionScore:
    """Location (15): preferred country 15 / same region 8 / elsewhere 0."""
    weight = taxonomy.WEIGHTS["location"]
    country = opportunity.country
    if country in profile.preferred_countries:
        score = float(weight)
        note = f"{country} is one of your preferred locations."
        matched = [country]
    else:
        job_region = taxonomy.COUNTRY_REGIONS.get(country)
        preferred_regions = {
            taxonomy.COUNTRY_REGIONS.get(preferred) for preferred in profile.preferred_countries
        }
        if job_region and job_region in preferred_regions:
            score = 8.0
            note = (
                f"{country} is outside your preferred countries but in your "
                f"preferred region ({job_region})."
            )
            matched = []
        else:
            score = 0.0
            note = f"{country} is outside your preferred countries and regions."
            matched = []
    return DimensionScore(
        key="location",
        label="Location",
        score=score,
        max_points=weight,
        matched=matched,
        missing=[],
        notes=[note],
    )


def _score_language(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> DimensionScore:
    """Language (10): mean ratio of your rank to each required rank."""
    weight = taxonomy.WEIGHTS["language"]
    required = opportunity.languages_required
    if not required:
        return DimensionScore(
            key="language",
            label="Language",
            score=float(weight),
            max_points=weight,
            matched=[],
            missing=[],
            notes=["Role states no language requirements."],
        )
    matched: list[str] = []
    missing: list[str] = []
    ratios: list[float] = []
    for language, required_level in sorted(required.items()):
        required_rank = taxonomy.LANGUAGE_RANK[required_level]
        user_rank = profile.language_rank(language)
        if user_rank >= required_rank:
            ratios.append(1.0)
            matched.append(f"{language} ({taxonomy.LANGUAGE_LEVEL_LABELS[required_level]}+)")
        else:
            ratios.append(user_rank / required_rank if required_rank else 1.0)
            user_label = taxonomy.LANGUAGE_LEVEL_LABELS[taxonomy.language_level_for_rank(user_rank)]
            missing.append(
                f"{language} at {taxonomy.LANGUAGE_LEVEL_LABELS[required_level]} "
                f"level (you: {user_label})"
            )
    score = round(weight * sum(ratios) / len(ratios), 1)
    return DimensionScore(
        key="language",
        label="Language",
        score=score,
        max_points=weight,
        matched=matched,
        missing=missing,
    )


def _score_interests(
    profile: NormalizedProfile, opportunity: NormalizedOpportunity
) -> DimensionScore:
    """Interests (5): overlap of stated interests with the role's tracks."""
    weight = taxonomy.WEIGHTS["interests"]
    tracks = list(opportunity.career_tracks)
    if not tracks:
        return DimensionScore(
            key="interests",
            label="Career interests",
            score=float(weight),
            max_points=weight,
            notes=["Role does not tag specific career tracks — full interest credit."],
        )
    interests = set(profile.career_interests)
    matched = [track for track in tracks if track in interests]
    score = round(weight * len(matched) / len(tracks), 1)
    return DimensionScore(
        key="interests",
        label="Career interests",
        score=score,
        max_points=weight,
        matched=matched,
        missing=[track for track in tracks if track not in interests],
    )
