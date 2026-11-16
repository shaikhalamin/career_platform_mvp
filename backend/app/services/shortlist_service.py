"""Shortlist (wishlist) business logic."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ErrorCode, NotFoundError
from app.models import ShortlistItem
from app.schemas.shortlist import ShortlistCreate


async def list_shortlist(session: AsyncSession, profile_id: int) -> list[ShortlistItem]:
    """All saved items for a profile, newest first."""
    stmt = (
        select(ShortlistItem)
        .where(ShortlistItem.profile_id == profile_id)
        .order_by(ShortlistItem.created_at.desc(), ShortlistItem.id.desc())
    )
    return list((await session.scalars(stmt)).all())


async def add_to_shortlist(session: AsyncSession, data: ShortlistCreate) -> ShortlistItem:
    """Save an opportunity for a profile; duplicates raise a 409 envelope."""
    duplicate = await session.scalar(
        select(ShortlistItem.id).where(
            ShortlistItem.profile_id == data.profile_id,
            ShortlistItem.opportunity_id == data.opportunity_id,
        )
    )
    if duplicate is not None:
        raise ConflictError(
            message=f"Opportunity {data.opportunity_id} is already shortlisted.",
            code=ErrorCode.SHORTLIST_ALREADY_EXISTS,
            details=[
                {
                    "field": "opportunity_id",
                    "message": "Already shortlisted for this profile.",
                    "code": "duplicate",
                }
            ],
        )
    item = ShortlistItem(
        profile_id=data.profile_id, opportunity_id=data.opportunity_id, note=data.note
    )
    session.add(item)
    try:
        await session.flush()
    except IntegrityError as exc:
        # Race-safe fallback against the unique pair constraint.
        await session.rollback()
        raise ConflictError(
            message=f"Opportunity {data.opportunity_id} is already shortlisted.",
            code=ErrorCode.SHORTLIST_ALREADY_EXISTS,
        ) from exc
    await session.refresh(item)
    return item


async def remove_from_shortlist(
    session: AsyncSession, profile_id: int, opportunity_id: str
) -> None:
    """Remove a saved opportunity; a missing pair raises the 404 envelope."""
    item = await session.scalar(
        select(ShortlistItem).where(
            ShortlistItem.profile_id == profile_id,
            ShortlistItem.opportunity_id == opportunity_id,
        )
    )
    if item is None:
        raise NotFoundError(
            f"Opportunity {opportunity_id} is not shortlisted for profile {profile_id}.",
            code=ErrorCode.SHORTLIST_NOT_FOUND,
        )
    await session.delete(item)
    await session.flush()
