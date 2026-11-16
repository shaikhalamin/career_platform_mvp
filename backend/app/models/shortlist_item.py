"""ShortlistItem ORM model — one saved (profile, opportunity) pair."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ShortlistItem(Base):
    """A shortlisted/wishlisted opportunity for a profile.

    Unique per (profile, opportunity): re-shortlisting an already-saved job
    is a conflict the API reports explicitly rather than silently ignoring.
    """

    __tablename__ = "shortlist_items"
    __table_args__ = (
        UniqueConstraint("profile_id", "opportunity_id", name="uq_shortlist_items_pair"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opportunity_id: Mapped[str] = mapped_column(
        ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ShortlistItem profile={self.profile_id} opportunity={self.opportunity_id!r}>"
