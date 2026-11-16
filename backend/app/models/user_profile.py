"""UserProfile ORM model — identity plus the career profile the matching
pipeline consumes."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

NAME_MAX_LENGTH = 100
#: RFC 5321 forward-path limit (the practical maximum email length).
EMAIL_MAX_LENGTH = 320

#: JSON columns use JSONB (queryable, contiguous storage). The JSON cast
#: keeps Alembic autogenerate quiet about dialect-specific types.
Json = JSON().with_variant(JSONB(), "postgresql")


class UserProfile(Base):
    """A user profile: display name + unique contact email, plus the career
    attributes (education, experience, skills, languages, preferences,
    work authorisation) used for matching.

    Emails are stored lowercase (normalized in the request schemas) and
    enforced unique by a dedicated index — the service layer also checks
    duplicates ahead of the insert to return a friendly 409 envelope, the
    index remains the source of truth under concurrent writes.

    Career fields are nullable: the API requires the core matching fields on
    create, while optional facts (citizenship, enrollment, per-country work
    authorisation) may legitimately be unknown — "unknown" is meaningful
    data for the eligibility engine, never a default-satisfied value.
    """

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
    email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH), nullable=False, unique=True, index=True
    )

    # --- Career profile (matching inputs) ---
    #: DEGREE_RANK key: none|secondary|diploma|associate|bachelors|masters|doctorate
    education_level: Mapped[str] = mapped_column(String(20), nullable=False, default="none")
    #: Free-text field of study, canonicalized at match time (e.g. "business")
    education_field: Mapped[str | None] = mapped_column(String(120), nullable=True)
    experience_years: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    #: Experience areas as a JSON array, e.g. ["business operations", "project support"]
    experience_areas: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    #: Skills as entered (chips), e.g. ["Excel", "Stakeholder communication"]
    skills: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    #: {"English": "professional", "Bengali": "native"} — LANGUAGE_RANK values
    languages: Mapped[dict[str, Any]] = mapped_column(Json, nullable=False, default=dict)
    #: Preferred countries (canonical names), e.g. ["Germany", "Canada"]
    preferred_locations: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    #: Career interests as entered, e.g. ["Programme support", "Business operations"]
    career_interests: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    #: {"Germany": "unknown", ...} — authorized|not_authorized|unknown per country
    work_authorisation: Mapped[dict[str, Any]] = mapped_column(Json, nullable=False, default=dict)
    #: Canonical country name or NULL when not stated (drives verification flags)
    citizenship: Mapped[str | None] = mapped_column(String(80), nullable=True)
    #: TRUE/FALSE when stated, NULL when unknown (drives verification flags)
    currently_enrolled: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<UserProfile id={self.id} email={self.email!r}>"
