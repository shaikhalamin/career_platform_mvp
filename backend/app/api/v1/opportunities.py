"""Opportunity endpoints: browse, detail, and per-profile match analysis."""

from fastapi import APIRouter, Query

from app.core.dependencies import PaginationDep, SessionDep
from app.core.exceptions import ValidationError
from app.core.responses import ApiResponse, build_pagination_meta
from app.schemas.opportunity import OpportunityListItem, OpportunityRead
from app.schemas.recommendation import MatchDetail
from app.services import (
    opportunity_service,
    profile_service,
    recommender,
    shortlist_service,
    taxonomy,
)

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


def _require_valid_country(country: str | None) -> str | None:
    """Resolve a country filter against the taxonomy (422 on unknown)."""
    if country is None:
        return None
    canonical = taxonomy.normalize_country_key(country)
    if canonical is None:
        raise ValidationError(
            message=f"Unknown country filter: {country!r}.",
            details=[
                {"field": "country", "message": "Unknown country.", "code": "invalid_country"}
            ],
        )
    return canonical


@router.get(
    "",
    response_model=ApiResponse[list[OpportunityListItem]],
    summary="List opportunities (paginated, filterable)",
    description="Structured job and internship postings. Optionally mark "
    "shortlisted items for a profile with `profile_id`.",
)
async def list_opportunities(
    session: SessionDep,
    pagination: PaginationDep,
    country: str | None = Query(default=None, description="Filter by country."),
    track: str | None = Query(default=None, description="Filter by career track."),
    employment_type: str | None = Query(
        default=None,
        pattern="^(full_time|internship|contract|part_time)$",
        description="Filter by employment type.",
    ),
    search: str | None = Query(
        default=None, max_length=80, description="Title/organisation/city search."
    ),
    profile_id: int | None = Query(
        default=None, ge=1, description="Mark shortlisted items for this profile."
    ),
) -> ApiResponse[list[OpportunityListItem]]:
    canonical_country = _require_valid_country(country)
    items, total = await opportunity_service.list_opportunities(
        session,
        page=pagination.page,
        page_size=pagination.page_size,
        country=canonical_country,
        track=track,
        employment_type=employment_type,
        search=search,
    )
    shortlisted_ids: set[str] = set()
    if profile_id is not None:
        profile = await profile_service.get_profile(session, profile_id)
        shortlisted_ids = {
            item.opportunity_id
            for item in await shortlist_service.list_shortlist(session, profile.id)
        }
    data = [
        OpportunityListItem.from_orm_opportunity(row, shortlisted=row.id in shortlisted_ids)
        for row in items
    ]
    return ApiResponse[list[OpportunityListItem]](
        data=data,
        meta=build_pagination_meta(pagination.page, pagination.page_size, total),
    )


@router.get(
    "/{opportunity_id}",
    response_model=ApiResponse[OpportunityRead],
    summary="Get an opportunity by id",
)
async def get_opportunity(opportunity_id: str, session: SessionDep) -> ApiResponse[OpportunityRead]:
    opportunity = await opportunity_service.get_opportunity(session, opportunity_id)
    return ApiResponse[OpportunityRead](data=OpportunityRead.from_orm_opportunity(opportunity))


@router.get(
    "/{opportunity_id}/match",
    response_model=ApiResponse[MatchDetail],
    summary="Explain the match between a profile and this opportunity",
    description="Six-part score breakdown, cosine similarity and evidence-based "
    "eligibility evaluation (guidance only — not a legal determination).",
)
async def match_opportunity(
    opportunity_id: str,
    session: SessionDep,
    profile_id: int = Query(ge=1, description="Profile to evaluate against."),
) -> ApiResponse[MatchDetail]:
    opportunity = await opportunity_service.get_opportunity(session, opportunity_id)
    profile = await profile_service.get_profile(session, profile_id)
    detail = await recommender.build_match_detail(session, profile, opportunity)
    return ApiResponse[MatchDetail](data=detail)
