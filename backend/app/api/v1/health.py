"""Health endpoints: liveness plus a real database round-trip."""

from fastapi import APIRouter
from sqlalchemy import text

from app.core.dependencies import SessionDep
from app.core.exceptions import ServiceUnavailableError
from app.core.responses import ApiResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=ApiResponse[dict[str, str]],
    summary="Liveness + database check",
)
async def health(session: SessionDep) -> ApiResponse[dict[str, str]]:
    """Report service status; `database: "ok"` only after a SELECT 1."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise ServiceUnavailableError(message="Database is unreachable.") from exc
    return ApiResponse[dict[str, str]](data={"status": "ok", "database": "ok"})
