"""Idempotent seeding: 50 fictional opportunities (+ demo profiles).

`ensure_opportunities` upserts the seed set by id — safe to call at every
startup and from test fixtures. `ensure_demo_profiles` additionally creates
the raw-text demo candidates (only when no profiles exist yet) to keep
test databases deterministic.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity, UserProfile
from app.seed_data.opportunities import OPPORTUNITIES, RAW_DEMO_CANDIDATES
from app.services.normalization import parse_raw_candidate

logger = logging.getLogger("app.services.seed")


async def ensure_opportunities(session: AsyncSession) -> int:
    """Upsert the seed opportunity set; returns the number applied."""
    existing_ids = set(await session.scalars(select(Opportunity.id)))
    applied = 0
    for payload in OPPORTUNITIES:
        if payload["id"] in existing_ids:
            row = await session.get(Opportunity, payload["id"])
            changed = False
            for column, value in payload.items():
                if getattr(row, column) != value:
                    setattr(row, column, value)
                    changed = True
            applied += int(changed)
        else:
            session.add(Opportunity(**payload))
            applied += 1
    await session.flush()
    logger.info(
        "Seed opportunities ready (%d rows, %d applied this run)", len(OPPORTUNITIES), applied
    )
    return applied


async def ensure_demo_profiles(session: AsyncSession) -> int:
    """Create demo candidates from their raw free-text payloads.

    Idempotent per email — existing demo profiles are never duplicated or
    overwritten, and unrelated profiles are left untouched.
    """
    existing_emails = set(await session.scalars(select(UserProfile.email)))
    created = 0
    for demo in RAW_DEMO_CANDIDATES:
        if demo["email"] in existing_emails:
            continue
        normalized = parse_raw_candidate(demo["raw"])
        session.add(
            UserProfile(
                name=demo["name"],
                email=demo["email"],
                education_level=normalized.education_level,
                education_field=normalized.education_field,
                experience_years=normalized.experience_years,
                experience_areas=list(normalized.experience_areas),
                skills=list(normalized.raw_skills),
                languages=dict(normalized.languages),
                preferred_locations=list(normalized.preferred_countries),
                career_interests=list(normalized.raw_interests),
                work_authorisation=dict(normalized.work_authorisation),
                citizenship=normalized.citizenship,
                currently_enrolled=normalized.currently_enrolled,
            )
        )
        created += 1
    if created:
        await session.flush()
        logger.info("Demo profiles created (%d)", created)
    return created


async def ensure_seeded(session: AsyncSession) -> None:
    """Startup hook: opportunities always, demo profiles into empty DBs."""
    await ensure_opportunities(session)
    await ensure_demo_profiles(session)
