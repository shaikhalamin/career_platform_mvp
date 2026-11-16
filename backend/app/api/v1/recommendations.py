"""Recommendation endpoints: the ranked, explained match list."""

from fastapi import APIRouter, Query

from app.core.dependencies import SessionDep
from app.core.responses import ApiResponse
from app.schemas.recommendation import RecommendationList
from app.services import profile_service, recommender

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

DEFAULT_TOP_K = 20
MAX_TOP_K = 50


@router.get(
    "",
    response_model=ApiResponse[RecommendationList],
    summary="Ranked recommendations for a profile",
    description=(
        "Two-stage pipeline: FAISS cosine retrieval over rule-generated feature "
        "vectors narrows the set to `top_k`, then each candidate gets the fixed "
        "six-part weighted score (skills 35 / experience 20 / education 15 / "
        "location 15 / language 10 / interests 5) plus an independent, "
        "evidence-based eligibility evaluation. Results are recomputed from live "
        "data on every call — a profile update is reflected immediately. "
        "Eligibility output is automated guidance, not a legal determination."
    ),
)
async def get_recommendations(
    session: SessionDep,
    profile_id: int = Query(ge=1, description="Profile to match."),
    top_k: int = Query(
        default=DEFAULT_TOP_K,
        ge=1,
        le=MAX_TOP_K,
        description=f"How many opportunities to retrieve and rank (1-{MAX_TOP_K}).",
    ),
) -> ApiResponse[RecommendationList]:
    profile = await profile_service.get_profile(session, profile_id)
    result = await recommender.build_recommendations(session, profile, top_k=top_k)
    return ApiResponse[RecommendationList](
        data=result,
        message=f"Recommendations recalculated for {profile.name!r}.",
    )
