"""Recommendation orchestration: the two-stage matching pipeline.

Stage 1 — Retrieval. Rule-generated feature vectors (vectors.py) feed an
in-memory FAISS cosine-similarity index (retrieval.py) that narrows the
opportunity set to the top-K most similar postings for the profile.

Stage 2 — Evaluation. Every retrieved opportunity gets the fixed six-part
weighted score (scoring.py) plus an independent evidence-based eligibility
evaluation (eligibility.py).

Ranking: eligibility tier first (eligible → needs verification → ineligible
— constrained roles stay visible but sort below clean matches), then total
score, then cosine similarity, then id for determinism.

Recommendations are computed from live data on every request, so a profile
update is reflected immediately — nothing to invalidate, no stale cache.
"""

import logging
from datetime import UTC, datetime

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity, ShortlistItem, UserProfile
from app.schemas.opportunity import OpportunitySummary
from app.schemas.recommendation import (
    DimensionScoreRead,
    EligibilityCheckRead,
    EligibilityRead,
    MatchDetail,
    RecommendationItem,
    RecommendationList,
)
from app.services import taxonomy, vectors
from app.services.eligibility import (
    STATUS_ELIGIBLE,
    STATUS_INELIGIBLE,
    STATUS_NEEDS_VERIFICATION,
    evaluate_eligibility,
)
from app.services.normalization import (
    NormalizedOpportunity,
    normalize_opportunity,
    normalize_profile,
)
from app.services.retrieval import FaissRetriever
from app.services.scoring import score_match

logger = logging.getLogger("app.services.recommender")

#: Eligibility tier used for ranking (lower sorts first).
_TIER_ORDER = {STATUS_ELIGIBLE: 0, STATUS_NEEDS_VERIFICATION: 1, STATUS_INELIGIBLE: 2}

#: Module-level FAISS index cache. Keyed by a cheap version signature
#: (row count + max updated_at); rebuilt only when the opportunity set
#: changes. 50 x ~80-dim vectors rebuild in well under a millisecond, so
#: even a forced rebuild per request would be fine — the cache exists to
#: keep "in-memory index" literal across requests.
_index_cache: dict[str, tuple[FaissRetriever, dict[str, NormalizedOpportunity]]] = {}


async def _load_index(
    session: AsyncSession,
) -> tuple[FaissRetriever, dict[str, NormalizedOpportunity]]:
    """Return the (cached) FAISS retriever + normalized opportunities."""
    rows = list((await session.scalars(select(Opportunity).order_by(Opportunity.id))).all())
    if not rows:
        raise ValueError("No opportunities available to build the retrieval index")
    version = f"{len(rows)}:{max(r.updated_at for r in rows).isoformat()}"
    cached = _index_cache.get(version)
    if cached is not None:
        return cached
    normalized = {row.id: normalize_opportunity(row) for row in rows}
    matrix = np.stack([vectors.opportunity_vector(opp) for opp in normalized.values()])
    retriever = FaissRetriever(matrix, list(normalized.keys()))
    _index_cache.clear()  # single-entry cache: only the current set matters
    _index_cache[version] = (retriever, normalized)
    return retriever, normalized


def _normalize_profile_from_orm(profile: UserProfile):
    """Normalize a UserProfile ORM row into the matching representation."""
    return normalize_profile(
        education_level=profile.education_level,
        education_field=profile.education_field,
        experience_years=profile.experience_years,
        experience_areas=list(profile.experience_areas or []),
        skills=list(profile.skills or []),
        languages=dict(profile.languages or {}),
        preferred_locations=list(profile.preferred_locations or []),
        career_interests=list(profile.career_interests or []),
        work_authorisation=dict(profile.work_authorisation or {}),
        citizenship=profile.citizenship,
        currently_enrolled=profile.currently_enrolled,
    )


def _to_eligibility_read(result) -> EligibilityRead:
    return EligibilityRead(
        status=result.status,
        status_label=result.status_label,
        eligible=result.is_eligible,
        summary=result.summary,
        checks=[
            EligibilityCheckRead(
                code=check.code,
                label=check.label,
                status=check.status,
                evidence=check.evidence,
                requires_verification=check.requires_verification,
            )
            for check in result.checks
        ],
    )


def _evaluate_one(
    profile_normalized,
    opportunity_orm,
    opportunity_normalized: NormalizedOpportunity,
    cosine: float,
) -> tuple[tuple[int, float, float, str], object, object]:
    """Score + eligibility for one pair; returns components for sorting."""
    match = score_match(profile_normalized, opportunity_normalized)
    eligibility = evaluate_eligibility(profile_normalized, opportunity_normalized)
    return (
        (
            _TIER_ORDER[eligibility.status],
            -match.total,  # ascending sort == descending score
            -cosine,
            opportunity_orm.id,
        ),
        match,
        eligibility,
    )


async def build_recommendations(
    session: AsyncSession, profile: UserProfile, *, top_k: int
) -> RecommendationList:
    """Run the full pipeline for one profile and return the ranked list."""
    retriever, normalized = await _load_index(session)
    profile_normalized = _normalize_profile_from_orm(profile)
    query = vectors.candidate_vector(profile_normalized)

    retrieved = retriever.search(query, top_k)
    shortlisted_ids = set(
        await session.scalars(
            select(ShortlistItem.opportunity_id).where(ShortlistItem.profile_id == profile.id)
        )
    )

    evaluated: list[tuple[dict[str, float], RecommendationItem]] = []
    rows_by_id = await _rows_by_id(session, [opportunity_id for opportunity_id, _ in retrieved])
    for opportunity_id, cosine in retrieved:
        row = rows_by_id.get(opportunity_id)
        if row is None:
            continue
        opp_normalized = normalized[opportunity_id]
        sort_key, match, eligibility = _evaluate_one(
            profile_normalized, row, opp_normalized, cosine
        )
        item = RecommendationItem(
            rank=0,  # assigned after final sorting
            opportunity=OpportunitySummary.from_orm_opportunity(row),
            total_score=match.total,
            max_score=match.max_score,
            cosine_similarity=round(cosine, 4),
            score_breakdown=[
                DimensionScoreRead(
                    key=dimension.key,
                    label=dimension.label,
                    score=dimension.score,
                    max_points=dimension.max_points,
                    percentage=dimension.percentage,
                    matched=dimension.matched,
                    missing=dimension.missing,
                    notes=dimension.notes,
                )
                for dimension in match.dimensions
            ],
            eligibility=_to_eligibility_read(eligibility),
            strengths=match.strengths,
            gaps=match.gaps,
            shortlisted=opportunity_id in shortlisted_ids,
        )
        evaluated.append((sort_key, item))

    # Final ranking: eligibility tier, then score, then cosine, then id.
    evaluated.sort(key=lambda pair: pair[0])  # tuple keys compare directly
    items = [item for _, item in evaluated]
    for position, item in enumerate(items, start=1):
        item.rank = position
    return RecommendationList(
        profile_id=profile.id,
        profile_name=profile.name,
        generated_at=datetime.now(UTC),
        top_k=top_k,
        total_opportunities=retriever.size,
        retrieved_count=len(items),
        disclaimer=taxonomy.ELIGIBILITY_DISCLAIMER,
        items=items,
    )


async def build_match_detail(
    session: AsyncSession, profile: UserProfile, opportunity: Opportunity
) -> MatchDetail:
    """Score a single (profile, opportunity) pair — the job detail view."""
    retriever, normalized = await _load_index(session)
    profile_normalized = _normalize_profile_from_orm(profile)
    opp_normalized = normalized.get(opportunity.id) or normalize_opportunity(opportunity)

    # Exact cosine for this pair (recompute against the index vectors rather
    # than reusing the candidate's top-K, which may not contain this job).
    query = vectors.candidate_vector(profile_normalized)
    target = vectors.opportunity_vector(opp_normalized)
    cosine = float(np.dot(query, target) / (np.linalg.norm(query) * np.linalg.norm(target) + 1e-12))

    match = score_match(profile_normalized, opp_normalized)
    eligibility = evaluate_eligibility(profile_normalized, opp_normalized)
    shortlisted = (
        await session.scalar(
            select(ShortlistItem.id).where(
                ShortlistItem.profile_id == profile.id,
                ShortlistItem.opportunity_id == opportunity.id,
            )
        )
    ) is not None
    _ = retriever  # index only guarantees the normalized set is warm
    return MatchDetail(
        opportunity_id=opportunity.id,
        profile_id=profile.id,
        total_score=match.total,
        max_score=match.max_score,
        cosine_similarity=round(cosine, 4),
        score_breakdown=[
            DimensionScoreRead(
                key=dimension.key,
                label=dimension.label,
                score=dimension.score,
                max_points=dimension.max_points,
                percentage=dimension.percentage,
                matched=dimension.matched,
                missing=dimension.missing,
                notes=dimension.notes,
            )
            for dimension in match.dimensions
        ],
        eligibility=_to_eligibility_read(eligibility),
        strengths=match.strengths,
        gaps=match.gaps,
        shortlisted=shortlisted,
        disclaimer=taxonomy.ELIGIBILITY_DISCLAIMER,
    )


async def _rows_by_id(session: AsyncSession, ids: list[str]) -> dict[str, Opportunity]:
    if not ids:
        return {}
    rows = await session.scalars(select(Opportunity).where(Opportunity.id.in_(ids)))
    return {row.id: row for row in rows}
