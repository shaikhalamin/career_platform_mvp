"""Reference taxonomy endpoint — drives the frontend form dropdowns and the
scoring legend."""

from fastapi import APIRouter

from app.core.responses import ApiResponse
from app.schemas.taxonomy import TaxonomyRead
from app.services import opportunity_service

router = APIRouter(prefix="/meta", tags=["Meta"])


@router.get(
    "/taxonomy",
    response_model=ApiResponse[TaxonomyRead],
    summary="Reference taxonomy for profiles and scoring",
    description=(
        "Ranked education levels and language proficiencies, the skills "
        "taxonomy, countries with regions, career tracks, work-authorisation "
        "values and the fixed score weights."
    ),
)
async def get_taxonomy() -> ApiResponse[TaxonomyRead]:
    return ApiResponse[TaxonomyRead](data=opportunity_service.taxonomy_summary())
