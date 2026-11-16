"""Rule-generated feature vectors for in-memory cosine retrieval.

Both the candidate profile and each opportunity are projected onto a fixed
feature space assembled from the taxonomy:

    [ skills slots | career tracks | countries | languages | numeric ]

- skills: 1.0 per canonical skill (opportunities: 1.0 required, 0.5 optional)
- tracks: 1.0 per canonical career track / stated interest
- countries: 1.0 per preferred country (candidate) / posting country (job)
- languages: proficiency rank / 5 per language
- numeric: degree rank / 6 and min(1, years / 10)

No embeddings, no learned models — pure feature engineering. Retrieval then
does cosine similarity over these vectors (see `retrieval.py`); the six-part
weighted score (see `scoring.py`) is what ultimately ranks the shortlist.
"""

import numpy as np

from app.services import taxonomy
from app.services.normalization import NormalizedOpportunity, NormalizedProfile

_SKILL_SLOTS: dict[str, int] = {skill: i for i, skill in enumerate(taxonomy.SKILLS)}
_TRACK_SLOTS: dict[str, int] = {track: i for i, track in enumerate(taxonomy.TRACKS)}
_COUNTRY_SLOTS: dict[str, int] = {c: i for i, c in enumerate(taxonomy.COUNTRIES)}
_LANGUAGE_SLOTS: dict[str, int] = {lang: i for i, lang in enumerate(taxonomy.LANGUAGES)}

#: [skills | tracks | countries | languages | degree | years]
DIMENSION: int = (
    len(_SKILL_SLOTS) + len(_TRACK_SLOTS) + len(_COUNTRY_SLOTS) + len(_LANGUAGE_SLOTS) + 2
)

_SKILL_OFFSET = 0
_TRACK_OFFSET = len(_SKILL_SLOTS)
_COUNTRY_OFFSET = _TRACK_OFFSET + len(_TRACK_SLOTS)
_LANGUAGE_OFFSET = _COUNTRY_OFFSET + len(_COUNTRY_SLOTS)
_DEGREE_INDEX = _LANGUAGE_OFFSET + len(_LANGUAGE_SLOTS)
_YEARS_INDEX = _DEGREE_INDEX + 1


def candidate_vector(profile: NormalizedProfile) -> np.ndarray:
    """Build the retrieval vector for a normalized candidate profile."""
    vector = np.zeros(DIMENSION, dtype=np.float32)
    for skill in profile.skills:
        slot = _SKILL_SLOTS.get(skill)
        if slot is not None:
            vector[_SKILL_OFFSET + slot] = 1.0
    for track in profile.career_interests:
        slot = _TRACK_SLOTS.get(track)
        if slot is not None:
            vector[_TRACK_OFFSET + slot] = 1.0
    for country in profile.preferred_countries:
        slot = _COUNTRY_SLOTS.get(country)
        if slot is not None:
            vector[_COUNTRY_OFFSET + slot] = 1.0
    for language, level in profile.languages.items():
        slot = _LANGUAGE_SLOTS.get(language)
        if slot is not None:
            vector[_LANGUAGE_OFFSET + slot] = taxonomy.LANGUAGE_RANK[level] / 5.0
    vector[_DEGREE_INDEX] = profile.degree_rank / 6.0
    vector[_YEARS_INDEX] = min(1.0, profile.experience_years / 10.0)
    return vector


def opportunity_vector(opportunity: NormalizedOpportunity) -> np.ndarray:
    """Build the retrieval vector for a normalized opportunity."""
    vector = np.zeros(DIMENSION, dtype=np.float32)
    for skill in opportunity.required_skills:
        slot = _SKILL_SLOTS.get(skill)
        if slot is not None:
            vector[_SKILL_OFFSET + slot] = 1.0
    for skill in opportunity.optional_skills:
        slot = _SKILL_SLOTS.get(skill)
        if slot is not None:
            vector[_SKILL_OFFSET + slot] = max(vector[_SKILL_OFFSET + slot], 0.5)
    for track in opportunity.career_tracks:
        slot = _TRACK_SLOTS.get(track)
        if slot is not None:
            vector[_TRACK_OFFSET + slot] = 1.0
    slot = _COUNTRY_SLOTS.get(opportunity.country)
    if slot is not None:
        vector[_COUNTRY_OFFSET + slot] = 1.0
    for language, level in opportunity.languages_required.items():
        slot = _LANGUAGE_SLOTS.get(language)
        if slot is not None:
            vector[_LANGUAGE_OFFSET + slot] = taxonomy.LANGUAGE_RANK[level] / 5.0
    vector[_DEGREE_INDEX] = taxonomy.DEGREE_RANK.get(opportunity.min_education_level, 0) / 6.0
    midpoint = (opportunity.min_years + opportunity.max_years) / 2.0
    vector[_YEARS_INDEX] = min(1.0, midpoint / 10.0)
    return vector
