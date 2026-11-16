"""Idempotent seeding: 50 fictional opportunities.

`ensure_opportunities` upserts the seed set by id — safe to call at every
startup and from test fixtures. User profiles are never seeded; only
profiles created through the API exist.
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity
from app.seed_data.opportunities import OPPORTUNITIES

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


async def ensure_seeded(session: AsyncSession) -> None:
    """Startup hook: reference opportunities only — profiles are user-created."""
    await ensure_opportunities(session)
