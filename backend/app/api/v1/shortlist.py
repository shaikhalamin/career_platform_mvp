"""Shortlist (wishlist) endpoints."""

from fastapi import APIRouter, Query, status

from app.core.dependencies import SessionDep
from app.core.responses import ApiResponse
from app.schemas.opportunity import OpportunityRead
from app.schemas.shortlist import ShortlistCreate, ShortlistItemRead
from app.services import opportunity_service, profile_service, shortlist_service

router = APIRouter(prefix="/shortlist", tags=["Shortlist"])


def _to_read(item, opportunity) -> ShortlistItemRead:
    """Compose the read model with the nested opportunity."""
    return ShortlistItemRead(
        id=item.id,
        profile_id=item.profile_id,
        opportunity=OpportunityRead.from_orm_opportunity(opportunity),
        note=item.note,
        created_at=item.created_at,
    )


@router.get(
    "",
    response_model=ApiResponse[list[ShortlistItemRead]],
    summary="List shortlisted opportunities for a profile",
)
async def list_shortlist(
    session: SessionDep,
    profile_id: int = Query(ge=1),
) -> ApiResponse[list[ShortlistItemRead]]:
    profile = await profile_service.get_profile(session, profile_id)
    items = await shortlist_service.list_shortlist(session, profile.id)
    data = []
    for item in items:
        opportunity = await opportunity_service.get_opportunity(session, item.opportunity_id)
        data.append(_to_read(item, opportunity))
    return ApiResponse[list[ShortlistItemRead]](data=data)


@router.post(
    "",
    response_model=ApiResponse[ShortlistItemRead],
    status_code=status.HTTP_201_CREATED,
    summary="Shortlist an opportunity",
    description="Saves an opportunity for the profile; duplicates return a 409 envelope.",
)
async def add_to_shortlist(
    payload: ShortlistCreate, session: SessionDep
) -> ApiResponse[ShortlistItemRead]:
    await profile_service.get_profile(session, payload.profile_id)
    opportunity = await opportunity_service.get_opportunity(session, payload.opportunity_id)
    item = await shortlist_service.add_to_shortlist(session, payload)
    return ApiResponse[ShortlistItemRead](
        data=_to_read(item, opportunity), message="Opportunity shortlisted."
    )


@router.delete(
    "/{profile_id}/{opportunity_id}",
    response_model=ApiResponse[None],
    summary="Remove an opportunity from the shortlist",
)
async def remove_from_shortlist(
    profile_id: int, opportunity_id: str, session: SessionDep
) -> ApiResponse[None]:
    await profile_service.get_profile(session, profile_id)
    await shortlist_service.remove_from_shortlist(session, profile_id, opportunity_id)
    return ApiResponse[None](data=None, message="Opportunity removed from shortlist.")
