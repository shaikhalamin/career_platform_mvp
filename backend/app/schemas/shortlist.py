"""Request/response schemas for the shortlist (wishlist)."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.opportunity import OpportunityRead


class ShortlistCreate(BaseModel):
    """Body for `POST /shortlist`."""

    profile_id: int = Field(ge=1, examples=[1])
    opportunity_id: str = Field(examples=["J012"])
    note: str | None = Field(
        default=None, max_length=500, examples=["Great fit for programme support."]
    )


class ShortlistItemRead(BaseModel):
    """One saved opportunity with its nesting context."""

    id: int
    profile_id: int
    opportunity: OpportunityRead
    note: str | None
    created_at: datetime
