"""User profile business logic.

Routers stay thin (parse/validate → delegate → envelope); all profile
queries and rules live here. The request session is committed by the
`get_db` dependency after a successful request — this service flushes
(never commits) so constraint violations surface inside the request where
they are mapped to clean error envelopes.
"""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ErrorCode, NotFoundError, ValidationError
from app.models.user_profile import UserProfile
from app.schemas.profile import ProfileCreate, ProfileUpdate


async def get_profile(session: AsyncSession, profile_id: int) -> UserProfile:
    """Return the profile or raise the standard 404 envelope error."""
    profile = await session.get(UserProfile, profile_id)
    if profile is None:
        raise NotFoundError(f"Profile {profile_id} not found.", code=ErrorCode.PROFILE_NOT_FOUND)
    return profile


async def list_profiles(
    session: AsyncSession, *, page: int, page_size: int
) -> tuple[list[UserProfile], int]:
    """Return one page of profiles ordered by id plus the total count."""
    total = await session.scalar(select(func.count()).select_from(UserProfile))
    stmt = (
        select(UserProfile).order_by(UserProfile.id).offset((page - 1) * page_size).limit(page_size)
    )
    items = list((await session.scalars(stmt)).all())
    return items, total or 0


async def create_profile(session: AsyncSession, data: ProfileCreate) -> UserProfile:
    """Create a profile; a taken email raises the 409 envelope error."""
    await _ensure_email_available(session, data.email)
    profile = UserProfile(
        name=data.name,
        email=data.email,
        education_level=data.education_level,
        education_field=data.education_field,
        experience_years=data.experience_years,
        experience_areas=list(data.experience_areas),
        skills=list(data.skills),
        languages=dict(data.languages),
        preferred_locations=list(data.preferred_locations),
        career_interests=list(data.career_interests),
        work_authorisation=dict(data.work_authorisation),
        citizenship=data.citizenship,
        currently_enrolled=data.currently_enrolled,
    )
    session.add(profile)
    try:
        await session.flush()
    except IntegrityError as exc:
        # Race-safe fallback: a concurrent insert can pass the check above
        # and still hit the unique index here.
        await session.rollback()
        raise _email_conflict() from exc
    await session.refresh(profile)  # load server defaults (timestamps)
    return profile


#: Career columns on UserProfile (PATCH semantics differ from name/email:
#: an explicit null clears nullable fields instead of meaning "no change").
_CAREER_FIELDS = frozenset(
    {
        "education_level",
        "education_field",
        "experience_years",
        "experience_areas",
        "skills",
        "languages",
        "preferred_locations",
        "career_interests",
        "work_authorisation",
        "citizenship",
        "currently_enrolled",
    }
)

#: Career fields that are NOT nullable — an explicit null is rejected.
_REQUIRED_CAREER_FIELDS = frozenset(
    {
        "education_level",
        "experience_years",
        "skills",
        "languages",
        "preferred_locations",
    }
)


async def update_profile(
    session: AsyncSession, profile_id: int, updates: ProfileUpdate
) -> UserProfile:
    """Apply a partial update.

    `name`/`email`: null means no change. Career fields: presence means
    change — null clears nullable fields and is rejected for required ones
    (the schemas make those non-nullable, so this is a defensive check).
    """
    profile = await get_profile(session, profile_id)
    changes = updates.model_dump(exclude_unset=True)
    if "email" in changes and changes["email"] is not None:
        await _ensure_email_available(session, changes["email"], exclude_id=profile_id)
    for field, value in changes.items():
        if field in _CAREER_FIELDS and value is None and field in _REQUIRED_CAREER_FIELDS:
            raise ValidationError(
                message=f"Field '{field}' cannot be cleared (it is required for matching).",
                details=[{"field": field, "message": "This field is required.", "code": "null"}],
            )
        if field in ("name", "email") and value is None:
            continue  # null = no change for identity fields
        setattr(profile, field, value)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise _email_conflict() from exc
    await session.refresh(profile)
    return profile


async def delete_profile(session: AsyncSession, profile_id: int) -> None:
    """Delete the profile; a missing id raises the 404 envelope error."""
    profile = await get_profile(session, profile_id)
    await session.delete(profile)
    await session.flush()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _email_conflict() -> ConflictError:
    return ConflictError(
        message="A profile with this email already exists.",
        code=ErrorCode.EMAIL_ALREADY_REGISTERED,
        details=[
            {"field": "email", "message": "Email is already registered.", "code": "duplicate"}
        ],
    )


async def _ensure_email_available(
    session: AsyncSession, email: str, *, exclude_id: int | None = None
) -> None:
    """Raise the 409 error when `email` is already taken by another profile."""
    stmt = select(UserProfile.id).where(UserProfile.email == email)
    if exclude_id is not None:
        stmt = stmt.where(UserProfile.id != exclude_id)
    existing_id = await session.scalar(stmt)
    if existing_id is not None:
        raise _email_conflict()
