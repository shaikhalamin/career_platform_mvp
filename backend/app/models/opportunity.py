"""Opportunity ORM model — a structured job/internship posting."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.user_profile import Json

TITLE_MAX_LENGTH = 160
ORG_MAX_LENGTH = 140


class Opportunity(Base):
    """A job or internship opportunity with structured requirements.

    Requirement fields are plain JSON (seed data is already structured);
    `normalize_opportunity` canonicalizes them at match time. The three
    `strict_*` flags move a requirement from "scored gap" to "hard
    eligibility constraint" (see services/eligibility.py).
    """

    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH), nullable=False)
    organisation: Mapped[str] = mapped_column(String(ORG_MAX_LENGTH), nullable=False)
    #: Canonical country name (taxonomy.COUNTRIES)
    country: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    city: Mapped[str | None] = mapped_column(String(80), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    #: full_time | internship | contract | part_time
    employment_type: Mapped[str] = mapped_column(String(20), nullable=False, default="full_time")

    # --- Requirements ---
    required_skills: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    optional_skills: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    min_years: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    max_years: Mapped[float] = mapped_column(Float, nullable=False, default=99.0)
    experience_areas: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    #: DEGREE_RANK key
    min_education_level: Mapped[str] = mapped_column(String(20), nullable=False, default="none")
    #: Canonical field keys, e.g. ["business", "economics"]
    relevant_fields: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    #: {"English": "professional"} — minimum LANGUAGE_RANK per language
    languages_required: Mapped[dict[str, Any]] = mapped_column(Json, nullable=False, default=dict)
    #: Canonical track keys, e.g. ["project coordination"]
    career_tracks: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)

    # --- Eligibility constraints (hard checks when enabled) ---
    #: Role requires pre-existing authorisation to work in `country`
    local_work_authorization_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    #: Restricted citizenship list (empty = open); NULL would mean "unknown"
    citizenship_required: Mapped[list[Any]] = mapped_column(Json, nullable=False, default=list)
    #: Only currently enrolled students may apply (typically internships)
    enrollment_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #: Language requirements are mandatory (fail) rather than scored gaps
    strict_language: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #: Minimum education level is a hard requirement
    strict_education: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #: Experience window is a hard requirement
    strict_experience: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

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
        return f"<Opportunity id={self.id} title={self.title!r} country={self.country!r}>"
