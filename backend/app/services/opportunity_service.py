"""Opportunity queries: listing, filtering, lookup."""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ErrorCode, NotFoundError
from app.models import Opportunity
from app.services import taxonomy


async def get_opportunity(session: AsyncSession, opportunity_id: str) -> Opportunity:
    """Return the opportunity or raise the standard 404 envelope error."""
    opportunity = await session.get(Opportunity, opportunity_id)
    if opportunity is None:
        raise NotFoundError(
            f"Opportunity {opportunity_id!r} not found.",
            code=ErrorCode.OPPORTUNITY_NOT_FOUND,
        )
    return opportunity


async def list_opportunities(
    session: AsyncSession,
    *,
    page: int,
    page_size: int,
    country: str | None = None,
    track: str | None = None,
    employment_type: str | None = None,
    search: str | None = None,
) -> tuple[list[Opportunity], int]:
    """One page of opportunities with optional filters plus the total count.

    - country: canonical country name (validated by the router)
    - track: canonical career track (JSON array containment)
    - employment_type: full_time | internship | contract | part_time
    - search: case-insensitive match on title/organisation/city
    """
    stmt = select(Opportunity)
    if country:
        stmt = stmt.where(Opportunity.country == country)
    if track:
        stmt = stmt.where(Opportunity.career_tracks.contains([track]))
    if employment_type:
        stmt = stmt.where(Opportunity.employment_type == employment_type)
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Opportunity.title.ilike(pattern),
                Opportunity.organisation.ilike(pattern),
                Opportunity.city.ilike(pattern),
            )
        )

    total = await session.scalar(select(func.count()).select_from(stmt.subquery()))
    rows = await session.scalars(
        stmt.order_by(Opportunity.id).offset((page - 1) * page_size).limit(page_size)
    )
    return list(rows), total or 0


def taxonomy_summary() -> dict:
    """The reference taxonomy payload for `GET /meta/taxonomy`."""
    from app.schemas.taxonomy import CountryInfo, RankedLevel, TaxonomyRead

    # Invert COUNTRY_ALIASES into country -> true alternative names (the
    # lowercase canonical name itself is not a distinct alias), so clients
    # can validate input against exactly what the backend accepts.
    country_aliases: dict[str, list[str]] = {}
    for alias, canonical in taxonomy.COUNTRY_ALIASES.items():
        if alias != canonical.lower():
            country_aliases.setdefault(canonical, []).append(alias)

    return TaxonomyRead(
        degree_levels=[
            RankedLevel(value=level, label=taxonomy.DEGREE_LEVEL_LABELS[level], rank=rank)
            for level, rank in taxonomy.DEGREE_RANK.items()
        ],
        language_levels=[
            RankedLevel(value=level, label=taxonomy.LANGUAGE_LEVEL_LABELS[level], rank=rank)
            for level, rank in taxonomy.LANGUAGE_RANK.items()
        ],
        languages=list(taxonomy.LANGUAGES),
        skills=list(taxonomy.SKILLS),
        fields=list(taxonomy.FIELDS),
        countries=[
            CountryInfo(name=name, region=region, aliases=country_aliases.get(name, []))
            for name, region in taxonomy.COUNTRY_REGIONS.items()
        ],
        career_tracks=list(taxonomy.TRACKS),
        work_auth_values=sorted(taxonomy.WORK_AUTH_VALUES),
        weights=dict(taxonomy.WEIGHTS),
        disclaimer=taxonomy.ELIGIBILITY_DISCLAIMER,
    )
